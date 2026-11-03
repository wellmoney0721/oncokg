import json, sqlite3, sys, time, collections
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'src'))
from app import Engine
c=sqlite3.connect(f'file:{(ROOT/"data/processed/oncokg.sqlite").as_posix()}?mode=ro',uri=True)
c.row_factory=sqlite3.Row
e=Engine(); e.kg.conn.close(); e.kg.conn=c
nodes={r['id']:dict(r) for r in c.execute('SELECT * FROM node')}
edges={r['id']:dict(r) for r in c.execute('SELECT * FROM edge')}
live={i:n for i,n in nodes.items() if n['retired_at'] is None}
adj=collections.defaultdict(list)
trial_counts=collections.Counter()
for ed in edges.values():
    if ed['retired_at'] is not None: continue
    if ed['rel']=='EVALUATES': trial_counts[ed['dst']]+=1
    if ed['dst'] in live: adj[ed['src']].append(ed)
    if ed['src'] in live and ed['src']!=ed['dst']: adj[ed['dst']].append(ed)
out={'checks':0,'errors':[],'relation_samples':{},'special':{}}
started=time.perf_counter()
for index,(nid,n) in enumerate(live.items()):
    r=e.explore(nid,per_group=100000)
    out['checks']+=1
    if r.get('center',{}).get('id')!=nid: out['errors'].append([nid,'center']); continue
    expected=collections.Counter()
    for ed in adj[nid]:
        direction='out' if ed['src']==nid else 'in'
        other=ed['dst'] if direction=='out' else ed['src']
        expected[(ed['rel'],direction,nodes[other]['type'])]+=1
    actual={(g['rel'],g['dir'],g['type']):g['total'] for g in r['groups']}
    if actual!=expected: out['errors'].append([nid,'group_counts',str(actual),str(expected)])
    if [g['total'] for g in r['groups']]!=sorted([g['total'] for g in r['groups']],reverse=True): out['errors'].append([nid,'group_sort'])
    for g in r['groups']:
        sample_key='|'.join((n['type'],g['rel'],g['dir'],g['type']))
        if sample_key not in out['relation_samples']: out['relation_samples'][sample_key]={'input':nid,'center':r['center'],'group':g}
        for it in g['items']:
            ed=edges[it['edge_id']]; nn=nodes[it['id']]; np=json.loads(nn['props']); ep=json.loads(ed['props'])
            if ed['retired_at'] is not None or nn['retired_at'] is not None: out['errors'].append([nid,'retired',it])
            if nn['label']!=it['label']: out['errors'].append([nid,'label',it])
            if ed['rel']=='SPONSORS_TRIAL_OF':
                if it['weight']!=(ep.get('evidence_trials') or 0) or it['sponsor_class']!=ep.get('sponsor_class'): out['errors'].append([nid,'sponsor',it])
            elif nn['type']=='Trial':
                for k in ('phases','status','title','start_date','url'):
                    if it.get(k)!=np.get(k): out['errors'].append([nid,k,it])
            elif nn['type']=='Drug':
                if it['weight']!=trial_counts[it['id']] or it['max_phase']!=np.get('max_phase_overall'): out['errors'].append([nid,'drug',it])
            if ed['rel']=='ACTS_ON' and it['action']!=ep.get('action_type'): out['errors'].append([nid,'action',it])
        if g['items']!=sorted(g['items'],key=lambda x:(x['weight'],x['label'] or ''),reverse=True): out['errors'].append([nid,'item_sort'])
    if n['type']=='Drug' and r['center']['trials'] != (trial_counts[nid] or None): out['errors'].append([nid,'center_trials',r['center']['trials'],trial_counts[nid]])
    if index%1000==0: print('checked',index,flush=True)
out['seconds']=time.perf_counter()-started
out['special']['investigator_trial']=next(v for k,v in out['relation_samples'].items() if k=='Trial|SPONSORS|in|Investigator')
(ROOT/'audit_evidence_claims/m1/db_validate.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'checks':out['checks'],'errors':out['errors'],'seconds':out['seconds'],'relation_sample_keys':list(out['relation_samples']),'investigator_trial':out['special']['investigator_trial']},ensure_ascii=False,indent=2))
