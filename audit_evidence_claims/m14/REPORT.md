# Independent relation-map review — round 14

Reviewed **`73ee310d970c8c3b4886bbbdfd6d88026d403c28`**. **Changes required: two P1 findings**, one regression introduced by the latest patch and one inherited refusal bypass. `3HVINBLASTINE` and `89Zrpanitumumab-PET-CT` pass every refusal stage and draw their originator molecules. The main M13 DARATUMUMAB reproductions are fixed; its supplementary `A33124I` example is still **NOT FIXED**.

No tracked file was edited. All new scripts, temporary files and results are under `audit_evidence_claims/m14/`. Existing m14 brief/log files were not edited by the audit. Known accepted over-refusals are retained as nonblockers. The verdict rests on reproduced originator leaks, not those over-refusals or performance observations.

## Verification and scope

- **341 passed in 30.33 s**, exit 0, using the requested `python -m pytest tests -q -p no:cacheprovider`; bytecode disabled and temporary paths confined to m14. [Output](root_checks/pytest.txt), [execution and hashes](root_checks/pytest_summary.json).
- Cumulative original HTTP reproducers were rerun, including the original m1 audit, m2b-m10 additions, exact m11 cases, and m12/m13 confirmations. All batches exit 0. Source scripts were reused with output-path/owned-port adaptations; original case inputs were retained. [Root manifest](reuse_manifest_root.json), [main batches](root_checks/execution_all.json), [m6](root_checks/execution_m6_http.json), [remaining](root_checks/execution_remaining.json), [m12/m13](root_checks/execution_rounds12_13.json).
- **55 reused name scripts / 45 executed leaf reproductions**, all exit 0, and **64 individual historical disposition rows** below. Replays include the **7,511-key** alias sweep and the **1,648-question** frozen counterfactual. Zero new lone-alias losses; `rad001c` alone recovered. The frozen comparison remains **68 identical / 1,556 metadata-only / 24 semantic / zero errors**. These comparisons swap methods against the same current data; they are not reconstructed historic deployments. [Name verification](names/FINDINGS.md), [manifest](names/reuse_manifest.json), [execution checks](names/worker_final_checks.json).
- Independent database oracle: **6,469 live centres, 22 relation/direction/type/role combinations, zero errors**. **19/19 DB assertions**, **24/24 UI assertions**, **4/4 self-loop/unknown-type/retirement fixture checks** pass. [Oracle](db_ui/db_validate.json), [DB](db_ui/db_assertions.json), [UI](db_ui/ui_assertions.json), [fixture](db_ui/self_loop_unknown.json).
- **36/36 page demos and six map callbacks pass**. All full demo objects equal each m7-m13 baseline. All 36 fresh CLI HTTP demo responses are 200 and equal direct Engine responses. Original QA evidence counts remain **12, 12, 11, 1, 12, 0, 0**. [Comparisons](db_ui/demo_previous_comparison.json), [HTTP](db_ui/demo_http.json), [callbacks](db_ui/ui_m3_checks.json).
- Attack matrices contain **97 current/HEAD^ direct comparison cases** and **308 final HTTP responses**, all HTTP 200. The root independently confirmed 24 cases through **96 HTTP requests**, and a separate reviewer traced both failures through `_marked` and the complete linker. [Attack execution](attacks/execution.json), [stages](attacks/edge_results.json), [independent HTTP](root_checks/independent_m14_http.json), [lifecycle](root_checks/independent_m14_lifecycle.json), [independent adjudication](db_ui/adjudication.md).

UI checks execute the actual page JavaScript in a Node VM with controlled DOM/fetch stubs. They verify generated markup and the exercised state/callback paths, not browser painting or browser-executed XSS. HTTP uses unmodified `src/app.py` or its real handler with isolated in-memory fixtures. No audit used port 8765 or called a model. Drug identity evidence comes from the repository dictionary, canonical keys and refused controls; no external pharmacology assumption is needed.

The successful raw-alias sweep does not cover every separator-removal/case variant of those aliases. It therefore does not contradict the transformed-alias regression below.

## M14-B1 — a consumed one-letter-isotope alias bypasses the case-marked check (regression)

