from pathlib import Path
import json,os,subprocess,sys,time
out=Path(__file__).resolve().parent
env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONUTF8='1',PYTHONIOENCODING='utf-8',TEMP=str(out/'tmp'),TMP=str(out/'tmp'),TMPDIR=str(out/'tmp'))
rows=[]
for name in ['m17_exact/new_probe.py','m17_exact/new_http.py']:
    start=time.perf_counter()
    with (out/(name.replace('/','_')+'.stdout.txt')).open('wb') as log:
        result=subprocess.run([sys.executable,'-B',str(out/name)],env=env,stdout=log,stderr=subprocess.STDOUT,timeout=300)
    row=dict(script=name,exit_code=result.returncode,seconds=time.perf_counter()-start)
    rows.append(row)
    (out/'m17_execution.json').write_text(json.dumps(rows,indent=2),encoding='utf8')
    print(json.dumps(row),flush=True)
    if result.returncode:raise SystemExit(result.returncode)
