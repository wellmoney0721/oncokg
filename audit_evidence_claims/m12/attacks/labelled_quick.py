import sys,json
from pathlib import Path
sys.dont_write_bytecode=True;sys.path.insert(0,str(Path.cwd()/'src'))
from app import Engine
import query
E=Engine();cases=['trastuzumab labelled with [89Zr]','trastuzumab labeled with 89Zr','trastuzumab labelled 89Zr','89Zr labelled trastuzumab','89Zr-labeled trastuzumab','89Zr radiolabelled trastuzumab','trastuzumab-89Zr','trastuzumab (labelled with 89Zr)','[89Zr]-DFO-trastuzumab','[89Z.r]-DFO-trastuzumab','[89Z.r]-DFO trastuzumab','[89Z.r]-labelled trastuzumab, osimertinib']
rows=[]
for t in cases:
 r={'t':t,'map':E.explore(t,1),'resolver':E.resolve(t),'blocked':E.kg._resolver_blocked(t),'item':E.kg._link(t),'qualified':query._qualified(t.split())};rows.append(r);print(json.dumps({'t':t,'center':r['map'].get('center',{}).get('label'),'refused':[x for x in r['item'] if x['type']=='Refused'],'blocked':r['blocked'],'tiers':[x['tier'] for x in r['resolver']['components']]},ensure_ascii=True))
Path('audit_evidence_claims/m12/attacks/labelled_quick.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf8')
