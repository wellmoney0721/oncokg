"""Grounded question answering over the graph.

The retrieval step is the same resolver the pipeline uses, pointed at the
question instead of at a registry record. A question that names "Tagrisso" and a
graph that stores CHEMBL3353410 only meet if one vocabulary serves both, so the
dictionary is reused rather than reimplemented.

Three properties the answering layer holds to:

* **Every statement is traceable.** Each claim carries the edges it rests on,
  each edge carries its source record and fetch time.
* **The graph answers, not the model.** With a key, the language model is given
  the retrieved evidence and returns claims, not prose; each claim is checked
  against the graph and the answer is written from the accepted ones in the
  graph's own words (structured.py). With no key the evidence is rendered
  directly.
* **Nothing unsupported is shipped.** A claim the graph does not support is
  reported and left out. An unverifiable answer is worse than a short one.
"""
from __future__ import annotations

import json
import os
import re
import sqlite3
import sys
from dataclasses import dataclass, field
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import config as C
import normalize as N
import textrules as T

DB_PATH = C.PROCESSED / "oncokg.sqlite"
TRIAL_URL = "https://clinicaltrials.gov/study/{}"


# --------------------------------------------------------------------------- #
# evidence
# --------------------------------------------------------------------------- #
@dataclass
class Evidence:
    statement: str
    edge_id: str
    relation: str
    source: str
    source_record: str | None
    fetched_at: str | None
    confidence: float
    tier: str | None = None
    url: str | None = None
    detail: dict = field(default_factory=dict)

    def citation(self) -> str:
        base = self.source_record or self.source
        return f"[{base}]"


@dataclass
class Answer:
    question: str
    intent: str
    entities: list[dict]
    text: str
    evidence: list[Evidence]
    generated_by: str
    checks: dict

    def to_dict(self) -> dict:
        return {
            "question": self.question,
            "intent": self.intent,
            "entities": self.entities,
            "answer": self.text,
            "generated_by": self.generated_by,
            "checks": self.checks,
            "evidence": [
                {"statement": e.statement, "relation": e.relation, "edge_id": e.edge_id,
                 "source": e.source, "source_record": e.source_record,
                 "fetched_at": e.fetched_at, "confidence": e.confidence,
                 "resolution_tier": e.tier, "url": e.url, **e.detail}
                for e in self.evidence
            ],
        }


