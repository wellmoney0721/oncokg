"""Structured answers: claims checked exactly against the graph, prose written from them.

Reading free prose for unsupported claims is a pattern match over sentence shapes,
and six adversarial rounds kept finding shapes it misread (see claims.py and README
known defect 13). This module removes the problem instead of chasing it: a language
model does not write the answer, it fills in claims, and the program writes the
answer from the claims that check out.

A claim is a small JSON object of a fixed kind with fixed keys:

  {"kind": "relation", "relation": "ACTS_ON", "subject": "osimertinib",
   "object": "EGFR", "evidence": "<edge id>", "action": "INHIBITOR"}          (action optional)
  {"kind": "relation", "relation": "EVALUATES", "subject": "NCT03909334",
   "object": "osimertinib", "evidence": "<edge id>"}
  {"kind": "relation", "relation": "SPONSORS_TRIAL_OF", "subject": "AstraZeneca",
   "object": "osimertinib", "evidence": "<edge id>", "trial_count": 14}       (trial_count optional)
  {"kind": "trial", "trial": "NCT03909334", "evidence": "<edge id>",
   "phase": ["PHASE2"], "status": "ACTIVE_NOT_RECRUITING"}                    (phase, status optional; one needed)
  {"kind": "drug", "drug": "osimertinib", "evidence": "<edge id>",
   "max_stage": "APPROVAL", "trials_in_graph": 118}                           (one of the two needed)

A claim is accepted only when all of these hold:

  * its kind and keys are exactly as above (an unknown key rejects the claim, so no
    free text can ride along) and every value has the expected type;
  * the cited evidence id is one of the edges retrieved for this question, and that
    edge is live in the graph (or, for a drug claim, it is the drug's own profile
    record "profile:<id>" retrieved for this question);
  * the edge's relation is the claimed relation, and its two ends are the entities
    the claim names: a name is a node id, a label that belongs to exactly one node of
    that type, or a printable-ASCII alias the entity linker resolves, as a whole, to
    one entity (for an organisation, that entity's merged ids count as one);
  * every value equals what the graph stores: the edge's action type, the sponsor's
    trial count, the trial's phase set and status, the drug's maximum stage, and the
    number of live trials evaluating the drug.

The answer shown to the reader is written by `render` from accepted claims only, using
the graph's own labels and values, never the claim's strings. A claim that does not
check out is reported with the reason and left out of the answer.

What this does not do: it cannot tell whether the claims chosen answer the question
well, or whether something important was left out. It guarantees that what is said is
in the graph, not that everything in the graph that matters was said.
"""
from __future__ import annotations

import json
import re
import sqlite3

RELATIONS = {"ACTS_ON": ("Drug", "Target"), "EVALUATES": ("Trial", "Drug"),
             "SPONSORS_TRIAL_OF": ("Company", "Drug")}
KEYS = {
    "relation": ({"kind", "relation", "subject", "object", "evidence"},
                 {"action", "trial_count"}),
    "trial": ({"kind", "trial", "evidence"}, {"phase", "status"}),
    "drug": ({"kind", "drug", "evidence"}, {"max_stage", "trials_in_graph"}),
}
RE_NCT = re.compile(r"NCT\d{8}")


def _norm(v: str) -> str:
    """Spelling-insensitive form of a stored code: "phase 2" = "PHASE2" = "Phase-2"."""
    return re.sub(r"[\s\-_/]+", "", v.strip().upper())


def _flat(s: str) -> str:
    """Case and punctuation aside, the same characters: letters of any script count, so
    "osimertinib가 아닌" is not the same name as "osimertinib"."""
    return " ".join(re.findall(r"[^\W_]+", s.casefold()))


def _no_constant(name):
    raise ValueError(f"{name} is not a JSON number")


def _finite_float(text):
    v = float(text)
    if v != v or v in (float("inf"), float("-inf")):
        raise ValueError(f"{text} is not a finite number")      # "1e309" overflows
    return v


