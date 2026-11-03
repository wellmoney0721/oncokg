"""Reused historical checks after run_round9, confined to this directory."""
from pathlib import Path
import json, os, subprocess, sys, time

out = Path(__file__).resolve().parent
(out / 'tmp').mkdir(exist_ok=True)
env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONUTF8='1',
           PYTHONIOENCODING='utf-8', TEMP=str(out / 'tmp'),
           TMP=str(out / 'tmp'), TMPDIR=str(out / 'tmp'))
rows = []
for name in ['run_additional.py', 'joined_label_probe.py',
             'm14_exact/edge_probe.py', 'm14_exact/fresh.py',
             'm14_supplement.py', 'm15_exact/targeted_probe.py',
             'm16_exact/new_probe.py', 'run_completion.py']:
    print('START', name, flush=True)
    start = time.perf_counter()
    with (out / (name.replace('/', '_') + '.m17.stdout.txt')).open('wb') as log:
        result = subprocess.run([sys.executable, '-B', str(out / name)],
                                env=env, stdout=log, stderr=subprocess.STDOUT,
                                timeout=1200)
    row = dict(script=name, exit_code=result.returncode,
               seconds=time.perf_counter() - start)
    rows.append(row)
    (out / 'remaining_execution.json').write_text(json.dumps(rows, indent=2), encoding='utf8')
    print(json.dumps(row), flush=True)
