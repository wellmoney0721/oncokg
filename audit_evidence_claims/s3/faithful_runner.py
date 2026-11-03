"""Replay all legacy faithful probes with inputs unchanged and output confined to s3."""
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path.cwd()
OUT = ROOT / 'audit_evidence_claims' / 's3'
env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONUTF8='1', PYTHONIOENCODING='utf-8')
jobs = [('s1', 'faithful_probe.py'), ('s2', 'faithful_probe.py'),
        ('s2', 'faithful_additional_replay.py'), ('s2', 'faithful_dictionary_replay.py')]
manifest = []
for stage, filename in jobs:
    destination = OUT / ('replay_' + stage)
    destination.mkdir(exist_ok=True)
    original = ROOT / 'audit_evidence_claims' / stage / filename
    code = original.read_text(encoding='utf-8')
    if filename == 'faithful_dictionary_replay.py':
        code = code.replace("ROOT/'audit_evidence_claims/s2/faithful_graph_dictionary.json'",
                            "ROOT/'audit_evidence_claims/s3/replay_s2/faithful_graph_dictionary.json'")
    else:
        code = code.replace("OUT=ROOT/'audit_evidence_claims'/'" + stage + "'",
                            "OUT=ROOT/'audit_evidence_claims'/'s3'/'replay_" + stage + "'")
        code = code.replace("OUT = ROOT/'audit_evidence_claims'/'" + stage + "'",
                            "OUT = ROOT/'audit_evidence_claims'/'s3'/'replay_" + stage + "'")
    path = destination / filename
    path.write_text(code, encoding='utf-8')
    run = subprocess.run([sys.executable, '-B', str(path)], cwd=ROOT, env=env,
                         stdout=subprocess.PIPE, stderr=subprocess.STDOUT, encoding='utf-8')
    (destination / (path.stem + '_stdout.txt')).write_text(run.stdout, encoding='utf-8')
    manifest.append({'source': str(original.relative_to(ROOT)), 'replay': str(path.relative_to(ROOT)),
                     'exit_code': run.returncode, 'changes': 'Output paths only. Historical commit metadata unchanged.'})
    print(stage, filename, run.returncode, run.stdout[:2000], flush=True)
checks = {}
for stage in ['s1', 's2']:
    old = json.loads((ROOT / 'audit_evidence_claims' / stage / 'faithful_results.json').read_text(encoding='utf-8'))
    new = json.loads((OUT / ('replay_' + stage) / 'faithful_results.json').read_text(encoding='utf-8'))
    inputs = lambda obj: [(r['question'], {k: v['input'] for k, v in r['modes'].items()}) for r in obj['demonstrations']]
    checks[stage] = {'same_demo_inputs': inputs(old) == inputs(new), 'questions': len(new['demonstrations']),
        'claims_accepted': {mode: sum(len(r['modes'][mode]['output'].get('accepted', [])) for r in new['demonstrations']) for mode in ['labels', 'ids']},
        'phase_cases': len(new['phase_examples']), 'schema_cases': len(new['schema_limitations'])}
(OUT / 'faithful_replay_manifest.json').write_text(json.dumps({'jobs': manifest, 'checks': checks}, indent=2), encoding='utf-8')
print(json.dumps(checks, indent=2))
