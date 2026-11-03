import json,os,subprocess,sys,time
from pathlib import Path
out=Path(__file__).resolve().parent
rows=[]
env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1','PYTHONIOENCODING':'utf-8','TMP':str(out),'TEMP':str(out),'TMPDIR':str(out)}
for name in ['focused.py','http_probe.py','fresh.py','fresh_http.py']:
 start=time.perf_counter()
 with (out/(name+'.stdout.txt')).open('w',encoding='utf-8') as f:
  r=subprocess.run([sys.executable,'-B',str(out/name)],env=env,stdout=f,stderr=subprocess.STDOUT)
 rows.append({'script':name,'exit':r.returncode,'seconds':time.perf_counter()-start})
 (out/'execution.json').write_text(json.dumps(rows,indent=2),encoding='utf-8')
 print(name,r.returncode,flush=True)
