"""Run exact M8/M9 HTTP reproductions with scratch and environment confined to M10."""
import json, os, subprocess, sys, time
from pathlib import Path
OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONUTF8='1', PYTHONIOENCODING='utf-8',
           TMP=str(OUT/'tmp'), TEMP=str(OUT/'tmp'), TMPDIR=str(OUT/'tmp'))
rows = []
for name in ['fresh_probe.py', 'independent_m12_http.py', 'independent_m13_http.py']:
    start = time.perf_counter()
    p = subprocess.run([sys.executable, '-B', str(OUT/name)], cwd=ROOT, env=env,
                       capture_output=True, timeout=180)
    (OUT/(name+'.stdout.txt')).write_bytes(p.stdout+p.stderr)
    rows.append(dict(script=name, exit_code=p.returncode, seconds=time.perf_counter()-start))
    (OUT/'execution_rounds12_13.json').write_text(json.dumps(rows, indent=2), encoding='utf8')
    print(json.dumps(rows[-1]), flush=True)
    if p.returncode: raise SystemExit(p.returncode)
