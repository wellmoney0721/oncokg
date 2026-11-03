from pathlib import Path
import subprocess,os,sys,json,time
out=Path(__file__).resolve().parent
(out/'tmp').mkdir(exist_ok=True)
env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONUTF8='1',PYTHONIOENCODING='utf-8',TEMP=str(out/'tmp'),TMP=str(out/'tmp'),TMPDIR=str(out/'tmp'))
rows=[]
names=['run_replays.py','run_supplement.py','adapted_frozen_qa_relink_sweep.py','adapted_m7_focus.py','historical_focus.py','adapted_names_m5_attack.py','alias_regressions.py','m1_exact/run_m1_exact.py','alias_http.py','attacks/probe.py','attacks/lone_alias_probe.py','alias_checks/probe.py']
for name in names:
 t=time.perf_counter();print('START',name,flush=True)
 with (out/(name.replace('/','_')+'.round9.stdout.txt')).open('wb') as log:
  p=subprocess.run([sys.executable,'-B',str(out/name)],env=env,stdout=log,stderr=subprocess.STDOUT)
 row={'script':name,'exit_code':p.returncode,'seconds':time.perf_counter()-t}
 rows.append(row);out.joinpath('round9_execution.json').write_text(json.dumps(rows,indent=2),encoding='utf8')
 print(row,flush=True)
