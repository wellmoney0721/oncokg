import os,sys,json,time,subprocess
from pathlib import Path
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2]
env={**os.environ,'TMP':str(OUT),'TEMP':str(OUT),'TMPDIR':str(OUT),'PYTHONDONTWRITEBYTECODE':'1','PYTHONIOENCODING':'utf-8'}
rows=[]
for name in ['focused.py','fresh.py','http_probe.py','fresh_http.py','edge_probe.py','edge_http.py']:
 start=time.perf_counter()
 with (OUT/(name+'.stdout.txt')).open('w',encoding='utf8') as f:
  p=subprocess.run([sys.executable,'-B',str(OUT/name)],cwd=ROOT,env=env,stdout=f,stderr=subprocess.STDOUT)
 rows.append({'script':name,'exit_code':p.returncode,'seconds':time.perf_counter()-start});print(rows[-1],flush=True)
 (OUT/'execution.json').write_text(json.dumps(rows,indent=2),encoding='utf8')
 if p.returncode: raise SystemExit(p.returncode)