**Exact HTTP:** `POST /api/explore`, JSON `{"text":"3HVINBLASTINE"}`. HTTP 200 draws **VINBLASTINE / CHEMBL159**, matched alias **`[3h]-vinblastine`**, with **5 live trials**, and no refusal. `Which trials evaluate 3HVINBLASTINE?` and `Who sponsors trials of 3HVINBLASTINE?` each return **5 originator evidence rows**. `3HVinblastine`, `3Hvinblastine`, and `3hvinblastine` do the same. With `3Hvinblastine, osimertinib`, the wrong first centre is still VINBLASTINE. [Full stages and previous comparison](attacks/edge_results.json), [HTTP](attacks/edge_http.json).

**Control and identity:** `[3h]-vinblastine` and `[3H]vinblastine` are refused, with zero trial/sponsor evidence. Their canonical key is the same **`3hvinblastine`** as the accepted input, uniquely naming the stored tracer alias of VINBLASTINE. Bare `vinblastine` remains available. For the deliberately case-marked input **`3HVINBLASTINE`**, `_isotope_edge` returns **true**. Thus this finding does not depend on reading lower-case chemistry as an isotope. [Dictionary, helper result, key checks](attacks/dictionary_evidence.json).

The HEAD^ query module refuses all four glued spellings and selects the separate OSIMERTINIB in the comma control. This is a **current-patch regression**, established with the same current app, normalization/rules, and database and only `query.py` replaced in memory. It is not a reconstructed old deployment. [Version-labelled direct results](attacks/edge_results.json).

**Cause:** positive matching consumes the complete alias (`src/query.py:450-470`). The new helper is called only on **outside neighbouring words** (`src/query.py:317-320`), never on the consumed name's `own` words. The inside scan (`src/query.py:282-297,321-323`) recognizes whole isotope labels but cannot split `3HVINBLASTINE`. The revised key fallback excludes one-letter elements and starts its prefix-length loop at 3 (`src/query.py:327-337`), although `3H` has length 2. The previous key fallback refused this canonical alias. The comment saying that one-letter elements are left to the case-marked check is ineffective for a consumed alias.

**Required outcome:** preserve refusal for a known tracer alias when its isotope separator is removed, including the case-marked form the new helper already recognizes, without broadening lower-case dose/chemistry interpretation.

## M14-B2 — a two-letter-isotope alias with a trailing PET/CT marker still maps its originator (inherited)

**Exact HTTP:** `POST /api/explore`, JSON `{"text":"89Zrpanitumumab-PET-CT"}`. HTTP 200 draws **PANITUMUMAB / CHEMBL1201827**, matched alias **`89zr-panitumumab-pet/ct`**, with **8 live trials**. Trial and sponsor QA return **8 / 7 originator evidence rows**. There is no Refused entity or refusal notice. [HTTP](attacks/edge_http.json), [stages](attacks/edge_results.json).

**Minimal control:** **`89Zr-panitumumab-PET-CT`** refuses and yields zero QA evidence. Removing only the hyphen between the isotope and the drug causes the leak. Both strings have canonical key **`89zrpanitumumabpetct`**, uniquely pointing to the same stored AACT alias. `89Zr panitumumab PET CT` also refuses; bare `panitumumab` still works. Fully glued `89ZrpanitumumabPETCT`, lower-case `89zrpanitumumabpetct`, and `89Zrpanitumumab PET CT` leak too. Appending `, osimertinib` does not prevent the wrong PANITUMUMAB centre. [Dictionary evidence](attacks/dictionary_evidence.json), [compact matrix](attacks/edge_summary.json).

**Cause:** the isotope is fused inside a consumed alias, so it is neither a whole isotope word nor an outside neighbour (`src/query.py:282-323`). `_isotope_edge('89Zrpanitumumab')` is true, but this helper is never applied to that own word. The final fallback isolates `89zr` but requires the remaining key **to end with** a same-drug key of at least five characters (`src/query.py:329-334`). `panitumumabpetct` does not end in any such key: the stored imaging marker follows the drug name. Allowing arbitrary text only **between** the isotope and a terminal same-drug name does not protect this actual stored tracer alias. The HEAD^ query module has the same leak, so this is inherited, not a newly introduced regression.

**Required outcome:** normalization of a stored refused tracer alias must preserve its refused identity even when the alias includes a trailing imaging marker.

## Every stage for both blockers

| Stage | `3HVINBLASTINE` | `89Zrpanitumumab-PET-CT` |
|---|---|---|
| Raw intervention resolver | ALIAS / CHEMBL159 | ALIAS / CHEMBL1201827 |
| `_qualified` | false | false |
| Resolver veto | `{}` | `{}` |
| Item linker | Drug; no Refused | Drug; no Refused |
| Whole-name shortcut | `None` | `None` |
| Public linker | VINBLASTINE; no Refused | PANITUMUMAB; no Refused |
| Map centre / live trial count | CHEMBL159 / 5 | CHEMBL1201827 / 8 |
| Qualified trial / sponsor QA rows | 5 / 5 | 8 / 7 |

