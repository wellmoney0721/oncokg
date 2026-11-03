"""Validate the completed s4 review without writing outside its scratch directory."""
import hashlib
import json
from pathlib import Path
import re
import subprocess

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[1]
def read(name):
    return json.loads((OUT / name).read_text(encoding='utf-8'))
def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT, text=True, encoding='utf-8').strip()

manifest = read('root_manifest.json')
root = read('root_results.json')
identity = read('identity/replay_manifest.json')
boundary = read('identity/boundary_results.json')
faithful = read('faithful/replay_manifest.json')
supplemental = read('faithful/historical_input_comparison.json')
model = read('modelui/comparison.json')
outages = read('modelui/modelui_legacy_sdk_failure_results.json')
contract = read('identity/replay_s2/root_contract_results.json')
constructor = read('replay_s3/root_confirmation.json')
report = (OUT / 'review_details.md').read_text(encoding='utf-8')
(OUT / 'REPORT.md').write_text(report, encoding='utf-8')
links = re.findall(r'\]\(([^)]+)\)', report)
checks = {
    'head': git('rev-parse', 'HEAD'),
    'reviewed_file_count': len(manifest['before']),
    'changed_reviewed_files': [p for p, h in manifest['before'].items()
        if hashlib.sha256((ROOT / p).read_bytes()).hexdigest() != h],
    'tracked_status': git('status', '--porcelain=v1', '--untracked-files=no'),
    'untracked_outside_s4': [p for p in git('-c', 'core.quotepath=false', 'ls-files', '--others',
        '--exclude-standard').splitlines() if not p.startswith('audit_evidence_claims/s4/')],
    'missing_report_links': [p for p in links if p != 'final_verification.json' and not (OUT / p).exists()],
    'root_replays': root['replays'],
    'identity_replays': [{k:v for k,v in r.items() if k != 'changed'} for r in identity['runs']],
    'duplicate_label_contract_rejected': not contract['output']['accepted'] and not contract['resolved_ids'],
    's4_boundary_cases': len(boundary['cases']),
    's4_boundary_all_expected': all(r['expectation_met'] for r in boundary['cases']),
    'constructor_alias_cases_rejected': all(not c['output']['accepted']
        for r in constructor['cases'] for c in r['cases'] if c['name'] == 'AstraZeneca!'),
    'faithful_checks': faithful['checks'],
    'faithful_historical_input_checks': supplemental['checks'],
    'model_ui': model,
    'model_ui_scripts_exit_zero': all(r['exit'] == 0 for r in read('modelui/replay_manifest.json')),
    'legacy_outages_captured': len(outages),
    'legacy_outages_no_groundedness_claim': all(r['result']['checks']['grounded'] is None
        and r['result']['checks']['applicable'] is False for r in outages),
    'pytest_result': (OUT / 'pytest_stdout.txt').read_text(encoding='utf-8').strip().splitlines()[-1],
    'sqlite_integrity': root['sqlite_integrity'],
    'report_final_line': report.strip().splitlines()[-1],
}
assert checks['head'] == manifest['head'] == root['head'] == identity['head'] == faithful['head']
assert not checks['changed_reviewed_files'] and not checks['tracked_status']
assert not checks['untracked_outside_s4'] and not checks['missing_report_links']
assert all(r['exit'] == 0 and r['identical_inputs'] for r in root['replays'])
assert all(r['exit'] == 0 and r['same_inputs'] and not r['exceptions'] for r in identity['runs'])
assert all(r.get('retired_edges_all_rejected', True) for r in identity['runs'])
assert checks['duplicate_label_contract_rejected'] and checks['constructor_alias_cases_rejected']
assert checks['s4_boundary_cases'] == 15 and checks['s4_boundary_all_expected']
assert all(r['returncode'] == 0 for r in faithful['jobs'])
assert all(r['same_demo_inputs'] and r['same_phase_inputs'] and r['same_schema_inputs']
    and r['claims_accepted'] == {'labels':73, 'ids':73} for r in faithful['checks'].values())
assert all(supplemental['checks'].values())
for series in ('s1', 's2'):
    row = model[series]
    assert row['model_cases_executed'] == 29 and row['common_inputs_identical']
    assert row['outage_captured_separately'] and row['api_requests_identical']
    assert row['no_raw_injected_elements']
assert model['s2']['attack_inputs_identical'] and model['s2']['attack_api_requests_identical']
assert model['s2']['attack_no_raw_injected_elements']
assert all(model['s3'][k] for k in ('inputs_identical','api_requests_identical','all_outputs_identical',
    'all_http_outputs_identical','all_strict_http_json','no_raw_injected_elements'))
assert checks['model_ui_scripts_exit_zero'] and checks['legacy_outages_captured'] == 2
assert checks['legacy_outages_no_groundedness_claim']
assert root['pytest_exit'] == 0 and '316 passed' in checks['pytest_result']
assert checks['sqlite_integrity'] == 'ok' and checks['report_final_line'] == 'VERDICT: APPROVE'
checks['all_assertions_passed'] = True
(OUT / 'final_verification.json').write_text(json.dumps(checks, indent=2), encoding='utf-8')
print(json.dumps({k: checks[k] for k in ('head','reviewed_file_count','changed_reviewed_files',
    'tracked_status','untracked_outside_s4','missing_report_links','pytest_result','sqlite_integrity',
    'all_assertions_passed','report_final_line')}, indent=2))
