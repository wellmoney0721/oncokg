"""HTTP score-type fixture; only in-memory mutation and sibling outputs."""
import json,sqlite3,sys,types,threading,urllib.request,subprocess
from pathlib import Path
from http.server import ThreadingHTTPServer
ROOT=Path(__file__).resolve().parents[2]
OUT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'src'))
import app
base=types.ModuleType('base_app')
base.__file__=str(ROOT/'src/app.py')
exec(compile(subprocess.check_output(['git','show','bfcb83d:src/app.py']),base.__file__,'exec'),base.__dict__)
def run(module,score):
    c=sqlite3.connect(':memory:',check_same_thread=False);c.row_factory=sqlite3.Row
    c.executescript('CREATE TABLE node(id TEXT PRIMARY KEY,type TEXT,label TEXT,props TEXT,retired_at TEXT); CREATE TABLE edge(id TEXT PRIMARY KEY,src TEXT,dst TEXT,rel TEXT,props TEXT,retired_at TEXT);')
    c.executemany('INSERT INTO node VALUES(?,?,?,?,?)',[('X','Target','Fixture target','{}',None),('Y','Disease','Fixture disease','{}',None)])
    c.execute('INSERT INTO edge VALUES(?,?,?,?,?,?)',('A','X','Y','ASSOCIATED_WITH',json.dumps({'association_score':score}),None))
    e=module.Engine.__new__(module.Engine);e.kg=types.SimpleNamespace(conn=c,link_entities=lambda t:[]);e.lock=threading.Lock()
    srv=ThreadingHTTPServer(('127.0.0.1',0),module.make_handler(e));th=threading.Thread(target=srv.serve_forever,daemon=True);th.start()
    out=[]
    try:
        for text in ['X','Y']:
            req=urllib.request.Request(f'http://127.0.0.1:{srv.server_port}/api/explore',json.dumps({'text':text}).encode(),{'Content-Type':'application/json'})
            with urllib.request.urlopen(req,timeout=10) as r:out.append({'text':text,'status':r.status,'body':json.load(r)})
    finally:srv.shutdown();srv.server_close();th.join(3);c.close()
    return out
out={'setup':'isolated in-memory X:Target -> ASSOCIATED_WITH -> Y:Disease, no disk DB mutations','cases':[{'score':s,'baseline':run(base,s),'HEAD':run(app,s)} for s in [True,False,0.8883707400322897]]}
c=sqlite3.connect('file:data/processed/oncokg.sqlite?mode=ro',uri=True)
out['current_score_json_types']=c.execute("select json_type(props,'$.association_score'),count(*) from edge where rel='ASSOCIATED_WITH' and retired_at is null group by 1").fetchall()
c.close()
(OUT/'db_score_fixture.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'cases':[{'score':x['score'],'HEAD_score':[r['body']['groups'][0]['items'][0].get('score') for r in x['HEAD']]} for x in out['cases']],'current_score_json_types':out['current_score_json_types']}))
