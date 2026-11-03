"""Reproduce additional current comma-boundary controls in isolation."""
import json,sqlite3,sys
from pathlib import Path
sys.path.insert(0,str(Path('src').resolve()))
from app import Engine
e=Engine()
e.kg.conn.close()
e.kg.conn=sqlite3.connect('file:data/processed/oncokg.sqlite?mode=ro',uri=True)
e.kg.conn.row_factory=sqlite3.Row
inputs=['biosimilar anastrozole, Arimidex','biosimilar anastrozole and Arimidex','Arimidex',
        'biosimilar recombinant, interleukin-2','interleukin-2','biosimilar lidocaine, patch','patch',
        'biosimilar Prolia, xgeva','xgeva','biosimilar pembrolizumab, Keytruda','Keytruda',
        'biosimilar nivolumab, Opdivo','Opdivo']
rows=[]
for s in inputs:
    m=e.explore(s);m.pop('groups',None)
    rows.append({'input':s,'map':m,'linker':e.kg.link_entities(s),'resolver':e.resolve(s)})
Path('audit_evidence_claims/m5/names_cross_item_refusal.json').write_text(
    json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'cases':len(rows)}))
e.kg.conn.close()
