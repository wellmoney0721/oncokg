"""Additional literal M11 report forms alongside unchanged original key-equivalence replay."""
import json,sqlite3,sys
from pathlib import Path
root=Path.cwd();out=Path(__file__).resolve().parent;sys.path.insert(0,str(root/'src'))
from app import Engine
e=Engine();e.kg.conn.close();e.kg.conn=sqlite3.connect((root/'data/processed/oncokg.sqlite').as_uri()+'?mode=ro',uri=True);e.kg.conn.row_factory=sqlite3.Row
inputs=['[89Z.r] trastuzumab','89Z_r trastuzumab','trastuzumab [89Z.r]','bevacizumab a - w w b','bevacizumab - a - w - w - b','bevacizumab a_w_w_b']
rows=[]
for name in inputs:
    for text in [name,name+', osimertinib']:
        m=e.explore(text,2);q=[e.ask(prefix+text+'?') for prefix in ['Which trials evaluate ','Which companies sponsor ']]
        rows.append(dict(text=text,expected_center='CHEMBL3353410' if text!=name else None,actual_center=m.get('center',{}).get('id'),map=m,linker=e.kg.link_entities(text),qa=q))
(out/'m11_exact.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(dict(cases=len(rows),mismatches=[r['text'] for r in rows if r['expected_center']!=r['actual_center']],pure_qa_evidence=[len(q['evidence']) for r in rows if not r['expected_center'] for q in r['qa']])))
e.kg.conn.close()
