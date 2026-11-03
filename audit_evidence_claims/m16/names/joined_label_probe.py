"""Independent normalized-alias probe: isotope glued to intervening chelator."""
from pathlib import Path
import json,sys,sqlite3
root=Path.cwd();out=Path(__file__).resolve().parent;sys.path.insert(0,str(root/'src'))
from app import Engine
import query,textrules as T
e=Engine();e.kg.conn.close();e.kg.conn=sqlite3.connect((root/'data/processed/oncokg.sqlite').as_uri()+'?mode=ro',uri=True);e.kg.conn.row_factory=sqlite3.Row
rows=[]
for text in ['89zrdfodaratumumab','89ZrDFO-daratumumab','[89ZrDFO]-daratumumab','89zrdfo daratumumab','89Zr-DFOdaratumumab','[89Z.r]-DFO-daratumumab','89Zr-dfo-daratumumab','daratumumab','89ZrDFO-daratumumab, osimertinib']:
 norm=query._fold(text);b=e.kg._resolver_blocked(norm);f=e.kg._link(norm)
 rows.append(dict(text=text,key=T.canonical_key(text),words=query._alnum_words(text),dictionary=e.dic['index'].get(T.canonical_key(text),[]),resolver=e.resolve(text),blocked=b,item_linker=f,whole_name=e.kg._whole_name(norm,b,f),public_linker=e.kg.link_entities(text),map=e.explore(text,2),trial_qa=e.ask('Which trials evaluate '+text+'?'),sponsor_qa=e.ask('Who sponsors trials of '+text+'?')))
(out/'joined_label_probe.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps([dict(text=r['text'],center=r['map'].get('center',{}).get('id'),refused=r['map'].get('refused'),blocked=r['blocked'],trials=len(r['trial_qa']['evidence']),sponsors=len(r['sponsor_qa']['evidence'])) for r in rows],indent=2))
e.kg.conn.close()
