"""Run the unmodified existing suite with scratch confined to this directory."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import time

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[1]
TMP = OUT / "tmp"
TMP.mkdir(exist_ok=True)
env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1", "PYTHONUTF8": "1",
       "PYTHONIOENCODING": "utf-8", "TMP": str(TMP), "TEMP": str(TMP),
       "TMPDIR": str(TMP)}

def git(*args):
    result = subprocess.run(["git", *args], cwd=ROOT, capture_output=True)
    return {"code": result.returncode, "stdout": result.stdout.decode("utf-8", "replace"),
            "stderr": result.stderr.decode("utf-8", "replace")}

files = ["src/app.py", "src/query.py", "web/try.html", "tests/test_app.py",
         "data/processed/oncokg.sqlite"]
before = {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in files}
(OUT / "verification_initial.json").write_text(json.dumps({"head": git("rev-parse", "HEAD"),
    "status": git("status", "--short"), "hashes": before}, indent=2), encoding="utf-8")
cmd = [sys.executable, "-m", "pytest", "tests", "-q", "-p", "no:cacheprovider"]
start = time.perf_counter()
run = subprocess.run(cmd, cwd=ROOT, env=env, capture_output=True)
(OUT / "pytest.txt").write_bytes(run.stdout + run.stderr)
after = {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in files}
summary = {"command": "python -m pytest tests -q -p no:cacheprovider",
           "environment": {k: env[k] for k in ("PYTHONDONTWRITEBYTECODE", "PYTHONUTF8", "PYTHONIOENCODING", "TMP", "TEMP", "TMPDIR")},
           "exit_code": run.returncode, "wall_seconds": round(time.perf_counter() - start, 3),
           "hashes_unchanged": before == after, "hashes_after": after}
(OUT / "pytest_summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
print((run.stdout + run.stderr).decode("utf-8", "replace"))
print(json.dumps(summary, indent=2))
raise SystemExit(run.returncode)
