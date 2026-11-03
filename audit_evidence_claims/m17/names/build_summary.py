"""Build evidence-bound historical name dispositions for round 17."""
from pathlib import Path
import hashlib, json, socket, subprocess

root = Path.cwd()
out = Path(__file__).resolve().parent
prior = root / 'audit_evidence_claims/m16/names'
def read(name):
    return json.loads((out / name).read_text(encoding='utf8'))
def old(name):
    return json.loads((prior / name).read_text(encoding='utf8'))
def safe_refusal(row):
    obj = row.get('current', row)
    return (bool(obj['map'].get('refused')) and not obj['map'].get('center')
            and not obj['trial_qa']['evidence'] and not obj['sponsor_qa']['evidence'])

qa = read('adapted_frozen_qa_relink_sweep.json')['summary']
assert qa == dict(questions=1648, identical=68, entities_only=1556, semantic_changes=24, errors=0)
assert [r['finding'] for r in read('focused_matrix.json') if not r['matches_expectation']] == ['M5-S2-known']
assert all(r['status'] == 'FIXED' for r in read('historical_focus.json')['cases'])
assert all(r['actual_center'] == r['expected_center'] for r in read('m11_exact.json'))
current = read('names_m5_summary.json')
before = {r['input'] for r in old('names_m5_summary.json')['new_lone_alias_refusals']}
after = {r['input'] for r in current['new_lone_alias_refusals']}
assert before == after
assert current['aliases_checked'] == 7511 and current['alias_anomalies'] == 320
assert len(after) == 71
assert not read('adapted_names_m5_summary.json')['cache_errors']
losses = dict(description='Current versus M16 raw stored-alias loss set; diagnostic counts, not defect counts.',
              new_losses=sorted(after-before), recovered=sorted(before-after),
              current_loss_count=len(after), previous_loss_count=len(before))
(out / 'new_alias_losses.json').write_text(json.dumps(losses, indent=2), encoding='utf8')
historical = json.loads((root / 'audit_evidence_claims/m7/names/names_m5_summary.json').read_text(encoding='utf8'))['new_lone_alias_refusals']
overlap = sorted(after & {r['input'] for r in historical})
assert overlap == ['Pegylated interferon alfa-2a']
(out / 'historical_alias_set_check.json').write_text(json.dumps(dict(original_loss_set=len(historical), still_lost=overlap, all_19_non_M5_S2_restored=True), indent=2), encoding='utf8')

m16 = {r['text']: r for r in read('m16_exact/new_results.json')['cases']}
exact = ['trastuzumab I-124', 'I-124 trastuzumab', 'trastuzumab I124', 'I124 trastuzumab',
         'trastuzumab i-124', 'i-124 trastuzumab', 'I-124-labelled trastuzumab',
         'trastuzumab labelled with I-124', 'trastuzumab labeled with I-124',
         'I-124-labeled trastuzumab', '[I-124] trastuzumab', 'trastuzumab [I-124]',
         'vinblastine H3', 'vinblastine H-3', '[H-3] vinblastine', 'trastuzumab I-131']
assert all(safe_refusal(m16[text]) for text in exact)
for text in ['trastuzumab I-124, osimertinib', 'osimertinib, trastuzumab I-124', 'I-124-labelled trastuzumab, osimertinib']:
    obj = m16[text]['current']
    assert obj['map']['center']['id'] == 'CHEMBL3353410'
    assert any(r['type'] == 'Refused' for r in obj['public_linker'])
for text in ['124I trastuzumab', 'trastuzumab 124I', '124I-labelled trastuzumab', 'trastuzumab labelled with 124I', 'vinblastine 3h', '3hvinblastine']:
    assert safe_refusal(m16[text])
assert m16['trastuzumab']['current']['map']['center']['id'] == 'CHEMBL1201585'
assert m16['vinblastine']['current']['map']['center']['id'] == 'CHEMBL159'

comparison = read('replay_comparison.json')
assert not any(r.get('missing') for r in comparison['files'])
changed = [r for r in comparison['files'] if not r['normalized_equal']]
assert not changed, [(r['file'], len(r.get('differences', []))) for r in changed]
matrix = old('historical_name_dispositions.json')
for row in matrix:
    if row['finding'] in ['GS-11CAL-101 known over-refusal', '3en3hg4wsw known over-refusal']:
        row['detail'] = ('The raw stored-alias sweep continues to refuse this alias. Explicitly user-accepted, '
                         'nonblocking; no new raw-alias loss versus M16.')
