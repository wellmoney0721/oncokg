"""Replay historical identity inputs on HEAD; outputs stay in this subtree."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
AUDIT = ROOT / 'audit_evidence_claims'
tmp = OUT / 'tmp'
tmp.mkdir(exist_ok=True)
env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONIOENCODING='utf-8',
           PYTHONUTF8='1', TMP=str(tmp), TEMP=str(tmp))
manifest = {'head': subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip(), 'runs': []}
for stage, names in [('s1', ['identity_probe.py']),
                     ('s2', ['identity_probe.py', 'identity_attack.py', 'root_contract_probe.py']),
                     ('s3', ['identity_attack.py'])]:
    dest = OUT / ('replay_' + stage)
    dest.mkdir(exist_ok=True)
    for name in names:
        source = AUDIT / stage / name
        original = source.read_text(encoding='utf-8')
        copied = original.replace('Path(__file__).resolve().parents[2]', 'Path(__file__).resolve().parents[4]')
        copied = copied.replace('ROOT = OUT.parents[1]', 'ROOT = OUT.parents[3]')
        if name == 'root_contract_probe.py':
            copied = copied.replace("assert len(ids) == 2 and out['output']['verified'] is True", "out['legacy_bug_assertion_holds'] = len(ids) == 2 and out['output']['verified'] is True")
        path = dest / name
        path.write_text(copied, encoding='utf-8')
        p = subprocess.run([sys.executable, '-B', str(path)], cwd=ROOT, env=env,
                           capture_output=True, encoding='utf-8')
        (dest / (name + '.stdout.txt')).write_text(p.stdout + '\nSTDERR:\n' + p.stderr, encoding='utf-8')
        manifest['runs'].append({'source': str(source.relative_to(ROOT)), 'output': str(path.relative_to(ROOT)),
            'exit': p.returncode, 'source_sha256': hashlib.sha256(original.encode()).hexdigest(),
            'adaptation': 'root/output paths only; historical bug assertion recorded as data'})
        print(stage, name, p.returncode, flush=True)
        if p.returncode:
            print(p.stderr, flush=True)
            continue
        resultname = 'root_contract_results.json' if name == 'root_contract_probe.py' else name.replace('.py', '_results.json')
        old = json.loads((AUDIT / stage / resultname).read_text(encoding='utf-8'))
        new = json.loads((dest / resultname).read_text(encoding='utf-8'))
        oldcases = old.get('cases', []) + old.get('synthetic_cases', []) + old.get('fixtures', [])
        newcases = new.get('cases', []) + new.get('synthetic_cases', []) + new.get('fixtures', [])
        manifest['runs'][-1].update({'cases': len(newcases),
            'same_inputs': repr([(r.get('tag'), r.get('input')) for r in oldcases]) == repr([(r.get('tag'), r.get('input')) for r in newcases]),
            'exceptions': [r.get('tag') for r in newcases if 'exception' in r],
            'changed': [{'tag': b.get('tag'), 'before': a.get('output', a.get('exception')),
                         'after': b.get('output', b.get('exception'))} for a, b in zip(oldcases, newcases)
                         if a.get('output', a.get('exception')) != b.get('output', b.get('exception'))]})
        if 'dictionary' in new:
            checks = new['dictionary']['retired_edge_checks']
            manifest['runs'][-1].update({'retired_edges': len(checks),
                'retired_edges_all_rejected': all(r['output'][0] is None for r in checks)})
(OUT / 'replay_manifest.json').write_text(json.dumps(manifest, indent=2, ensure_ascii=True), encoding='utf-8')