The raw tracer predicate expects a boundary after the element (`src/textrules.py:303-314`), so the normalized raw resolver also misses the guard (`src/normalize.py:738-746`). `Engine.explore` selects the surviving first positive hit (`src/app.py:88-95`). These are not cases where the map ignores an already-recorded refusal; **all refusal paths miss**. The relationships shown may be valid for the originator but are attached to a wrongly selected centre.

Both findings were independently reproduced over the unmodified CLI server. The root responses contain the same centre IDs and **5/5** or **8/7** qualified QA evidence counts; the separated controls refuse. The second reviewer recorded `_marked` returning `None` for both current candidates. [Root confirmation](root_checks/independent_m14_http.json), [separate stage traces](db_ui/adjudication_tracer.json). No repair was implemented in this audit.

## Earlier reproductions — FIXED / NOT FIXED per finding

Dispositions classify the exact prior reproductions. A repaired spelling does not imply that every equivalent spelling is safe. m2 stopped without a completed report; its partial fixtures and the completed m2b findings are included. Known historical limitations remain visible instead of being counted as repaired.

### Name resolution, m1–m13


M2 has no completed report; partial name cases are covered by M2b's cumulative reproductions. Other workers cover DB, UI, cost and root HTTP evidence.

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
| M12 M12-S1 rad001c / RAD001C stored-alias over-refusal | **FIXED** | rad001c and RAD001C now select EVEROLIMUS / CHEMBL1908360 with 9 stored trials and 9 trial-QA rows; HEAD^ still refuses. rad, RAD001, EVEROLIMUS and its ID remain available. [Evidence](names/new_alias_regression.json). |
| M12 M12 supplementary previously unpromoted descriptive label-distance inputs | **NOT FIXED** | The old labelled/labeled-distance forms still draw TRASTUZUMAB and match the HEAD^ result. Retained separately from the new joined-chelator blocker, consistent with prior classification. [Evidence](names/m12_attacks/focused_results.json). |
| M13 M13-B1 isotope fused to chelator inside matched alias | **FIXED** | 89ZrDFO-daratumumab, 89zrdfodaratumumab, [89ZrDFO]-daratumumab, 89zrdfo daratumumab and 89Zr-DFOdaratumumab refuse, with zero trial/sponsor evidence. Bare daratumumab maps correctly; separately listed osimertinib survives. [Evidence](names/joined_label_probe.json). |
| M13 M13 supplementary A33124I trailing isotope | **NOT FIXED** | A33124I still draws ADAKITUG / CHEMBL5314551 via stored A33 124i; spaced control refuses. M13 recorded this as a supplementary corroboration, not a separately counted blocker. The originator gap remains. [Evidence](attacks/fresh_results.json). |


### Database, UI and server, m1–m13


The table covers non-name findings from m1-m13. m2 has no completed REPORT; its partial role/order cases are included. Later rounds repeat these fixtures. Name and cost findings belong to the naming and cost matrices. [Historical report inventory](db_ui/historical_report_headings.json).

| Earlier finding / exact reproduction | Round 14 result and evidence |
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

## Supplementary cases and accepted over-refusals

The explicitly accepted M5-S2, `40-o-(2-hydroxyethyl)-rapamycin`, `42-o-(2-hydroxyethyl)rapamycin`, `Trastuzumab--vcmmae conjugate`, `9-amino-20(s)-camptothecin`, `il-6ra` and `TAK-659F` remain **NOT FIXED / known over-refusals**, not blockers. In contrast, M12/M13 `rad001c` and `RAD001C` are now **FIXED**: EVEROLIMUS / CHEMBL1908360, nine live trials. [Fresh alias comparisons](names/new_alias_regression.json), [root HTTP](root_checks/independent_m13_http.json).

M13's supplementary **`A33124I` remains NOT FIXED**: it still maps ADAKITUG / CHEMBL5314551, while `A33 124i` refuses. Both keys are `a33124i`. This has zero trial/sponsor QA evidence but still draws the originator; it is a residual previously reported example, not a third newly counted finding. The complete M13 finding family therefore cannot be called fully repaired. [Exact previous/current stages](attacks/fresh_results.json), [root HTTP](root_checks/independent_m13_http.json).

