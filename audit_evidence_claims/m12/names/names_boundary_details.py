"""Minimal refusal-span controls and regression evidence; all DB reads are read-only."""
import ast,json,sys,sqlite3,subprocess,textwrap,types
from pathlib import Path
sys.path.insert(0,str(Path('src').resolve()))
import query
from app import Engine
import textrules as T
OUT=Path('audit_evidence_claims/m12/names')
oldsource=subprocess.check_output(['git','show','bfcb83d:src/query.py']).decode('utf8')
method=next(n for n in ast.walk(ast.parse(oldsource)) if isinstance(n,ast.FunctionDef) and n.name=='link_entities')
namespace=dict(query.__dict__)
exec(compile(textwrap.dedent(ast.get_source_segment(oldsource,method)),'bfcb83d:src/query.py','exec'),namespace)
cur=Engine(); old=Engine()
for e in (cur,old):
 e.kg.conn.close();e.kg.conn=sqlite3.connect('file:data/processed/oncokg.sqlite?mode=ro',uri=True);e.kg.conn.row_factory=sqlite3.Row
old.kg.link_entities=types.MethodType(namespace['link_entities'],old.kg)
inputs=['generic version of bevacizumab','the generic version of bevacizumab','What is the generic version of bevacizumab?','generic version of bevacizumab and osimertinib','osimertinib and generic version of bevacizumab','Which trials evaluate osimertinib and generic version of bevacizumab?','Which companies sponsor osimertinib and generic version of bevacizumab?','oral azacitidine','osimertinib and oral azacitidine','[89Zr] trastuzumab','[89Zr] trastuzumab and osimertinib','osimertinib and [89Zr] trastuzumab','x '*300+'osimertinib','osimertinib '+'x '*300]
def map_summary(e,s):
 r=e.explore(s)
 return {k:v for k,v in r.items() if k!='groups'}
rows=[]
for s in inputs:
 a,b=cur.ask(s),old.ask(s)
 row={'input':s,'current_map':map_summary(cur,s),'baseline_map_using_old_linker':map_summary(old,s),'current_linker':cur.kg.link_entities(s),'baseline_linker':old.kg.link_entities(s),'resolver':cur.resolve(s),'current_answer':a,'baseline_answer':b}
 rows.append(row)
retired=[]
for r in cur.kg.conn.execute('SELECT id,type,label,retired_at FROM node WHERE retired_at IS NOT NULL'):
 retired.append({'stored':dict(r),'by_id':map_summary(cur,r['id']),'by_name':map_summary(cur,r['label'])})
# An isolated index fixture; no SQLite write. Model a multi-ID name as allowed by OncoKG.
cur.kg.companies['sharedbrand']=['ORG:astrazeneca','ORG:roche']
fixture=[{'input':s,'linker':cur.kg.link_entities(s),'map':map_summary(cur,s)} for s in ['Sharedbrand','Sharedbrand company']]
result={'cases':rows,'retired_names':retired,'multi_company_alias_fixture':fixture}
OUT.joinpath('names_boundary_details.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
for x in rows:
 print(json.dumps({'input':x['input'],'current':x['current_map'],'baseline_center':x['baseline_map_using_old_linker'].get('center',{}).get('id'),'resolver':[(c['component'],c['tier'],c.get('drug_id')) for c in x['resolver']['components']],'current_first_edge':next((z['edge_id'] for z in x['current_answer']['evidence']),None),'old_first_edge':next((z['edge_id'] for z in x['baseline_answer']['evidence']),None)},ensure_ascii=False))
print('alias_fixture',json.dumps(fixture,ensure_ascii=False))
cur.kg.conn.close();old.kg.conn.close()
