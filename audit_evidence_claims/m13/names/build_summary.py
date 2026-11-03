"""Verify current replay evidence before carrying historical dispositions forward."""
from pathlib import Path
import hashlib, json, socket, subprocess

root = Path.cwd()
out = Path(__file__).resolve().parent
prior = root / 'audit_evidence_claims/m12/names'
def read(name):
    return json.loads((out / name).read_text(encoding='utf8'))

comparison = read('replay_comparison.json')
assert all(not r.get('missing') and r['normalized_equal'] for r in comparison['files']), comparison
matrix = json.loads((prior / 'historical_name_dispositions.json').read_text(encoding='utf8'))
assert [r['finding'] for r in read('focused_matrix.json') if not r['matches_expectation']] == ['M5-S2-known']
assert all(r['status'] == 'FIXED' for r in read('historical_focus.json')['cases'])
assert all(r['actual_center'] == r['expected_center'] for r in read('m11_exact.json'))
assert all(not q['evidence'] for r in read('m11_exact.json') if not r['expected_center'] for q in r['qa'])
assert read('adapted_frozen_qa_relink_sweep.json')['summary'] == dict(questions=1648, identical=68, entities_only=1556, semantic_changes=24, errors=0)

m12 = read('m12_attacks/focused_results.json')['cases']
by_text = {r['text']: r for r in m12}
fixed_inputs = ['[89Z.r]-DFO-daratumumab', '89Z_r-dfo-daratumumab', '89Z.r-dfo-daratumumab', '89Z.r dfo daratumumab', '89Z.r-dfo daratumumab']
for text in fixed_inputs:
    r = by_text[text]['current']
    assert not r['map'].get('center') and r['map'].get('refused'), text
    assert not r['trial_qa']['evidence'] and not r['sponsor_qa']['evidence'], text
assert by_text['[89Z.r]-DFO-daratumumab, osimertinib']['current']['map']['center']['id'] == 'CHEMBL3353410'
assert by_text['daratumumab']['current']['map']['center']['id'] == 'CHEMBL1743007'
matrix.append(dict(round='M12', finding='M12-B1 split symbol inside chelator-bearing stored alias', status='FIXED', detail='Exact reported [89Z.r]-DFO-daratumumab and 89Z_r-dfo-daratumumab, plus three alternate old cases, refuse with zero qualified trial/sponsor QA evidence. Separate osimertinib survives; bare daratumumab maps correctly.', evidence='m12_attacks/focused_results.json'))

alias = {r['text']: r for r in read('new_alias_regression.json')['cases']}
for text in ['rad001c', 'RAD001C']:
    assert not alias[text]['current']['map'].get('center') and alias[text]['current']['map'].get('refused')
    assert not alias[text]['previous']['map'].get('center') and alias[text]['previous']['map'].get('refused')
for text in ['rad', 'RAD001', 'EVEROLIMUS', 'CHEMBL1908360']:
    assert alias[text]['current']['map']['center']['id'] == 'CHEMBL1908360'
matrix.append(dict(round='M12', finding='M12-S1 rad001c / RAD001C stored-alias over-refusal', status='NOT FIXED', detail='Still refuses with no centre, as in M12. Current and HEAD^ agree. rad, RAD001, EVEROLIMUS and exact ID remain available. This is inherited and nonblocking.', evidence='new_alias_regression.json'))
supplement = ['trastuzumab labelled with [89Zr]', 'trastuzumab labeled with 89Zr', '[89Z.r]-labelled trastuzumab']
for text in supplement:
    assert by_text[text]['current']['map'].get('center', {}).get('id') == by_text[text]['previous']['map'].get('center', {}).get('id') == 'CHEMBL1201585'
matrix.append(dict(round='M12', finding='M12 supplementary previously unpromoted descriptive label-distance inputs', status='NOT FIXED', detail='The old labelled/labeled-distance forms still draw TRASTUZUMAB and match the HEAD^ result. Retained separately from the new joined-chelator blocker, consistent with prior classification.', evidence='m12_attacks/focused_results.json'))
(out / 'historical_name_dispositions.json').write_text(json.dumps(matrix, ensure_ascii=False, indent=2), encoding='utf8')

