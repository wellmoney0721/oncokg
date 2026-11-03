# Independent relation-map review — round 15

Reviewed **`1b3896669387cbc142c12b726909231cca8658db`**. **Changes required: one newly reproduced P1 refusal bypass, plus an unresolved P1 family from M14.** `89-ZrDFO trastuzumab` passes every refusal stage and draws TRASTUZUMAB; adding one hyphen to a refused control is sufficient. The literal earlier `3hvinblastine` also still draws VINBLASTINE. The upper-case repair cases, PANITUMUMAB PET/CT variants, and original `A33124I` are **FIXED**. No new regression introduced by this latest patch was demonstrated.

All new files are under `audit_evidence_claims/m15/`. No tracked file or application code was edited. The verdict does not count the explicitly accepted over-refusals or ChEMBL bevacizumab-development-code limitation as blockers.

## Verification and scope

- **342 passed in 30.64 s**, exit 0, with `python -m pytest tests -q -p no:cacheprovider`. Bytecode disabled; temporary paths confined to m15. [Output](root_checks/pytest.txt), [execution/hashes](root_checks/pytest_summary.json).
- Cumulative original HTTP scripts were reused for m1, partial m2/completed m2b, m3-m11, then exact m12/m13 and m14 confirmations. Every execution batch exited zero; original historical input lists were preserved. [Source/adaptation manifest](reuse_manifest_root.json), [main batches](root_checks/execution_all.json), [m6](root_checks/execution_m6_http.json), [remaining](root_checks/execution_remaining.json), [m12/m13](root_checks/execution_rounds12_13.json), [m14 HTTP](root_checks/independent_m14_http.json).
- **58 copied name scripts / 47 executed reused leaf reproductions**, plus one supplemental wrapper; **69 individual historical name dispositions** below. The **7,511-key** raw-alias sweep has no new loss or recovery versus m14. The **1,648-question** frozen counterfactual remains **68 identical / 1,556 metadata-only / 24 semantic / zero errors**. These are same-current-data method comparisons, not reconstructed historical deployments. [Name assessment](names/FINDINGS.md), [manifest](names/reuse_manifest.json), [execution checks](names/worker_final_checks.json).
- Stored-row oracle: **6,469 live centres, 22 relation/direction/type/role combinations, zero errors**. **19/19 DB assertions, 24/24 UI assertions and 4/4 self-loop/unknown-type/retirement fixture checks pass**. [Oracle](db_ui/db_validate.json), [DB](db_ui/db_assertions.json), [UI](db_ui/ui_assertions.json), [fixture](db_ui/self_loop_unknown.json).
- **36/36 page demos** equal all m7-m14 full response baselines. **36/36 fresh CLI HTTP demos** return 200 and exactly equal direct Engine responses. Six map callbacks pass; original seven QA evidence counts remain **12, 12, 11, 1, 12, 0, 0**. [Comparisons](db_ui/demo_previous_comparison.json), [HTTP](db_ui/demo_http.json), [callbacks](db_ui/ui_m3_checks.json).
- **97 original m14 direct attack cases** rerun unchanged, **29 targeted current/HEAD^ stage cases**, and **116 targeted CLI HTTP responses**, all 200. An exploratory **428 variants / 104 stored keys** scan found no additional promoted family. Its raw acceptance count includes already-labelled drugs and chemical locants, so it is not a defect count. [Attack execution](attacks/execution.json), [stages](attacks/targeted_results.json), [scan](attacks/alias_variants.json).
- The root independently repeated **11 candidate/control cases through 44 HTTP requests** and the **24-case M14 matrix through 96 requests**, all 200. Another reviewer independently captured the raw-helper versus normalized-fragment failure. [Root M15 HTTP](root_checks/independent_m15_http.json), [M15 lifecycle](root_checks/independent_m15_lifecycle.json), [M14 lifecycle](root_checks/independent_m14_lifecycle.json), [independent adjudication](db_ui/adjudication.md).

UI checks execute actual page JavaScript in a Node VM with controlled DOM/fetch stubs. They establish generated markup and exercised state/callback behavior, not browser painting or browser-executed XSS. HTTP uses unmodified `src/app.py` on owned ports other than 8765, or its real handler with isolated in-memory fixtures. No model was called. Tracer identity is established from stored aliases, normalization equivalence and refused controls; this review does not claim an external validation of the entire medical-isotope table.

The hypothesis for the naming attacks was that equivalent punctuation/case forms of an identified refused tracer retain that identity through every resolution stage. The following paired controls falsify that hypothesis. Successful demos, tests and raw-alias sweeps do not cover all transformed aliases or neighbouring label forms.

## M15-B1 — splitting an isotope in a neighbouring chelator token defeats the check that recognizes its raw form

**Exact request:** `POST /api/explore`, JSON `{"text":"89-ZrDFO trastuzumab"}`.

**Observed:** HTTP 200, **TRASTUZUMAB / CHEMBL1201585**, **13 live trials**, no refusal. `Which trials evaluate 89-ZrDFO trastuzumab?` and `Who sponsors trials of 89-ZrDFO trastuzumab?` each return **12 originator evidence rows** (the QA result cap). The reverse **`trastuzumab DFO89-Zr`** does the same. The split-symbol alternatives **`89Z.rDFO trastuzumab`** and **`trastuzumab DFO89Z.r`** also leak. Adding `, osimertinib` still selects TRASTUZUMAB for the split-symbol input. [Full stages](attacks/targeted_results.json), [HTTP](attacks/targeted_http.json), [compact matrix](attacks/targeted_summary.json).

**Controls:** `89ZrDFO trastuzumab` and `trastuzumab DFO89Zr` refuse and have zero qualified trial/sponsor evidence. Each failing/control pair has the same canonical key; adding a hyphen inside `89Zr` is sufficient to change refusal into originator selection. No full DFO/trastuzumab key is present in the dictionary, so this is a neighbour-check failure rather than a consumed-whole-alias failure. Bare `trastuzumab` remains available. [Dictionary and helper evidence](attacks/dictionary_helper_evidence.json).

