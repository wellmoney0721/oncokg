"""Fresh explicit self-loop and unknown-type fixtures; in-memory only."""
import json,sqlite3,sys,types,threading,urllib.request
from pathlib import Path
from http.server import ThreadingHTTPServer
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
sys.path.insert(0,str(ROOT/'src'))
from app import Engine,make_handler
conn=sqlite3.connect(':memory:',check_same_thread=False)
conn.row_factory=sqlite3.Row
conn.executescript("CREATE TABLE node(id TEXT PRIMARY KEY,type TEXT,label TEXT,props TEXT,retired_at TEXT); CREATE TABLE edge(id TEXT PRIMARY KEY,src TEXT,dst TEXT,rel TEXT,props TEXT,retired_at TEXT);")
conn.executemany('INSERT INTO node VALUES(?,?,?,?,?)',[
 ('X','Company','Self company','{}',None),('U','Other','Unknown type','{}',None),('R','Other','Retired','{}','AUDIT')])
conn.executemany('INSERT INTO edge VALUES(?,?,?,?,?,?)',[
 ('SELF','X','X','PARENT_OF','{}',None),('UNKNOWN','X','U','NEWREL','{}',None),
 ('RETIRED_EDGE','X','U','NEWREL','{}','AUDIT'),('RETIRED_NODE','X','R','NEWREL','{}',None)])
e=Engine.__new__(Engine);e.kg=types.SimpleNamespace(conn=conn,link_entities=lambda t:[]);e.lock=threading.Lock()
srv=ThreadingHTTPServer(('127.0.0.1',0),make_handler(e));th=threading.Thread(target=srv.serve_forever,daemon=True);th.start()
rows=[]
try:
 for name in ['X','U']:
  req=urllib.request.Request(f'http://127.0.0.1:{srv.server_port}/api/explore',json.dumps({'text':name}).encode(),{'Content-Type':'application/json'})
  with urllib.request.urlopen(req,timeout=10) as r:rows.append({'input':name,'status':r.status,'body':json.load(r)})
 checks={
  'self_edge_once_out':[(g['rel'],g['dir'],i['id'],i['edge_id']) for g in rows[0]['body']['groups'] for i in g['items'] if i['edge_id']=='SELF']==[('PARENT_OF','out','X','SELF')],
  'unknown_type_and_relation_preserved':any(g['rel']=='NEWREL' and g['type']=='Other' and g['dir']=='out' for g in rows[0]['body']['groups']),
  'retired_edges_and_nodes_absent':all(not i['edge_id'].startswith('RETIRED') for r in rows for g in r['body']['groups'] for i in g['items']),
  'unknown_reverse_preserved':rows[1]['body']['groups'][0]['rel']=='NEWREL' and rows[1]['body']['groups'][0]['dir']=='in',
 }
 assert all(checks.values()),checks
 result={'setup':'new isolated in-memory fixture, real HTTP handler','checks':checks,'rows':rows}
 (OUT/'self_loop_unknown.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
 print(json.dumps(checks))
finally:
 srv.shutdown();srv.server_close();th.join(timeout=3);conn.close()
