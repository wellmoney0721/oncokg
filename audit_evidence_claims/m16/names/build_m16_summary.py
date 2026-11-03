"""Assess fresh historical replays; reads history, writes only its own m16 folder."""
from pathlib import Path
import hashlib, json, socket, subprocess

root = Path.cwd()
out = Path(__file__).resolve().parent
prior = root / 'audit_evidence_claims/m15/names'

def read(name):
    return json.loads((out / name).read_text(encoding='utf8'))

def old(name):
    return json.loads((prior / name).read_text(encoding='utf8'))

def safe_refusal(row):
    obj = row.get('current', row)
    return bool(obj['map'].get('refused')) and not obj['map'].get('center') and not obj['trial_qa']['evidence'] and not obj['sponsor_qa']['evidence']

edge = {r['text']: r for r in read('m14_exact/edge_results.json')['cases']}
for text in ['A33124I', '3HVINBLASTINE', '3HVinblastine', '3Hvinblastine', '3hvinblastine', '89Zrpanitumumab-PET-CT', '89ZrpanitumumabPETCT', '89zrpanitumumabpetct', '89Zrpanitumumab PET CT']:
    assert safe_refusal(edge[text]), text
targeted = {r['text']: r for r in read('m15_exact/targeted_results.json')['cases']}
for text in ['89-ZrDFO trastuzumab', 'trastuzumab DFO89-Zr', '89Z.rDFO trastuzumab', 'trastuzumab DFO89Z.r', '3hvinblastine', 'A33124i', 'a33124i']:
    assert safe_refusal(targeted[text]), text
for text in ['3hvinblastine, osimertinib', '89Z.rDFO trastuzumab, osimertinib']:
    row = targeted[text]['current']
    assert row['map']['center']['id'] == 'CHEMBL3353410'
    assert any(r['type'] == 'Refused' for r in row['public_linker'])

extras = {r['text']: r for r in read('m14_supplement.json')['cases']}
for text in ['89ZRDFO trastuzumab', '89zrDFO trastuzumab']:
    assert safe_refusal(extras[text]), text
for text in ['HLX04', 'HLX-04', 'HLX04-O', 'BAT1706', 'SB8', 'MB02', 'FKB238', 'BI 695502']:
    assert extras[text]['map']['center']['id'] == 'CHEMBL1201583'

distance = {r['text']: r for r in read('m12_attacks/focused_results.json')['cases']}
distance_cases = ['trastuzumab labelled with [89Zr]', 'trastuzumab labeled with 89Zr', 'trastuzumab labelled 89Zr', 'trastuzumab (labelled with 89Zr)', '89Zr labelled trastuzumab', '[89Z.r]-labelled trastuzumab', '[89Z_r] labelled trastuzumab', '[89Z.r] labelled trastuzumab']
assert all(safe_refusal(distance[text]) for text in distance_cases)
for text, did, count in [('b.i.o.similar bevacizumab', 'CHEMBL1201583', 12), ('lip.osomal doxorubicin', 'CHEMBL53463', 3)]:
    row = distance[text]['current']
    assert row['map']['center']['id'] == did and not row['map'].get('refused')
    assert len(row['trial_qa']['evidence']) == len(row['sponsor_qa']['evidence']) == count
assert edge['89zr-panitumumab-pet/ct']['current']['map'] == {'not_found': '89zr-panitumumab-pet/ct'}
assert [r['finding'] for r in read('focused_matrix.json') if not r['matches_expectation']] == ['M5-S2-known']
assert all(r['status'] == 'FIXED' for r in read('historical_focus.json')['cases'])
assert all(r['actual_center'] == r['expected_center'] for r in read('m11_exact.json'))
qa = read('adapted_frozen_qa_relink_sweep.json')['summary']
assert qa == dict(questions=1648, identical=68, entities_only=1556, semantic_changes=24, errors=0)