matrix.append(dict(round='M16', finding='M16-B1 element-first one-letter isotope within one word',
                   status='FIXED',
                   detail='I-124-labelled trastuzumab, trastuzumab labelled with I-124, I124/i-124/[I-124] variants and H3/H-3 vinblastine corroborations now refuse with no centre and zero trial/sponsor evidence. Bare controls survive; separate comma-osimertinib remains selected with refusal disclosed. All 42 original stage cases replayed.',
                   evidence='m16_exact/new_results.json'))
(out / 'historical_name_dispositions.json').write_text(json.dumps(matrix, ensure_ascii=False, indent=2), encoding='utf8')

exec_files = ['round9_execution.json', 'replay_execution.json', 'supplement_execution.json',
              'final_replay_execution.json', 'additional_execution.json',
              'completion_execution.json', 'remaining_execution.json', 'control_repair_execution.json']
executions = {f: read(f) for f in exec_files}
assert len(executions['round9_execution.json']) == 12
assert len(executions['remaining_execution.json']) == 8
assert all(r['exit_code'] == 0 for rows in executions.values() for r in rows)
assert all(r['exit_code'] == 0 for r in read('m1_exact/execution.json')['scripts'])
closed = {}
for port in [8981, 8982]:
    with socket.socket() as sock:
        closed[str(port)] = sock.connect_ex(('127.0.0.1', port)) != 0
assert all(closed.values())
manifest = read('reuse_manifest.json')
assert all(hashlib.sha256((root / r['source']).read_bytes()).hexdigest() == r['source_sha256'] for r in manifest)
assert all(hashlib.sha256((root / r['destination']).read_bytes()).hexdigest() == r['destination_sha256'] for r in manifest)
leafs = sorted(set(r['script'] for rows in executions.values() for r in rows
                   if not Path(r['script']).name.startswith('run_') and r['script'] != 'compare_replays.py')
               | {'m1_exact/' + r['script'] for r in read('m1_exact/execution.json')['scripts']})
counts = {status: sum(r['status'] == status for r in matrix) for status in ['FIXED', 'NOT FIXED']}
head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], text=True).strip()
checks = dict(head=head, scripts_reused=len(manifest), executed_leaf_reproductions=len(leafs),
              executed_leaf_scripts=leafs, historical_disposition_count=len(matrix),
              disposition_counts=counts, raw_aliases_checked=7511, raw_alias_differences=320,
              raw_alias_losses=71, new_alias_losses=[], alias_recoveries=[],
              original_19_non_M5_S2_aliases_restored=True, frozen_qa=qa,
              replay_comparison_files=len(comparison['files']), changed_replay_files=[],
              m16_original_stage_cases=len(m16), m16_exact_promoted_forms_checked=len(exact),
              source_script_hashes_unchanged=True, adapted_script_hashes_match=True,
              owned_ports_closed=closed, all_execution_exit_codes_zero=True)
(out / 'worker_final_checks.json').write_text(json.dumps(checks, indent=2), encoding='utf8')

