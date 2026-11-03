"""A local page for trying the pipeline by hand.

    python src/app.py            then open http://localhost:8765

A relation map (a node and everything a live edge ties it to, click to move on),
then four boxes: type an intervention string the way a registry would write it and see
how the resolver reads it, or ask a question and see the grounded answer with its
evidence, give a structured answer (claims citing evidence edges) and see which
claims the graph supports and the answer written from them, or paste free prose and
see what the auxiliary word-order check flags. All of them call
the functions the pipeline uses (resolve_drug_string, OncoKG.answer,
OncoKG.check_groundedness) on the built artefacts, so what the page shows is what the
pipeline would do. Nothing is written; the language model is never called.
"""
from __future__ import annotations

import json
import sqlite3
import sys
import threading
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import config as C
import normalize as N
import textrules as T
from query import OncoKG

PAGE = C.WEB / "try.html"
PORT = 8765


class Engine:
    def __init__(self):
        self.kg = OncoKG()
        # A browser opens spare connections it may never use, which would stall a
        # single-threaded server; requests are threaded, the engine is not.
        self.kg.conn.close()
        self.kg.conn = sqlite3.connect(C.PROCESSED / "oncokg.sqlite", check_same_thread=False)
        self.kg.conn.row_factory = sqlite3.Row
        self.lock = threading.Lock()
        self.dic = self.kg.dic
        self.index_keys = self.kg.index_keys
        target_rows, _, _ = N._load("targets")
        self.target_keys = N.target_guard_keys(target_rows, self.dic)

    def resolve(self, text: str) -> dict:
        out = N.resolve_drug_string(text, self.dic, self.index_keys, self.target_keys)
        for c in out["components"]:
            d = self.dic["drugs"].get(c.get("drug_id") or "")
            if d:
                c["drug"] = {k: d.get(k) for k in
                             ("name", "drug_type", "max_phase_overall", "max_phase_in_nsclc")}
                c["drug"]["mechanisms"] = [m.get("mechanismOfAction") if isinstance(m, dict) else m
                                           for m in (d.get("mechanisms") or [])][:3]
                c["drug"]["trials"] = self.kg.conn.execute(
                    "SELECT COUNT(*) FROM edge WHERE rel='EVALUATES' AND dst=? AND retired_at IS NULL",
                    (d["drug_id"],)).fetchone()[0]
                par = self.dic["drugs"].get(d.get("parent_molecule") or "")
                if par:
                    c["drug"]["parent"] = {"name": par["name"], "trials": self.kg.conn.execute(
                        "SELECT COUNT(*) FROM edge WHERE rel='EVALUATES' AND dst=? AND retired_at IS NULL",
                        (par["drug_id"],)).fetchone()[0]}
            if c.get("candidates"):
                c["candidate_names"] = [
                    (self.dic["drugs"].get(x) or {}).get("name", x) for x in c["candidates"]]
        return out

    def explore(self, text: str, per_group: int = 30) -> dict:
        """One live node and the live nodes its live edges tie it to, grouped by relation.

        `text` is a node id or a name the question linker reads as one entity. A name
        the linker refuses (a biosimilar, a reformulation, a tracer) is reported, never
        mapped to the originator. Each group keeps `per_group` neighbours, sorted as the
        page states: trials by start date (latest first), drugs by trials in the graph,
        sponsors by trials they lead, disease targets by association score. Sponsorship
        keeps its role (lead sponsor or collaborator)."""
        conn = self.kg.conn
        also: list = []
        matched = None
        row = conn.execute("SELECT id FROM node WHERE id=? AND retired_at IS NULL",
                           (text,)).fetchone()
        if row:
            nid = row["id"]
        else:
            ents = self.kg.link_entities(text)
            refused = [e for e in ents if e["type"] == "Refused"]
            hits = [e for e in ents if e.get("id") and e["type"] != "Refused"]
            if not hits:
                if refused:
                    return {"refused": refused[0]["label"], "why": refused[0]["why"]}
                return {"not_found": text}
            nid, matched = hits[0]["id"], hits[0].get("matched_alias") or hits[0].get("matched_text")
            also = [{"id": e["id"], "type": e["type"], "label": e["label"]} for e in hits[1:]]
            # the same words may also name an organisation or a target the linker
            # passed over because a drug alias came first ("Roche" is a folic acid alias)
            key = T.canonical_key(text)
            for cid in self.kg.companies.get(key, []):
                if cid != nid:
                    lab = conn.execute("SELECT label FROM node WHERE id=? AND retired_at IS NULL",
                                       (cid,)).fetchone()
                    if lab:
                        also.append({"id": cid, "type": "Company", "label": lab["label"]})
            t = self.kg.targets.get(text.strip().lower())
            if t and t["target_id"] != nid:
                also.append({"id": t["target_id"], "type": "Target", "label": t["symbol"]})
            also += [{"refused": e["label"]} for e in refused]
        node = conn.execute("SELECT id, type, label, props FROM node WHERE id=? "
                            "AND retired_at IS NULL", (nid,)).fetchone()
        if node is None:                              # a name can outlive its node
            return {"not_found": text}
        rows = conn.execute(
            "SELECT e.id AS eid, e.rel, e.src, e.props AS eprops, n.id, n.type, n.label, "
            "n.props AS nprops FROM edge e JOIN node n "
            "ON n.id = CASE WHEN e.src=? THEN e.dst ELSE e.src END "
            "WHERE (e.src=? OR e.dst=?) AND e.retired_at IS NULL AND n.retired_at IS NULL",
            (nid, nid, nid)).fetchall()
        drug_ids = list({r["id"] for r in rows if r["type"] == "Drug"} | {nid})
        trials = {}
        for i in range(0, len(drug_ids), 500):
            chunk = drug_ids[i:i + 500]
            trials.update(conn.execute(               # live trials only
                "SELECT e.dst, COUNT(*) FROM edge e JOIN node t ON t.id = e.src "
                "WHERE e.rel='EVALUATES' AND e.retired_at IS NULL AND t.retired_at IS NULL "
                f"AND e.dst IN ({','.join('?' * len(chunk))}) GROUP BY e.dst", chunk).fetchall())
        groups: dict = {}
        for r in rows:
            ep, np_ = _obj(r["eprops"]), _obj(r["nprops"])
            item = {"id": r["id"], "type": r["type"], "label": r["label"], "edge_id": r["eid"]}
            role = ep.get("role") if r["rel"] == "SPONSORS" else None
            if r["type"] == "Drug":
                item["trials"] = trials.get(r["id"], 0)
                item["max_phase"] = np_.get("max_phase_overall")
            if r["rel"] == "SPONSORS_TRIAL_OF":
                item["weight"] = ep.get("evidence_trials") or 0
                item["sponsor_class"] = ep.get("sponsor_class")
            elif r["type"] == "Trial":
                item.update({k: np_.get(k) for k in ("phases", "status", "title", "start_date", "url")})
                item["weight"] = str(np_.get("start_date") or "")
            elif r["type"] == "Drug":
                item["weight"] = item["trials"]
            elif r["rel"] == "ASSOCIATED_WITH":
                score = ep.get("association_score")
                item["score"] = score if isinstance(score, (int, float)) else None
                item["weight"] = item["score"] or 0
            else:
                item["weight"] = 0
            if r["rel"] == "ACTS_ON":
                item["action"] = ep.get("action_type")
            if role:
                item["role"] = role
            key = (r["rel"], "out" if r["src"] == nid else "in", r["type"], role)
            groups.setdefault(key, []).append(item)
        out = []
        for (rel, direction, ntype, role), items in groups.items():
            items.sort(key=lambda x: x["label"] or "")              # names A to Z
            items.sort(key=lambda x: x["weight"], reverse=True)     # then by the stated weight
            out.append({"rel": rel, "dir": direction, "type": ntype, "role": role,
                        "total": len(items), "items": items[:per_group]})
        out.sort(key=lambda g: -g["total"])
        props = _obj(node["props"])
        return {"center": {"id": node["id"], "type": node["type"], "label": node["label"],
                           "matched_text": matched,
                           "trials": trials.get(node["id"], 0) if node["type"] == "Drug" else None,
                           "props": {k: props.get(k) for k in
                                     ("max_phase_overall", "drug_type", "phases", "status",
                                      "title", "url", "start_date") if props.get(k) is not None}},
                "also": also, "groups": out}

    def ask(self, question: str) -> dict:
        return self.kg.answer(question, use_llm=False).to_dict()

    def structured(self, question: str, payload: str) -> dict:
        """Check a structured answer (claims citing edges) and write the answer from it."""
        kg = self.kg
        entities = kg.link_entities(question)
        evidence = kg.retrieve(kg.classify(question, entities), entities)
        res = kg.verify_structured(payload, evidence)
        res["evidence"] = [{"edge_id": e.edge_id, "statement": e.statement} for e in evidence]
        return res

    def check(self, question: str, answer: str) -> dict:
        """Check an answer someone else wrote against the evidence for the question."""
        kg = self.kg
        entities = kg.link_entities(question)
        intent = kg.classify(question, entities)
        evidence = kg.retrieve(intent, entities)
        checks = kg.check_groundedness(answer, evidence, entities, generated=True,
                                       vocabulary=set(self.dic["index"]),
                                       linker=kg.link_entities)
        return {"intent": intent, "entities": entities, "checks": checks,
                "evidence": [{"statement": e.statement, "source_record": e.source_record,
                              "source": e.source, "url": e.url} for e in evidence[:8]],
                "evidence_count": len(evidence)}