current = read('names_m5_summary.json')
before_set = {r['input'] for r in old('names_m5_summary.json')['new_lone_alias_refusals']}
after_set = {r['input'] for r in current['new_lone_alias_refusals']}
assert after_set - before_set == {'GS-11CAL-101', '3en3hg4wsw'}
assert not before_set - after_set
assert current['aliases_checked'] == 7511 and current['alias_anomalies'] == 320
assert len(after_set) == 71
assert not read('adapted_names_m5_summary.json')['cache_errors']
losses = dict(description='Current versus M15 raw stored-alias loss set, not a defect count.', new_losses=sorted(after_set-before_set), recovered=sorted(before_set-after_set), current_loss_count=len(after_set), previous_loss_count=len(before_set), both_new_losses_user_accepted=True)
(out / 'new_alias_losses.json').write_text(json.dumps(losses, indent=2), encoding='utf8')
prior19 = json.loads((root / 'audit_evidence_claims/m7/names/names_m5_summary.json').read_text(encoding='utf8'))['new_lone_alias_refusals']
overlap = sorted(after_set & {r['input'] for r in prior19})
assert overlap == ['Pegylated interferon alfa-2a']
(out / 'historical_alias_set_check.json').write_text(json.dumps(dict(original_loss_set=len(prior19), still_lost=overlap, all_19_non_M5_S2_restored=True), indent=2), encoding='utf8')

matrix = old('historical_name_dispositions.json')
for r in matrix:
    if r['finding'].startswith('M12 supplementary previously unpromoted'):
        r.update(status='FIXED', detail='All old Zr-89 labelled/labeled-distance examples now refuse with no originator centre and zero qualified trial/sponsor evidence. Comma-separated osimertinib survives.', evidence='m12_attacks/focused_results.json')
    if r['finding'].startswith('M13 supplementary A33124I'):
        r.update(detail='A33124I and A33 124i refuse with no centre and zero qualified trial/sponsor evidence; also fixed in HEAD^.', evidence='m14_exact/fresh_results.json')
    if r['finding'].startswith('M14-B1 supplementary lower-case'):
        r.update(status='FIXED', detail='The exact prior 3hvinblastine now refuses with no centre and zero trial/sponsor evidence; its lower-case A33124i and a33124i corroborations also refuse.', evidence='m15_exact/targeted_results.json')
    if r['finding'].startswith('M14 supplementary neighbouring'):
        r.update(status='FIXED', detail='89ZRDFO trastuzumab and 89zrDFO trastuzumab now refuse with no centre and zero trial/sponsor evidence; properly cased control also refuses.', evidence='m14_supplement.json')
matrix += [
    dict(round='M12/M15 supplementary', finding='Fragmented qualifier b.i.o.similar bevacizumab', status='NOT FIXED', detail='The exact old supplementary input still draws BEVACIZUMAB / CHEMBL1201583 (122 live trials) and supplies 12 trial / 12 sponsor QA rows, without a refusal. Preserved as the previously recorded supplementary gap, not a newly discovered family.', evidence='m12_attacks/focused_results.json'),
    dict(round='M12/M15 supplementary', finding='Fragmented qualifier lip.osomal doxorubicin', status='NOT FIXED', detail='The exact old supplementary input still draws DOXORUBICIN / CHEMBL53463 (3 live trials) and supplies 3 trial / 3 sponsor QA rows, without a refusal. Preserved as the previously recorded supplementary gap, not a newly discovered family.', evidence='m12_attacks/focused_results.json'),
    dict(round='M14/M15 supplementary', finding='Slash PET/CT presentation: 89zr-panitumumab-pet/ct', status='NOT FIXED', detail='The exact slash-bearing input returns not_found with no centre, no refusal message and zero trial/sponsor evidence. This remains a should-fix distinction in failure presentation, not an originator leak; the glued/hyphen PETCT blocker inputs explicitly refuse.', evidence='m14_exact/edge_results.json'),
    dict(round='M15', finding='M15-B1 punctuation inside adjacent isotope/chelator', status='FIXED', detail='89-ZrDFO trastuzumab, trastuzumab DFO89-Zr, 89Z.rDFO trastuzumab, and trastuzumab DFO89Z.r refuse with zero originator map/trial/sponsor results. Separate comma osimertinib survives.', evidence='m15_exact/targeted_results.json'),
    dict(round='M15', finding='M15-B2 lower-case stored tracer; A33 corroboration', status='FIXED', detail='3hvinblastine, A33124i, and a33124i refuse; bare VINBLASTINE and ADAKITUG remain available. Comma-separated osimertinib survives the refused lower-case vinblastine tracer.', evidence='m15_exact/targeted_results.json'),
    dict(round='M15 repair note / user', finding='GS-11CAL-101 known over-refusal', status='NOT FIXED', detail='The raw stored-alias sweep newly refuses GS-11CAL-101. Explicitly user-accepted, nonblocking; no other unexpected new raw alias loss.', evidence='names_m5_summary.json'),
    dict(round='M15 repair note / user', finding='3en3hg4wsw known over-refusal', status='NOT FIXED', detail='The raw stored-alias sweep newly refuses 3en3hg4wsw. Explicitly user-accepted, nonblocking; no other unexpected new raw alias loss.', evidence='names_m5_summary.json'),
]
(out / 'historical_name_dispositions.json').write_text(json.dumps(matrix, ensure_ascii=False, indent=2), encoding='utf8')

