# Independent relation-map review - round 13

Reviewed **`481100c584ec772cc2332960ba5d3b28ba36ae6f`**. **Changes required: one P1 blocker, M13-B1.** The exact blocking inputs reported in m1-m12 are fixed, including M12's split-symbol/chelator aliases. A different spelling of that same refused stored tracer alias still passes every refusal stage and draws DARATUMUMAB. This is an inherited, newly demonstrated boundary, not a regression introduced by the latest commit.

No tracked file was edited. New scripts and outputs are confined to `audit_evidence_claims/m13/`; existing brief/log files were preserved. Known over-refusals and performance concerns are reported separately and do not determine the verdict.

## Verification and scope

- **340 passed in 28.95 s**, exit 0: `python -m pytest tests -q -p no:cacheprovider`. Bytecode disabled; temporary paths confined to m13. [Output](root_checks/pytest.txt), [execution/hash record](root_checks/pytest_summary.json).
- Reused the cumulative original HTTP runners: six original/cumulative runners, four M6 runners, M8/M9 confirmations, M10 confirmations, M11 exact HTTP and M12 exact HTTP plus the inherited supplementary probe. All exit 0. Inputs were preserved; output locations and owned ports changed. [Manifest](reuse_manifest_root.json), [main batches](root_checks/execution_all.json), [M6](root_checks/execution_m6_http.json), [remaining](root_checks/execution_remaining.json), [M12](root_checks/execution_m12_extra.json).
- **44 reused name leaf scripts** (from 52 reused scripts) ran with exit 0, covering **62 individual finding rows**, including the original M1 files, cumulative m2b-m12 matrices, **7,511-key** alias sweeps and **1,648-question** frozen no-relink counterfactual. The alias loss set and frozen counts are unchanged from m12: **70** prior-method positives without a current Drug; **68 identical / 1,556 metadata-only / 24 semantic / zero errors** in the frozen QA comparison. These are same-data method counterfactuals, not whole-deployment comparisons. [Name execution and individual findings](names/FINDINGS.md), [reuse manifest](names/reuse_manifest.json).
- Independent graph oracle: **6,469 live centres, 22 relation/direction/type/role combinations, zero errors**. **19/19 DB assertions**, **24/24 UI assertions**, and **4/4 self-loop/unknown-type/retirement fixture checks** pass. [Oracle](db_ui/db_validate.json), [DB](db_ui/db_assertions.json), [UI](db_ui/ui_assertions.json), [fixture](db_ui/self_loop_unknown.json).
- **36/36 page demos and all six map callbacks pass.** Every full demo response equals m7-m12; all 36 actual CLI HTTP requests return 200 and equal direct Engine responses. The seven original QA evidence counts remain **12, 12, 11, 1, 12, 0, 0**. [Comparison](db_ui/demo_previous_comparison.json), [HTTP](db_ui/demo_http.json), [callbacks](db_ui/ui_m3_checks.json).
- New attacks compare **27 inputs** with current and HEAD^ query modules and reuse the **41-input** m12 attack matrix. **184 attack HTTP requests**, plus **60 root-independent HTTP requests** and **56 exact m12 root replay requests**, all returned 200. Servers closed; served pages match `web/try.html`. [Stages](attacks/fresh_results.json), [reused attack stages](attacks/focused_results.json), [attack execution](attacks/execution.json), [independent HTTP](root_checks/independent_m13_http.json), [independent lifecycle](root_checks/independent_m13_lifecycle.json), [M12 lifecycle](root_checks/independent_m12_lifecycle.json).

UI checks execute actual page JavaScript in a Node VM with controlled DOM/fetch stubs. They verify generated markup and exercised state/callback behavior, not browser painting or browser-executed XSS. Real HTTP checks use unmodified `src/app.py` or its handler with isolated in-memory fixtures. No audit used port 8765. No model was called. No external pharmacology assumption is used: identity evidence comes from the repository dictionary, canonical key, predicates and refused controls.

