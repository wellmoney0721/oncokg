"""Run prior identity probes without writing outside s3. Input expressions unchanged."""
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[1]
env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONIOENCODING='utf-8', PYTHONUTF8='1')
results = []
for stage, names in [('s1', ['identity_probe.py']),
                     ('s2', ['identity_probe.py', 'identity_attack.py', 'root_contract_probe.py'])]:
    dest = OUT / ('replay_' + stage)
    dest.mkdir(exist_ok=True)
    for name in names:
        original = (OUT.parent / stage / name).read_text(encoding='utf-8')
        copied = original.replace('Path(__file__).resolve().parents[2]', 'Path(__file__).resolve().parents[3]')
        if name == 'root_contract_probe.py':
            copied = copied.replace("assert len(ids) == 2 and out['output']['verified'] is True", "out['legacy_bug_assertion_holds'] = len(ids) == 2 and out['output']['verified'] is True")
        path = dest / name
        path.write_text(copied, encoding='utf-8')
        proc = subprocess.run([sys.executable, '-B', str(path)], cwd=ROOT, env=env, capture_output=True, encoding='utf-8')
        (dest / (path.stem + '_stdout.txt')).write_text(proc.stdout + '\nSTDERR:\n' + proc.stderr, encoding='utf-8')
        results.append({'stage': stage, 'name': name, 'exit': proc.returncode,
                        'source_sha256': hashlib.sha256(original.encode()).hexdigest(),
                        'adaptation': 'root path and output location only; contract legacy bug assertion recorded as data'})
        print(stage, name, proc.returncode, flush=True)
        if proc.returncode:
            print(proc.stderr, flush=True)
summary = {'runs': results}
for stage in ['s1', 's2']:
    old = json.loads((OUT.parent / stage / 'identity_probe_results.json').read_text(encoding='utf-8'))
    new = json.loads((OUT / ('replay_' + stage) / 'identity_probe_results.json').read_text(encoding='utf-8'))
    summary[stage] = {'case_count': len(new['cases']), 'synthetic_count': len(new['synthetic_cases']),
                     'retired_edge_count': len(new['dictionary']['retired_edge_checks']),
                     'same_inputs': repr([(r['tag'], r['input']) for r in old['cases']]) == repr([(r['tag'], r['input']) for r in new['cases']]),
                     'exceptions': [r['tag'] for r in new['cases'] if 'exception' in r],
                     'changed_outcomes': [{'tag': a['tag'], 'before': a.get('output', a.get('exception')), 'after': b.get('output', b.get('exception'))} for a, b in zip(old['cases'] + old['synthetic_cases'], new['cases'] + new['synthetic_cases']) if a.get('output', a.get('exception')) != b.get('output', b.get('exception'))]}
summary['s2_attack'] = json.loads((OUT / 'replay_s2' / 'identity_attack_results.json').read_text(encoding='utf-8'))
(OUT / 'identity_replay_summary.json').write_text(json.dumps(summary, indent=2, ensure_ascii=True), encoding='utf-8')
