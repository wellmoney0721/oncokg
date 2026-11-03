"""Validate fresh evidence and emit the Round 14 historical name matrix."""
from pathlib import Path
import hashlib, json, runpy, socket, subprocess

root = Path.cwd()
out = Path(__file__).resolve().parent
prior = root / 'audit_evidence_claims/m13/names'
def read(name): return json.loads((out / name).read_text(encoding='utf8'))
def old(name): return json.loads((prior / name).read_text(encoding='utf8'))

comparison = read('replay_comparison.json')
assert not any(r.get('missing') for r in comparison['files'])
changed = {r['file'] for r in comparison['files'] if not r['normalized_equal']}
assert changed == {'adapted_names_m5_summary.json', 'alias_regressions.json', 'names_m5_attack.json', 'names_m5_summary.json', 'new_alias_regression.json'}
clean = runpy.run_path(str(out / 'compare_replays.py'))['clean']
adjudication = []
for name, field in [('names_m5_summary.json', 'new_lone_alias_refusals'), ('adapted_names_m5_summary.json', 'new_lone_alias_refusals'), ('names_m5_attack.json', 'alias_anomalies'), ('alias_regressions.json', 'cases')]:
    before, after = old(name)[field], read(name)[field]
    assert {r['input'] for r in before} - {r['input'] for r in after} == {'rad001c'}, name
    assert not ({r['input'] for r in after} - {r['input'] for r in before}), name
    assert clean([r for r in before if r['input'] != 'rad001c']) == clean(after), name
    adjudication.append(dict(file=name, removed_only='rad001c', retained_rows_semantically_equal=True))
aliases = {r['text']: r for r in read('new_alias_regression.json')['cases']}
for text in ['rad001c', 'RAD001C']:
    assert aliases[text]['current']['map']['center']['id'] == 'CHEMBL1908360'
    assert len(aliases[text]['current']['trial_qa']['evidence']) == 9
    assert not aliases[text]['previous']['map'].get('center')
assert [r['finding'] for r in read('focused_matrix.json') if not r['matches_expectation']] == ['M5-S2-known']
assert all(r['status'] == 'FIXED' for r in read('historical_focus.json')['cases'])
assert all(r['actual_center'] == r['expected_center'] for r in read('m11_exact.json'))
assert all(not q['evidence'] for r in read('m11_exact.json') if not r['expected_center'] for q in r['qa'])
assert read('adapted_frozen_qa_relink_sweep.json')['summary'] == dict(questions=1648, identical=68, entities_only=1556, semantic_changes=24, errors=0)
for r in read('joined_label_probe.json'):
    if r['text'] == 'daratumumab': assert r['map']['center']['id'] == 'CHEMBL1743007'
    elif r['text'].endswith(', osimertinib'):
        assert r['map']['center']['id'] == 'CHEMBL3353410'
        assert any(x['type'] == 'Refused' for x in r['public_linker'])
    else:
        assert not r['map'].get('center') and r['map'].get('refused'), r['text']
        assert not r['trial_qa']['evidence'] and not r['sponsor_qa']['evidence'], r['text']
attack_rows = json.loads((out.parent / 'attacks/fresh_results.json').read_text(encoding='utf8'))['cases']
assert next(r for r in attack_rows if r['text'] == 'A33124I')['current']['map']['center']['id'] == 'CHEMBL5314551'

matrix = old('historical_name_dispositions.json')
for r in matrix:
    if r['finding'].startswith('M12-S1'):
        r.update(status='FIXED', detail='rad001c and RAD001C now select EVEROLIMUS / CHEMBL1908360 with 9 stored trials and 9 trial-QA rows; HEAD^ still refuses. rad, RAD001, EVEROLIMUS and its ID remain available.')