comparison = read('replay_comparison.json')
assert not any(r.get('missing') for r in comparison['files'])
changed = [r for r in comparison['files'] if not r['normalized_equal']]
executions = {f: read(f) for f in ['round9_execution.json', 'replay_execution.json', 'supplement_execution.json', 'final_replay_execution.json', 'additional_execution.json', 'completion_execution.json']}
assert len(executions['round9_execution.json']) == 12
assert all(r['exit_code'] == 0 for rows in executions.values() for r in rows)
assert all(r['exit_code'] == 0 for r in read('m1_exact/execution.json')['scripts'])
closed = {}
for port in [8951, 8952]:
    with socket.socket() as sock:
        closed[str(port)] = sock.connect_ex(('127.0.0.1', port)) != 0
assert all(closed.values())
manifest = read('reuse_manifest.json')
assert all(hashlib.sha256((root / r['source']).read_bytes()).hexdigest() == r['source_sha256'] for r in manifest)
leafs = sorted(set(r['script'] for rows in executions.values() for r in rows if not Path(r['script']).name.startswith('run_') and r['script'] != 'compare_replays.py') | {'m1_exact/' + r['script'] for r in read('m1_exact/execution.json')['scripts']} | {'joined_label_probe.py', 'm14_exact/edge_probe.py', 'm14_exact/fresh.py', 'm14_supplement.py', 'm15_exact/targeted_probe.py'})
assert all((out / r['evidence']).exists() for r in matrix)
head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()
final = dict(head=head, all_runners_exit_zero=True, owned_ports_closed=closed, reused_source_hashes_unchanged=True, copied_reused_script_count=len(manifest), executed_reused_leaf_count=len(leafs), executed_reused_leafs=leafs, historical_matrix_rows=len(matrix), historical_fixed=sum(r['status']=='FIXED' for r in matrix), historical_not_fixed=sum(r['status']=='NOT FIXED' for r in matrix), alias_keys_checked=7511, alias_anomalies=320, formerly_linked_without_current_drug=71, newly_lost_aliases=losses['new_losses'], recovered_aliases=[], cache_errors=[], frozen_counterfactual=qa, changed_historical_evidence=[dict(file=r['file'], difference_count=len(r['differences'])) for r in changed])
(out / 'worker_final_checks.json').write_text(json.dumps(final, indent=2), encoding='utf8')

