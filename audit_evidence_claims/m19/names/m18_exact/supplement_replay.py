from pathlib import Path
import json,sys
out=Path(__file__).resolve().parent;root=Path.cwd();sys.path.insert(0,str(root/'src'))
import query
from app import Engine
e=Engine();prior=json.loads((root/'audit_evidence_claims/m18/attacks/labelled_exception_probe.json').read_text(encoding='utf8'));rows=[]
for old in prior:
 t=old['text'];row=dict(text=t,map=e.explore(t,2),linker=e.kg.link_entities(t),resolver=e.resolve(t),qualified=query._qualified(t.split()),blocked=e.kg._resolver_blocked(query._fold(t)),isotope=query._item_has_isotope(tuple(t.split())));rows.append(row)
(out/'labelled_exception_replay.json').write_text(json.dumps(dict(source='audit_evidence_claims/m18/attacks/labelled_exception_probe.json; exact text fields replayed because no standalone original generator exists',cases=rows),ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps([dict(text=r['text'],center=r['map'].get('center',{}).get('id'),refused=bool(r['map'].get('refused'))) for r in rows],indent=2));e.kg.conn.close()
