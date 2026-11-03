# Round 10 historical name-resolution verification

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
| M1 B1 `bevacizumab - awwb`, `89Zr - trastuzumab`, `[89Zr] trastuzumab` | **FIXED** | Original three suffix/tracer inputs all refuse, no centre. [Evidence](m1_exact/names_product_bypass.json). |
| M1 B4 retire CHEMBL3353410 in memory; query name, ID, EGFR | **FIXED** | Retired OSIMERTINIB by name and ID is not_found; retired neighbour excluded. [Evidence](m1_exact/names_retired_http_results.json). |
| M1 S5 silent ambiguity: Roche, MET, osimertinib EGFR/reversal, Mvasi and bevacizumab | **FIXED** | Roche/MET/multiple entities retain the selected identity and disclose alternatives/refusal. [Evidence](names_reproduction_results.json). |
| M1 Lowercase IDs / Investigator names: nct00200395, chembl3353410, Armando Santoro Md | **NOT FIXED** | Lowercase NCT/CHEMBL IDs and investigator label remain not_found; exact IDs work. [Evidence](names_unsupported_forms.json). |
| M2b R1 `osimertinib and generic version of bevacizumab`, reverse/comma, trial/sponsor QA | **FIXED** | Explicit separate osimertinib survives beside generic bevacizumab in both orders. [Evidence](names_regressions.json). |
| M2b R1 tracer/oral-product collateral refusal, both orders | **FIXED** | Separate osimertinib survives tracer/oral-product refusals in both orders. [Evidence](names_regressions.json). |
| M2b Inherited `What is the generic version of bevacizumab?` | **FIXED** | Leading question text no longer detaches the generic qualifier. [Evidence](names_new_boundaries.json). |
| M2b Embedded multi-ID `Sharedbrand company` fixture | **FIXED** | Sharedbrand company fixture discloses the other matching company ID. [Evidence](names_boundary_details.json). |
| M3 and M4 M3-B1 `paclitaxel with albumin bound nanoparticles`, formulation variant, `generic version with bevacizumab` | **FIXED** | Albumin-bound nanoparticle/generic-with original cases refuse, no parent map. [Evidence](names_new_boundaries.json). |
| M3 and M4 M3-B2 leading generic-version question | **FIXED** | What is the generic version of bevacizumab? refuses. [Evidence](names_new_boundaries.json). |
| M3 and M4 M3 comma collateral refusal: osimertinib with separately listed liposomal/biosimilar drug; reversals/QA | **FIXED** | Comma-separated ordinary osimertinib survives qualified-product refusal. [Evidence](names_new_boundaries.json). |
| M3 and M4 M3 bare erlotinib hydrochloride / long paclitaxel-poliglumex name; nested-parent re-link | **FIXED** | Complete erlotinib salt/paclitaxel-poliglumex names retain their own IDs without re-linking nested parents. [Evidence](names_attack.json). |
| M3 and M4 M4-B1 wrong shortest-span tie: `osimertinib with generic version of bevacizumab`, reversal/added a | **FIXED** | Both drugs in the original same-item generic-description tie are refused under revised design. [Evidence](names_attack.json). |
| M3 and M4 M4-B1 semicolon and fullwidth-comma variants | **FIXED** | Semicolon and fullwidth comma separate the valid osimertinib item. [Evidence](names_separator_checks.json). |
| M3 and M4 M4-B2 long qualified poliglumex / `generic version of the monoclonal antibody bevacizumab` | **FIXED** | Long qualified poliglumex and distant generic qualifier refuse; bare long-name control survives. [Evidence](names_attack.json). |
| M3 and M4 M4-B3 consumed qualifier: biosimilar version / liposomal formulation / albumin-bound / two-product combination | **FIXED** | Consumed qualifier cases for biosimilar/liposomal/albumin/two products refuse parent identity. [Evidence](names_attack.json). |
| M3 and M4 M4 target/company collateral refusal: EGFR or AstraZeneca beside biosimilar bevacizumab, reverse/with controls | **FIXED** | EGFR/AstraZeneca survive beside refused bevacizumab; refusal remains disclosed. [Evidence](names_m5_attack.json). |
| M3 and M4 M4 no-relink QA assessment | **FIXED** | Frozen 1,648 cases: 64 identical, 1,560 entity-metadata-only, 24 semantic changes, 0 errors. [Evidence](adapted_frozen_qa_relink_sweep.json). |
| M5 and M6 M5-B1 reported attached slash/pipe and internal both-sides-glued attack | **FIXED** | Attached slash/pipe cases select separate OSIMERTINIB and disclose refused bevacizumab. [Evidence](names_m5_confirm.json). |
| M5 and M6 M5-B2 `liposomal and nanoparticle formulation of doxorubicin`, plural/sustained-release | **FIXED** | Forward bare-qualifier carry refuses original liposomal/nanoparticle product descriptions. [Evidence](names_m5_confirm.json). |
| M5 and M6 M5-S1 `biosimilar anastrozole, Arimidex`; `biosimilar Prolia, xgeva` | **FIXED** | Separate Arimidex/xgeva aliases survive prior-item refusal. [Evidence](names_cross_item_refusal.json). |
| M5 and M6 M5-S1 `Erlotinib, hydrochloride biosimilar bevacizumab`, semicolon | **FIXED** | Qualified comma/semicolon Erlotinib lists preserve CHEMBL553. [Evidence](names_m5_attack.json). |
| M5 and M6 M5-S2 Pegylated interferon alfa-2a | **NOT FIXED** | NOT FIXED; explicitly accepted M5-S2 over-refusal. Preferred name and ID remain available. [Evidence](names_m5_summary.json). |
| M5 and M6 M6-B1 interior slash/pipe | **FIXED** | Interior slash/pipe variants retain separate osimertinib; no refused-product originator. [Evidence](focused_matrix.json). |
| M5 and M6 M6-B2 U+3002 suffix punctuation, trailing em dash/hyphen, leading hyphen | **FIXED** | Original U+3002/trailing em dash/trailing hyphen/leading hyphen suffix inputs all refuse. [Evidence](historical_focus.json). |
| M5 and M6 M6-B2 supplementary bracketed/Unicode variants | **FIXED** | Bracketed, quoted, question-mark and Unicode-hyphen suffix variants all refuse. [Evidence](historical_focus.json). |
| M5 and M6 M6-B3 `doxorubicin (nanoparticle and liposomal formulation)` / `bevacizumab (investigational and biosimilar)` | **FIXED** | Both original parenthesized trailing qualifier descriptions refuse; QA evidence 0. [Evidence](historical_focus.json). |
| M5 and M6 M6 non-parenthetical reversed-qualifier supplement | **NOT FIXED** | NOT FIXED as original expectation: doxorubicin in nanoparticle and liposomal formulations selects CHEMBL53463, unchanged listing-word policy consequence. [Evidence](reversed_results.json). |
| M5 and M6 M6-S1 six complete stored aliases returning another Drug ID | **FIXED** | All six exact complete stored aliases select their intended Drug IDs. [Evidence](historical_focus.json). |
| M5 and M6 M6-S1 prefixed QA using those comma-containing names | **NOT FIXED** | NOT FIXED: prefixed ENDOSTATIN comma-name QA selects CHEMBL4297747 with 2 rows; prefixed Rapamycin comma-name QA selects CHEMBL413 with 5 rows. [Evidence](historical_focus.json). |
| M5 and M6 M6 associated lone stored-alias losses | **FIXED** | All 19 old non-M5-S2 losses retain the stored Drug ID; only accepted M5-S2 remains refused. [Evidence](alias_regressions.json). |
| M7 M7-B1 Whole-name refusal bypass: `bevacizumab-awwb?`, `bevacizumab-awwb!`, quoted form | **FIXED** | All original whole-name question-mark/exclamation/quote bypasses refuse; QA evidence 0. [Evidence](historical_focus.json). |
| M7 M7-B2 Wrappers and Unicode hyphens: `(bevacizumab-awwb)`, `[bevacizumab-awwb]`, U+2011 suffix and bio-similar | **FIXED** | Parentheses, brackets, U+2011 suffix and bio-similar qualifier originals refuse. [Evidence](historical_focus.json). |
| M7 M7-B3 Whitespace isotope: `89Zr trastuzumab` | **FIXED** | 89Zr trastuzumab refuses; both trial and sponsor QA evidence 0. [Evidence](historical_focus.json). |
| M7 M7-S1 Canonical equality too broad: `Erlotinib, hydrochloride`, `osimertinib,mesylate`, `is a` | **FIXED** | Erlotinib, hydrochloride -> CHEMBL553; osimertinib,mesylate -> CHEMBL3353410; is a -> not_found. [Evidence](historical_focus.json). |
| M7 M7-S2 Lone exact stored names: `(E/Z)-AFATINIB`, `RO 09-1978/000`, `Anusol plus hc` and 19-alias set | **FIXED** | All 19 historical non-M5-S2 lone names are restored, including (E/Z)-AFATINIB, RO 09-1978/000, Anusol plus hc. [Evidence](alias_regressions.json). |
| M8 M8-B1 [89 Zr] trastuzumab; tab/newline/NBSP mass-element variants | **FIXED** | [89 Zr] and tab/newline/NBSP variants refuse; trial/sponsor QA evidence 0. [Evidence](attacks/probe_results.json). |
| M8 M8-B2 bevacizumab-(awwb), bevacizumab-[awwb]; separate osimertinib | **FIXED** | Internal wrappers bevacizumab-(awwb)/-[awwb] refuse; separate osimertinib survives. [Evidence](attacks/probe_results.json). |
| M8 M8-B3 bevacizumab⸺awwb and all 26 Unicode Pd characters | **FIXED** | All 26 Unicode Pd characters normalize and refuse the suffix product. [Evidence](attacks/unicode_dashes.json). |
| M8 M8-S1 Natural cache rollover in exact 7,511-key sweep | **FIXED** | Original 7,511-key scan completes; adapted scan cache_errors=[]; natural HTTP rollover verified by cost worker. [Evidence](adapted_names_m5_summary.json). |
| M8 M8-S2 biosimilar, and osimertinib; semicolon; biosimilar and, osimertinib | **FIXED** | biosimilar, and osimertinib / semicolon / and-comma forms retain CHEMBL3353410. [Evidence](m9_attacks/probe_results.json). |
| M8 M8-S3 566C, 9-ac, 5ac | **FIXED** | 566C/9-ac/5ac retain CHEMBL1450/CHEMBL274070/CHEMBL1489. [Evidence](attacks/lone_alias_results.json). |
| M8 M8-S4 5.BETA.,20-EPOXY-1,2.ALPHA.,4,7.BETA. | **FIXED** | 5.BETA.,20-EPOXY-1,2.ALPHA.,4,7.BETA. retains CHEMBL428647. [Evidence](attacks/lone_alias_results.json). |
| M9 M9-B1 bevacizumab_awwb; bevacizumab-a.w.w.b; bevacizumab-(a.w.w.b); accented/decomposed forms | **FIXED** | All named original positive-key mismatch forms refuse; independent actual HTTP confirms underscore/accent examples and QA evidence 0. [Evidence](m9_attacks/probe_results.json). |
| M9 M9-B2 [89.Zr] trastuzumab; 89:Zr trastuzumab; 89.Zr and 89::Zr variants | **FIXED** | Original folded isotope inputs refuse; actual HTTP and trial/sponsor QA evidence 0. [Evidence](m9_attacks/probe_results.json). |
| M9 M9-B3 bevacizumab awwb; bevacizumab (awwb)/[awwb]; trastuzumab dkst/(dkst) | **FIXED** | All original whitespace/wrapper suffix forms refuse; HTTP QA evidence 0. [Evidence](m9_attacks/probe_results.json). |
| M9 M9-S1 Theophylline in dextrose 5% in plastic container | **FIXED** | Exact lone alias now maps THEOPHYLLINE / CHEMBL1355736 over HTTP200. [Evidence](new_alias_confirmation.json). |
| M9 M9-S1 40-o-(2-hydroxyethyl)-rapamycin | **NOT FIXED** | Accepted known over-refusal; EVEROLIMUS and its ID work. [Evidence](new_alias_confirmation.json). |
| M9 M9-S1 42-o-(2-hydroxyethyl)rapamycin | **NOT FIXED** | Accepted known over-refusal; EVEROLIMUS and its ID work. [Evidence](new_alias_confirmation.json). |
| M9 M9-S1 Trastuzumab--vcmmae conjugate | **NOT FIXED** | Accepted known over-refusal; TRASTUZUMAB VEDOTIN and its ID work. [Evidence](new_alias_confirmation.json). |

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
