"""Historical cost suites, sequentially after other review workloads finish."""
from pathlib import Path
import os,sys,time,json,subprocess
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2]
env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONUTF8='1',PYTHONIOENCODING='utf-8',TMP=str(OUT/'tmp'),TEMP=str(OUT/'tmp'),TMPDIR=str(OUT/'tmp'))
rows=[]
for name in ['run_perf_current.py','cost_stress.py','unique_piece_cost.py','fresh_cost.py','cache_boundary_http.py','perf_check_http.py','unique_cost_http.py','unicode_cost_http.py','normalization_cost.py']:
 start=time.perf_counter()
 p=subprocess.run([sys.executable,'-B',str(OUT/name)],cwd=ROOT,env=env,capture_output=True,timeout=300)
 (OUT/(name+'.stdout.txt')).write_bytes(p.stdout+p.stderr)
 row=dict(script=name,exit_code=p.returncode,seconds=time.perf_counter()-start);rows.append(row)
 (OUT/'execution_isolated.json').write_text(json.dumps(rows,indent=2),encoding='utf8')
 print(json.dumps(row),flush=True)
 if p.returncode:raise SystemExit(p.returncode)
