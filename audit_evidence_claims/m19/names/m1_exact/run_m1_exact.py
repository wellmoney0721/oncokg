from pathlib import Path
import json,os,subprocess,sys,time,urllib.request
OUT=Path(__file__).resolve().parent
ENV={**os.environ,'PYTHONDONTWRITEBYTECODE':'1','PYTHONUTF8':'1','PYTHONIOENCODING':'utf-8'}
rows=[]
with (OUT/'server.txt').open('wb') as log:
 p=subprocess.Popen([sys.executable,'-B','-u','src/app.py','9110'],stdout=log,stderr=subprocess.STDOUT,env=ENV)
 try:
  for i in range(100):
   if p.poll() is not None:raise RuntimeError('owned server exited')
   try:
    with urllib.request.urlopen('http://127.0.0.1:9110/',timeout=1) as r:
     if r.status==200:break
   except Exception:time.sleep(0.1)
  else:raise RuntimeError('server not ready')
  for name in ['names_probe.py','names_extra_probe.py','names_product_probe.py','names_retired_probe.py','names_retired_http.py']:
   start=time.perf_counter()
   with (OUT/(name[:-3]+'_stdout.txt')).open('wb') as f:
    r=subprocess.run([sys.executable,'-B',str(OUT/name)],stdout=f,stderr=subprocess.STDOUT,env=ENV,timeout=120)
   row={'script':name,'exit_code':r.returncode,'seconds':round(time.perf_counter()-start,3)}
   rows.append(row);print(json.dumps(row),flush=True)
 finally:
  p.terminate();p.wait(timeout=10)
  (OUT/'execution.json').write_text(json.dumps({'owned_server_pid':p.pid,'port':9110,'server_returncode':p.returncode,'scripts':rows},indent=2),encoding='utf8')
