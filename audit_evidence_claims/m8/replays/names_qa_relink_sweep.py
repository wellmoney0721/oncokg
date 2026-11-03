"""Isolate no-relink on all aliases whose link result differs plus company/mixed questions."""
import ast,json,sqlite3,sys,textwrap,types
from pathlib import Path
sys.path.insert(0,str(Path('src').resolve()))
import query
from app import Engine
OUT=Path('audit_evidence_claims/m8/replays')
cur=Engine(); old=Engine()
src=Path('src/query.py').read_text(encoding='utf8')
method=next(n for n in ast.walk(ast.parse(src)) if isinstance(n,ast.FunctionDef) and n.name=='link_entities')
ns=dict(query.__dict__)
exec(compile(textwrap.dedent(ast.get_source_segment(src,method)).replace('(refused | matched)','refused'),'HEAD-with-relink','exec'),ns)
old.kg.link_entities=types.MethodType(ns['link_entities'],old.kg)
for e in (cur,old):
    e.kg.conn.close();e.kg.conn=sqlite3.connect('file:data/processed/oncokg.sqlite?mode=ro',uri=True);e.kg.conn.row_factory=sqlite3.Row
aliases=json.loads(OUT.joinpath('names_attack.json').read_text(encoding='utf8'))['multi_token_aliases']
changed=[r['input'] for r in aliases if r['current']!=r['relink']]
inputs=[template.format(name) for name in changed for template in ['Tell me about {}','Which trials evaluate {}?','Who sponsors {}?','What targets does {} act on?']]
inputs += [template.format(name) for name in ['AstraZeneca','National Cancer Institute','Bristol Myers Squibb','Johnson & Johnson','Pfizer','GlaxoSmithKline','MD Anderson Cancer Center','GSK 1120212 and EGFR','osimertinib and erlotinib hydrochloride','erlotinib hydrochloride and osimertinib','AstraZeneca and erlotinib hydrochloride','erlotinib hydrochloride and AstraZeneca'] for template in ['Tell me about {}','Which trials evaluate {}?','Who sponsors {}?','What targets does {} act on?']]
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
out={'baseline':'HEAD identical except matched tokens may be linked again','summary':counts,'inputs':inputs,'changed_answers':rows}
OUT.joinpath('names_qa_relink_sweep.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(counts))
for r in rows:
    if 'error' in r:print(r);continue
    print(r['input'],r['current']['intent'],'<-',r['relink']['intent'],len(r['current']['evidence']),len(r['relink']['evidence']))
for e in (cur,old):e.kg.conn.close()
