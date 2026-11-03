"""Replay original cost workloads sequentially; no other audit benchmark runs alongside."""
import json, os, subprocess, sys, time
from pathlib import Path
OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONUTF8='1', PYTHONIOENCODING='utf-8',
           TMP=str(OUT/'tmp'), TEMP=str(OUT/'tmp'), TMPDIR=str(OUT/'tmp'))
rows = []
names = ['cache_boundary_http.py'] if 'cache' in sys.argv else [
    'run_perf_current.py', 'cost_stress.py', 'unique_piece_cost.py',
    'unique_cost_http.py', 'fresh_cost.py']
for name in names:
    start = time.perf_counter()
    p = subprocess.run([sys.executable, '-B', str(OUT/name)], cwd=ROOT, env=env,
                       capture_output=True, timeout=240)
    (OUT/(name+'.stdout.txt')).write_bytes(p.stdout+p.stderr)
    rows.append(dict(script=name, exit_code=p.returncode, seconds=time.perf_counter()-start))
    (OUT/('execution_'+sys.argv[-1]+'.json')).write_text(json.dumps(rows, indent=2), encoding='utf8')
    print(json.dumps(rows[-1]), flush=True)
    if p.returncode: raise SystemExit(p.returncode)
