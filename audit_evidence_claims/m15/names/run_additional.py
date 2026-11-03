from pathlib import Path
import os,subprocess,sys,time,json
out=Path(__file__).resolve().parent
env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONUTF8='1',PYTHONIOENCODING='utf-8',TEMP=str(out/'tmp'),TMP=str(out/'tmp'),TMPDIR=str(out/'tmp'))
rows=[]
for name in ['m9_attacks/probe.py','m10_attacks/probe.py','m10_attacks/focus.py','m11_attacks/key_equivalence.py','alias_loss_controls.py']:
    t=time.perf_counter()
    with (out/(name.replace('/','_')+'.m12.stdout.txt')).open('wb') as log:
        p=subprocess.run([sys.executable,'-B',str(out/name)],env=env,stdout=log,stderr=subprocess.STDOUT,timeout=300)
    row=dict(script=name,exit_code=p.returncode,seconds=time.perf_counter()-t)
    rows.append(row);(out/'additional_execution.json').write_text(json.dumps(rows,indent=2),encoding='utf8')
    print(json.dumps(row),flush=True)
