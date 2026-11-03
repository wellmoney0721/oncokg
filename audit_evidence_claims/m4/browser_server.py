import os, subprocess, sys, time, socket, json, hashlib
from pathlib import Path
out=Path(__file__).resolve().parent
root=out.parents[1]
port=8881
with socket.socket() as s: assert s.connect_ex(('127.0.0.1',port))!=0
before=hashlib.sha256((root/'data/processed/oncokg.sqlite').read_bytes()).hexdigest()
log=(out/'browser_server.txt').open('w',encoding='utf-8')
p=subprocess.Popen([sys.executable,'-B','-u','src/app.py',str(port)],cwd=root,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1','PYTHONUTF8':'1'},stdout=log,stderr=subprocess.STDOUT,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
try:
    start=time.monotonic()
    while time.monotonic()-start<600 and not (out/'browser_stop').exists():
        assert p.poll() is None
        time.sleep(.2)
finally:
    p.terminate(); p.wait(timeout=10); log.close()
    with socket.socket() as s: closed=s.connect_ex(('127.0.0.1',port))!=0
    after=hashlib.sha256((root/'data/processed/oncokg.sqlite').read_bytes()).hexdigest()
    (out/'browser_lifecycle.json').write_text(json.dumps({'pid':p.pid,'port':port,'closed':closed,'db_unchanged':before==after},indent=2),encoding='utf-8')
