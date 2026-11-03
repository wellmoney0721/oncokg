from pathlib import Path
import json,re
out=Path(__file__).resolve().parent
prior=json.loads(Path('audit_evidence_claims/m8/replays/historical_findings_matrix.json').read_text(encoding='utf8'))
verified={0,3,9,17,19,20,21,24,28,29,30,31,32,33,34,35,36,37,41,42,43,44,45,47,48,49,50,51,52,53,54,56,57,58,59,60}
for i,r in enumerate(prior):
 r['round8_row_index']=i;r['status_changed_from_round8']=False
 r['round9_verification']='Current name scripts rerun and inspected' if i in verified else 'Root or DB/UI/cost worker owns current verification'
 if i==54:r['current_evidence']='FIXED for all 19 non-M5-S2 historical lost aliases. Exact m7 20-name loss set overlaps current 7,511-key losses only at accepted Pegylated interferon alfa-2a. See alias_regressions.json and historical_alias_set_check.json.'
 if i==60:r['current_evidence']='FIXED for all 19 non-M5-S2 old losses, including named three controls; separate newly lost aliases are new_alias_confirmation.json.'
extra=[
 ('M8-B1','[89 Zr] trastuzumab; tab/newline/NBSP mass-element variants','Refused, no originator centre; trial/sponsor QA 0.','attacks/probe_results.json'),
 ('M8-B2','bevacizumab-(awwb), bevacizumab-[awwb]; separate osimertinib','Refused; separate osimertinib preserved; trial/sponsor QA 0.','attacks/probe_results.json'),
 ('M8-B3','bevacizumab⸺awwb and all 26 Unicode Pd characters','Every Pd fold is ASCII hyphen; no originator centre; QA 0.','attacks/unicode_dashes.json'),
 ('M8-S1','Natural cache rollover in exact 7,511-key sweep','Original script now completes; adapted script records cache_errors=[]; HTTP boundary owned by cost worker.','names_m5_summary.json'),
 ('M8-S2','biosimilar, and osimertinib; semicolon; biosimilar and, osimertinib','All return CHEMBL3353410; trial/sponsor QA 12 rows.','attacks/probe_results.json'),
 ('M8-S3','566C, 9-ac, 5ac','Correct CHEMBL1450 / CHEMBL274070 / CHEMBL1489, actual HTTP200.','alias_checks/new_http.json'),
 ('M8-S4','5.BETA.,20-EPOXY-1,2.ALPHA.,4,7.BETA.','Correct CHEMBL428647, actual HTTP200.','alias_checks/new_http.json')]
