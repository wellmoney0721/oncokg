from pathlib import Path
import hashlib,json,sqlite3,subprocess,sys,types
root=Path.cwd();out=Path(__file__).resolve().parent
sys.path.insert(0,str(root/'src'))
import query,textrules as T
from app import Engine
source=subprocess.check_output(['git','show','HEAD^:src/query.py'],cwd=root).decode('utf8')
mod=types.ModuleType('m12_previous_alias_query');mod.__file__=str(root/'src/query.py');sys.modules[mod.__name__]=mod
exec(compile(source,'HEAD^:src/query.py','exec'),mod.__dict__)
engines={'current':Engine(),'previous':Engine()};engines['previous'].kg.conn.close();engines['previous'].kg=mod.OncoKG()
for e in engines.values():
    e.kg.conn.close();e.kg.conn=sqlite3.connect((root/'data/processed/oncokg.sqlite').as_uri()+'?mode=ro',uri=True);e.kg.conn.row_factory=sqlite3.Row
rows=[]
for text in ['rad001c','RAD001C','rad','RAD001','EVEROLIMUS','CHEMBL1908360','001c','1C']:
    row=dict(text=text,canonical_key=T.canonical_key(text),dictionary=engines['current'].dic['index'].get(T.canonical_key(text),[]),is_isotope=T.is_isotope_label(text))
    for label,e in engines.items():
        norm=query._fold(text);blocked=e.kg._resolver_blocked(norm);found=e.kg._link(norm)
        row[label]=dict(resolver=e.resolve(text),blocked=blocked,item_linker=found,whole_name=e.kg._whole_name(norm,blocked,found),public_linker=e.kg.link_entities(text),map=e.explore(text,2),trial_qa=e.ask('Which trials evaluate '+text+'?'))
    rows.append(row)
payload=dict(head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),previous=subprocess.check_output(['git','rev-parse','HEAD^'],text=True).strip(),comparison_scope='HEAD^ query module with current app/rules/data; not a previous deployment reconstruction',previous_query_sha256=hashlib.sha256(source.encode()).hexdigest(),cases=rows)
(out/'new_alias_regression.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding='utf8')
for e in engines.values():e.kg.conn.close()
print(json.dumps([dict(text=r['text'],current=r['current']['map'].get('center',{}).get('id'),previous=r['previous']['map'].get('center',{}).get('id'),refused=r['current']['map'].get('refused')) for r in rows],indent=2))
