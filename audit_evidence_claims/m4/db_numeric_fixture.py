"""Numeric edge-property controls; memory database only."""
import json,sqlite3,sys,types,threading,urllib.request,urllib.error
from pathlib import Path
from http.server import ThreadingHTTPServer
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'src'))
import app
c=sqlite3.connect(':memory:',check_same_thread=False);c.row_factory=sqlite3.Row
c.executescript('CREATE TABLE node(id TEXT PRIMARY KEY,type TEXT,label TEXT,props TEXT,retired_at TEXT); CREATE TABLE edge(id TEXT PRIMARY KEY,src TEXT,dst TEXT,rel TEXT,props TEXT,retired_at TEXT);')
c.executemany('INSERT INTO node VALUES(?,?,?,?,?)',[('X','Target','Fixture target','{}',None),('Y','Disease','Fixture disease','{}',None),('O','Company','Fixture company','{}',None),('D','Drug','Fixture drug','{}',None)])
c.executemany('INSERT INTO edge VALUES(?,?,?,?,?,?)',[('A','X','Y','ASSOCIATED_WITH','{}',None),('S','O','D','SPONSORS_TRIAL_OF','{}',None)])
e=app.Engine.__new__(app.Engine);e.kg=types.SimpleNamespace(conn=c,link_entities=lambda text:[]);e.lock=threading.Lock()
srv=ThreadingHTTPServer(('127.0.0.1',0),app.make_handler(e));th=threading.Thread(target=srv.serve_forever,daemon=True);th.start()
cases=[]
try:
    for literal in ['null','true','false','0','1','3.5','"3"','NaN','Infinity','-Infinity']:
        with e.lock:
            c.execute('UPDATE edge SET props=? WHERE id=?',('{"association_score":'+literal+'}','A'))
            c.execute('UPDATE edge SET props=? WHERE id=?',('{"evidence_trials":'+literal+'}','S'))
        requests=[]
        for text in ['X','O']:
            req=urllib.request.Request(f'http://127.0.0.1:{srv.server_port}/api/explore',json.dumps({'text':text}).encode(),{'Content-Type':'application/json'})
            try:
                with urllib.request.urlopen(req,timeout=10) as r:status=r.status;body=json.load(r)
            except urllib.error.HTTPError as ex:status=ex.code;body=json.load(ex)
            requests.append({'input':text,'status':status,'body':body})
        cases.append({'stored_json_numeric_literal':literal,'requests':requests})
finally:
    srv.shutdown();srv.server_close();th.join(3);c.close()
(OUT/'db_numeric_fixture.json').write_text(json.dumps({'setup':'isolated in-memory X->ASSOCIATED_WITH->Y and O->SPONSORS_TRIAL_OF->D','cases':cases},ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps([{'literal':v['stored_json_numeric_literal'],'status':[r['status'] for r in v['requests']],'items':[r['body'].get('groups',[{'items':[]}])[0]['items'] for r in v['requests']]} for v in cases],ensure_ascii=False))
