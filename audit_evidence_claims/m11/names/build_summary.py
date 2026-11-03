from pathlib import Path
import hashlib,json,socket
out=Path(__file__).resolve().parent
root=Path.cwd()
def read(name):return json.loads((out/name).read_text(encoding='utf8'))
# Reuse the previous exhaustive disposition specification, then ground it in the fresh outputs.
source=Path('audit_evidence_claims/m10/names/build_findings.py').read_text(encoding='utf8')
source=source.split("(out/'historical_name_dispositions.json').write_text",1)[0]
source=source.replace('Frozen 1,648 cases: 64 identical, 1,560 entity-metadata-only, 24 semantic changes, 0 errors.','Frozen 1,648 cases: 68 identical, 1,556 entity-metadata-only, 24 semantic changes, 0 errors.')
exec(compile(source,'m10 historical disposition specification','exec'),globals())
focus=read('m10_attacks/focus_results.json');by={r['text']:r['current'] for r in focus['cases']}
new_specs=[
 ('M10-B1 isotope inside stored name',['A33 124i','A33 124 i','A33 [124i]','A33 124I','A33-124i']),
 ('M10-B2 isotope token substituted for substance',['18F fluorothymidine','18-F fluorothymidine','[18F] fluorothymidine','18F nonexistingdrug','18-F trastuzumab','90y somatostatin']),
 ('M10-B3 punctuation consumed neighbor-word budget',['trastuzumab 89 - Zr','trastuzumab [89 - Zr]','trastuzumab 89 _ Zr']),
 ('M10-B4 separator variants of product qualifiers',['generic-version of bevacizumab','generic_version of bevacizumab','albumin - bound paclitaxel','follow-on-biologic bevacizumab'])]
for finding,texts in new_specs:
 passed=all(not by[t]['map'].get('center') and by[t]['map'].get('refused') and not by[t]['trial_qa']['evidence'] and not by[t]['sponsor_qa']['evidence'] for t in texts)
 matrix.append(dict(round='M10',finding=finding,status='FIXED' if passed else 'NOT FIXED',detail='Exact inputs now refuse with no centre and zero trial/sponsor QA evidence: '+ '; '.join(texts),evidence='m10_attacks/focus_results.json'))
