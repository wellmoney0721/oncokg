"""Summarize current executions; preserve every name-related historical disposition."""
from pathlib import Path
import hashlib,json,socket
out=Path(__file__).resolve().parent
root=Path.cwd()
def read(name):return json.loads((out/name).read_text(encoding='utf8'))
prior=json.loads((root/'audit_evidence_claims/m9/names/historical_findings_matrix.json').read_text(encoding='utf8'))
spec={
0:('m1_exact/names_product_bypass.json','Original three suffix/tracer inputs all refuse, no centre.'),
3:('m1_exact/names_retired_http_results.json','Retired OSIMERTINIB by name and ID is not_found; retired neighbour excluded.'),
9:('names_reproduction_results.json','Roche/MET/multiple entities retain the selected identity and disclose alternatives/refusal.'),
17:('names_unsupported_forms.json','Lowercase NCT/CHEMBL IDs and investigator label remain not_found; exact IDs work.'),
19:('names_regressions.json','Explicit separate osimertinib survives beside generic bevacizumab in both orders.'),
20:('names_regressions.json','Separate osimertinib survives tracer/oral-product refusals in both orders.'),
21:('names_new_boundaries.json','Leading question text no longer detaches the generic qualifier.'),
24:('names_boundary_details.json','Sharedbrand company fixture discloses the other matching company ID.'),
28:('names_new_boundaries.json','Albumin-bound nanoparticle/generic-with original cases refuse, no parent map.'),
29:('names_new_boundaries.json','What is the generic version of bevacizumab? refuses.'),
30:('names_new_boundaries.json','Comma-separated ordinary osimertinib survives qualified-product refusal.'),
31:('names_attack.json','Complete erlotinib salt/paclitaxel-poliglumex names retain their own IDs without re-linking nested parents.'),
32:('names_attack.json','Both drugs in the original same-item generic-description tie are refused under revised design.'),
33:('names_separator_checks.json','Semicolon and fullwidth comma separate the valid osimertinib item.'),
34:('names_attack.json','Long qualified poliglumex and distant generic qualifier refuse; bare long-name control survives.'),
35:('names_attack.json','Consumed qualifier cases for biosimilar/liposomal/albumin/two products refuse parent identity.'),
36:('names_m5_attack.json','EGFR/AstraZeneca survive beside refused bevacizumab; refusal remains disclosed.'),
37:('adapted_frozen_qa_relink_sweep.json','Frozen 1,648 cases: 64 identical, 1,560 entity-metadata-only, 24 semantic changes, 0 errors.'),
41:('names_m5_confirm.json','Attached slash/pipe cases select separate OSIMERTINIB and disclose refused bevacizumab.'),
42:('names_m5_confirm.json','Forward bare-qualifier carry refuses original liposomal/nanoparticle product descriptions.'),
43:('names_cross_item_refusal.json','Separate Arimidex/xgeva aliases survive prior-item refusal.'),
44:('names_m5_attack.json','Qualified comma/semicolon Erlotinib lists preserve CHEMBL553.'),
45:('names_m5_summary.json','NOT FIXED; explicitly accepted M5-S2 over-refusal. Preferred name and ID remain available.'),
47:('focused_matrix.json','Interior slash/pipe variants retain separate osimertinib; no refused-product originator.'),
48:('historical_focus.json','Original U+3002/trailing em dash/trailing hyphen/leading hyphen suffix inputs all refuse.'),
49:('historical_focus.json','Bracketed, quoted, question-mark and Unicode-hyphen suffix variants all refuse.'),
50:('historical_focus.json','Both original parenthesized trailing qualifier descriptions refuse; QA evidence 0.'),
51:('reversed_results.json','NOT FIXED as original expectation: doxorubicin in nanoparticle and liposomal formulations selects CHEMBL53463, unchanged listing-word policy consequence.'),
52:('historical_focus.json','All six exact complete stored aliases select their intended Drug IDs.'),
53:('historical_focus.json','NOT FIXED: prefixed ENDOSTATIN comma-name QA selects CHEMBL4297747 with 2 rows; prefixed Rapamycin comma-name QA selects CHEMBL413 with 5 rows.'),
54:('alias_regressions.json','All 19 old non-M5-S2 losses retain the stored Drug ID; only accepted M5-S2 remains refused.'),
56:('historical_focus.json','All original whole-name question-mark/exclamation/quote bypasses refuse; QA evidence 0.'),
57:('historical_focus.json','Parentheses, brackets, U+2011 suffix and bio-similar qualifier originals refuse.'),
58:('historical_focus.json','89Zr trastuzumab refuses; both trial and sponsor QA evidence 0.'),
59:('historical_focus.json','Erlotinib, hydrochloride -> CHEMBL553; osimertinib,mesylate -> CHEMBL3353410; is a -> not_found.'),
60:('alias_regressions.json','All 19 historical non-M5-S2 lone names are restored, including (E/Z)-AFATINIB, RO 09-1978/000, Anusol plus hc.'),
62:('attacks/probe_results.json','[89 Zr] and tab/newline/NBSP variants refuse; trial/sponsor QA evidence 0.'),
63:('attacks/probe_results.json','Internal wrappers bevacizumab-(awwb)/-[awwb] refuse; separate osimertinib survives.'),
64:('attacks/unicode_dashes.json','All 26 Unicode Pd characters normalize and refuse the suffix product.'),
65:('adapted_names_m5_summary.json','Original 7,511-key scan completes; adapted scan cache_errors=[]; natural HTTP rollover verified by cost worker.'),
66:('m9_attacks/probe_results.json','biosimilar, and osimertinib / semicolon / and-comma forms retain CHEMBL3353410.'),
67:('attacks/lone_alias_results.json','566C/9-ac/5ac retain CHEMBL1450/CHEMBL274070/CHEMBL1489.'),
68:('attacks/lone_alias_results.json','5.BETA.,20-EPOXY-1,2.ALPHA.,4,7.BETA. retains CHEMBL428647.'),
}
matrix=[]
for index,(evidence,detail) in spec.items():
    old=prior[index]
    matrix.append(dict(round=old['round'],finding=old['finding'],status=old['status'],detail=detail,evidence=evidence,prior_matrix_index=index))
