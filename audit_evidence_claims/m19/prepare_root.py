from pathlib import Path
import datetime, hashlib, json, subprocess
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[1]
def git(*args):
    return subprocess.check_output(['git',*args],cwd=ROOT).decode('utf8')
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
snapshot=OUT/'integrity_before.json'
assert not snapshot.exists()
hashes={p:digest(ROOT/p) for p in git('ls-files','-z').split('\0') if p}
snapshot.write_text(json.dumps(dict(time=datetime.datetime.now().astimezone().isoformat(),head=git('rev-parse','HEAD').strip(),status=git('status','--short'),tracked_sha256=hashes,db_sha256=digest(ROOT/'data/processed/oncokg.sqlite')),indent=2),encoding='utf8')
manifest=[]
for family in ['root_checks','cost']:
    dest=OUT/family
    dest.mkdir(exist_ok=True)
    (dest/'tmp').mkdir(exist_ok=True)
    for source in (OUT.parent/'m18'/family).glob('*.py'):
        target=dest/source.name
        assert not target.exists(),str(target)
        target.write_bytes(source.read_bytes())
        manifest.append(dict(source=source.relative_to(ROOT).as_posix(),copy=target.relative_to(ROOT).as_posix(),source_sha256=digest(source),copy_sha256=digest(target),changes=[],note='Output uses __file__; exact case literals unchanged. Historical baseline readers retained.'))
(OUT/'reuse_manifest_root.json').write_text(json.dumps(manifest,indent=2),encoding='utf8')
print(json.dumps(dict(copies=len(manifest),tracked_files=len(hashes),head=git('rev-parse','HEAD').strip())))
