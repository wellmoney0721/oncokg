import json,sys,re,sqlite3
from pathlib import Path
ROOT=Path.cwd(); OUT=Path("C:\\Users\\geoum\\Dropbox\\GY's Formal Workspace\\2026 Job recruting\\바이오리서치에이아이\\oncokg\\audit_evidence_claims\\s4\\faithful\\s1")
sys.path.insert(0,str(ROOT/'src'))
import query as Q
kg=Q.OncoKG(); kg.conn.execute('PRAGMA query_only=ON')
questions=[
'Which companies are developing osimertinib?',
'What trials evaluate Tagrisso?',
'What does osimertinib target?',
'Which drugs act on ALK?',
'What is AstraZeneca running in NSCLC?',
'What is the capital of France?',
'What is osimertinib?']
def retrieve(q):
    ents=kg.link_entities(q); return ents,kg.classify(q,ents),kg.retrieve(kg.classify(q,ents),ents)
def node(i):
    n=dict(kg.conn.execute('SELECT * FROM node WHERE id=?',(i,)).fetchone()); n['props']=json.loads(n['props']); return n
def build(ev,use_ids=False):
    claims=[]
    for e in ev:
        if e.relation=='PROFILE':
            dn=node(e.edge_id.split(':',1)[1]); p=dn['props']
            c={'kind':'drug','drug':dn['id'] if use_ids else dn['label'],'evidence':e.edge_id,'trials_in_graph':int(re.search(r'appearing in (\d+) NSCLC',e.statement)[1])}
            if p.get('max_phase_overall'): c['max_stage']=p['max_phase_overall']
            claims.append(c); continue
        edge=dict(kg.conn.execute('SELECT * FROM edge WHERE id=?',(e.edge_id,)).fetchone()); p=json.loads(edge['props'])
        sn,dn=node(edge['src']),node(edge['dst'])
        c={'kind':'relation','relation':edge['rel'],'subject':sn['id'] if use_ids else sn['label'],'object':dn['id'] if use_ids else dn['label'],'evidence':e.edge_id}
        if edge['rel']=='SPONSORS_TRIAL_OF': c['trial_count']=p['evidence_trials']
        elif edge['rel']=='ACTS_ON' and p.get('action_type'): c['action']=p['action_type']
        claims.append(c)
        if edge['rel']=='EVALUATES':
            claims.append({'kind':'trial','trial':sn['id'],'evidence':e.edge_id,'phase':sn['props'].get('phases') or [],'status':sn['props']['status']})
        elif edge['rel']=='ACTS_ON' and 'max stage' in e.statement:
            c={'kind':'drug','drug':sn['id'] if use_ids else sn['label'],'evidence':e.edge_id,'trials_in_graph':e.detail['trials_in_graph']}
            if sn['props'].get('max_phase_overall'): c['max_stage']=sn['props']['max_phase_overall']
            claims.append(c)
    return {'claims':claims}
results=[]
for q in questions:
    ents,intent,ev=retrieve(q)
    modes={}
    for mode in ['labels','ids']:
        payload=build(ev,mode=='ids')
        modes[mode]={'input':payload,'output':kg.verify_structured(payload,ev)} if ev else {'input':payload,'output':kg.answer(q,use_llm=True).to_dict()}
    results.append({'question':q,'intent':intent,'entities':ents,'evidence':[e.__dict__ for e in ev],'modes':modes})
# Locate a real default-retrieval example with empty phase(s), plus mixed phases.
phase_examples=[]
for row in kg.conn.execute("SELECT e.dst,n.label FROM edge e JOIN node n ON n.id=e.dst WHERE e.rel='EVALUATES' AND e.retired_at IS NULL GROUP BY e.dst"):
    q=f"What trials evaluate {row['label']}?"; ents,intent,ev=retrieve(q)
    for e in ev:
        ph=e.detail.get('phases')
        category='empty' if not ph else 'multiple' if len(ph)>1 else None
        if category and category not in [x['category'] for x in phase_examples]:
            payload={'claims':[c for c in build([e])['claims'] if c['kind']=='trial']}
            phase_examples.append({'category':category,'question':q,'evidence':e.__dict__,'input':payload,'output':kg.verify_structured(payload,ev)})
    if len(phase_examples)==2: break
# Schema rejects evidence facts outside the fixed kinds.
_,_,ev=retrieve('What is osimertinib?')
base=build(ev)['claims'][0]
limitations=[]
for key,value in [('drug_type','Small molecule'),('aliases_known',len(kg.dic['drugs']['CHEMBL3353410']['aliases']))]:
    c=dict(base); c[key]=value
    limitations.append({'question':'What is osimertinib?','input':{'claims':[c]},'output':kg.verify_structured({'claims':[c]},ev)})
# Current action-code diversity, stage values and missing fields for rendering audit.
codes={}
for rel,key in [('ACTS_ON','action_type'),('SPONSORS_TRIAL_OF','evidence_trials')]:
    vals={}
    for row in kg.conn.execute('SELECT props FROM edge WHERE rel=? AND retired_at IS NULL',(rel,)):
        v=json.loads(row['props']).get(key); vals[str(v)]=vals.get(str(v),0)+1
    codes[key]=vals
report={'commit':'aa5655ae89c47631fefb9c868989ba2c1befa82e','demonstrations':results,'phase_examples':phase_examples,'schema_limitations':limitations,'codes':codes}
(OUT/'faithful_results.json').write_text(json.dumps(report,indent=2,ensure_ascii=False),encoding='utf-8')
for r in results:
    print(r['question'])
    for k,v in r['modes'].items():
        o=v['output']; print(k, 'accepted',len(o.get('accepted',[])), 'rejected',len(o.get('rejected',[])), 'verified',o.get('verified'))
        if o.get('rejected'): print(json.dumps(o['rejected'],ensure_ascii=False))
for r in phase_examples: print(json.dumps(r,ensure_ascii=False))
print('Action codes',codes['action_type'])