for finding,detail,status in [
('M9-B1 bevacizumab_awwb; bevacizumab-a.w.w.b; bevacizumab-(a.w.w.b); accented/decomposed forms','All named original positive-key mismatch forms refuse; independent actual HTTP confirms underscore/accent examples and QA evidence 0.','FIXED'),
('M9-B2 [89.Zr] trastuzumab; 89:Zr trastuzumab; 89.Zr and 89::Zr variants','Original folded isotope inputs refuse; actual HTTP and trial/sponsor QA evidence 0.','FIXED'),
('M9-B3 bevacizumab awwb; bevacizumab (awwb)/[awwb]; trastuzumab dkst/(dkst)','All original whitespace/wrapper suffix forms refuse; HTTP QA evidence 0.','FIXED')]:
    matrix.append(dict(round='M9',finding=finding,status=status,detail=detail,evidence='m9_attacks/probe_results.json',http='m9_attacks/http_results.json'))
for text,status,detail in [
('Theophylline in dextrose 5% in plastic container','FIXED','Exact lone alias now maps THEOPHYLLINE / CHEMBL1355736 over HTTP200.'),
('40-o-(2-hydroxyethyl)-rapamycin','NOT FIXED','Accepted known over-refusal; EVEROLIMUS and its ID work.'),
('42-o-(2-hydroxyethyl)rapamycin','NOT FIXED','Accepted known over-refusal; EVEROLIMUS and its ID work.'),
('Trastuzumab--vcmmae conjugate','NOT FIXED','Accepted known over-refusal; TRASTUZUMAB VEDOTIN and its ID work.')]:
    matrix.append(dict(round='M9',finding='M9-S1 '+text,status=status,detail=detail,evidence='new_alias_confirmation.json'))
