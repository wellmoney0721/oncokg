# Independent relation-map review — round 17

Reviewed **`4df54ae7f8bd16babc4ccb2dd0e8d4ce0314098b`**. **CHANGES REQUIRED: one new P1 originator-refusal bypass.** `trastuzumab labelled-I-124` passes every refusal stage and draws unlabelled TRASTUZUMAB with its clinical-trial evidence. The corresponding `labelled-124I` form refuses. The gap also exists in HEAD^: this is a newly reproduced inherited defect, not a demonstrated latest-patch regression.

All exact previously promoted M1–M16 name blockers are **FIXED**, including M16-B1 `I-124-labelled trastuzumab`. **M16-S1's repeated isotope computation is FIXED**: the helper now performs one whole-item scan rather than one scan per matched occurrence. Historical unresolved supplemental, availability, UI, documentation and residual cost observations retain their individual NOT FIXED dispositions below. The explicitly accepted over-refusals and ChEMBL bevacizumab-code limitation do not determine this verdict.

All new scratch files are under `audit_evidence_claims/m17/`. No application source or tracked file was edited.

## Verification and scope

- **344 passed in 34.25 s**, exit 0: `python -m pytest tests -q -p no:cacheprovider`. Bytecode disabled and temporary paths confined to m17. [Output](root_checks/pytest.txt), [execution/hashes](root_checks/pytest_summary.json).
- Cumulative original-script replays cover m1, partial m2/completed m2b, m3–m16. The root's main and late batches exit zero. Exact m16 independent HTTP covers **19 cases / 76 requests**; the new root confirmation covers **17 cases / 68 requests**. [Manifest](reuse_manifest_root.json), [main](root_checks/execution_all.json), [remaining](root_checks/execution_remaining.json), [late](root_checks/execution_late.json), [old HTTP](root_checks/independent_m16_http.json), [new HTTP](root_checks/independent_m17_http.json).
- Raw **7,511-key** alias sweep has **zero new losses versus m16**. Adapted frozen **1,648-question** comparison remains **68 identical / 1,556 metadata-only / 24 semantic / zero errors**. [Name report](names/FINDINGS.md), [worker checks](names/worker_final_checks.json), [raw differences](names/new_alias_losses.json), [counterfactual](names/adapted_frozen_qa_relink_sweep.json).
- Stored-row oracle: **6,469 live centres / 22 relation-direction-type-role combinations / zero errors**. **19/19 DB**, **24/24 UI**, and **4/4 self-loop/unknown-type/retirement** assertions pass. [Oracle](db_ui/db_validate.json), [DB](db_ui/db_assertions.json), [UI](db_ui/ui_assertions.json), [fixture](db_ui/self_loop_unknown.json).
- **36/36 demos** exactly match all m7–m16 full-response baselines; **36/36 CLI HTTP demos** return 200 and match Engine responses. Six map callbacks pass; seven original QA evidence counts remain **12, 12, 11, 1, 12, 0, 0**. [Baselines](db_ui/demo_previous_comparison.json), [HTTP](db_ui/demo_http.json), [callbacks](db_ui/ui_m3_checks.json).
- Attack worker reran **168 historical staged cases**, plus **63 new current/HEAD^ pairs**, and **420 HTTP requests**, all 200. A separate reviewer records **36 current/HEAD^ paired stage cases**, including all 17 original m16 independent adjudication inputs. **428 transformed variants / 104 stored keys** have no centre/refusal changes from m16. [Attack checks](attacks/final_checks.json), [independent stages](db_ui/adjudication_tracer.json), [alias comparison](attacks/alias_variants_comparison.json).

UI checks execute actual page JavaScript in a Node VM with controlled DOM/fetch stubs: they verify generated markup and callbacks/state, not browser painting or browser-executed XSS. HTTP uses unmodified `src/app.py` on owned ports other than 8765, or its actual handler with in-memory fixtures. Counterfactuals replace only the stated query code against current remaining modules/data; they are not full historical deployments. No model was called. Scientific sources establish the primary iodine-124/trastuzumab identity; synthetic corroborating spellings are not claimed to be marketed products.

## M17-B1 — P1: punctuation before a one-letter isotope loses its boundary

**Exact input:** `trastuzumab labelled-I-124`.

