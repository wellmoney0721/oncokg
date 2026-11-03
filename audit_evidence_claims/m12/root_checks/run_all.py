"""Sequential test and real-HTTP reproduction suite."""
from pathlib import Path
import json,os,subprocess,sys,time
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONUTF8='1',PYTHONIOENCODING='utf-8',TMP=str(OUT/'tmp'),TEMP=str(OUT/'tmp'),TMPDIR=str(OUT/'tmp'))
jobs=[['run_replays.py','tests'],['run_replays.py','http'],['run_remaining.py'],['new_leaks_http.py']]
rows=[]
for args in jobs:
 start=time.perf_counter()
 p=subprocess.run([sys.executable,'-B',str(OUT/args[0]),*args[1:]],cwd=ROOT,env=env,capture_output=True,timeout=900)
 (OUT/(args[0]+'.batch.txt')).write_bytes(p.stdout+p.stderr)
 row=dict(args=args,exit_code=p.returncode,seconds=time.perf_counter()-start);rows.append(row)
 (OUT/'execution_all.json').write_text(json.dumps(rows,indent=2),encoding='utf8')
 print(json.dumps(row),flush=True)
 if p.returncode:raise SystemExit(p.returncode)