def _safe(v, depth=0):
    """A rejected claim echoed back, with anything JSON cannot carry made a string."""
    if depth > 20:
        return "…"
    if isinstance(v, float) and (v != v or v in (float("inf"), float("-inf"))):
        return str(v)
    if isinstance(v, dict):
        return {str(k): _safe(x, depth + 1) for k, x in list(v.items())[:50]}
    if isinstance(v, (list, tuple)):
        return [_safe(x, depth + 1) for x in list(v)[:50]]
    if v is None or isinstance(v, (bool, int, float)):
        return v
    return str(v)[:500]


class Verifier:
    def __init__(self, kg):
        self.kg = kg

    # -- entity names --------------------------------------------------------- #
    def resolve(self, name, want: str) -> tuple[set[str], str | None]:
        """Node ids a name stands for, as a whole, among nodes of type `want`."""
        if not isinstance(name, str) or not name.strip() or len(name) > 120:
            return set(), "the name must be a short non-empty string"
        name = name.strip()
        row = self.kg.conn.execute("SELECT id, type FROM node WHERE id=? AND retired_at IS NULL",
                                   (name,)).fetchone()
        if row:
            return ({row["id"]}, None) if row["type"] == want else (
                set(), f"{name} is a {row['type'].lower()}, not a {want.lower()}")
        if want == "Trial":
            return set(), "a trial is named by its registry id (NCT followed by 8 digits)"
        # a label exactly as the graph (and so the evidence) writes it
        rows = self.kg.conn.execute(
            "SELECT id, type FROM node WHERE lower(label)=lower(?) AND retired_at IS NULL",
            (name,)).fetchall()
        if rows:
            ids = {r["id"] for r in rows if r["type"] == want}
            if len(ids) > 1:
                return set(), (f"'{name}' is the label of {len(ids)} {want.lower()} nodes; "
                               "use the id")
            if ids:
                return ids, None
            return set(), f"{name} is a {rows[0]['type'].lower()}, not a {want.lower()}"
        if not (name.isascii() and name.isprintable()):
            # the linker drops characters it cannot read, so "osimertinib是安全的" would
            # pass as osimertinib; outside the graph's own labels, names are plain ASCII
            return set(), (f"'{name}' is not written the way the graph writes names "
                           "(use the id or the name as it appears in the evidence)")
        ents = [e for e in self.kg.link_entities(name) if e.get("type") not in ("Disease",)]
        whole = len(ents) == 1 and _flat(ents[0].get("matched_text") or "") == _flat(name)
        if whole and ents[0].get("type") != want:
            return set(), f"{name} is a {ents[0]['type'].lower()}, not a {want.lower()}"
        if not whole:
            return set(), f"'{name}' does not name exactly one {want.lower()} on its own"
        e = ents[0]
        return {e["id"], *e.get("also_matching_ids", [])}, None

    # -- one claim ------------------------------------------------------------ #
    def check(self, claim, retrieved: set[str]) -> tuple[dict | None, str | None]:
        """Return (facts to render, None) or (None, reason)."""
        if not isinstance(claim, dict):
            return None, "a claim must be a JSON object"
        kind = claim.get("kind")
        if not isinstance(kind, str) or kind not in KEYS:
            return None, f"unknown kind {kind!r}; use relation, trial or drug"
        need, may = KEYS[kind]
        keys = set(claim)
        if need - keys:
            return None, f"missing {sorted(need - keys)}"
        if keys - need - may:
            return None, f"unknown keys {sorted(keys - need - may)} (no free text is accepted)"
        ev = claim["evidence"]
        if not isinstance(ev, str) or ev not in retrieved:
            return None, "the cited evidence is not among the edges retrieved for this question"
        edge = self.kg.conn.execute(
            "SELECT * FROM edge WHERE id=? AND retired_at IS NULL", (ev,)).fetchone()
        if kind == "drug" and edge is None and ev.startswith("profile:"):
            edge = {"id": ev, "rel": "PROFILE", "src": ev.split(":", 1)[1], "dst": None,
                    "props": "{}"}
        if edge is None:
            return None, "the cited evidence is not a live edge of the graph"
        return getattr(self, "_" + kind)(claim, edge)

    def _relation(self, c, edge):
        rel = c["relation"]
        if not isinstance(rel, str) or rel not in RELATIONS:
            return None, f"unknown relation {rel!r}"
        if edge["rel"] != rel:
            return None, f"the cited edge is {edge['rel']}, not {rel}"
        st, ot = RELATIONS[rel]
        s_ids, why = self.resolve(c["subject"], st)
        if why:
            return None, why
        o_ids, why = self.resolve(c["object"], ot)
        if why:
            return None, why
        if edge["src"] not in s_ids or edge["dst"] not in o_ids:
            return None, "the cited edge does not join these two entities in this direction"
        props = json.loads(edge["props"] or "{}")
        facts = {"kind": "relation", "relation": rel, "edge": edge["id"],
                 "subject": edge["src"], "object": edge["dst"]}
        if "action" in c:
            if rel != "ACTS_ON" or not isinstance(c["action"], str):
                return None, "an action belongs to an ACTS_ON claim, as a string"
            if _norm(c["action"]) != _norm(props.get("action_type") or ""):
                return None, (f"the graph gives the action as {props.get('action_type') or 'none'}, "
                              f"not {c['action']}")
            facts["action"] = props["action_type"]
        if "trial_count" in c:
            n = c["trial_count"]
            if rel != "SPONSORS_TRIAL_OF" or type(n) is not int:
                return None, "a trial_count belongs to a SPONSORS_TRIAL_OF claim, as a whole number"
            if n != props.get("evidence_trials"):
                return None, f"the graph gives {props.get('evidence_trials')} trials, not {n}"
            facts["trial_count"] = n
        return facts, None

    def _trial(self, c, edge):
        if edge["rel"] != "EVALUATES":
            return None, "a trial's phase or status is cited from an EVALUATES edge of that trial"
        ids, why = self.resolve(c["trial"], "Trial")
        if why:
            return None, why
        if edge["src"] not in ids:
            return None, "the cited edge belongs to a different trial"
        if "phase" not in c and "status" not in c:
            return None, "a trial claim states a phase, a status or both"
        node = self.kg.conn.execute("SELECT props FROM node WHERE id=?", (edge["src"],)).fetchone()
        props = json.loads(node["props"] or "{}")
        facts = {"kind": "trial", "edge": edge["id"], "trial": edge["src"]}
        if "phase" in c:
            ph = c["phase"]
            if not isinstance(ph, list) or not all(isinstance(x, str) for x in ph):
                return None, "phase is a list of strings, e.g. [\"PHASE2\"]"
            if sorted(_norm(x) for x in ph) != sorted(_norm(x) for x in props.get("phases") or []):
                return None, f"the graph gives the phase as {props.get('phases')}, not {ph}"
            facts["phase"] = props.get("phases")
        if "status" in c:
            if not isinstance(c["status"], str) or _norm(c["status"]) != _norm(props.get("status") or ""):
                return None, f"the graph gives the status as {props.get('status')}, not {c['status']}"
            facts["status"] = props.get("status")
        return facts, None

    def _drug(self, c, edge):
        ids, why = self.resolve(c["drug"], "Drug")
        if why:
            return None, why
        if edge["rel"] not in ("ACTS_ON", "PROFILE") or edge["src"] not in ids:
            return None, "a drug's stage or trial count is cited from that drug's own statement"
        if "max_stage" not in c and "trials_in_graph" not in c:
            return None, "a drug claim states max_stage, trials_in_graph or both"
        node = self.kg.conn.execute("SELECT props FROM node WHERE id=?", (edge["src"],)).fetchone()
        props = json.loads(node["props"] or "{}")
        facts = {"kind": "drug", "edge": edge["id"], "drug": edge["src"]}
        if "max_stage" in c:
            if not isinstance(c["max_stage"], str) or \
                    _norm(c["max_stage"]) != _norm(props.get("max_phase_overall") or ""):
                return None, (f"the graph gives the maximum stage as "
                              f"{props.get('max_phase_overall')}, not {c['max_stage']}")
            facts["max_stage"] = props.get("max_phase_overall")
        if "trials_in_graph" in c:
            n = c["trials_in_graph"]
            real = self.kg.conn.execute(
                "SELECT COUNT(*) FROM edge WHERE rel='EVALUATES' AND dst=? AND retired_at IS NULL",
                (edge["src"],)).fetchone()[0]
            if type(n) is not int or n != real:
                return None, f"the graph gives {real} trials evaluating this drug, not {n}"
            facts["trials_in_graph"] = real
        return facts, None

    # -- a whole answer -------------------------------------------------------- #
    def verify(self, payload, evidence) -> dict:
        """`payload` is the model's JSON (a string or already parsed)."""
        if isinstance(payload, str):
            try:
                # NaN and Infinity are not JSON; refusing them keeps every echo valid JSON
                payload = json.loads(payload, parse_constant=_no_constant,
                                     parse_float=_finite_float)
            except (ValueError, RecursionError) as e:
                return {"verified": False, "accepted": [], "text": "",
                        "rejected": [{"claim": None, "why": "not valid JSON: "
                                      + (getattr(e, "msg", None) or "nested too deeply")}]}
        claims = payload.get("claims") if isinstance(payload, dict) else None
        if isinstance(claims, list) and not claims and set(payload) == {"claims"}:
            # the model's way of saying the evidence does not answer the question
            return {"verified": False, "accepted": [], "rejected": [], "text": "",
                    "empty": True}
        if not isinstance(claims, list) or set(payload) != {"claims"}:
            return {"verified": False, "accepted": [], "text": "",
                    "rejected": [{"claim": None,
                                  "why": 'the answer must be {"claims": [...]} and nothing else'}]}
        retrieved = {e.edge_id for e in evidence}
        accepted, rejected = [], []
        for c in claims[:50]:
            try:
                facts, why = self.check(c, retrieved)
            except Exception as e:           # a claim the checker cannot read is rejected
                facts, why = None, f"the claim could not be read ({type(e).__name__})"
            if why:
                rejected.append({"claim": _safe(c), "why": why})
            else:
                accepted.append(facts)
        if len(claims) > 50:
            rejected.append({"claim": None, "why": "more than 50 claims; the rest were not read"})
        return {"verified": not rejected, "accepted": accepted, "rejected": rejected,
                "text": render(accepted, self.kg.conn)}


