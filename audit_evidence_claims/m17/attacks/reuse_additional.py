import hashlib,json,os,subprocess,sys,time
from pathlib import Path
sys.dont_write_bytecode=True
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2]
manifest=[];execution=[]
env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1','PYTHONIOENCODING':'utf-8','TEMP':str(OUT),'TMP':str(OUT),'TMPDIR':str(OUT)}
for name in ['focused.py','fresh.py','edge_probe.py','targeted_probe.py','alias_variants.py']:
 p=ROOT/'audit_evidence_claims/m16/attacks'/name
 body=p.read_text(encoding='utf8').replace('m16_previous','m17_previous')
 dst=OUT/name;dst.write_text(body,encoding='utf8')
 manifest.append({'source':str(p.relative_to(ROOT)),'destination':str(dst.relative_to(ROOT)),'source_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'adapted_sha256':hashlib.sha256(dst.read_bytes()).hexdigest(),'adaptations':['previous module label m16 to m17; output path inferred from script; original cases unchanged']})
 start=time.perf_counter()
 with (OUT/(dst.stem+'.stdout.txt')).open('w',encoding='utf8') as log:
  result=subprocess.run([sys.executable,'-B',str(dst)],cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT)
 execution.append({'script':str(dst.relative_to(ROOT)),'exit_code':result.returncode,'seconds':time.perf_counter()-start});print(execution[-1],flush=True)
 (OUT/'reuse_additional_manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf8')
 (OUT/'reuse_additional_execution.json').write_text(json.dumps(execution,indent=2),encoding='utf8')
 if result.returncode:raise SystemExit(result.returncode)
old=json.loads((ROOT/'audit_evidence_claims/m16/attacks/alias_variants.json').read_text(encoding='utf8'))
new=json.loads((OUT/'alias_variants.json').read_text(encoding='utf8'));by_text={r['text']:r for r in old};changes=[]
for r in new:
 p=by_text.get(r['text'],{})
 if (p.get('center'),bool(p.get('refused'))) !=(r.get('center'),bool(r.get('refused'))):changes.append({'text':r['text'],'old':p,'new':r})
(OUT/'alias_variants_comparison.json').write_text(json.dumps({'old_count':len(old),'new_count':len(new),'unique_keys':len(set(r['key'] for r in new)),'changes':changes},indent=2,ensure_ascii=False),encoding='utf8')
