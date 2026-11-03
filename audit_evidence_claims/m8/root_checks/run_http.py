"""Round 5 HTTP and QA regression checks; all output stays beside this file."""
import ast
import hashlib
import json
import os
from pathlib import Path
import re
import socket
import subprocess
import sys
import time
import types
import urllib.error
import urllib.request

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
PORT = 8931
BASE = f"http://127.0.0.1:{PORT}"
sys.path.insert(0, str(ROOT / "src"))
os.environ["PYTHONDONTWRITEBYTECODE"] = "1"
DB = ROOT / "data/processed/oncokg.sqlite"

def git(*args):
    p = subprocess.run(["git", *args], cwd=ROOT, capture_output=True)
    return {"code": p.returncode, "stdout": p.stdout.decode("utf-8", "replace"),
            "stderr": p.stderr.decode("utf-8", "replace")}

def post(path, payload):
    req = urllib.request.Request(BASE + path, data=json.dumps(payload).encode(),
                                 headers={"Content-Type": "application/json"})
    try:
        res = urllib.request.urlopen(req, timeout=30)
    except urllib.error.HTTPError as e:
        res = e
    return {"status": res.status, "body": json.loads(res.read())}

before = hashlib.sha256(DB.read_bytes()).hexdigest()
initial = {"head": git("rev-parse", "HEAD"), "status": git("status", "--short"),
           "db_sha256": before}
(OUT / "initial_integrity.json").write_text(json.dumps(initial, indent=2), encoding="utf-8")
with socket.socket() as s:
    assert s.connect_ex(("127.0.0.1", PORT)) != 0, "audit port already occupied"

log = (OUT / "server.txt").open("w", encoding="utf-8")
proc = subprocess.Popen([sys.executable, "-B", "-u", "src/app.py", str(PORT)], cwd=ROOT,
                        env=os.environ.copy(), stdout=log, stderr=subprocess.STDOUT,
                        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
try:
    for _ in range(100):
        if proc.poll() is not None:
            raise RuntimeError("server exited")
        try:
            urllib.request.urlopen(BASE, timeout=1).read()
            break
        except OSError:
            time.sleep(.1)
    else:
        raise RuntimeError("server unavailable")
    # Re-run every original HTTP case without executing a writer in m1.
    original = (ROOT / "audit_evidence_claims/m1/http_audit.py").read_text(encoding="utf-8")
    adapted = original.replace("8876", str(PORT)).replace("bfcb83d", "514929c")
    (OUT / "http_audit.py").write_text(adapted.replace("OUT.parents[1]", "OUT.parents[2]"), encoding="utf-8")
    run = subprocess.run([sys.executable, "-B", str(OUT / "http_audit.py")], cwd=ROOT,
                         capture_output=True, env={**os.environ, "PYTHONIOENCODING": "utf-8"})
    (OUT / "http_stdout.txt").write_bytes(run.stdout + run.stderr)
    assert run.returncode == 0

    regression = subprocess.run([sys.executable, "-B", str(OUT / "regression_http.py")],
        cwd=ROOT, capture_output=True, env={**os.environ, "PYTHONIOENCODING":"utf-8"})
    (OUT / "regression_http_stdout.txt").write_bytes(regression.stdout + regression.stderr)
    assert regression.returncode == 0

    # Load the previous linker/answer module in memory; use the identical database.
    old = types.ModuleType("m2b_old_query")
    old.__file__ = str(ROOT / "src/query.py")
    sys.modules[old.__name__] = old
    code = subprocess.run(["git", "show", "bfcb83d:src/query.py"], cwd=ROOT,
                          capture_output=True, check=True).stdout.decode("utf-8")
    exec(compile(code, old.__file__, "exec"), old.__dict__)
    baseline = old.OncoKG()
    baseline.conn.execute("PRAGMA query_only=ON")
    html = (ROOT / "web/try.html").read_text(encoding="utf-8")
    questions = json.loads(re.search(r"const EX2 = (\[.*?\]);", html, re.S).group(1))
    # Verify CLI/dashboard demos are covered by the page list, without running
    # their entrypoints (which write tracked report/dashboard artifacts).
    sources = {}
    for filename, variable in [("src/query.py", "questions"),
                               ("src/make_dashboard_data.py", "demo_questions")]:
        parsed = ast.parse((ROOT / filename).read_text(encoding="utf-8"))
        assignments = [n for n in ast.walk(parsed) if isinstance(n, ast.Assign)
                       and any(isinstance(t, ast.Name) and t.id == variable for t in n.targets)]
        value = assignments[-1].value
        if isinstance(value, ast.BoolOp):
            value = value.values[-1]
        sources[filename] = ast.literal_eval(value)
        assert set(sources[filename]) <= set(questions)
    answers = []
    for question in questions:
        previous = baseline.answer(question, use_llm=False).to_dict()
        current = post("/api/ask", {"text": question})
        answers.append({"question": question, "http_status": current["status"],
                        "identical_to_bfcb83d": current["body"] == previous,
                        "current": current["body"], "previous": previous})
    baseline.conn.close()
    (OUT / "http_demo_results.json").write_text(json.dumps({"source_lists": sources,
        "answers": answers}, indent=2, ensure_ascii=False), encoding="utf-8")
    print(json.dumps({"demo_questions": len(answers),
        "all_http_200": all(a["http_status"] == 200 for a in answers),
        "all_identical_to_bfcb83d": all(a["identical_to_bfcb83d"] for a in answers)}))
finally:
    proc.terminate()
    proc.wait(timeout=10)
    log.close()
    with socket.socket() as s:
        port_closed = s.connect_ex(("127.0.0.1", PORT)) != 0
    after = hashlib.sha256(DB.read_bytes()).hexdigest()
    (OUT / "http_lifecycle.json").write_text(json.dumps({"pid": proc.pid, "port": PORT,
        "server_exit": proc.returncode, "port_closed": port_closed,
        "database_unchanged": after == before, "db_sha256_before": before,
        "db_sha256_after": after}, indent=2), encoding="utf-8")