body = f'''# Round 16 historical name-resolution verification

Reviewed HEAD `{head}`. **All exact previously promoted name-resolution blockers from M1 through M15 are FIXED.** M15's split neighbouring label, lower-case stored tracer, and A33 lower-case corroborations now refuse. The old M12 descriptive label-distance and M14 neighbouring-case supplementals also refuse. Earlier nonblocking limits and explicitly accepted over-refusals remain individually marked below. This is a historical-verification contribution, not the overall audit verdict.

## Execution and evidence

- **{len(manifest)} original scripts copied/reused; {len(leafs)} reused leaf reproductions executed.** Every runner exits zero. Outputs and temporary paths are inside m16/names; original source hashes match the manifest. Owned ports **8951 and 8952 are closed**. [Manifest](reuse_manifest.json), [checks](worker_final_checks.json), [main](round9_execution.json), [additional](additional_execution.json), [completion](completion_execution.json).
- Raw **113-case / 7,511-key** sweep: **320** differences from the old method, **71** prior linked aliases without a current Drug. The only new losses versus M15 are **GS-11CAL-101 and 3en3hg4wsw**, both explicitly accepted in this round's brief. No unexpected new raw-alias loss; no recovered alias. These diagnostic totals are not defect counts. [Sweep](names_m5_attack.json), [summary](names_m5_summary.json), [loss sets](new_alias_losses.json).
- Meaningful adapted frozen **1,648-question** no-relink counterfactual remains **68 identical / 1,556 metadata-only / 24 semantic / zero errors**. The old source-replacement wrapper that no longer alters current logic reports 1,648 identical and is not interpreted as the original comparison. [Adapted](adapted_frozen_qa_relink_sweep.json), [legacy](frozen_qa_relink_sweep.json).
- **39-case** matrix only mismatches the accepted M5-S2; **26** literal M6/M7 controls pass; all **19** old non-M5-S2 alias losses remain restored. [Matrix](focused_matrix.json), [controls](historical_focus.json), [aliases](historical_alias_set_check.json).
- Exact reused inventories include M9 **146 inputs / 16 QA**, M10 **1,224 inputs + 35 focus cases**, M11 **26 probes + 12 literal cases**, M12 **41 focus cases**, M13 **nine joined-label cases**, M14 **29 edge + 27 inherited stage cases + nine neighbouring supplementals**, and M15 **29 targeted stage cases**. Eight user-listed bevacizumab development codes remain the known accepted dictionary limitation. [M9](m9_attacks/probe_results.json), [M10](m10_attacks/probe_results.json), [M11](m11_exact.json), [M12](m12_attacks/focused_results.json), [M13](joined_label_probe.json), [M14](m14_exact/edge_results.json), [M15](m15_exact/targeted_results.json).
- All evidence files behind M15's 69-row naming table were freshly replayed and compared, retaining identity, map values, evidence and refusal existence. Changes are the repaired isotope forms, the accepted same-item refusal rule, and the two known raw-alias losses. [Comparison](replay_comparison.json).

## Individual historical dispositions

M2 has no completed report; its partial cases are covered by cumulative M2b scripts. DB, UI, server and performance findings are handled by the root/other reviewer. The table contains **{len(matrix)} rows: {final['historical_fixed']} FIXED, {final['historical_not_fixed']} NOT FIXED**. NOT FIXED includes recorded nonblocking limitations and user-accepted exceptions; it does not itself assign blocker severity.

| Round / finding | Status | Fresh evidence |
|---|---|---|
'''
for r in matrix:
    body += f"| {r['round']} {r['finding'].replace('|', '&#124;')} | **{r['status']}** | {r['detail']} [Evidence]({r['evidence']}). |\n"
body += '''
## Interpretation and limits

Same-list-item changes are expected under this round's explicit fail-closed policy: `osimertinib with [89Zr] trastuzumab` now refuses both; a comma-separated osimertinib still survives. Previously promoted repairs remain intact. The old non-parenthetical `doxorubicin in nanoparticle and liposomal formulations` listing-word issue and prefixed comma-containing names remain at their prior nonblocking classification; they are not silently counted fixed. The original lowercase IDs / investigator-name lookup limitation also remains. The exact old `b.i.o.similar bevacizumab` and `lip.osomal doxorubicin` fragmented-qualifier supplements still select the originator and are explicitly NOT FIXED above. The slash-bearing `89zr-panitumumab-pet/ct` control remains not_found with no centre; it must not be reported as an explicit refusal.

Seven original QA demos retain **12, 12, 11, 1, 12, 0, 0** evidence rows. Six responses equal the bfcb83d-linker counterfactual; Mvasi differs only in refusal metadata. [Demos](names_demo_results.json). Counterfactuals replace only the stated query methods/modules with the same current app/data; they do not reconstruct historical deployments.

No application source or tracked file was modified. Scratch output, logs and temporary directories remain under m16/names; bytecode is disabled. Mutation fixtures use in-memory copies. HTTP probes launch the unmodified application and terminate only their own processes. No model was called. Root verification owns repository-wide integrity and the final verdict.
'''
(out / 'FINDINGS.md').write_text(body, encoding='utf8')
print(json.dumps(final, indent=2))
