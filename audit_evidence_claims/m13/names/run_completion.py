from pathlib import Path
import os,subprocess,sys,time,json
out=Path(__file__).resolve().parent
env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONUTF8='1',PYTHONIOENCODING='utf-8',TEMP=str(out/'tmp'),TMP=str(out/'tmp'),TMPDIR=str(out/'tmp'))
rows=[]
for name in ['run_additional.py','run_final_replays.py','m11_exact.py','new_alias_regression.py','m12_attacks/focused.py','compare_replays.py']:
 t=time.perf_counter();print('START',name,flush=True)
 with (out/(name.replace('/','_')+'.m13.stdout.txt')).open('wb') as log:
  p=subprocess.run([sys.executable,'-B',str(out/name)],env=env,stdout=log,stderr=subprocess.STDOUT,timeout=600)
 row=dict(script=name,exit_code=p.returncode,seconds=time.perf_counter()-t);rows.append(row)
 (out/'completion_execution.json').write_text(json.dumps(rows,indent=2),encoding='utf8');print(json.dumps(row),flush=True)
