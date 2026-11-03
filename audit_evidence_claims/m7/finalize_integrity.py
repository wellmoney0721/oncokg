"""Read-only repository and owned-server checks, with one m7 JSON output."""
import hashlib
import json
from pathlib import Path
import re
import socket
import subprocess

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[1]
baseline = json.loads((OUT / "root_checks/tracked_initial.json").read_text(encoding="utf8"))


def git(*args):
    result = subprocess.run(["git", *args], cwd=ROOT, capture_output=True)
    return {"exit_code": result.returncode, "stdout": result.stdout.decode("utf8", "replace"),
            "stderr": result.stderr.decode("utf8", "replace")}


changed, missing = [], []
for name, previous in baseline["hashes"].items():
    path = ROOT / name
    if not path.is_file():
        missing.append(name)
    elif hashlib.sha256(path.read_bytes()).hexdigest() != previous:
        changed.append(name)
ports = {}
for port in range(8901, 8906):
    with socket.socket() as sock:
        sock.settimeout(.5)
        ports[str(port)] = sock.connect_ex(("127.0.0.1", port)) != 0
broken = []
link_count = 0
for report in [OUT / "REPORT.md", OUT / "names/REPORT.md", OUT / "db_ui/REPORT.md", OUT / "attacks/REPORT.md"]:
    for href in re.findall(r"\]\(([^)]+)\)", report.read_text(encoding="utf8")):
        if href.startswith(("http:", "https:", "#")):
            continue
        link_count += 1
        target = href.split("#", 1)[0]
        if not (report.parent / target).exists() and target != "integrity_final.json":
            broken.append({"report": str(report.relative_to(OUT)), "href": href})
head = git("rev-parse", "HEAD")
diff = git("diff", "--exit-code")
staged = git("diff", "--cached", "--exit-code")
status = git("status", "--short")
result = {"initial_head": baseline["head"], "final_head": head,
          "head_unchanged": head["stdout"].strip() == baseline["head"],
          "tracked_files_checked": len(baseline["hashes"]), "changed_tracked_files": changed,
          "missing_tracked_files": missing, "tracked_diff": diff, "staged_diff": staged,
          "status": status, "all_owned_ports_closed": ports,
          "report_local_links_checked": link_count, "broken_report_links": broken,
          "database_sha256": hashlib.sha256((ROOT / "data/processed/oncokg.sqlite").read_bytes()).hexdigest(),
          "main_report_last_line": (OUT / "REPORT.md").read_text(encoding="utf8").rstrip().splitlines()[-1]}
result["pass"] = bool(result["head_unchanged"] and not changed and not missing and
                       diff["exit_code"] == 0 and staged["exit_code"] == 0 and
                       all(ports.values()) and not broken and
                       result["main_report_last_line"] == "VERDICT: CHANGES REQUIRED")
(OUT / "integrity_final.json").write_text(json.dumps(result, indent=2), encoding="utf8")
print(json.dumps(result, indent=2))
raise SystemExit(0 if result["pass"] else 1)
