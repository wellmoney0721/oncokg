"""Bounded HEAD versus exact ec4eede query-module comparison; no old files changed."""
import json
import sqlite3
import subprocess
import sys
import types
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))
from app import Engine

source = subprocess.check_output(["git", "show", "ec4eede:src/query.py"], cwd=ROOT).decode("utf-8")
module = types.ModuleType("r9_previous_query")
module.__file__ = str(ROOT / "src/query.py")
sys.modules[module.__name__] = module
exec(compile(source, "ec4eede:src/query.py", "exec"), module.__dict__)
engines = {"current": Engine(), "ec4eede_query": Engine()}
engines["ec4eede_query"].kg.conn.close()
engines["ec4eede_query"].kg = module.OncoKG()
for engine in engines.values():
    engine.kg.conn.close()
    engine.kg.conn = sqlite3.connect((ROOT / "data/processed/oncokg.sqlite").as_uri() + "?mode=ro", uri=True)
    engine.kg.conn.row_factory = sqlite3.Row
rows = []
for text in ["bevacizumab_awwb", "bevacizumab (awwb)", "bevacizumab awwb", "[89.Zr] trastuzumab",
             "89:Zr trastuzumab", "bev\u00e1cizumab-awwb", "bevacizumab-a.w.w.b", "bevacizumab-(a.w.w.b)",
             "bevacizumab-(awwb)", "[89 Zr] trastuzumab"]:
    row = {"text": text}
    for label, engine in engines.items():
        result = engine.explore(text, 1)
        row[label] = {k: v for k, v in result.items() if k != "groups"}
    rows.append(row)
(OUT / "predecessor_results.json").write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps({"cases": len(rows)}))
for engine in engines.values():
    engine.kg.conn.close()