## M13-B1 - P1: removing an isotope/chelator separator bypasses every refusal

Exact request: `POST /api/explore` with `{"text":"89ZrDFO-daratumumab"}`.

**Actual:** HTTP 200, centre **DARATUMUMAB / CHEMBL1743007**, matched alias **`89zr-dfo-daratumumab`**, **2 live trials**, no Refused entity or refusal notice. `Which trials evaluate 89ZrDFO-daratumumab?` and `Who sponsors trials of 89ZrDFO-daratumumab?` each return **2 originator evidence rows**. Fully glued `89zrdfodaratumumab` does the same. Appending `, osimertinib` still selects DARATUMUMAB. [Root HTTP evidence](root_checks/independent_m13_http.json), [separate worker adjudication](db_ui/adjudication.md).

**Control and identity proof:** `[89Zr]-DFO-daratumumab`, `89Zr-dfo-daratumumab` and the repaired `[89Z.r]-DFO-daratumumab` refuse, with no centre and zero qualified trial/sponsor evidence. Bare `daratumumab` works. The leaking spelling and refused control share **canonical key `89zrdfodaratumumab`**, mapped uniquely to the AACT synonym `89zr-dfo-daratumumab` for DARATUMUMAB. Thus the positive lookup recognizes the very stored tracer identity whose refusal is lost; this is not a guess about an unrelated unknown name. [Dictionary evidence](attacks/dictionary_evidence.json).

| Stage for `89ZrDFO-daratumumab` | Observed result |
|---|---|
| Raw resolver | `ALIAS` to CHEMBL1743007; no blocked component |
| Resolver veto | `{}` |
| Item linker | Drug DARATUMUMAB; no Refused |
| Whole-name shortcut | `None`; it does not override an existing refusal |
| Public linker | Drug DARATUMUMAB; no Refused |
| Map / trial QA / sponsor QA | Originator centre / 2 evidence rows / 2 evidence rows |

The tested hypothesis is that the latest scan closes split symbols but still relies on input word boundaries. The evidence supports it:

1. Positive lookup deletes separators (`src/textrules.py:339-346`) and matches the complete alias (`src/query.py:413-426`).
2. `_alnum_words` splits only at non-ASCII-letter/digit separators (`src/query.py:111-113`). The candidate produces `['89ZrDFO', 'daratumumab']`; `89Zr` is not a separate word. The new scan at `src/query.py:258-267` glues complete words but never separates an isotope from an already joined word. The first word has seven characters and exceeds its six-character bound.
3. All isotope text is inside the consumed alias, so outside-neighbour checks cannot recover it (`src/query.py:273-289`).
4. The key-prefix fallback isolates `89zr` but requires `dfodaratumumab` to be a same-drug dictionary key (`src/query.py:291-295`). It is absent; only the shorter `daratumumab` key exists. The same failure affects the fully glued alias.
5. Raw tracer predicates also miss this boundary (`src/textrules.py:303-314`; `src/normalize.py:740-745`); the item guard returns false (`src/query.py:119-141`). With all guards silent, `Engine.explore` selects the surviving hit (`src/app.py:87-95`).

Current and exact HEAD^ (`d9260a1ea544cf7bb80415383667784e0aba146a`) query modules both reproduce the leak against the same current app/rules/database. This identifies an **inherited unclosed boundary**, while exact M12-B1 inputs now refuse. [Current/previous comparison](attacks/fresh_results.json), [independent comparison](db_ui/adjudication_tracer.json).

**Required outcome:** positive alias normalization must preserve refusal of a stored tracer identity even when the isotope is joined to its chelator or another alias component. Refusal must not require an independently stored isotope-stripped remainder. No fix was implemented in this audit.

`A33124I` is an additional example of the same boundary: stored alias `A33 124i` refuses, but the glued spelling maps to ADAKITUG / CHEMBL5314551 because remainder `a33` is not a standalone key. It has zero trial/sponsor evidence; it is corroboration of M13-B1, not a second counted blocker. [Root HTTP](root_checks/independent_m13_http.json), [dictionary evidence](attacks/dictionary_evidence.json).

