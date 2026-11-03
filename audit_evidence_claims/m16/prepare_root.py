"""Snapshot tracked bytes and adapt previous root/cost reproducers, never application code."""
from pathlib import Path
import datetime, hashlib, json, subprocess

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[1]

def git(*args):
    p = subprocess.run(['git', *args], cwd=ROOT, capture_output=True, check=True)
    return p.stdout.decode('utf8')

snapshot = OUT / 'integrity_before.json'
if not snapshot.exists():
    paths = git('ls-files', '-z').split('\0')
    hashes = {p: hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in paths if p}
    snapshot.write_text(json.dumps(dict(time=datetime.datetime.now().astimezone().isoformat(),
        head=git('rev-parse','HEAD').strip(), status=git('status','--short'), tracked_sha256=hashes,
        db_sha256=hashlib.sha256((ROOT/'data/processed/oncokg.sqlite').read_bytes()).hexdigest()), indent=2), encoding='utf8')
manifest=[]
for family in ['root_checks', 'cost']:
    dest=OUT/family
    dest.mkdir(exist_ok=True)
    (dest/'tmp').mkdir(exist_ok=True)
    for source in (OUT.parent/'m15'/family).glob('*.py'):
        code=source.read_text(encoding='utf8')
        # Existing readers of earlier round baselines remain unchanged.
        # All writers in these scripts use __file__-relative OUT.
        target=dest/source.name
        if target.exists():
            raise RuntimeError(f'Refusing to overwrite {target}')
        target.write_text(code,encoding='utf8')
        manifest.append(dict(source=str(source.relative_to(ROOT)),copy=str(target.relative_to(ROOT)),
            sha256=hashlib.sha256(source.read_bytes()).hexdigest(),changes=[],
            output_root='__file__ relative m16; original historical case inputs retained'))
(OUT/'reuse_manifest_root.json').write_text(json.dumps(manifest,indent=2),encoding='utf8')
print(json.dumps({'tracked_files':len(hashes),'copies':len(manifest),'head':git('rev-parse','HEAD').strip()}))
