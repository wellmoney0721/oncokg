"""Hash tracked bytes and adapt existing reproducers into round 15 only."""
from pathlib import Path
import hashlib, json, subprocess

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[1]
tracked = subprocess.check_output(['git', 'ls-files', '-z'], cwd=ROOT).decode('utf8').split('\0')
initial = dict(
    head=subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT).decode().strip(),
    tracked_sha256={p: hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in tracked if p},
    status=subprocess.check_output(['git', 'status', '--porcelain'], cwd=ROOT).decode(),
    db_sha256=hashlib.sha256((ROOT/'data/processed/oncokg.sqlite').read_bytes()).hexdigest(),
)
assert not (OUT/'integrity_before.json').exists(), 'Do not overwrite initial snapshot'
(OUT/'integrity_before.json').write_text(json.dumps(initial, indent=2), encoding='utf8')
manifest = []
for sub in ['root_checks', 'cost']:
    dest = OUT/sub
    (dest/'tmp').mkdir(parents=True, exist_ok=True)
    for src in sorted((ROOT/'audit_evidence_claims/m14'/sub).glob('*.py')):
        code = src.read_text(encoding='utf8')
        changes = []
        for old, new in [('audit_evidence_claims/m14/', 'audit_evidence_claims/m15/')]:
            if old in code:
                code = code.replace(old, new)
                changes.append(f'{old} -> {new}')
        (dest/src.name).write_text(code, encoding='utf8')
        manifest.append(dict(source=src.relative_to(ROOT).as_posix(), copy=(dest/src.name).relative_to(ROOT).as_posix(), sha256=hashlib.sha256(src.read_bytes()).hexdigest(), changes=changes, output_root='__file__ relative m15; exact historical case inputs retained'))
src = ROOT/'audit_evidence_claims/m14/finalize_integrity.py'
(OUT/'finalize_integrity.py').write_text(src.read_text(encoding='utf8').replace('8952]', '8952,8945]'), encoding='utf8')
(OUT/'reuse_manifest_root.json').write_text(json.dumps(manifest, indent=2), encoding='utf8')
print(json.dumps(dict(head=initial['head'], tracked=len(initial['tracked_sha256']), scripts=len(manifest))))
