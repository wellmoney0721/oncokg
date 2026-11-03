"""Independent identity/value probes; no writes except sibling output JSON."""
import collections
import copy
import json
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'src'))
from query import OncoKG
from structured import Verifier, _norm

kg = OncoKG()
kg.conn.execute('PRAGMA query_only=ON')
out = {'cases': [], 'dictionary': {}, 'synthetic_cases': []}
OSI = 'CHEMBL3353410|ACTS_ON|ENSG00000146648|CHEMBL3353410'
T1 = 'NCT03909334|EVALUATES|CHEMBL3353410|NCT03909334'
AZ = 'ORG:astrazeneca|SPONSORS_TRIAL_OF|CHEMBL3353410|'
Q3 = 'What does osimertinib target?'
Q2 = 'What trials evaluate Tagrisso?'
Q5 = 'What is AstraZeneca running in NSCLC?'

def evidence(q, graph=kg):
    ents = graph.link_entities(q)
    return graph.retrieve(graph.classify(q, ents), ents)

def probe(tag, q, payload, graph=kg, synthetic=False, ev=None):
    row = {'tag': tag, 'question': q, 'input': payload}
    evid = evidence(q, graph) if ev is None else ev
    row['retrieved_ids'] = [e.edge_id for e in evid]
    try:
        row['output'] = graph.verify_structured(payload, evid)
    except Exception as ex:
        row['exception'] = {'type': type(ex).__name__, 'message': str(ex)}
    out['synthetic_cases' if synthetic else 'cases'].append(row)
    return row

base = dict(kind='relation', relation='ACTS_ON', subject='osimertinib', object='EGFR', evidence=OSI, action='INHIBITOR')
def one(c): return {'claims': [c]}

for name in ['osimertinib', 'Tagrisso', 'CHEMBL3353410', '  OSIMERTINIB  ', 'OSIMERTINIB\u200b',
             'osimertinib\u764c', 'osimertinib\U0001f489', 'osimertinib\uac00 \uc544\ub2cc', '\u975eosimertinib', 'osimertinib\u662f\u5b89\u5168\u7684',
             'osimertinib mesylate', 'osimertinib mesilate',
             'CHEMBL3545063', 'osimertinib hydrochloride', 'osimertinib is safe', 'osimertinib EGFR',
             'osimertinib NSCLC', 'osimertinib' + ' '*121, 'MEDI4736', 'heparin', 'calcium folinate']:
    probe('name:' + repr(name), Q3, one({**base, 'subject': name}))

for action in ['INHIBITOR', 'in-hib/it_or', 'ANTISENSE INHIBITOR', 'ACTIVATOR', '', '---', None, True, 1, 1.0, [], ['INHIBITOR'], {}, float('nan'), float('inf')]:
    probe('action:' + repr(action), Q3, one({**base, 'action': action}))

for field in ['kind', 'relation', 'subject', 'object', 'evidence']:
    for value in [None, True, 1, 1.0, [], {}, ['ACTS_ON'], float('nan'), float('inf')]:
        probe('type:' + field + ':' + repr(value), Q3, one({**base, field: value}))

for field in ['phase', 'status']:
    for value in [None, True, 2, 2.0, [], ['PHASE2', 2], ['PHASE2'], 'PHASE2', {}, float('nan'), float('inf')]:
        probe('trial_type:' + field + ':' + repr(value), Q2, one(dict(kind='trial', trial='NCT03909334', evidence=T1, **{field: value})))

for value in [14, True, 14.0, '14', None, [], {}, -1, float('nan'), float('inf')]:
    probe('count:' + repr(value), Q5, one(dict(kind='relation', relation='SPONSORS_TRIAL_OF', subject='AstraZeneca', object='osimertinib', evidence=AZ, trial_count=value)))

probe('wrong_question_edge', Q2, one(base))
probe('relation_mismatch', Q3, one({**base, 'relation':'EVALUATES'}))
probe('unknown_key', Q3, one({**base, 'text':'<img src=x onerror=alert(1)>'}))
probe('profile', 'What is osimertinib?', one(dict(kind='drug', drug='osimertinib', evidence='profile:CHEMBL3353410', max_stage='APPROVAL', trials_in_graph=79)))
probe('profile_as_relation', 'What is osimertinib?', one({**base,'evidence':'profile:CHEMBL3353410'}))
probe('profile_wrong_question', Q3, one(dict(kind='drug', drug='osimertinib', evidence='profile:CHEMBL3353410', max_stage='APPROVAL')))
probe('51_claims', Q3, {'claims':[base]*51})
probe('duplicate_claim_keys_last_supported', Q3, '{"claims":[{"kind":"relation","relation":"ACTS_ON","subject":"osimertinib","object":"EGFR","evidence":"'+OSI+'","action":"ACTIVATOR","action":"INHIBITOR"}]}')
probe('duplicate_claim_keys_last_unsupported', Q3, '{"claims":[{"kind":"relation","relation":"ACTS_ON","subject":"osimertinib","object":"EGFR","evidence":"'+OSI+'","action":"INHIBITOR","action":"ACTIVATOR"}]}')
probe('large_scalar', Q3, one({**base,'action':'X'*20000}))
probe('deep_json', Q3, '{"claims":'+'['*1100+'null'+']'*1100+'}')
probe('very_deep_json', Q3, '{"claims":'+'['*5000+'null'+']'*5000+'}')
probe('oversized_integer', Q3, '{"claims":['+'9'*5000+']}')
probe('alk_salt_canonical_name', 'Which drugs act on ALK?', one(dict(kind='relation', relation='ACTS_ON', subject='ALECTINIB HYDROCHLORIDE', object='ALK', evidence='CHEMBL3707320|ACTS_ON|ENSG00000171094|CHEMBL3707320',action='INHIBITOR')))
probe('alk_salt_id', 'Which drugs act on ALK?', one(dict(kind='relation', relation='ACTS_ON', subject='CHEMBL3707320', object='ALK', evidence='CHEMBL3707320|ACTS_ON|ENSG00000171094|CHEMBL3707320',action='INHIBITOR')))
for row in out['cases']:
    if row['tag'].startswith('name:'):
        name=row['input']['claims'][0]['subject']
        row['linker_output']=kg.link_entities(name)

