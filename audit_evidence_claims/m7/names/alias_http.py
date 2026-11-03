from pathlib import Path
import json,os,subprocess,sys,time,urllib.request
sys.path.insert(0,str(Path('src').resolve()))
from app import Engine
import textrules as T
OUT=Path(__file__).resolve().parent
ENV={**os.environ,'PYTHONDONTWRITEBYTECODE':'1','PYTHONUTF8':'1','PYTHONIOENCODING':'utf-8'}
E=Engine();rows=[]
with (OUT/'alias_server.txt').open('wb') as log:
 p=subprocess.Popen([sys.executable,'-B','-u','src/app.py','8903'],stdout=log,stderr=subprocess.STDOUT,env=ENV)
 try:
  for i in range(100):
   if p.poll() is not None:raise RuntimeError('owned server exited')
   try:
    with urllib.request.urlopen('http://127.0.0.1:8903/',timeout=1) as r:
     if r.status==200:break
   except Exception:time.sleep(0.1)
  else:raise RuntimeError('server not ready')
  for s in ['(E/Z)-AFATINIB','RO 09-1978/000','Anusol plus hc','CHEMBL1173655','CHEMBL1773','CHEMBL389621']:
   row={'input':s,'stored_hits':E.dic['index'].get(T.canonical_key(s),[]),'requests':[]}
   for endpoint in ['resolve','explore']:
    request=urllib.request.Request('http://127.0.0.1:8903/api/'+endpoint,data=json.dumps({'text':s}).encode(),headers={'Content-Type':'application/json'})
    with urllib.request.urlopen(request,timeout=10) as r:
     row['requests'].append({'endpoint':endpoint,'status':r.status,'response':json.load(r)})
   rows.append(row)
 finally:
  p.terminate();p.wait(timeout=10);E.kg.conn.close()
  (OUT/'alias_http.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf8')
  (OUT/'alias_lifecycle.json').write_text(json.dumps({'owned_server_pid':p.pid,'port':8903,'server_returncode':p.returncode},indent=2),encoding='utf8')
print(json.dumps([{'input':r['input'],'center':r['requests'][1]['response'].get('center',{}).get('id'),'not_found':r['requests'][1]['response'].get('not_found')} for r in rows],ensure_ascii=False))
