"""Complete reused DB/UI checks; scratch outputs stay beside this runner."""
from pathlib import Path
import json, os, subprocess, sys, time

out = Path(__file__).resolve().parent
root = out.parents[2]
env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONIOENCODING='utf-8',
           TMP=str(out/'tmp'), TEMP=str(out/'tmp'), TMPDIR=str(out/'tmp'))
commands = [
    ['node', str(out/'ui_missing_sponsor_count.js')],
    [sys.executable, '-B', str(out/'ui_assertions.py')],
]
rows = []
for command in commands:
    start = time.perf_counter()
    run = subprocess.run(command, cwd=root, env=env, capture_output=True, timeout=90)
    log = out/(Path(command[-1]).name+'.stdout.txt')
    log.write_bytes(run.stdout+run.stderr)
    rows.append({'command': command, 'exit': run.returncode,
                 'seconds': time.perf_counter()-start, 'log': str(log)})
    print(json.dumps(rows[-1]), flush=True)
    if run.returncode:
        break
(out/'execution_final.json').write_text(json.dumps(rows, indent=2), encoding='utf8')
raise SystemExit(rows[-1]['exit'])
