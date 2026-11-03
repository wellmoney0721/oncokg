import json, os, subprocess, sys, time
from pathlib import Path
out = Path(__file__).resolve().parent
root = out.parents[2]
env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONIOENCODING='utf-8',
           PYTHONUTF8='1', TMP=str(out/'tmp'), TEMP=str(out/'tmp'), TMPDIR=str(out/'tmp'))
rows = []
for name in ['db_recheck.py','db_missing_sponsor_count.py','db_role_fallback.py',
             'db_score_fixture.py','db_numeric_fixture.py','db_snapshot.py','db_assertions.py']:
    started = time.perf_counter()
    run = subprocess.run([sys.executable,'-B',str(out/name)], cwd=root, env=env,
                         capture_output=True, timeout=300)
    (out/(name+'.stdout.txt')).write_bytes(run.stdout+run.stderr)
    rows.append(dict(script=name, exit_code=run.returncode, seconds=time.perf_counter()-started))
    (out/'execution.json').write_text(json.dumps(rows,indent=2),encoding='utf8')
    print(json.dumps(rows[-1]),flush=True)
    if run.returncode: raise SystemExit(run.returncode)
