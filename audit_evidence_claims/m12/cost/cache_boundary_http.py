"""Reach the 4097-entry resolver-cache boundary through legal original-CLI requests."""
from pathlib import Path
import hashlib,json,os,socket,subprocess,sys,time,urllib.request,urllib.error
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2];PORT=8914;BASE=f'http://127.0.0.1:{PORT}'
env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1','PYTHONIOENCODING':'utf-8','TEMP':str(OUT/'tmp'),'TMP':str(OUT/'tmp'),'TMPDIR':str(OUT/'tmp')}
def post(text):
 t=time.perf_counter();req=urllib.request.Request(BASE+'/api/explore',json.dumps({'text':text}).encode(),{'Content-Type':'application/json'})
 try:r=urllib.request.urlopen(req,timeout=20)
 except urllib.error.HTTPError as ex:r=ex
 with r:body=json.load(r);status=r.status
 return {'input':text,'characters':len(text),'status':status,'seconds':time.perf_counter()-t,'center':body.get('center'),'error':body.get('error'),'body':body if status!=200 else None}
sock=socket.socket();sock.bind(('127.0.0.1',PORT));sock.close()
before=hashlib.sha256((ROOT/'data/processed/oncokg.sqlite').read_bytes()).hexdigest()
with (OUT/'cache_boundary_server.txt').open('w',encoding='utf8') as log:
 p=subprocess.Popen([sys.executable,'-B','-u','src/app.py',str(PORT)],cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0));rows=[]
 try:
  for _ in range(100):
   if p.poll() is not None:raise RuntimeError('server exit')
   try:urllib.request.urlopen(BASE,timeout=1).read();break
   except OSError:time.sleep(.1)
  else:raise RuntimeError('server startup timeout')
  pieces=[f'isa x{i:04d}' for i in range(4096)]
  for offset in range(0,len(pieces),50):
   text=';'.join(pieces[offset:offset+50]);assert len(text)<=500
   row=post(text);row['filled_distinct_pieces']=min(offset+50,4096);rows.append(row)
   if row['status']!=200:break
  boundary=post('osimertinib');retry=post('osimertinib')
  result={'fill_requests':len(rows),'fill_http_200':sum(r['status']==200 for r in rows),'fill':rows,'boundary':boundary,'retry':retry}
  (OUT/'cache_boundary_http.json').write_text(json.dumps(result,indent=2,ensure_ascii=False),encoding='utf8')
  print(json.dumps({'fill_requests':len(rows),'filled':rows[-1]['filled_distinct_pieces'],'boundary':boundary,'retry_status':retry['status'],'retry_center':retry['center']},ensure_ascii=False))
 finally:
  p.terminate();p.wait(timeout=10)
  after=hashlib.sha256((ROOT/'data/processed/oncokg.sqlite').read_bytes()).hexdigest()
  with socket.socket() as sock:closed=sock.connect_ex(('127.0.0.1',PORT))!=0
  (OUT/'cache_boundary_lifecycle.json').write_text(json.dumps({'pid':p.pid,'port':PORT,'port_closed':closed,'db_before':before,'db_after':after,'db_unchanged':before==after,'exit':p.returncode},indent=2),encoding='utf8')
