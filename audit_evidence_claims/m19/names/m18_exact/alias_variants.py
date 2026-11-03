import sys,json,re,time
from pathlib import Path
sys.dont_write_bytecode=True
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[3]
sys.path.insert(0,str(ROOT/'src'))
from app import Engine
import query,textrules as T
e=Engine();cases=[];seen=set()
for k,hits in e.dic['index'].items():
 if len({h['drug_id'] for h in hits})!=1:continue
 h=hits[0];a=h['alias'];did=h['drug_id']
 if not any(T.is_isotope_label(' '.join(ws)) for i in range(len(query._alnum_words(a))) for ws in [query._alnum_words(a)[i:i+1],query._alnum_words(a)[i:i+2]]):continue
 ctrl=e.explore(a,1)
 for t in {a,re.sub(r'[^A-Za-z0-9]','',a),re.sub(r'[^A-Za-z0-9]','',a).upper(),re.sub(r'[^A-Za-z0-9]','',a).lower(),a.replace('-',''),a.replace(' ','')}:
  if t in seen:continue
  seen.add(t);r=e.explore(t,1)
  cases.append({'text':t,'alias':a,'key':k,'drug_id':did,'drug_name':e.dic['drugs'][did]['name'],'original_refused':ctrl.get('refused'),'center':r.get('center',{}).get('id'),'refused':r.get('refused')})
(OUT/'alias_variants.json').write_text(json.dumps(cases,ensure_ascii=False,indent=2),encoding='utf8')
leaks=[r for r in cases if r['original_refused'] and r['center']]
print(json.dumps({'cases':len(cases),'accepted_from_refused':leaks},ensure_ascii=False,indent=2))
e.kg.conn.close()
