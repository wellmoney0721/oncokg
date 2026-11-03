"""Round 7: shared refusal gaps, whole-name bypass, and list isolation.

This script owns only artifacts alongside itself and replaces in-process DB
connections with mode=ro. Previous methods are read from git, never checked out.
"""
import ast
import hashlib
import json
import os
import socket
import sqlite3
import subprocess
import sys
import textwrap
import time
import types
import urllib.error
import urllib.request
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path.cwd()
OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / "src"))
import query
import textrules as T
from app import Engine


def save(name, value):
    (OUT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding="utf-8")


def engine_at(ref=None):
    engine = Engine()
    engine.kg.conn.close()
    engine.kg.conn = sqlite3.connect((ROOT / "data/processed/oncokg.sqlite").as_uri() + "?mode=ro", uri=True)
    engine.kg.conn.row_factory = sqlite3.Row
    if ref:
        source = subprocess.check_output(["git", "show", ref + ":src/query.py"], cwd=ROOT).decode("utf-8")
        tree = ast.parse(source)
        namespace = dict(query.__dict__)
        for node in tree.body:
            if isinstance(node, ast.Assign) and any(isinstance(target, ast.Name) and target.id == "_JOINERS" for target in node.targets):
                namespace["_JOINERS"] = ast.literal_eval(node.value)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef) and node.name in {"link_entities", "_drug_spans"}:
                exec(compile(textwrap.dedent(ast.get_source_segment(source, node)), ref + ":src/query.py", "exec"), namespace)
                setattr(engine.kg, node.name, types.MethodType(namespace[node.name], engine.kg))
    return engine


current, previous = engine_at(), engine_at("b7a00f9")
cases = []


def add(family, values):
    cases.extend((family, value) for value in values)


suffix = "bevacizumab-awwb"
add("suffix_wrappers", [suffix, "(" + suffix + ")", "[" + suffix + "]", '"' + suffix + '"',
    "'" + suffix + "'", "\u201c" + suffix + "\u201d", "<" + suffix + ">", suffix + "\u3002",
    "bevacizumab - (awwb)", "bevacizumab (awwb)", "bevacizumab [awwb]", suffix + "?", suffix + "!"])
add("suffix_dashes", ["bevacizumab" + sep + "awwb" for sep in ["-", "\u2010", "\u2011", "\u2012", "\u2013", "\u2014", "\u2212", "\uff0d"]])
add("suffix_case", ["bevacizumab-" + suffix for suffix in ["awwb", "AWWB", "Awwb", "awWb", "bvzr", "Pfizer", "pfizer"]])
add("qualifier_unicode", [prefix + " bevacizumab" for prefix in ["biosimilar", "bio-similar", "bio similar", "bio\u2010similar", "bio\u2011similar", "bio\u2014similar", "bi\u00f3similar", "\uff42\uff49\uff4f\uff53\uff49\uff4d\uff49\uff4c\uff41\uff52"]])
add("tracer", ["89Zr-trastuzumab", "[89Zr] trastuzumab", "89Zr trastuzumab", "89Zr\u2011trastuzumab", "89Zr\u2014trastuzumab", '"[89Zr] trastuzumab"', "([89Zr] trastuzumab)", "[89Zr]-trastuzumab", "trastuzumab (89Zr)", "trastuzumab-[89Zr]"])
add("whole_name_lists", [drug + sep + salt for drug, salt in [("Erlotinib", "hydrochloride"), ("osimertinib", "mesylate")] for sep in [" ", ", ", "; ", "\uff0c", "\uff1b", "\u3001", "/", "|", " and "]])
add("accepted_separate_items", ["biosimilar anastrozole, Arimidex", "biosimilar anastrozole/Arimidex", "Mvasi and bevacizumab", "bevacizumab-awwb, bevacizumab", "bevacizumab-awwb and bevacizumab", "bevacizumab-awwb/Avastin", "liposomal doxorubicin, osimertinib", "osimertinib, liposomal doxorubicin", "EGFR biosimilar bevacizumab", "AstraZeneca biosimilar bevacizumab"])
add("carry_boundary", ["liposomal and doxorubicin", "liposomal, doxorubicin", "liposomal, and doxorubicin", "liposomal and, doxorubicin", "biosimilar, and osimertinib", "biosimilar; and osimertinib", "biosimilar / and osimertinib", "biosimilar | and osimertinib", "biosimilar and / osimertinib", "doxorubicin in nanoparticle and liposomal formulations"])
add("whole_stored_controls", ["CP-358,774", "Rapamycin, 42-o-(2-hydroxyethyl)-", "Paclitaxel conjugate with poly-l-glutamic acid", "Pegylated interferon alfa-2a"])
add("whole_key_only", ["is a", "isa", "DOX, ORUBICIN", "bevacizumab - awwb?", "bevacizumab-awwb? EGFR"])


def summary_map(engine, text):
    response = engine.explore(text, 1)
    return {k: v for k, v in response.items() if k != "groups"}


