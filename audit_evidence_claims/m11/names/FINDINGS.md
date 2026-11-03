# Round 11 historical name-resolution verification

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
| M3 and M4 M4 no-relink QA assessment | **FIXED** | Frozen 1,648 cases: 68 identical, 1,556 entity-metadata-only, 24 semantic changes, 0 errors. [Evidence](adapted_frozen_qa_relink_sweep.json). |
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
| M10 M10-B1 isotope inside stored name | **FIXED** | Exact inputs now refuse with no centre and zero trial/sponsor QA evidence: A33 124i; A33 124 i; A33 [124i]; A33 124I; A33-124i [Evidence](m10_attacks/focus_results.json). |
| M10 M10-B2 isotope token substituted for substance | **FIXED** | Exact inputs now refuse with no centre and zero trial/sponsor QA evidence: 18F fluorothymidine; 18-F fluorothymidine; [18F] fluorothymidine; 18F nonexistingdrug; 18-F trastuzumab; 90y somatostatin [Evidence](m10_attacks/focus_results.json). |
| M10 M10-B3 punctuation consumed neighbor-word budget | **FIXED** | Exact inputs now refuse with no centre and zero trial/sponsor QA evidence: trastuzumab 89 - Zr; trastuzumab [89 - Zr]; trastuzumab 89 _ Zr [Evidence](m10_attacks/focus_results.json). |
| M10 M10-B4 separator variants of product qualifiers | **FIXED** | Exact inputs now refuse with no centre and zero trial/sponsor QA evidence: generic-version of bevacizumab; generic_version of bevacizumab; albumin - bound paclitaxel; follow-on-biologic bevacizumab [Evidence](m10_attacks/focus_results.json). |

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