(out/'historical_name_dispositions.json').write_text(json.dumps(matrix,ensure_ascii=False,indent=2),encoding='utf8')
old_aliases=json.loads((root/'audit_evidence_claims/m7/names/names_m5_summary.json').read_text(encoding='utf8'))['new_lone_alias_refusals']
current=read('names_m5_summary.json')
overlap=[r['input'] for r in current['new_lone_alias_refusals'] if r['input'] in {r['input'] for r in old_aliases}]
alias_check=dict(old_count=len(old_aliases),still_lost=overlap,all_19_non_M5_S2_restored=overlap==['Pegylated interferon alfa-2a'])
(out/'historical_alias_set_check.json').write_text(json.dumps(alias_check,indent=2),encoding='utf8')
with socket.socket() as s:closed=s.connect_ex(('127.0.0.1',8892))!=0
manifest=read('reuse_manifest.json')
hashes_ok=all(hashlib.sha256((root/r['source']).read_bytes()).hexdigest()==r['source_sha256'] for r in manifest)
check=dict(head='c364c84',all_replay_runners_exit_zero=all(r['exit_code']==0 for f in ['round9_execution.json','replay_execution.json','supplement_execution.json','final_replay_execution.json'] for r in read(f)),exact_m1_scripts_exit_zero=all(r['exit_code']==0 for r in read('m1_exact/execution.json')['scripts']),port_8892_closed=closed,reused_source_hashes_unchanged=hashes_ok,alias_keys_checked=current['aliases_checked'],alias_anomalies=current['alias_anomalies'],formerly_linked_without_current_drug=len(current['new_lone_alias_refusals']),adapted_cache_errors=read('adapted_names_m5_summary.json')['cache_errors'])
(out/'worker_final_checks.json').write_text(json.dumps(check,indent=2),encoding='utf8')
body='''# Round 10 historical name-resolution verification

Reviewed HEAD `c364c84`. Every **previously reported originator blocker M1 through M9** is **FIXED for its exact original reproduction**. This is not approval of all inputs: the fresh attack worker independently found new isotope leaks; the full historical alias sweep also exposed the newly restored `A33 124i` identity and supplied it for independent confirmation.

## Reuse and execution

- [Reuse manifest](reuse_manifest.json): 42 copied prior scripts, with output relocation, sequential HTTP port 8892 and a nested-script ROOT correction only. Case inventories remain unchanged. Obsolete unadapted `m7_focus.py` is preserved for provenance, not executed; inherited `adapted_m7_focus.py` uses the current `_whole_name` signature.
- [Core execution](replay_execution.json): 13/13 inherited scripts exit 0. [Six supplements](supplement_execution.json), [inherited outer runner](round9_execution.json), [five exact M1 scripts](m1_exact/execution.json), [final HTTP runs](final_replay_execution.json) all exit 0. The standalone [exact m9 matrix](m9_attacks/probe.py) also exits 0 with 146 inputs / 16 QA questions. In total, 37 leaf reproduction scripts executed, excluding wrapper runners.
- Original 113-case / 7,511-unique-key sweep: 282 metadata/refusal differences from its old method baseline, 32 formerly linked aliases now lack a Drug, zero wrong-ID results in that sweep. This is **not** proof against wrong-product identity: the dictionary itself stores some unsafe labelled aliases under an originator. [Raw sweep](names_m5_attack.json), [summary](names_m5_summary.json).
- [Frozen no-relink counterfactual](adapted_frozen_qa_relink_sweep.json): exact 1,648 original inputs, **64 identical / 1,560 entity-metadata-only / 24 semantic differences / 0 errors**. It patches current `_link`; older scripts that patch `link_entities` only are rerun for provenance but are inert counterfactuals and do not justify the no-relink conclusion.
- [26 M6/M7 controls + 4 prefixed QA](historical_focus.json) all match their stated current design expectations; [39-case matrix](focused_matrix.json) has only the accepted M5-S2 mismatch. [Original 20 lost aliases](historical_alias_set_check.json): 19/19 non-M5-S2 restored.
- Exact [m8 matrix](attacks/probe_results.json): 174 inputs / 8 QA, including all 26 Pd dashes. Exact [m7 probe](m7_attacks/fresh_results.json): 93 inputs / 10 QA plus 44 actual HTTP requests. Exact [m9 HTTP](m9_attacks/http_results.json): 50 requests, all HTTP200; all reported bad map/QA examples now refuse. [M9-S1 HTTP](new_alias_confirmation.json): 10 requests, all HTTP200. M1, m7, m8-alias and m9 servers are independently created and stopped; served HTML checks match the current worktree.
- Port 8892 is closed; earlier source SHA256 values remain unchanged. [Final worker checks](worker_final_checks.json). Temp files and outputs are under this folder. No model or application edit was used.

## Individual name-related historical dispositions

The following rows cover all historical name-resolution findings, including continued limitations. DB/UI/cost findings are owned by the sibling/root workers; cache below is the exact alias-sweep reproduction only. M2 had no final report; its name scripts are represented by the cumulative M2b replay.

| Round / finding | Status | Current evidence |
|---|---|---|
'''
for r in matrix:
    body+=f"| {r['round']} {r['finding'].replace('|','&#124;')} | **{r['status']}** | {r['detail']} [Evidence]({r['evidence']}). |\n"
