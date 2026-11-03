"""Exact final QA questions and unsupported-form controls, read-only."""
import ast,json,sqlite3,subprocess,sys,textwrap,types
from pathlib import Path
sys.path.insert(0,str(Path('src').resolve()))
import query
from app import Engine
OUT=Path('audit_evidence_claims/m18/names')
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
questions=[
 'Which trials evaluate osimertinib with generic version of bevacizumab?',
 'Which companies sponsor osimertinib with generic version of bevacizumab?',
 'What targets does generic version of Paclitaxel conjugate with poly-l-glutamic acid act on?',
 'Which trials evaluate generic version of Paclitaxel conjugate with poly-l-glutamic acid?',
 'generic version of Paclitaxel conjugate with poly-l-glutamic acid',
 'What trials evaluate erlotinib hydrochloride and erlotinib?',
 'What trials evaluate erlotinib and erlotinib hydrochloride?',
]
rows=[{'input':s,'current':cur.ask(s),'previous':old.ask(s)} for s in questions]
forms=[]
for r in json.loads(Path('audit_evidence_claims/m3/names_unsupported_forms.json').read_text(encoding='utf8')):
    s=r['input'];v=cur.explore(s)
    forms.append({'input':s,'result':{k:v for k,v in v.items() if k!='groups'},'group_total':sum(g['total'] for g in v.get('groups',[]))})
OUT.joinpath('names_final_checks.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf8')
OUT.joinpath('names_unsupported_forms.json').write_text(json.dumps(forms,ensure_ascii=False,indent=2),encoding='utf8')
for r in rows:print(r['input'],len(r['current']['evidence']),len(r['previous']['evidence']),r['current']['evidence'][:1],r['previous']['evidence'][:1])
for e in (cur,old):e.kg.conn.close()