# --------------------------------------------------------------------------- #
# engine
# --------------------------------------------------------------------------- #
class OncoKG:
    def __init__(self, db_path: Path = DB_PATH,
                 resolved_path: Path = C.PROCESSED / "resolved.json"):
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row
        resolved = json.loads(resolved_path.read_text(encoding="utf-8"))
        self.dic = resolved["dictionary"]
        self.index_keys = list(self.dic["index"].keys())
        self.disease = resolved["disease"]
        self.targets = {t["symbol"].lower(): t for t in resolved["targets"]
                        if t.get("symbol")}
        # one name can denote several organisations (a group and a subsidiary
        # renamed after it), so a key maps to every matching node, not one.
        self.companies: dict[str, list[str]] = {}
        for row in self.conn.execute(
                "SELECT id,label FROM node WHERE type='Company' AND retired_at IS NULL"):
            self.companies.setdefault(T.canonical_key(row["label"]), []).append(row["id"])
            self.companies.setdefault(row["id"].removeprefix("ORG:"), []).append(row["id"])
        # a former name ("BeiGene") must still find the merged node
        for old, same in N.CURATED_SAME_ENTITY.items():
            if same in self.companies:
                self.companies.setdefault(old, []).extend(self.companies[same])
        self.companies = {k: sorted(set(v)) for k, v in self.companies.items()}

    # -- entity linking ---------------------------------------------------- #
    def link_entities(self, question: str) -> list[dict]:
        found: list[dict] = []
        seen: set = set()
        tokens = [t.strip(" ?.,!;:") for t in re.split(r"[\s,]+", question)
                  if t.strip(" ?.,!;:")]

        # The resolver's refusals apply to questions too. Linking straight
        # against the index let "Mvasi" or "liposomal doxorubicin" answer as
        # the originator molecule. A token naming a distinct product is
        # refused; a qualifier ("liposomal", "biosimilar") takes its
        # neighbours with it.
        refused: set[int] = set()
        for i, tok in enumerate(tokens):
            if T.is_distinct_product(tok) or T.is_radiotracer(tok):
                refused.add(i)
                if not T.canonical_key(tok) in self.dic["index"]:
                    refused.update({i - 1, i + 1})
        refused = {x for x in refused if 0 <= x < len(tokens)}
        run: list[int] = []
        for i in sorted(refused) + [None]:
            if run and (i is None or i != run[-1] + 1):
                span = " ".join(tokens[run[0]:run[-1] + 1])
                found.append({"type": "Refused", "id": None, "label": span,
                              "matched_text": span,
                              "why": "names a distinct product or tracer, not "
                                     "the originator molecule"})
                run = []
            if i is not None:
                run.append(i)

        for size in range(min(5, len(tokens)), 0, -1):
            for i in range(len(tokens) - size + 1):
                if refused & set(range(i, i + size)):
                    continue
                window = " ".join(tokens[i:i + size])
                if len(window) < 3:
                    continue
                # A product or tracer spelt across several tokens ("bevacizumab -
                # awwb", "[89Zr] trastuzumab") is refused whole, so no part of it
                # links to the originator.
                if size > 1 and (T.is_distinct_product(window) or T.is_radiotracer(window)):
                    found.append({"type": "Refused", "id": None, "label": window,
                                  "matched_text": window,
                                  "why": "names a distinct product or tracer, not "
                                         "the originator molecule"})
                    refused.update(range(i, i + size))
                    continue
                key = T.canonical_key(window)

                hits = self.dic["index"].get(key)
                # Several words only make a drug name when the name itself has
                # several words. The key drops spaces, so "is a" read as the
                # abbreviation "isa" (isatuximab) in any question or answer.
                if hits and size > 1 and not re.search(r"[\s\-/]", hits[0]["alias"]):
                    hits = None
                if hits and len({h["drug_id"] for h in hits}) == 1:
                    did = hits[0]["drug_id"]
                    if ("Drug", did) not in seen:
                        seen.add(("Drug", did))
                        found.append({"type": "Drug", "id": did,
                                      "label": self.dic["drugs"][did]["name"],
                                      "matched_text": window,
                                      "matched_alias": hits[0]["alias"]})
                    continue

                if window.lower() in self.targets:
                    t = self.targets[window.lower()]
                    if ("Target", t["target_id"]) not in seen:
                        seen.add(("Target", t["target_id"]))
                        found.append({"type": "Target", "id": t["target_id"],
                                      "label": t["symbol"], "matched_text": window})
                    continue

                if key in self.companies:
                    cid = self.companies[key][0]
                    if ("Company", cid) not in seen:
                        seen.add(("Company", cid))
                        row = self.conn.execute(
                            "SELECT label FROM node WHERE id=?", (cid,)).fetchone()
                        found.append({"type": "Company", "id": cid,
                                      "label": row["label"], "matched_text": window,
                                      "also_matching_ids": self.companies[key][1:]})
                    continue

                if key in self.disease["index"]:
                    if ("Disease", self.disease["disease_id"]) not in seen:
                        seen.add(("Disease", self.disease["disease_id"]))
                        found.append({"type": "Disease",
                                      "id": self.disease["disease_id"],
                                      "label": self.disease["name"],
                                      "matched_text": window})
        return found

    def org_family(self, company_id: str) -> list[str]:
        """The organisation plus any companies a curated parent edge links to it."""
        ids = {company_id}
        for row in self.conn.execute(
                "SELECT dst FROM edge WHERE rel='PARENT_OF' AND src=?"
                " AND retired_at IS NULL", (company_id,)):
            ids.add(row["dst"])
        return sorted(ids)

    # -- intent ------------------------------------------------------------ #
    @staticmethod
    def classify(question: str, entities: list[dict]) -> str:
        q = question.lower()
        types = {e["type"] for e in entities}
        if re.search(r"\b(who|which compan|which firm|sponsor|develop|partner)", q):
            return "companies_for_drug" if "Drug" in types else "companies_for_target"
        if re.search(r"\b(trials?|stud(y|ies)|nct)\b", q):
            return "trials_for_entity"
        if re.search(r"\b(target|mechanism|acts? on|moa)\b", q) and "Drug" in types:
            return "targets_of_drug"
        if "Target" in types and re.search(r"\b(drug|inhibitor|agent|candidate)", q):
            return "drugs_for_target"
        if "Company" in types:
            return "company_portfolio"
        if "Drug" in types:
            return "drug_profile"
        if "Target" in types:
            return "drugs_for_target"
        return "unsupported"

    # -- retrieval --------------------------------------------------------- #
    def _rows(self, sql: str, params: tuple) -> list[sqlite3.Row]:
        return list(self.conn.execute(sql, params))

    def retrieve(self, intent: str, entities: list[dict], limit: int = 12):
        ev: list[Evidence] = []
        drug = next((e for e in entities if e["type"] == "Drug"), None)
        target = next((e for e in entities if e["type"] == "Target"), None)
        company = next((e for e in entities if e["type"] == "Company"), None)

        if intent == "companies_for_drug" and drug:
            for r in self._rows("""
                SELECT e.id, e.src, e.confidence, e.props, n.label AS company
                FROM edge e JOIN node n ON n.id = e.src
                WHERE e.rel='SPONSORS_TRIAL_OF' AND e.dst=? AND e.retired_at IS NULL
                ORDER BY json_extract(e.props,'$.evidence_trials') DESC LIMIT ?
            """, (drug["id"], limit)):
                p = json.loads(r["props"])
                ev.append(Evidence(
                    # sponsorship only; the sponsor class is stated so a reader
                    # can tell an originator from a cooperative group
                    statement=f"{r['company']} ({(p.get('sponsor_class') or 'unknown class').lower()} "
                              f"sponsor) is lead sponsor of "
                              f"{p['evidence_trials']} trial(s) evaluating {drug['label']}"
                              " - a sponsorship, not evidence of developing the drug",
                    edge_id=r["id"], relation="SPONSORS_TRIAL_OF", source="derived",
                    source_record=", ".join(p.get("evidence_sample", [])[:3]),
                    fetched_at=None, confidence=r["confidence"],
                    detail={"derived_rule": p.get("rule"),
                            "sponsor_class": p.get("sponsor_class"),
                            "evidence_trials": p["evidence_trials"],
                            "example_trials": p.get("evidence_sample", [])[:3]}))

        elif intent in ("trials_for_entity",) and drug:
            for r in self._rows("""
                SELECT e.id, e.src, e.confidence, e.tier, e.props, e.source_record,
                       e.source_fetched_at, n.props AS tprops, n.label AS nct
                FROM edge e JOIN node n ON n.id = e.src
                WHERE e.rel='EVALUATES' AND e.dst=? AND e.retired_at IS NULL
                ORDER BY e.confidence DESC LIMIT ?
            """, (drug["id"], limit)):
                tp = json.loads(r["tprops"])
                p = json.loads(r["props"])
                ev.append(Evidence(
                    statement=f"{r['nct']} ({', '.join(tp.get('phases') or []) or 'phase n/a'}, "
                              f"{tp.get('status')}) evaluates {drug['label']}",
                    edge_id=r["id"], relation="EVALUATES", source="clinicaltrials.gov",
                    source_record=r["source_record"], fetched_at=r["source_fetched_at"],
                    confidence=r["confidence"], tier=r["tier"],
                    url=TRIAL_URL.format(r["nct"]),
                    detail={"stated_intervention": p.get("stated_intervention"),
                            "title": tp.get("title"), "status": tp.get("status"),
                            "phases": tp.get("phases")}))

        elif intent == "targets_of_drug" and drug:
            for r in self._rows("""
                SELECT e.id, e.confidence, e.props, e.source_record,
                       e.source_fetched_at, n.label AS symbol, n.props AS tprops
                FROM edge e JOIN node n ON n.id = e.dst
                WHERE e.rel='ACTS_ON' AND e.src=? AND e.retired_at IS NULL LIMIT ?
            """, (drug["id"], limit)):
                p = json.loads(r["props"])
                ev.append(Evidence(
                    statement=f"{drug['label']} acts on {r['symbol']}"
                              + (f" ({p['action_type'].lower()})" if p.get("action_type") else ""),
                    edge_id=r["id"], relation="ACTS_ON", source="Open Targets / ChEMBL",
                    source_record=r["source_record"], fetched_at=r["source_fetched_at"],
                    confidence=r["confidence"], detail={"action_type": p.get("action_type")}))

        elif intent == "drugs_for_target" and target:
            for r in self._rows("""
                SELECT e.id, e.confidence, e.props, e.source_record,
                       e.source_fetched_at, n.label AS drug, n.props AS dprops, n.id AS did
                FROM edge e JOIN node n ON n.id = e.src
                WHERE e.rel='ACTS_ON' AND e.dst=? AND e.retired_at IS NULL LIMIT ?
            """, (target["id"], limit)):
                dp = json.loads(r["dprops"])
                trials = self.conn.execute(
                    "SELECT COUNT(*) FROM edge WHERE rel='EVALUATES' AND dst=?"
                    " AND retired_at IS NULL", (r["did"],)).fetchone()[0]
                p = json.loads(r["props"])
                act = (p.get("action_type") or "").lower()
                ev.append(Evidence(
                    statement=f"{r['drug']} acts on {target['label']}"
                              f" ({act + '; ' if act else ''}"
                              f"max stage {dp.get('max_phase_overall') or 'n/a'};"
                              f" {trials} NSCLC trial(s) in this graph)",
                    edge_id=r["id"], relation="ACTS_ON", source="Open Targets / ChEMBL",
                    source_record=r["source_record"], fetched_at=r["source_fetched_at"],
                    confidence=r["confidence"],
                    detail={"drug_id": r["did"], "trials_in_graph": trials,
                            "max_phase_overall": dp.get("max_phase_overall")}))

        elif intent == "company_portfolio" and company:
            # a question about a group means the group and the companies it owns
            org_ids = self.org_family(company["id"]) + company.get("also_matching_ids", [])
            placeholders = ",".join("?" * len(org_ids))
            for r in self._rows(f"""
                SELECT e.id, e.confidence, e.props, n.label AS drug,
                       m.label AS org
                FROM edge e JOIN node n ON n.id = e.dst
                JOIN node m ON m.id = e.src
                WHERE e.rel='SPONSORS_TRIAL_OF' AND e.src IN ({placeholders})
                  AND e.retired_at IS NULL
                ORDER BY json_extract(e.props,'$.evidence_trials') DESC LIMIT ?
            """, (*org_ids, limit)):
                p = json.loads(r["props"])
                ev.append(Evidence(
                    statement=f"{r['org']} sponsors {p['evidence_trials']} "
                              f"NSCLC trial(s) evaluating {r['drug']}",
                    edge_id=r["id"], relation="SPONSORS_TRIAL_OF", source="derived",
                    source_record=", ".join(p.get("evidence_sample", [])[:3]),
                    fetched_at=None, confidence=r["confidence"],
                    detail={"evidence_trials": p["evidence_trials"],
                            "example_trials": p.get("evidence_sample", [])[:3]}))

        elif intent == "drug_profile" and drug:
            d = self.dic["drugs"][drug["id"]]
            trials = self.conn.execute(
                "SELECT COUNT(*) FROM edge WHERE rel='EVALUATES' AND dst=?"
                " AND retired_at IS NULL", (drug["id"],)).fetchone()[0]
            ev.append(Evidence(
                statement=f"{d['name']} is a {d['drug_type'] or 'substance'}, "
                          f"max clinical stage {d['max_phase_overall'] or 'n/a'}, "
                          f"appearing in {trials} NSCLC trial(s) in this graph",
                edge_id=f"profile:{drug['id']}", relation="PROFILE",
                source="Open Targets / ChEMBL", source_record=drug["id"],
                fetched_at=None, confidence=1.0,
                detail={"aliases_known": len(d["aliases"]),
                        "mechanisms": d["mechanisms"][:3]}))
            ev.extend(self.retrieve("targets_of_drug", entities, limit=6))
        return ev

    # -- answering --------------------------------------------------------- #
    def answer(self, question: str, use_llm: bool | None = None) -> Answer:
        entities = self.link_entities(question)
        intent = self.classify(question, entities)
        evidence = self.retrieve(intent, entities)

        if intent == "unsupported" or not evidence:
            text = ("This graph cannot answer that. It covers companies, drugs, "
                    "targets and trials in non-small cell lung cancer only, and "
                    "it answers questions about which of those relate to which. "
                    "No entity in the question matched the graph."
                    if not entities else
                    "The entities in the question were recognised but the graph "
                    "holds no edges that answer it.")
            return Answer(question, intent, entities, text, [],
                          "refusal (no supporting evidence)",
                          {"grounded": True, "unsupported_claims": [],
                           "note": "refusing is the correct output when evidence is absent"})

        if use_llm is None:
            use_llm = bool(os.environ.get("ANTHROPIC_API_KEY"))
        if use_llm:
            # The model does not write the answer. It returns claims, each citing an
            # edge; the claims are checked exactly against the graph and the answer is
            # written from the accepted ones (structured.py).
            raw, by = self._llm_claims(question, evidence)
            if by.startswith("error"):
                return Answer(question, intent, entities,
                              "The language model could not be used (" + by[7:] + "); no "
                              "answer was generated.", evidence, by,
                              {"grounded": None, "applicable": False, "accepted": 0,
                               "rejected": [], "unsupported_claims": [],
                               "method": "no model reply to check"})
            result = self.verify_structured(raw, evidence)
            text = result["text"] or (
                "The model found nothing in the evidence that answers this question."
                if result.get("empty") else "None of the model's claims could be verified.")
            if result["rejected"]:
                text += (f"\n\n({len(result['rejected'])} claim(s) were removed because "
                         "the graph does not support them.)")
            checks = {"grounded": result["verified"], "applicable": True,
                      "method": "structured claims checked edge by edge against the graph",
                      "accepted": len(result["accepted"]), "rejected": result["rejected"],
                      "unsupported_claims": [{"kind": "rejected_claim", "value":
                                              json.dumps(r["claim"])[:120], "why": r["why"]}
                                             for r in result["rejected"]]}
            return Answer(question, intent, entities, text, evidence, by, checks)

        text, by = self._template_answer(question, intent, entities, evidence)
        # the trailing scope line is generated metadata, not a claim about the
        # world, so it is excluded from the groundedness check
        claim_text = text.split("\nScope:")[0]
        checks = self.check_groundedness(claim_text, evidence, entities,
                                         generated=False,
                                         vocabulary=set(self.dic["index"]),
                                         linker=self.link_entities)
        return Answer(question, intent, entities, text, evidence, by, checks)

    def verify_structured(self, payload, evidence) -> dict:
        """Check a structured answer against this question's evidence (structured.py)."""
        from structured import Verifier
        return Verifier(self).verify(payload, evidence)

    @staticmethod
    def _template_answer(question, intent, entities, evidence) -> tuple[str, str]:
        head = {
            # headings name the list without stating a relation of their own, so
            # the claim check can read each line under them as it stands
            "companies_for_drug": "Lead sponsorship of trials of this drug",
            "trials_for_entity": "Trials of this drug",
            "targets_of_drug": "Reported mechanism",
            "drugs_for_target": "Agents for this target",
            "company_portfolio": "This organisation's NSCLC trials",
            "drug_profile": "Profile",
        }.get(intent, "Findings")
        lines = [f"{head}:"]
        for e in evidence:
            lines.append(f"  - {e.statement} {e.citation()}")
        lines.append("")
        lines.append(f"Scope: {len(evidence)} edge(s) from this graph; "
                     "non-small cell lung cancer only.")
        return "\n".join(lines), "deterministic template (no language model)"

    @staticmethod
    def _llm_claims(question, evidence) -> tuple[str, str]:
        """Ask the model for claims, not prose. Its reply is data to be checked."""
        try:
            import anthropic
        except ImportError:
            return "", "error: the anthropic package is not installed"
        block = "\n".join(f"- id={e.edge_id} | {e.statement}" for e in evidence)
        prompt = (
            "You answer a question about a non-small cell lung cancer knowledge graph "
            "by choosing facts from the evidence below. Reply with JSON only, of the form "
            '{"claims": [...]}, where each claim is one of:\n'
            '{"kind": "relation", "relation": "ACTS_ON" | "EVALUATES" | "SPONSORS_TRIAL_OF", '
            '"subject": name, "object": name, "evidence": id, "action": optional, '
            '"trial_count": optional integer}\n'
            '{"kind": "trial", "trial": NCT id, "evidence": id, "phase": optional list, '
            '"status": optional}\n'
            '{"kind": "drug", "drug": name, "evidence": id, "max_stage": optional, '
            '"trials_in_graph": optional integer}\n'
            "Use the names and ids exactly as written in the evidence. Add no other keys "
            "and no prose. If the evidence does not answer the question, reply "
            '{"claims": []}.\n\n'
            f"Question: {question}\n\nEvidence:\n{block}\n")
        try:
            client = anthropic.Anthropic()
            msg = client.messages.create(
                model="claude-sonnet-4-5", max_tokens=1500,
                messages=[{"role": "user", "content": prompt}])
        except Exception as e:                    # an outage is reported, not raised
            return "", f"error: {type(e).__name__}"
        raw = next((b.text for b in (msg.content or []) if getattr(b, "text", None)), "")
        raw = raw.strip()
        m = re.search(r"\{.*\}", raw, re.S)            # tolerate a code fence around it
        return (m.group(0) if m else raw), "language model, structured claims"

    # -- answer quality ---------------------------------------------------- #
    @staticmethod
    def check_groundedness(text: str, evidence: list[Evidence],
                           entities: list[dict], generated: bool = True,
                           vocabulary: set | None = None, linker=None) -> dict:
        """Report what in a *generated* answer the retrieved evidence does not support.

        Two things this check is not, both found by an adversarial review and
        written down here rather than papered over:

        1. It is meaningless on the template answer. The template is built by
           concatenating the evidence statements, so checking it against those
           same statements is circular -- it cannot fail, and reporting
           `grounded=True` for it would be a test that always passes. When the
           answer was rendered rather than generated, the check reports
           `applicable=False` and asserts nothing.
        2. It is a reader of word order, not of meaning. Without a `linker` it
           only checks that capitalised entities, drug-shaped names and numbers
           appear somewhere in the retrieved set. With one (the query layer's
           entity linker) it also reads each clause into subject, relation and
           object (claims.check_claims) and reports relations, values and words
           the evidence does not give for those entities. Sentence shapes it was
           not written for can still be misread; claims.py and README known
           defect 13 list what is known to get through.
        """
        if not generated:
            return {
                "grounded": None,
                "applicable": False,
                "unsupported_claims": [],
                "evidence_count": len(evidence),
                "method": "not applicable",
                "why": ("the answer was rendered directly from the retrieved "
                        "evidence, so checking it against that evidence is "
                        "circular and would always pass"),
            }

        if linker is not None:
            # a citation whose every id is a record of this evidence is a citation,
            # not a claim; anything else in brackets stays and is checked
            from claims import _strip_citations
            known = {x.strip().lower() for e in evidence
                     for part in (e.source_record or "", e.edge_id or "", e.statement or "")
                     for x in re.split(r"[,;\s|]+", part) if x.strip()}
            text = _strip_citations(text, known)

        haystack = " ".join(
            [e.statement for e in evidence]
            + [str(v) for e in evidence for v in e.detail.values()]
            + [e.source_record or "" for e in evidence]
            + [en["label"] for en in entities]
        ).lower()
        # Words are tokenised so "47" is not satisfied by NCT02303977. Numbers
        # are tokenised separately and whole, decimals included: splitting on
        # non-alphanumerics turned evidence "47.5" into the tokens "47" and
        # "5", so an invented "47" passed and the exact "47.5" was rejected.
        haystack_tokens = set(re.findall(r"[a-z0-9]+", haystack))
        haystack_numbers = {n.replace(",", "") for n in RE_NUMBER.findall(haystack)}

        unsupported: list[dict] = []

        def alias_in_evidence(word: str) -> bool:
            if linker is None:
                return False
            return any(e.get("type") in ("Drug", "Target", "Company")
                       and e["label"].lower() in haystack for e in linker(word))

        # "phase 3" is stated as PHASE3 in the evidence, so a phase number is
        # matched against that form, not against the bare figures
        haystack_flat = re.sub(r"[\s_\-]+", "", haystack)
        phase_nums = {n for m in re.finditer(r"\bphase\s*(\d)(?:\s*/\s*(\d))?\b", text, re.I)
                      for n in m.groups() if n}
        # digits inside a linked name ("AZD 9291") are part of the name, not a figure
        number_text = text
        if linker is not None:
            for _ in range(8):           # the linker reports each entity once
                before = number_text
                for e in linker(number_text):
                    mt = e.get("matched_text") or ""
                    if mt and e.get("type") != "Refused" and re.search(r"\d", mt):
                        number_text = re.sub(r"[\W_]+".join(map(re.escape, mt.split())),
                                             " ", number_text, flags=re.I)
                if number_text == before:
                    break
        for num in {n.rstrip(",") for n in RE_NUMBER.findall(number_text)}:
            if num in phase_nums and (linker is not None or f"phase{num}" in haystack_flat):
                continue      # with a linker, claims.py checks the phase per entity
            if num.replace(",", "") not in haystack_numbers:
                unsupported.append({"kind": "number", "value": num,
                                    "why": "not present in the retrieved evidence"})

        # A figure written in words cannot be matched against the evidence, so
        # it is reported as unverifiable rather than allowed through.
        for word in set(RE_NUMBER_WORD.findall(text.lower())):
            unsupported.append({"kind": "number_in_words", "value": word,
                                "why": "a figure written in words cannot be "
                                       "checked against the evidence"})

        capitalised = set(re.findall(r"\b[A-Z][A-Za-z0-9\-]{3,}\b", text))
        stop = {"Scope", "Organisations", "Trials", "Profile", "Findings",
                "Agents", "Reported", "This", "The", "None", "NSCLC", "What",
                "There", "These", "That", "Those", "According", "Sponsors",
                "They", "Them", "Their", "Its"}
        for name in capitalised - stop:
            if name.lower() not in haystack and not alias_in_evidence(name):
                unsupported.append({"kind": "entity", "value": name,
                                    "why": "named in the answer but not in the evidence"})

        # Drug names are usually lowercase in prose ("xyzabumab cures cancer"
        # passed the capitalised-only check). Anything shaped like an INN or a
        # development code must appear in the evidence too.
        for name in set(RE_DRUGLIKE.findall(text)):
            if (name.lower() not in haystack_tokens and name.lower() not in haystack
                    and not alias_in_evidence(name)):
                unsupported.append({"kind": "drug_like_name", "value": name,
                                    "why": "looks like a drug name or code but "
                                           "is not in the evidence"})

        # Any word the drug vocabulary knows ("aspirin") is a drug name,
        # whatever its shape, and must be in the evidence.
        if vocabulary:
            for w in set(re.findall(r"[A-Za-z][A-Za-z0-9\-]{3,}", text)):
                if (T.canonical_key(w) in vocabulary and w.lower() not in haystack
                        and not alias_in_evidence(w)):
                    unsupported.append({"kind": "drug_name", "value": w,
                                        "why": "a known drug name not in the evidence"})

        # Figures in forms the number matcher does not read: scientific
        # notation ("1e6") and Unicode fractions or superscripts ("⅔").
        for odd in set(RE_ODD_NUMBER.findall(text)):
            unsupported.append({"kind": "number_unreadable", "value": odd,
                                "why": "a figure in a form the check cannot match"})

        if linker is not None:
            from claims import check_claims
            unsupported.extend(check_claims(text, evidence, linker, entities))

        # one finding per value, first reason kept, in a stable order
        seen_values: set[str] = set()
        key = lambda u: (str(u["value"]), u.get("sentence", ""))
        unsupported = [u for u in sorted(unsupported, key=lambda u: (*key(u), u["kind"]))
                       if not (key(u) in seen_values or seen_values.add(key(u)))]

        return {
            "grounded": not unsupported,
            "applicable": True,
            "unsupported_claims": unsupported,
            "evidence_count": len(evidence),
            "method": ("entity and tokenised-numeric overlap against the "
                       "retrieved evidence" + ("; sentence claims checked against "
                       "edges and entity-scoped wording" if linker is not None
                       else "; relations not checked (no linker)")),
        }


