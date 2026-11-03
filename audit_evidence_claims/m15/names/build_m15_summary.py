"""Verify current cumulative name replays and preserve every prior disposition."""
from pathlib import Path
import hashlib, json, socket, subprocess

root = Path.cwd()
out = Path(__file__).resolve().parent
prior = root / 'audit_evidence_claims/m14/names'
def read(name): return json.loads((out / name).read_text(encoding='utf8'))
def old(name): return json.loads((prior / name).read_text(encoding='utf8'))

comparison = read('replay_comparison.json')
assert not any(r.get('missing') for r in comparison['files'])
changed = [r for r in comparison['files'] if not r['normalized_equal']]
assert {r['file'] for r in changed} == {'../attacks/fresh_results.json'}, changed
# The original M13 A33124I case is the only semantic change in this historical comparison.
assert all('/cases/14/' in d['path'] for r in changed for d in r['differences'])
edge = {r['text']: r for r in read('m14_exact/edge_results.json')['cases']}
for text in ['A33124I', '3HVINBLASTINE', '3Hvinblastine', '3HVinblastine', '89Zrpanitumumab-PET-CT', '89ZrpanitumumabPETCT', '89zrpanitumumabpetct', '89Zrpanitumumab PET CT']:
    r = edge[text]['current']
    assert r['map'].get('refused') and not r['map'].get('center'), text
    assert not r['trial_qa']['evidence'] and not r['sponsor_qa']['evidence'], text
low = edge['3hvinblastine']['current']
assert low['map']['center']['id'] == 'CHEMBL159'
assert len(low['trial_qa']['evidence']) == len(low['sponsor_qa']['evidence']) == 5
for text in ['3Hvinblastine, osimertinib', '89ZrpanitumumabPETCT, osimertinib']:
    r = edge[text]['current']
    assert r['map']['center']['id'] == 'CHEMBL3353410'
    assert any(x['type'] == 'Refused' for x in r['public_linker'])
assert [r['finding'] for r in read('focused_matrix.json') if not r['matches_expectation']] == ['M5-S2-known']
assert all(r['status'] == 'FIXED' for r in read('historical_focus.json')['cases'])
assert all(r['actual_center'] == r['expected_center'] for r in read('m11_exact.json'))
assert all(not q['evidence'] for r in read('m11_exact.json') if not r['expected_center'] for q in r['qa'])
assert read('adapted_frozen_qa_relink_sweep.json')['summary'] == dict(questions=1648, identical=68, entities_only=1556, semantic_changes=24, errors=0)

current = read('names_m5_summary.json')
before_set = {r['input'] for r in old('names_m5_summary.json')['new_lone_alias_refusals']}
after_set = {r['input'] for r in current['new_lone_alias_refusals']}
assert before_set == after_set and len(after_set) == 69
assert current['aliases_checked'] == 7511 and current['alias_anomalies'] == 318
assert not read('adapted_names_m5_summary.json')['cache_errors']
losses = dict(description='Current versus M14 raw stored-alias loss set; not a defect count.', new_losses=[], recovered=[], current_loss_count=69, previous_loss_count=69)
(out / 'new_alias_losses.json').write_text(json.dumps(losses, indent=2), encoding='utf8')
prior19 = json.loads((root / 'audit_evidence_claims/m7/names/names_m5_summary.json').read_text(encoding='utf8'))['new_lone_alias_refusals']
overlap = sorted(after_set & {r['input'] for r in prior19})
assert overlap == ['Pegylated interferon alfa-2a']
(out / 'historical_alias_set_check.json').write_text(json.dumps(dict(original_loss_set=len(prior19), still_lost=overlap, all_19_non_M5_S2_restored=True), indent=2), encoding='utf8')

matrix = old('historical_name_dispositions.json')
for r in matrix:
    if r['finding'].startswith('M12-S1'):
        r['detail'] = 'rad001c and RAD001C retain EVEROLIMUS / CHEMBL1908360 with 9 stored trials and 9 trial-QA rows, equal to HEAD^. rad, RAD001, EVEROLIMUS and its ID remain available.'
    if r['finding'].startswith('M13 supplementary A33124I'):
        r.update(status='FIXED', detail='A33124I now refuses, with no centre and zero trial/sponsor QA evidence; A33 124i also refuses. HEAD^ still draws ADAKITUG. The original trailing-label reproduction is repaired.', evidence='m14_exact/fresh_results.json')
