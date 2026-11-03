"""A local page for trying the pipeline by hand.

    python src/app.py            then open http://localhost:8765

Four boxes: type an intervention string the way a registry would write it and see
how the resolver reads it, or ask a question and see the grounded answer with its
evidence, give a structured answer (claims citing evidence edges) and see which
claims the graph supports and the answer written from them, or paste free prose and
see what the auxiliary word-order check flags. All three call
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
                                     "/api/structured"):
                    return self._send(404, b"{}", "application/json")
                with engine.lock:
                    if self.path == "/api/resolve":
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
