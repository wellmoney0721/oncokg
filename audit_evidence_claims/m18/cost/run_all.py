"""Run copied historical workloads and Round11 controls sequentially."""
from pathlib import Path
import hashlib,json,os,subprocess,sys,time
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2]
env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONUTF8='1',PYTHONIOENCODING='utf-8',TEMP=str(OUT/'tmp'),TMP=str(OUT/'tmp'),TMPDIR=str(OUT/'tmp'))
rows=[]
names=['run_perf_current.py','perf_check_http.py','cost_stress.py','fresh_cost.py','unique_piece_cost.py','unique_cost_http.py','normalization_cost.py']
for name in names:
 start=time.perf_counter()
 try:
  p=subprocess.run([sys.executable,'-B',str(OUT/name)],cwd=ROOT,env=env,capture_output=True,timeout=240)
  (OUT/(name+'.stdout.txt')).write_bytes(p.stdout+p.stderr)
  row={'script':name,'exit_code':p.returncode,'seconds':time.perf_counter()-start}
 except subprocess.TimeoutExpired as e:
  (OUT/(name+'.stdout.txt')).write_bytes((e.stdout or b'')+(e.stderr or b''))
  row={'script':name,'timeout_seconds':240,'seconds':time.perf_counter()-start}
 rows.append(row);(OUT/'execution.json').write_text(json.dumps(rows,indent=2),encoding='utf8');print(json.dumps(row),flush=True)
 if row.get('exit_code')!=0:raise SystemExit(1)