## Earlier reproductions - FIXED / NOT FIXED per finding

These tables classify exact historical reproductions, not an entire input family. M12-B1 can therefore be FIXED while M13-B1 remains a blocker. m2 ended without a completed report; its partial role/order fixtures and the completed m2b findings are included. Earlier script bodies and historical read-only comparison sources were reused, not historical result files presented as new evidence.

### Name resolution, m1-m12

| Round / finding | Status | Current evidence |
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
| M12 M12-S1 rad001c / RAD001C stored-alias over-refusal | **NOT FIXED** | Still refuses with no centre, as in M12. Current and HEAD^ agree. rad, RAD001, EVEROLIMUS and exact ID remain available. This is inherited and nonblocking. [Evidence](names/new_alias_regression.json). |
| M12 M12 supplementary previously unpromoted descriptive label-distance inputs | **NOT FIXED** | The old labelled/labeled-distance forms still draw TRASTUZUMAB and match the HEAD^ result. Retained separately from the new joined-chelator blocker, consistent with prior classification. [Evidence](names/m12_attacks/focused_results.json). |

### Relations, stored values, UI, server and wording

| Earlier finding / exact reproduction | Round 13 result and evidence |
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
| M1/M2b silent truncation: "x"*500 + " osimertinib" and "osimertinib " + "x"*600 | **FIXED**. Both exact oversized inputs return 400 with `input is longer than 500 characters`; neither silently draws the retained prefix. `src/app.py:239-243`. [Fresh root HTTP](db_ui/../root_checks/http_results.json). |
| M1/M2b malformed JSON/list/null/oversized-body parser-error disclosure | **NOT FIXED**, inherited nonblocking qualification. Requests fail closed with 400; list/null bodies still expose `.get` errors and the 20,000-byte body cap can expose JSON parser text. Valid later calls succeed. `src/app.py:236-240,264-269`. [Fresh root HTTP](db_ui/../root_checks/http_results.json). |

### Supplemental cases and accepted over-refusals

The explicitly accepted M5-S2, `40-o-(2-hydroxyethyl)-rapamycin`, `42-o-(2-hydroxyethyl)rapamycin`, `Trastuzumab--vcmmae conjugate`, `9-amino-20(s)-camptothecin`, `il-6ra`, and `TAK-659F` remain **NOT FIXED / known over-refusals**, not blockers. M12-S1 `rad001c` remains refused; `RAD001`, EVEROLIMUS and its ID still work. It remains the earlier recorded nonblocking alias loss, not a new m13 regression. [Name controls](names/FINDINGS.md), [root HTTP](root_checks/independent_m13_http.json).

`99MTc trastuzumab` and `[99MTc] trastuzumab` remain **FIXED**: both refuse with no centre in the inherited probe. [Exact replay](root_checks/fresh_probe.json).

M11/M12 supplementary descriptive-distance isotope forms and punctuated lexical qualifiers remain **NOT FIXED**, as individually recorded in the fresh reused matrix; they are not counted as new regressions or additional blockers. The M12 supplementary `Lutetium (177L.u) dotatate` now refuses (**FIXED**); its previous centre was already isotope-labelled and was not an unlabelled-originator blocker. [Exact supplementary dispositions](attacks/FINDINGS.md), [original-case replay](attacks/focused_results.json), [inherited probe](root_checks/fresh_probe.json).

## Cost and performance reproductions

All nine inherited cost scripts exited 0, run sequentially after the other agents' CPU/HTTP workloads ended. Unrelated host activity is uncontrolled. These are measured observations, not latency guarantees or a proof of global complexity. Historical comparisons swap only the query module against the same current remaining modules/database. [Execution](cost/execution_isolated.json), [source manifest](cost/../reuse_manifest_root.json).