def render(facts: list[dict], conn: sqlite3.Connection) -> str:
    """Sentences from accepted facts, in the graph's own words."""
    def label(i):
        r = conn.execute("SELECT label FROM node WHERE id=?", (i,)).fetchone()
        return r[0] if r else i

    lines = []
    for f in facts:
        if f["kind"] == "relation" and f["relation"] == "ACTS_ON":
            act = f" ({f['action'].lower()})" if f.get("action") else ""
            lines.append(f"{label(f['subject'])} acts on {label(f['object'])}{act}")
        elif f["kind"] == "relation" and f["relation"] == "EVALUATES":
            lines.append(f"{label(f['subject'])} evaluates {label(f['object'])}")
        elif f["kind"] == "relation":
            n = f" {f['trial_count']}" if "trial_count" in f else ""
            lines.append(f"{label(f['subject'])} is lead sponsor of{n} trial(s) evaluating "
                         f"{label(f['object'])} - a sponsorship, not evidence of developing "
                         "the drug")
        elif f["kind"] == "trial":
            bits = []
            if "phase" in f:
                bits.append("phase " + ", ".join(f["phase"]) if f["phase"] else "no phase given")
            if "status" in f:
                bits.append("status " + f["status"])
            lines.append(f"{label(f['trial'])}: " + "; ".join(bits))
        else:
            bits = []
            if "max_stage" in f:
                bits.append(f"maximum clinical stage {f['max_stage']}")
            if "trials_in_graph" in f:
                bits.append(f"{f['trials_in_graph']} NSCLC trial(s) in this graph")
            lines.append(f"{label(f['drug'])}: " + "; ".join(bits))
        lines[-1] += f" [{f['edge']}]"
    return "\n".join(f"- {x}" for x in lines)
