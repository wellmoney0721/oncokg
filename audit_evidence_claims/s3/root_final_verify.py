"""Verify the read-only review and aggregate exact-input replay checks."""
import hashlib
import json
from pathlib import Path
import re
import subprocess

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[1]
read = lambda name: json.loads((OUT / name).read_text(encoding='utf-8'))
checks = {}
manifest = read('root_manifest.json')
checks['head'] = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
checks['head_unchanged'] = checks['head'] == manifest['head']
checks['reviewed_files_count'] = len(manifest['before'])
checks['changed_reviewed_files'] = [p for p, digest in manifest['before'].items()
    if hashlib.sha256((ROOT / p).read_bytes()).hexdigest() != digest]
checks['tracked_status'] = subprocess.check_output(['git', 'status', '--porcelain=v1', '--untracked-files=no'], cwd=ROOT, text=True)
untracked = subprocess.check_output(['git', '-c', 'core.quotepath=false', 'ls-files', '--others', '--exclude-standard'], cwd=ROOT, text=True, encoding='utf-8').splitlines()
checks['untracked_outside_s3'] = [p for p in untracked if not p.startswith('audit_evidence_claims/s3/')]
checks['root_replays'] = read('root_results.json')['replays']
identity = read('identity_replay_summary.json')
checks['identity'] = {round_: {k: identity[round_][k] for k in
    ('case_count', 'synthetic_count', 'retired_edge_count', 'same_inputs', 'exceptions')}
    for round_ in ('s1', 's2')}
checks['faithful_demos'] = read('faithful_replay_manifest.json')['checks']
checks['faithful_supplemental'] = read('faithful_comparison.json')
checks['model_ui'] = read('modelui_comparison.json')
checks['outage_captures'] = [{'round': r['source_round'], 'exact_exception': r['exact_exception'],
    'grounded': r['result']['checks']['grounded'],
    'applicable': r['result']['checks']['applicable']}
    for r in read('modelui_legacy_sdk_failure_results.json')]
checks['pytest_result'] = (OUT / 'pytest_stdout.txt').read_text(encoding='utf-8').strip().splitlines()[-1]
report = (OUT / 'REPORT.md').read_text(encoding='utf-8')
links = re.findall(r'\]\(([^)]+)\)', report)
# The final-verification artifact is about to be written by this script.
checks['missing_report_links'] = [link for link in links
    if link != 'root_final_verification.json' and not (OUT / link).exists()]
checks['report_last_line'] = report.strip().splitlines()[-1]
checks['sqlite_integrity'] = read('root_confirmation.json')['source_integrity']
assert checks['head_unchanged']
assert not checks['changed_reviewed_files'] and not checks['tracked_status']
assert not checks['untracked_outside_s3'] and not checks['missing_report_links']
assert all(r['identical_inputs'] and not r['exceptions'] and r['exit'] == 0 for r in checks['root_replays'])
assert all(r['same_inputs'] and not r['exceptions'] for r in checks['identity'].values())
assert all(r['same_demo_inputs'] and r['claims_accepted'] == {'labels': 73, 'ids': 73}
           for r in checks['faithful_demos'].values())
assert all(checks['faithful_supplemental'].values())
for round_ in ('s1', 's2'):
    r = checks['model_ui'][round_]
    assert r['common_model_inputs_identical'] and r['api_requests_identical']
    assert r['model_cases_executed'] == 29 and r['legacy_sdk_failure_captured_separately']
    assert r['page_no_raw_injected_elements']
assert checks['model_ui']['s2']['attack_inputs_identical']
assert checks['model_ui']['s2']['attack_api_requests_identical']
assert checks['model_ui']['new']['no_raw_injected_elements']
assert len(checks['outage_captures']) == 2
assert all(r['grounded'] is None and r['applicable'] is False for r in checks['outage_captures'])
assert '315 passed' in checks['pytest_result'] and checks['sqlite_integrity'] == 'ok'
assert checks['report_last_line'] == 'VERDICT: CHANGES REQUIRED'
(OUT / 'root_final_verification.json').write_text(json.dumps(checks, indent=2), encoding='utf-8')
print(json.dumps({k: checks[k] for k in ['head', 'reviewed_files_count', 'changed_reviewed_files',
    'tracked_status', 'untracked_outside_s3', 'missing_report_links', 'pytest_result',
    'sqlite_integrity', 'report_last_line']}, indent=2))
