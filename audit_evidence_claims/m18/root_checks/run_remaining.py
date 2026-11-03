"""Sequential inherited CLI/HTTP replays including exact M10 reproductions."""
from pathlib import Path
import os, subprocess, sys, time, json
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONUTF8='1',PYTHONIOENCODING='utf-8',
         TMP=str(OUT/'tmp'),TEMP=str(OUT/'tmp'),TMPDIR=str(OUT/'tmp'))
rows=[]
for args in [['run_m6_http.py','m6_http'],['run_extra.py'],['candidate_confirm.py'],['isotope_confirm.py']]:
    start=time.perf_counter()
    p=subprocess.run([sys.executable,'-B',str(OUT/args[0]),*args[1:]],cwd=ROOT,env=env,capture_output=True,timeout=240)
    (OUT/(args[0]+'.stdout.txt')).write_bytes(p.stdout+p.stderr)
    rows.append(dict(args=args,exit_code=p.returncode,seconds=time.perf_counter()-start))
    (OUT/'execution_remaining.json').write_text(json.dumps(rows,indent=2),encoding='utf8')
    print(json.dumps(rows[-1]),flush=True)
    if p.returncode: raise SystemExit(p.returncode)