**Precise cause:** `_isotope_edge('89-ZrDFO')` and `_isotope_edge('DFO89-Zr')` both return **True** (`src/query.py:138-147`). However, `_marked` first uses `_alnum_words` to turn the preceding/following token into `['89', 'ZrDFO']` or `['DFO89', 'Zr']` (`src/query.py:293-294,316-317`). Its fused-label helper is then called on each fragment, which is false for all of them (`src/query.py:330-333`). Its separate gluing loops check only *whole* isotope labels, so `89zrDFO`/`DFO89zr` is not accepted by those checks (`src/query.py:318-329`). The later name-key fallback sees only `trastuzumab`, not the adjacent marker (`src/query.py:345-363`). `_marked` returns `None` in the captured actual `_link` call. This is a precise normalization inconsistency: the raw token is already recognizable by the existing helper, but that recognizable form is discarded before it is used.

Neither the raw resolver's guard (`src/normalize.py:738-746`; `src/textrules.py:303-314`) nor `_qualified` recognizes these forms. `Engine.explore` then draws the surviving first positive hit (`src/app.py:88-95`). Both current and HEAD^ query modules leak against the same current app/data: **inherited**, not introduced by the latest patch. This comparison changes only the query module in memory, not an entire historical deployment.

**Required outcome:** preserve the refusal of a case-marked isotope fused to a neighbouring chelator when punctuation is inserted inside its label, before or after the named drug. Validate actual linker/map/QA paths in addition to the standalone helper. No repair was implemented.

## M15-B2 — residual M14-B1: lower-case stored tracer alias still maps VINBLASTINE

**Exact request:** `POST /api/explore`, JSON `{"text":"3hvinblastine"}`. HTTP 200 draws **VINBLASTINE / CHEMBL159**, with **5 live trials** and **5/5 qualified trial/sponsor evidence rows**. No stage records a refusal. `3hvinblastine, osimertinib` still draws VINBLASTINE first. This exact lower-case spelling was explicitly in the M14 report and attack matrix. [Original matrix rerun](attacks/edge_results.json), [new targeted HTTP](attacks/targeted_http.json).

The dictionary has one hit for key `3hvinblastine`: stored ChEMBL synonym **`[3h]-vinblastine`**. That original synonym and the separated `3h vinblastine` refuse. Thus the remaining failure is demonstrated by the known stored tracer identity and its refusing control, without assuming that every lower-case chemical expression is an isotope. Removing only brackets and a hyphen from a refused stored tracer draws its originator. [Identity evidence](attacks/dictionary_helper_evidence.json).

The latest patch fixes `3HVINBLASTINE`, `3HVinblastine`, and `3Hvinblastine`, but `_marked` explicitly skips a one-letter isotope when the corresponding input letter is lower-case (`src/query.py:353-355`). No earlier stage or later fallback recovers the stored alias's refusal. The user describes an upper-case repair but retains the original approval bar and does not list this originator leak among the accepted exceptions. Therefore **M14-B1 is FIXED for its three upper-case spellings, NOT FIXED as an entire reported finding family**. This should not be conflated with the accepted over-refusals or development-code dictionary limitation.

**Same-mechanism corroboration:** **`A33124i`** and **`a33124i`** still draw ADAKITUG / CHEMBL5314551 (zero trials), while **`A33 124i`** refuses and repaired **`A33124I`** now refuses. Both share the stored key `a33124i`. `_medical_isotope('124i')` is true, but the lower-case check skips the iteration before the medical-mass closing-label branch (`src/query.py:354-362`). The original upper-case M13/M14 reproduction is **FIXED**; the lower-case equivalent remains an originator leak. This is corroboration of the remaining case-sensitive stored-alias gap, not a separately inflated new finding.

## Every stage for representative failures

| Stage | `89-ZrDFO trastuzumab` | `3hvinblastine` | `A33124i` |
|---|---|---|---|
| Raw intervention resolver | CONTAINED_ALIAS + UNRESOLVED; no BLOCKED component | ALIAS / CHEMBL159 | ALIAS / CHEMBL5314551 |
| `_qualified` on the single item | false | false | false |
| Resolver veto | `{}` | `{}` | `{}` |
| `_marked` during actual `_link` | `None` | `None` | `None` |
| Item linker | Drug, no Refused | Drug, no Refused | Drug, no Refused |
| Whole-name shortcut | `None` | `None` | `None` |
| Public linker | TRASTUZUMAB, no Refused | VINBLASTINE, no Refused | ADAKITUG, no Refused |
| Map / live trial count | CHEMBL1201585 / 13 | CHEMBL159 / 5 | CHEMBL5314551 / 0 |
| Qualified trial / sponsor QA rows | 12 / 12 | 5 / 5 | 0 / 0 |

All entries come from [captured current and HEAD^ stages](attacks/targeted_results.json), not inference from the map alone. The ordinary relationships may be correct for the originator, but the wrong selected centre fails the approval bar.

## Independent confirmation and required outcome

The new punctuation bypass is sufficient for **CHANGES REQUIRED** even without the lower-case residual. It changes neither the named drug nor the label's distance: `89ZrDFO trastuzumab` refuses, while `89-ZrDFO trastuzumab` selects CHEMBL1201585. The raw helper itself recognizes the hyphenated word. The fix therefore needs to preserve recognized adjacent isotope/chelator identity through normalization. The residual stored-tracer case needs identity preservation for a known refused alias; it does not require interpreting every lower-case chemical locant as an isotope. No repair was implemented here.

Root HTTP independently confirms TRASTUZUMAB's **13 live trials / 12 trial-QA / 12 sponsor-QA** and VINBLASTINE's **5 / 5 / 5**; the controls return zero QA evidence. `A33124i` draws ADAKITUG with zero trials; zero evidence does not make the wrong centre acceptable. With `89-ZrDFO trastuzumab, osimertinib`, the wrong TRASTUZUMAB centre remains; reversing the list selects OSIMERTINIB but still accepts the qualified TRASTUZUMAB hit without refusal. [Root responses](root_checks/independent_m15_http.json), [separate stage traces](db_ui/adjudication_tracer.json).

## Earlier reproductions — FIXED / NOT FIXED per finding

The tables classify exact historical reproductions, including nonblocking qualifications. M2 ended without a completed report; its partial fixtures and completed M2b results are included. A repaired spelling is not evidence that all equivalent spellings are fixed.

### Name resolution, m1-m14


