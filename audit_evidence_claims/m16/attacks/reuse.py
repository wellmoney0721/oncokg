import sys,os,json,subprocess,hashlib,re
from pathlib import Path
sys.dont_write_bytecode=True
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2];SRC=ROOT/'audit_evidence_claims/m15/attacks'
manifest=[]
for name in ['focused.py','fresh.py','edge_probe.py','targeted_probe.py','alias_variants.py']:
 p=SRC/name;s=p.read_text(encoding='utf8');s=s.replace("'m15_previous", "'m16_previous")
 (OUT/name).write_text(s,encoding='utf8')
 manifest.append({'source':str(p.relative_to(ROOT)),'output':str((OUT/name).relative_to(ROOT)),'source_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'adaptations':['Python module name m15_previous -> m16_previous; outputs derive from script location; all original input lists unchanged']})
(OUT/'reuse_manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf8')
env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1','PYTHONIOENCODING':'utf-8','TEMP':str(OUT),'TMP':str(OUT),'TMPDIR':str(OUT)}
results=[]
for r in manifest:
 p=ROOT/r['output']
 with (OUT/(p.stem+'.stdout.txt')).open('w',encoding='utf8') as out:
  x=subprocess.run([sys.executable,'-B',str(p)],cwd=ROOT,env=env,stdout=out,stderr=subprocess.STDOUT)
 results.append({'script':r['output'],'returncode':x.returncode});print(results[-1],flush=True)
(OUT/'reuse_execution.json').write_text(json.dumps(results,indent=2),encoding='utf8')