| Historical reproduction / exact workload | Current observation and disposition |
|---|---|
| M5-S3 all-runs scan, `' '.join(['x']*250)` (499 characters) | **FIXED for this original workload**: 2,224 calls per product/tracer predicate and 33,880 aggregate predicate-input characters; direct-link 0.02745 s. Work no longer enumerates all arbitrarily long word windows. [Instrumentation](cost/perf_current.json). |
| Original 999-character plain-answer timeout, `' '.join(['x']*500)` | **FIXED**: real `/api/check` HTTP 200 in **0.17800 s**; ordinary subsequent map **0.03380 s**. [Exact HTTP](cost/perf_check_http.json). |
| M6/M7 repeated 2,000-piece resolver cost, `';'.join(['x']*2000)` | **FIXED for the exact repeated-piece control**: current direct-link median **0.15732 s** versus historical `9bd7cb4` **1.85562 s**. HTTP check **0.42723 s**, queued EGFR **0.34353 s**, both 200. [Comparison](cost/fresh_cost_comparison.json), [HTTP](cost/fresh_cost_http.json), [stress replay](cost/cost_stress.json). |
| M8-S1 natural 4,097th resolver-cache entry | **FIXED**: **82/82** fill requests create 4,096 distinct pieces; first osimertinib at rollover and retry both HTTP 200, CHEMBL3353410, 79 trials. No KeyError. [Exact HTTP](cost/cache_boundary_http.json). The separate original 7,511-key naming sweep also completes without cache errors. |
| M10/M11/M12 distinct-piece lock contention, `';'.join(f'isa x{i:04d}' for i in range(400))` (3,999 answer characters) | **NOT FIXED**, inherited nonblocking cost concern: cold `/api/check` **2.22874 s**, queued ordinary EGFR map **2.14799 s**, warm check **0.46838 s**, all 200. Instrumented direct-link makes **400 cold / 0 warm** resolver calls. [HTTP](cost/isolated_unique_cost_http.json), [instrumentation](cost/unique_piece_cost.json). |
| M11/M12 Unicode expansion, answer `'\ufdfa'*4000` | **NOT FIXED**, inherited cost concern: 4,000 characters expand to 72,000 under NFKC; check **2.75097 s**, queued EGFR **2.67803 s**, warm check **3.51298 s**, all 200. [HTTP](cost/isolated_unicode_cost_http.json). |
| M11/M12 punctuation normalization, `' - '.join(['x']*1000)+'xx'` (3,999 characters) | **NOT FIXED as measured overhead**, no timeout/data error: current / HEAD^ direct-link medians **0.28970 / 0.29199 s**. At 499 characters: **0.03616 / 0.03556 s**. [Same-data comparison](cost/normalization_cost.json). |
| M12 repeated matches in one item, `' '.join(['isa']*1000)` (3,999 characters) | **NOT FIXED as measured overhead**, no failure: current / HEAD^ direct-link medians **1.05179 / 1.06954 s**. At 499 characters: **0.03414 / 0.03270 s**. [Comparison](cost/normalization_cost.json). |
| Current repair, repeated isotope-bearing alias, `';'.join(['A33 124i']*444)` (3,995 characters) | Current / HEAD^ direct-link medians **0.06926 / 0.06769 s**; no error. Cached ordinary osimertinib **0.0001025 / 0.0001437 s**. All 24 version/workload samples completed; results are not a statistically established speedup/regression. [Comparison](cost/normalization_cost.json). |
| Disease / ordinary concurrent requests | Disease: **2,774 Trials + 300 Targets**, 30 per list, **18,575 bytes / 73.314 ms**. **24 requests / 12 workers**, all expected HTTP 200 shapes, **677.551 ms** total. These ordinary HTTP samples overlapped early audit work and are not isolated benchmarks. [HTTP](cost/../root_checks/http_results.json). |