for fid,inp,result,evidence in extra:prior.append(dict(round='M8',finding=fid+' '+inp,status='FIXED',current_evidence=result,evidence=evidence,round9_verification='Current name scripts rerun and inspected'))
(out/'historical_findings_matrix.json').write_text(json.dumps(prior,ensure_ascii=False,indent=2),encoding='utf8')
old=json.loads(Path('audit_evidence_claims/m7/names/names_m5_summary.json').read_text(encoding='utf8'))['new_lone_alias_refusals']
new=json.loads((out/'names_m5_summary.json').read_text(encoding='utf8'))['new_lone_alias_refusals']
overlap=sorted({r['input'] for r in old}&{r['input'] for r in new})
(out/'historical_alias_set_check.json').write_text(json.dumps(dict(old_count=len(old),old_inputs=[r['input'] for r in old],still_lost=overlap,all_19_non_M5_S2_restored=overlap==['Pegylated interferon alfa-2a']),ensure_ascii=False,indent=2),encoding='utf8')
body='''# Round 9 historical name and QA verification

Reviewed HEAD `3a362eb`. Every previously named originator-leak reproduction through M8 is FIXED. All 19 non-M5-S2 historical lone-name losses remain repaired. All seven M8 findings are FIXED for their original inputs (cache HTTP confirmation belongs to the cost worker). Four other exact stored aliases now lose their valid lone-drug map; they are new regressions, described below.

## Reuse, execution and scope

- [Reuse manifest](reuse_manifest.json): earlier Python scripts copied with output relocation and HTTP-port changes only, except ROOT-path adjustment for deeper m9 nesting. Existing M8 instrumentation adaptations remain explicit; no application/tracked source changed.
- [Core run](replay_execution.json): all **13/13** inherited scripts exit 0, including the original **113 cases / 7,511 unique alias keys**. This literal original script no longer aborts on cache rollover. It finds zero wrong-ID results in this particular unique-key sweep. **278** prior/current metadata differences or refusals were recorded, **29** formerly linked aliases currently lack a Drug; genuine isotope/product names are not all labeled defects.
- [Six original supplements](supplement_execution.json) all exit 0. They include 39 focused cases, 106 cases / 8 QA from the older fresh probe, and reversed-qualifier controls.
- [Execution](round9_execution.json): inherited adapted 7,511-key sweep also exits 0 with **zero cache errors**; [23 focused cases](adapted_m7_focus.json), [26 cases and 4 prefixed QA](historical_focus.json), exact alias comparisons, [all five literal m1 scripts](m1_exact/execution.json), and m8 exact attack/alias probes all pass execution. The obsolete unadapted m7_focus.py was copied for provenance but not executed; its known `_whole_name` arity is handled by the inherited adapted script without changing inputs.
- [Frozen 1,648-question no-relink counterfactual](adapted_frozen_qa_relink_sweep.json): **64 identical / 1,560 entity-metadata-only / 24 semantic changes / 0 errors**. It patches current `_link` matched-token exclusion. The inherited scripts that patch only `link_entities` were rerun but are inert counterfactuals now and are not used to infer no-relink behavior.
- The distinct [m7 attack script](m7_attacks/fresh_probe.py) was also reused after the cost worker's isolated timing ended: **93 cases, 10 QA, 44 HTTP requests**, all HTTP200, own port closed. [Stage/direct results](m7_attacks/fresh_results.json), [HTTP](m7_attacks/http_results.json), [lifecycle](m7_attacks/http_lifecycle.json). This inherited M8 script already includes the current `_whole_name(..., found)` signature adaptation. Its raw internal-stage probes do not normalize first; public linker/map results determine the disposition.
- [Exact m8 attack replay](attacks/probe_results.json): **174 inputs / 8 QA**, including all **26 Unicode Pd** characters. [M8 single-name checks](attacks/lone_alias_results.json), [16 actual alias/control HTTP requests](alias_checks/new_http.json). HTTP page bytes match current worktree; the database SHA256 before and after is unchanged (`7341c5a7089731f67356da5a588b269d4b69e8e6c4c054acf19aa4ef2837b529`).
- Own CLI HTTP ports **8891** (sequential inherited runs) and **8901** (new alias confirmation) are closed. OS process exit code1 after intentional terminate is cleanup, not a failed reproduction. All script temp files are confined under m9.

## Exact historical dispositions

The [69-row merge matrix](historical_findings_matrix.json) preserves all 62 previous rows and appends seven M8 rows. Current name verification applies to the rows marked accordingly; DB/UI/cost/root own the remaining rows. No name row changes status from the M8 report. The table below contains all name rows plus M8. FIXED applies to the exact reproduction; it is not a universal claim over variations.

| Finding / input | Current result |
|---|---|
'''
for i,r in enumerate(prior):
 if i not in verified and r['round']!='M8':continue
 desc=r['current_evidence']
 if r['round']!='M8':
  # Retain useful original observations, but remove stale sibling-evidence links.
  desc=re.sub(r'\[[^]]+\]\([^)]*\)','',desc)
  desc=desc.replace('The current sweep separately records new isotope-token over-refusals.','New valid-alone losses are separately confirmed below.')
 body+=f"| {r['round']} {r['finding']} | {r['status']} — {desc} |\n"
