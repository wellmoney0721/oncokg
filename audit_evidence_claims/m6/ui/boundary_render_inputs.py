from pathlib import Path
import json,sqlite3,sys
sys.path.insert(0,str(Path('src').resolve()))
from app import Engine
out=Path(__file__).parent
e=Engine();e.kg.conn.close();e.kg.conn=sqlite3.connect('file:data/processed/oncokg.sqlite?mode=ro',uri=True);e.kg.conn.row_factory=sqlite3.Row
inputs=['bevacizumab - awwb/osimertinib','bevacizumab - awwb& osimertinib','bevacizumab-awwb+ osimertinib','bevacizumab-awwb& osimertinib','bevacizumab-awwb + osimertinib','bevacizumab-awwb & osimertinib']
rows=[]
for text in inputs:
    response=e.explore(text)
    row={'input':text,'response':response,'resolve':e.resolve(text),'entities':e.kg.link_entities(text)}
    rows.append(row)
    print(json.dumps({'input':text,'center':response.get('center',{}).get('id'),'refused':response.get('refused'),'also':response.get('also')},ensure_ascii=False))
(out/'boundary_render_inputs.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf8')
