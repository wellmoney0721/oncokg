"""S2 adversarial identity review. Persisted graph is query-only; fixtures in memory."""
import copy, json, sqlite3, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'src'))
from query import OncoKG
from structured import Verifier
kg=OncoKG(); kg.conn.execute('PRAGMA query_only=ON')
OUT=Path(__file__).parent
Q='What does osimertinib target?'
OSI='CHEMBL3353410'; EGFR='ENSG00000146648'
E=OSI+'|ACTS_ON|'+EGFR+'|'+OSI
base=dict(kind='relation',relation='ACTS_ON',subject='osimertinib',object='EGFR',evidence=E,action='INHIBITOR')
def ev(g,q=Q):
    es=g.link_entities(q); return g.retrieve(g.classify(q,es),es)
evidence=ev(kg)
out={'persisted':{},'cases':[],'fixtures':[]}
out['persisted']['duplicate_labels']=[dict(r) for r in kg.conn.execute("SELECT lower(label) label,COUNT(*) n,GROUP_CONCAT(type||':'||id) nodes FROM node WHERE retired_at IS NULL GROUP BY lower(label) HAVING COUNT(*)>1")]
out['persisted']['nonascii_labels']=[dict(r) for r in kg.conn.execute('SELECT id,type,label FROM node WHERE retired_at IS NULL') if not r['label'].isascii()]
out['persisted']['long_labels']=[dict(r) for r in kg.conn.execute('SELECT id,type,label FROM node WHERE retired_at IS NULL AND length(label)>120')]
nodes=[dict(r) for r in kg.conn.execute('SELECT id,type,label FROM node WHERE retired_at IS NULL')]
ids={n['id']:n for n in nodes}
out['persisted']['id_label_collisions']=[{'label_node':n,'id_node':ids[n['label']]} for n in nodes if n['label'] in ids and n['id']!=n['label']]
out['persisted']['exact_nonascii_resolve_failures']=[n for n in nodes if not n['label'].isascii() and Verifier(kg).resolve(n['label'],n['type'])[0]!={n['id']}]
import textrules as T
out['persisted']['label_alias_collisions']=[]
for n in nodes:
    key=T.canonical_key(n['label'])
    aliases=[('Drug',h['drug_id'],h['alias']) for h in kg.dic['index'].get(key,[]) if h['drug_id']!=n['id']]
    if n['label'].lower() in kg.targets:
        t=kg.targets[n['label'].lower()]
        if t['target_id']!=n['id']: aliases.append(('Target',t['target_id'],t['symbol']))
    for cid in kg.companies.get(key,[]):
        if cid!=n['id']: aliases.append(('Company',cid,n['label']))
    if aliases: out['persisted']['label_alias_collisions'].append({'node':n,'other_alias_matches':sorted(set(aliases))})
def run(tag,name,graph=kg,fixture=None,want='Drug',key='subject',claim=None):
    c=dict(base,**{key:name}) if claim is None else claim
    ids,reason=Verifier(graph).resolve(name,want)
    row={'tag':tag,'name':name,'want':want,'resolved_ids':sorted(ids),'reason':reason,'input':{'claims':[c]},'output':graph.verify_structured({'claims':[c]},evidence)}
    if fixture: row['fixture_change']=fixture
    out['fixtures' if fixture else 'cases'].append(row)
for n in ['osimertinib가 아닌','非osimertinib','osimertinib是安全的','osimertinib\u200b','osimertinib\x00','osimertinib\n','osimertinib\t','\u00a0osimertinib\u00a0','\ufeffosimertinib','!osimertinib','~osimertinib','osimertinib !=','osimertinib is not','NOT osimertinib','non-osimertinib','osimertinib/placebo','osimertinib NSCLC','osimertinib EGFR','osimertinib...','o-si-mer-ti-nib','CHEMBL3353410','chembl3353410','Tagrisso','osimertinib mesylate','ALECTINIB HYDROCHLORIDE']:
    run('literal:'+repr(n),n)
for n in ['EGFR','egfr','EGFR inhibitor','EGFR not','ENSG00000146648','CHEMBL3353410']:
    run('object:'+repr(n),n,want='Target',key='object')
def clone():
    g=copy.copy(kg); g.conn=sqlite3.connect(':memory:'); g.conn.row_factory=sqlite3.Row; kg.conn.backup(g.conn); return g
g=clone(); g.conn.execute("UPDATE node SET label='OSIMERTINIB' WHERE id='CHEMBL3707320'")
run('shared_same_type_exact_label','OSIMERTINIB',g,"Label CHEMBL3707320 changed from ALECTINIB HYDROCHLORIDE to OSIMERTINIB; existing OSIMERTINIB node unchanged")
run('shared_same_type_exact_label_id','CHEMBL3353410',g,'same duplicate Drug label fixture')
g=clone(); g.conn.execute("UPDATE node SET label='OSIMERTINIB' WHERE id=?",(EGFR,))
run('shared_cross_type_exact_label_subject','OSIMERTINIB',g,'EGFR Target label changed to OSIMERTINIB')
run('shared_cross_type_exact_label_object','OSIMERTINIB',g,'EGFR Target label changed to OSIMERTINIB',want='Target',key='object')
g=clone(); g.conn.execute("UPDATE node SET label=? WHERE id=?",('오시머티닙',OSI))
run('nonascii_exact_label','오시머티닙',g,'OSIMERTINIB Drug label changed to Korean 오시머티닙')
run('nonascii_label_extra_negation','오시머티닙가 아닌',g,'OSIMERTINIB Drug label changed to Korean 오시머티닙')
g=clone(); g.conn.execute("UPDATE node SET label=? WHERE id=?",('ÄRZT',OSI))
run('nonascii_exact_case','ÄRZT',g,'Drug label changed to ÄRZT')
run('nonascii_lowercase','ärzt',g,'Drug label changed to ÄRZT')
g=clone(); g.conn.execute("UPDATE node SET label=? WHERE id=?",('A'*121,OSI))
run('long_exact_label','A'*121,g,'Drug label changed to 121 ASCII A characters')
g=clone(); g.companies=copy.deepcopy(kg.companies); g.companies['azalias']=['ORG:astrazeneca','ORG:genentech']
c=dict(kind='relation',relation='SPONSORS_TRIAL_OF',subject='azalias',object='osimertinib',evidence='ORG:astrazeneca|SPONSORS_TRIAL_OF|CHEMBL3353410|',trial_count=14)
old_ev=evidence; evidence=ev(kg,'What is AstraZeneca running in NSCLC?')
run('ambiguous_nonexact_alias','azalias',g,"companies['azalias'] maps to AstraZeneca and Genentech",want='Company',claim=c)
evidence=old_ev
evidence=ev(kg,'What does metformin target?')
me=next(e for e in evidence if e.relation=='ACTS_ON')
edge=kg.conn.execute('SELECT * FROM edge WHERE id=?',(me.edge_id,)).fetchone()
for name in ['met','METFORMIN','CHEMBL1431']:
    c=dict(kind='relation',relation='ACTS_ON',subject=name,object=edge['dst'],evidence=edge['id'])
    run('live_alias_shadowed_by_target_label:'+name,name,claim=c)
evidence=old_ev
(OUT/'identity_attack_results.json').write_text(json.dumps(out,ensure_ascii=True,indent=2),encoding='utf-8')
print(json.dumps({'persisted':out['persisted'],'cases':[{k:r[k] for k in ['tag','resolved_ids','reason']}|{'verified':r['output']['verified']} for r in out['cases']+out['fixtures']]},ensure_ascii=True,indent=2))
