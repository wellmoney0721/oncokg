import json, sqlite3, sys, types, urllib.request
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'src'))
from app import Engine
c=sqlite3.connect(f'file:{(ROOT/"data/processed/oncokg.sqlite").as_posix()}?mode=ro',uri=True); c.row_factory=sqlite3.Row
out={}
out['roles']=[dict(r) for r in c.execute("SELECT json_extract(props,'$.role') role,count(*) n FROM edge WHERE rel='SPONSORS' AND retired_at IS NULL GROUP BY role")]
out['collaborator_sample']=[dict(r) for r in c.execute("SELECT e.*,n.label,n.type FROM edge e JOIN node n ON n.id=e.src WHERE rel='SPONSORS' AND e.retired_at IS NULL AND n.retired_at IS NULL AND json_extract(e.props,'$.role')='collaborator' LIMIT 5")]
out['investigator_sample']=[dict(r) for r in c.execute("SELECT e.*,n.label,n.type FROM edge e JOIN node n ON n.id=e.src WHERE rel='SPONSORS' AND e.retired_at IS NULL AND n.type='Investigator' LIMIT 5")]
e=Engine();e.kg.conn.close();e.kg.conn=c
for label,samples in [('collaborator',out['collaborator_sample']),('investigator',out['investigator_sample'])]:
    if samples:
        nct=samples[0]['dst'];out[label+'_explore']=e.explore(nct)
        try:
            req=urllib.request.Request('http://127.0.0.1:8876/api/explore',json.dumps({'text':nct}).encode(),{'Content-Type':'application/json'})
            with urllib.request.urlopen(req,timeout=10) as resp: out[label+'_http']={'status':resp.status,'response':json.load(resp)}
        except Exception as exc: out[label+'_http_error']=str(exc)

fc=sqlite3.connect(':memory:');fc.row_factory=sqlite3.Row
fc.executescript('CREATE TABLE node(id TEXT PRIMARY KEY,type TEXT,label TEXT,props TEXT,retired_at TEXT); CREATE TABLE edge(id TEXT PRIMARY KEY,src TEXT,dst TEXT,rel TEXT,props TEXT,retired_at TEXT);')
f=Engine.__new__(Engine);f.kg=types.SimpleNamespace(conn=fc,link_entities=lambda text:[])
fc.executemany('INSERT INTO node VALUES(?,?,?,?,?)',[('D','Drug','Fixture drug','{}',None),('T','Trial','Retired trial','{}','2026-01-01'),('X','Target','Fixture target','{}',None)])
fc.executemany('INSERT INTO edge VALUES(?,?,?,?,?,?)',[('E','T','D','EVALUATES','{}',None),('A','D','X','ACTS_ON','{}',None)])
out['retired_trial_fixture']={'input_rows':[dict(r) for r in fc.execute('SELECT * FROM node')],'edges':[dict(r) for r in fc.execute('SELECT * FROM edge')],'drug':f.explore('D'),'target':f.explore('X')}
fc.execute('DELETE FROM edge');fc.execute('DELETE FROM node')
fc.execute('INSERT INTO node VALUES(?,?,?,?,?)',('X','Target','Fixture target','{}',None))
for i in range(1001):
    fc.execute('INSERT INTO node VALUES(?,?,?,?,?)',(f'D{i}','Drug',f'Drug {i}','{"max_phase_overall":"PHASE2"}',None))
    fc.execute('INSERT INTO node VALUES(?,?,?,?,?)',(f'T{i}','Trial',f'Trial {i}','{}',None))
    fc.execute('INSERT INTO edge VALUES(?,?,?,?,?,?)',(f'A{i}',f'D{i}','X','ACTS_ON','{}',None))
    fc.execute('INSERT INTO edge VALUES(?,?,?,?,?,?)',(f'E{i}',f'T{i}',f'D{i}','EVALUATES','{}',None))
r=f.explore('X',2000)
out['chunking_fixture']={'drug_count':1001,'group_total':r['groups'][0]['total'],'items':len(r['groups'][0]['items']),'weights':dict(__import__('collections').Counter(it['weight'] for it in r['groups'][0]['items']))}
out['bad_props_fixture']={}
for value in ['null','[]','{broken']:
    fc.execute('UPDATE node SET props=? WHERE id=?',(value,'D0'))
    try: out['bad_props_fixture'][value]={'response':f.explore('X')}
    except Exception as exc: out['bad_props_fixture'][value]={'error_type':type(exc).__name__,'message':str(exc)}
    fc.execute('UPDATE node SET props=? WHERE id=?',('{}','D0'))
(ROOT/'audit_evidence_claims/m1/db_fixture.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(out,ensure_ascii=False,indent=2))