lines = [f'''# Round 17 historical name-resolution verification

Reviewed HEAD `{head}`. **All exact previously promoted name-resolution blockers from M1 through M16 are FIXED.** M16's element-first one-letter isotope inputs now refuse, including the H3/H-3 corroborations. Status is specific to the exact reproduced input; it does not establish safety for all spellings. This is the historical-name contribution, not the overall audit verdict.

## Execution and evidence

- **{len(manifest)} original scripts copied/reused; {len(leafs)} reused leaf reproductions executed.** Every runner exits zero, source scripts remain hash-identical, and owned ports **8981/8982 are closed**. All outputs and temporary paths are under m17/names. [Provenance](reuse_manifest.json), [checks](worker_final_checks.json), [main](round9_execution.json), [remaining](remaining_execution.json).
- Raw **113-case / 7,511-key** scan: **320** differences from the frozen old method and **71** prior-linked aliases without a current Drug. **No new alias loss or recovery versus M16**. GS-11CAL-101 and 3en3hg4wsw remain accepted known over-refusals. These diagnostic totals are not defect counts. [Raw sweep](names_m5_attack.json), [summary](names_m5_summary.json), [loss comparison](new_alias_losses.json).
- Adapted frozen **1,648-question** no-relink counterfactual: **68 identical / 1,556 metadata-only / 24 semantic / zero errors**. The legacy wrapper that no longer changes current logic again reports 1,648 identical and is not treated as the meaningful counterfactual. [Adapted](adapted_frozen_qa_relink_sweep.json), [legacy](frozen_qa_relink_sweep.json).
- **39-case** focused matrix mismatches only accepted M5-S2; all **26** literal M6/M7 controls and **19** old non-M5-S2 alias restorations remain valid. [Matrix](focused_matrix.json), [controls](historical_focus.json), [alias set](historical_alias_set_check.json).
- Earlier exact inventories include M9 **146 inputs / 16 QA**, M10 **1,224 inputs + 35 focus cases**, M11 **26 probes + 12 literal cases**, M12 **41 focus cases**, M13 **nine joined-label cases**, M14 **29 edge + 27 inherited stage cases + nine supplementals**, M15 **29 targeted stage cases**, and M16 **42 original stage cases**. [M9](m9_attacks/probe_results.json), [M10](m10_attacks/probe_results.json), [M11](m11_exact.json), [M12](m12_attacks/focused_results.json), [M13](joined_label_probe.json), [M14](m14_exact/edge_results.json), [M15](m15_exact/targeted_results.json), [M16](m16_exact/new_results.json).
- Every file behind M16's 76-row historical naming table was replayed. Preserving selected identity, map values, evidence, and refusal existence, **all {len(comparison['files'])} compared files are unchanged**. M16-B1 was assessed separately with its original probe. [Comparison](replay_comparison.json).
- Replay comparison caught a scratch-only port-substitution mistake that altered the development-code control DX-8951F. The original literal was restored and its complete 29-case M15 probe rerun before the final comparison. All 59 reused scripts' changed string constants were then checked; only output/baseline paths and localhost-port text differ. [Literal validation](adaptation_literal_check.json), [corrected rerun](control_repair_execution.json). This was an audit-harness error, not a product regression.

## Individual historical dispositions

M2 had no completed report; its partial cases are covered by cumulative M2b scripts. DB/UI/server/cost findings are handled by the other reviewers. **{len(matrix)} rows: {counts['FIXED']} FIXED / {counts['NOT FIXED']} NOT FIXED.** The latter includes accepted over-refusals, availability limits and recorded supplements; status alone does not assign severity.

| Round / finding | Status | Fresh evidence |
|---|---|---|''']
for row in matrix:
    cells = [row['round'] + ' ' + row['finding'], '**' + row['status'] + '**',
             row['detail'] + ' [Evidence](' + row['evidence'] + ').']
    lines.append('| ' + ' | '.join(cell.replace('|', '\\|') for cell in cells) + ' |')
lines.append('''
## Interpretation and limits

Same-list-item refusal remains intentional: `osimertinib with [89Zr] trastuzumab` refuses both, whereas a comma-separated osimertinib survives. The lower-case ID/investigator lookup limitation, old non-parenthetical reversed qualifier and prefixed comma-containing-name issues remain individually NOT FIXED. The previously recorded `b.i.o.similar bevacizumab` and `lip.osomal doxorubicin` supplements still draw originators; the table does not silently mark these fixed or imply that they were newly discovered here. `89zr-panitumumab-pet/ct` remains not_found, distinct from an explicit refusal. The overall reviewer must apply the approval bar to remaining findings and any new attacks.

Seven original QA demos retain **12, 12, 11, 1, 12, 0, 0** evidence rows. Six responses equal the bfcb83d-linker counterfactual; Mvasi differs in refusal metadata. [Demos](names_demo_results.json). Historical counterfactuals replace only their stated query methods/modules against current app/data, not a complete historical deployment. Fixture changes use in-memory database copies. No model was called.

The M16-B1 code path now recognizes one-letter element-first isotope tokens at `src/query.py:155-168`, and `_marked` consumes the cached item check at `src/query.py:391-398`. The exact historical `I-124-labelled trastuzumab` and `trastuzumab labelled with I-124` now produce Refused, no map centre, and zero trial/sponsor evidence. Their bare and mass-first controls retain their expected responses. Cost of the cached item check is evaluated separately by the root reviewer.

All scratch output, logs, and temporary directories are under m17/names; bytecode is disabled. No tracked or application source file was modified. Root verification owns repository-wide integrity and the final verdict.
''')
(out / 'FINDINGS.md').write_text('\n'.join(lines), encoding='utf8')
print(json.dumps(checks, indent=2))
