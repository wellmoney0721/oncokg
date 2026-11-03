import json,sys,hashlib,subprocess
from pathlib import Path
sys.dont_write_bytecode=True
out=Path(__file__).resolve().parent;root=out.parents[2];sys.path.insert(0,str(root/'src'))
import query,textrules as T
from app import Engine
e=Engine()
labels=['124I','I-124','I124','H3','3H','Ga68','68Ga','Zr89','89Zr']
x={'head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip(),'helpers':{s:{'key':T.canonical_key(s),'medical_mass_first':query._medical_isotope(s),'medical_in':query._medical_isotope_in(T.canonical_key(s)),'labelled':query._labelled(s),'old_isotope_label':T.is_isotope_label(s),'old_radiotracer':T.is_radiotracer(s)} for s in labels},'preferred_name':'TRASTUZUMAB','preferred_is_labelled':query._labelled('TRASTUZUMAB'),'vinblastine_stored_tracer_hits':e.dic['index'].get('3hvinblastine'),'sources':[{'title':'Construction of 124I-trastuzumab for noninvasive PET imaging of HER2 expression','url':'https://pubmed.ncbi.nlm.nih.gov/31919745/','support':'Primary clinical study establishes that 124I-trastuzumab is a radiolabelled PET tracer, distinct from unlabelled trastuzumab.'},{'title':'NCI definition of iodine I 124 CPD-1028','url':'https://www.cancer.gov/publications/dictionaries/cancer-drug/def/iodine-i-124-cpd-1028','support':'NCI uses the abbreviation [I-124]-CPD-1028 for an iodine-124 radioconjugate, supporting the element-first notation.'},{'title':'FDA GSRS IODINE I-124','url':'https://precision.fda.gov/ginas/app/ui/substances/6432f496-edbb-4482-b6a0-00f18498bf8a','support':'FDA substance entry uses IODINE I-124.'}]}
(out/'helper_identity_evidence.json').write_text(json.dumps(x,ensure_ascii=False,indent=2),encoding='utf8');e.kg.conn.close()
manifest=json.loads((out/'reuse_manifest.json').read_text(encoding='utf8'))
manifest.extend([{'source':'audit_evidence_claims/m15/attacks/targeted_probe.py','output':'audit_evidence_claims/m16/attacks/new_probe.py','adaptations':['Replace cases with 42 new targeted controls/attacks','Rename outputs new_* and previous in-memory module m16_previous']},{'source':'audit_evidence_claims/m15/attacks/targeted_http.py','output':'audit_evidence_claims/m16/attacks/new_http.py','adaptations':['Replace cases with same 42 targeted inputs','Port 8945 -> 8970','Rename outputs new_*']}])
(out/'reuse_manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf8')
checks={}
for stem in ['focused','fresh','edge','targeted','new']:
 data=json.loads((out/(stem+'_results.json')).read_text(encoding='utf8')); checks[stem]={'cases':len(data['cases']),'head':data['head'],'previous':data['previous']}
checks['http']=json.loads((out/'new_lifecycle.json').read_text(encoding='utf8'))
checks['reused_scripts']=json.loads((out/'reuse_execution.json').read_text(encoding='utf8'))
(out/'execution_summary.json').write_text(json.dumps(checks,indent=2),encoding='utf8')
print(json.dumps(checks,indent=2))
