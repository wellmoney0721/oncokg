"""Execute inherited reproducers, owning and closing one HTTP port at a time."""
import json,os,subprocess,sys,time
from pathlib import Path
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1','PYTHONUTF8':'1','PYTHONIOENCODING':'utf-8',
     'TMP':str(OUT/'tmp'),'TEMP':str(OUT/'tmp'),'TMPDIR':str(OUT/'tmp')}
names=(['run_verification.py'] if 'tests' in sys.argv else ['perf_probe.py'] if 'perf' in sys.argv
       else ['run_http.py','supplemental_http.py','attack_http.py','m5_http.py','cross_item_http.py','perf_check_http.py'])
rows=[]
for name in names:
    start=time.perf_counter()
    p=subprocess.run([sys.executable,'-B',str(OUT/name)],cwd=ROOT,env=env,capture_output=True,timeout=240)
    (OUT/(name+'.stdout.txt')).write_bytes(p.stdout+p.stderr)
    rows.append({'script':name,'exit_code':p.returncode,'seconds':time.perf_counter()-start})
    (OUT/('execution_'+sys.argv[-1]+'.json')).write_text(json.dumps(rows,indent=2),encoding='utf-8')
    print(json.dumps(rows[-1]),flush=True)
    if p.returncode: raise SystemExit(p.returncode)
