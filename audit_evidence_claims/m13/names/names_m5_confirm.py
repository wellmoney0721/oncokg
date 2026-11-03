"""Focused confirmed adversarial boundary cases, no network or writes beyond output."""
import ast,json,sqlite3,subprocess,sys,textwrap,types
from pathlib import Path
sys.path.insert(0,str(Path('src').resolve()))
import query,textrules as T
from app import Engine
OUT=Path('audit_evidence_claims/m13/names')
cur,old=Engine(),Engine()
source=subprocess.check_output(['git','show','bf436c6:src/query.py']).decode('utf8')
tree=ast.parse(source); ns=dict(query.__dict__)
for node in tree.body:
    if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='_JOINERS' for t in node.targets):ns['_JOINERS']=ast.literal_eval(node.value)
for name in ('link_entities','_drug_spans','_qualified_drug_spans'):
    method=next(n for n in ast.walk(tree) if isinstance(n,ast.FunctionDef) and n.name==name)
    exec(compile(textwrap.dedent(ast.get_source_segment(source,method)),'bf436c6:src/query.py','exec'),ns)
    setattr(old.kg,name,types.MethodType(ns[name],old.kg))
for e in (cur,old):
    e.kg.conn.close();e.kg.conn=sqlite3.connect('file:data/processed/oncokg.sqlite?mode=ro',uri=True);e.kg.conn.row_factory=sqlite3.Row
inputs=[
 'bevacizumab-awwb', 'bevacizumab-awwb/ osimertinib', 'bevacizumab-awwb / osimertinib',
 'bevacizumab - awwb/ osimertinib', 'bevacizumab - awwb / osimertinib',
 'bevacizumab - awwb & osimertinib','bevacizumab - awwb&osimertinib',
 'bevacizumab - awwb& osimertinib','bevacizumab - awwb /osimertinib',
 'bevacizumab-awwb| osimertinib','bevacizumab-awwb+ osimertinib',
 'Which trials evaluate bevacizumab-awwb/ osimertinib?',
 'Which companies sponsor bevacizumab-awwb/ osimertinib?',
 'bevacizumab - awwb\u061b osimertinib', 'bevacizumab - awwb\u060c osimertinib',
 'bevacizumab - awwb\uff64 osimertinib','bevacizumab - awwb\uff0f osimertinib',
 'Which trials evaluate liposomal and nanoparticle formulations of doxorubicin?',
 'Which companies sponsor biosimilar and investigational versions of bevacizumab?',
 'Which trials evaluate a liposomal and investigational formulation of doxorubicin?',
 'Which trials evaluate liposomal and sustained-release doxorubicin?',
 'liposomal and investigational formulation of doxorubicin',
 'Erlotinib','hydrochloride biosimilar bevacizumab',
 'Erlotinib, hydrochloride biosimilar bevacizumab',
 'Erlotinib; hydrochloride biosimilar bevacizumab',
 'Erlotinib and hydrochloride biosimilar bevacizumab',
 'Which trials evaluate Erlotinib, hydrochloride biosimilar bevacizumab?',
 'biosimilar interferon, alfa-2a','biosimilar interferon; alfa-2a','alfa-2a',
 'biosimilar interferon, alfa-2b','alfa-2b',
 'Pegylated interferon alfa-2a','PEGINTERFERON ALFA-2A','CHEMBL1201560',
 'Pegasys','Which trials evaluate Pegylated interferon alfa-2a?',
 'Which trials evaluate PEGINTERFERON ALFA-2A?',
 'biosimilar anastrozole, Arimidex','biosimilar anastrozole and Arimidex','Arimidex',
 'biosimilar Prolia, xgeva','biosimilar Prolia and xgeva','xgeva',
 'Which trials evaluate biosimilar anastrozole, Arimidex?',
 'Which trials evaluate biosimilar anastrozole and Arimidex?',
 'biosimilar recombinant, interleukin-2','interleukin-2',
]
def result(e,s):
    m=e.explore(s)
    return {'linker':e.kg.link_entities(s),'map':{k:v for k,v in m.items() if k!='groups'},'answer':e.ask(s)}
rows=[{'input':s,'resolver':cur.resolve(s),'distinct':T.is_distinct_product(s),'tracer':T.is_radiotracer(s),
       'current':result(cur,s),'previous':result(old,s)} for s in inputs]
OUT.joinpath('names_m5_confirm.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf8')
for r in rows:
    a,b=r['current'],r['previous']
    print(json.dumps({'input':r['input'],'map':a['map'],'old_center':b['map'].get('center',{}).get('id'),
                     'resolver':[(c['component'],c['tier'],c.get('drug_id')) for c in r['resolver']['components']],
                     'evidence':len(a['answer']['evidence']),'first_edge':next((e['edge_id'] for e in a['answer']['evidence']),None)},ensure_ascii=False))
for e in (cur,old):e.kg.conn.close()
