import json, sqlite3, sys, types, threading, urllib.request, urllib.error
from http.server import ThreadingHTTPServer
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'src'))
from app import Engine, make_handler
c=sqlite3.connect(':memory:',check_same_thread=False);c.row_factory=sqlite3.Row
c.executescript('CREATE TABLE node(id TEXT PRIMARY KEY,type TEXT,label TEXT,props TEXT,retired_at TEXT); CREATE TABLE edge(id TEXT PRIMARY KEY,src TEXT,dst TEXT,rel TEXT,props TEXT,retired_at TEXT);')
c.executemany('INSERT INTO node VALUES(?,?,?,?,?)',[('D','Drug','Fixture drug','{}',None),('T','Trial','Retired trial','{}','2026-01-01'),('X','Target','Fixture target','{}',None)])
c.executemany('INSERT INTO edge VALUES(?,?,?,?,?,?)',[('E','T','D','EVALUATES','{}',None),('A','D','X','ACTS_ON','{}',None)])
e=Engine.__new__(Engine);e.kg=types.SimpleNamespace(conn=c,link_entities=lambda text:[]);e.lock=threading.Lock()
server=ThreadingHTTPServer(('127.0.0.1',0),make_handler(e));thread=threading.Thread(target=server.serve_forever,daemon=True);thread.start()
def post(text):
    request=urllib.request.Request(f'http://127.0.0.1:{server.server_port}/api/explore',json.dumps({'text':text}).encode(),{'Content-Type':'application/json'})
    try:
        with urllib.request.urlopen(request,timeout=10) as r:return {'status':r.status,'body':json.load(r)}
    except urllib.error.HTTPError as exc:return {'status':exc.code,'body':json.load(exc)}
out={'port':server.server_port,'retired_trial':{'input':'D','response':post('D')},'malformed':[]}
for table,identifier in [('node','D'),('edge','A')]:
    for value in ['null','[]','{broken']:
        with e.lock:c.execute(f'UPDATE {table} SET props=? WHERE id=?',(value,identifier))
        result={'table':table,'id':identifier,'props':value,'input':'X','response':post('X')}
        with e.lock:c.execute(f'UPDATE {table} SET props=? WHERE id=?',('{}',identifier))
        result['after_restore']=post('X')
        out['malformed'].append(result)
server.shutdown();server.server_close();c.close()
prod=sqlite3.connect(f'file:{(ROOT/"data/processed/oncokg.sqlite").as_posix()}?mode=ro',uri=True);prod.row_factory=sqlite3.Row
out['current_live_edge_retired_endpoint']=[dict(r) for r in prod.execute('SELECT e.rel,count(*) n FROM edge e JOIN node s ON s.id=e.src JOIN node d ON d.id=e.dst WHERE e.retired_at IS NULL AND (s.retired_at IS NOT NULL OR d.retired_at IS NOT NULL) GROUP BY e.rel')]
out['current_evaluates_counts']=[dict(r) for r in prod.execute("SELECT count(*) n,sum(e.retired_at IS NOT NULL) retired_edges,sum(e.retired_at IS NULL AND (s.retired_at IS NOT NULL OR d.retired_at IS NOT NULL)) live_edges_with_retired_endpoint FROM edge e JOIN node s ON s.id=e.src JOIN node d ON d.id=e.dst WHERE rel='EVALUATES'")]
out['live_sponsor_classes']=[dict(r) for r in prod.execute("SELECT json_extract(props,'$.sponsor_class') sponsor_class,count(*) n FROM edge WHERE rel='SPONSORS_TRIAL_OF' AND retired_at IS NULL GROUP BY sponsor_class")]
(ROOT/'audit_evidence_claims/m1/db_http_fixtures.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(out,ensure_ascii=False,indent=2))