RE_ODD_NUMBER = re.compile(r"\d+(?:\.\d+)?[eE][+\-]?\d+|[\u00bc-\u00be\u2150-\u215e\u00b2\u00b3\u00b9\u2070-\u2079]")
RE_NUMBER = re.compile(r"(?<![\w.])\d[\d,]{0,8}(?:\.\d+)?(?![\w])")
RE_NUMBER_WORD = re.compile(
    r"\b(?:zero|one|two|three|four|five|six|seven|eight|nine|ten|eleven|"
    r"twelve|thirteen|fourteen|fifteen|sixteen|seventeen|eighteen|nineteen|"
    r"twenty|thirty|forty|fifty|sixty|seventy|eighty|ninety|hundred|thousand|"
    r"million|half|third|quarter|percent)\b")
# INN stems common in oncology, plus development codes (letters, optional
# hyphen, digits: "AZD9291", "MK-3475", "CC-486")
RE_DRUGLIKE = re.compile(
    r"\b(?:[a-z]{3,}(?:mab|nib|tinib|parib|ciclib|lisib|platin|taxel|rubicin|"
    r"mycin|fosfamide|trexate|citabine|abine|tecan|stat|zomib|degib|rafenib|"
    r"ximab|zumab|umab|limus|mustine)|[A-Za-z]{1,5}-?\d{2,6}[A-Za-z]?)\b")


def main() -> None:
    questions = sys.argv[1:] or [
        "Which companies are developing osimertinib?",
        "What trials evaluate Tagrisso?",
        "What does osimertinib target?",
        "Which drugs act on ALK?",
        "What is AstraZeneca running in NSCLC?",
        "What is the capital of France?",
    ]
    kg = OncoKG()
    out = []
    for q in questions:
        a = kg.answer(q)
        out.append(a.to_dict())
        print("=" * 72)
        print("Q:", q)
        print(f"   intent={a.intent}  entities="
              f"{[(e['type'], e['label']) for e in a.entities]}")
        print(f"   generated_by={a.generated_by}")
        print(a.text)
        g = a.checks
        print(f"   grounded={g['grounded']}  unsupported={g['unsupported_claims']}")
    (C.REPORTS / "query_examples.json").write_text(
        json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
    print("\n->", (C.REPORTS / "query_examples.json").relative_to(C.ROOT))


if __name__ == "__main__":
    main()
