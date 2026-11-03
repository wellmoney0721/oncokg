"""Execute historical scripts sequentially with every audit write under m8."""
from pathlib import Path
import subprocess,os,sys,json,time
out=Path(__file__).resolve().parent
env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONUTF8='1',PYTHONIOENCODING='utf-8',TEMP=str(out/'tmp'),TMP=str(out/'tmp'),TMPDIR=str(out/'tmp'))
rows=[]
names=['run_replays.py','run_supplement.py','adapted_frozen_qa_relink_sweep.py','m7_focus.py','m1_exact/run_m1_exact.py','alias_http.py']
for name in names:
    t=time.perf_counter();print('START',name,flush=True)
    with (out/(name.replace('/','_')+'.stdout.txt')).open('wb') as log:
        p=subprocess.run([sys.executable,'-B',str(out/name)],env=env,stdout=log,stderr=subprocess.STDOUT)
    row={'script':name,'exit_code':p.returncode,'seconds':time.perf_counter()-t}
    rows.append(row);out.joinpath('all_execution.json').write_text(json.dumps(rows,indent=2),encoding='utf8')
    print(row,flush=True)
