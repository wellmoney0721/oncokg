import sys,json,sqlite3
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path.cwd();sys.path.insert(0,str(ROOT/'src'))
from app import Engine
import query,textrules as T
E=Engine();E.kg.conn.close();E.kg.conn=sqlite3.connect((ROOT/'data/processed/oncokg.sqlite').as_uri()+'?mode=ro',uri=True);E.kg.conn.row_factory=sqlite3.Row
cases=['M vasi','M.vasi','bevacizumab - P.fizer','bevacizumab - Pf izer','bevacizumab-Pfizer','bevacizumab P.fizer','bio.similar bevacizumab','b.i.o.similar bevacizumab','biosimilar bevacizumab','lip.osomal doxorubicin','liposomal doxorubicin','trastuzumab 89Zr-labelled','[89Zr]labelled trastuzumab','[89Zr]-labelled trastuzumab','[89Z.r]labelled trastuzumab','trastuzumab (89Z.r-labelled)','bevacizumab a.w.w.b','A33 1.2.4.i']
rows=[]
for t in cases:
 n=query._fold(t);b=E.kg._resolver_blocked(n);f=E.kg._link(n);r={'text':t,'key':T.canonical_key(t),'resolver':E.resolve(t),'blocked':b,'found':f,'whole':E.kg._whole_name(n,b,f),'map':E.explore(t,1),'qualified':query._qualified(t.split())}
 rows.append(r);print(json.dumps({'text':t,'center':r['map'].get('center',{}).get('label'),'blocked':b,'found':f,'resolver_tiers':[x['tier'] for x in r['resolver']['components']]},ensure_ascii=True))
(ROOT/'audit_evidence_claims/m12/attacks/quick.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf8')
