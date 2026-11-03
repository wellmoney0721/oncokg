"""Independent CLI HTTP confirmation of candidate round-nine findings."""
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
PORT = 8970
BASE = f"http://127.0.0.1:{PORT}"
CASES = ['trastuzumab I-124', 'I-124 trastuzumab', 'trastuzumab I124', 'I124 trastuzumab', 'trastuzumab i-124', 'i-124 trastuzumab', 'I-124-labelled trastuzumab', 'trastuzumab labelled with I-124', 'trastuzumab labeled with I-124', 'I-124-labeled trastuzumab', '[I-124] trastuzumab', 'trastuzumab [I-124]', '124I trastuzumab', 'trastuzumab 124I', '124I-labelled trastuzumab', 'trastuzumab labelled with 124I', 'trastuzumab', 'trastuzumab I-124, osimertinib', 'osimertinib, trastuzumab I-124', 'vinblastine H3', 'vinblastine H-3', '[H-3] vinblastine', 'vinblastine 3h', '3hvinblastine', 'vinblastine', '18 FDFO trastuzumab', '18-FDFO trastuzumab', '18 F DFO trastuzumab', '18FDFO trastuzumab', 'osimertinib 80 mg', 'paclitaxel 2 cycles', 'cisplatin 75 mg/m2 day 1', '13-cis retinoic acid', 'BKM-120NX', 'trastuzumab Ga-68', 'trastuzumab 68Ga', 'trastuzumab Ga68', 'trastuzumab Zr-89', 'trastuzumab 89Zr', 'trastuzumab I-131', 'trastuzumab 131I', 'I-124-labelled trastuzumab, osimertinib']


def post(endpoint, text):
    req = urllib.request.Request(BASE + "/api/" + endpoint,
        data=json.dumps({"text": text}).encode(),
        headers={"Content-Type": "application/json"})
    start = time.perf_counter()
    try:
        response = urllib.request.urlopen(req, timeout=30)
    except urllib.error.HTTPError as error:
        response = error
    with response:
        return {"endpoint": endpoint, "input": text, "status": response.status,
                "seconds": time.perf_counter() - start,
                "response": json.loads(response.read())}

with socket.socket() as sock:
    assert sock.connect_ex(("127.0.0.1", PORT)) != 0, "owned port already occupied"
db = ROOT / "data/processed/oncokg.sqlite"
before = hashlib.sha256(db.read_bytes()).hexdigest()
env = {**os.environ, "TMP": str(OUT), "TEMP": str(OUT), "TMPDIR": str(OUT), "PYTHONDONTWRITEBYTECODE": "1", "PYTHONIOENCODING": "utf-8"}
with (OUT / "new_server.txt").open("w", encoding="utf-8") as log:
    proc = subprocess.Popen([sys.executable, "-B", "-u", "src/app.py", str(PORT)],
        cwd=ROOT, env=env, stdout=log, stderr=subprocess.STDOUT,
        creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    results = []
    try:
        for _ in range(100):
            assert proc.poll() is None, "server exited"
            try:
                page = urllib.request.urlopen(BASE, timeout=1).read()
                break
            except OSError:
                time.sleep(.1)
        else:
            raise RuntimeError("server unavailable")
        for name in CASES:
            for endpoint in ("resolve", "explore"):
                results.append(post(endpoint, name))
            if not name.startswith("CHEMBL"):
                results.append(post("ask", f"Which trials evaluate {name}?"))
                results.append(post("ask", f"Who sponsors trials of {name}?"))
        (OUT / "new_http.json").write_text(json.dumps(results,
            ensure_ascii=False, indent=2), encoding="utf-8")
        print(json.dumps([{"input": r["input"], "status": r["status"],
            "center": r["response"].get("center", {}).get("id"),
            "refused": r["response"].get("refused")}
            for r in results if r["endpoint"] == "explore"], indent=2))
    finally:
        proc.terminate()
        proc.wait(timeout=10)
        with socket.socket() as sock:
            closed = sock.connect_ex(("127.0.0.1", PORT)) != 0
        (OUT / "new_lifecycle.json").write_text(json.dumps({
            "pid": proc.pid, "port": PORT, "port_closed": closed,
            "database_unchanged": hashlib.sha256(db.read_bytes()).hexdigest() == before,
            "requests": len(results), "all_200": all(r["status"] == 200 for r in results),
            "page_matches_worktree": page == (ROOT / "web/try.html").read_bytes()
        }, indent=2), encoding="utf-8")
