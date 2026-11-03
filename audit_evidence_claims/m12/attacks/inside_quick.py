import sys,json,re
from pathlib import Path
sys.dont_write_bytecode=True;sys.path.insert(0,str(Path.cwd()/'src'))
from app import Engine
import textrules as T,query
E=Engine();cases=['Lutetium (177L.u) dotatate','Lutetium (177Lu) dotatate','Lutetium (177L_u) dotatate','Lutetium (177 L u) dotatate','Lutetium (177L.u) dotatate, osimertinib','[89Z.r]-labelled trastuzumab','[89Z.r] labelled trastuzumab','[89Zr]-labelled trastuzumab','[89Zr] labelled trastuzumab']
rows=[]
for t in cases:
 f=E.kg._link(t);r={'text':t,'key':T.canonical_key(t),'hits':E.dic['index'].get(T.canonical_key(t)),'resolver':E.resolve(t),'blocked':E.kg._resolver_blocked(t),'found':f,'map':E.explore(t,1)};rows.append(r);print(json.dumps({'t':t,'center':r['map'].get('center',{}).get('label'),'found':f,'tiers':[x['tier'] for x in r['resolver']['components']]},ensure_ascii=True))
Path('audit_evidence_claims/m12/attacks/inside_quick.json').write_text(json.dumps(rows,indent=2,ensure_ascii=False),encoding='utf8')