matrix += [
    dict(round='M14', finding='M14-B1 uppercase one-letter element inside a consumed name', status='FIXED', detail='3HVINBLASTINE, 3HVinblastine and 3Hvinblastine now refuse with no centre and zero trial/sponsor evidence. Comma-osimertinib selects the separate CHEMBL3353410 and discloses the refusal.', evidence='m14_exact/edge_results.json'),
    dict(round='M14', finding='M14-B1 supplementary lower-case 3hvinblastine', status='NOT FIXED', detail='The exact lower-case prior example still draws VINBLASTINE / CHEMBL159 with 5 trial and 5 sponsor QA rows. Recorded separately because this round explicitly narrows one-letter own-key handling to an upper-case element; the upper-case repairs must not imply this spelling was fixed.', evidence='m14_exact/edge_results.json'),
    dict(round='M14', finding='M14-B2 isotope plus drug plus trailing PET/CT marker', status='FIXED', detail='89Zrpanitumumab-PET-CT, 89ZrpanitumumabPETCT, 89zrpanitumumabpetct and 89Zrpanitumumab PET CT now refuse with zero trial/sponsor evidence. A comma-separated osimertinib survives.', evidence='m14_exact/edge_results.json'),
    dict(round='M14', finding='M14 supplementary neighbouring fused-label casing', status='NOT FIXED', detail='89ZRDFO trastuzumab and 89zrDFO trastuzumab still draw TRASTUZUMAB. Properly cased 89ZrDFO trastuzumab refuses. This is the literal prior supplementary observation, separate from new round-15 attacks.', evidence='m14_supplement.json'),
    dict(round='M14 repair note / user', finding='Known ChEMBL bevacizumab development-code synonym limitation', status='NOT FIXED', detail='HLX04, HLX-04, HLX04-O, BAT1706, SB8, MB02, FKB238 and BI 695502 still resolve to CHEMBL1201583. Explicitly user-accepted dictionary limitation, not a map blocker.', evidence='m14_supplement.json'),
]
(out / 'historical_name_dispositions.json').write_text(json.dumps(matrix, ensure_ascii=False, indent=2), encoding='utf8')
executions = {f: read(f) for f in ['round9_execution.json', 'replay_execution.json', 'supplement_execution.json', 'final_replay_execution.json', 'additional_execution.json', 'completion_execution.json']}
assert all(r['exit_code'] == 0 for rows in executions.values() for r in rows)
assert all(r['exit_code'] == 0 for r in read('m1_exact/execution.json')['scripts'])
with socket.socket() as sock: closed = sock.connect_ex(('127.0.0.1', 8921)) != 0
manifest = read('reuse_manifest.json')
assert all(hashlib.sha256((root / r['source']).read_bytes()).hexdigest() == r['source_sha256'] for r in manifest)
assert closed
leafs = sorted(set(r['script'] for rows in executions.values() for r in rows if not Path(r['script']).name.startswith('run_') and r['script'] != 'compare_replays.py') | {'m1_exact/' + r['script'] for r in read('m1_exact/execution.json')['scripts']} | {'joined_label_probe.py', 'm14_exact/edge_probe.py', 'm14_exact/fresh.py'})
head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()
final = dict(head=head, all_runners_exit_zero=True, owned_port_closed=closed, reused_source_hashes_unchanged=True, copied_reused_script_count=len(manifest), executed_reused_leaf_count=len(leafs), executed_reused_leafs=leafs, additional_new_leafs=['m14_supplement.py'], historical_matrix_rows=len(matrix), alias_keys_checked=7511, alias_anomalies=318, formerly_linked_without_current_drug=69, newly_lost_aliases=[], recovered_aliases=[], cache_errors=[], changed_historical_evidence=[dict(file=r['file'], reason='A33124I now refuses', difference_count=len(r['differences'])) for r in changed])
(out / 'worker_final_checks.json').write_text(json.dumps(final, indent=2), encoding='utf8')
body = f'''# Round 15 historical name-resolution verification

Reviewed HEAD `{head}`. The main exact M1-M14 blocking-name reproductions are **FIXED**, including M14 uppercase `3HVINBLASTINE`, its PET/CT forms, and M13 `A33124I`. The literal lower-case `3hvinblastine` variant and prior supplementary limitations remain explicitly **NOT FIXED** below. This report supplies historical verification, not an overall approval verdict.

## Execution and evidence

- **{len(manifest)} scripts copied/reused; {len(leafs)} reused leaf reproductions executed**, plus one new wrapper replaying nine literal M14 supplemental inputs and eight user-listed dictionary codes. All runners exited zero. Port **8921** is closed. [Manifest](reuse_manifest.json), [cumulative execution](round9_execution.json), [additional](additional_execution.json), [completion](completion_execution.json), [checks](worker_final_checks.json).
- Original **113-case / 7,511-key** sweep: **318** differences from the old method and **69** previously linked aliases without a current Drug, unchanged from M14. **Zero new raw stored-alias losses**. These are diagnostic counts, not defect counts. [Sweep](names_m5_attack.json), [summary](names_m5_summary.json), [loss sets](new_alias_losses.json).
- Frozen **1,648-question** no-relink counterfactual: **68 identical / 1,556 metadata-only / 24 semantic / zero errors**, unchanged. Current-code counterfactual wrappers that no longer match the old implementation alteration report 1,648 identical; the adapted counterfactual is the meaningful original comparison. [Adapted QA](adapted_frozen_qa_relink_sweep.json), [legacy wrapper](frozen_qa_relink_sweep.json).
- **39-case** matrix only mismatches accepted M5-S2; **26** literal M6/M7 controls pass; all **19** non-M5-S2 historic alias losses remain restored. [Matrix](focused_matrix.json), [controls](historical_focus.json), [aliases](historical_alias_set_check.json).
- Replayed M9 **146 inputs / 16 QA**, M10 **1,224 inputs + 35 focus cases**, M11 **26 probes + 12 literal cases**, M12 **41 focus cases**, M13 **nine joined-label cases**, and M14's **29-case edge** and **27-case inherited** stage matrices. [M9](m9_attacks/probe_results.json), [M10](m10_attacks/probe_results.json), [M11 exact](m11_exact.json), [M12](m12_attacks/focused_results.json), [M13](joined_label_probe.json), [M14 edges](m14_exact/edge_results.json), [M14 inherited](m14_exact/fresh_results.json).
- Every evidence file underlying M14's **64-row** naming matrix was compared on identity, maps, evidence and refusal existence. Only `A33124I` changed semantically, now refusing. [Comparison](replay_comparison.json), [checks](worker_final_checks.json).

## Individual historical dispositions

M2 has no completed report; its partial name cases are covered by M2b's cumulative scripts. DB, UI, performance and root HTTP checks belong to the other review sections. Exact repaired spellings do not imply all normalized equivalents are safe.

| Round / finding | Status | Fresh evidence |
|---|---|---|
'''
for r in matrix:
    body += f"| {r['round']} {r['finding'].replace('|', '&#124;')} | **{r['status']}** | {r['detail']} [Evidence]({r['evidence']}). |\n"
