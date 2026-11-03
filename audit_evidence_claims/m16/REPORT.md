# Independent relation-map review — round 16

Reviewed **`8ebd6629b51a474f216457c8c00f20152304bd1d`**. **CHANGES REQUIRED: one new P1 originator-refusal bypass is sufficient.** `I-124-labelled trastuzumab` passes every refusal stage and draws unlabelled TRASTUZUMAB with its clinical-trial evidence. The equivalent mass-first control refuses. This gap also exists in HEAD^; it is newly reproduced here, not demonstrated to have been introduced by the latest patch.

All exact previously promoted M1–M15 name blockers are **FIXED**, including M15-B1 `89-ZrDFO trastuzumab`, M15-B2 `3hvinblastine`, and the lower-case `A33124i` corroboration. The historical tables retain unresolved supplemental/availability/UI/cost qualifications. The explicitly accepted over-refusals and ChEMBL bevacizumab-code limitation do not determine this verdict.

All new scratch files are under `audit_evidence_claims/m16/`. No application code or tracked file was edited.

## Verification and scope

- **343 passed in 39.54 s**, exit 0: `python -m pytest tests -q -p no:cacheprovider`. Bytecode disabled and temporary paths confined to m16. [Output](root_checks/pytest.txt), [execution and hashes](root_checks/pytest_summary.json).
- Reused cumulative HTTP scripts cover m1, partial m2/completed m2b, m3–m11 and literal m12–m15 confirmations. All root batches exit zero. [Original-script provenance](reuse_manifest_root.json), [main execution](root_checks/execution_all.json), [remaining](root_checks/execution_remaining.json), [late execution](root_checks/execution_late.json).
- **58 copied historical name scripts / 49 executed leaf reproductions**. The naming table has **76 dispositions: 60 FIXED / 16 NOT FIXED**; status is separate from severity. Raw **7,511-key** sweep has exactly the two user-accepted new losses, `GS-11CAL-101` and `3en3hg4wsw`. Adapted frozen **1,648-question** comparison remains **68 identical / 1,556 metadata-only / 24 semantic / zero errors**. [Name assessment](names/FINDINGS.md), [checks](names/worker_final_checks.json), [raw alias differences](names/new_alias_losses.json), [counterfactual](names/adapted_frozen_qa_relink_sweep.json).
- Stored-row oracle: **6,469 live centres / 22 relation-direction-type-role combinations / zero errors**. **19/19 DB**, **24/24 UI**, and **4/4 self-loop/unknown-type/retirement** assertions pass. [Oracle](db_ui/db_validate.json), [DB](db_ui/db_assertions.json), [UI](db_ui/ui_assertions.json), [fixture](db_ui/self_loop_unknown.json).
- **36/36 demos** exactly match every m7–m15 full-response baseline; **36/36 fresh CLI HTTP demos** return 200 and equal direct Engine responses. Six map callbacks pass. Original seven QA evidence counts remain **12, 12, 11, 1, 12, 0, 0**. [Baselines](db_ui/demo_previous_comparison.json), [HTTP](db_ui/demo_http.json), [callbacks](db_ui/ui_m3_checks.json).
- Attack worker reran **97 original m14 + 29 original m15 cases**, then **42 new current/HEAD^ stage cases and 168 HTTP requests**, all 200. Root independently confirms **19 paired cases / 76 HTTP requests**; a third reviewer independently traces the stages. [Attack execution](attacks/execution_summary.json), [new stages](attacks/new_results.json), [new HTTP](attacks/new_http.json), [root HTTP](root_checks/independent_m16_http.json), [independent adjudication](db_ui/adjudication.md).

UI checks execute the actual page JavaScript in a Node VM with controlled DOM/fetch stubs. They establish generated markup and exercised callbacks/state, not browser painting or browser-executed XSS. HTTP uses unmodified `src/app.py` on owned ports other than 8765, or its actual handler with isolated in-memory fixtures. Counterfactuals swap only stated query methods/modules against current app/data, not full historical deployments. No model was called. Medical sources below establish the promoted tracer's identity and notation; the entire isotope table was not externally certified.

## M16-B1 — P1: an element-first one-letter isotope bypasses every refusal stage