body+='''
## Current boundaries and regressions

M9-S1 is split rather than given one blanket verdict: Theophylline is repaired, while both hydroxyethyl rapamycin spellings and the Trastuzumab ADC spelling remain the explicitly accepted over-refusals. M5-S2 also remains accepted. They are not newly classified as blockers. Unchanged unsupported lowercase IDs/investigator-label lookup, prefixed comma-name QA and nonparenthetical reversed-qualifier behavior remain **NOT FIXED** with their original policy qualifications.

`_qualified` now folds accents/underscores/punctuation (`src/query.py:119-138`), `_marked` applies suffix and adjacent isotope checks (`src/query.py:231-255`), the positive matcher refuses a marked hit (`src/query.py:384-395`), and `_whole_name` waits for those refusals (`src/query.py:258-276`). These changes repair M9's exact examples. The fresh attack result is broader: `_marked` does not inspect every isotope-bearing location inside a complete matched alias, so a successful old-reproduction suite cannot establish universal refusal safety. Root/attack evidence records the independently verified new blocker rather than calling M9's original examples unfixed.

The 7,511-key comparison finds 19 newly refused aliases versus m9 (18 known FDA-suffix forms and `lipo-dox`), plus 16 restored inputs. Restored isotope-bearing aliases are not all labelled defects: several identify their own isotope-bearing stored node. `A33 124i` is the actionable originator candidate passed to the attack worker. [Comparison inputs and exact identities](names_m5_attack.json).

All seven original QA demos retain evidence counts **12, 12, 11, 1, 12, 0, 0**; six whole responses match original bfcb83d, Mvasi differs only in refusal metadata. [Demo comparison](names_demo_results.json). UI and cost validation are separate.

## Reproduction

From the repository root, with bytecode disabled; do not run port-sharing runners concurrently:

```text
python -B audit_evidence_claims/m10/names/run_round9.py
python -B audit_evidence_claims/m10/names/m9_attacks/probe.py
python -B audit_evidence_claims/m10/names/run_final_replays.py
python -B audit_evidence_claims/m10/names/build_findings.py
```

`run_round9.py` keeps its inherited name for provenance; it runs the relocated scripts against current HEAD. The historical baseline comparisons swap only the stated old query methods/module; app, rules and database remain current. No application code changed, so the conditional KOA/KhOpenApi original-versus-modified code requirement does not apply.
'''
(out/'FINDINGS.md').write_text(body,encoding='utf8')
print(json.dumps(dict(rows=len(matrix),checks=check)))
