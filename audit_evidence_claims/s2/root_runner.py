"""Read-only review runner: replay unchanged s1 cases and run repo tests in s2."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONIOENCODING='utf-8', PYTHONUTF8='1')
tmp = OUT / 'pytest_tmp'
tmp.mkdir(exist_ok=True)
env['TEMP'] = env['TMP'] = env['TMPDIR'] = str(tmp)
head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
paths = ['data/processed/oncokg.sqlite', 'data/processed/resolved.json',
         'src/structured.py', 'src/query.py', 'src/app.py', 'web/try.html',
         'README.md', 'README.ko.md', 'web/template.html']
def hashes():
    return {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in paths}
before = hashes()
(OUT / 'root_current_manifest.json').write_text(json.dumps({'head': head, 'before': before}, indent=2), encoding='utf-8')
original = (ROOT / 'audit_evidence_claims/s1/root_probe.py').read_text(encoding='utf-8')
# The script locates output beside itself. Only its hardcoded manifest SHA is updated.
copied = original.replace('aa5655ae89c47631fefb9c868989ba2c1befa82e', head)
(OUT / 'root_probe.py').write_text(copied, encoding='utf-8')
for label, cmd in [('root_replay', [sys.executable, '-B', str(OUT / 'root_probe.py')]),
                   ('pytest', [sys.executable, '-B', '-m', 'pytest', 'tests', '-q', '-p', 'no:cacheprovider', '--basetemp', str(tmp / 'base')])]:
    proc = subprocess.run(cmd, cwd=ROOT, env=env, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, encoding='utf-8')
    (OUT / (label + '_stdout.txt')).write_text(proc.stdout, encoding='utf-8')
    print(label, 'exit', proc.returncode, flush=True)
    print(proc.stdout[-6000:], flush=True)
after = hashes()
status = subprocess.run(['git', 'status', '--porcelain=v1', '--untracked-files=no'], cwd=ROOT, capture_output=True, text=True)
(OUT / 'root_integrity.json').write_text(json.dumps({'head': head, 'before': before, 'after': after, 'unchanged': before == after, 'tracked_status': status.stdout}, indent=2), encoding='utf-8')
