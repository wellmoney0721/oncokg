"""Confirm fresh attack cases against the unmodified CLI server on owned port 8892."""
import json
import os
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path.cwd()
OUT = Path(__file__).resolve().parent
PORT = 8892
BASE = f"http://127.0.0.1:{PORT}"

with socket.socket() as check:
    check.bind(("127.0.0.1", PORT))
inputs = ["bevacizumab_awwb", "bevacizumab__awwb", "bevacizumab-_awwb", "trastuzumab_dkst",
    "bevacizumab (awwb)", "bevacizumab awwb", "bev\u00e1cizumab-awwb", "beva\u0301cizumab-awwb",
    "[89.Zr] trastuzumab", "89:Zr trastuzumab", "89_Zr-trastuzumab",
    "bevacizumab-awwb", "bevacizumab-(awwb)", "89-Zr trastuzumab", "[89 Zr] trastuzumab",
    "bevacizumab", "trastuzumab", "biosimilar, and osimertinib", "5ac, osimertinib"]
rows = []
env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1", "PYTHONIOENCODING": "utf-8"}


def request(path, payload):
    req = urllib.request.Request(BASE + path, data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"}, method="POST")
    before = time.perf_counter()
    try:
        with urllib.request.urlopen(req, timeout=20) as response:
            status, body = response.status, response.read()
    except urllib.error.HTTPError as error:
        status, body = error.code, error.read()
    rows.append({"path": path, "payload": payload, "status": status,
        "seconds": time.perf_counter() - before, "body": json.loads(body)})


with (OUT / "server_stdout.txt").open("w", encoding="utf-8") as log:
    proc = subprocess.Popen([sys.executable, "-B", str(ROOT / "src/app.py"), str(PORT)],
        cwd=ROOT, env=env, stdout=log, stderr=subprocess.STDOUT, creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    try:
        started = time.perf_counter()
        while True:
            if proc.poll() is not None:
                raise RuntimeError(f"server exited {proc.returncode}")
            try:
                with urllib.request.urlopen(BASE, timeout=1) as response:
                    page = response.read()
                break
            except (OSError, urllib.error.URLError):
                if time.perf_counter() - started > 15:
                    raise
                time.sleep(0.1)
        for text in inputs:
            request("/api/explore", {"text": text})
            request("/api/resolve", {"text": text})
        for text in ["bevacizumab_awwb", "bevacizumab (awwb)", "bev\u00e1cizumab-awwb", "[89.Zr] trastuzumab",
                     "bevacizumab-awwb", "89-Zr trastuzumab"]:
            for prefix in ["Which trials evaluate ", "Which companies sponsor "]:
                request("/api/ask", {"text": prefix + text + "?"})
    finally:
        proc.terminate()
        try:
            proc.wait(timeout=10)
        except subprocess.TimeoutExpired:
            proc.kill()
            proc.wait(timeout=5)

with socket.socket() as check:
    port_closed = check.connect_ex(("127.0.0.1", PORT)) != 0
result = {"port": PORT, "pid": proc.pid, "process_exit": proc.returncode, "port_closed": port_closed,
    "page_matches_worktree": page == (ROOT / "web/try.html").read_bytes(), "requests": rows}
(OUT / "http_results.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps({"requests": len(rows), "statuses": sorted({r["status"] for r in rows}),
                  "port_closed": port_closed, "page_matches_worktree": result["page_matches_worktree"]}))