body += '''
## Repair interpretation and limits

The own-key scan now allows a one-letter isotope only when the element position is upper-case (`src/query.py:345-355`), searches for a same-drug key anywhere in the remainder (`356-357`), and checks a medically enumerated closing isotope when the full key is stored (`361-363`, mass table `121-131`). This repairs the named uppercase and PET/CT forms and `A33124I`. `_marked` then emits refusal through `src/query.py:495-501`; the whole-name shortcut cannot override recorded refusal (`367-379`). All three claims are reproduced at the map and trial/sponsor QA stages.

`3hvinblastine` still selects VINBLASTINE, while `[3h]-vinblastine` refuses. This literal M14 residual remains documented; it is not silently counted as fixed by the uppercase-only requirement. `89ZRDFO trastuzumab` and `89zrDFO trastuzumab` likewise remain the earlier supplemental casing observations.

The known M5-S2, rapamycin hydroxyethyl aliases, `Trastuzumab--vcmmae conjugate`, `9-amino-20(s)-camptothecin`, `il-6ra`, and `TAK-659F` over-refusals are unchanged and explicitly nonblocking under the user's brief. The bevacizumab development-code aliases are the user's accepted data limitation.

Seven original QA demos retain counts **12, 12, 11, 1, 12, 0, 0**. Six responses equal the bfcb83d-linker counterfactual; Mvasi differs only in refusal metadata. [Demos](names_demo_results.json). These comparisons replace specified query code against the same current data, not historical deployed applications.

Only m15/names artifacts were written. Bytecode is disabled and TMP/TEMP/TMPDIR remain under m15/names. Database mutation fixtures use in-memory copies; ordinary probes use the existing read paths or explicit read-only connections. HTTP probes start the unmodified CLI and terminate their owned processes. No model was called. Historical source hashes still match the reuse manifest. Root verification owns repository-wide integrity and final verdict.
'''
(out / 'FINDINGS.md').write_text(body, encoding='utf8')
print(json.dumps(final, indent=2))
