"""Exact separator and hyphenated-form controls against 574097f; read-only."""
import ast,json,sqlite3,subprocess,sys,textwrap,types
from pathlib import Path
sys.path.insert(0,str(Path('src').resolve()))
import query
from app import Engine
OUT=Path('audit_evidence_claims/m17/names')
cur=Engine();old=Engine()
source=subprocess.check_output(['git','show','574097f:src/query.py']).decode('utf8')
tree=ast.parse(source);ns=dict(query.__dict__)
for n in tree.body:
    if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='_JOINERS' for t in n.targets):ns['_JOINERS']=ast.literal_eval(n.value)
m=next(n for n in ast.walk(tree) if isinstance(n,ast.FunctionDef) and n.name=='link_entities')
exec(compile(textwrap.dedent(ast.get_source_segment(source,m)),'574097f:src/query.py','exec'),ns)
old.kg.link_entities=types.MethodType(ns['link_entities'],old.kg)
for e in (cur,old):
    e.kg.conn.close();e.kg.conn=sqlite3.connect('file:data/processed/oncokg.sqlite?mode=ro',uri=True);e.kg.conn.row_factory=sqlite3.Row
inputs=[
    'osimertinib; generic version of bevacizumab',
    'osimertinib， generic version of bevacizumab',
    'osimertinib, generic version of bevacizumab',
    'paclitaxel with albumin-bound nanoparticles',
    'bevacizumab with albumin-bound nanoparticles',
    'paclitaxel with albumin bound nanoparticles',
    'Which trials evaluate osimertinib; generic version of bevacizumab?',
    'Which trials evaluate osimertinib， generic version of bevacizumab?',
    'Which trials evaluate paclitaxel with albumin-bound nanoparticles?',
]
def result(e,s):
    v=e.explore(s)
    return {'linker':e.kg.link_entities(s),'map':{k:v for k,v in v.items() if k!='groups'},'answer':e.ask(s)}
rows=[{'input':s,'input_codepoints':['U+%04X'%ord(c) for c in s if ord(c)>127],
       'resolver':cur.resolve(s),'current':result(cur,s),'previous':result(old,s)} for s in inputs]
OUT.joinpath('names_separator_checks.json').write_text(json.dumps({'baseline':'574097f exact method and _JOINERS','cases':rows},ensure_ascii=False,indent=2),encoding='utf8')
for r in rows:
    print(json.dumps({'input':r['input'],'current_center':r['current']['map'].get('center',{}).get('id'),
                      'previous_center':r['previous']['map'].get('center',{}).get('id'),
                      'current_refused':r['current']['map'].get('refused'),'previous_refused':r['previous']['map'].get('refused'),
                      'current_evidence':len(r['current']['answer']['evidence']),'previous_evidence':len(r['previous']['answer']['evidence'])},ensure_ascii=False))
for e in (cur,old):e.kg.conn.close()
