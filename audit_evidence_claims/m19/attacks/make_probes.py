import ast,json,re,hashlib
from pathlib import Path
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2]
initial=ast.parse((OUT/'initial_scan.py').read_text(encoding='utf-8-sig'))
cases=next(ast.literal_eval(n.value) for n in initial.body if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='cases' for t in n.targets))
cases += ['radio-labelled Herceptin','radiolabelled Herceptin','radio-labelled vinblastine','radiolabelled vinblastine','radio-labelled erlotinib','radiolabelled erlotinib','trastuzumab radio-labelled','trastuzumab radiolabelled','radio‑labelled trastuzumab','radio_labelled trastuzumab','RADIO-LABELLED TRASTUZUMAB','radio labelled trastuzumab','radioactively labelled trastuzumab','99m technetium trastuzumab','technetium 99m trastuzumab','trastuzumab labelled with 99m-technetium','trastuzumab labelled with technetium-99m','trastuzumab labelled with 99mTc','99m-Tc trastuzumab','technetium99m-trastuzumab','trastuzumab radioligands','trastuzumab radioligand','trastuzumab radiopharmaceuticals','trastuzumab radiopharmaceutical','radio-conjugated trastuzumab']
(OUT/'new_cases.json').write_text(json.dumps(cases,ensure_ascii=False,indent=2),encoding='utf8')
manifest=[]
for name in ['new_probe.py','new_http.py']:
 src=ROOT/'audit_evidence_claims/m18/attacks'/name;s=src.read_text(encoding='utf8')
 s=s.replace('m18_previous','m19_previous').replace('PORT = 9132','PORT = 19193')
 var='cases' if name=='new_probe.py' else 'CASES'
 s=re.sub(r'^'+var+r' = .*$',var+' = '+repr(cases),s,flags=re.M)
 dst=OUT/name;dst.write_text(s,encoding='utf8')
 manifest.append({'source':str(src.relative_to(ROOT)),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'destination':str(dst.relative_to(ROOT)),'destination_sha256':hashlib.sha256(dst.read_bytes()).hexdigest(),'adaptations':['new case list, saved verbatim in new_cases.json','module label m19_previous','HTTP port 19193'],'cases':len(cases)})
(OUT/'reuse_manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf8')
print(json.dumps({'cases':len(cases),'scripts':len(manifest)}))