M2 has no completed report; its partial name cases are covered by M2b's cumulative scripts. DB, UI, performance and root HTTP checks belong to the other review sections. Exact repaired spellings do not imply all normalized equivalents are safe.

| Round / finding | Status | Fresh evidence |
|---|---|---|
| M1 B1 `bevacizumab - awwb`, `89Zr - trastuzumab`, `[89Zr] trastuzumab` | **FIXED** | Original three suffix/tracer inputs all refuse, no centre. [Evidence](names/m1_exact/names_product_bypass.json). |
| M1 B4 retire CHEMBL3353410 in memory; query name, ID, EGFR | **FIXED** | Retired OSIMERTINIB by name and ID is not_found; retired neighbour excluded. [Evidence](names/m1_exact/names_retired_http_results.json). |
| M1 S5 silent ambiguity: Roche, MET, osimertinib EGFR/reversal, Mvasi and bevacizumab | **FIXED** | Roche/MET/multiple entities retain the selected identity and disclose alternatives/refusal. [Evidence](names/names_reproduction_results.json). |
| M1 Lowercase IDs / Investigator names: nct00200395, chembl3353410, Armando Santoro Md | **NOT FIXED** | Lowercase NCT/CHEMBL IDs and investigator label remain not_found; exact IDs work. [Evidence](names/names_unsupported_forms.json). |
| M2b R1 `osimertinib and generic version of bevacizumab`, reverse/comma, trial/sponsor QA | **FIXED** | Explicit separate osimertinib survives beside generic bevacizumab in both orders. [Evidence](names/names_regressions.json). |
| M2b R1 tracer/oral-product collateral refusal, both orders | **FIXED** | Separate osimertinib survives tracer/oral-product refusals in both orders. [Evidence](names/names_regressions.json). |
| M2b Inherited `What is the generic version of bevacizumab?` | **FIXED** | Leading question text no longer detaches the generic qualifier. [Evidence](names/names_new_boundaries.json). |
| M2b Embedded multi-ID `Sharedbrand company` fixture | **FIXED** | Sharedbrand company fixture discloses the other matching company ID. [Evidence](names/names_boundary_details.json). |
| M3 and M4 M3-B1 `paclitaxel with albumin bound nanoparticles`, formulation variant, `generic version with bevacizumab` | **FIXED** | Albumin-bound nanoparticle/generic-with original cases refuse, no parent map. [Evidence](names/names_new_boundaries.json). |
| M3 and M4 M3-B2 leading generic-version question | **FIXED** | What is the generic version of bevacizumab? refuses. [Evidence](names/names_new_boundaries.json). |
| M3 and M4 M3 comma collateral refusal: osimertinib with separately listed liposomal/biosimilar drug; reversals/QA | **FIXED** | Comma-separated ordinary osimertinib survives qualified-product refusal. [Evidence](names/names_new_boundaries.json). |
| M3 and M4 M3 bare erlotinib hydrochloride / long paclitaxel-poliglumex name; nested-parent re-link | **FIXED** | Complete erlotinib salt/paclitaxel-poliglumex names retain their own IDs without re-linking nested parents. [Evidence](names/names_attack.json). |
| M3 and M4 M4-B1 wrong shortest-span tie: `osimertinib with generic version of bevacizumab`, reversal/added a | **FIXED** | Both drugs in the original same-item generic-description tie are refused under revised design. [Evidence](names/names_attack.json). |
| M3 and M4 M4-B1 semicolon and fullwidth-comma variants | **FIXED** | Semicolon and fullwidth comma separate the valid osimertinib item. [Evidence](names/names_separator_checks.json). |
| M3 and M4 M4-B2 long qualified poliglumex / `generic version of the monoclonal antibody bevacizumab` | **FIXED** | Long qualified poliglumex and distant generic qualifier refuse; bare long-name control survives. [Evidence](names/names_attack.json). |
| M3 and M4 M4-B3 consumed qualifier: biosimilar version / liposomal formulation / albumin-bound / two-product combination | **FIXED** | Consumed qualifier cases for biosimilar/liposomal/albumin/two products refuse parent identity. [Evidence](names/names_attack.json). |
| M3 and M4 M4 target/company collateral refusal: EGFR or AstraZeneca beside biosimilar bevacizumab, reverse/with controls | **FIXED** | EGFR/AstraZeneca survive beside refused bevacizumab; refusal remains disclosed. [Evidence](names/names_m5_attack.json). |
| M3 and M4 M4 no-relink QA assessment | **FIXED** | Frozen 1,648 cases: 68 identical, 1,556 entity-metadata-only, 24 semantic changes, 0 errors. [Evidence](names/adapted_frozen_qa_relink_sweep.json). |
| M5 and M6 M5-B1 reported attached slash/pipe and internal both-sides-glued attack | **FIXED** | Attached slash/pipe cases select separate OSIMERTINIB and disclose refused bevacizumab. [Evidence](names/names_m5_confirm.json). |
| M5 and M6 M5-B2 `liposomal and nanoparticle formulation of doxorubicin`, plural/sustained-release | **FIXED** | Forward bare-qualifier carry refuses original liposomal/nanoparticle product descriptions. [Evidence](names/names_m5_confirm.json). |
| M5 and M6 M5-S1 `biosimilar anastrozole, Arimidex`; `biosimilar Prolia, xgeva` | **FIXED** | Separate Arimidex/xgeva aliases survive prior-item refusal. [Evidence](names/names_cross_item_refusal.json). |
| M5 and M6 M5-S1 `Erlotinib, hydrochloride biosimilar bevacizumab`, semicolon | **FIXED** | Qualified comma/semicolon Erlotinib lists preserve CHEMBL553. [Evidence](names/names_m5_attack.json). |
| M5 and M6 M5-S2 Pegylated interferon alfa-2a | **NOT FIXED** | NOT FIXED; explicitly accepted M5-S2 over-refusal. Preferred name and ID remain available. [Evidence](names/names_m5_summary.json). |
| M5 and M6 M6-B1 interior slash/pipe | **FIXED** | Interior slash/pipe variants retain separate osimertinib; no refused-product originator. [Evidence](names/focused_matrix.json). |
| M5 and M6 M6-B2 U+3002 suffix punctuation, trailing em dash/hyphen, leading hyphen | **FIXED** | Original U+3002/trailing em dash/trailing hyphen/leading hyphen suffix inputs all refuse. [Evidence](names/historical_focus.json). |
| M5 and M6 M6-B2 supplementary bracketed/Unicode variants | **FIXED** | Bracketed, quoted, question-mark and Unicode-hyphen suffix variants all refuse. [Evidence](names/historical_focus.json). |
| M5 and M6 M6-B3 `doxorubicin (nanoparticle and liposomal formulation)` / `bevacizumab (investigational and biosimilar)` | **FIXED** | Both original parenthesized trailing qualifier descriptions refuse; QA evidence 0. [Evidence](names/historical_focus.json). |
| M5 and M6 M6 non-parenthetical reversed-qualifier supplement | **NOT FIXED** | NOT FIXED as original expectation: doxorubicin in nanoparticle and liposomal formulations selects CHEMBL53463, unchanged listing-word policy consequence. [Evidence](names/reversed_results.json). |
| M5 and M6 M6-S1 six complete stored aliases returning another Drug ID | **FIXED** | All six exact complete stored aliases select their intended Drug IDs. [Evidence](names/historical_focus.json). |
| M5 and M6 M6-S1 prefixed QA using those comma-containing names | **NOT FIXED** | NOT FIXED: prefixed ENDOSTATIN comma-name QA selects CHEMBL4297747 with 2 rows; prefixed Rapamycin comma-name QA selects CHEMBL413 with 5 rows. [Evidence](names/historical_focus.json). |
| M5 and M6 M6 associated lone stored-alias losses | **FIXED** | All 19 old non-M5-S2 losses retain the stored Drug ID; only accepted M5-S2 remains refused. [Evidence](names/alias_regressions.json). |
| M7 M7-B1 Whole-name refusal bypass: `bevacizumab-awwb?`, `bevacizumab-awwb!`, quoted form | **FIXED** | All original whole-name question-mark/exclamation/quote bypasses refuse; QA evidence 0. [Evidence](names/historical_focus.json). |
| M7 M7-B2 Wrappers and Unicode hyphens: `(bevacizumab-awwb)`, `[bevacizumab-awwb]`, U+2011 suffix and bio-similar | **FIXED** | Parentheses, brackets, U+2011 suffix and bio-similar qualifier originals refuse. [Evidence](names/historical_focus.json). |
| M7 M7-B3 Whitespace isotope: `89Zr trastuzumab` | **FIXED** | 89Zr trastuzumab refuses; both trial and sponsor QA evidence 0. [Evidence](names/historical_focus.json). |
| M7 M7-S1 Canonical equality too broad: `Erlotinib, hydrochloride`, `osimertinib,mesylate`, `is a` | **FIXED** | Erlotinib, hydrochloride -> CHEMBL553; osimertinib,mesylate -> CHEMBL3353410; is a -> not_found. [Evidence](names/historical_focus.json). |
| M7 M7-S2 Lone exact stored names: `(E/Z)-AFATINIB`, `RO 09-1978/000`, `Anusol plus hc` and 19-alias set | **FIXED** | All 19 historical non-M5-S2 lone names are restored, including (E/Z)-AFATINIB, RO 09-1978/000, Anusol plus hc. [Evidence](names/alias_regressions.json). |
| M8 M8-B1 [89 Zr] trastuzumab; tab/newline/NBSP mass-element variants | **FIXED** | [89 Zr] and tab/newline/NBSP variants refuse; trial/sponsor QA evidence 0. [Evidence](names/attacks/probe_results.json). |
| M8 M8-B2 bevacizumab-(awwb), bevacizumab-[awwb]; separate osimertinib | **FIXED** | Internal wrappers bevacizumab-(awwb)/-[awwb] refuse; separate osimertinib survives. [Evidence](names/attacks/probe_results.json). |
| M8 M8-B3 bevacizumab⸺awwb and all 26 Unicode Pd characters | **FIXED** | All 26 Unicode Pd characters normalize and refuse the suffix product. [Evidence](names/attacks/unicode_dashes.json). |
| M8 M8-S1 Natural cache rollover in exact 7,511-key sweep | **FIXED** | Original 7,511-key scan completes; adapted scan cache_errors=[]; natural HTTP rollover verified by cost worker. [Evidence](names/adapted_names_m5_summary.json). |
| M8 M8-S2 biosimilar, and osimertinib; semicolon; biosimilar and, osimertinib | **FIXED** | biosimilar, and osimertinib / semicolon / and-comma forms retain CHEMBL3353410. [Evidence](names/m9_attacks/probe_results.json). |
| M8 M8-S3 566C, 9-ac, 5ac | **FIXED** | 566C/9-ac/5ac retain CHEMBL1450/CHEMBL274070/CHEMBL1489. [Evidence](names/attacks/lone_alias_results.json). |
| M8 M8-S4 5.BETA.,20-EPOXY-1,2.ALPHA.,4,7.BETA. | **FIXED** | 5.BETA.,20-EPOXY-1,2.ALPHA.,4,7.BETA. retains CHEMBL428647. [Evidence](names/attacks/lone_alias_results.json). |
| M9 M9-B1 bevacizumab_awwb; bevacizumab-a.w.w.b; bevacizumab-(a.w.w.b); accented/decomposed forms | **FIXED** | All named original positive-key mismatch forms refuse; independent actual HTTP confirms underscore/accent examples and QA evidence 0. [Evidence](names/m9_attacks/probe_results.json). |
| M9 M9-B2 [89.Zr] trastuzumab; 89:Zr trastuzumab; 89.Zr and 89::Zr variants | **FIXED** | Original folded isotope inputs refuse; actual HTTP and trial/sponsor QA evidence 0. [Evidence](names/m9_attacks/probe_results.json). |
| M9 M9-B3 bevacizumab awwb; bevacizumab (awwb)/[awwb]; trastuzumab dkst/(dkst) | **FIXED** | All original whitespace/wrapper suffix forms refuse; HTTP QA evidence 0. [Evidence](names/m9_attacks/probe_results.json). |
| M9 M9-S1 Theophylline in dextrose 5% in plastic container | **FIXED** | Exact lone alias now maps THEOPHYLLINE / CHEMBL1355736 over HTTP200. [Evidence](names/new_alias_confirmation.json). |
| M9 M9-S1 40-o-(2-hydroxyethyl)-rapamycin | **NOT FIXED** | Accepted known over-refusal; EVEROLIMUS and its ID work. [Evidence](names/new_alias_confirmation.json). |
| M9 M9-S1 42-o-(2-hydroxyethyl)rapamycin | **NOT FIXED** | Accepted known over-refusal; EVEROLIMUS and its ID work. [Evidence](names/new_alias_confirmation.json). |
| M9 M9-S1 Trastuzumab--vcmmae conjugate | **NOT FIXED** | Accepted known over-refusal; TRASTUZUMAB VEDOTIN and its ID work. [Evidence](names/new_alias_confirmation.json). |
| M10 M10-B1 isotope inside stored name | **FIXED** | Exact inputs now refuse with no centre and zero trial/sponsor QA evidence: A33 124i; A33 124 i; A33 [124i]; A33 124I; A33-124i [Evidence](names/m10_attacks/focus_results.json). |
| M10 M10-B2 isotope token substituted for substance | **FIXED** | Exact inputs now refuse with no centre and zero trial/sponsor QA evidence: 18F fluorothymidine; 18-F fluorothymidine; [18F] fluorothymidine; 18F nonexistingdrug; 18-F trastuzumab; 90y somatostatin [Evidence](names/m10_attacks/focus_results.json). |
| M10 M10-B3 punctuation consumed neighbor-word budget | **FIXED** | Exact inputs now refuse with no centre and zero trial/sponsor QA evidence: trastuzumab 89 - Zr; trastuzumab [89 - Zr]; trastuzumab 89 _ Zr [Evidence](names/m10_attacks/focus_results.json). |
| M10 M10-B4 separator variants of product qualifiers | **FIXED** | Exact inputs now refuse with no centre and zero trial/sponsor QA evidence: generic-version of bevacizumab; generic_version of bevacizumab; albumin - bound paclitaxel; follow-on-biologic bevacizumab [Evidence](names/m10_attacks/focus_results.json). |
| M11 M11-B1 split isotope element symbol | **FIXED** | All literal reported forms refuse with no centre and zero trial/sponsor evidence; each comma-osimertinib form retains CHEMBL3353410. Inputs: [89Z.r] trastuzumab; 89Z_r trastuzumab; trastuzumab [89Z.r] [Evidence](names/m11_exact.json). |
| M11 M11-B2 fragmented biosimilar suffix | **FIXED** | All literal reported forms refuse with no centre and zero trial/sponsor evidence; each comma-osimertinib form retains CHEMBL3353410. Inputs: bevacizumab a - w w b; bevacizumab - a - w - w - b; bevacizumab a_w_w_b [Evidence](names/m11_exact.json). |
| M11 M11-S1 9-amino-20(s)-camptothecin | **NOT FIXED** | Explicitly accepted known over-refusal; preferred name and exact node ID still select CHEMBL274070. [Evidence](names/alias_loss_controls.json). |
| M11 M11-S1 il-6ra | **NOT FIXED** | Explicitly accepted known over-refusal; preferred name and exact node ID still select CHEMBL1237022. [Evidence](names/alias_loss_controls.json). |
| M11 M11-S1 TAK-659F | **NOT FIXED** | Explicitly accepted known over-refusal; preferred name and exact node ID still select CHEMBL3979920. [Evidence](names/alias_loss_controls.json). |
| M12 M12-B1 split symbol inside chelator-bearing stored alias | **FIXED** | Exact reported [89Z.r]-DFO-daratumumab and 89Z_r-dfo-daratumumab, plus three alternate old cases, refuse with zero qualified trial/sponsor QA evidence. Separate osimertinib survives; bare daratumumab maps correctly. [Evidence](names/m12_attacks/focused_results.json). |
| M12 M12-S1 rad001c / RAD001C stored-alias over-refusal | **FIXED** | rad001c and RAD001C retain EVEROLIMUS / CHEMBL1908360 with 9 stored trials and 9 trial-QA rows, equal to HEAD^. rad, RAD001, EVEROLIMUS and its ID remain available. [Evidence](names/new_alias_regression.json). |
| M12 M12 supplementary previously unpromoted descriptive label-distance inputs | **NOT FIXED** | The old labelled/labeled-distance forms still draw TRASTUZUMAB and match the HEAD^ result. Retained separately from the new joined-chelator blocker, consistent with prior classification. [Evidence](names/m12_attacks/focused_results.json). |
| M13 M13-B1 isotope fused to chelator inside matched alias | **FIXED** | 89ZrDFO-daratumumab, 89zrdfodaratumumab, [89ZrDFO]-daratumumab, 89zrdfo daratumumab and 89Zr-DFOdaratumumab refuse, with zero trial/sponsor evidence. Bare daratumumab maps correctly; separately listed osimertinib survives. [Evidence](names/joined_label_probe.json). |
| M13 M13 supplementary A33124I trailing isotope | **FIXED** | A33124I now refuses, with no centre and zero trial/sponsor QA evidence; A33 124i also refuses. HEAD^ still draws ADAKITUG. The original trailing-label reproduction is repaired. [Evidence](names/m14_exact/fresh_results.json). |
| M14 M14-B1 uppercase one-letter element inside a consumed name | **FIXED** | 3HVINBLASTINE, 3HVinblastine and 3Hvinblastine now refuse with no centre and zero trial/sponsor evidence. Comma-osimertinib selects the separate CHEMBL3353410 and discloses the refusal. [Evidence](names/m14_exact/edge_results.json). |
| M14 M14-B1 supplementary lower-case 3hvinblastine | **NOT FIXED** | The exact lower-case prior example still draws VINBLASTINE / CHEMBL159 with 5 trial and 5 sponsor QA rows. Recorded separately because this round explicitly narrows one-letter own-key handling to an upper-case element; the upper-case repairs must not imply this spelling was fixed. [Evidence](names/m14_exact/edge_results.json). |
| M14 M14-B2 isotope plus drug plus trailing PET/CT marker | **FIXED** | 89Zrpanitumumab-PET-CT, 89ZrpanitumumabPETCT, 89zrpanitumumabpetct and 89Zrpanitumumab PET CT now refuse with zero trial/sponsor evidence. A comma-separated osimertinib survives. [Evidence](names/m14_exact/edge_results.json). |
| M14 M14 supplementary neighbouring fused-label casing | **NOT FIXED** | 89ZRDFO trastuzumab and 89zrDFO trastuzumab still draw TRASTUZUMAB. Properly cased 89ZrDFO trastuzumab refuses. This is the literal prior supplementary observation, separate from new round-15 attacks. [Evidence](names/m14_supplement.json). |
| M14 repair note / user Known ChEMBL bevacizumab development-code synonym limitation | **NOT FIXED** | HLX04, HLX-04, HLX04-O, BAT1706, SB8, MB02, FKB238 and BI 695502 still resolve to CHEMBL1201583. Explicitly user-accepted dictionary limitation, not a map blocker. [Evidence](names/m14_supplement.json). |


