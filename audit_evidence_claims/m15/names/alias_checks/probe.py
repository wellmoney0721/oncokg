"""Independent HTTP confirmation of R8 candidates and same-molecule controls."""
import hashlib, json, os, re, socket, sqlite3, subprocess, sys, time, unicodedata
import urllib.request
from pathlib import Path

OUT = Path(__file__).resolve().parent
ROOT = Path.cwd()
sys.path.insert(0, str(ROOT/'src'))
from app import Engine
import query
PORT = 8921
texts = ['566C', 'ATOVAQUONE', '9-ac', '9-AMINOCAMPTOTHECIN', '5ac', 'AZACITIDINE', '5.BETA.,20-EPOXY-1,2.ALPHA.,4,7.BETA.', 'PACLITAXEL']
qas = []
e=Engine()
e.kg.conn.execute('PRAGMA query_only=ON')
stages=[]
for s in texts:
    norm=re.sub(query._DASHES,'-',unicodedata.normalize('NFKC',s))
    blocked=e.kg._resolver_blocked(norm); found=e.kg._link(norm)
    stages.append(dict(input=s, normalized=norm, resolver=e.resolve(s),
                       resolver_blocked=blocked, item_linker=found,
                       whole_name=e.kg._whole_name(norm,blocked,found),
                       public_linker=e.kg.link_entities(s)))
e.kg.conn.close()
with socket.socket() as sock:
    assert sock.connect_ex(('127.0.0.1',PORT))!=0,'owned audit port occupied'
db=ROOT/'data/processed/oncokg.sqlite'
before=hashlib.sha256(db.read_bytes()).hexdigest()
env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONUTF8='1',PYTHONIOENCODING='utf-8',
         TMP=str(OUT/'tmp'),TEMP=str(OUT/'tmp'),TMPDIR=str(OUT/'tmp'))
log=(OUT/'new_http_server.txt').open('w',encoding='utf8')
p=subprocess.Popen([sys.executable,'-B','-u','src/app.py',str(PORT)],cwd=ROOT,env=env,
                   stdout=log,stderr=subprocess.STDOUT,
                   creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
results=[]; lifecycle=dict(pid=p.pid,port=PORT,db_sha256_before=before)
try:
    for _ in range(100):
        if p.poll() is not None: raise RuntimeError('server exited')
        try:
            served=urllib.request.urlopen(f'http://127.0.0.1:{PORT}/',timeout=1).read()
            break
        except OSError: time.sleep(.1)
    else: raise RuntimeError('server unavailable')
    lifecycle['served_html_matches_worktree']=served==(ROOT/'web/try.html').read_bytes()
    for endpoint,s in [(x,s) for s in texts for x in ['explore','resolve']]+[('ask',s) for s in qas]:
        req=urllib.request.Request(f'http://127.0.0.1:{PORT}/api/{endpoint}',
            json.dumps({'text':s}).encode(),{'Content-Type':'application/json'})
        start=time.perf_counter()
        with urllib.request.urlopen(req,timeout=30) as res:
            body=json.load(res)
            results.append(dict(endpoint=endpoint,input=s,status=res.status,
                                elapsed_seconds=time.perf_counter()-start,response=body))
    (OUT/'new_http.json').write_text(json.dumps(dict(stages=stages,http=results),indent=2,ensure_ascii=False),encoding='utf8')
finally:
    p.terminate();p.wait(timeout=10);log.close()
    with socket.socket() as sock:lifecycle['port_closed']=sock.connect_ex(('127.0.0.1',PORT))!=0
    lifecycle['db_sha256_after']=hashlib.sha256(db.read_bytes()).hexdigest()
    lifecycle['database_unchanged']=lifecycle['db_sha256_after']==before
    (OUT/'new_http_lifecycle.json').write_text(json.dumps(lifecycle,indent=2),encoding='utf8')
print(json.dumps(dict(requests=len(results),all_200=all(r['status']==200 for r in results),lifecycle=lifecycle)))
