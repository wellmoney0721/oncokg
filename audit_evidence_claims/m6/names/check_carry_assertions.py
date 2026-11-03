"""Validate the reported carry cases against complete fresh Engine evidence."""
import json
from pathlib import Path
OUT=Path('audit_evidence_claims/m6/names')
data=json.loads((OUT/'focused_new.json').read_text(encoding='utf8'))
by={row['input']:row for row in data['cases']}
rows=[]
for s in ['(Mvasi) and bevacizumab','[Mvasi] and bevacizumab','"Mvasi" and bevacizumab']:
    r=by[s];a,b=r['current'],r['previous_m5']
    passed=(a['map'].get('center') is None and a['map'].get('refused')
            and not a['answer']['evidence'] and b['map'].get('center',{}).get('id')=='CHEMBL1201583')
    rows.append({'input':s,'expectation':'current refuses separately named bevacizumab; exact M5 maps it',
                 'passed':bool(passed),'current_map':a['map'],'previous_center':b['map'].get('center')})
for s in ['liposomal, and doxorubicin','liposomal and; doxorubicin','liposomal and / doxorubicin','liposomal and | doxorubicin']:
    r=by[s];a,b=r['current'],r['previous_m5']
    passed=(a['map'].get('center') is None and a['map'].get('refused')=='liposomal ... doxorubicin'
            and not a['answer']['evidence'] and b['map'].get('center',{}).get('id')=='CHEMBL53463')
    rows.append({'input':s,'expectation':'current carry crosses hard boundary; exact M5 maps doxorubicin',
                 'passed':bool(passed),'current_map':a['map'],'previous_center':b['map'].get('center')})
for s in ['Mvasi and bevacizumab','Mvasi, bevacizumab']:
    a=by[s]['current']['map']
    rows.append({'input':s,'expectation':'control maps bevacizumab and discloses Mvasi refusal',
                 'passed':a.get('center',{}).get('id')=='CHEMBL1201583' and {'refused':'Mvasi'} in a.get('also',[]),
                 'current_map':a})
out={'source':'focused_new.json','head':data['head'],'query_sha256':data['query_sha256'],
     'checks':len(rows),'passed':sum(r['passed'] for r in rows),'assertions':rows}
(OUT/'carry_assertions.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({k:v for k,v in out.items() if k!='assertions'}))
assert all(r['passed'] for r in rows)