### Database, UI and server, m1-m14



The table covers non-name findings from m1-m14. m2 has no completed REPORT; its partial role/order cases are included. Later rounds repeat these fixtures. Name and cost findings belong to the naming and cost matrices. [Historical report inventory](db_ui/historical_report_headings.json).

| Earlier finding / exact reproduction | Round 15 result and evidence |
|---|---|
| M1-B2: collaborator described as lead; `NCT00200395`, reverse `ORG:genentech` | **FIXED**. Lead and collaborator groups retain separate role-aware labels in both directions. `src/app.py:137,160-169`; `web/try.html:142-149`. [DB](db_ui/db_validate.json), [rendered UI](db_ui/ui_harness_results.json). |
| M1-B3: Investigator described as institution; `NCT00754364`, `ORG:armandosantoromd` | **FIXED**. The incoming trial heading says researcher for Investigator. `web/try.html:143,148`. [DB](db_ui/db_validate.json), [UI](db_ui/ui_harness_results.json). |
| M1-B4: retire `CHEMBL3353410` in memory, query `osimertinib`, ID and `EGFR` | **FIXED**. Name and ID return not_found; EGFR has no retired neighbour. `src/app.py:83-84,115-123`. [Real-handler fixture](db_ui/db_retired_center.json). |
| M1: retired Trial still counted for live Drug; retired T -> EVALUATES -> live D, live D -> ACTS_ON -> X | **FIXED**. D centre count and its count/weight under X are zero. `src/app.py:129-132`. [Fixture](db_ui/db_fixtures.json). |
| M1-S1: misleading most-evidence wording and ordering, Disease | **FIXED**. The page states start-date ordering for Trials, graph counts for Drugs, stored counts for sponsor relations, association scores for Disease/Target, and name ordering for equal weights. All-node oracle agrees. `src/app.py:141-170`; `web/try.html:148-158,231-235`. [Oracle](db_ui/db_validate.json). |
| M1-S2: silent ring cut; `CHEMBL1201438`, `MONDO_0005233`, AstraZeneca | **FIXED**. Ring counts and list cuts are disclosed. ALDESLEUKIN draws 22/25; Disease draws 39/3,074 with 30 items in each list. Every exercised nonempty group has ring representatives. `web/try.html:191,204,233`. [UI](db_ui/ui_harness_results.json). |
| M1-S3: stale trail after Mvasi, unknown name, server/network errors | **FIXED**. Terminal states clear trail/buttons; stale back handlers do not throw. `web/try.html:213-216,243-244`. [UI](db_ui/ui_harness_results.json). |
| M1-S4: reverse response order, duplicate clicks, stale network error | **FIXED**. Latest KRAS remains; duplicate completion yields one trail entry. `web/try.html:211-214`. [UI](db_ui/ui_harness_results.json). |
| M1-S5: silent reading and alternatives; Roche, MET, `osimertinib EGFR`, `Mvasi and bevacizumab` | **FIXED for disclosure**. Selected reading, additional company/target and refused-span chips are displayed. `web/try.html:222-226`. [UI](db_ui/ui_harness_results.json). Semantic name resolution is covered by the naming worker. |
| M1-S6: AGONIST/BINDING AGENT gloss and sponsor classes | **FIXED**. Specific Korean glosses retain the stored action/class codes. `web/try.html:161-176`. [UI](db_ui/ui_harness_results.json). |
| M1-S7: missing Trial start, sponsor-to-drug global count/phase, zero Trial count | **FIXED**. `NCT00200395` displays start 2003-07-02; Drug details retain global count/phase alongside sponsor evidence; `CHEMBL925` displays zero. `src/app.py:172-177`; `web/try.html:173-174,228-229`. [UI](db_ui/ui_harness_results.json). |
| M1-S8: node/edge props `null`, `[]`, `{broken`; restoration; 1,001-drug count chunking | **FIXED**. Twelve malformed-property requests and all restored requests return 200; all 1,001 Drugs retain count/weight 1. `src/app.py:127-132,211-217`. [Fixtures](db_ui/db_fixtures.json). |
| M1 URL/script/ID/text injection | **FIXED for exercised generated-markup paths**. Unsafe javascript/data schemes and credential, prefix-host and backslash spoofs are rejected. Labels, IDs and other payload text are escaped; no raw injected image/script or javascript href appears. `web/try.html:104,180,199,221-235`. [UI](db_ui/ui_regressions.json), [assertions](db_ui/ui_assertions.json). |
| M1 unknown type Other / relation NEWREL | **FIXED**. Raw fallback values survive; tooltip is not undefined. [UI](db_ui/ui_regressions.json). |
| M1 module all-three/everything claims | **FIXED**. The module says All of them and a capped list per relation. `src/app.py:5-11`. |
| M2 partial/M2b: missing/unknown SPONSORS role and equal-weight A-Z | **FIXED**. Eight role-property cases return 200; valid roles survive and unspecified roles receive neutral wording. All-node name ordering agrees. [DB](db_ui/db_role_fallback.json), [UI](db_ui/ui_regressions.json), [oracle](db_ui/db_validate.json). |
| M2b-R2: Alaunos/ALDESLEUKIN derived edge props `null`, `[]`, `{broken`, `{}`, both endpoints | **FIXED**. Missing count remains `evidence_trials:null` with sort weight zero and displays not recorded. Actual numeric zero remains zero. `src/app.py:141-146`; `web/try.html:173`. [DB](db_ui/db_missing_sponsor_count.json), [UI](db_ui/ui_missing_sponsor_count.json), [zero controls](db_ui/ui_m3_checks.json). |
| M2b: boolean association score and hidden decimal rounding | **FIXED**. Bool becomes unknown; both directions return 200; exact stored decimal 0.8883707400322897 is retained. [DB](db_ui/db_score_fixture.json), [UI](db_ui/ui_regressions.json). |
| M2b/M3: `phases='PHASE2'` render error through form/node/back/example | **FIXED**. All four callbacks catch the error, clear state and recover; stale malformed response is ignored. `web/try.html:239-248`. [Callbacks](db_ui/ui_m3_checks.json). |
| M3/M4 repeated blank/whitespace submission qualification | **NOT FIXED**, unchanged nonblocker. No request is made; previous view remains. `web/try.html:241`. [Callbacks](db_ui/ui_m3_checks.json). |
| M3/M4 repeated positive/negative Infinity qualification | **NOT FIXED**, unchanged failure closed. The real handler returns controlled 400; no invalid map value is drawn and snapshot has none. `src/app.py:207-208,264-269`. [Fixture](db_ui/db_numeric_fixture.json). |
| M1/M2b silent truncation: "x"*500 + " osimertinib" and "osimertinib " + "x"*600 | **FIXED**. Both exact oversized inputs return 400 with `input is longer than 500 characters`; neither silently draws the retained prefix. `src/app.py:239-243`. [Fresh root HTTP](root_checks/http_results.json). |
| M1/M2b malformed JSON/list/null/oversized-body parser-error disclosure | **NOT FIXED**, inherited nonblocking qualification. Requests fail closed with 400; list/null bodies still expose `.get` errors and the 20,000-byte body cap can expose JSON parser text. Valid later calls succeed. `src/app.py:236-240,264-269`. [Fresh root HTTP](root_checks/http_results.json). |

