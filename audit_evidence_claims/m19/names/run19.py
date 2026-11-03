from pathlib import Path
import json,os,subprocess,sys,time
out=Path(__file__).resolve().parent
env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONUTF8='1',PYTHONIOENCODING='utf-8',TEMP=str(out/'tmp'),TMP=str(out/'tmp'),TMPDIR=str(out/'tmp'))
rows=[]
for name in ['run_round9.py','run_remaining.py','run_m17.py','m18_exact/new_probe.py','m18_exact/new_http.py']:
 print('START',name,flush=True);start=time.perf_counter()
 with (out/(name.replace('/','_')+'.m19.stdout.txt')).open('wb') as log:
  p=subprocess.run([sys.executable,'-B',str(out/name)],env=env,stdout=log,stderr=subprocess.STDOUT,timeout=1800)
 row=dict(script=name,exit_code=p.returncode,seconds=time.perf_counter()-start);rows.append(row);(out/'m19_execution.json').write_text(json.dumps(rows,indent=2),encoding='utf8');print(json.dumps(row),flush=True)
 if p.returncode:raise SystemExit(p.returncode)
