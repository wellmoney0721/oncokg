"""M5 focused boundaries and lone stored aliases; read-only exact predecessor comparison."""
import ast,json,re,sqlite3,subprocess,sys,textwrap,types,time
from pathlib import Path
sys.path.insert(0,str(Path('src').resolve()))
import query
import textrules as T
from app import Engine
OUT=Path('audit_evidence_claims/m19/names')
cur,old=Engine(),Engine()
source=subprocess.check_output(['git','show','bf436c6:src/query.py']).decode('utf8')
tree=ast.parse(source); ns=dict(query.__dict__)
for node in tree.body:
    if isinstance(node,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='_JOINERS' for t in node.targets):
        ns['_JOINERS']=ast.literal_eval(node.value)
for name in ('link_entities','_drug_spans','_qualified_drug_spans'):
    method=next(n for n in ast.walk(tree) if isinstance(n,ast.FunctionDef) and n.name==name)
    exec(compile(textwrap.dedent(ast.get_source_segment(source,method)),'bf436c6:src/query.py','exec'),ns)
    setattr(old.kg,name,types.MethodType(ns[name],old.kg))
for engine in (cur,old):
    engine.kg.conn.close();engine.kg.conn=sqlite3.connect('file:data/processed/oncokg.sqlite?mode=ro',uri=True)
    engine.kg.conn.row_factory=sqlite3.Row
def result(e,s):
    m=e.explore(s); a=e.ask(s)
    return {'linker':e.kg.link_entities(s),'map':{k:v for k,v in m.items() if k!='groups'},'answer':a}
inputs=[]
separators=[',',';', '\uff0c','\uff1b','\u3001','\n','\r\n','\t','/','|','\u2022','\u00b7','\u061b','\u060c','\uff64','\u3002','.',':','\u2014','\\','and','or','plus','versus','vs','vs.','+','&','then','followed','or/and','and/or','AND','as well as','together with','alongside']
for sep in separators:
    inputs += ['osimertinib '+sep+' biosimilar bevacizumab','biosimilar bevacizumab '+sep+' osimertinib']
inputs += [
    'biosimilar versions of bevacizumab and trastuzumab',
    'biosimilar bevacizumab and trastuzumab',
    'liposomal and pegylated doxorubicin',
    'liposomal or conventional doxorubicin',
    'liposomal and nanoparticle formulations of doxorubicin',
    'liposomal and nanoparticle doxorubicin',
    'liposomal and non-pegylated doxorubicin',
    'generic and biosimilar version of bevacizumab',
    'generic version of bevacizumab and osimertinib',
    'generic version of bevacizumab plus osimertinib',
    '[89Zr] and [64Cu] trastuzumab',
    '[89Zr] and copper labelled trastuzumab',
    '[89Zr] - and [64Cu] - trastuzumab',
    '[89Zr] - and trastuzumab',
    '[89Zr] versus trastuzumab',
    'daratumumab and hyaluronidase-fihj',
    'bevacizumab - awwb and osimertinib',
    'bevacizumab - awwb & osimertinib',
    'bevacizumab - awwb&osimertinib',
    'bevacizumab - awwb/osimertinib',
    'bevacizumab - awwb|osimertinib',
    'bevacizumab - awwb;osimertinib',
    'bevacizumab - awwb；osimertinib',
    'bevacizumab - awwb、osimertinib',
    'bevacizumab - awwb，osimertinib',
    'bevacizumab-awwb/osimertinib',
    'bevacizumab-awwb/ osimertinib',
    'bevacizumab-awwb /osimertinib',
    'bevacizumab-awwb/osimertinib EGFR',
    'osimertinib mesylate, biosimilar bevacizumab',
    'osimertinib, mesylate biosimilar bevacizumab',
    'Erlotinib hydrochloride, biosimilar bevacizumab',
    'Erlotinib, hydrochloride biosimilar bevacizumab',
    'Erlotinib; hydrochloride biosimilar bevacizumab',
    'Erlotinib and hydrochloride biosimilar bevacizumab',
    'Paclitaxel conjugate, with poly-l-glutamic acid biosimilar bevacizumab',
    'Paclitaxel, conjugate with poly-l-glutamic acid',
    'EGFR biosimilar bevacizumab',
    'AstraZeneca biosimilar bevacizumab',
    'Johnson & Johnson biosimilar bevacizumab',
    'EGFR and AstraZeneca biosimilar bevacizumab',
]
inputs=list(dict.fromkeys(inputs))
rows=[]
for s in inputs:
    rows.append({'input':s,'distinct':T.is_distinct_product(s),'tracer':T.is_radiotracer(s),
                 'resolver':cur.resolve(s),'current':result(cur,s),'previous':result(old,s)})
alias_rows=[];checks=0
for key,hits in cur.dic['index'].items():
    if len({h['drug_id'] for h in hits})!=1:continue
    checks+=1
    s=hits[0]['alias'];a,b=cur.kg.link_entities(s),old.kg.link_entities(s)
    current_ids=[x.get('id') for x in a if x['type']=='Drug'];old_ids=[x.get('id') for x in b if x['type']=='Drug']
    if any(x['type']=='Refused' for x in a) or a!=b:
        alias_rows.append({'input':s,'stored':hits[0],'current':a,'previous':b,
                           'current_ids':current_ids,'previous_ids':old_ids,
                           'resolver':cur.resolve(s)})
out={'baseline':'bf436c6 exact link_entities, _drug_spans, _qualified_drug_spans and _JOINERS; remaining code/data current',
     'cases':rows,'alias_keys_checked':checks,'alias_anomalies':alias_rows}
OUT.joinpath('names_m5_attack.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8')
summary={'cases':len(rows),'aliases_checked':checks,'alias_anomalies':len(alias_rows),
         'new_lone_alias_refusals':[r for r in alias_rows if r['previous_ids'] and not r['current_ids']]}
OUT.joinpath('names_m5_summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({k:v for k,v in summary.items() if k!='new_lone_alias_refusals'},ensure_ascii=False))
for r in summary['new_lone_alias_refusals']:print('ALIAS REGRESSION',json.dumps(r,ensure_ascii=False))
for row in rows:
    a,b=row['current']['map'],row['previous']['map']
    print(json.dumps({'input':row['input'],'center':a.get('center',{}).get('id'),'refused':a.get('refused'),
                     'also':a.get('also'),'previous_center':b.get('center',{}).get('id'),
                     'distinct':row['distinct'],'tracer':row['tracer'],'evidence':len(row['current']['answer']['evidence'])},ensure_ascii=False))
for engine in (cur,old):engine.kg.conn.close()