All six live node types and all 22 existing relation combinations are covered. The snapshot has **7 retired nodes, 142 retired edges, zero self-loops and zero live edges with retired endpoints**. PARENT_OF, STUDIES, ASSOCIATED_WITH, EVALUATES, ACTS_ON and role-aware SPONSORS agree with stored endpoints. All 3,000 stored URLs are registry HTTPS URLs, and all node/edge props are valid JSON objects. [Snapshot](db_ui/db_snapshot_facts.json), [oracle](db_ui/db_validate.json). The self-loop result is a fixture result, not a snapshot claim.

## Known limitations and regressions

The expressly accepted M5-S2, `40-o-(2-hydroxyethyl)-rapamycin`, `42-o-(2-hydroxyethyl)rapamycin`, `Trastuzumab--vcmmae conjugate`, `9-amino-20(s)-camptothecin`, `il-6ra` and `TAK-659F` remain **NOT FIXED / known over-refusals**, not blockers. `rad001c` and `RAD001C` remain restored to EVEROLIMUS. [Alias controls](names/alias_loss_controls.json), [current/previous controls](names/new_alias_regression.json).

`HLX04`, `HLX-04`, `HLX04-O`, `BAT1706`, `SB8`, `MB02`, `FKB238` and `BI 695502` still select BEVACIZUMAB. This is the user's explicitly recorded ChEMBL synonym limitation, **not a map defect**. [Fresh code controls](names/m14_supplement.json).

