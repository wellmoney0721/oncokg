import os,sys,json,copy,sqlite3
from pathlib import Path
os.environ['PYTHONDONTWRITEBYTECODE']='1'
ROOT=Path(__file__).resolve().parent.parent; OUT=ROOT/'audit_evidence_round3'
sys.path.insert(0,str(ROOT/'src'))
import graph as G,normalize as N
r=json.loads((OUT/'graph_resolved.json').read_text(encoding='utf8'))
mini=copy.deepcopy(r); mini['targets']=[]
mini['trials']=[t for t in r['trials'] if t.get('lead_sponsor') and any(c['tier'] in N.ACCEPTED_TIERS and c.get('drug_id') for iv in t['interventions'] for c in iv['components'])][:2]
removed_nct=mini['trials'][1]['nct_id']
ids={c['drug_id'] for t in mini['trials'] for iv in t['interventions'] for c in iv['components'] if c.get('drug_id')}
mini['dictionary']['drugs']={k:v for k,v in mini['dictionary']['drugs'].items() if k in ids}
p=OUT/'graph_collision_removal.sqlite'
if p.exists():p.unlink()
G.now=lambda:'2026-11-03T06:00:00+00:00'
a=G.build(mini,db_path=p)
mini['trials']=mini['trials'][:1]
b=G.build(mini,db_path=p)
c=sqlite3.connect(p);c.row_factory=sqlite3.Row
result={'method':'Freeze graph.now to one timestamp; default build_id both times; two trials then one.','removed_nct':removed_nct,'first':a,'second':b,
 'removed_trial_node':dict(c.execute('SELECT * FROM node WHERE id=?',(removed_nct,)).fetchone()),
 'removed_trial_edges':[dict(x) for x in c.execute('SELECT * FROM edge WHERE src=? OR dst=?',(removed_nct,removed_nct))],
 'live_removed_trial_edges':c.execute('SELECT count(*) FROM edge WHERE retired_at IS NULL AND (src=? OR dst=?)',(removed_nct,removed_nct)).fetchone()[0],
 'build_rows':[dict(x) for x in c.execute('SELECT * FROM build')],
 'changes_by_build_and_type':[dict(x) for x in c.execute('SELECT build_id,change_type,count(*) n FROM edge_change GROUP BY build_id,change_type')]}
(OUT/'graph_collision_removal.json').write_text(json.dumps(result,indent=2),encoding='utf8')
print(json.dumps({k:v for k,v in result.items() if k in ['removed_nct','first','second','live_removed_trial_edges','changes_by_build_and_type']}))