current = read('names_m5_summary.json')
old = json.loads((prior / 'names_m5_summary.json').read_text(encoding='utf8'))
oldset = {r['input'] for r in old['new_lone_alias_refusals']}
newset = {r['input'] for r in current['new_lone_alias_refusals']}
assert current['aliases_checked'] == 7511 and current['alias_anomalies'] == 319 and len(newset) == 70
assert newset == oldset
(out / 'new_alias_losses.json').write_text(json.dumps(dict(description='Current versus M12 loss-set comparison; not a defect count.', new_losses=sorted(newset-oldset), recovered=sorted(oldset-newset), unchanged_loss_count=len(newset)), indent=2), encoding='utf8')
prior19 = json.loads((root / 'audit_evidence_claims/m7/names/names_m5_summary.json').read_text(encoding='utf8'))['new_lone_alias_refusals']
overlap = sorted(newset & {r['input'] for r in prior19})
assert overlap == ['Pegylated interferon alfa-2a']
alias_check = dict(original_loss_set=len(prior19), still_lost=overlap, all_19_non_M5_S2_restored=True)
(out / 'historical_alias_set_check.json').write_text(json.dumps(alias_check, indent=2), encoding='utf8')
executions = {f: read(f) for f in ['round9_execution.json', 'replay_execution.json', 'supplement_execution.json', 'final_replay_execution.json', 'additional_execution.json', 'completion_execution.json']}
assert all(r['exit_code'] == 0 for rows in executions.values() for r in rows)
assert all(r['exit_code'] == 0 for r in read('m1_exact/execution.json')['scripts'])
with socket.socket() as sock:
    closed = sock.connect_ex(('127.0.0.1', 19300)) != 0
manifest = read('reuse_manifest.json')
hashes_ok = all(hashlib.sha256((root / r['source']).read_bytes()).hexdigest() == r['source_sha256'] for r in manifest)
assert closed and hashes_ok and not read('adapted_names_m5_summary.json')['cache_errors']
leafs = sorted(set(r['script'] for rows in executions.values() for r in rows if not Path(r['script']).name.startswith('run_') and r['script'] != 'compare_replays.py') | {'m1_exact/' + r['script'] for r in read('m1_exact/execution.json')['scripts']})
head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()
checks = dict(head=head, all_runners_exit_zero=True, exact_m1_scripts_exit_zero=True, port_19300_closed=closed, reused_source_hashes_unchanged=hashes_ok, reused_script_count=len(manifest), executed_reused_leaf_count=len(leafs), executed_reused_leafs=leafs, historical_matrix_rows=len(matrix), alias_keys_checked=7511, alias_anomalies=319, formerly_linked_without_current_drug=70, newly_lost_aliases=[], cache_errors=[], old_alias_set=alias_check)
(out / 'worker_final_checks.json').write_text(json.dumps(checks, indent=2), encoding='utf8')

body = f'''# Round 13 historical name-resolution verification

Reviewed HEAD `{head}`. **Every originally reported blocking name reproduction M1–M12 is FIXED for its exact input.** Retained over-refusals and previously recorded policy limitations are individually classified below. This does not imply the overall map is safe: a new joined-chelator originator leak was independently found and handed to the root/attack workers.

## Execution and evidence

- **{len(manifest)} reused scripts** copied with current-run outputs relocated to m13/names and owned HTTP port **19300**; historical read paths and exact input inventories retained. **{len(leafs)} reused leaf reproduction scripts executed**, excluding wrapper/comparison utilities, all exit 0. [Manifest](reuse_manifest.json), [core](replay_execution.json), [supplement](supplement_execution.json), [cumulative runner](round9_execution.json), [original M1](m1_exact/execution.json), [additional](additional_execution.json), [final HTTP](final_replay_execution.json), [completion](completion_execution.json).
- Original **113-case / 7,511-key** sweep: **319** changes against its declared old-method counterfactual, **70** formerly linked aliases without a current Drug. Counts and loss set equal M12: **zero newly lost aliases**. These are diagnostic counts, not 70 defects. [Sweep](names_m5_attack.json), [summary](names_m5_summary.json), [current/M12 loss sets](new_alias_losses.json), [cache-safe sweep](adapted_names_m5_summary.json).
- Frozen no-relink counterfactual: **1,648 exact questions; 68 identical / 1,556 metadata-only / 24 semantic / zero errors**, identical to M12. The adapted script changes current `_link`; public-wrapper-only historical counterfactuals are retained as provenance. [Evidence](adapted_frozen_qa_relink_sweep.json).
- **39-case earlier matrix:** only the explicitly accepted M5-S2 over-refusal differs from its old expectation. **26 M6/M7 literal controls pass**; all **19 non-M5-S2 old alias losses remain restored**. [Matrix](focused_matrix.json), [literal controls](historical_focus.json), [restored set](historical_alias_set_check.json).
- Reused exact M9 matrix: **146 inputs / 16 QA**; M10 probe: **1,224 inputs**, plus **35-case focus**; M11 original probe: **26 inputs**, plus **12 literal/preserved-osimertinib cases**. M12 original focused attack: **41 inputs**, comparing current with the actual HEAD^ query module on the same current app/rules/database. [M9](m9_attacks/probe_results.json), [M10](m10_attacks/probe_results.json), [M10 focus](m10_attacks/focus_results.json), [M11](m11_attacks/key_equivalence_results.json), [M11 exact](m11_exact.json), [M12](m12_attacks/focused_results.json).
- Historical name HTTP scripts use the unmodified CLI server and closed owned port 19300 after completion. M7 44 / M9 50 / M9-S1 10 responses remain HTTP200. [M7](m7_attacks/http_results.json), [M9](m9_attacks/http_results.json), [M9-S1](new_alias_confirmation.json), [final checks](worker_final_checks.json).
- Every evidence file referenced by the 59 inherited name-finding rows is semantically equal to M12 after ignoring declared counterfactual outputs, refusal wording, timing and process metadata. Positive centres, graph/evidence values and refusal existence are retained in this comparison. This validates carrying the dispositions forward; it is not an exhaustive safety proof. [Comparison and ignored fields](replay_comparison.json).

## Individual historical dispositions

M2 has no completed report; its partial name cases are represented in M2b's cumulative scripts. DB, UI, cost and full HTTP confirmation are covered by other workers.

| Round / finding | Status | Current evidence |
|---|---|---|
'''
for r in matrix:
    body += f"| {r['round']} {r['finding'].replace('|', '&#124;')} | **{r['status']}** | {r['detail']} [Evidence]({r['evidence']}). |\n"