Old distant-label and fragmented-qualifier supplements remain where previously recorded: for example `trastuzumab labelled with 89Zr`, `89Zr labeled trastuzumab`, `b.i.o.similar bevacizumab` and `lip.osomal doxorubicin`. They are reported as **NOT FIXED supplementary gaps**, not newly discovered families. The old casing observations `89ZRDFO trastuzumab` and `89zrDFO trastuzumab` likewise remain. [Reused focused matrix](attacks/focused_results.json), [exact old supplements](names/m14_supplement.json). This does not weaken the independently sufficient new punctuation-only reproduction.

The raw stored-alias loss set is unchanged versus m14. Ordinary controls `13-cis retinoic acid`, `BKM-120NX`, `NSC-118218H`, `DX-8951F`, `GW572016F`, `osimertinib 80 mg`, `paclitaxel 2 cycles` and `cisplatin 75 mg/m2 day 1` preserve their identities. Upper-case M14 cases and PET/CT variants are repaired. No new demo regression or stored-value defect was observed. [Targeted controls](attacks/targeted_results.json), [independent dose controls](root_checks/independent_m14_http.json).

Failure-closed presentation qualification: the exact slash-bearing control `89zr-panitumumab-pet/ct` returns HTTP 200 with `not_found`, rather than an explicit `refused` message. It draws no centre. This should-fix distinction must not be described as an explicit refusal; the reported M14-B2 glued/hyphen PETCT reproductions do explicitly refuse. [Exact HTTP response](root_checks/independent_m14_http.json).