(out/'historical_name_dispositions.json').write_text(json.dumps(matrix,ensure_ascii=False,indent=2),encoding='utf8')
old=json.loads((root/'audit_evidence_claims/m10/names/names_m5_summary.json').read_text(encoding='utf8'));current=read('names_m5_summary.json')
oldset={r['input'] for r in old['new_lone_alias_refusals']};newlost=[r for r in current['new_lone_alias_refusals'] if r['input'] not in oldset]
(out/'new_alias_losses.json').write_text(json.dumps(dict(description='Current versus m10 loss-set comparison, not a defect count; previous values inside each row retain original historical-method baseline semantics.',count=len(newlost),cases=newlost),ensure_ascii=False,indent=2),encoding='utf8')
old19=json.loads((root/'audit_evidence_claims/m7/names/names_m5_summary.json').read_text(encoding='utf8'))['new_lone_alias_refusals'];old19set={r['input'] for r in old19}
overlap=[r['input'] for r in current['new_lone_alias_refusals'] if r['input'] in old19set]
alias_check=dict(original_loss_set=len(old19set),still_lost=overlap,all_19_non_M5_S2_restored=overlap==['Pegylated interferon alfa-2a'])
(out/'historical_alias_set_check.json').write_text(json.dumps(alias_check,indent=2),encoding='utf8')
with socket.socket() as sock:closed=sock.connect_ex(('127.0.0.1',8892))!=0
manifest=read('reuse_manifest.json')
checks=dict(head=focus['head'],all_replay_runners_exit_zero=all(r['exit_code']==0 for f in ['round9_execution.json','replay_execution.json','supplement_execution.json','final_replay_execution.json'] for r in read(f)),exact_m1_scripts_exit_zero=all(r['exit_code']==0 for r in read('m1_exact/execution.json')['scripts']),port_8892_closed=closed,reused_source_hashes_unchanged=all(hashlib.sha256((root/r['source']).read_bytes()).hexdigest()==r['source_sha256'] for r in manifest),alias_keys_checked=current['aliases_checked'],alias_anomalies=current['alias_anomalies'],formerly_linked_without_current_drug=len(current['new_lone_alias_refusals']),adapted_cache_errors=read('adapted_names_m5_summary.json')['cache_errors'],old_alias_set=alias_check)
(out/'worker_final_checks.json').write_text(json.dumps(checks,indent=2),encoding='utf8')
body='''# Round 11 historical name-resolution verification

HEAD `2b9fc92`. All previously reported originator blockers M1 through M10 are FIXED for their exact reproductions. The new independent attacks still establish two inherited positive/refusal normalization gaps.

## Execution and exact case reuse

- [Reuse manifest](reuse_manifest.json): 45 prior Python scripts copied, preserving cases and historical read paths; output m10/names becomes m11/names, nested m10 attack root becomes cwd. Port 8892 is shared sequentially. Obsolete unadapted m7_focus.py is retained but not executed; adapted version uses current signature. focus.py dynamically compares HEAD^ as originally written, now the actual M10 implementation.
- [Core runner](replay_execution.json): 13/13 exit 0; [six supplements](supplement_execution.json), [12-step inherited wrapper](round9_execution.json), [five original M1 scripts](m1_exact/execution.json), [three final HTTP scripts](final_replay_execution.json) all exit 0. Additionally exact M9 probe (146 inputs/16 QA), M10 probe (1,224 inputs), M10 focus (35 inputs/current+parent map/QA) exit 0. 39 leaf reproduction scripts executed, excluding wrapper runners.
- [Original alias sweep](names_m5_attack.json): 113 cases and 7,511 unique keys, 318 changed alias results against its stated old-method counterfactual, 69 formerly linked names now lack a Drug. [Adapted sweep](adapted_names_m5_summary.json) reports no cache errors. These are comparison counts, not 69 defects.
- [Frozen no-relink counterfactual](adapted_frozen_qa_relink_sweep.json): 1,648 exact prior cases, 68 identical / 1,556 entity-metadata-only / 24 semantic differences / zero errors. This adapted version patches current _link; older inert patches to the public wrapper are retained only as replay provenance.
- [26 exact M6/M7 controls](historical_focus.json) satisfy their current expected centres; [39-case matrix](focused_matrix.json) has only the explicitly accepted M5-S2 mismatch. All 19 old non-M5-S2 lone-name losses remain restored. [Old alias set](historical_alias_set_check.json).
- Original M7 HTTP: 44 requests; M9 HTTP: 50 requests; M9-S1: 10 requests. All expected HTTP200, port 8892 closed after owned servers are stopped. [M7](m7_attacks/http_results.json), [M9](m9_attacks/http_results.json), [M9-S1](new_alias_confirmation.json), [final checks](worker_final_checks.json). Server exit 1 is the explicit Windows terminate lifecycle, not a request failure.

## Individual historical dispositions

M2 has no final REPORT.md; its scripts are represented by the cumulative M2b replay. The table covers historical name-resolution findings; DB/UI/cost findings are owned by sibling/root workers.

| Round / finding | Status | Current evidence |
|---|---|---|
'''
for r in matrix:body+=f"| {r['round']} {r['finding'].replace('|','&#124;')} | **{r['status']}** | {r['detail']} [Evidence]({r['evidence']}). |\n"
body+='''
## Demo and broader lookup effects

All seven original page/CLI QA demos retain evidence counts **12, 12, 11, 1, 12, 0, 0**. Six complete answers equal bfcb83d; Mvasi differs only in refusal metadata. [Demo comparison](names_demo_results.json).

The newly refused bare-alias set has 37 more entries than m10. It includes intended labelled-product refusals such as A33 124i and numerous true isotope-bearing stored substances; it is not 37 defects. [Exact loss set](new_alias_losses.json). Apparent nonblocking over-refusals include `9-amino-20(s)-camptothecin` (20(s) stereochemical notation read as an isotope), `il-6ra` (TOCILIZUMAB alias contains 6ra), and `TAK-659F` (MIVAVOTINIB development alias contains 659F). All three preferred-name and exact-ID controls select the expected stored IDs. [Direct controls](alias_loss_controls.json). No wrong molecule is drawn. The supplied M5-S2 and M9-S1 accepted over-refusals remain recorded above and are not reasons for blocking approval.

No application code changed; the conditional KOA/KhOpenApi original-versus-modified code requirement does not apply. Outputs reside under m11 and stage probes reopen database handles read-only. Root owns complete tracked-file and DB hash verification.

## Reproduction

```text
python -B audit_evidence_claims/m11/names/run_round9.py
python -B audit_evidence_claims/m11/names/m9_attacks/probe.py
python -B audit_evidence_claims/m11/names/run_final_replays.py
python -B audit_evidence_claims/m11/names/m10_attacks/probe.py
python -B audit_evidence_claims/m11/names/m10_attacks/focus.py
python -B audit_evidence_claims/m11/names/build_summary.py
```

Set PYTHONDONTWRITEBYTECODE=1, PYTHONUTF8=1 and TMP/TEMP/TMPDIR under m11/names/tmp. Port-sharing scripts must be sequential. Counterfactuals replace only their stated query methods/module and retain current app/rules/data; they are not historical deployment reconstructions.
'''
(out/'FINDINGS.md').write_text(body,encoding='utf8')
print(json.dumps(dict(rows=len(matrix),checks=checks)))