body += '''
## M12 repair and retained loss

The newly added loop joins every letters-and-digits word run inside a consumed name up to six characters (`src/query.py:259-267`), then feeds the result to the isotope predicate (`287-289`). `[89Z.r]-DFO-daratumumab` now contains the glued run `89Zr`, so the matched drug is refused at `426-435`; `_whole_name` cannot override it (`304-305`). The exact reported M12 variants have no centre or qualified QA evidence. [Stage evidence](m12_attacks/focused_results.json).

`rad001c` remains a nonblocking inherited stored-alias loss: both current and HEAD^ refuse. The key-splitting rule sees same-drug alias `rad` plus isotope-shaped `001c` (`src/query.py:291-295`); `rad`, `RAD001`, EVEROLIMUS and its ID still work. No newly lost unambiguous stored alias was observed in the 7,511-key replay. [Stages and controls](new_alias_regression.json).

## Independently discovered new candidate

`89ZrDFO-daratumumab` and `89zrdfodaratumumab` have the same canonical key as the stored/refused `89zr-dfo-daratumumab`, yet map to **DARATUMUMAB / CHEMBL1743007**, with **2 trial + 2 sponsor QA rows**. The raw resolver is ALIAS, resolver veto `{}`, item/public linkers emit Drug without Refused, and whole-name shortcut is `None`. The isotope is now inside one longer alnum word (`89ZrDFO`), so joining whole words does not extract it; the separate key-prefix check still requires missing same-drug remainder `dfodaratumumab`. `[89ZrDFO]-daratumumab`, `89zrdfo daratumumab`, and a separate-osimertinib variant also leak. Refused controls and bare daratumumab behave as expected. This candidate was independently communicated to the root/attack workers for actual HTTP confirmation. [Nine-case independent stage/QA evidence](joined_label_probe.json).

## Demos, integrity and reproduction

All seven original QA demos retain counts **12, 12, 11, 1, 12, 0, 0**. Six full responses still equal bfcb83d; Mvasi differs only in refusal metadata. [Demo comparison](names_demo_results.json). Full page demos are in the separate DB/UI worker's evidence.

No tracked file or application code was changed. Historical source hashes are unchanged; owned port 19300 is closed. Outputs and TMP/TEMP/TMPDIR stay under m13/names, bytecode is disabled. No model was called. Counterfactuals replace only their stated query methods/module and retain current app/rules/data; they are not historical deployment reconstructions. The KOA/KhOpenApi original-versus-modified-code requirement is conditional on application edits; this audit makes none.

```text
python -B audit_evidence_claims/m13/names/run_round9.py
python -B audit_evidence_claims/m13/names/run_completion.py
python -B audit_evidence_claims/m13/names/joined_label_probe.py
python -B audit_evidence_claims/m13/names/build_summary.py
```

Run port-sharing wrappers sequentially. The root report decides the overall verdict using independent HTTP and DB/UI evidence.
'''
(out / 'FINDINGS.md').write_text(body, encoding='utf8')
print(json.dumps(checks, indent=2))