**Exact request:** `POST /api/explore`, `{"text":"I-124-labelled trastuzumab"}`. HTTP 200 draws **TRASTUZUMAB / CHEMBL1201585**, with **13 live trials** and no refusal. `Which trials evaluate I-124-labelled trastuzumab?` and `Who sponsors trials of I-124-labelled trastuzumab?` each return **12 originator evidence rows**. The natural phrase **`trastuzumab labelled with I-124`** does exactly the same. The explicit word `labelled` makes these one product description, not a coincidental list of two names.

The mass-first controls **`124I-labelled trastuzumab`** and **`trastuzumab labelled with 124I`** refuse; both QA queries then have zero evidence. Bare `trastuzumab` remains available. Shorter `I-124 trastuzumab`, `trastuzumab I-124`, no-hyphen `I124`, lowercase `i-124`, and bracketed `[I-124]` also leak. `I-124-labelled trastuzumab, osimertinib` still selects the wrong TRASTUZUMAB centre; the separately tested `osimertinib, trastuzumab I-124` selects OSIMERTINIB but leaves the tracer accepted as another drug.

[All current/previous stage captures](attacks/new_results.json), [compact summary](attacks/new_summary.json), [168 actual CLI HTTP responses](attacks/new_http.json), [server lifecycle](attacks/new_lifecycle.json), [helper and identity evidence](attacks/helper_identity_evidence.json).

| Stage | `I-124-labelled trastuzumab` | `124I-labelled trastuzumab` |
|---|---|---|
| Raw resolver | CONTAINED_ALIAS + UNRESOLVED; no BLOCKED component | BLOCKED_CLASS_TERM, radiotracer_guard |
| `_qualified` | false | true |
| `_resolver_blocked` | `{}` | CHEMBL1201585 veto |
| `_marked` actual call | `None`, both tokens in segment 0 | not reached, already refused |
| `_whole_name` | `None` | `None` |
| Public linker | TRASTUZUMAB, no Refused | Refused only |
| Map | CHEMBL1201585 / 13 trials | refused |
| Trial QA / sponsor QA | 12 / 12 | 0 / 0 |

**Cause:** `_medical_isotope_in` accepts mass-first isotopes at `src/query.py:139-145`, but its element-first regex requires **exactly two letters** at `src/query.py:146-148`. `I-124` becomes `i124` within a single original token, but `_medical_isotope_in('i124')` is false. This is not the expressly excluded cross-word one-letter case: the input isotope is wholly within `I-124-labelled` or `I-124`. `_marked` therefore misses both the whole-item and same-word checks at `src/query.py:375-379`. Earlier isotope/tracer regexes also require mass first (`src/textrules.py:289,303-314`; used by `src/normalize.py:740-743`). `_qualified` has no independent guard for this spelling (`src/query.py:184-205`), so no layer recovers the refusal. `Engine.explore` selects the surviving positive hit (`src/app.py:88-95`).

The asymmetry is visible even in the newly added helpers: `_labelled('I-124')` is **true** because the preferred-name path accepts one-letter element-first labels (`src/query.py:152-162`), whereas `_medical_isotope_in('i124')` is **false**. The medical table already contains iodine 124 (`src/query.py:126`); this is an orientation gap, not a missing mass or an inference about an unlisted isotope.

