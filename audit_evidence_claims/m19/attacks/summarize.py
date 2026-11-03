import json
from pathlib import Path
O=Path(__file__).resolve().parent
rs=json.loads((O/'new_results.json').read_text(encoding='utf8'))
h=json.loads((O/'new_http.json').read_text(encoding='utf8'))
keys=['radio-labelled trastuzumab','radiolabelled trastuzumab','trastuzumab radioactively labelled','99m-technetium trastuzumab','technetium-99m trastuzumab','trastuzumab labelled with 99m-technetium','trastuzumab labelled with technetium-99m','trastuzumab radioimmunoconjugates','trastuzumab radiopharmaceuticals','trastuzumab radiopharmaceutical']
rows=[]
for t in keys:
 r=next(x for x in rs['cases'] if x['text']==t)
 c=r['current']; hs=[x for x in h if x['input']==t or x['input'] in ['Which trials evaluate '+t+'?','Who sponsors trials of '+t+'?']]
 row={'text':t,'current_center':c['map'].get('center'),'current_groups':[{k:g.get(k) for k in ('relation','direction','total')} for g in c['map'].get('groups',[])],'previous_center':r['previous']['map'].get('center',{}).get('label'),'qualified':c['qualified'],'item_has_isotope':c['item_has_isotope'],'blocked':c['blocked'],'marked_calls':c['marked_calls'],'whole_name':c['whole_name'],'linker':c['public_linker'],'resolver_tiers':[x['tier'] for x in c['resolver']['components']],'trial_evidence':len(c['trial_qa']['evidence']),'sponsor_evidence':len(c['sponsor_qa']['evidence']),'http':[{'endpoint':x['endpoint'],'status':x['status'],'center':x['response'].get('center',{}).get('id'),'refused':x['response'].get('refused'),'evidence':len(x['response'].get('evidence',[]))} for x in hs]}
 rows.append(row)
(O/'key_evidence.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps([{k:v for k,v in r.items() if k not in ['current_center','marked_calls','linker','http','current_groups']} for r in rows],ensure_ascii=False,indent=2))
print(json.dumps({'head':rs['head'],'previous':rs['previous'],'cases':len(rs['cases']),'http':len(h)}))
