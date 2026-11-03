"""Re-run the six R1 probes without writing outside the R2 scratch directory."""
import difflib
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
TEMP = OUT / "replay_temp"
TEMP.mkdir(exist_ok=True)
env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONIOENCODING="utf-8",
           TEMP=str(TEMP), TMP=str(TEMP))
names = ["main", "adversarial_probe", "adversarial_pairs", "faithful_probe",
         "code_dictionary", "code_probes"]
manifest = []
for name in names:
    source = ROOT / "audit_evidence_claims" / f"independent_{name}.py"
    dest = OUT / f"replay_{name}.py"
    original = source.read_text(encoding="utf-8")
    adapted = original.replace(".parents[1]", ".parents[2]")
    adapted = adapted.replace("audit_evidence_claims/independent_", "audit_evidence_claims/r2/replay_")
    adapted = adapted.replace("independent_", "replay_")
    dest.write_text(adapted, encoding="utf-8")
    diff = "".join(difflib.unified_diff(original.splitlines(True), adapted.splitlines(True),
                                     fromfile=source.name, tofile=dest.name))
    (OUT / f"replay_{name}_adaptation.diff").write_text(diff, encoding="utf-8")
    proc = subprocess.run([sys.executable, "-B", str(dest)], cwd=ROOT, env=env,
                          capture_output=True, text=True, encoding="utf-8")
    (OUT / f"replay_{name}.stdout.txt").write_text(proc.stdout, encoding="utf-8")
    (OUT / f"replay_{name}.stderr.txt").write_text(proc.stderr, encoding="utf-8")
    manifest.append({"source":str(source.relative_to(ROOT)), "source_sha256":hashlib.sha256(source.read_bytes()).hexdigest(),
                     "copy":str(dest.relative_to(ROOT)), "returncode":proc.returncode})
    print(name, proc.returncode, flush=True)
proc = subprocess.run([sys.executable, "-m", "pytest", "tests", "-q", "-p", "no:cacheprovider"],
                      cwd=ROOT, env=env, capture_output=True, text=True, encoding="utf-8")
(OUT / "replay_pytest.stdout.txt").write_text(proc.stdout, encoding="utf-8")
(OUT / "replay_pytest.stderr.txt").write_text(proc.stderr, encoding="utf-8")
manifest.append({"command":"python -m pytest tests -q -p no:cacheprovider", "returncode":proc.returncode})
(OUT / "replay_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
print(proc.stdout, flush=True)
print(proc.stderr, flush=True)
sys.exit(any(x["returncode"] for x in manifest))
