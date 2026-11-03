"""Bounded new boundary attacks, read-only DB and exact M5 predecessor methods."""
import ast,hashlib,json,sqlite3,subprocess,sys,textwrap,types
from pathlib import Path
sys.path.insert(0,str(Path('src').resolve()))
import query,textrules as T
from app import Engine
OUT=Path('audit_evidence_claims/m17/names')
current,previous=Engine(),Engine()
rev='514929c83fb7ab8cdd23fdd50eb300bd409c3250'
source=subprocess.check_output(['git','show',rev+':src/query.py']).decode('utf8')
tree=ast.parse(source); namespace=dict(query.__dict__)
for node in tree.body:
    if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='_JOINERS' for t in node.targets):
        namespace['_JOINERS']=ast.literal_eval(node.value)
for name in ('link_entities','_drug_spans'):
    node=next(n for n in ast.walk(tree) if isinstance(n,ast.FunctionDef) and n.name==name)
    exec(compile(textwrap.dedent(ast.get_source_segment(source,node)),rev+':src/query.py','exec'),namespace)
    setattr(previous.kg,name,types.MethodType(namespace[name],previous.kg))
for e in (current,previous):
    e.kg.conn.close();e.kg.conn=sqlite3.connect('file:data/processed/oncokg.sqlite?mode=ro',uri=True)
    e.kg.conn.row_factory=sqlite3.Row
inputs=[
 'bevacizumab-awwb', 'bevacizumab-awwb/ osimertinib', 'bevacizumab-awwb| osimertinib',
 'bevacizumab-awwb+ osimertinib','bevacizumab - awwb& osimertinib','bevacizumab - awwb&osimertinib',
 'bevacizumab - awwb/osimertinib','bevacizumab - awwb|osimertinib',
 'bevacizumab - awwb/EGFR','bevacizumab - awwb|EGFR',
 'bevacizumab - awwb / osimertinib','bevacizumab - awwb | osimertinib',
 'bevacizumab-awwb/osimertinib','bevacizumab-awwb|osimertinib',
 'Which trials evaluate bevacizumab - awwb/osimertinib?',
 'Which companies sponsor bevacizumab - awwb/osimertinib?',
 'Which trials evaluate bevacizumab-awwb+ osimertinib?',
 'Which companies sponsor bevacizumab-awwb+ osimertinib?',
 'Erlotinib/hydrochloride','Erlotinib|hydrochloride','Erlotinib / hydrochloride','Erlotinib | hydrochloride',
 'biosimilar anastrozole/Arimidex','biosimilar anastrozole|Arimidex',
 'biosimilar anastrozole, Arimidex','biosimilar Prolia, xgeva',
 'Erlotinib, hydrochloride biosimilar bevacizumab',
 'liposomal and nanoparticle formulation of doxorubicin',
 'liposomal and investigational formulation of doxorubicin',
 'doxorubicin in a novel and liposomal formulation',
 'bevacizumab in an investigational and biosimilar formulation',
 'Which trials evaluate doxorubicin in a novel and liposomal formulation?',
 'Which companies sponsor bevacizumab in an investigational and biosimilar formulation?',
 '[89Zr] and investigational trastuzumab','[89Zr] and copper labelled trastuzumab',
 '[89Zr] - and trastuzumab','[89Zr] versus trastuzumab','[89Zr] and [64Cu] trastuzumab',
 'liposomal and, doxorubicin','liposomal, and doxorubicin','liposomal and; doxorubicin',
 'liposomal and / doxorubicin','liposomal and | doxorubicin',
 'liposomal and unknown and doxorubicin','generic version and EGFR and bevacizumab',
 'Mvasi and bevacizumab','Mvasi, bevacizumab','(Mvasi) and bevacizumab',
 'liposomal and Mvasi and bevacizumab','liposomal and Mvasi, bevacizumab',
 'Pegylated interferon alfa-2a','PEGINTERFERON ALFA-2A',
 'CP-358,774','ERLOTINIB','CP-358','ENDOSTATIN, N-TERMINAL-MGGSHHHHH',
 'ENDOSTATIN','Rapamycin, 42-o-(2-hydroxyethyl)-',
 'Usp mab 003, monoclonal igg1','Usp mab 002, monoclonal igg1','12,13-desoxyepothilone b, cis',
 '\uff42\uff45\uff56\uff41\uff43\uff49\uff5a\uff55\uff4d\uff41\uff42\uff0d\uff41\uff57\uff57\uff42',
 'bevacizumab\u2014awwb','bevacizumab\u2013awwb','bevacizumab\u2011awwb',
 'bevacizumab \u2014 awwb','bevacizumab \uff0d awwb',
 '[\uff18\uff19\uff3a\uff52] trastuzumab','[89Zr] trastuzumab',
 '\uff3b89Zr\uff3d trastuzumab','[89Zr]\u2014trastuzumab',
 '(Mvasi), bevacizumab','[Mvasi] and bevacizumab','\"Mvasi\" and bevacizumab',
]
def result(e,s):
    m=e.explore(s);m.pop('groups',None)
    a=e.ask(s)
    return {'linker':e.kg.link_entities(s),'map':m,'answer':a}
rows=[]
for s in inputs:
    rows.append({'input':s,'distinct':T.is_distinct_product(s),'tracer':T.is_radiotracer(s),
                 'dictionary_hits':current.dic['index'].get(T.canonical_key(s),[]),
                 'resolver':current.resolve(s),'current':result(current,s),'previous_m5':result(previous,s)})
payload={'head':subprocess.check_output(['git','rev-parse','HEAD']).decode().strip(),
 'query_sha256':hashlib.sha256(Path('src/query.py').read_bytes()).hexdigest(),
 'baseline':rev+' exact link_entities, _drug_spans, _JOINERS; other source/data current', 'cases':rows}
(OUT/'focused_new.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding='utf8')
for r in rows:
    a,b=r['current'],r['previous_m5']
    print(json.dumps({'input':r['input'],'center':a['map'].get('center',{}).get('id'),
        'refused':a['map'].get('refused'),'also':a['map'].get('also'),
        'previous_center':b['map'].get('center',{}).get('id'),
        'evidence':len(a['answer']['evidence']),
        'first_edge':next((e['edge_id'] for e in a['answer']['evidence']),None)},ensure_ascii=False))
for e in (current,previous):e.kg.conn.close()
