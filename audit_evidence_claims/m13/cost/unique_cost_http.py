"""Actual lock contention for 400 distinct drug-bearing pieces within answer cap."""
from pathlib import Path
import concurrent.futures,hashlib,json,os,socket,subprocess,sys,time,urllib.request,urllib.error
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2];PORT=19403;BASE=f'http://127.0.0.1:{PORT}'
env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1','PYTHONIOENCODING':'utf-8','TEMP':str(OUT/'tmp'),'TMP':str(OUT/'tmp'),'TMPDIR':str(OUT/'tmp')}
def post(path,payload):
 t=time.perf_counter();req=urllib.request.Request(BASE+path,json.dumps(payload).encode(),{'Content-Type':'application/json'})
 try:r=urllib.request.urlopen(req,timeout=20)
 except urllib.error.HTTPError as ex:r=ex
 with r:body=json.load(r);status=r.status
 return {'path':path,'input':payload,'status':status,'seconds':time.perf_counter()-t,'body':body}
sock=socket.socket();sock.bind(('127.0.0.1',PORT));sock.close()
before=hashlib.sha256((ROOT/'data/processed/oncokg.sqlite').read_bytes()).hexdigest()
with (OUT/'unique_cost_server.txt').open('w',encoding='utf8') as log:
 p=subprocess.Popen([sys.executable,'-B','-u','src/app.py',str(PORT)],cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
 try:
  for _ in range(100):
   if p.poll() is not None:raise RuntimeError('server exit')
   try:urllib.request.urlopen(BASE,timeout=1).read();break
   except OSError:time.sleep(.1)
  else:raise RuntimeError('server startup timeout')
  baseline=post('/api/explore',{'text':'EGFR'})
  text=';'.join(f'isa x{i:04d}' for i in range(400));assert len(text)==3999
  with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
   start=time.perf_counter();leader=pool.submit(post,'/api/check',{'text':'EGFR','answer':text});time.sleep(.1);dispatched=time.perf_counter()-start;follower=pool.submit(post,'/api/explore',{'text':'EGFR'})
   t=time.perf_counter();r=urllib.request.urlopen(BASE,timeout=3);r.read();live={'seconds':time.perf_counter()-t,'status':r.status}
   cold=leader.result();queued=follower.result()
  warm=post('/api/check',{'text':'EGFR','answer':text});after_req=post('/api/explore',{'text':'EGFR'})
  result={'baseline':baseline,'cold':cold,'queued_egfr':queued,'follower_dispatched_seconds':dispatched,'live_get':live,'warm':warm,'after':after_req}
  (OUT/'isolated_unique_cost_http.json').write_text(json.dumps(result,indent=2,ensure_ascii=False),encoding='utf8');print(json.dumps({k:{'status':v['status'],'seconds':v['seconds']} for k,v in result.items() if isinstance(v,dict)},indent=2))
 finally:
  p.terminate();p.wait(timeout=10);after=hashlib.sha256((ROOT/'data/processed/oncokg.sqlite').read_bytes()).hexdigest()
  with socket.socket() as sock:closed=sock.connect_ex(('127.0.0.1',PORT))!=0
  (OUT/'unique_cost_lifecycle.json').write_text(json.dumps({'pid':p.pid,'port':PORT,'port_closed':closed,'db_before':before,'db_after':after,'db_unchanged':before==after,'exit':p.returncode},indent=2),encoding='utf8')
