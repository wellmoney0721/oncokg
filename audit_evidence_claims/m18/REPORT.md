# Independent relation-map review — round 18

Reviewed **`4bed79c1f170ebe1efa3d452ce4398cce17b2113`**. **CHANGES REQUIRED: one newly reproduced P1 originator-refusal family.** `trastuzumab radiolabelled with iodine-124` passes every refusal stage and draws unlabelled TRASTUZUMAB, with 13 map trials and 12 trial / 12 sponsor QA evidence rows. Its `I-124` spelling refuses. This is an inherited gap present in HEAD^, not a demonstrated latest-patch regression.

All exact previously promoted M1–M17 primary name blockers are **FIXED**, including M17-B1 `trastuzumab labelled-I-124`. Earlier supplemental gaps, availability limits and cost/UI/documentation qualifications retain individual **NOT FIXED** dispositions below. They are not silently counted as repaired. The user-listed over-refusals and ChEMBL bevacizumab-code limitation do not determine this verdict.

No application source or tracked file was edited. New scratch files are confined to `audit_evidence_claims/m18/`.

## Verification and scope

- **345 passed in 39.81 s**, exit 0: `python -m pytest tests -q -p no:cacheprovider`. Bytecode disabled; temporary paths confined to m18. [Test output](root_checks/pytest.txt), [command/environment/hashes](root_checks/pytest_summary.json).
- Reused cumulative originals cover m1, partial m2/completed m2b, and m3–m17. Root main, remaining and late batches exit zero; m16 independent HTTP replays 19 cases / 76 requests; m17 replays 17 cases / 68 requests. [Report inventory](historical_report_inventory.json), [root provenance](reuse_manifest_root.json), [main](root_checks/execution_all.json), [remaining](root_checks/execution_remaining.json), [late](root_checks/execution_m18_late.json), [m16 HTTP](root_checks/independent_m16_http.json), [m17 HTTP](root_checks/independent_m17_http.json).
- Historical naming: **62 scripts reused / 52 leaf reproducers executed**, all successful. **78 disposition rows: 62 FIXED / 16 NOT FIXED**. Raw **7,511-key** alias sweep has **zero new losses or recoveries versus m17**. Adapted frozen **1,648-question** comparison remains **68 identical / 1,556 metadata-only / 24 semantic / zero errors**. Diagnostic raw sweep differences are not defect counts. [Name review](names/FINDINGS.md), [execution checks](names/worker_final_checks.json), [alias delta](names/new_alias_losses.json), [QA comparison](names/adapted_frozen_qa_relink_sweep.json).
- Stored-row oracle: **6,469 live centres / 22 relation-direction-type-role combinations / zero errors**. **19/19 DB**, **24/24 UI**, **4/4 self-loop/unknown-type/retirement** checks pass. [Oracle](db_ui/db_validate.json), [DB](db_ui/db_assertions.json), [UI](db_ui/ui_assertions.json), [fixture](db_ui/self_loop_unknown.json).
- **36/36 demos** equal every m7–m17 full-response baseline, and all 36 original-CLI HTTP demo responses equal direct Engine responses. Six map callbacks pass; seven original QA evidence counts remain **12, 12, 11, 1, 12, 0, 0**. [Baseline comparisons](db_ui/demo_previous_comparison.json), [HTTP](db_ui/demo_http.json), [callbacks](db_ui/ui_m3_checks.json).
- Attack worker: **231 historical staged cases + 64 fresh current/HEAD^ paired cases**, **676 actual CLI HTTP requests**, all 200; **428 transformed aliases / 104 keys** have no centre/refusal changes versus m17. A separate name worker reran 63 m17 staged cases / 252 HTTP requests; DB/UI independently replayed 36 previous stage cases. Root independently confirmed the new family and controls with **19 cases / 76 HTTP requests**. These counts overlap by design and are not summed as unique cases. [Attack assertions](attacks/final_checks.json), [alias comparison](attacks/alias_variants_comparison.json), [name HTTP](names/m17_exact/new_http.json), [DB/UI stages](db_ui/adjudication_tracer.json), [root assertions](root_checks/independent_m18_summary.json).