rows = []
for family, text in cases:
    blocked = current.kg._resolver_blocked(text)
    rows.append({"family": family, "text": text, "distinct": T.is_distinct_product(text), "tracer": T.is_radiotracer(text),
        "resolver": current.resolve(text), "resolver_blocked": blocked,
        "whole_name": current.kg._whole_name(text, blocked, current.kg._link(text)), "item_linker": current.kg._link(text),
        "link_entities": current.kg.link_entities(text), "map": summary_map(current, text),
        "previous_b7a00f9": summary_map(previous, text)})

qa_inputs = ["Which trials evaluate (bevacizumab-awwb)?", "Which companies sponsor (bevacizumab-awwb)?",
    "Which trials evaluate bevacizumab\u2011awwb?", "Which trials evaluate bio\u2011similar bevacizumab?",
    "Which trials evaluate 89Zr trastuzumab?", 'Which trials evaluate "bevacizumab-awwb"?',
    "Which trials evaluate Erlotinib, hydrochloride?", "Which trials evaluate osimertinib,mesylate?",
    "Which trials evaluate bevacizumab-awwb?", "Which trials evaluate [89Zr] trastuzumab?"]
qas = [{"text": text, "result": current.ask(text)} for text in qa_inputs]
save("fresh_results.json", {"head": subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT).decode().strip(), "count": len(rows), "cases": rows, "qa": qas})
save("fresh_summary.json", [{"family": r["family"], "text": r["text"], "resolver": [{"tier": c["tier"], "drug_id": c.get("drug_id")} for c in r["resolver"]["components"]], "item_linker": r["item_linker"], "map": r["map"], "previous": r["previous_b7a00f9"]} for r in rows])
save("dictionary_evidence.json", [{"text": text, "canonical_key": T.canonical_key(text),
    "hits": current.dic["index"].get(T.canonical_key(text), []),
    "exact_casefold_alias_match": any(h["alias"].casefold() == text.casefold() for h in current.dic["index"].get(T.canonical_key(text), []))}
    for text in ["bevacizumab-awwb?", "(bevacizumab-awwb)", "89Zr trastuzumab", "Erlotinib, hydrochloride", "osimertinib,mesylate", "is a", "CP-358,774", "Rapamycin, 42-o-(2-hydroxyethyl)-"]])
print(json.dumps({"cases": len(rows), "qa": len(qas)}, ensure_ascii=True))

port = 8920
probe = socket.socket()
if probe.connect_ex(("127.0.0.1", port)) == 0:
    probe.close()
    raise RuntimeError("Owned HTTP test port is occupied; refusing to replace existing server")
probe.close()
env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONIOENCODING="utf-8")
temp = OUT / "tmp"
temp.mkdir(exist_ok=True)
env.update(TEMP=str(temp), TMP=str(temp))
log = (OUT / "http_server.txt").open("w", encoding="utf-8")
server = subprocess.Popen([sys.executable, "-B", "-u", "src/app.py", str(port)], cwd=ROOT, env=env, stdout=log, stderr=subprocess.STDOUT, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
http_results = []
life = {"pid": server.pid, "port": port, "command": [sys.executable, "-B", "-u", "src/app.py", str(port)]}
try:
    deadline = time.monotonic() + 20
    while True:
        try:
            with urllib.request.urlopen(f"http://127.0.0.1:{port}/", timeout=1) as response:
                served = response.read()
            life["served_html_matches_worktree"] = served == (ROOT / "web/try.html").read_bytes()
            break
        except Exception:
            if server.poll() is not None or time.monotonic() > deadline:
                raise
            time.sleep(0.1)
    map_inputs = ["bevacizumab-awwb", "(bevacizumab-awwb)", "[bevacizumab-awwb]", '"bevacizumab-awwb"',
        "bevacizumab\u2011awwb", "bio-similar bevacizumab", "bio\u2011similar bevacizumab", "89Zr-trastuzumab", "89Zr trastuzumab",
        "Erlotinib, hydrochloride", "Erlotinib hydrochloride", "Erlotinib/hydrochloride", "osimertinib,mesylate", "biosimilar, and osimertinib", "bevacizumab-awwb?", "bevacizumab-awwb!", "is a"]
    for endpoint, text in [(endpoint, text) for text in map_inputs for endpoint in ["explore", "resolve"]] + [("ask", text) for text in qa_inputs]:
        payload = {"text": text}
        req = urllib.request.Request(f"http://127.0.0.1:{port}/api/{endpoint}", data=json.dumps(payload).encode(), headers={"Content-Type": "application/json"})
        started = time.perf_counter()
        with urllib.request.urlopen(req, timeout=15) as response:
            raw = response.read()
            http_results.append({"endpoint": endpoint, "input": payload, "status": response.status, "elapsed_seconds": time.perf_counter() - started, "response": json.loads(raw)})
    save("http_results.json", http_results)
finally:
    server.terminate()
    try:
        server.wait(timeout=5)
    except subprocess.TimeoutExpired:
        server.kill()
        server.wait(timeout=5)
    log.close()
    life["returncode_after_cleanup"] = server.returncode
    check = socket.socket()
    life["port_closed"] = check.connect_ex(("127.0.0.1", port)) != 0
    check.close()
    save("http_lifecycle.json", life)
    current.kg.conn.close()
    previous.kg.conn.close()
print(json.dumps({"http_requests": len(http_results), "all_200": all(r["status"] == 200 for r in http_results), "port_closed": life["port_closed"]}))
