from pathlib import Path
import json
OUT=Path(__file__).resolve().parent
raw=json.loads((OUT/'independent_m19_http.json').read_text(encoding='utf8'))
rows=[]
for offset in range(0,len(raw),4):
    resolve,explore,trial,sponsor=raw[offset:offset+4]
    b=explore['response']
    row=dict(input=explore['input'],statuses=[r['status'] for r in raw[offset:offset+4]],center=b.get('center',{}).get('id'),trials=b.get('center',{}).get('trials'),refused=b.get('refused'),also=b.get('also'),resolver_tiers=[c.get('tier') for c in resolve['response'].get('components',[])],trial_rows=len(trial['response'].get('evidence',[])),sponsor_rows=len(sponsor['response'].get('evidence',[])),generated_by=[trial['response'].get('generated_by'),sponsor['response'].get('generated_by')])
    rows.append(row)
by={r['input']:r for r in rows}
leaks=['radio-labelled trastuzumab','radio-labeled trastuzumab','trastuzumab radioactively labelled','99m-technetium trastuzumab','trastuzumab 99m-technetium']
refusals=['radiolabelled trastuzumab','radiolabeled trastuzumab','trastuzumab radiolabelled with iodine-124','technetium-99m trastuzumab','trastuzumab technetium-99m']
checks={
 'all_http_200':all(r['status']==200 for r in raw),
 'five_new_leaks':all(by[x]['center']=='CHEMBL1201585' and by[x]['refused'] is None and by[x]['trials']==13 and by[x]['trial_rows']==by[x]['sponsor_rows']==12 for x in leaks),
 'paired_controls_refuse':all(by[x]['center'] is None and by[x]['refused'] and by[x]['trial_rows']==by[x]['sponsor_rows']==0 for x in refusals),
 'explicit_labelled_drug_survives':by['fluorine-18 fluorodeoxyglucose']['center']=='CHEMBL2030434',
 'lead_compound_survives':by['lead compound osimertinib']['center']=='CHEMBL3353410',
 'known_unaccepted_supplements_leak':by['b.i.o.similar bevacizumab']['center']=='CHEMBL1201583' and by['lip.osomal doxorubicin']['center']=='CHEMBL53463',
 'deterministic_no_model':all(s in {'deterministic template (no language model)','refusal (no supporting evidence)'} for r in rows for s in r['generated_by'])
}
result=dict(cases=len(rows),requests=len(raw),checks=checks,assertions_passed=all(checks.values()),rows=rows)
(OUT/'independent_m19_summary.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({k:v for k,v in result.items() if k!='rows'},indent=2))
assert all(checks.values())
