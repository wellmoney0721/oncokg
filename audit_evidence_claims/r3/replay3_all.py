"""Replay R1/R2 probes at HEAD, writing only to this R3 directory."""
import difflib
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
TEMP = OUT / "replay3_temp"
TEMP.mkdir(exist_ok=True)
env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONUTF8="1",
           PYTHONIOENCODING="utf-8", TEMP=str(TEMP), TMP=str(TEMP))
manifest = []
names = ["main", "adversarial_probe", "adversarial_pairs", "faithful_probe",
         "code_dictionary", "code_probes"]
jobs = [(ROOT / "audit_evidence_claims" / f"independent_{n}.py", f"replay3_{n}.py", "R1")
        for n in names]
jobs += [(ROOT / "audit_evidence_claims/r2" / f"{n}.py", f"replay3_r2_{n}.py", "R2")
         for n in ["root_design_probe", "spec_probe", "standards_probe"]]
for source, filename, round_name in jobs:
    dest = OUT / filename
    original = source.read_text(encoding="utf-8")
    if round_name == "R1":
        adapted = original.replace(".parents[1]", ".parents[2]")
        adapted = adapted.replace("audit_evidence_claims/independent_", "audit_evidence_claims/r3/replay3_")
        adapted = adapted.replace("independent_", "replay3_")
    else:
        adapted = original.replace("audit_evidence_claims/r2/", "audit_evidence_claims/r3/replay3_r2_")
        adapted = adapted.replace("with_name('spec_probe_results.json')", "with_name('replay3_r2_spec_probe_results.json')")
        # Only current internal API adaptation; question/answer corpus unchanged.
        adapted = adapted.replace("_tokenise(answer, engine.kg.link_entities, {}, None)",
                                  "_tokenise(answer, engine.kg.link_entities)")
        adapted = adapted.replace("_tokenise(alias, engine.kg.link_entities, {}, None)",
                                  "_tokenise(alias, engine.kg.link_entities)")
    dest.write_text(adapted, encoding="utf-8")
    (OUT / (dest.stem + "_adaptation.diff")).write_text("".join(difflib.unified_diff(
        original.splitlines(True), adapted.splitlines(True), fromfile=str(source.relative_to(ROOT)),
        tofile=str(dest.relative_to(ROOT)))), encoding="utf-8")
    proc = subprocess.run([sys.executable, "-B", str(dest)], cwd=ROOT, env=env,
                          capture_output=True, text=True, encoding="utf-8")
    (OUT / (dest.stem + ".stdout.txt")).write_text(proc.stdout, encoding="utf-8")
    (OUT / (dest.stem + ".stderr.txt")).write_text(proc.stderr, encoding="utf-8")
    manifest.append({"round": round_name, "source": str(source.relative_to(ROOT)),
                     "source_sha256": hashlib.sha256(source.read_bytes()).hexdigest(),
                     "copy": str(dest.relative_to(ROOT)), "returncode": proc.returncode})
    print(filename, proc.returncode, flush=True)
proc = subprocess.run([sys.executable, "-m", "pytest", "tests", "-q", "-p", "no:cacheprovider"],
                      cwd=ROOT, env=env, capture_output=True, text=True, encoding="utf-8")
(OUT / "replay3_pytest.stdout.txt").write_text(proc.stdout, encoding="utf-8")
(OUT / "replay3_pytest.stderr.txt").write_text(proc.stderr, encoding="utf-8")
manifest.append({"command": "python -m pytest tests -q -p no:cacheprovider", "returncode": proc.returncode})
(OUT / "replay3_manifest.json").write_text(json.dumps(manifest, indent=2), encoding="utf-8")
print(proc.stdout, flush=True)
print(proc.stderr, flush=True)
sys.exit(any(x["returncode"] for x in manifest))
