from pathlib import Path
import subprocess,os,sys,json,time
out=Path(__file__).resolve().parent
names=['focused_matrix.py','focused_new.py','fresh_probe.py','reversed_probe.py','frozen_qa_relink_sweep.py','historical_qa_replay.py']
rows=[]
for name in names:
 start=time.perf_counter()
 with (out/(name[:-3]+'_stdout.txt')).open('wb') as fh:
  r=subprocess.run([sys.executable,'-B',str(out/name)],stdout=fh,stderr=subprocess.STDOUT,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1','PYTHONUTF8':'1','PYTHONIOENCODING':'utf-8'},timeout=300)
 row={'script':name,'exit_code':r.returncode,'seconds':round(time.perf_counter()-start,3)}
 rows.append(row);print(json.dumps(row),flush=True)
 (out/'supplement_execution.json').write_text(json.dumps(rows,indent=2),encoding='utf-8')
