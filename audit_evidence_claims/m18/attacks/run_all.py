"""Run reused historical and fresh attacks; every output stays beside this script."""
import json, os, subprocess, sys, time
from pathlib import Path
sys.dont_write_bytecode = True
OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
(OUT / 'tmp').mkdir(exist_ok=True)
env = {**os.environ, 'PYTHONDONTWRITEBYTECODE':'1', 'PYTHONIOENCODING':'utf-8',
       'TEMP':str(OUT/'tmp'), 'TMP':str(OUT/'tmp'), 'TMPDIR':str(OUT/'tmp')}
scripts = ['new_probe.py', 'new_http.py', 'm17_new_probe.py', 'm17_new_http.py',
           'previous_new_probe.py', 'previous_new_http.py', 'focused.py', 'fresh.py',
           'edge_probe.py', 'targeted_probe.py', 'alias_variants.py']
execution=[]
for name in scripts:
    start=time.perf_counter()
    with (OUT/(name+'.stdout.txt')).open('w',encoding='utf8') as log:
        result=subprocess.run([sys.executable,'-B',str(OUT/name)],cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT)
    row={'script':name,'exit_code':result.returncode,'seconds':time.perf_counter()-start}
    execution.append(row)
    (OUT/'execution.json').write_text(json.dumps(execution,indent=2),encoding='utf8')
    print(json.dumps(row),flush=True)
    if result.returncode:
        raise SystemExit(result.returncode)