`POST /api/explore` returns HTTP 200 and draws **TRASTUZUMAB / CHEMBL1201585**, with **13 live clinical trials**, without any refusal. `Which trials evaluate trastuzumab labelled-I-124?` and `Who sponsors trials of trastuzumab labelled-I-124?` each return **12 originator evidence rows**. The same occurs for `trastuzumab labelled-with-I-124`, `iodine-I-124 trastuzumab`, and `trastuzumab (iodine-I-124)`.

The paired inputs `trastuzumab labelled-124I`, `I-124-labelled trastuzumab`, and `trastuzumab labelled with I-124` all refuse, and both QA questions have zero evidence. Bare `trastuzumab` remains available. These are one-product descriptions: the explicit word "labelled" and the I-124 isotope identify radiolabelled trastuzumab. This is not the explicitly excluded cross-word one-letter case: the isotope is wholly inside the original token `labelled-I-124`, and its preceding boundary is a visible hyphen.

Fresh primary scientific identity evidence: the original study constructed iodine-124-labelled trastuzumab for PET imaging, so the radioligand is not interchangeable with unlabelled trastuzumab. [Guo et al., original study, PMID 31919745](https://pubmed.ncbi.nlm.nih.gov/31919745/). The NCI also uses element-first I-124 notation for an iodine radioconjugate. [NCI Drug Dictionary](https://www.cancer.gov/publications/dictionaries/cancer-drug/def/iodine-i-124-labeled-hsp90-inhibitor-puh71). These establish the isotope/product distinction and notation; no medical recommendation is made.

| Stage | `trastuzumab labelled-I-124` | `trastuzumab labelled-124I` |
|---|---|---|
| Raw resolver | CONTAINED_ALIAS + UNRESOLVED; no BLOCKED component | CONTAINED_ALIAS + UNRESOLVED |
| `_qualified` | false | false |
| `_resolver_blocked` | `{}` | `{}` |
| Actual `_marked` call | `None`; both tokens in segment 0 | `trastuzumab` refusal |
| `_item_has_isotope` | false | true |
| `_whole_name` | `None` | `None` |
| Public linker | Drug TRASTUZUMAB, no Refused | Refused only |
| Map | CHEMBL1201585, 13 trials | refused |
| Trial/sponsor QA | 12 / 12 | 0 / 0 |

**Cause:** `src/query.py:164` first converts every original token to its letters-and-digits key. At `src/query.py:167`, the new `(?<![a-z])([a-z])(\d{1,3})(?!\d)` guard then sees `labelledi124`. The preceding hyphen no longer exists, so `i` is incorrectly treated as internal to a letter run. `_medical_isotope_in` still recognizes only two-letter element-first forms (`src/query.py:147-149`); no earlier helper catches this spelling. `_qualified` (`src/query.py:204-226`) and `_resolver_blocked` (`src/query.py:275-317`) also miss. The earlier `_marked` neighbour loops start at `labelled` and cannot recover the trailing element-first label (`src/query.py:358-385`). The item guard at `src/query.py:395-397` therefore returns false, and `Engine.explore` selects the surviving positive hit (`src/app.py:88-95`). [Helper evidence](attacks/helper_evidence.json).

**Introduction:** both current and HEAD^ link/map/QA results reproduce this leak. The latest change repairs the earlier spelling but leaves this inherited boundary gap. The original approval bar still forbids the originator map.

**Corroborations, not extra findings:** uppercase/lowercase, underscore, colon, attached parentheses/brackets, and reversed comma/and list orders have the same result. `vinblastine labelled-H3`, `erlotinib labelled-F18`, `paclitaxel labelled-C14`, and `cetuximab labelled-Y-90` also draw their unlabelled drugs; mass-first and bare element-first controls refuse. Their token shapes support the common code cause; only the primary iodine-124/trastuzumab scientific identity was independently sourced. No claim that each synthetic spelling is a real marketed product is needed.

**Required result:** retain genuine within-token punctuation boundaries when checking element-first one-letter isotope labels, while preserving BKM120/AZD9291 and dose/schedule controls. Check all public resolver/linker/map/QA paths with these paired inputs. No repair was implemented.

## Independent HTTP confirmation

The root independently started the unmodified CLI server, verified the served page bytes, and made 68 requests across resolve, explore and trial/sponsor QA. `trastuzumab labelled-I-124`, `iodine-I-124 trastuzumab`, and `trastuzumab labelled-with-I124` draw CHEMBL1201585 without refusal. Their mass-first or whitespace-separated isotope controls refuse. `vinblastine tritium-H-3` similarly draws CHEMBL159, while `vinblastine tritium-3H` refuses. Separate-list reversals show that the tracer remains an accepted Drug even when OSIMERTINIB is selected first. BKM120, AZD9291 and `osimertinib 80 mg` remain available. [Requests and complete responses](root_checks/independent_m17_http.json), [server lifecycle](root_checks/independent_m17_lifecycle.json), [source adaptation](root_checks/independent_m17_manifest.json).

The separate DB/UI reviewer independently traces the same lost boundary in `iodine-I-124-labelled trastuzumab` and `trastuzumab labelled with iodine-I-124`. Both current and HEAD^ produce 13 map trials and 12/12 QA evidence. This corroborates the primary finding; it is not counted as another blocker. [Adjudication](db_ui/adjudication.md), [stage captures](db_ui/adjudication_tracer.json).

## Earlier reproductions — FIXED / NOT FIXED per finding

Status describes the exact previous reproduction, not every possible spelling. A passing script exit alone does not establish a repair. M2 has no completed report; its partial cases and completed M2b work are included. [Report inventory](historical_report_inventory.json). Recorded nonblocking limitations and accepted exceptions remain visible.

### Name resolution, m1–m16

M2 had no completed report; its partial cases are covered by cumulative M2b scripts. DB/UI/server/cost findings are handled by the other reviewers. **77 rows: 61 FIXED / 16 NOT FIXED.** The latter includes accepted over-refusals, availability limits and recorded supplements; status alone does not assign severity.

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
| M15 repair note / user GS-11CAL-101 known over-refusal | **NOT FIXED** | The raw stored-alias sweep continues to refuse this alias. Explicitly user-accepted, nonblocking; no new raw-alias loss versus M16. [Evidence](names/names_m5_summary.json). |
| M15 repair note / user 3en3hg4wsw known over-refusal | **NOT FIXED** | The raw stored-alias sweep continues to refuse this alias. Explicitly user-accepted, nonblocking; no new raw-alias loss versus M16. [Evidence](names/names_m5_summary.json). |
| M16 M16-B1 element-first one-letter isotope within one word | **FIXED** | I-124-labelled trastuzumab, trastuzumab labelled with I-124, I124/i-124/[I-124] variants and H3/H-3 vinblastine corroborations now refuse with no centre and zero trial/sponsor evidence. Bare controls survive; separate comma-osimertinib remains selected with refusal disclosed. All 42 original stage cases replayed. [Evidence](names/m16_exact/new_results.json). |

### Database, UI, server and wording

The table covers non-name findings from m1-m16. m2 has no completed REPORT; its partial role/order cases are included. Later rounds repeat these fixtures. Name and cost findings belong to the naming and cost matrices. [Historical report inventory](db_ui/historical_report_headings.json).

| Earlier finding / exact reproduction | Round 17 result and evidence |
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
| M16-B1 exact element-first one-letter inputs: `I-124-labelled trastuzumab`, `trastuzumab labelled with I-124`, `I124 trastuzumab`, `F18 trastuzumab`, `C14 paclitaxel` | **FIXED**. Current refuses the unlabelled originator with zero QA evidence; HEAD^ accepts. [Independent stages](db_ui/adjudication_tracer.json). |
| M16 labelled-product qualification: `89ZrDFO 18-FDG` / `89-ZrDFO 18-FDG`, lutathera/FDG isotope variants | **NOT FIXED**, unchanged nonblocking discrepancy under the explicitly permitted labelled-product exception. All 17 original m16 adjudication inputs rerun. [Disposition](db_ui/adjudication.md), [stages](db_ui/adjudication_tracer.json). |
| M1-M16 README test-count comments, README.md:565 / README.ko.md:386 | **NOT FIXED**, inherited documentation-only: both say 317 tests. Nearby app descriptions remain accurate. [Standards](db_ui/STANDARDS.md). |

All six live node types and all 22 existing relation combinations are covered. The snapshot has **7 retired nodes, 142 retired edges, zero self-loops and zero live edges with retired endpoints**. PARENT_OF, STUDIES, ASSOCIATED_WITH, EVALUATES, ACTS_ON and role-aware SPONSORS agree with stored endpoints. All 3,000 stored URLs are registry HTTPS URLs, and all node/edge props are valid JSON objects. [Snapshot](db_ui/db_snapshot_facts.json), [oracle](db_ui/db_validate.json). The self-loop result is a fixture result, not a snapshot claim.

## Regressions and supplemental observations

No new demo regression, live-edge defect, wrong relation direction, stored-value mismatch, or demonstrated script injection was reproduced. Raw stored-alias outcomes are unchanged from m16. The transformed-alias scan retains the two fully collapsed systematic SIROLIMUS alias over-refusals: **NOT FIXED**, availability-only. The literal stored alias remains available. [428-variant comparison](attacks/alias_variants_comparison.json), [exact variant inputs/results](attacks/alias_variants.json).

The inherited already-labelled-product discrepancy remains **NOT FIXED**: `89ZrDFO 18-FDG` refuses, while `89-ZrDFO 18-FDG` draws FLUDEOXYGLUCOSE F 18. The current brief allows labelled products, so this remains a consistency/specification clarification rather than an unlabelled-originator blocker. Cross-word one-letter exploratory forms remain outside the stated within-word requirement. [Full original-case replay and adjudication](db_ui/adjudication.md).

The user-accepted M5-S2, rapamycin locant aliases, `Trastuzumab--vcmmae conjugate`, `9-amino-20(s)-camptothecin`, `il-6ra`, `TAK-659F`, `GS-11CAL-101`, `3en3hg4wsw`, same-list-item over-refusal, and ChEMBL bevacizumab development-code limitation do not determine the verdict. Other old supplemental gaps remain explicitly NOT FIXED in the naming table. The new M17-B1 independently fails the approval bar.

## Cost and performance reproductions

All nine inherited cost scripts exited zero, sequentially after other audit CPU/HTTP workloads finished. The additional M16 repeated-match instrumentation and HTTP reproducer also exited zero. Unrelated host load is uncontrolled; these are measurements, not service guarantees. Counterfactuals substitute only historical `query.py` against the same current app/data. [Execution](cost/execution_isolated.json), [provenance](reuse_manifest_root.json), [M16 follow-up execution](cost/repeated_match_execution.json).

| Historical finding / exact workload | Current disposition and measured evidence |
|---|---|
| M5-S3 cubic qualifier scan, `' '.join(['x']*250)` (499 chars) | **FIXED for the original workload.** 2,224 calls to each predicate / 33,880 aggregate predicate-input characters, 0.02845 s direct. [Instrumentation](cost/perf_current.json). |
| Original 999-character plain-answer timeout, `' '.join(['x']*500)` | **FIXED.** HTTP check 200 in 0.19197 s; later map 0.03369 s. [HTTP](cost/perf_check_http.json). |
| M6/M7 repeated 2,000-piece resolver cost, `';'.join(['x']*2000)` | **FIXED for this repeated-piece control.** Current / historical `9bd7cb4` direct medians 0.21202 / 1.92070 s. HTTP check 0.42823 s, queued EGFR 0.34583 s, both 200. [Comparison](cost/fresh_cost_comparison.json), [HTTP](cost/fresh_cost_http.json), [stress](cost/cost_stress.json). |
| M8-S1 4,097th resolver-cache entry | **FIXED.** 82/82 fill requests succeed; rollover and retry return OSIMERTINIB / CHEMBL3353410 with 79 trials, no KeyError. [HTTP](cost/cache_boundary_http.json). |
| M10-M16 distinct-piece lock delay, `';'.join(f'isa x{i:04d}' for i in range(400))` | **NOT FIXED**, inherited cost concern. Cold check 2.65898 s, queued EGFR 2.59203 s, warm 0.51063 s; all 200. [HTTP](cost/isolated_unique_cost_http.json), [instrumentation](cost/unique_piece_cost.json). |
| M11-M16 Unicode expansion, answer `'\ufdfa'*4000` | **NOT FIXED**, inherited cost concern. 4,000 chars expand to 72,000 under NFKC. Cold check 2.50050 s, queued EGFR 2.42491 s, warm 2.87081 s; all 200. [HTTP](cost/isolated_unicode_cost_http.json). |
| M11-M16 punctuation normalization, `' - '.join(['x']*1000)+'xx'` | **NOT FIXED as measured overhead**, no error. Current / HEAD^ medians 0.37195 / 0.35989 s; at 499 chars 0.04917 / 0.04164 s. [Comparison](cost/normalization_cost.json). |
| M12-M16 repeated matches, `' '.join(['isa']*1000)` | **NOT FIXED as residual repeated-match overhead**; **M16-S1 added isotope rescans FIXED**, detailed below. Current / HEAD^ direct medians 1.32586 / 4.50393 s; at 499 chars 0.03936 / 0.08517 s. [Comparison](cost/normalization_cost.json). |
| M13-M16 repeated isotope alias, `';'.join(['A33 124i']*444)` | No error reproduced. Current / HEAD^ medians 0.06949 / 0.07035 s. Cached ordinary OSIMERTINIB 0.00014 / 0.00020 s. All 24 workload/version rows complete. [Comparison](cost/normalization_cost.json). |
| Disease / ordinary concurrent maps | No failure reproduced: 2,774 Trials + 300 Targets, 30 per list, **18,575 bytes / 95.604 ms**. 24 requests / 12 workers all expected HTTP200 shapes in **1042.374 ms**. These ordinary early samples overlapped other audit work. [HTTP](root_checks/http_results.json). |

### M16-S1: the item's isotope state is now computed once

**FIXED for the exact reported extra work.** At 125 / 1,000 occurrences, instrumentation records **one whole-item scan** and **125 / 1,000 within-word helper calls**, respectively. The prior reproduction recorded 125 / 1,000 whole-item scans and 15,625 / 1,000,000 within-word calls. `@functools.lru_cache(maxsize=4096)` caches the pure tuple-keyed computation (`src/query.py:154-170`), called from `_marked` at `src/query.py:395-397`. The same single ISATUXIMAB entity survives. [Fresh instrumentation](cost/repeated_match_instrumentation.json), [reused script](cost/repeated_match_followup.py).

For the legal 3,999-character **answer** field, the fresh HTTP check takes **2.38207 s**, queues EGFR for **2.29969 s**, and takes **2.65707 s** warm. The ordinary map after completion takes 0.04031 s; all return 200. This verifies the repair without claiming all repeated-match work was removed. `_marked` still constructs/scans token lists before checking the cache and runs before entity deduplication (`src/query.py:340-368,553-563`). [HTTP](cost/isolated_repeated_match_cost_http.json), [closed owned server / unchanged DB](cost/repeated_match_cost_lifecycle.json).

`engine.lock` serializes API operations (`src/app.py:247-263`). These 3,999/4,000-character workloads use direct linking or the **answer field**; explore correctly rejects more than 500 characters. Limits precede NFKC (`src/app.py:239-243,260`; `src/query.py:117-118,254-256`). Residual costs are should-fix observations, not the reason for the verdict. **No model calls or model cost were incurred.**

## Standards

**No documented-standard violation found.** Reviewed fixed point `bfcb83d` through HEAD `4df54ae7f8bd16babc4ccb2dd0e8d4ce0314098b`, using `git diff bfcb83d...HEAD -- src/app.py web/try.html`, and the latest query/test patch. Both diffs are nonempty. [App/UI diff](db_ui/review_diff_app_ui.txt), [latest patch](db_ui/review_diff_latest.txt).

`git ls-files '*AGENTS.md' '*CONTRIBUTING.md' '*CODING_STANDARDS.md' 'docs/agents/*'` returned no tracked standard files. [Inventory](db_ui/review_diff_standards.txt). The user's audit instructions govern: independent evidence-based review, no tracked-file changes, new scratch files only under m17, and FIXED / NOT FIXED per earlier finding. Reproductions preserve original fixture logic, record source/adapted hashes, and compare API output against stored rows. Mutation fixtures use isolated in-memory databases; UI test limitations are explicit.

No application code was edited. The user's conditional instruction to compare original/modified code against KOA Studio and KhOpenApi references therefore does not arise. Issue-tracker setup was not performed because the explicit audit-only/no-tracked-edit scope takes precedence over skill setup guidance.

**Specification defect, not a standards violation:** the new one-letter reverse-isotope check operates after punctuation removal. `iodine-I-124-labelled trastuzumab` loses the boundary before I and passes every refusal stage, drawing unlabelled TRASTUZUMAB. The separate attack/specification review owns severity and verdict. [Independent stages](db_ui/adjudication_tracer.json).

Inherited README comments still say 317 tests (`README.md:565`, `README.ko.md:386`); nearby app descriptions remain accurate. This is a documentation should-fix, not a new documented coding-standard violation.

## Specification

Spec source: the user's Round 17 brief and original relation-map guarantees; baseline `bfcb83d` to HEAD `4df54ae7f8bd16babc4ccb2dd0e8d4ce0314098b`.

The round requires "element-first one-letter isotopes inside one word (I-124, F18, C14, Y-90) count". The original approval bar forbids a refused tracer being drawn as the originator.

**Wrong/partial behavior, P1:** `trastuzumab labelled-I-124` contains I-124 inside one original word, visibly separated from the preceding letters by a hyphen. Every refusal stage misses, and the actual HTTP map draws unlabelled TRASTUZUMAB / CHEMBL1201585 with 13 clinical trials. Trial and sponsor QA each return 12 originator evidence rows. `trastuzumab labelled-124I`, `I-124-labelled trastuzumab`, and `trastuzumab labelled with I-124` refuse. In `src/query.py:164-169`, punctuation is removed before the negative letter lookbehind, so the hyphen-delimited I becomes a letter inside the flattened run `labelledi124`. This is an inherited gap present in HEAD^, newly reproduced here, rather than a demonstrated newly introduced leak. New stage captures, exact HTTP requests, and paired counterfactuals are in [new_results.json](attacks/new_results.json) / [new_http.json](attacks/new_http.json).

**Repair success:** the 42 original m16 attack/control cases were rerun, and original M16-B1 forms now refuse. Original M15 chelator/lowercase cases remain refused. Ordinary BKM120/AZD9291, dose/schedule, and bare-drug controls survive. The 428 transformed aliases over 104 keys have zero changed centre/refusal outcomes from m16. Cached item-state performance is measured separately by the root.

**Scope:** no tracked edits or missing spec were observed. Recorded over-refusals and ChEMBL biosimilar-code curation are outside blocker scope. No independent additional blocker is inferred from the same-family corroborations.

Specification: **one newly promoted P1 family**, sufficient for CHANGES REQUIRED.

## Integrity and reproduction

`Engine.ask` passes `use_llm=False` (`src/app.py:181`). Mutation fixtures use in-memory copies. The application's SQLite connection is not globally read-only; no-write conclusions rely on the inspected/executed paths and before/after hashes. Final verification compares **6,119 tracked-file SHA-256 hashes**, unchanged HEAD, clean tracked/staged diffs, unchanged database bytes, report links, and closed owned ports. [Initial snapshot](integrity_before.json), [final verification](integrity_final.json). DB SHA-256: `7341c5a7089731f67356da5a588b269d4b69e8e6c4c054acf19aa4ef2837b529`.

Run from repository root with bytecode disabled and temporary paths inside each m17 family's `tmp/`. Shared-port suites must run sequentially; cost must run after other workloads. The manifests retain original/adapted hashes and path/port changes. The name worker caught an accidental scratch-only port substitution inside the `DX-8951F` control, restored the original input, and reran the affected probe; final dispositions use corrected outputs. [Literal-preservation audit](names/adaptation_literal_check.json).

```text
python -B audit_evidence_claims/m17/root_checks/run_all.py
python -B audit_evidence_claims/m17/root_checks/run_late.py
python -B audit_evidence_claims/m17/root_checks/independent_m16_http.py
python -B audit_evidence_claims/m17/root_checks/independent_m17_http.py
python -B audit_evidence_claims/m17/names/run_round9.py
python -B audit_evidence_claims/m17/names/run_additional.py
python -B audit_evidence_claims/m17/names/run_completion.py
python -B audit_evidence_claims/m17/db_ui/run_db.py
python -B audit_evidence_claims/m17/db_ui/run_ui.py
python -B audit_evidence_claims/m17/db_ui/run_final.py
python -B audit_evidence_claims/m17/attacks/new_probe.py
python -B audit_evidence_claims/m17/attacks/new_http.py
python -B audit_evidence_claims/m17/cost/run_isolated.py
python -B audit_evidence_claims/m17/cost/repeated_match_followup.py
python -B audit_evidence_claims/m17/build_cost_section.py
python -B audit_evidence_claims/m17/build_report.py
python -B audit_evidence_claims/m17/finalize_integrity.py
```

Standards: **0 documented violations**. Specification: **one new P1 family**, sufficient to reject approval.

VERDICT: CHANGES REQUIRED
