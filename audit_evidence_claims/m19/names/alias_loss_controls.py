from pathlib import Path
import json,sqlite3,sys
sys.path.insert(0,'src');from app import Engine
out=Path(__file__).resolve().parent;root=Path.cwd()
e=Engine();e.kg.conn.close();e.kg.conn=sqlite3.connect((root/'data/processed/oncokg.sqlite').as_uri()+'?mode=ro',uri=True);e.kg.conn.row_factory=sqlite3.Row
rows=[]
for alias,name,did in [('9-amino-20(s)-camptothecin','9-AMINOCAMPTOTHECIN','CHEMBL274070'),('il-6ra','TOCILIZUMAB','CHEMBL1237022'),('TAK-659F','MIVAVOTINIB','CHEMBL3979920')]:
 row={'alias':alias,'preferred':name,'id':did,'forms':[]}
 for text in [alias,name,did]:
  mp=e.explore(text,1);row['forms'].append({'text':text,'map':mp,'linker':e.kg.link_entities(text)})
 rows.append(row)
(out/'alias_loss_controls.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps([{'alias':r['alias'],'centers':[v['map'].get('center',{}).get('id') for v in r['forms']]} for r in rows]))
e.kg.conn.close()
