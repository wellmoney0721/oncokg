"""Confine replay outputs to M11 and capture initial tracked-file bytes."""
from pathlib import Path
import hashlib, json, subprocess

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
(OUT/'tmp').mkdir(exist_ok=True)
tracked = subprocess.check_output(['git','ls-files','-z'], cwd=ROOT).decode('utf8').split('\0')
hashes = {p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in tracked if p}
initial = dict(head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT).decode().strip(),
               tracked_sha256=hashes, db_sha256=hashlib.sha256((ROOT/'data/processed/oncokg.sqlite').read_bytes()).hexdigest())
(OUT/'integrity_before.json').write_text(json.dumps(initial,indent=2),encoding='utf8')
manifest=[]
for src in sorted((ROOT/'audit_evidence_claims/m10/root_checks').glob('*.py')):
    if src.name == 'build_report.py':
        continue
    code=src.read_text(encoding='utf8')
    # These scripts use __file__-relative outputs; only round-specific input files move.
    code=code.replace('audit_evidence_claims/m10/', 'audit_evidence_claims/m11/')
    (OUT/src.name).write_text(code,encoding='utf8')
    manifest.append(dict(source=src.relative_to(ROOT).as_posix(),copy=(OUT/src.name).relative_to(ROOT).as_posix(),
                         source_sha256=hashlib.sha256(src.read_bytes()).hexdigest(),
                         adaptations='Outputs relative to copied script; m10 paths remapped to m11; historical baseline reads preserved.'))
(OUT/'reuse_manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf8')
print(json.dumps(dict(tracked_files=len(hashes),scripts=len(manifest),head=initial['head'])))
