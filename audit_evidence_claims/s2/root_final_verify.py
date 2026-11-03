"""Verify replay input identity, report links, and reviewed-file integrity."""
import hashlib
import json
from pathlib import Path
import re
import subprocess

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[1]
S1 = OUT.parent / 's1'
def read(base, name):
    return json.loads((base / name).read_text(encoding='utf-8'))
checks = {}
old, new = read(S1, 'root_probe_results.json'), read(OUT, 'root_probe_results.json')
# repr normalizes matching non-standard NaN values for comparison of these legacy artifacts.
checks['root_same_inputs'] = repr([(r['case'], r['input']) for r in old]) == repr([(r['case'], r['input']) for r in new])
checks['root_cases'] = len(new)
old, new = read(S1, 'identity_probe_results.json'), read(OUT, 'identity_probe_results.json')
checks['identity_same_inputs'] = repr([(r['tag'], r['input']) for r in old['cases']]) == repr([(r['tag'], r['input']) for r in new['cases']])
checks['identity_cases'] = len(new['cases'])
checks['identity_synthetic_cases'] = len(new['synthetic_cases'])
old, new = read(S1, 'faithful_results.json'), read(OUT, 'faithful_results.json')
extract = lambda a: [(r['question'], {mode: val['input'] for mode, val in r['modes'].items()}) for r in a['demonstrations']]
checks['faithful_same_inputs'] = extract(old) == extract(new)
checks['faithful_accepted'] = {mode: sum(len(r['modes'][mode]['output'].get('accepted', [])) for r in new['demonstrations']) for mode in ['labels', 'ids']}
old, new = read(S1, 'modelui_results.json'), read(OUT, 'modelui_results.json')
extract = lambda a: [(r['case'], r.get('raw_reply'), r.get('input_description')) for r in a['model_cases']]
checks['model_same_inputs'] = extract(old) == extract(new)
checks['model_cases'] = len(new['model_cases'])
checks['api_same_requests'] = [(r['case'], r['request']) for r in old['api_cases']] == [(r['case'], r['request']) for r in new['api_cases']]
checks['api_cases'] = len(new['api_cases'])
manifest = read(OUT, 'root_current_manifest.json')
checks['reviewed_hashes_unchanged'] = all(hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == expected for path, expected in manifest['before'].items())
status = subprocess.run(['git', 'status', '--porcelain=v1', '--untracked-files=no'], cwd=ROOT, capture_output=True, text=True)
checks['tracked_status'] = status.stdout
report = (OUT / 'REPORT.md').read_text(encoding='utf-8')
checks['missing_report_links'] = [target for target in re.findall(r'\]\(([^)]+)\)', report) if not (OUT / target).exists()]
checks['report_last_line'] = report.strip().splitlines()[-1]
for key, val in checks.items():
    if key.endswith('same_inputs') or key.endswith('same_requests') or key == 'reviewed_hashes_unchanged':
        assert val, key
assert not checks['tracked_status']
assert not checks['missing_report_links']
assert checks['report_last_line'] == 'VERDICT: CHANGES REQUIRED'
(OUT / 'root_final_verification.json').write_text(json.dumps(checks, indent=2), encoding='utf-8')
print(json.dumps(checks, indent=2))
