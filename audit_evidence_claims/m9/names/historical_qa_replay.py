"""Isolate no-relink on all aliases whose link result differs plus company/mixed questions."""
import ast,json,sqlite3,sys,textwrap,types
from pathlib import Path
sys.path.insert(0,str(Path('src').resolve()))
import query
from app import Engine
OUT=Path('audit_evidence_claims/m9/names')
cur=Engine(); old=Engine()
src=Path('src/query.py').read_text(encoding='utf8')
method=next(n for n in ast.walk(ast.parse(src)) if isinstance(n,ast.FunctionDef) and n.name=='link_entities')
ns=dict(query.__dict__)
exec(compile(textwrap.dedent(ast.get_source_segment(src,method)).replace('(refused | matched)','refused'),'HEAD-with-relink','exec'),ns)
old.kg.link_entities=types.MethodType(ns['link_entities'],old.kg)
for e in (cur,old):
    e.kg.conn.close();e.kg.conn=sqlite3.connect('file:data/processed/oncokg.sqlite?mode=ro',uri=True);e.kg.conn.row_factory=sqlite3.Row
input_sources=['audit_evidence_claims/m4/qa_relink_sweep.json',
               'audit_evidence_claims/m5/names_qa_relink_sweep.json']
inventories=[json.loads(Path(p).read_text(encoding='utf8'))['inputs'] for p in input_sources]
inputs=list(dict.fromkeys(s for values in inventories for s in values))
rows=[]
counts={'questions':len(inputs),'identical':0,'entities_only':0,'semantic_changes':0,'errors':0}
for s in inputs:
    try:
        a,b=cur.ask(s),old.ask(s)
        # Effects on answer/evidence/intent matter separately from pruned entity metadata.
        sema={k:v for k,v in a.items() if k!='entities'}
        semb={k:v for k,v in b.items() if k!='entities'}
        kind='identical' if a==b else 'entities_only' if sema==semb else 'semantic_changes'
        counts[kind]+=1
        if kind=='semantic_changes':rows.append({'input':s,'current':a,'relink':b})
    except Exception as ex:
        counts['errors']+=1;rows.append({'input':s,'error':repr(ex)})
out={'baseline':'HEAD identical except matched tokens may be linked again','input_sources':input_sources,'source_input_counts':[len(v) for v in inventories],'summary':counts,'inputs':inputs,'changed_answers':rows}
OUT.joinpath('historical_qa_replay.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(counts))
for r in rows:
    if 'error' in r:print(r);continue
    print(r['input'],r['current']['intent'],'<-',r['relink']['intent'],len(r['current']['evidence']),len(r['relink']['evidence']))
for e in (cur,old):e.kg.conn.close()