**Identity evidence:** the original clinical study constructed iodine-124-labelled trastuzumab as a PET radioligand, distinct from unlabelled trastuzumab ([Guo et al., primary study](https://pubmed.ncbi.nlm.nih.gov/31919745/)). NCI explicitly uses `[I-124]` in a radioconjugate abbreviation ([NCI Drug Dictionary](https://www.cancer.gov/publications/dictionaries/cancer-drug/def/iodine-i-124-cpd-1028)); FDA names the isotope IODINE I-124 ([FDA GSRS](https://precision.fda.gov/ginas/app/ui/substances/6432f496-edbb-4482-b6a0-00f18498bf8a)). These sources support tracer identity and spelling; no efficacy or clinical-use recommendation is inferred.

**Corroboration:** `vinblastine H3`, `vinblastine H-3` and `[H-3] vinblastine` draw VINBLASTINE / CHEMBL159 with 5 live trials and 5/5 trial/sponsor QA rows. The stored `[3h]-vinblastine` identity, `vinblastine 3h` and repaired `3hvinblastine` refuse. This is the same element-first failure, not a second inflated finding.

**Introduction:** both current and HEAD^ query modules leak the representative cases when run against the same current app/data. It is an inherited gap newly reproduced in this round. This comparison does not reconstruct the complete old deployment. The original approval bar still forbids the resulting originator map.

**Required result:** preserve refusal when an unambiguously radiolabelled product uses the element-first form of a one-letter isotope within a word. Check actual resolver/linker/map/QA responses with paired mass-first controls. No fix was implemented.

## Independent confirmation

The root's separate CLI HTTP reproducer confirms `I-124 trastuzumab`, `I124 trastuzumab`, `trastuzumab I-124`, `trastuzumab I124`, and lower-case `i-124 trastuzumab` all select CHEMBL1201585 with no refusal. `124I trastuzumab` / `trastuzumab 124I` refuse. `H3 vinblastine` and `C11 erlotinib` similarly select unlabelled drugs, while their mass-first controls refuse. `Cu64 trastuzumab` refuses as expected for the implemented two-letter reverse form. [19-case / 76-request evidence](root_checks/independent_m16_http.json), [lifecycle](root_checks/independent_m16_lifecycle.json).

With `I-124 trastuzumab, osimertinib`, the wrong TRASTUZUMAB is selected first. Reversing the list selects OSIMERTINIB but leaves the tracer accepted as another Drug. Root also independently confirms `89-ZrDFO trastuzumab`, `3hvinblastine`, and `A33124i` now refuse. These are independent responses, not conclusions inferred from the standalone helper. The separate reviewer captures the same failed stages and old-case repairs. [Staged adjudication](db_ui/adjudication_tracer.json).

## Earlier reproductions — FIXED / NOT FIXED per finding

The tables classify exact earlier reproductions, with fresh evidence links. A fixed spelling does not prove every isotope notation is safe. M2 ended without a completed report; its partial cases and completed M2b reproductions are included. Nonblocking status is not inferred from a passing script exit code.

### Name resolution, m1–m15



M2 has no completed report; its partial cases are covered by cumulative M2b scripts. DB, UI, server and performance findings are handled by the root/other reviewer. The table contains **76 rows: 60 FIXED, 16 NOT FIXED**. NOT FIXED includes recorded nonblocking limitations and user-accepted exceptions; it does not itself assign blocker severity.

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
| M12 M12 supplementary previously unpromoted descriptive label-distance inputs | **FIXED** | All old Zr-89 labelled/labeled-distance examples now refuse with no originator centre and zero qualified trial/sponsor evidence. Comma-separated osimertinib survives. [Evidence](names/m12_attacks/focused_results.json). |
| M13 M13-B1 isotope fused to chelator inside matched alias | **FIXED** | 89ZrDFO-daratumumab, 89zrdfodaratumumab, [89ZrDFO]-daratumumab, 89zrdfo daratumumab and 89Zr-DFOdaratumumab refuse, with zero trial/sponsor evidence. Bare daratumumab maps correctly; separately listed osimertinib survives. [Evidence](names/joined_label_probe.json). |
| M13 M13 supplementary A33124I trailing isotope | **FIXED** | A33124I and A33 124i refuse with no centre and zero qualified trial/sponsor evidence; also fixed in HEAD^. [Evidence](names/m14_exact/fresh_results.json). |
| M14 M14-B1 uppercase one-letter element inside a consumed name | **FIXED** | 3HVINBLASTINE, 3HVinblastine and 3Hvinblastine now refuse with no centre and zero trial/sponsor evidence. Comma-osimertinib selects the separate CHEMBL3353410 and discloses the refusal. [Evidence](names/m14_exact/edge_results.json). |
| M14 M14-B1 supplementary lower-case 3hvinblastine | **FIXED** | The exact prior 3hvinblastine now refuses with no centre and zero trial/sponsor evidence; its lower-case A33124i and a33124i corroborations also refuse. [Evidence](names/m15_exact/targeted_results.json). |
| M14 M14-B2 isotope plus drug plus trailing PET/CT marker | **FIXED** | 89Zrpanitumumab-PET-CT, 89ZrpanitumumabPETCT, 89zrpanitumumabpetct and 89Zrpanitumumab PET CT now refuse with zero trial/sponsor evidence. A comma-separated osimertinib survives. [Evidence](names/m14_exact/edge_results.json). |
| M14 M14 supplementary neighbouring fused-label casing | **FIXED** | 89ZRDFO trastuzumab and 89zrDFO trastuzumab now refuse with no centre and zero trial/sponsor evidence; properly cased control also refuses. [Evidence](names/m14_supplement.json). |
| M14 repair note / user Known ChEMBL bevacizumab development-code synonym limitation | **NOT FIXED** | HLX04, HLX-04, HLX04-O, BAT1706, SB8, MB02, FKB238 and BI 695502 still resolve to CHEMBL1201583. Explicitly user-accepted dictionary limitation, not a map blocker. [Evidence](names/m14_supplement.json). |
| M12/M15 supplementary Fragmented qualifier b.i.o.similar bevacizumab | **NOT FIXED** | The exact old supplementary input still draws BEVACIZUMAB / CHEMBL1201583 (122 live trials) and supplies 12 trial / 12 sponsor QA rows, without a refusal. Preserved as the previously recorded supplementary gap, not a newly discovered family. [Evidence](names/m12_attacks/focused_results.json). |
| M12/M15 supplementary Fragmented qualifier lip.osomal doxorubicin | **NOT FIXED** | The exact old supplementary input still draws DOXORUBICIN / CHEMBL53463 (3 live trials) and supplies 3 trial / 3 sponsor QA rows, without a refusal. Preserved as the previously recorded supplementary gap, not a newly discovered family. [Evidence](names/m12_attacks/focused_results.json). |
| M14/M15 supplementary Slash PET/CT presentation: 89zr-panitumumab-pet/ct | **NOT FIXED** | The exact slash-bearing input returns not_found with no centre, no refusal message and zero trial/sponsor evidence. This remains a should-fix distinction in failure presentation, not an originator leak; the glued/hyphen PETCT blocker inputs explicitly refuse. [Evidence](names/m14_exact/edge_results.json). |
| M15 M15-B1 punctuation inside adjacent isotope/chelator | **FIXED** | 89-ZrDFO trastuzumab, trastuzumab DFO89-Zr, 89Z.rDFO trastuzumab, and trastuzumab DFO89Z.r refuse with zero originator map/trial/sponsor results. Separate comma osimertinib survives. [Evidence](names/m15_exact/targeted_results.json). |
| M15 M15-B2 lower-case stored tracer; A33 corroboration | **FIXED** | 3hvinblastine, A33124i, and a33124i refuse; bare VINBLASTINE and ADAKITUG remain available. Comma-separated osimertinib survives the refused lower-case vinblastine tracer. [Evidence](names/m15_exact/targeted_results.json). |
| M15 repair note / user GS-11CAL-101 known over-refusal | **NOT FIXED** | The raw stored-alias sweep newly refuses GS-11CAL-101. Explicitly user-accepted, nonblocking; no other unexpected new raw alias loss. [Evidence](names/names_m5_summary.json). |
| M15 repair note / user 3en3hg4wsw known over-refusal | **NOT FIXED** | The raw stored-alias sweep newly refuses 3en3hg4wsw. Explicitly user-accepted, nonblocking; no other unexpected new raw alias loss. [Evidence](names/names_m5_summary.json). |


### Database, UI, values, wording and server




The table covers non-name findings from m1-m15. m2 has no completed REPORT; its partial role/order cases are included. Later rounds repeat these fixtures. Name and cost findings belong to the naming and cost matrices. [Historical report inventory](db_ui/historical_report_headings.json).

| Earlier finding / exact reproduction | Round 16 result and evidence |
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

## Regressions, accepted limitations and should-fix observations

No new demo regression, live-edge defect, stored-value mismatch, or demonstrated script injection was found. The raw stored-alias sweep changes only the two newly accepted over-refusals. The explicitly accepted M5-S2, rapamycin locant aliases, `Trastuzumab--vcmmae conjugate`, `9-amino-20(s)-camptothecin`, `il-6ra`, `TAK-659F`, `GS-11CAL-101`, `3en3hg4wsw`, same-list-item over-refusal, and bevacizumab development-code limitation remain outside the blocker count. `osimertinib with [89Zr] trastuzumab` now refuses both as specified; a comma-separated osimertinib survives. [Fresh alias controls](names/alias_loss_controls.json), [raw sweep](names/names_m5_summary.json), [development codes](names/m14_supplement.json).

The separate **428 transformed variants / 104 stored keys** scan has five changed responses versus m15: three repaired lower-case tracer forms, and two newly refused fully collapsed systematic SIROLIMUS alias variants containing `3h`. The exact stored SIROLIMUS alias remains available. This is an additional **availability should-fix**, not an originator leak; it is distinct from the raw-alias sweep. Exact long inputs and outputs are retained in [comparison](attacks/alias_variants_comparison.json). Its accepted-variant total is not a defect count.

Already-labelled products retain an inherited normalization discrepancy: `89ZrDFO 18-FDG` refuses but `89-ZrDFO 18-FDG`, with the same canonical key, draws FLUDEOXYGLUCOSE F 18 / CHEMBL2030434 (one trial, 1/1 QA rows). `_labelled` exempts the latter from the new rule, while an earlier guard catches the former. The 14 preferred names classified as labelled all visibly carry isotope designations. This merits **consistency/specification clarification**, but is not promoted to an unlabelled-originator blocker because the brief expressly allows labelled products and the extra-isotope semantics are ambiguous. [Full staged analysis](db_ui/adjudication.md), [preferred-name scan](db_ui/labelled_preferred_names.json).

Cross-word one-letter exploratory inputs such as `18 FDFO trastuzumab` are likewise not promoted: this round expressly limits that check to within a word. The promoted `I-124-labelled trastuzumab` meets the within-word condition. README comments still say 317 tests (`README.md:565`, `README.ko.md:386`): **NOT FIXED**, documentation-only. The app descriptions immediately below remain accurate.

## Cost and performance reproductions

All **nine inherited cost scripts** exited zero, run sequentially after the other reviewers' CPU/HTTP work finished. Unrelated host activity is uncontrolled. Timings are observations, not service-level guarantees or proof of global complexity. Historical comparisons substitute only `query.py` against the same current remaining modules and database. [Execution](cost/execution_isolated.json), [provenance](reuse_manifest_root.json).

| Historical reproduction / exact workload | Current result and disposition |
|---|---|
| M5-S3 cubic scan, `' '.join(['x']*250)` (499 characters) | **FIXED for this original workload**: 2,224 calls to each predicate, 33,880 aggregate predicate-input characters, **0.02895 s** direct linking. [Instrumentation](cost/perf_current.json). |
| Original 999-character plain-answer timeout, `' '.join(['x']*500)` | **FIXED**: `/api/check` 200 in **0.17687 s**; subsequent ordinary map **0.02225 s**. [HTTP](cost/perf_check_http.json). |
| M6/M7 repeated 2,000-piece resolver cost, `';'.join(['x']*2000)` | **FIXED for this exact repeated-piece control**: current direct median **0.16896 s**, historical `9bd7cb4` **1.90091 s**. HTTP check **0.43118 s**, queued EGFR **0.34792 s**, both 200. [Comparison](cost/fresh_cost_comparison.json), [HTTP](cost/fresh_cost_http.json), [stress](cost/cost_stress.json). |
| M8-S1 natural 4,097th cache entry | **FIXED**: 82/82 fill requests create 4,096 entries; first OSIMERTINIB at rollover and retry both 200 / CHEMBL3353410 / 79 trials. No KeyError. [HTTP](cost/cache_boundary_http.json). |
| M10-M15 distinct-piece lock contention, `';'.join(f'isa x{i:04d}' for i in range(400))` (3,999 answer characters) | **NOT FIXED**, inherited cost concern: cold check **2.42630 s**, queued EGFR **2.35112 s**, warm **0.59026 s**, all 200. 400 cold / 0 warm resolver calls. [HTTP](cost/isolated_unique_cost_http.json), [instrumentation](cost/unique_piece_cost.json). |
| M11-M15 Unicode expansion, answer `'\ufdfa'*4000` | **NOT FIXED**, inherited cost concern: 4,000 characters expand to 72,000 under NFKC; cold check **3.77042 s**, queued EGFR **3.70555 s**, warm **3.06876 s**, all 200. [HTTP](cost/isolated_unicode_cost_http.json). |
| M11-M15 punctuation normalization, `' - '.join(['x']*1000)+'xx'` | **NOT FIXED as measured overhead**, no failure: current / HEAD^ medians **0.30250 / 0.29809 s**; at 499 characters **0.04103 / 0.03798 s**. [Comparison](cost/normalization_cost.json). |
| M12-M15 repeated matches, `' '.join(['isa']*1000)` | **NOT FIXED as measured overhead**, no failure: current / HEAD^ medians **4.37413 / 1.01015 s**; at 499 characters **0.08195 / 0.03360 s**. [Comparison](cost/normalization_cost.json). |
| M13-M15 repeated isotope alias, `';'.join(['A33 124i']*444)` | **No error reproduced**: current / HEAD^ medians **0.07122 / 0.07292 s**. Cached OSIMERTINIB **0.00017 / 0.00015 s**. All 24 version/workload rows finish; three samples each do not establish a statistical regression/speedup. [Comparison](cost/normalization_cost.json). |
| Disease / ordinary concurrent maps | **No failure reproduced**: 2,774 Trials + 300 Targets, 30 per list, **18,575 bytes / 100.414 ms**. 24 requests / 12 workers all expected HTTP 200 shapes, **865.497 ms** total. These early ordinary samples overlapped other audit work. [HTTP](root_checks/http_results.json). |

`engine.lock` serializes operations (`src/app.py:247-263`), so costly legal check-answer requests delay maps. The 3,999/4,000-character stresses are direct-link or **answer-field** cases; explore correctly rejects input longer than 500 characters. Input limits precede NFKC (`src/app.py:239-243,260`; `src/query.py:116-117,234-236`). No deadlock or invented value was observed. These costs remain should-fix items and do not determine the verdict. The added repeated-match work is a latest-patch amplification, detailed below. **No model call or model cost was incurred.**

### M16-S1 — added repeated-match work and HTTP lock delay (should-fix)

The reused same-data workload `' '.join(['isa']*1000)` (3,999 characters) has a current/HEAD^ direct-link median of **4.37413 / 1.01015 s**, about **4.33x** in these three-sample observations. Unlike the inherited baseline cost, the new item-wide isotope scan adds demonstrably quadratic work to this workload: `_marked` runs before entity deduplication (`src/query.py:534-545`), and each invocation rescans all tokens of the same item (`src/query.py:375-379`).

Bounded instrumentation counts **125 whole-item / 15,625 within-word calls** at 125 occurrences (499 characters), versus **1,000 whole-item / 1,000,000 within-word calls** at 1,000 occurrences. The helper sees **6,000,000 aggregate characters** in the latter. The output remains one ISATUXIMAB entity. This establishes the additional repeated scanning directly; the timing ratio is not claimed as a universal benchmark. [Instrumentation](cost/repeated_match_instrumentation.json), [script](cost/repeated_match_followup.py), [original paired medians](cost/normalization_cost.json).

The same 3,999-character string is legal in the **answer field**: `POST /api/check` with `text='EGFR'` and that answer returns 200 in **11.26548 s**, with a concurrent EGFR map queued for **11.18237 s**. A warm repeat takes **10.59518 s**; the ordinary map after completion takes **0.04685 s**. All calls return 200, the page GET remains responsive, and the owned server closes with unchanged DB bytes. No historical HTTP timing is inferred from the direct-link comparator. [HTTP responses](cost/isolated_repeated_match_cost_http.json), [lifecycle](cost/repeated_match_cost_lifecycle.json), [adaptation/execution](cost/repeated_match_execution.json).

Compute or reuse the item's isotope state without rechecking every token for every matched occurrence, while preserving the refusal outcomes. This is a performance should-fix under the given correctness-focused approval bar; it is not needed to establish the separate P1 verdict. No repair was implemented.

## Standards


**No documented-standard violations found.** Reviewed the changed app/UI hunks from fixed point `bfcb83d` through HEAD `8ebd6629b51a474f216457c8c00f20152304bd1d`, plus the latest query/test patch. The fixed-point diff is nonempty. [App/UI diff](db_ui/review_diff_app_ui.txt), [latest patch](db_ui/review_diff_latest.txt).

`git ls-files '*AGENTS.md' '*CONTRIBUTING.md' '*CODING_STANDARDS.md' 'docs/agents/*'` returned no tracked standards files. [Inventory](db_ui/review_diff_standards.txt). The user's instructions therefore govern: evidence-based independent review, no tracked edits, scratch only under m16, and a disposition for each earlier reproduction. The review uses original fixture logic, records source/adapted hashes, preserves raw outputs, compares current responses against stored data, and identifies the limits of simulated UI tests. Mutation fixtures change only in-memory database copies.

No application code was changed. The user's conditional requirement to compare original and modified application code against KOA Studio/KhOpenApi therefore does not arise. Issue-tracker setup was not performed because the explicit audit-only/no-tracked-edit scope takes precedence over optional workflow setup.

**Judgment rather than a standards violation:** the new isotope helper still misses an element-first one-letter label, while `_labelled` has a separate reverse-label implementation. The independent `I-124 trastuzumab` reproduction is a specification defect, not a style or documented-standard violation. The labelled-product exception also leaves a paired punctuation discrepancy for an already-labelled centre; that is recorded separately as a nonblocking clarification because the brief explicitly permits labelled products. [Independent staged evidence](db_ui/adjudication_tracer.json).

The stale 317-test README comments are inherited documentation should-fix items (`README.md:565`, `README.ko.md:386`). App descriptions at lines 566 and 387 remain accurate. No extra coding convention has been invented as a blocker.

## Specification


Spec source: the user's Round 16 brief and original approval bar; baseline `bfcb83d` to current HEAD `8ebd6629b51a474f216457c8c00f20152304bd1d`.

The current round says: "a medical isotope anywhere in the list item (two-letter elements across words, one-letter within a word) refuses an unlabelled drug". The original approval bar includes "a refused product drawn as the originator" among prohibited outcomes.

**Wrong behavior, P1:** `I-124-labelled trastuzumab` and `trastuzumab labelled with I-124` name one radiolabelled product, with the one-letter isotope wholly inside a word. Every refusal stage misses; HTTP map selects unlabelled TRASTUZUMAB / CHEMBL1201585, 13 trials, and both trial/sponsor QA paths return 12 originator rows. The mass-first controls refuse. The new helper's element-first branch accepts only two-letter symbols, despite the companion `_labelled` helper recognizing one-letter element-first names. Full stages and 168 HTTP responses are in `new_results.json` / `new_http.json`. Both current and HEAD^ query modules leak, so this is an inherited failure, not a demonstrated latest-patch regression.

**Repair success:** exact M15-B1 punctuation/chelator and M15-B2 lower-case vinblastine cases now refuse. A33 lower-case residual also refuses. The reused 97 m14 and 29 m15 attack cases completed. Approved dose/development-code controls remain available.

**Nonblocking limitation:** two fully collapsed systematic SIROLIMUS alias variants now over-refuse; their literal stored alias is still accepted. Accepted user-listed over-refusals and the known ChEMBL bevacizumab-code limitation are not blockers. Explicitly excluded cross-word one-letter exploratory cases are not promoted.

No tracked code was changed and no repair is proposed as implemented. The P1 originator leak is sufficient for CHANGES REQUIRED independently of any other reviewer findings.

[Specification evidence and source references](attacks/FINDINGS.md). Standards: **0 documented violations**. Specification: **1 newly promoted P1 family**; its inherited originator leak independently requires changes.

## Integrity and reproduction

`Engine.ask` explicitly passes `use_llm=False` (`src/app.py:181`). Explore follows read paths; mutation fixtures use in-memory databases. The app's SQLite handle is not globally read-only, so the no-write conclusion relies on inspected/executed paths and before/after bytes, not a permission guarantee.

Final verification compares **5,592 tracked-file SHA-256 hashes**, unchanged HEAD, tracked/staged diffs, database bytes, local report links and owned-port closure. [Initial snapshot](integrity_before.json), [final verification](integrity_final.json). Database SHA-256: `7341c5a7089731f67356da5a588b269d4b69e8e6c4c054acf19aa4ef2837b529`.

Run from repository root with bytecode disabled and temporary paths inside each m16 family's `tmp/`. Reused shared-port suites are sequential; run cost after other CPU/HTTP work. Preparation creates new files and should not overwrite an initial snapshot. Manifests identify the original scripts and every path/port adaptation.

```text
python -B audit_evidence_claims/m16/root_checks/run_all.py
python -B audit_evidence_claims/m16/root_checks/run_late.py
python -B audit_evidence_claims/m16/root_checks/independent_m16_http.py
python -B audit_evidence_claims/m16/names/run_round9.py
python -B audit_evidence_claims/m16/names/run_additional.py
python -B audit_evidence_claims/m16/names/run_completion.py
python -B audit_evidence_claims/m16/db_ui/run_db.py
python -B audit_evidence_claims/m16/db_ui/run_ui.py
python -B audit_evidence_claims/m16/db_ui/run_final.py
python -B audit_evidence_claims/m16/attacks/new_probe.py
python -B audit_evidence_claims/m16/attacks/new_http.py
python -B audit_evidence_claims/m16/cost/run_isolated.py
python -B audit_evidence_claims/m16/cost/repeated_match_followup.py
python -B audit_evidence_claims/m16/build_report.py
python -B audit_evidence_claims/m16/finalize_integrity.py
```

VERDICT: CHANGES REQUIRED
