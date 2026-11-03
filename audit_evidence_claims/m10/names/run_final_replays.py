"""Remaining exact original m7/m9 HTTP reproductions; all owned servers use 8892."""
from pathlib import Path
import json,os,subprocess,sys,time
out=Path(__file__).resolve().parent
env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONUTF8='1',PYTHONIOENCODING='utf-8',TEMP=str(out/'tmp'),TMP=str(out/'tmp'),TMPDIR=str(out/'tmp'))
rows=[]
for name in ['m7_attacks/fresh_probe.py','m9_attacks/http_probe.py','new_alias_confirmation.py']:
    started=time.perf_counter()
    with (out/(name.replace('/','_')+'.round10.stdout.txt')).open('wb') as log:
        p=subprocess.run([sys.executable,'-B',str(out/name)],env=env,stdout=log,stderr=subprocess.STDOUT,timeout=300)
    row=dict(script=name,exit_code=p.returncode,seconds=time.perf_counter()-started)
    rows.append(row)
    (out/'final_replay_execution.json').write_text(json.dumps(rows,indent=2),encoding='utf8')
    print(json.dumps(row),flush=True)
