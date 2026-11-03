"""Ground cumulative name dispositions in rerun outputs and explicit current assertions."""
from pathlib import Path
import hashlib,json,socket,subprocess
root=Path.cwd();out=Path(__file__).resolve().parent;old=root/'audit_evidence_claims/m11/names'
def read(n):return json.loads((out/n).read_text(encoding='utf8'))
matrix=json.loads((old/'historical_name_dispositions.json').read_text(encoding='utf8'))
comparison=read('replay_comparison.json')
assert not any(r.get('missing') for r in comparison['files'])
aggregate_files={'names_m5_attack.json','names_m5_summary.json','adapted_names_m5_summary.json','alias_regressions.json'}
assert all(r['normalized_equal'] for r in comparison['files'] if r['file'] not in aggregate_files)
focused=read('focused_matrix.json');historical=read('historical_focus.json')
assert [r['finding'] for r in focused if not r['matches_expectation']]==['M5-S2-known']
assert all(r['status']=='FIXED' for r in historical['cases'])
exact=read('m11_exact.json')
assert all(r['actual_center']==r['expected_center'] for r in exact)
assert all(not q['evidence'] for r in exact if not r['expected_center'] for q in r['qa'])
for finding,inputs in [('M11-B1 split isotope element symbol',['[89Z.r] trastuzumab','89Z_r trastuzumab','trastuzumab [89Z.r]']),('M11-B2 fragmented biosimilar suffix',['bevacizumab a - w w b','bevacizumab - a - w - w - b','bevacizumab a_w_w_b'])]:
    matrix.append(dict(round='M11',finding=finding,status='FIXED',detail='All literal reported forms refuse with no centre and zero trial/sponsor evidence; each comma-osimertinib form retains CHEMBL3353410. Inputs: '+ '; '.join(inputs),evidence='m11_exact.json',stage_evidence='m11_attacks/key_equivalence_results.json'))
for row in read('alias_loss_controls.json'):
    forms=row['forms'];still_lost=not forms[0]['map'].get('center') and bool(forms[0]['map'].get('refused'))
    assert still_lost and all(v['map'].get('center',{}).get('id')==row['id'] for v in forms[1:])
    matrix.append(dict(round='M11',finding='M11-S1 '+row['alias'],status='NOT FIXED',detail='Explicitly accepted known over-refusal; preferred name and exact node ID still select '+row['id']+'.',evidence='alias_loss_controls.json'))
(out/'historical_name_dispositions.json').write_text(json.dumps(matrix,ensure_ascii=False,indent=2),encoding='utf8')
current=read('names_m5_summary.json');prev=json.loads((old/'names_m5_summary.json').read_text(encoding='utf8'))
oldset={r['input'] for r in prev['new_lone_alias_refusals']};newlost=[r for r in current['new_lone_alias_refusals'] if r['input'] not in oldset]
assert [r['input'] for r in newlost]==['rad001c']
(out/'new_alias_losses.json').write_text(json.dumps(dict(description='Current versus m11 loss-set comparison; not a total defect count.',count=len(newlost),cases=newlost),ensure_ascii=False,indent=2),encoding='utf8')
prior19=json.loads((root/'audit_evidence_claims/m7/names/names_m5_summary.json').read_text(encoding='utf8'))['new_lone_alias_refusals']
overlap=[r['input'] for r in current['new_lone_alias_refusals'] if r['input'] in {x['input'] for x in prior19}]
assert overlap==['Pegylated interferon alfa-2a']
alias_check=dict(original_loss_set=len(prior19),still_lost=overlap,all_19_non_M5_S2_restored=True)
(out/'historical_alias_set_check.json').write_text(json.dumps(alias_check,indent=2),encoding='utf8')
executions={f:read(f) for f in ['round9_execution.json','replay_execution.json','supplement_execution.json','final_replay_execution.json','additional_execution.json']}
assert all(r['exit_code']==0 for rows in executions.values() for r in rows)
assert all(r['exit_code']==0 for r in read('m1_exact/execution.json')['scripts'])
with socket.socket() as sock:closed=sock.connect_ex(('127.0.0.1',8920))!=0
manifest=read('reuse_manifest.json');hashes_ok=all(hashlib.sha256((root/r['source']).read_bytes()).hexdigest()==r['source_sha256'] for r in manifest)
assert closed and hashes_ok and not read('adapted_names_m5_summary.json')['cache_errors']
leafs=[]
for name,rows in executions.items():
    leafs += [r['script'] for r in rows if not Path(r['script']).name.startswith('run_')]
