"""Snapshot tracked bytes and adapt previous audit runners without changing inputs."""
from pathlib import Path
import hashlib, json, subprocess
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[1]
tracked=subprocess.check_output(['git','ls-files','-z'],cwd=ROOT).decode('utf8').split('\0')
initial={'head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT).decode().strip(),
 'tracked_sha256':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in tracked if p},
 'status':subprocess.check_output(['git','status','--porcelain'],cwd=ROOT).decode(),
 'db_sha256':hashlib.sha256((ROOT/'data/processed/oncokg.sqlite').read_bytes()).hexdigest()}
(OUT/'integrity_before.json').write_text(json.dumps(initial,indent=2),encoding='utf8')
manifest=[]
for sub in ['root_checks','cost']:
 dest=OUT/sub
 (dest/'tmp').mkdir(parents=True,exist_ok=True)
 for src in sorted((ROOT/'audit_evidence_claims/m11'/sub).glob('*.py')):
  if src.name in ('setup.py','build_report.py'):continue
  code=src.read_text(encoding='utf8')
  changes=[]
  for old,new in [('8897','8917'),('8898','8918'),('8899','8919'),('8894','8914')]:
   if old in code:code=code.replace(old,new);changes.append(f'port {old} -> {new}')
  if 'audit_evidence_claims/m11/' in code:
   raise RuntimeError('Review explicit round path before adapting: '+str(src))
  (dest/src.name).write_text(code,encoding='utf8')
  manifest.append({'source':src.relative_to(ROOT).as_posix(),'copy':(dest/src.name).relative_to(ROOT).as_posix(),
   'sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'changes':changes,'output_root':'__file__ relative m12; historical inputs unchanged'})
(OUT/'reuse_manifest_root.json').write_text(json.dumps(manifest,indent=2),encoding='utf8')
print(json.dumps({'tracked':len(initial['tracked_sha256']),'scripts':len(manifest),'head':initial['head']}))
