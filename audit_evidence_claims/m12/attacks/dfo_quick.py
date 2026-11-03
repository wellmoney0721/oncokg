import sys,json
from pathlib import Path
sys.dont_write_bytecode=True;sys.path.insert(0,str(Path.cwd()/'src'))
from app import Engine
E=Engine();cases=['[89Z.r]-DFO-daratumumab','89Z_r-dfo-daratumumab','89Z.r-dfo-daratumumab','89Zr-dfo-daratumumab','[89Zr]-DFO-daratumumab','[89Z.r]-DFO-daratumumab, osimertinib','89Z.r-dfo daratumumab','89Z.r dfo daratumumab','daratumumab']
r=[]
for t in cases:
 x={'text':t,'map':E.explore(t,1),'raw':E.resolve(t),'blocked':E.kg._resolver_blocked(t),'item':E.kg._link(t),'qa':E.ask('Which trials evaluate '+t+'?')};r.append(x);print(json.dumps({'t':t,'center':x['map'].get('center'),'raw_tiers':[z['tier'] for z in x['raw']['components']],'blocked':x['blocked'],'item':x['item'],'qa_n':len(x['qa']['evidence'])},ensure_ascii=True))
Path('audit_evidence_claims/m12/attacks/dfo_quick.json').write_text(json.dumps(r,ensure_ascii=False,indent=2),encoding='utf8')