`engine.lock` serializes engine operations (`src/app.py:247-263`), so expensive legal check-answer requests delay map requests. The 3,999/4,000-character stresses are direct-link or **answer-field** cases; `/api/explore` rejects text over 500 characters. Limits precede NFKC normalization (`src/app.py:239-243,260`; `src/query.py:116-117,169-177`). No deadlock or invented graph value was observed. The latest six-character word-run loop is bounded per start word (`src/query.py:261-267`); this does not establish linear cost for the surrounding linker.

The new patch showed no material failure in the tested same-data cost comparison. Distinct-piece resolver work, expansion before linking and repeated matched-name scanning remain should-fix costs; they are not used to manufacture a second approval blocker. Owned benchmark port **19403** is closed and lifecycle checks record unchanged DB bytes. No model cost was incurred.

Reproduce with `python -B audit_evidence_claims/m13/cost/run_isolated.py`; its wrappers confine temporary output here and use owned port 19403 sequentially.

## Standards and specification

**Standards: zero documented violations found.** The app/UI diff from `bfcb83d` and latest query/test patch were examined. No tracked repository AGENTS.md, CONTRIBUTING.md, CODING_STANDARDS.md or issue-tracker instructions were found. User-supplied evidence-based, m13-only, no-tracked-edit instructions govern. The KOA Studio/KhOpenApi original-versus-modified-code instruction is conditional on changing application code; no such change was made. [Independent standards record](db_ui/standards_review.json).

**Specification: one P1 blocker, M13-B1.** Exact earlier blocking reproductions are fixed, but a normalization-equivalent refused tracer alias still draws its originator without any refusal. Live/correct edges surrounding a wrongly selected centre do not meet the name-refusal guarantee. Known over-refusals and measured costs do not determine the verdict.

README descriptions for app.py are accurate (`README.md:566`, `README.ko.md:387`); nearby test-count comments still say 317, **NOT FIXED**, a nonblocking documentation-only stale count. Actual current tests are 340. [DB/UI source assessment](db_ui/FINDINGS.md).

## Integrity and reproduction

Snapshot: **7 retired nodes, 142 retired edges, zero real self-loops, zero live edges with retired endpoints**. All six live node types and 22 relation combinations were exercised. Self-loop/unknown-type behavior was tested in memory, not claimed to exist in the snapshot. [Snapshot](db_ui/db_snapshot_facts.json), [fixture](db_ui/self_loop_unknown.json).

`Engine.ask` sets `use_llm=False` (`src/app.py:180-181`). Explore follows SELECT paths; mutation fixtures use in-memory databases. The app does not globally enforce a read-only SQLite handle, so no-write evidence rests on source, executed paths and unchanged bytes rather than a database-permission guarantee.

Final verification compares **4,176 tracked-file SHA-256 hashes**, HEAD, tracked/staged diffs, database bytes, report links and owned-port cleanup. [Initial snapshot](integrity_before.json), [final verification](integrity_final.json). Database SHA-256: `7341c5a7089731f67356da5a588b269d4b69e8e6c4c054acf19aa4ef2837b529`.

Run from repository root with bytecode disabled and TMP/TEMP/TMPDIR inside each script family's m13 `tmp/` directory. Shared-port HTTP scripts run sequentially; benchmarks run after the other suites finish. The setup script records the original hashes and adapted script provenance; do not replace that original snapshot when rerunning checks.

```text
python -B audit_evidence_claims/m13/root_checks/run_all.py
python -B audit_evidence_claims/m13/root_checks/fresh_probe.py
python -B audit_evidence_claims/m13/root_checks/independent_m12_http.py
python -B audit_evidence_claims/m13/root_checks/independent_m13_http.py
python -B audit_evidence_claims/m13/names/run_round9.py
python -B audit_evidence_claims/m13/names/run_completion.py
python -B audit_evidence_claims/m13/names/joined_label_probe.py
python -B audit_evidence_claims/m13/db_ui/run_db.py
python -B audit_evidence_claims/m13/db_ui/run_ui.py
python -B audit_evidence_claims/m13/attacks/run.py
python -B audit_evidence_claims/m13/cost/run_isolated.py
```

VERDICT: CHANGES REQUIRED
