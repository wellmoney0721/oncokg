"""Own an unchanged CLI server; independently verify round-3 name and UI cases."""
import hashlib
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
PORT = 8897
BASE = f"http://127.0.0.1:{PORT}"
DB = ROOT / "data/processed/oncokg.sqlite"


def post(path, text):
    req = urllib.request.Request(BASE + path,
        data=json.dumps({"text": text}).encode(),
        headers={"Content-Type": "application/json"})
    try:
        response = urllib.request.urlopen(req, timeout=30)
    except urllib.error.HTTPError as error:
        response = error
    return {"path": path, "text": text, "status": response.status,
            "body": json.loads(response.read())}


before = hashlib.sha256(DB.read_bytes()).hexdigest()
with socket.socket() as sock:
    assert sock.connect_ex(("127.0.0.1", PORT)) != 0, "audit port occupied"
env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1", "PYTHONUTF8": "1",
       "PYTHONIOENCODING": "utf-8"}
with (OUT / "attack_server.txt").open("w", encoding="utf-8") as log:
    proc = subprocess.Popen([sys.executable, "-B", "-u", "src/app.py", str(PORT)],
        cwd=ROOT, env=env, stdout=log, stderr=subprocess.STDOUT,
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    try:
        for _ in range(100):
            assert proc.poll() is None, "server exited"
            try:
                urllib.request.urlopen(BASE, timeout=1).read()
                break
            except OSError:
                time.sleep(.1)
        else:
            raise RuntimeError("server unavailable")
        inputs = [
            "osimertinib with generic version of bevacizumab",
            "bevacizumab with generic version of osimertinib",
            "osimertinib with a generic version of bevacizumab",
            "generic version of Paclitaxel conjugate with poly-l-glutamic acid",
            "Paclitaxel conjugate with poly-l-glutamic acid",
            "biosimilar version of bevacizumab",
            "liposomal formulation of doxorubicin",
            "generic version of the monoclonal antibody bevacizumab",
            "generic version of the antibody bevacizumab",
            "generic version of bevacizumab and generic version of trastuzumab",
            "EGFR with biosimilar bevacizumab",
            "AstraZeneca with biosimilar bevacizumab",
        ]
        cases = [post(path, value) for value in inputs
                 for path in ("/api/explore", "/api/resolve")]
        for value in [
            "Which trials evaluate osimertinib with generic version of bevacizumab?",
            "Which companies sponsor osimertinib with generic version of bevacizumab?",
            "What targets does generic version of Paclitaxel conjugate with poly-l-glutamic acid act on?",
            "Which trials evaluate biosimilar version of bevacizumab?",
            "Which trials evaluate liposomal formulation of doxorubicin?",
            "Which trials evaluate generic version of the monoclonal antibody bevacizumab?",
        ]:
            cases.append(post("/api/ask", value))
        (OUT / "attack_http.json").write_text(json.dumps(
            {"base": BASE, "cases": cases}, indent=2, ensure_ascii=False), encoding="utf-8")
        for case in cases:
            body = case["body"]
            print(json.dumps({"path": case["path"], "text": case["text"], "status": case["status"],
                "center": body.get("center", {}).get("id"), "refused": body.get("refused"),
                "evidence_count": len(body.get("evidence", [])),
                "first_edge": (body.get("evidence") or [{}])[0].get("edge_id")}, ensure_ascii=False))
    finally:
        proc.terminate()
        proc.wait(timeout=10)
        with socket.socket() as sock:
            closed = sock.connect_ex(("127.0.0.1", PORT)) != 0
        after = hashlib.sha256(DB.read_bytes()).hexdigest()
        (OUT / "attack_http_lifecycle.json").write_text(json.dumps({
            "pid": proc.pid, "port": PORT, "server_exit": proc.returncode,
            "port_closed": closed, "database_unchanged": before == after,
            "db_sha256_before": before, "db_sha256_after": after}, indent=2), encoding="utf-8")
        assert closed and before == after
