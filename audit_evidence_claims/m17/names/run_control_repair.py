"""Rerun the original M15 control inventory after repairing a port-only adaptation."""
from pathlib import Path
import json, os, subprocess, sys, time

out = Path(__file__).resolve().parent
env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONUTF8='1',
           PYTHONIOENCODING='utf-8', TEMP=str(out / 'tmp'),
           TMP=str(out / 'tmp'), TMPDIR=str(out / 'tmp'))
rows = []
for name in ['m15_exact/targeted_probe.py', 'compare_replays.py']:
    start = time.perf_counter()
    with (out / (name.replace('/', '_') + '.control_repair.stdout.txt')).open('wb') as log:
        result = subprocess.run([sys.executable, '-B', str(out / name)],
                                env=env, stdout=log, stderr=subprocess.STDOUT,
                                timeout=120)
    row = dict(script=name, exit_code=result.returncode,
               seconds=time.perf_counter() - start)
    rows.append(row)
    (out / 'control_repair_execution.json').write_text(json.dumps(rows, indent=2), encoding='utf8')
    print(json.dumps(row), flush=True)
    if result.returncode:
        raise SystemExit(result.returncode)
