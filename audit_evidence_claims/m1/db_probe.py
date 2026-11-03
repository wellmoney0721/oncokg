import json, sqlite3, sys, time
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'src'))
from app import Engine

c = sqlite3.connect(f'file:{(ROOT / "data/processed/oncokg.sqlite").as_posix()}?mode=ro', uri=True)
c.row_factory = sqlite3.Row
def rows(sql, args=()): return [dict(r) for r in c.execute(sql,args)]
out = {}
out['schema'] = rows("SELECT sql FROM sqlite_master WHERE type='table'")
out['node_types'] = rows('SELECT type,count(*) n,sum(retired_at IS NOT NULL) retired FROM node GROUP BY type')
out['relation_types'] = rows('SELECT e.rel,s.type src_type,d.type dst_type,count(*) n,sum(e.retired_at IS NOT NULL) retired FROM edge e JOIN node s ON s.id=e.src JOIN node d ON d.id=e.dst GROUP BY e.rel,s.type,d.type')
out['self_loops'] = rows('SELECT * FROM edge WHERE src=dst')
out['retired'] = rows("SELECT 'node' kind,count(*) n FROM node WHERE retired_at IS NOT NULL UNION SELECT 'edge',count(*) FROM edge WHERE retired_at IS NOT NULL")
out['props_null'] = rows("SELECT 'node' kind,count(*) n FROM node WHERE props IS NULL OR props='null' UNION SELECT 'edge',count(*) FROM edge WHERE props IS NULL OR props='null'")
out['props_invalid'] = rows("SELECT 'node' kind,count(*) n FROM node WHERE NOT json_valid(props) UNION SELECT 'edge',count(*) FROM edge WHERE NOT json_valid(props)")
out['sponsor_classes'] = rows("SELECT json_extract(props,'$.sponsor_class') sponsor_class,count(*) n FROM edge WHERE rel='SPONSORS_TRIAL_OF' GROUP BY sponsor_class")
out['action_types'] = rows("SELECT json_extract(props,'$.action_type') action,count(*) n FROM edge WHERE rel='ACTS_ON' GROUP BY action")
out['disease_nodes'] = rows("SELECT * FROM node WHERE type='Disease'")
e=Engine()
e.kg.conn.close()
e.kg.conn=c
out['explores']={}
for name in ['osimertinib','EGFR','AstraZeneca'] + [x['id'] for x in out['disease_nodes']]:
    t=time.perf_counter(); r=e.explore(name); elapsed=time.perf_counter()-t
    out['explores'][name]={'seconds':elapsed,'json_bytes':len(json.dumps(r,ensure_ascii=False).encode()),'response':r}
(ROOT/'audit_evidence_claims/m1/db_probe.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in out.items() if k!='explores'},ensure_ascii=False,indent=2))
print(json.dumps({n:{'seconds':v['seconds'],'json_bytes':v['json_bytes'],'groups':[{k:g[k] for k in ['rel','dir','type','total']} for g in v['response'].get('groups',[])]} for n,v in out['explores'].items()},ensure_ascii=False,indent=2))
for i,s in enumerate((ROOT/'web/try.html').read_text(encoding='utf-8').splitlines(),1):
    if 130<=i<=157: print(f'{i}: {s}')
