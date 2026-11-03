"""Replay every late-round independent HTTP input against current HEAD."""
from pathlib import Path
import json, os, subprocess, sys, time
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONUTF8='1',PYTHONIOENCODING='utf-8',
         TMP=str(OUT/'tmp'),TEMP=str(OUT/'tmp'),TMPDIR=str(OUT/'tmp'))
rows=[]
for name in ['run_late.py','independent_m16_http.py','independent_m17_http.py']:
    start=time.perf_counter()
    p=subprocess.run([sys.executable,'-B',str(OUT/name)],cwd=ROOT,env=env,capture_output=True,timeout=300)
    (OUT/(name+'.m18.stdout.txt')).write_bytes(p.stdout+p.stderr)
    rows.append(dict(script=name,exit_code=p.returncode,seconds=time.perf_counter()-start))
    (OUT/'execution_m18_late.json').write_text(json.dumps(rows,indent=2),encoding='utf8')
    print(json.dumps(rows[-1]),flush=True)
    if p.returncode: raise SystemExit(p.returncode)
