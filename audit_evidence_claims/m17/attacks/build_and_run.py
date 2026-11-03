import ast,hashlib,json,os,subprocess,sys,time
from pathlib import Path
sys.dont_write_bytecode=True
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2]
cases=[
 'trastuzumab labelled-I-124','trastuzumab labelled-124I','I-124-labelled trastuzumab','trastuzumab labelled with I-124','trastuzumab labelled-with-I-124','trastuzumab labelled-with-124I',
 'trastuzumab radiolabelled-I-124','trastuzumab radiolabeled-I124','trastuzumab radiolabelled with I-124','iodine-I-124 trastuzumab','iodine I-124 trastuzumab','trastuzumab iodine-I-124','trastuzumab (iodine-I-124)','trastuzumab [iodine-I-124]',
 'trastuzumab LABELLED-I-124','TRASTUZUMAB LABELLED-I-124','trastuzumab labelled-i-124','trastuzumab labelled_I_124','trastuzumab labelled:I-124','trastuzumab labelled(I-124)','trastuzumab labelled[I-124]',
 'trastuzumab labelled-I-124, osimertinib','osimertinib, trastuzumab labelled-I-124','trastuzumab labelled-I-124 and osimertinib','osimertinib and trastuzumab labelled-I-124','trastuzumab labelled-124I, osimertinib',
 'vinblastine tritium-H-3','vinblastine tritium-3H','vinblastine labelled-H3','vinblastine labelled-3H','vinblastine H3','vinblastine H-3','vinblastine 3H',
 'erlotinib fluorine-F18','erlotinib fluorine F18','erlotinib labelled-F18','erlotinib labelled-18F','erlotinib F18','erlotinib 18F',
 'paclitaxel carbon-C14','paclitaxel carbon C14','paclitaxel labelled-C14','paclitaxel labelled-14C','paclitaxel C14','paclitaxel 14C',
 'cetuximab labelled-Y-90','cetuximab labelled-90Y','cetuximab Y-90','cetuximab 90Y',
 'osimertinib 80 mg','paclitaxel 2 cycles','cisplatin 75 mg/m2 day 1','13-cis retinoic acid','BKM120','AZD9291','trastuzumab','vinblastine','erlotinib','paclitaxel','cetuximab',
 '89-ZrDFO trastuzumab','3hvinblastine','A33124i',
]
(OUT/'new_cases.json').write_text(json.dumps(cases,indent=2,ensure_ascii=False),encoding='utf8')
manifest=json.loads((OUT/'reuse_manifest.json').read_text(encoding='utf8'))
for name,var in [('new_probe.py','cases'),('new_http.py','CASES')]:
 source=ROOT/'audit_evidence_claims/m16/attacks'/name
 body=source.read_text(encoding='utf8')
 tree=ast.parse(body)
 assignment=next(x for x in tree.body if isinstance(x,ast.Assign) and any(isinstance(t,ast.Name) and t.id==var for t in x.targets))
 lines=body.splitlines(keepends=True);lines[assignment.lineno-1:assignment.end_lineno]=[var+' = '+repr(cases)+'\n'];body=''.join(lines)
 body=body.replace('m16_previous','m17_previous').replace('PORT = 8970','PORT = 8972')
 if name=='new_probe.py':
  body=body.replace("row['current']['qualified']=query._qualified(text.split());rows.append(row)","row['current']['qualified']=query._qualified(text.split());row['current']['item_has_isotope']=query._item_has_isotope(tuple(text.split()));rows.append(row)")
 (OUT/name).write_text(body,encoding='utf8')
 manifest.append({'source':str(source.relative_to(ROOT)),'destination':str((OUT/name).relative_to(ROOT)),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'adapted_sha256':hashlib.sha256((OUT/name).read_bytes()).hexdigest(),'adaptations':['replace input list with 63 new paired cases','module version name and owned port changed','add current item isotope boolean; actual _marked calls retain segmentation']})
(OUT/'reuse_manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf8')
env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1','PYTHONIOENCODING':'utf-8','TEMP':str(OUT),'TMP':str(OUT),'TMPDIR':str(OUT)}
execution=[]
for name in ('previous_new_probe.py','previous_new_http.py','new_probe.py','new_http.py'):
 start=time.perf_counter()
 with (OUT/(Path(name).stem+'.stdout.txt')).open('w',encoding='utf8') as log:
  result=subprocess.run([sys.executable,'-B',str(OUT/name)],cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT)
 execution.append({'script':str((OUT/name).relative_to(ROOT)),'exit_code':result.returncode,'seconds':time.perf_counter()-start});print(execution[-1],flush=True)
 (OUT/'execution_summary.json').write_text(json.dumps(execution,indent=2),encoding='utf8')
 if result.returncode:raise SystemExit(result.returncode)
