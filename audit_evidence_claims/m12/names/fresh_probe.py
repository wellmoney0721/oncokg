"""Round 6 independent adversarial cases. Writes only alongside this file."""
import ast
import json
import sqlite3
import subprocess
import sys
import textwrap
import types
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))
import query
import textrules as T
from app import Engine


def engine_at(ref=None):
    e = Engine()
    e.kg.conn.close()
    e.kg.conn = sqlite3.connect((ROOT / "data/processed/oncokg.sqlite").as_uri() + "?mode=ro", uri=True)
    e.kg.conn.row_factory = sqlite3.Row
    if ref:
        source = subprocess.check_output(["git", "show", ref + ":src/query.py"], cwd=ROOT).decode("utf-8")
        tree = ast.parse(source)
        ns = dict(query.__dict__)
        for node in tree.body:
            if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "_JOINERS" for t in node.targets):
                ns["_JOINERS"] = ast.literal_eval(node.value)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name in {"link_entities", "_drug_spans", "_qualified_drug_spans"}:
                exec(compile(textwrap.dedent(ast.get_source_segment(source, node)), ref + ":src/query.py", "exec"), ns)
                setattr(e.kg, node.name, types.MethodType(ns[node.name], e.kg))
    return e


cur, prior = engine_at(), engine_at("514929c")
suffix = "bevacizumab-awwb"
inputs = []


def add(family, values):
    for value in values:
        inputs.append((family, value))


add("punctuation", [suffix, suffix + ".", suffix + "?", suffix + "\u3002", "\u3002" + suffix,
    suffix + "\u2014", "\u2014" + suffix, suffix + "-", "-" + suffix, suffix + "\u00ae",
    "(" + suffix + ")", "[" + suffix + "]", '"' + suffix + '"', suffix + ")",
    "bevacizumab\u2010awwb", "bevacizumab\u2014awwb", "bevacizumab--awwb", "bevacizumab - (awwb)",
    "[89Zr] trastuzumab", '"[89Zr] trastuzumab"', "([89Zr] trastuzumab)"])
add("joined_separators", [a + sep + b for a, b in [("osimertinib", "EGFR"),
    ("Erlotinib", "hydrochloride"), ("biosimilar anastrozole", "Arimidex"),
    ("bevacizumab-awwb", "osimertinib")] for sep in ["/", "|", "/ ", " /", " / ", " | ", ",", ";", "\uff0c", "\uff1b", "\u3001", " and "]])
add("joined_separators", ["bevacizumab - awwb/osimertinib", "bevacizumab - awwb|osimertinib",
    "bevacizumab - awwb / osimertinib", "bevacizumab - awwb | osimertinib"])
add("carry", ["liposomal and nanoparticle formulation of doxorubicin",
    "liposomal and sustained release doxorubicin", "liposomal and EGFR and doxorubicin",
    "liposomal and sustained release and doxorubicin", "liposomal and/or doxorubicin",
    "Mvasi and bevacizumab", "(Mvasi) and bevacizumab", "Mvasi\u00ae and bevacizumab",
    "Abraxane and paclitaxel", "liposomal, doxorubicin", "liposomal, and doxorubicin",
    "liposomal / and doxorubicin", "liposomal and Mvasi and doxorubicin",
    "doxorubicin in nanoparticle and liposomal formulations",
    "doxorubicin in a sustained release and liposomal formulation",
    "paclitaxel as injection and albumin bound nanoparticles",
    "bevacizumab as an investigational and biosimilar product"])
add("distance", [" ".join(["context"] * n + [q] + ["context"] * n) for n in [0, 4, 8, 16]
    for q in ["bevacizumab - awwb", "[89Zr] trastuzumab", "liposomal doxorubicin",
              "generic version of bevacizumab"]])


def summarize(e, text):
    m = e.explore(text, 1)
    return {"linker": e.kg.link_entities(text), "map": {k: v for k, v in m.items() if k != "groups"},
            "groups": [{k: v for k, v in g.items() if k != "items"} for g in m.get("groups", [])]}


rows = []
for family, text in inputs:
    rows.append({"family": family, "input": text,
                 "distinct": T.is_distinct_product(text), "tracer": T.is_radiotracer(text),
                 "resolver": cur.resolve(text), "current": summarize(cur, text),
                 "previous_514929c": summarize(prior, text)})

qa = []
for text in ["Which trials evaluate bevacizumab-awwb\u3002?",
             "Which companies sponsor bevacizumab-awwb\u3002?",
             "Which trials evaluate bevacizumab - awwb/osimertinib?",
             "Which companies sponsor bevacizumab - awwb/osimertinib?",
             "Which trials evaluate (bevacizumab-awwb)?",
             "Which trials evaluate Erlotinib/hydrochloride?",
             "Which trials evaluate biosimilar anastrozole/Arimidex?",
             "Which trials evaluate doxorubicin in nanoparticle and liposomal formulations?"]:
    qa.append({"input": text, "answer": cur.ask(text)})

result = {"head": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT).decode().strip(),
          "previous_linker_ref": "514929c", "count": len(rows), "cases": rows, "qa": qa}
OUT.joinpath("fresh_results.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
summary = [{"input": r["input"], "current_center": r["current"]["map"].get("center", {}).get("id"),
            "prior_center": r["previous_514929c"]["map"].get("center", {}).get("id"),
            "refused": r["current"]["map"].get("refused"),
            "resolver": [(c["component"], c["tier"], c.get("drug_id")) for c in r["resolver"]["components"]]}
           for r in rows]
OUT.joinpath("fresh_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps({"cases": len(rows), "qa": [{"input": r["input"], "count": len(r["answer"]["evidence"]),
    "first_edge": next((x["edge_id"] for x in r["answer"]["evidence"]), None)} for r in qa]}, ensure_ascii=True))
for e in [cur, prior]:
    e.kg.conn.close()