## Cost and performance reproductions

All **nine inherited cost scripts** exited zero, run sequentially after the other reviewers' CPU/HTTP work finished. Unrelated host activity is uncontrolled. Timings are observations, not service-level guarantees or proof of global complexity. Historical comparisons substitute only `query.py` against the same current remaining modules and database. [Execution](cost/execution_isolated.json), [provenance](reuse_manifest_root.json).

| Historical reproduction / exact workload | Current result and disposition |
|---|---|
| M5-S3 cubic scan, `' '.join(['x']*250)` (499 characters) | **FIXED for this original workload**: 2,224 calls to each predicate, 33,880 aggregate predicate-input characters, **0.02714 s** direct linking. [Instrumentation](cost/perf_current.json). |
| Original 999-character plain-answer timeout, `' '.join(['x']*500)` | **FIXED**: `/api/check` 200 in **0.18501 s**; subsequent ordinary map **0.03396 s**. [HTTP](cost/perf_check_http.json). |
| M6/M7 repeated 2,000-piece resolver cost, `';'.join(['x']*2000)` | **FIXED for this exact repeated-piece control**: current direct median **0.16089 s**, historical `9bd7cb4` **1.83930 s**. HTTP check **0.44876 s**, queued EGFR **0.36582 s**, both 200. [Comparison](cost/fresh_cost_comparison.json), [HTTP](cost/fresh_cost_http.json), [stress](cost/cost_stress.json). |
| M8-S1 natural 4,097th cache entry | **FIXED**: 82/82 fill requests create 4,096 entries; first OSIMERTINIB at rollover and retry both 200 / CHEMBL3353410 / 79 trials. No KeyError. [HTTP](cost/cache_boundary_http.json). |
| M10-M14 distinct-piece lock contention, `';'.join(f'isa x{i:04d}' for i in range(400))` (3,999 answer characters) | **NOT FIXED**, inherited cost concern: cold check **2.22862 s**, queued EGFR **2.14571 s**, warm **0.32572 s**, all 200. 400 cold / 0 warm resolver calls. [HTTP](cost/isolated_unique_cost_http.json), [instrumentation](cost/unique_piece_cost.json). |
| M11-M14 Unicode expansion, answer `'\ufdfa'*4000` | **NOT FIXED**, inherited cost concern: 4,000 characters expand to 72,000 under NFKC; cold check **2.44682 s**, queued EGFR **2.36587 s**, warm **2.74905 s**, all 200. [HTTP](cost/isolated_unicode_cost_http.json). |
| M11-M14 punctuation normalization, `' - '.join(['x']*1000)+'xx'` | **NOT FIXED as measured overhead**, no failure: current / HEAD^ medians **0.37395 / 0.30708 s**; at 499 characters **0.03763 / 0.03517 s**. [Comparison](cost/normalization_cost.json). |
| M12-M14 repeated matches, `' '.join(['isa']*1000)` | **NOT FIXED as measured overhead**, no failure: current / HEAD^ medians **1.01583 / 1.00400 s**; at 499 characters **0.03314 / 0.03479 s**. [Comparison](cost/normalization_cost.json). |
| M13/M14 repeated isotope alias, `';'.join(['A33 124i']*444)` | **No error reproduced**: current / HEAD^ medians **0.06961 / 0.07185 s**. Cached OSIMERTINIB **0.00013 / 0.00012 s**. All 24 version/workload rows finish; three samples each do not establish a statistical regression/speedup. [Comparison](cost/normalization_cost.json). |
| Disease / ordinary concurrent maps | **No failure reproduced**: 2,774 Trials + 300 Targets, 30 per list, **18,575 bytes / 68.325 ms**. 24 requests / 12 workers all expected HTTP 200 shapes, **619.995 ms** total. These early ordinary samples overlapped other audit work. [HTTP](root_checks/http_results.json). |