v=Verifier(kg)
for table,prop in [('edge','action_type'),('node','phases'),('node','status'),('node','max_phase_overall')]:
    vals=collections.Counter()
    for row in kg.conn.execute('SELECT props FROM '+table):
        x=json.loads(row['props'] or '{}').get(prop)
        if isinstance(x,list): vals.update(x)
        elif x is not None: vals[x]+=1
    groups=collections.defaultdict(list)
    for x in vals: groups[_norm(x)].append(x)
    out['dictionary'][prop]={'stored_values':dict(vals),'collisions':{n:xs for n,xs in groups.items() if len(xs)>1}}
out['dictionary']['multi_company']={n:ids for n,ids in kg.companies.items() if len(ids)>1}
out['dictionary']['ambiguous_drugs']={n:xs for n,xs in kg.dic['index'].items() if len({x['drug_id'] for x in xs})>1}
out['dictionary']['retired_nodes']=[dict(r) for r in kg.conn.execute('SELECT id,type,label FROM node WHERE retired_at IS NOT NULL')]
out['dictionary']['invalid_live_edge_endpoints']=[dict(r) for r in kg.conn.execute('SELECT e.id,e.rel FROM edge e LEFT JOIN node s ON s.id=e.src LEFT JOIN node d ON d.id=e.dst WHERE e.retired_at IS NULL AND (s.retired_at IS NOT NULL OR d.retired_at IS NOT NULL OR s.id IS NULL OR d.id IS NULL)')]

# Verify every currently retired edge is rejected even if it appears in an old allowlist.
out['dictionary']['retired_edge_checks']=[]
for e in kg.conn.execute('SELECT * FROM edge WHERE retired_at IS NOT NULL'):
    c=dict(kind='relation',relation=e['rel'],subject=e['src'],object=e['dst'],evidence=e['id'])
    result=v.check(c,{e['id']})
    out['dictionary']['retired_edge_checks'].append({'claim':c,'output':result})

# Explicitly labelled synthetic regression: isolated in-memory copy, never live DB.
synth=copy.copy(kg)
synth.conn=sqlite3.connect(':memory:'); synth.conn.row_factory=sqlite3.Row
kg.conn.backup(synth.conn)
synth.companies=copy.deepcopy(kg.companies)
synth.companies['astrazeneca'].append('ORG:genentech')
q='What is AstraZeneca running in NSCLC?'
ev=evidence(q,synth)
azclaim=dict(kind='relation',relation='SPONSORS_TRIAL_OF',subject='AstraZeneca',object='osimertinib',evidence=AZ,trial_count=14)
r=probe('multi_id_company_resolution_fixture',q,one(azclaim),synth,True,ev)
r['fixture_change']="companies['astrazeneca'] includes both ORG:astrazeneca and ORG:genentech"
r['resolved_subject']=sorted(Verifier(synth).resolve('AstraZeneca','Company')[0])

synth=copy.copy(kg)
synth.conn=sqlite3.connect(':memory:'); synth.conn.row_factory=sqlite3.Row
kg.conn.backup(synth.conn)
synth.conn.execute("UPDATE node SET retired_at='test-retired' WHERE id='CHEMBL3353410'")
q='What is osimertinib?'
r=probe('retired_drug_profile_fixture',q,one(dict(kind='drug',drug='osimertinib',evidence='profile:CHEMBL3353410',max_stage='APPROVAL')),synth,True)
r['fixture_change']="node CHEMBL3353410 retired_at set to test-retired in isolated in-memory DB"

path=Path(__file__).with_name('identity_probe_results.json')
path.write_text(json.dumps(out,indent=2,ensure_ascii=True,allow_nan=True),encoding='utf-8')
print(json.dumps({'cases':len(out['cases']),'exceptions':[{k:r[k] for k in ('tag','exception')} for r in out['cases'] if 'exception' in r], 'retired_edges_checked':len(out['dictionary']['retired_edge_checks']),'synthetic':[{k:r[k] for k in ('tag','output')} for r in out['synthetic_cases']],'results':str(path)},indent=2))