`99MTc trastuzumab` and `[99MTc] trastuzumab` remain **FIXED**. The earlier descriptive-distance isotope and punctuated lexical-qualifier cases remain **NOT FIXED** where recorded, including `trastuzumab labelled with 89Zr`, `89Zr labeled trastuzumab`, `b.i.o.similar bevacizumab` and `lip.osomal doxorubicin`; they are retained as supplementary observations rather than newly counted findings. `Lutetium (177L.u) dotatate` remains **FIXED** (its historical centre was already isotope-labelled). [Original small replay](root_checks/fresh_probe.json), [reused 41-case matrix](attacks/focused_results.json), [attack assessment](attacks/FINDINGS.md).

Additional neighbouring-word casing boundary: `89ZRDFO trastuzumab` and `89zrDFO trastuzumab` draw TRASTUZUMAB, while `89ZrDFO trastuzumab` refuses. The helper requires exact upper/lower casing for two-letter elements too (`src/query.py:133-134`). This is recorded without inflating the two stored-alias findings. [Stage evidence](attacks/extra_neighbors.json).

The exact controls `13-cis retinoic acid`, `BKM-120NX`, `osimertinib 80 mg`, `paclitaxel 2 cycles` and `cisplatin 75 mg/m2 day 1` still select their intended Drugs. [Independent HTTP](root_checks/independent_m14_http.json).

## Cost and performance reproductions

All nine inherited cost scripts exited 0, sequentially after the other reviewers finished their CPU/HTTP workloads. Unrelated host activity is uncontrolled. Timings are observations, not service-level guarantees or proof of global complexity. Historical comparisons substitute only `query.py` against the same current remaining modules and database. [Execution](cost/execution_isolated.json), [source provenance](reuse_manifest_root.json).

| Historical reproduction / exact workload | Current observation and disposition |
|---|---|
| M5-S3 cubic all-runs scan, `' '.join(['x']*250)` (499 characters) | **FIXED for the original workload**: 2,224 calls per predicate, 33,880 aggregate predicate-input characters; direct linking **0.02855 s**. [Instrumentation](cost/perf_current.json). |
| Original 999-character plain-answer timeout, `' '.join(['x']*500)` | **FIXED**: `/api/check` HTTP 200 in **0.19408 s**; subsequent ordinary map **0.02116 s**. [HTTP](cost/perf_check_http.json). |
| M6/M7 repeated 2,000-piece resolver cost, `';'.join(['x']*2000)` | **FIXED for this exact repeated-piece control**: current direct-link median **0.16059 s** versus historical `9bd7cb4` **1.79161 s**. HTTP check **0.44417 s**, queued EGFR **0.36103 s**, both 200. [Comparison](cost/fresh_cost_comparison.json), [HTTP](cost/fresh_cost_http.json), [stress](cost/cost_stress.json). |
| M8-S1 natural 4,097th resolver-cache entry | **FIXED**: 82/82 fill requests create 4,096 distinct entries; first osimertinib at rollover and retry both HTTP 200 / CHEMBL3353410 / 79 trials. No KeyError. [HTTP](cost/cache_boundary_http.json). Original 7,511-key sweep also completes. |
| M10/M11/M12/M13 distinct-piece lock contention, `';'.join(f'isa x{i:04d}' for i in range(400))` (3,999 answer characters) | **NOT FIXED**, inherited cost concern: cold check **2.21735 s**, queued ordinary EGFR **2.13464 s**, warm check **0.33769 s**, all 200. Instrumentation: 400 cold / 0 warm resolver calls. [HTTP](cost/isolated_unique_cost_http.json), [instrumentation](cost/unique_piece_cost.json). |
| M11–M13 Unicode expansion, answer `'\ufdfa'*4000` | **NOT FIXED**, inherited cost concern: 4,000 input characters become 72,000 under NFKC; check **2.81401 s**, queued EGFR **2.73872 s**, warm **3.65129 s**, all 200. [HTTP](cost/isolated_unicode_cost_http.json). |
| M11–M13 punctuation normalization, `' - '.join(['x']*1000)+'xx'` (3,999 characters) | **NOT FIXED as measured overhead**, no timeout/data error: current / HEAD^ direct-link medians **0.31497 / 0.30591 s**; at 499 characters **0.03769 / 0.03577 s**. [Comparison](cost/normalization_cost.json). |
| M12/M13 repeated matches in one item, `' '.join(['isa']*1000)` | **NOT FIXED as measured overhead**, no failure: current / HEAD^ medians **1.04694 / 1.20577 s**. At 499 characters: **0.04365 / 0.03345 s**. [Comparison](cost/normalization_cost.json). |
| M13 repeated isotope alias, `';'.join(['A33 124i']*444)` | Current / HEAD^ medians **0.08935 / 0.07325 s**. No error. Cached osimertinib **0.00016 / 0.00011 s**. All 24 version/workload rows complete; three samples each do not establish a statistical regression/speedup. [Comparison](cost/normalization_cost.json). |
| Disease / ordinary concurrent map requests | Disease: 2,774 Trials + 300 Targets, 30 per list, **18,575 bytes / 71.480 ms**. 24 requests / 12 workers all expected HTTP 200 shapes, **713.299 ms** total. These ordinary samples overlapped early audit work. [HTTP](root_checks/http_results.json). |

