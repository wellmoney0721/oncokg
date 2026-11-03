"""Final review provenance; creates only the sibling integrity manifest."""
import datetime
import hashlib
import json
from pathlib import Path
import re
import socket
import subprocess

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[1]

def git(*args):
    p = subprocess.run(["git", *args], cwd=ROOT, capture_output=True)
    return {"exit_code": p.returncode, "stdout": p.stdout.decode("utf-8", "replace").strip(),
            "stderr": p.stderr.decode("utf-8", "replace").strip()}

initial = json.loads((OUT / "verification_initial.json").read_text(encoding="utf-8"))
hashes = {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in initial["hashes"]}
report = (OUT / "REPORT.md").read_text(encoding="utf-8")
links = re.findall(r"\]\(([^)]+)\)", report)
with socket.socket() as s:
    s.settimeout(1)
    closed = s.connect_ex(("127.0.0.1", 8879)) != 0
manifest = {
    "checked_at": datetime.datetime.now(datetime.timezone.utc).isoformat(),
    "head": git("rev-parse", "HEAD"),
    "tracked_diff": git("diff", "--exit-code"),
    "staged_diff": git("diff", "--cached", "--exit-code"),
    "status": git("status", "--short"),
    "tracked_standards_search": git("ls-files", "*AGENTS.md", "*CONTRIBUTING*", "*CODING*", "docs/agents/*"),
    "hashes": hashes,
    "source_and_database_hashes_unchanged": hashes == initial["hashes"],
    "audit_port_8879_closed": closed,
    "report_local_links_checked": len(links),
    "report_missing_local_links": [p for p in links if p != "integrity.json" and not (OUT / p).exists()],
    "report_final_line": report.strip().splitlines()[-1],
    "report_verdict_line_count": sum(line.startswith("VERDICT:") for line in report.splitlines()),
    "browser_verification": {"browser_inventory_error": "The browser access host is unavailable",
        "native_chrome_selection_error": "Computer Use was not approved to use Google Chrome",
        "browser_inputs_performed": False, "real_browser_verified": False},
}
(OUT / "integrity.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False), encoding="utf-8")
print(json.dumps(manifest, indent=2, ensure_ascii=False))
assert manifest["head"]["stdout"] == "574097f67e0719c32bfdc0526133e649b1864993"
assert manifest["tracked_diff"]["exit_code"] == manifest["staged_diff"]["exit_code"] == 0
assert manifest["source_and_database_hashes_unchanged"]
assert closed and not manifest["report_missing_local_links"]
assert manifest["report_final_line"] == "VERDICT: CHANGES REQUIRED"
assert manifest["report_verdict_line_count"] == 1
