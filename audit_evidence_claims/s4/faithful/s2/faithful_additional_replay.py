import copy, json, sqlite3, sys
from pathlib import Path
ROOT = Path.cwd(); OUT=Path("C:\\Users\\geoum\\Dropbox\\GY's Formal Workspace\\2026 Job recruting\\바이오리서치에이아이\\oncokg\\audit_evidence_claims\\s4\\faithful\\s2")
sys.path.insert(0, str(ROOT/'src'))
import query as Q
from structured import Verifier, _norm
kg = Q.OncoKG(); kg.conn.execute('PRAGMA query_only=ON')
def evidence(q):
    ents=kg.link_entities(q)
    return kg.retrieve(kg.classify(q,ents),ents)
old = json.loads((ROOT/'audit_evidence_claims'/'s1'/'faithful_additional.json').read_text(encoding='utf-8'))
res = {'action_cases': []}
for case in old['action_cases']:
    res['action_cases'].append({'question':case['question'],'input':case['input'], 'output':kg.verify_structured(case['input'],evidence(case['question']))})
case=old['profile']
res['profile']={'question':case['question'],'input':case['input'],'output':kg.verify_structured(case['input'],evidence(case['question'])), 'live_edge_count':kg.conn.execute("SELECT COUNT(*) FROM edge WHERE id='profile:CHEMBL3353410' AND retired_at IS NULL").fetchone()[0]}
fixture=json.loads((ROOT/'audit_evidence_claims'/'s1'/'faithful_empty_phase_fixture.json').read_text(encoding='utf-8'))
clone=copy.copy(kg); clone.conn=sqlite3.connect(':memory:'); clone.conn.row_factory=sqlite3.Row
kg.conn.backup(clone.conn)
props=json.loads(clone.conn.execute("SELECT props FROM node WHERE id='NCT03909334'").fetchone()[0]); props['phases']=[]
clone.conn.execute("UPDATE node SET props=? WHERE id='NCT03909334'", (json.dumps(props),))
res['empty_phase_fixture']={'fixture':fixture['fixture'],'input':fixture['input'],'output':clone.verify_structured(fixture['input'],evidence('What trials evaluate Tagrisso?'))}
res['long_live_labels']=[dict(r) for r in kg.conn.execute('SELECT id,type,label,length(label) n FROM node WHERE retired_at IS NULL AND length(label)>120')]
res['duplicate_trial_pairs']=[dict(r) for r in kg.conn.execute("SELECT src,dst,COUNT(*) n FROM edge WHERE rel='EVALUATES' AND retired_at IS NULL GROUP BY src,dst HAVING COUNT(*)>1")]
res['norm_collisions']={}
for table, typ, key in [('edge','ACTS_ON','action_type'),('node','Trial','status'),('node','Trial','phases'),('node','Drug','max_phase_overall')]:
    col='rel' if table=='edge' else 'type'
    groups={}
    for row in kg.conn.execute(f'SELECT props FROM {table} WHERE {col}=? AND retired_at IS NULL',(typ,)):
        value=json.loads(row['props']).get(key)
        values=value if isinstance(value,list) else [value]
        for value in values:
            if isinstance(value,str):groups.setdefault(_norm(value),set()).add(value)
    res['norm_collisions'][key]={k:sorted(v) for k,v in groups.items() if len(v)>1}
(OUT/'faithful_additional_replay.json').write_text(json.dumps(res,indent=2,ensure_ascii=True),encoding='utf-8')
print(json.dumps({'action_cases': [{'object':x['input']['claims'][0]['object'],'action':x['input']['claims'][0]['action'],'output':x['output']} for x in res['action_cases']], 'profile_verified':res['profile']['output']['verified'],'empty_phase':res['empty_phase_fixture']['output'],'long_label_count':len(res['long_live_labels']),'norm_collisions':res['norm_collisions'],'duplicate_trial_pairs':res['duplicate_trial_pairs']},ensure_ascii=True,indent=2))