`engine.lock` serializes engine operations (`src/app.py:247-263`), so costly legal check-answer requests delay maps. The 3,999/4,000-character stresses are direct-link or **answer-field** cases; `/api/explore` correctly rejects text over 500 characters. Limits precede NFKC (`src/app.py:239-243,260`; `src/query.py:116-117,190-192`). No deadlock or invented graph value was observed. These costs remain should-fix items; they do not determine the refusal verdict. No model cost was incurred.

## Standards and specification

**Standards axis: zero documented violations found.** The application/UI diff from `bfcb83d` and latest query/test patch were inspected. No tracked repository AGENTS.md, CONTRIBUTING.md, CODING_STANDARDS.md or issue-tracker instructions were found. User-provided evidence-based, m14-only and no-tracked-edit requirements govern. KOA Studio / KhOpenApi original-versus-modified-code comparison applies when changing application code; none was changed. [Standards record](db_ui/standards_review.json).

**Specification axis: two P1 findings**, M14-B1 (regression) and M14-B2 (inherited). The main M13 repair works, but every refusal stage misses these stored-tracer variants. Correct edges around an incorrectly chosen originator do not meet the approval bar. The residual M13 `A33124I` example also remains unresolved. [Independent specification assessment](attacks/FINDINGS.md), [separate adjudication](db_ui/adjudication.md).

README app descriptions remain accurate (`README.md:566`, `README.ko.md:387`). The nearby test-count comments still say 317: **NOT FIXED**, a documentation-only should-fix; the actual suite has 341 passing tests. [Source assessment](db_ui/FINDINGS.md).

## Integrity and reproduction

`Engine.ask` sets `use_llm=False` (`src/app.py:180-181`); explore follows SELECT paths. Mutation fixtures use in-memory database copies. The app does not globally enforce a read-only SQLite handle, so the no-write result rests on source inspection, executed paths and byte equality rather than a database-permission guarantee.

Final checks compare **4,632 tracked-file SHA-256 hashes**, HEAD, tracked/staged diffs, database bytes, report links and owned-port cleanup. [Initial snapshot](integrity_before.json), [final verification](integrity_final.json). Database SHA-256: `7341c5a7089731f67356da5a588b269d4b69e8e6c4c054acf19aa4ef2837b529`.

Run from the repository root with bytecode disabled and TMP/TEMP/TMPDIR under the corresponding m14 family. Run shared-port suites sequentially and benchmarks after other suites. The manifests preserve original sources and adaptations; do not overwrite the initial integrity snapshot.

```text
python -B audit_evidence_claims/m14/root_checks/run_all.py
python -B audit_evidence_claims/m14/root_checks/run_rounds12_13.py
python -B audit_evidence_claims/m14/root_checks/independent_m14_http.py
python -B audit_evidence_claims/m14/names/run_round9.py
python -B audit_evidence_claims/m14/names/run_additional.py
python -B audit_evidence_claims/m14/names/run_completion.py
python -B audit_evidence_claims/m14/names/joined_label_probe.py
python -B audit_evidence_claims/m14/db_ui/run_db.py
python -B audit_evidence_claims/m14/db_ui/run_ui.py
python -B audit_evidence_claims/m14/db_ui/run_final.py
python -B audit_evidence_claims/m14/attacks/run.py
python -B audit_evidence_claims/m14/cost/run_isolated.py
python -B audit_evidence_claims/m14/build_report.py
python -B audit_evidence_claims/m14/finalize_integrity.py
```

VERDICT: CHANGES REQUIRED
