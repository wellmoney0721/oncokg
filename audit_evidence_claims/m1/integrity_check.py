"""Final read-only provenance check, writing only this directory's manifest."""
import datetime
import hashlib
import json
import re
import socket
import subprocess
from pathlib import Path

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[1]


def git(*args):
    p = subprocess.run(["git", *args], cwd=ROOT, capture_output=True)
    return {"exit_code": p.returncode, "stdout": p.stdout.decode("utf-8", errors="replace").strip(),
            "stderr": p.stderr.decode("utf-8", errors="replace").strip()}


db_hash = hashlib.sha256((ROOT / "data/processed/oncokg.sqlite").read_bytes()).hexdigest()
http = json.loads((OUT / "http_results.json").read_text(encoding="utf-8"))
report = (OUT / "REPORT.md").read_text(encoding="utf-8")
links = re.findall(r"\]\(([^)]+)\)", report)
with socket.socket() as s:
    s.settimeout(1)
    port_open = s.connect_ex(("127.0.0.1", 8876)) == 0
result = {
    "checked_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "head": git("rev-parse", "HEAD"),
    "tracked_diff": git("diff", "--exit-code"),
    "staged_diff": git("diff", "--cached", "--exit-code"),
    "status": git("status", "--short"),
    "final_database_sha256": db_hash,
    "same_as_before_http": db_hash == http["db_sha256_before"],
    "port_8876_open_after_server_stop": port_open,
    "report_missing_local_links": [p for p in links if not (OUT / p).exists()],
    "report_final_line": report.strip().splitlines()[-1],
    "source_sha256": {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest()
                      for p in ["src/app.py", "src/query.py", "web/try.html", "tests/test_app.py"]},
}
(OUT / "integrity.json").write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(result, ensure_ascii=False, indent=2))