leafs += ['m1_exact/'+r['script'] for r in read('m1_exact/execution.json')['scripts']]
head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
checks=dict(head=head,all_runners_exit_zero=True,exact_m1_scripts_exit_zero=True,port_8920_closed=closed,reused_source_hashes_unchanged=hashes_ok,reused_script_count=len(manifest),executed_reused_leaf_count=len(leafs),executed_reused_leafs=leafs,additional_new_checks=['m11_exact.py','new_alias_regression.py'],historical_matrix_rows=len(matrix),alias_keys_checked=current['aliases_checked'],alias_anomalies=current['alias_anomalies'],formerly_linked_without_current_drug=len(current['new_lone_alias_refusals']),cache_errors=[],old_alias_set=alias_check)
(out/'worker_final_checks.json').write_text(json.dumps(checks,indent=2),encoding='utf8')
body=f'''# Round 12 historical name-resolution verification

Reviewed HEAD `{head}`. Every originally reported originator blocker **M1 through M11 is FIXED for its exact reproduction**. The accepted lookup losses and documented policy limitations remain separately **NOT FIXED**. One additional stored-alias over-refusal is established below; no fresh originator leak is claimed by this historical replay worker.

## Execution and evidence

- [Source manifest](reuse_manifest.json): **{len(manifest)}** prior scripts copied with output/current-run paths relocated to m12 and owned HTTP port changed to **8920**. Historical read paths and input inventories remain unchanged. The obsolete unadapted `m7_focus.py` is preserved, while its adapted version runs. `HEAD^` comparisons now mean the actual m11 query module, with current app/rules/database.
- **{len(leafs)} reused leaf reproduction scripts** executed, excluding wrapper runners, all exit 0: [13 core](replay_execution.json), [six supplements](supplement_execution.json), [12-step inherited wrapper](round9_execution.json), [five original M1 scripts](m1_exact/execution.json), [three final HTTP scripts](final_replay_execution.json), [five additional prior scripts](additional_execution.json). Two new focused checks complete literal m11 forms and diagnose the new alias loss.
- Original sweep: **113 cases / 7,511 unique keys**, **319** changes against the stated old-method counterfactual, **70** formerly linked names lacking a current Drug. The m11 totals were 318 and 69. These are diagnostic counts, not 70 defects. [Sweep](names_m5_attack.json), [summary](names_m5_summary.json), [adapted cache-safe replay](adapted_names_m5_summary.json).
- Frozen no-relink counterfactual: **1,648 exact inputs, 68 identical / 1,556 entity-metadata-only / 24 semantic differences / zero errors**. The adapted script patches current `_link`; older public-wrapper-only counterfactuals are retained as replay provenance, not used to establish no-relink correctness. [Evidence](adapted_frozen_qa_relink_sweep.json).
- The 39-case earlier matrix has only the accepted M5-S2 mismatch; all 26 M6/M7 controls match expected centres; all 19 old non-M5-S2 alias losses remain restored. [Matrix](focused_matrix.json), [M6/M7](historical_focus.json), [alias set](historical_alias_set_check.json).
- Exact M9 probe: 146 inputs / 16 QA; M10 probe: 1,224 inputs; M10 focus: 35 current/previous cases; M11 original probe: 26 cases. M11's six literal report forms plus six separate-osimertinib forms all satisfy expected centres; all 12 pure qualified trial/sponsor questions return zero evidence. [M11 original stages](m11_attacks/key_equivalence_results.json), [literal checks](m11_exact.json).
- Historical HTTP probes: M7 **44**, M9 **50**, M9-S1 **10** requests, all HTTP200. Port 8920 is closed and reused source hashes are unchanged. [M7](m7_attacks/http_results.json), [M9](m9_attacks/http_results.json), [M9-S1](new_alias_confirmation.json), [final checks](worker_final_checks.json).
- To validate retained dispositions, fresh current maps/evidence/refusal existence were compared with m11, ignoring refusal wording and declared baseline outputs. All per-case evidence files match semantically; the four changed aggregate files reflect the sole extra `rad001c` alias case. This comparison is supplementary evidence, not a universal correctness oracle. [Comparison and ignored keys](replay_comparison.json).

## Individual historical dispositions

M2 has no final REPORT.md; its partial scripts are represented in the completed M2b cumulative replay. DB, UI, cost and fresh adversarial findings are owned by sibling/root workers.

| Round / finding | Status | Current evidence |
|---|---|---|
'''
for r in matrix:body+=f"| {r['round']} {r['finding'].replace('|','&#124;')} | **{r['status']}** | {r['detail']} [Evidence]({r['evidence']}). |\n"
body+='''
## New nonblocking alias loss

`rad001c` / `RAD001C`, a stored AACT synonym for **EVEROLIMUS / CHEMBL1908360**, now returns Refused with no centre. The exact HEAD^ query module selects EVEROLIMUS. Raw resolver remains ALIAS, `_resolver_blocked` is empty, and current `_link` emits Refused. `rad`, `RAD001`, `EVEROLIMUS` and the exact node ID remain valid. [Current/previous stages and QA](new_alias_regression.json), [sole newly lost alias](new_alias_losses.json).

The new trailing-key check (`src/query.py:282-286`) divides `rad001c` into stored same-drug key `rad` and suffix `001c`; `is_isotope_label('001c')` returns true under the 1–3 digit plus element grammar (`src/textrules.py:289-298`). This is an observed stored-alias lookup regression; no claim about isotope physics is needed. It draws no wrong molecule and is a should-fix lookup loss, not a blocker under the supplied approval bar.

## Demo and source assessment

All seven original page/CLI QA demos retain evidence counts **12, 12, 11, 1, 12, 0, 0**. Six complete responses match bfcb83d; Mvasi differs only in refusal metadata. [Demo comparison](names_demo_results.json). Broader page/UI demos are covered separately by the DB/UI worker.

The current `_marked` joins normalized neighbour words at `src/query.py:264-278` and tests isotope-plus-same-drug keys at `282-286`; `_link` applies the returned refusal before any positive Drug is emitted (`417-426`); `_whole_name` cannot override a recorded refusal (`295-296`). These lines explain why M11's exact split-symbol and fragmented-suffix inputs now refuse. The earlier broad tests still cannot prove safety for all possible inputs, so the independent fresh attacks remain necessary.

No application code was edited and no model was used. Outputs and temporary files stay under m12/names; historical sources retain their recorded hashes. The KOA/KhOpenApi original-versus-modified-code requirement is conditional on application changes and does not apply to this no-edit audit.

## Reproduction

```text
python -B audit_evidence_claims/m12/names/setup.py
python -B audit_evidence_claims/m12/names/run_round9.py
python -B audit_evidence_claims/m12/names/run_additional.py
python -B audit_evidence_claims/m12/names/run_final_replays.py
python -B audit_evidence_claims/m12/names/m11_exact.py
python -B audit_evidence_claims/m12/names/new_alias_regression.py
python -B audit_evidence_claims/m12/names/compare_replays.py
python -B audit_evidence_claims/m12/names/build_summary.py
```

Port-sharing scripts must run sequentially. Runner environments disable bytecode and place TEMP/TMP/TMPDIR under m12/names/tmp. Historical counterfactuals replace only their declared query methods/module and retain current app/rules/data; they are not reconstructed past deployments.
'''
(out/'FINDINGS.md').write_text(body,encoding='utf8')
print(json.dumps(checks,indent=2))
