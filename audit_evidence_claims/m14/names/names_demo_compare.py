"""Compare the unchanged demo questions at HEAD and with only the bfcb83d linker restored."""
import ast,json,re,sys,sqlite3,subprocess,textwrap,types
from pathlib import Path
sys.path.insert(0,str(Path('src').resolve()))
import query
from app import Engine
OUT=Path('audit_evidence_claims/m14/names')
oldsource=subprocess.check_output(['git','show','bfcb83d:src/query.py']).decode('utf8')
method=next(n for n in ast.walk(ast.parse(oldsource)) if isinstance(n,ast.FunctionDef) and n.name=='link_entities')
oldglobals=dict(query.__dict__)
exec(compile(textwrap.dedent(ast.get_source_segment(oldsource,method)),'bfcb83d:src/query.py','exec'),oldglobals)
cur=Engine(); old=Engine()
for e in (cur,old):
 e.kg.conn.close();e.kg.conn=sqlite3.connect('file:data/processed/oncokg.sqlite?mode=ro',uri=True);e.kg.conn.row_factory=sqlite3.Row
old.kg.link_entities=types.MethodType(oldglobals['link_entities'],old.kg)
page=Path('web/try.html').read_text(encoding='utf8')
questions=json.loads(re.search(r'const EX2 = (\[.*?\]);',page,re.S).group(1))
module=ast.parse(Path('src/query.py').read_text(encoding='utf8'))
main=next(n for n in module.body if isinstance(n,ast.FunctionDef) and n.name=='main')
for n in ast.walk(main):
 if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='questions' for t in n.targets):
  cli=ast.literal_eval(n.value.values[-1])
questions=list(dict.fromkeys(questions+cli))
rows=[]
for q in questions:
 a,b=cur.ask(q),old.ask(q)
 rows.append({'input':q,'from_page':q in json.loads(re.search(r'const EX2 = (\[.*?\]);',page,re.S).group(1)),'same':a==b,'current':a,'baseline':b})
summary={'page_questions':7,'unique_page_and_cli_questions':len(rows),'identical':sum(x['same'] for x in rows),'differences':[x['input'] for x in rows if not x['same']],'rows':[{'input':x['input'],'intent':x['current']['intent'],'entities':[(y['type'],y['label']) for y in x['current']['entities']],'evidence_count':len(x['current']['evidence']),'generated_by':x['current']['generated_by'],'identical':x['same']} for x in rows]}
OUT.joinpath('names_demo_results.json').write_text(json.dumps({'summary':summary,'comparisons':rows},ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(summary,ensure_ascii=False,indent=2))
cur.kg.conn.close();old.kg.conn.close()