def _obj(raw) -> dict:
    """Stored props as a dict; anything else (null, a list, broken JSON) as empty."""
    try:
        v = json.loads(raw) if raw else {}
    except ValueError:
        return {}
    return v if isinstance(v, dict) else {}


def make_handler(engine: Engine):
    class Handler(BaseHTTPRequestHandler):
        def _send(self, code: int, body: bytes, ctype: str):
            self.send_response(code)
            self.send_header("Content-Type", ctype)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)

        def do_GET(self):
            if self.path in ("/", "/index.html"):
                self._send(200, PAGE.read_bytes(), "text/html; charset=utf-8")
            else:
                self._send(404, b"not found", "text/plain")

        def do_POST(self):
            try:
                n = int(self.headers.get("Content-Length") or 0)
                body = json.loads(self.rfile.read(min(n, 20000)) or b"{}")
                text = str(body.get("text") or "").strip()[:500]
                if not text:
                    raise ValueError("empty input")
                if self.path not in ("/api/resolve", "/api/ask", "/api/check",
                                     "/api/structured", "/api/explore"):
                    return self._send(404, b"{}", "application/json")
                with engine.lock:
                    if self.path == "/api/explore":
                        res = engine.explore(text)
                    elif self.path == "/api/resolve":
                        res = engine.resolve(text)
                    elif self.path == "/api/ask":
                        res = engine.ask(text)
                    elif self.path == "/api/structured":
                        answer = str(body.get("answer") or "").strip()[:20000]
                        if not answer:
                            raise ValueError("empty answer")
                        res = engine.structured(text, answer)
                    else:
                        answer = str(body.get("answer") or "").strip()[:4000]
                        if not answer:
                            raise ValueError("empty answer")
                        res = engine.check(text, answer)
                self._send(200, json.dumps(res, ensure_ascii=False,
                                           allow_nan=False).encode("utf-8"),
                           "application/json; charset=utf-8")
            except Exception as e:  # show the reason on the page, not a dead request
                self._send(400, json.dumps({"error": str(e)}, ensure_ascii=False).encode("utf-8"),
                           "application/json; charset=utf-8")

        def log_message(self, *a):
            pass
    return Handler


def main() -> None:
    port = int(sys.argv[1]) if len(sys.argv) > 1 else PORT
    engine = Engine()
    print(f"OncoKG try-it page: http://localhost:{port}", flush=True)
    ThreadingHTTPServer(("127.0.0.1", port), make_handler(engine)).serve_forever()


if __name__ == "__main__":
    main()
