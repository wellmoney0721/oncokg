"""Round 9 independent normalization/refusal attacks; output confined to this folder."""
import json
import re
import sqlite3
import string
import subprocess
import sys
import unicodedata
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))
import query
import textrules as T
from app import Engine

engine = Engine()
engine.kg.conn.close()
engine.kg.conn = sqlite3.connect((ROOT / "data/processed/oncokg.sqlite").as_uri() + "?mode=ro", uri=True)
engine.kg.conn.row_factory = sqlite3.Row
cases = []


def add(family, texts):
    for text in texts:
        if not any(text == old for _, old in cases):
            cases.append((family, text))


add("suffix_separator", ["bevacizumab" + p + "awwb" for p in string.punctuation])
add("underscore_runs", ["bevacizumab_awwb", "bevacizumab__awwb", "bevacizumab_-awwb", "bevacizumab-_awwb",
    "bevacizumab_._awwb", "bevacizumab _ awwb", "trastuzumab_dkst", "rituximab_abbs"])
add("suffix_spelling", ["bevacizumab awwb", "bevacizumab (awwb)", "bevacizumab [awwb]", "bevacizumab {awwb}",
    "bevacizumab-a.w.w.b", "bevacizumab-aw.wb", "bevacizumab-(a.w.w.b)", "bevacizumab a.w.w.b",
    "trastuzumab dkst", "trastuzumab (dkst)", "rituximab abbs", "rituximab (abbs)"])
add("accent_normalization", ["bev\u00e1cizumab-awwb", "beva\u0301cizumab-awwb", "bevacizumab-a\u0301wwb",
    "bevacizumab-\u00e1wwb", "bevacizumab-\u1e81wwb", "tr\u00e1stuzumab-dkst", "rituximab-\u00e1bbs"])
add("format_normalization", ["bevacizumab" + p + "awwb" for p in ["\u00ad", "\u200b", "\u2060", "\ufeff"]])
add("isotope_inner_separator", ["89" + p + "Zr trastuzumab" for p in string.punctuation])
add("isotope_wrappers", ["[89.Zr] trastuzumab", "[89:Zr] trastuzumab", "89(Zr) trastuzumab",
    "89[Zr] trastuzumab", "89::Zr trastuzumab", "89: Zr trastuzumab", "89 : Zr trastuzumab",
    "89.Zr-trastuzumab", "89:Zr-trastuzumab", "89_Zr-trastuzumab", "89_Zr trastuzumab",
    "[89.Zr]-trastuzumab", "[89:Zr]-trastuzumab", "89-Zr trastuzumab", "89 Zr trastuzumab"])
add("boundaries", ["biosimilar (and), osimertinib", "biosimilar (and); osimertinib",
    "biosimilar (and)/osimertinib", "biosimilar (and)|osimertinib",
    "biosimilar (x/, and osimertinib", "biosimilar (x/; and osimertinib",
    "biosimilar, (and osimertinib)", "biosimilar; (and osimertinib)",
    "biosimilar / (and osimertinib)", "biosimilar | (and osimertinib)",
    "biosimilar and (/ osimertinib)", "biosimilar and (| osimertinib)",
    "biosimilar (x), and osimertinib", "biosimilar (x); and osimertinib",
    "(biosimilar / x), osimertinib", "(biosimilar | x); osimertinib"])
add("valid_lone_controls", ["566C", "9-ac", "5ac", "566C, osimertinib", "9-ac; osimertinib", "5ac / osimertinib",
    "biosimilar, and osimertinib", "biosimilar; and osimertinib", "biosimilar and, osimertinib",
    "bevacizumab", "trastuzumab", "osimertinib", "cemiplimab-rwlc", "dostarlimab-gxly",
    "Pegylated interferon alfa-2a", "Mvasi and bevacizumab"])
add("repaired_controls", ["bevacizumab-awwb", "bevacizumab-(awwb)", "bevacizumab-[awwb]",
    "bevacizumab\u2e3aawwb", "[89 Zr] trastuzumab", "[89Zr] trastuzumab", "89Zr trastuzumab",
    "(89 Zr) trastuzumab"])

rows = []
for family, text in cases:
    normalized = query._fold(text)
    blocked = engine.kg._resolver_blocked(normalized)
    found = engine.kg._link(normalized)
    result = engine.explore(text, 1)
    rows.append({"family": family, "text": text, "normalized": normalized,
        "punctuation_fold": re.sub(r"[^\w\s]+", "-", normalized).strip("-"),
        "raw_resolver": engine.resolve(text), "normalized_resolver": engine.resolve(normalized),
        "resolver_blocked": blocked, "item_linker": found,
        "whole_name": engine.kg._whole_name(normalized, blocked, found),
        "link_entities": engine.kg.link_entities(text),
        "map": {k: v for k, v in result.items() if k != "groups"},
        "canonical_key": T.canonical_key(text), "dictionary_hits": engine.dic["index"].get(T.canonical_key(text), [])})

qa_inputs = ["bevacizumab_awwb", "bevacizumab (awwb)", "bev\u00e1cizumab-awwb", "[89.Zr] trastuzumab",
    "bevacizumab-awwb", "89-Zr trastuzumab", "bevacizumab", "trastuzumab"]
qas = [{"text": prefix + text + "?", "response": engine.ask(prefix + text + "?")}
       for text in qa_inputs for prefix in ["Which trials evaluate ", "Which companies sponsor "]]
payload = {"head": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip(),
    "cases": rows, "qa": qas}
(OUT / "probe_results.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
summary = [{"family": r["family"], "text": r["text"], "center": r["map"].get("center", {}).get("id"),
    "refused": r["map"].get("refused"), "resolver_tiers": [c["tier"] for c in r["raw_resolver"]["components"]],
    "blocked": r["resolver_blocked"], "whole_name": r["whole_name"]} for r in rows]
(OUT / "probe_summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps({"count": len(rows), "qa_count": len(qas), "families": sorted({r["family"] for r in rows})}))
engine.kg.conn.close()
