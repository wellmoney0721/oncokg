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
PORT = 19193
BASE = f"http://127.0.0.1:{PORT}"
CASES = ['radio-labelled trastuzumab', 'radiolabelled trastuzumab', 'radio-labeled trastuzumab', 'radio labeled trastuzumab', 'radio-labelled trastuzumab tracer', 'trastuzumab radio-tracer', 'trastuzumab radiotracer', 'trastuzumab radioactively labelled', 'trastuzumab radioactively labeled', 'trastuzumab radioactive label', 'trastuzumab radioiodinated', 'trastuzumab radio-iodinated', 'trastuzumab radio iodinated', 'iodine124 trastuzumab', 'iodine-124 trastuzumab', '124iodine trastuzumab', '124-iodine trastuzumab', 'trastuzumab iodine124', '99m-technetium trastuzumab', 'technetium-99m trastuzumab', '99-technetium trastuzumab', 'technetium99m trastuzumab', '99mtechnetium trastuzumab', 'technetium metastable 99 trastuzumab', 'trastuzumab labelled with iodine 124', 'trastuzumab labelled with iodine (124)', 'trastuzumab labelled with iodine mass 124', 'zirconium89 trastuzumab', 'zirconium-89 trastuzumab', '89zirconium trastuzumab', 'radioconjugated trastuzumab', 'trastuzumab radioimmunoconjugates', 'trastuzumab radionuclide-labelled', 'trastuzumab radionuclide labeled', 'trastuzumab isotopically labelled', 'trastuzumab radio-labelled with iodine-124', 'trastuzumab radio-labelled with I-124', 'trastuzumab radio-labelled with 124I', 'trastuzumab (radio-labelled)', 'radio-ligand trastuzumab', 'radio-immunoconjugate trastuzumab', 'radio-pharmaceutical trastuzumab', 'osimertinib, radio-labelled trastuzumab', 'radio-labelled trastuzumab, osimertinib', 'radio-labelled trastuzumab and osimertinib', 'unlabelled trastuzumab', 'non-radiolabelled trastuzumab', 'nonradioactive trastuzumab', 'trastuzumab', 'fluorine-18 fluorodeoxyglucose', 'radio-labelled fluorodeoxyglucose', 'radio-labelled FDG', 'tritiated FDG', 'FDG labelled with carbon-14', 'osimertinib 80 mg', 'paclitaxel 2 cycles', 'lead compound osimertinib', 'radio-labelled Herceptin', 'radiolabelled Herceptin', 'radio-labelled vinblastine', 'radiolabelled vinblastine', 'radio-labelled erlotinib', 'radiolabelled erlotinib', 'trastuzumab radio-labelled', 'trastuzumab radiolabelled', 'radio‑labelled trastuzumab', 'radio_labelled trastuzumab', 'RADIO-LABELLED TRASTUZUMAB', 'radio labelled trastuzumab', 'radioactively labelled trastuzumab', '99m technetium trastuzumab', 'technetium 99m trastuzumab', 'trastuzumab labelled with 99m-technetium', 'trastuzumab labelled with technetium-99m', 'trastuzumab labelled with 99mTc', '99m-Tc trastuzumab', 'technetium99m-trastuzumab', 'trastuzumab radioligands', 'trastuzumab radioligand', 'trastuzumab radiopharmaceuticals', 'trastuzumab radiopharmaceutical', 'radio-conjugated trastuzumab']


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