matrix += [
 dict(round='M13', finding='M13-B1 isotope fused to chelator inside matched alias', status='FIXED', detail='89ZrDFO-daratumumab, 89zrdfodaratumumab, [89ZrDFO]-daratumumab, 89zrdfo daratumumab and 89Zr-DFOdaratumumab refuse, with zero trial/sponsor evidence. Bare daratumumab maps correctly; separately listed osimertinib survives.', evidence='joined_label_probe.json'),
 dict(round='M13', finding='M13 supplementary A33124I trailing isotope', status='NOT FIXED', detail='A33124I still draws ADAKITUG / CHEMBL5314551 via stored A33 124i; spaced control refuses. M13 recorded this as a supplementary corroboration, not a separately counted blocker. The originator gap remains.', evidence='../attacks/fresh_results.json'),
]
(out / 'historical_name_dispositions.json').write_text(json.dumps(matrix, ensure_ascii=False, indent=2), encoding='utf8')
current = read('names_m5_summary.json')
oldset = {r['input'] for r in old('names_m5_summary.json')['new_lone_alias_refusals']}
newset = {r['input'] for r in current['new_lone_alias_refusals']}
assert current['aliases_checked'] == 7511 and current['alias_anomalies'] == 318 and len(newset) == 69
assert not newset - oldset and oldset - newset == {'rad001c'}
(out / 'new_alias_losses.json').write_text(json.dumps(dict(description='Current versus M13 loss set; not a defect count.', new_losses=[], recovered=['rad001c'], current_loss_count=69, previous_loss_count=70), indent=2), encoding='utf8')
prior19 = json.loads((root / 'audit_evidence_claims/m7/names/names_m5_summary.json').read_text(encoding='utf8'))['new_lone_alias_refusals']
overlap = sorted(newset & {r['input'] for r in prior19})
assert overlap == ['Pegylated interferon alfa-2a']
(out / 'historical_alias_set_check.json').write_text(json.dumps(dict(original_loss_set=len(prior19), still_lost=overlap, all_19_non_M5_S2_restored=True), indent=2), encoding='utf8')
executions = {f: read(f) for f in ['round9_execution.json', 'replay_execution.json', 'supplement_execution.json', 'final_replay_execution.json', 'additional_execution.json', 'completion_execution.json']}
assert all(r['exit_code'] == 0 for rows in executions.values() for r in rows)
assert all(r['exit_code'] == 0 for r in read('m1_exact/execution.json')['scripts'])
with socket.socket() as sock: closed = sock.connect_ex(('127.0.0.1', 8921)) != 0
manifest = read('reuse_manifest.json')
assert all(hashlib.sha256((root / r['source']).read_bytes()).hexdigest() == r['source_sha256'] for r in manifest)
assert closed and not read('adapted_names_m5_summary.json')['cache_errors']
leafs = sorted(set(r['script'] for rows in executions.values() for r in rows if not Path(r['script']).name.startswith('run_') and r['script'] != 'compare_replays.py') | {'m1_exact/' + r['script'] for r in read('m1_exact/execution.json')['scripts']} | {'joined_label_probe.py'})
head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()
final = dict(head=head, all_runners_exit_zero=True, owned_port_closed=closed, reused_source_hashes_unchanged=True, reused_script_count=len(manifest), executed_reused_leaf_count=len(leafs), executed_reused_leafs=leafs, historical_matrix_rows=len(matrix), alias_keys_checked=7511, alias_anomalies=318, formerly_linked_without_current_drug=69, newly_lost_aliases=[], recovered_aliases=['rad001c'], cache_errors=[], changed_evidence_adjudication=adjudication)
(out / 'worker_final_checks.json').write_text(json.dumps(final, indent=2), encoding='utf8')
body = f'''# Round 14 historical name-resolution verification

Reviewed HEAD `{head}`. Principal originally reported blocking name inputs M1-M13 are **FIXED for their exact spellings**. The supplementary M13 `A33124I` example is **NOT FIXED**. This historical result does not establish overall approval; the fresh-attack worker separately confirmed current originator leaks.

## Execution and evidence

- **{len(manifest)} scripts reused; {len(leafs)} leaf reproductions executed**, all runner exits zero. Outputs are under m14/names; exact input inventories and historical read paths remain intact. Port **8921** is closed. [Manifest](reuse_manifest.json), [cumulative execution](round9_execution.json), [additional](additional_execution.json), [completion](completion_execution.json), [checks](worker_final_checks.json).
- Original **113-case / 7,511-key** sweep: **318** old-method differences and **69** previously linked aliases without a current Drug. These are diagnostic counts. Versus M13: **zero new losses; rad001c alone recovered**. [Sweep](names_m5_attack.json), [summary](names_m5_summary.json), [loss sets](new_alias_losses.json).
- Frozen **1,648-question** counterfactual: **68 identical / 1,556 metadata-only / 24 semantic / zero errors**, unchanged. [QA](adapted_frozen_qa_relink_sweep.json).
- **39-case** matrix only mismatches accepted M5-S2; **26** literal M6/M7 controls pass; all **19** non-M5-S2 historic alias losses remain restored. [Matrix](focused_matrix.json), [controls](historical_focus.json), [aliases](historical_alias_set_check.json).
- Replayed M9 **146 inputs / 16 QA**, M10 **1,224 inputs + 35 focus cases**, M11 **26 probes + 12 literal cases**, M12 **41 focused cases**, M13 **nine joined-label stage cases**. [M9](m9_attacks/probe_results.json), [M10](m10_attacks/probe_results.json), [focus](m10_attacks/focus_results.json), [M11](m11_attacks/key_equivalence_results.json), [M11 exact](m11_exact.json), [M12](m12_attacks/focused_results.json), [M13](joined_label_probe.json).
- Fresh evidence for **62 inherited findings** was compared with M13, retaining identities, maps, evidence and refusal existence. Only rad001c recovery changes results. The four changed aggregate lists lose exactly rad001c; all retained rows are semantically equal. [Comparison](replay_comparison.json), [adjudication](worker_final_checks.json).

## Individual historical dispositions

M2 has no completed report; partial name cases are covered by M2b's cumulative reproductions. Other workers cover DB, UI, cost and root HTTP evidence.

| Round / finding | Status | Fresh evidence |
|---|---|---|
'''
for r in matrix:
    body += f"| {r['round']} {r['finding'].replace('|', '&#124;')} | **{r['status']}** | {r['detail']} [Evidence]({r['evidence']}). |\n"
