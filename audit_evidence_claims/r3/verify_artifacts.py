"""Verify saved audit outputs without rerunning the completed tests."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys
sys.dont_write_bytecode = True
OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[1]
def read(name):
    return json.loads((OUT / name).read_text(encoding='utf-8'))
def git(*args):
    p = subprocess.run(['git', *args], cwd=ROOT, capture_output=True, text=True, encoding='utf-8')
    return dict(returncode=p.returncode, stdout=p.stdout, stderr=p.stderr)
root = read('root3_probe.json')
ids = {r['id']: r for r in root}
blockers = ['pronoun_same_clause', 'count_cross_pair', 'count_shared_group',
            'heading_sponsors_full', 'heading_activators_full',
            'clinical_trial_unsupported', 'nsclc_trial_unsupported', 'zero_evidence_clinical']
for ident in blockers:
    c = ids[ident]['result']['checks']
    assert c['grounded'] is True and c['unsupported_claims'] == [], ident
controls = ['pronoun_same_clause_swap', 'pronoun_explicit_control',
            'count_cross_pair_control', 'plain_sponsors_full', 'plain_activators_full',
            'question_seed_bad', 'question_seed_wrong_type']
for ident in controls:
    assert ids[ident]['result']['checks']['grounded'] is False, ident
assert ids['zero_evidence_clinical']['result']['checks']['evidence_count'] == 0
replay = read('replay3_all_cases.json')
assert len(replay) == 246
docs = read('docs3_probe_results.json')
faithful = [r for r in docs if r['family'] == 'faithful']
assert sum(r['result']['checks']['grounded'] for r in faithful if r['q'] < 6) == 24
assert len([r for r in faithful if r['q'] < 6]) == 30
assert '175 passed' in (OUT / 'replay3_pytest.stdout.txt').read_text(encoding='utf-8')
tracked = git('diff', '--exit-code', 'HEAD', '--', '.')
staged = git('diff', '--cached', '--exit-code')
assert tracked['returncode'] == staged['returncode'] == 0
source_paths = ['src/claims.py', 'src/query.py', 'src/app.py', 'tests/test_claims.py',
                'README.md', 'README.ko.md', 'web/template.html', 'web/try.html',
                'data/processed/oncokg.sqlite']
hashes = {name:hashlib.sha256((ROOT/name).read_bytes()).hexdigest()
          for name in source_paths if (ROOT/name).is_file()}
baseline = read('replay3_verification.json')
result = dict(head=git('rev-parse', 'HEAD')['stdout'].strip(),
              tracked_diff=tracked, staged_diff=staged, git_status=git('status', '--short'),
              source_sha256=hashes, replay_cases=len(replay), root_probe_cases=len(root),
              numeric_probe_cases=len(read('numeric3_probe.json')),
              documentation_probe_cases=len(docs), focused_probe_cases=len(read('docs3_focused_results.json')),
              verified_new_blocker_ids=blockers, verified_negative_control_ids=controls,
              fresh_faithful_evidence_pass='24/30', fresh_refusal_pass='2/6',
              pytest=(OUT/'replay3_pytest.stdout.txt').read_text(encoding='utf-8').strip(),
              earlier_verification=baseline,
              artifact_sha256={p.name:hashlib.sha256(p.read_bytes()).hexdigest()
                               for p in OUT.iterdir() if p.is_file()
                               and p.name not in ('brief.md','log.txt','r3_verification.json')})
(OUT/'r3_verification.json').write_text(json.dumps(result,indent=2,ensure_ascii=False),encoding='utf-8')
print(json.dumps({k:result[k] for k in ['head','replay_cases','root_probe_cases','numeric_probe_cases',
                                      'documentation_probe_cases','focused_probe_cases','pytest']},ensure_ascii=True))
