"""Reuse the m5 instrumented worker on current HEAD, with bounded subprocesses."""
import json, os, subprocess, sys
from pathlib import Path
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[1]
rows=[]
cases=[('plain',n) for n in [50,100,200,250,500,1000,2000]]+ [('split',n) for n in [250,1000,2000]]+[('single',500),('drug',244),('late_qualifier',235)]
for kind,size in cases:
    p=subprocess.run([sys.executable,'-B',str(OUT/'perf_probe.py'),'HEAD',kind,str(size)],cwd=ROOT,
        env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1','PYTHONUTF8':'1'},capture_output=True,timeout=15)
    assert p.returncode==0,p.stderr
    row=json.loads(p.stdout); rows.append(row)
    (OUT/'perf_current.json').write_text(json.dumps(rows,indent=2),encoding='utf8')
    print(json.dumps(row),flush=True)