body += '''
## Latest repair and remaining limits

The same-drug isotope-edge rule (`src/query.py:324-338`) catches `89ZrDFO-daratumumab`: key starts with two-letter-element `89zr` and ends with same-drug key `daratumumab`. The inside-name scan (`288-297`) still catches M12 split-symbol forms. `_marked` emits Refused (`470-479`), and `_whole_name` cannot override it (`342-349`). The main M13 cases have no centre or qualified QA evidence; separate osimertinib remains available. [Stages](joined_label_probe.json).

`rad001c` and `RAD001C` now return EVEROLIMUS / CHEMBL1908360, nine trials; HEAD^ refuses both. No new lone-alias loss occurred. `A33124I` still maps to ADAKITUG and remains explicitly NOT FIXED. [Recovery](new_alias_regression.json), [remaining example](../attacks/fresh_results.json).

Seven original QA demos retain evidence counts **12, 12, 11, 1, 12, 0, 0**. Six responses equal the bfcb83d-linker counterfactual; Mvasi differs only in refusal metadata. This is a same-data method counterfactual, not a historical deployment reconstruction. [Demos](names_demo_results.json).

No tracked/application file changed. Historical source hashes are unchanged. Bytecode is disabled; TMP/TEMP/TMPDIR are within m14/names. Direct fixtures are read-only or in-memory; HTTP scripts start unmodified CLI servers and terminate only their own processes. The root report contains whole-workspace integrity and the verdict.

```text
python -B audit_evidence_claims/m14/names/run_round9.py
python -B audit_evidence_claims/m14/names/run_additional.py
python -B audit_evidence_claims/m14/names/run_completion.py
python -B audit_evidence_claims/m14/names/joined_label_probe.py
python -B audit_evidence_claims/m14/names/build_current_summary.py
```

Run port-sharing wrappers sequentially. The summary also reads the independently replayed m13 attack output in m14/attacks.
'''
(out / 'FINDINGS.md').write_text(body, encoding='utf8')
print(json.dumps(final, indent=2))