UI checks execute actual page JavaScript in a Node VM with controlled DOM/fetch stubs: they verify generated markup and exercised callbacks/state, not browser painting or browser-executed XSS. HTTP uses unmodified `src/app.py` on owned ports other than 8765, or its actual handler with isolated in-memory fixtures. Counterfactuals replace only the stated query code against current remaining modules/data; they are not complete old deployments. No model was called.

## M18-B1 — P1: iodine-124 wording draws unlabelled trastuzumab

**Exact input:** `trastuzumab radiolabelled with iodine-124`.

The actual CLI server returns HTTP 200 for `/api/explore` and draws **TRASTUZUMAB / CHEMBL1201585**, with **13 live trials**, without a refusal. `Which trials evaluate trastuzumab radiolabelled with iodine-124?` and `Who sponsors trials of trastuzumab radiolabelled with iodine-124?` each return **12 originator evidence rows**. Changing only `iodine-124` to `I-124` or `124I` produces a refusal and zero trial/sponsor evidence. Bare trastuzumab remains available.

The input explicitly describes a radiolabelled product; it does not merely list iodine separately from trastuzumab. The original study constructed a PET radioligand by labelling trastuzumab with iodine-124, and PubMed indexes Iodine-124 as a substance for that study. This establishes the tracer/originator distinction for the primary example. [Guo et al., original study, PMID 31919745](https://pubmed.ncbi.nlm.nih.gov/31919745/). The notation and isotope/product distinction were freshly checked, not inferred solely from a spelling pattern. No medical recommendation is made.

The original approval bar says there must be no known way to draw a refused product as the originator. The paired symbol spelling of this same tracer is refused, whereas the ordinary full element name bypasses every stage. [Full stage records](attacks/new_results.json), [summary](attacks/new_summary.json), [actual HTTP requests/responses](attacks/new_http.json).

| Stage | `trastuzumab radiolabelled with iodine-124` | `trastuzumab radiolabelled with I-124` |
|---|---|---|
| Raw intervention resolver | CONTAINED_ALIAS + UNRESOLVED; no BLOCKED component | CONTAINED_ALIAS + UNRESOLVED |
| `_qualified` | false | false |
| `_resolver_blocked` | `{}` | `{}` |
| `_item_has_isotope` | false | true |
| Actual `_marked` call | `None`; four tokens, all segment 0 | returns refusal |
| `_whole_name` | `None` | `None` |
| Public linker | Drug TRASTUZUMAB; no Refused | Refused only |
| Map | CHEMBL1201585, 13 trials | refused, no centre |
| Trial / sponsor QA | 12 / 12 | 0 / 0 |

**Code cause:** the medical-mass table keys are element **symbols** (`src/query.py:124-128`). `_medical_isotope_in` only reads one/two-letter symbols (`src/query.py:136-150`); `_item_has_isotope` tries the canonical token, punctuation-separated pieces, and each adjacent concatenation, but never converts a full element name to its symbol (`src/query.py:154-173`). For `iodine-124`, the checked keys include `iodine124`, `iodine`, `124`, and `iodine124`; none becomes `i124`. The inverse regex may see `ne124`, and the one-letter inverse regex cannot treat the final `e` as a standalone element. [Exact helper inputs](attacks/helper_evidence.json).

Earlier layers also have no full element-name radiolabel rule: `_qualified` delegates to product/tracer patterns (`src/query.py:207-229`), whose isotope expressions accept only one/two-letter symbols (`src/textrules.py:289-314`). `_resolver_blocked` cannot block this input because its recorded components are CONTAINED_ALIAS and UNRESOLVED (`src/query.py:301-319`). `_marked` sees no recognised neighbouring/own isotope and the item check is false (`src/query.py:370-400`). `Engine.explore` therefore selects the surviving positive Drug (`src/app.py:88-95`). This is not a whole-name override, database alias corruption, or loss of a previously recorded refusal.

**Corroborations:** `iodine-124 trastuzumab`, `trastuzumab iodine-124`, `trastuzumab labelled-iodine-124`, `trastuzumab iodinated with iodine-124`, `trastuzumab (iodine-124)`, and `trastuzumab [iodine-124]` have the same wrong centre and 12/12 QA evidence. Uppercase, underscore and colon variants also bypass. Comma/and reversals keep the tracer as an accepted Drug even when OSIMERTINIB is selected first. Full-name zirconium-89/copper-64 forms behave the same, while their symbol controls refuse. Other synthetic element/drug pairs are common-cause probes, not claims that each is a marketed product or independent blockers.

**Required behaviour:** recognise this explicit iodine-124-labelled product consistently with its I-124/124I spellings; it must not draw unlabelled TRASTUZUMAB. Retain ordinary drugs, code/salt aliases and dose/schedule controls. No application repair was made.

## Independent confirmation and repair assessment

The root independently started the original CLI server on port 8849, verified served page bytes, and issued resolve/explore/trial-QA/sponsor-QA requests. Four full-element-name inputs (`iodine-124 trastuzumab`, `trastuzumab radiolabelled with iodine-124`, `trastuzumab labelled with iodine-124`, `trastuzumab radiolabelled with zirconium-89`) draw CHEMBL1201585 with 13 trials and 12/12 QA evidence, without refusal. Seven paired symbol/M17 controls refuse with no centre and zero QA evidence. `BKM120`, `AZD9291`, `osimertinib 80 mg`, `paclitaxel 2 cycles`, and `13-cis retinoic acid` remain available. Comma-list reversal exposes the accepted tracer even when OSIMERTINIB is selected first. [All 76 requests/responses](root_checks/independent_m18_http.json), [explicit assertions](root_checks/independent_m18_summary.json), [server lifecycle](root_checks/independent_m18_lifecycle.json), [adaptation](root_checks/independent_m18_manifest.json).

The separate DB/UI reviewer independently captures `_qualified=false`, `_resolver_blocked={}`, `_marked=None`, `_whole_name=None`, Drug-only linking, 13 map trials and 12/12 QA for `trastuzumab labelled with iodine-124`, in current and HEAD^ code. [Independent stages](db_ui/independent_boundary.json). This corroborates M18-B1 rather than adding a blocker count.

The actual latest patch preserves punctuation boundaries for symbol notation (`src/query.py:164-172`). Twenty-four formerly leaking centre cases in the 63-case m17 attack set improve; the old primary `trastuzumab labelled-I-124` now refuses. This validates the repair while showing that the full-name identity gap remains. [M17 stage replay](attacks/m17_results.json), [M17 root HTTP](root_checks/independent_m17_http.json).

## Earlier reproductions — FIXED / NOT FIXED per finding

Status applies to the exact prior reproduction, not every possible spelling. Passing exit codes alone are not the basis for these dispositions; returned identities, refusal existence, stored values and QA evidence are inspected. M2 has no completed report: its partial fixtures are included through m2b. Matrices overlap where independent reviewers reproduced the same finding, so their row totals are not a count of unique defects.

### Name resolution, m1–m17

**78 rows: 62 FIXED / 16 NOT FIXED.**

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
| M15 repair note / user GS-11CAL-101 known over-refusal | **NOT FIXED** | The raw stored-alias sweep continues to refuse this alias. Explicitly user-accepted, nonblocking; no new raw-alias loss versus M17. [Evidence](names/names_m5_summary.json). |
| M15 repair note / user 3en3hg4wsw known over-refusal | **NOT FIXED** | The raw stored-alias sweep continues to refuse this alias. Explicitly user-accepted, nonblocking; no new raw-alias loss versus M17. [Evidence](names/names_m5_summary.json). |
| M16 M16-B1 element-first one-letter isotope within one word | **FIXED** | I-124-labelled trastuzumab, trastuzumab labelled with I-124, I124/i-124/[I-124] variants and H3/H-3 vinblastine corroborations now refuse with no centre and zero trial/sponsor evidence. Bare controls survive; separate comma-osimertinib remains selected with refusal disclosed. All 42 original stage cases replayed. [Evidence](names/m16_exact/new_results.json). |
| M17 M17-B1 punctuation-delimited element-first one-letter isotope | **FIXED** | Original trastuzumab labelled-I-124 and 21 punctuation/case/H3/F18/C14/Y90 corroborations now refuse without a centre and with zero trial/sponsor evidence. Separate-list osimertinib survives with refusal disclosed. All 63 original staged cases and 252 original HTTP requests replayed; dose/BKM120/AZD9291/bare controls survive. [Evidence](names/m17_exact/new_results.json). |


### DB, UI, server and documentation

**27 rows: 22 FIXED / 5 NOT FIXED**, including independent overlap with the naming matrix.

| Earlier finding / exact reproduction | Round 18 result and evidence |
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
| M16-B1 exact element-first one-letter inputs: `I-124-labelled trastuzumab`, `trastuzumab labelled with I-124`, `I124 trastuzumab`, `F18 trastuzumab`, `C14 paclitaxel` | **FIXED**. Current and HEAD^ refuse the original unlabelled-originator spellings with zero QA evidence. [Independent stages](db_ui/adjudication_tracer.json). |
| M16 labelled-product qualification: `89ZrDFO 18-FDG` / `89-ZrDFO 18-FDG`, lutathera/FDG isotope variants | **NOT FIXED**, unchanged nonblocking discrepancy under the explicitly permitted labelled-product exception. All 17 original m16 adjudication inputs rerun. [stages](db_ui/adjudication_tracer.json). |
| M1-M17 README test-count comments, README.md:565 / README.ko.md:386 | **NOT FIXED**, inherited documentation-only: both say 317 tests. Nearby app descriptions remain accurate. [Standards](db_ui/STANDARDS.md). |
| M17-B1 punctuation-before-symbol: `trastuzumab labelled-I-124`; `iodine-I-124-labelled trastuzumab`; `trastuzumab labelled with iodine-I-124` | **FIXED**. Every original selected tracer input refuses, with zero trial/sponsor QA evidence; HEAD^ still leaks. Adjacent symbol pieces now preserve the boundary. `src/query.py:164-172`. [Fresh m17 staged replay](db_ui/adjudication_tracer.json), [exact main input](db_ui/independent_boundary.json). |



### Accepted exceptions and unresolved historical qualifications

The user explicitly excludes these known over-refusals from blockers: M5-S2; 40-o-/42-o-(2-hydroxyethyl)rapamycin; Trastuzumab--vcmmae conjugate; 9-amino-20(s)-camptothecin; il-6ra; TAK-659F; GS-11CAL-101; 3en3hg4wsw; and same-list-item refusal. The ChEMBL bevacizumab biosimilar-code synonym limitation is also explicitly excluded. Fresh dispositions retain these exclusions.

Other old supplements are not presented as accepted exceptions or as fixed: `b.i.o.similar bevacizumab` still draws BEVACIZUMAB with 122 trials and 12/12 QA rows; `lip.osomal doxorubicin` still draws DOXORUBICIN with 3 trials and 3/3 QA rows. Reversed formulation wording and prefixed comma-containing drug-name QA also remain NOT FIXED as tabulated. These are inherited unresolved gaps, not newly discovered M18 families. The new natural iodine-124 description is independently sufficient for rejection under the original approval bar. [Replayed supplemental cases](names/m12_attacks/focused_results.json), [reversed wording](names/reversed_results.json), [comma-name QA](names/historical_focus.json).

Lowercase IDs/investigator-name lookup, slash PET/CT not_found wording, blank-form state, malformed-body error text, README test counts and residual costs remain separately recorded. Failure-closed observations and presentation issues are should-fix items, not the new originator blocker.

## Additional diagnostic probes



- `trastuzumab labelled-I-1-24` still bypasses while `trastuzumab labelled-I-124` refuses: a reverse isotope spread across three punctuation pieces can escape the adjacent-pair budget. The split mass is an artificial spelling; it is not needed to establish M18-B1. The same applies to `labelled-C-1-4`. [Stage records](attacks/new_results.json).
- `trastuzumab labelled-I 124` bypasses. The documented item rule intentionally excludes one-letter symbols across whitespace to protect text such as `13 NSCLC`. This is recorded without calling that deliberate scope choice a new patch regression.
- A preferred-name `_labelled` inventory contains 14 visibly isotope-labelled drug names; no accidental exemption for a clearly unlabelled preferred name was observed. A synthetic `FDG labelled-C-14` selects the stored F18 product while `FDG 14C` refuses, because an already-labelled preferred name bypasses the item-wide guard. This is an unpromoted isotope-compatibility concern, not the originator blocker; product identity for that synthetic input was not independently established. [Inventory](attacks/labelled_preferred_names.json), [probe](attacks/labelled_exception_probe.json).


## Cost and performance reproductions

All nine inherited cost scripts exited zero, sequentially after other audit CPU/HTTP workloads finished. The additional M16 repeated-match instrumentation and HTTP reproducer also exited zero. Unrelated host load is uncontrolled; these are measurements, not service guarantees. Counterfactuals substitute only historical `query.py` against the same current app/data. [Execution](cost/execution_isolated.json), [provenance](reuse_manifest_root.json), [M16 follow-up execution](cost/repeated_match_execution.json).

| Historical finding / exact workload | Current disposition and measured evidence |
|---|---|
| M5-S3 cubic qualifier scan, `' '.join(['x']*250)` (499 chars) | **FIXED for the original workload.** 2,224 calls to each predicate / 33,880 aggregate predicate-input characters, 0.02802 s direct. [Instrumentation](cost/perf_current.json). |
| Original 999-character plain-answer timeout, `' '.join(['x']*500)` | **FIXED.** HTTP check 200 in 0.18285 s; later map 0.03814 s. [HTTP](cost/perf_check_http.json). |
| M6/M7 repeated 2,000-piece resolver cost, `';'.join(['x']*2000)` | **FIXED for this repeated-piece control.** Current / historical `9bd7cb4` direct medians 0.16809 / 2.32935 s. HTTP check 0.41127 s, queued EGFR 0.32796 s, both 200. [Comparison](cost/fresh_cost_comparison.json), [HTTP](cost/fresh_cost_http.json), [stress](cost/cost_stress.json). |
| M8-S1 4,097th resolver-cache entry | **FIXED.** 82/82 fill requests succeed; rollover and retry return OSIMERTINIB / CHEMBL3353410 with 79 trials, no KeyError. [HTTP](cost/cache_boundary_http.json). |
| M10-M17 distinct-piece lock delay, `';'.join(f'isa x{i:04d}' for i in range(400))` | **NOT FIXED**, inherited cost concern. Cold check 2.46990 s, queued EGFR 2.40004 s, warm 0.37761 s; all 200. [HTTP](cost/isolated_unique_cost_http.json), [instrumentation](cost/unique_piece_cost.json). |
| M11-M17 Unicode expansion, answer `'\ufdfa'*4000` | **NOT FIXED**, inherited cost concern. 4,000 chars expand to 72,000 under NFKC. Cold check 2.27104 s, queued EGFR 2.18763 s, warm 2.86132 s; all 200. [HTTP](cost/isolated_unicode_cost_http.json). |
| M11-M17 punctuation normalization, `' - '.join(['x']*1000)+'xx'` | **NOT FIXED as measured overhead**, no error. Current / HEAD^ medians 0.36324 / 0.30057 s; at 499 chars 0.03552 / 0.03624 s. [Comparison](cost/normalization_cost.json). |
| M12-M17 repeated matches, `' '.join(['isa']*1000)` | **NOT FIXED as residual repeated-match overhead**; **M16-S1 added isotope rescans FIXED**, detailed below. Current / HEAD^ direct medians 1.03520 / 1.03293 s; at 499 chars 0.03586 / 0.03487 s. [Comparison](cost/normalization_cost.json). |
| M13-M17 repeated isotope alias, `';'.join(['A33 124i']*444)` | No error reproduced. Current / HEAD^ medians 0.08762 / 0.07724 s. Cached ordinary OSIMERTINIB 0.00012 / 0.00013 s. All 24 workload/version rows complete. [Comparison](cost/normalization_cost.json). |
| Disease / ordinary concurrent maps | No failure reproduced: 2,774 Trials + 300 Targets, 30 per list, **18,575 bytes / 98.027 ms**. 24 requests / 12 workers all expected HTTP200 shapes in **863.322 ms**. These ordinary early samples overlapped other audit work. [HTTP](root_checks/http_results.json). |

### M16-S1: the item's isotope state is now computed once

**FIXED for the exact reported extra work.** At 125 / 1,000 occurrences, instrumentation records **one whole-item scan** and **250 / 2,000 within-word helper calls**, respectively. M16 originally recorded 125 / 1,000 whole-item scans and 15,625 / 1,000,000 within-word calls. M17 recorded one scan with 125 / 1,000 within-word calls. The latest patch checks both the canonical word and its punctuation piece, which are identical for `isa`; this doubles those within-word calls but does not restore per-match whole-item rescanning. `@functools.lru_cache(maxsize=4096)` caches the pure tuple-keyed computation (`src/query.py:154-173`), called from `_marked` at `src/query.py:398-400`. The same single ISATUXIMAB entity survives. [Fresh instrumentation](cost/repeated_match_instrumentation.json), [reused script](cost/repeated_match_followup.py).

For the legal 3,999-character **answer** field, the fresh HTTP check takes **2.31487 s**, queues EGFR for **2.23243 s**, and takes **2.45020 s** warm. The ordinary map after completion takes 0.03246 s; all return 200. This verifies the repair without claiming all repeated-match work was removed. `_marked` still constructs/scans token lists before checking the cache and runs before entity deduplication (`src/query.py:343-371,556-566`). [HTTP](cost/isolated_repeated_match_cost_http.json), [closed owned server / unchanged DB](cost/repeated_match_cost_lifecycle.json).

`engine.lock` serializes API operations (`src/app.py:247-263`). These 3,999/4,000-character workloads use direct linking or the **answer field**; explore correctly rejects more than 500 characters. Limits precede NFKC (`src/app.py:239-243,260`; `src/query.py:117-118,257-259`). Residual costs are should-fix observations, not the reason for the verdict. **No model calls or model cost were incurred.**

## Standards

**0 documented-standard violations found.** Fixed point `bfcb83d` through current HEAD `4bed79c1f170ebe1efa3d452ce4398cce17b2113`; inspected `git diff bfcb83d...HEAD -- src/app.py web/try.html` and `git show HEAD -- src/query.py tests/test_app.py`. Both diffs are nonempty. [App/UI diff](db_ui/review_diff_app_ui.txt), [latest patch](db_ui/review_diff_latest.txt).

`git ls-files '*AGENTS.md' '*CONTRIBUTING.md' '*CODING_STANDARDS.md' 'docs/agents/*'` returns no tracked standards files. [Inventory](db_ui/review_diff_standards.txt). The user's evidence-based, audit-only instructions govern: no tracked changes, fresh outputs only under m18, and FIXED / NOT FIXED for historical findings. Reused scripts preserve fixture logic and exact historical inputs; manifests record source/adapted hashes. Database mutation fixtures are isolated in-memory copies; the snapshot/oracle connection uses SQLite mode=ro. Node VM UI scope is explicitly limited to generated markup and exercised state/callbacks.

No application code was changed, so the user's conditional KOA Studio/KhOpenApi original-versus-modified code comparison does not arise. Issue-tracker setup was not performed because the explicit audit-only/no-tracked-edit scope takes precedence over skill setup guidance.

The latest patch preserves punctuation boundaries for one-letter isotope symbols, and original m17 examples now refuse. A separate specification gap remains for full element names: `trastuzumab labelled with iodine-124` misses every refusal stage and draws the unlabelled originator. This is a specification finding, not an independent standards violation; the attack reviewer owns its severity. [Independent stages](db_ui/independent_boundary.json).

Inherited README comments still say 317 tests (`README.md:565`, `README.ko.md:386`); adjacent app descriptions remain accurate. This is a documentation should-fix.

## Specification


Spec source: the user's Round 18 brief and original map guarantees. The latest patch implements its stated punctuation-piece/adjacent-pair rule, and exact M17-B1 reproductions are fixed. No scope-creep finding is identified.

**One P1 specification failure:** the original approval bar forbids drawing a refused tracer as its originator. `trastuzumab radiolabelled with iodine-124` is the same labelled product whose `I-124`/`124I` spellings are refused, but all resolver/linker guards miss it, the live HTTP map draws CHEMBL1201585 with 13 trials, and trial/sponsor QA each supplies 12 originator rows. Full element names never become the symbol-keyed isotope labels in `src/query.py:124-173`; the positive hit survives at `src/app.py:88-95`. Fresh primary identity evidence and paired stages/HTTP are above.

Both current and HEAD^ query code exhibit the miss against the same current data/app modules. Thus the latest repair succeeds on its exact target while an inherited tracer-identity hole remains. Known over-refusals and ChEMBL bevacizumab-code curation do not determine this finding. **Specification: one newly promoted P1 family; CHANGES REQUIRED.**


## Integrity and reproduction

`Engine.ask` passes `use_llm=False` (`src/app.py:181`). Database mutation fixtures use isolated in-memory copies. The app's SQLite handle is not globally read-only; no-write conclusions rely on the inspected/executed paths and byte comparisons. Final verification checks **6,672 tracked-file SHA-256 hashes**, unchanged HEAD, clean tracked/staged diffs, unchanged DB bytes, report links, and closure of ports identified in this run's server-lifecycle records. [Initial snapshot](integrity_before.json), [final verification](integrity_final.json). DB SHA-256: `7341c5a7089731f67356da5a588b269d4b69e8e6c4c054acf19aa4ef2837b529`.

The pre-existing m18 brief/log were preserved. Bytecode is disabled and temporary files remain under each m18 family's `tmp/`. Source/adapted hashes and path/port changes are recorded in the manifests. Original scripts are reused from m18 copies, so the earlier tracked audit directories are not rewritten. No application repair was implemented; the conditional request to show original/replacement production code against KOA Studio/KhOpenApi therefore does not arise.

Representative runners, from repository root (shared-port HTTP suites run sequentially; cost runs after other workloads):

```text
python -B audit_evidence_claims/m18/root_checks/run_all.py
python -B audit_evidence_claims/m18/root_checks/run_m18_late.py
python -B audit_evidence_claims/m18/root_checks/independent_m18_http.py
python -B audit_evidence_claims/m18/names/run_round9.py
python -B audit_evidence_claims/m18/names/run_remaining.py
python -B audit_evidence_claims/m18/db_ui/run_db.py
python -B audit_evidence_claims/m18/db_ui/run_ui.py
python -B audit_evidence_claims/m18/db_ui/run_final.py
python -B audit_evidence_claims/m18/attacks/new_probe.py
python -B audit_evidence_claims/m18/attacks/new_http.py
python -B audit_evidence_claims/m18/cost/run_isolated.py
python -B audit_evidence_claims/m18/cost/repeated_match_followup.py
python -B audit_evidence_claims/m18/build_cost_section.py
python -B audit_evidence_claims/m18/build_report.py
python -B audit_evidence_claims/m18/finalize_integrity.py
```

Standards: **0 documented violations**. Specification: **one newly promoted P1 originator-refusal family**, independently sufficient for rejection; unresolved historical supplements remain explicitly NOT FIXED.

VERDICT: CHANGES REQUIRED