body+='''
The 39-case matrix has only the accepted M5-S2 mismatch. Exact old 20-alias set comparison confirms **19/19 non-M5-S2 recoveries**; [machine-readable check](historical_alias_set_check.json). M6 prefixed QA remains a stated whole-input-name-policy limitation: `Which trials evaluate ENDOSTATIN, N-TERMINAL-MGGSHHHHH?` selects CHEMBL4297747 with 2 rows; `Which trials evaluate Rapamycin, 42-o-(2-hydroxyethyl)-?` selects CHEMBL413 with 5 rows. Bare complete names correctly select CHEMBL4297946 and CHEMBL1908360. The non-parenthetical reversed-qualifier supplement still selects doxorubicin after a listing-word boundary. Lowercase IDs / investigator names remain unsupported. None is relabeled newly fixed.

## New valid-alone regressions: four exact stored aliases

These inputs are exact, unique dictionary aliases, supplied alone. Each yielded the correct live Drug using the exact M8 query module; each now returns HTTP200 Refused/no centre on the original CLI server. Preferred names and IDs still work. This violates the user's exception for a valid drug alone in its item, independently of intended same-item over-refusal. [Reproducer](new_alias_confirmation.py), [all stages, exact-M8 comparison and 10 actual HTTP requests](new_alias_confirmation.json).

| Exact input | Correct stored Drug | Current result / mechanism |
|---|---|---|
| `Trastuzumab--vcmmae conjugate` | TRASTUZUMAB VEDOTIN / CHEMBL5315030 | Refused. Resolver returns ALIAS to this separate ADC, with no refusal. Punctuation runs fold to one hyphen and the truncated `Trastuzumab-vcmmae` window trips the suffix guard. |
| `Theophylline in dextrose 5% in plastic container` | THEOPHYLLINE / CHEMBL1355736 | Refused. Edge stripping removes `%`; adjacent `5 in` is read as isotope number+element. |
| `40-o-(2-hydroxyethyl)-rapamycin` | EVEROLIMUS / CHEMBL1908360 | Refused. Punctuation-collapse guards interpret the leading chemical locant as tracer-like. |
| `42-o-(2-hydroxyethyl)rapamycin` | EVEROLIMUS / CHEMBL1908360 | Refused. Same collapsed predicate; resolver also records a radiotracer guard after cleaning. |

Raw `T.is_distinct_product` and `T.is_radiotracer` are false for all four complete spellings. The new item checks at `src/query.py:114-126` are sufficient to produce refusal; `_whole_name` at `227-228` then refuses exact stored-name recovery. `src/query.py:196` exempts only resolver pieces that tokenize as one word, not all complete exact stored names. Current source references: universal fold `101-106`, recorded `radiotracer_guard` `204-207`, comma-piece-limited carry `300-302`, symmetric stored punctuation comparison `229-235`.

These four are new should-fix regressions. Do not infer that every other isotope-bearing alias in the 29-name loss list is a defect; those require the explicit tracer/product policy. The alias comparison restores an exact earlier query module while keeping current app/rules/data, not the entire old application.

## Demos and commands

The seven unchanged QA demos retain evidence counts **12,12,11,1,12,0,0**. Six complete responses match the original `bfcb83d` linker; Mvasi differs only in refusal entity metadata. [Comparison](names_demo_results.json). Full page/UI/cost checks belong to the sibling worker.

```text
python -B audit_evidence_claims/m9/names/run_round9.py
python -B audit_evidence_claims/m9/names/m7_attacks/fresh_probe.py
python -B audit_evidence_claims/m9/names/new_alias_confirmation.py
python -B audit_evidence_claims/m9/names/build_round9_findings.py
```

Bytecode disabled; HTTP runners sharing8891 must run sequentially. Old stage-harness adaptations and original-vs-current boundaries are stated above. No application code was changed; therefore the conditional KOA/KhOpenApi before/after-code comparison does not apply.
'''
(out/'FINDINGS.md').write_text(body,encoding='utf8')
print('Wrote',len(prior),'merge rows and',len(verified)+len(extra),'current name/M8 rows')