`engine.lock` serializes operations (`src/app.py:247-263`), so costly legal check-answer requests delay maps. The 3,999/4,000-character stresses are direct-link or **answer-field** cases; explore correctly rejects input longer than 500 characters. Input limits precede NFKC (`src/app.py:239-243,260`; `src/query.py:116-117,203-205`). No deadlock or invented value was observed. These inherited costs remain should-fix items and do not determine the verdict. **No model call or model cost was incurred.**

## Standards and specification

**Standards axis: zero documented violations found.** The app/UI diff from `bfcb83d` and latest query/test patch were reviewed. No tracked repository AGENTS.md, CONTRIBUTING.md, CODING_STANDARDS.md or issue-tracker instructions were found. User-provided evidence-based, m15-only and no-tracked-edit requirements govern. The requested KOA Studio / KhOpenApi original-versus-modified-code comparison is conditional on changing application code; none was changed. [Standards record](db_ui/standards_review.json).

**Specification axis: one new P1 family and one unresolved P1 family.** M15-B1 is a new reproduction of an inherited neighbouring-label normalization defect; M15-B2 records the lower-case residual of M14-B1 with an A33 corroboration. The latest upper-case, PET/CT and `A33124I` repairs work as described, but the original no-originator-leak approval bar remains unmet. The new finding alone suffices. [Independent attack assessment](attacks/FINDINGS.md), [separate adjudication](db_ui/adjudication.md).

README app descriptions remain accurate (`README.md:566`, `README.ko.md:387`). Nearby comments still say 317 tests: **NOT FIXED**, documentation-only should-fix; the actual suite has 342 passing tests. [Source assessment](db_ui/FINDINGS.md).

## Integrity and reproduction

`Engine.ask` explicitly sets `use_llm=False` (`src/app.py:180-181`); explore follows SELECT paths. Mutation fixtures use in-memory copies. The application does not enforce a globally read-only SQLite handle; the no-write conclusion rests on inspected/executed paths and byte equality, not a DB-permission guarantee.

Final verification compares **5,104 tracked-file SHA-256 hashes**, HEAD, tracked/staged diffs, database bytes, report links and owned-port cleanup. [Initial snapshot](integrity_before.json), [final verification](integrity_final.json). Database SHA-256: `7341c5a7089731f67356da5a588b269d4b69e8e6c4c054acf19aa4ef2837b529`.

Run from repository root with bytecode disabled and TMP/TEMP/TMPDIR under each m15 family's `tmp/`. Run shared-port suites sequentially and cost after other workloads. The manifests identify original scripts and adaptations; do not overwrite the initial integrity snapshot.

```text
python -B audit_evidence_claims/m15/root_checks/run_all.py
python -B audit_evidence_claims/m15/root_checks/run_rounds12_13.py
python -B audit_evidence_claims/m15/root_checks/independent_m14_http.py
python -B audit_evidence_claims/m15/root_checks/independent_m15_http.py
python -B audit_evidence_claims/m15/names/run_round9.py
python -B audit_evidence_claims/m15/names/run_additional.py
python -B audit_evidence_claims/m15/names/run_completion.py
python -B audit_evidence_claims/m15/db_ui/run_db.py
python -B audit_evidence_claims/m15/db_ui/run_ui.py
python -B audit_evidence_claims/m15/db_ui/run_final.py
python -B audit_evidence_claims/m15/attacks/targeted_probe.py
python -B audit_evidence_claims/m15/attacks/targeted_http.py
python -B audit_evidence_claims/m15/cost/run_isolated.py
python -B audit_evidence_claims/m15/build_report.py
python -B audit_evidence_claims/m15/finalize_integrity.py
```

VERDICT: CHANGES REQUIRED
