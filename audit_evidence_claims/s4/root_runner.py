"""Read-only round-four root replays and test run; all output is inside s4."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[1]
temp = OUT / 'root_tmp'
temp.mkdir(exist_ok=True)
env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONIOENCODING='utf-8',
           PYTHONUTF8='1', TEMP=str(temp), TMP=str(temp), TMPDIR=str(temp))
head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
paths = ['data/processed/oncokg.sqlite', 'data/processed/resolved.json',
         'README.md', 'README.ko.md', 'CODEX_STRUCTURED_S3_VERDICT.md']
paths += [str(p.relative_to(ROOT)).replace('\\', '/') for folder in ('src', 'tests', 'web')
          for p in (ROOT / folder).rglob('*') if p.is_file() and '__pycache__' not in str(p)]
def hashes():
    return {p: hashlib.sha256((ROOT / p).read_bytes()).hexdigest() for p in paths}
before = hashes()
(OUT / 'root_manifest.json').write_text(json.dumps({'head': head, 'before': before}, indent=2), encoding='utf-8')
runs = []
for series in ('s1', 's2'):
    target = OUT / ('replay_' + series)
    target.mkdir(exist_ok=True)
    original = ROOT / 'audit_evidence_claims' / series / 'root_probe.py'
    source = original.read_text(encoding='utf-8')
    copied = target / 'root_probe.py'
    copied.write_text(source.replace('Path(__file__).resolve().parents[2]',
                                     'Path(__file__).resolve().parents[3]'), encoding='utf-8')
    proc = subprocess.run([sys.executable, '-B', str(copied)], cwd=ROOT, env=env,
                          stdout=subprocess.PIPE, stderr=subprocess.STDOUT, encoding='utf-8')
    (target / 'root_stdout.txt').write_text(proc.stdout, encoding='utf-8')
    old = json.loads((original.parent / 'root_probe_results.json').read_text(encoding='utf-8'))
    new = json.loads((target / 'root_probe_results.json').read_text(encoding='utf-8'))
    signature = lambda rows: repr([(r['case'], r['input']) for r in rows])
    row = {'series': series, 'exit': proc.returncode, 'cases': len(new),
           'identical_inputs': signature(old) == signature(new),
           'exceptions': [r['case'] for r in new if 'exception' in r],
           'source_sha256': hashlib.sha256(original.read_bytes()).hexdigest(),
           'adaptation': 'ROOT parent index 2 -> 3 only; original commit field remains historical metadata.'}
    runs.append(row)
    print(json.dumps(row), flush=True)

target = OUT / 'replay_s3'
target.mkdir(exist_ok=True)
original = ROOT / 'audit_evidence_claims/s3/root_confirmation.py'
copied = target / original.name
copied.write_text(original.read_text(encoding='utf-8').replace('ROOT = OUT.parents[1]',
                  'ROOT = OUT.parents[2]'), encoding='utf-8')
proc = subprocess.run([sys.executable, '-B', str(copied)], cwd=ROOT, env=env,
                      stdout=subprocess.PIPE, stderr=subprocess.STDOUT, encoding='utf-8')
(target / 'root_confirmation_stdout.txt').write_text(proc.stdout, encoding='utf-8')
old = json.loads((original.parent / 'root_confirmation.json').read_text(encoding='utf-8'))
new = json.loads((target / 'root_confirmation.json').read_text(encoding='utf-8'))
signature = lambda obj: [(r['fixture_sql'], r['fixture_args'], r['question'],
                         [c['input'] for c in r['cases']]) for r in obj['cases']]
runs.append({'series': 's3_constructor', 'exit': proc.returncode,
             'cases': sum(len(r['cases']) for r in new['cases']),
             'identical_inputs': signature(old) == signature(new),
             'source_sha256': hashlib.sha256(original.read_bytes()).hexdigest(),
             'adaptation': 'ROOT parent index 1 -> 2 only',
             'results': [{'fixture': r['fixture_args'], 'accepted':
                          [c['name'] for c in r['cases'] if c['output']['accepted']]}
                         for r in new['cases']]})
print(json.dumps(runs[-1]), flush=True)
proc = subprocess.run([sys.executable, '-B', '-m', 'pytest', 'tests', '-q', '-p', 'no:cacheprovider',
                       '--basetemp', str(temp / 'pytest_base')], cwd=ROOT, env=env,
                      stdout=subprocess.PIPE, stderr=subprocess.STDOUT, encoding='utf-8')
(OUT / 'pytest_stdout.txt').write_text(proc.stdout, encoding='utf-8')
print(proc.stdout, flush=True)
after = hashes()
tracked = subprocess.run(['git', 'status', '--porcelain=v1', '--untracked-files=no'], cwd=ROOT,
                         capture_output=True, text=True)
result = {'head': head, 'replays': runs, 'pytest_exit': proc.returncode,
          'unchanged': before == after, 'changed_files': [p for p in before if before[p] != after[p]],
          'tracked_status': tracked.stdout, 'sqlite_integrity': new['source_integrity']}
(OUT / 'root_results.json').write_text(json.dumps(result, indent=2), encoding='utf-8')
print(json.dumps(result, indent=2), flush=True)
