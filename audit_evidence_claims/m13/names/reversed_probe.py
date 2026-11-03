"""Follow-up: qualifiers detached to the right of a drug by a listing word."""
import ast
import json
import sqlite3
import subprocess
import sys
import textwrap
import types
from pathlib import Path

sys.dont_write_bytecode = True
OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
sys.path.insert(0, str(ROOT / "src"))
import query
from app import Engine

cur, old = Engine(), Engine()
for e in (cur, old):
    e.kg.conn.close()
    e.kg.conn = sqlite3.connect((ROOT / "data/processed/oncokg.sqlite").as_uri() + "?mode=ro", uri=True)
    e.kg.conn.row_factory = sqlite3.Row
source = subprocess.check_output(["git", "show", "514929c:src/query.py"], cwd=ROOT).decode("utf-8")
tree, ns = ast.parse(source), dict(query.__dict__)
for node in tree.body:
    if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "_JOINERS" for t in node.targets):
        ns["_JOINERS"] = ast.literal_eval(node.value)
for node in ast.walk(tree):
    if isinstance(node, ast.FunctionDef) and node.name in {"link_entities", "_drug_spans", "_qualified_drug_spans"}:
        exec(compile(textwrap.dedent(ast.get_source_segment(source, node)), "514929c:src/query.py", "exec"), ns)
        setattr(old.kg, node.name, types.MethodType(ns[node.name], old.kg))

inputs = [
    "doxorubicin in nanoparticle and liposomal formulations",
    "doxorubicin in nanoparticle and liposomal",
    "doxorubicin (nanoparticle and liposomal formulation)",
    "doxorubicin (sustained-release and liposomal)",
    "bevacizumab (investigational and biosimilar)",
    "bevacizumab (generic and biosimilar formulation)",
    "paclitaxel (investigational and albumin-bound nanoparticle formulation)",
    "doxorubicin formulated as sustained-release and liposomal",
    "doxorubicin (nanoparticle liposomal formulation)",
    "bevacizumab (investigational biosimilar)",
    "liposomal and nanoparticle formulation of doxorubicin",
]
rows = []
for text in inputs:
    a, b = cur.explore(text, 1), old.explore(text, 1)
    q = "Which trials evaluate " + text + "?"
    answer = cur.ask(q)
    rows.append({"input": text, "resolver": cur.resolve(text), "linker": cur.kg.link_entities(text),
                 "map": a, "previous_514929c": b, "qa_input": q, "qa": answer})
OUT.joinpath("reversed_results.json").write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps([{"input": r["input"], "center": r["map"].get("center", {}).get("id"),
    "prior": r["previous_514929c"].get("center", {}).get("id"),
    "resolver": [(c["tier"], c.get("drug_id")) for c in r["resolver"]["components"]],
    "evidence": len(r["qa"]["evidence"]), "first_edge": next((x["edge_id"] for x in r["qa"]["evidence"]), None)}
    for r in rows], ensure_ascii=True))
for e in (cur, old):
    e.kg.conn.close()
