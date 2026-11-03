"""Sequential owned CLI servers; all inherited reproduction cases preserved."""
import json, os, subprocess, sys, time
from pathlib import Path
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[1]
(OUT/'tmp').mkdir(exist_ok=True)
env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1','PYTHONUTF8':'1','PYTHONIOENCODING':'utf-8',
     'TMP':str(OUT/'tmp'),'TEMP':str(OUT/'tmp'),'TMPDIR':str(OUT/'tmp')}
rows=[]
for name in ['run_http.py','supplemental_http.py','attack_http.py','m5_http.py','cross_item_http.py','perf_check_http.py']:
    start=time.perf_counter()
    p=subprocess.run([sys.executable,'-B',str(OUT/name)],cwd=ROOT,env=env,capture_output=True,timeout=180)
    (OUT/(name+'.stdout.txt')).write_bytes(p.stdout+p.stderr)
    row={'script':name,'exit_code':p.returncode,'seconds':time.perf_counter()-start}
    rows.append(row)
    (OUT/'root_replay_execution.json').write_text(json.dumps(rows,indent=2),encoding='utf8')
    print(json.dumps(row),flush=True)
    if p.returncode: raise SystemExit(p.returncode)
