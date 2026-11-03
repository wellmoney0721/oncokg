# Independent relation-map review — round 19

Reviewed **`c476d9d559ce5e723c6f5d91fad5e6c3599cfe93`**. **CHANGES REQUIRED: two P1 originator-refusal failures.** `radio-labelled trastuzumab` and `trastuzumab labelled with 99m-technetium` pass every refusal stage and draw unlabelled TRASTUZUMAB. Both show 13 map trials; trial/sponsor QA each returns 12 originator evidence rows. Their joined-label / element-first controls refuse. Both holes reproduce in HEAD^; they are not claimed as originator regressions introduced by this commit.

Exact prior promoted M1–M18 primary name findings are FIXED, including M18-B1 `trastuzumab radiolabelled with iodine-124`. Historical supplemental gaps and accepted exceptions retain individual NOT FIXED dispositions below. The user-listed over-refusals and ChEMBL bevacizumab-code limitation do not determine the verdict. New `non-radiolabelled trastuzumab` over-refusal is separately reported as a should-fix.

No production code or tracked file was edited. New scratch files are confined to `audit_evidence_claims/m19/`.

## Method, evidence, and limits

The review tests four claims separately: prior exact failures stay repaired; equivalent tracer descriptions never select an unlabelled molecule; displayed edges/values agree with live stored rows; request cost remains bounded. Paired inputs change only the relevant spelling, direct helper traces identify the missed guard, and independently owned original CLI servers establish the public response. A passing test suite alone is not treated as proof of the refusal guarantee.

- **346 passed in 36.74 s**, exit 0, using `python -m pytest tests -q -p no:cacheprovider`. Bytecode disabled and temp paths under m19. [Output](root_checks/pytest.txt), [command/environment](root_checks/pytest_summary.json).
- Cumulative historical scripts re-executed on current HEAD: m1, partial m2/completed m2b, m3–m18. Main/remaining/late root batches exit zero. [Reuse manifest](reuse_manifest_root.json), [main execution](root_checks/execution_all.json), [remaining](root_checks/execution_remaining.json), [late](root_checks/execution_m18_late.json), [M18 independent HTTP](root_checks/independent_m18_http.json). The name and DB/UI matrices below give exact per-finding dispositions and fresh artifacts rather than inferring repair from process exit codes.
- Historical naming: **83 rows, 63 FIXED / 20 NOT FIXED**; **66 scripts reused / 55 reused leaf scripts executed**, plus 15 frozen M18 supplement inputs whose original standalone generator was absent. The **7,511-key** sweep has zero new losses/recoveries versus m18. The frozen **1,648-question** comparison has 68 identical / 1,556 metadata-only / 24 semantic differences / zero errors. These frozen-comparison differences are diagnostics, not defect counts. [Coverage/assertions](names/worker_final_checks.json), [reuse/literal manifest](names/reuse_manifest.json), [QA comparison](names/adapted_frozen_qa_relink_sweep.json). DB/UI contributes 30 overlapping rows (23 FIXED / 7 NOT FIXED); matrix row counts are not unique defect counts.
- **6,469 live centres / 22 relation-direction-type-role combinations / zero oracle errors**; **19/19 DB**, **24/24 UI**, **4/4 self-loop/unknown/retirement** assertions pass. [Stored-row oracle](db_ui/db_validate.json), [DB assertions](db_ui/db_assertions.json), [UI assertions](db_ui/ui_assertions.json), [fixture](db_ui/self_loop_unknown.json).
- **36/36 original CLI HTTP demos** return 200 and equal direct Engine responses. All 36 page demos render in the JavaScript harness. [HTTP demos](db_ui/demo_http.json), [demo comparisons](db_ui/demo_previous_comparison.json), [page callback checks](db_ui/ui_m3_checks.json).
- Attack reviewer: **82 current/HEAD^ stage pairs / 328 actual HTTP requests**, all 200. Root separately confirmed **22 inputs / 88 requests**, including the two holes, paired refusals, list reversal, ordinary controls and older unresolved qualifiers. Counts overlap and are not summed as unique examples. [Stages](attacks/new_results.json), [HTTP](attacks/new_http.json), [root HTTP](root_checks/independent_m19_http.json), [root assertions](root_checks/independent_m19_summary.json).
- All 22 root map responses were exercised through the actual page form callback. The two leaks render a TRASTUZUMAB SVG centre and CHEMBL1201585 trail; their controls render refusal with no SVG and an empty trail. [Page evidence](db_ui/ui_m19_http.json), [harness](db_ui/ui_m19_http.js).

UI checks execute actual page JavaScript in a Node VM with controlled DOM/fetch stubs. They establish generated markup, state and callbacks, not browser painting or browser-executed XSS. HTTP uses unmodified `src/app.py` on owned ports other than 8765, or its real handler with in-memory fixtures. Historical counterfactuals substitute only `query.py` against current remaining modules/data; they are not complete historical deployments. No model was called. Performance samples are host measurements, not service guarantees.

## M19-B1 — P1: hyphenated radio-labelling words still draw the originator

Exact input: **`radio-labelled trastuzumab`**. `POST /api/explore` returns HTTP 200 with **TRASTUZUMAB / CHEMBL1201585**, **13 trials**, and no refusal. `Which trials evaluate radio-labelled trastuzumab?` and `Who sponsors trials of radio-labelled trastuzumab?` each return **12 originator evidence rows**. Removing only the hyphen, producing `radiolabelled trastuzumab`, returns a refusal and zero QA evidence.

This is an ordinary spelling of a tracer description, not a contrived isotope spelling: a primary experimental article develops and evaluates isotope-labelled trastuzumab and uses the exact phrase “radio-labelled trastuzumab” in its Discussion. [Lub-de Hooge et al., Preclinical characterisation of 111In-DTPA-trastuzumab](https://pmc.ncbi.nlm.nih.gov/articles/PMC1575276/). The article supports the terminology and tracer/originator distinction; it does not supply graph evidence or a clinical recommendation.

| Stage | `radio-labelled trastuzumab` | `radiolabelled trastuzumab` |
|---|---|---|
| Intervention resolver | CONTAINED_ALIAS + UNRESOLVED, no BLOCKED | CONTAINED_ALIAS + UNRESOLVED, no BLOCKED |
| `_resolver_blocked` | `{}` | `{}` |
| `_qualified` | false | false |
| `_item_has_isotope` | false | true |
| Actual `_marked` call | `None`; both tokens in segment 0 | refusal |
| `_whole_name` | `None` | `None` |
| Public linker | Drug TRASTUZUMAB, no Refused | Refused only |
| HTTP map | CHEMBL1201585, 13 trials | refused, no centre |
| Trial / sponsor QA | 12 / 12 | 0 / 0 |

**Cause:** `src/query.py:177-179` splits the phrase into alphanumeric words and tests each word independently for membership in `_LABEL_WORDS` or a `radiolabel`/`radioiod` prefix. The hyphenated word becomes `radio`, `labelled`; neither passes. The earlier patterns in `src/textrules.py:306-318` recognise isotope-symbol syntax, not this word. The resolver records no BLOCKED component (`src/query.py:303-343`), `_qualified` misses it (`src/query.py:232-256`), and the item-wide check in `_marked` is false (`src/query.py:423-425`). `Engine.explore` selects the surviving positive hit (`src/app.py:88-95`). The new test only checks joined `radiolabelled` (`tests/test_app.py:428-440`).

**Corroborating exact inputs:** `radio-labeled trastuzumab`, `radio labelled trastuzumab`, `radio‑labelled trastuzumab` (U+2011), `radio_labelled trastuzumab`, `RADIO-LABELLED TRASTUZUMAB`, `trastuzumab (radio-labelled)`, `trastuzumab radio-iodinated`, `trastuzumab radio-tracer`. These all draw the originator, while their joined control spellings refuse. `radio-labelled Herceptin`, `radio-labelled vinblastine`, and `radio-labelled erlotinib` show the same guard failure across aliases/drugs. They are common-cause software probes; no claim is made that every synthetic descriptor denotes a marketed product.

The same new lexical check is incomplete for ordinary morphology: `trastuzumab radioactively labelled`, `radioconjugated trastuzumab`, `trastuzumab radioimmunoconjugates`, and `trastuzumab radiopharmaceuticals` survive, while `trastuzumab radioactive label` and `trastuzumab radiopharmaceutical` refuse. These are corroborations of incomplete labelling-word recognition, not separate counted blockers.

## M19-B2 — P1: mass-first metastable full element name bypasses the reverse-order rule

Exact input: **`trastuzumab labelled with 99m-technetium`**. The HTTP map again selects CHEMBL1201585 with 13 trials and no refusal; trial and sponsor QA each return 12 originator evidence rows. Change only the isotope spelling to `technetium-99m` or `99mTc`: the map refuses and both QA evidence arrays are empty. `99m-technetium trastuzumab`, `99m technetium trastuzumab`, and the fused `technetium99m trastuzumab` also survive. The direct paired case is the explicit labelled product, not a drug merely mentioned alongside a separate isotope.

Tc-99m-labelled trastuzumab is an actual radiopharmaceutical research product: the original RP-39 abstract reports its preparation via DTPA for imaging. [Bhusari et al., Radiopharmacy RP-39](https://pmc.ncbi.nlm.nih.gov/articles/PMC3868035/). The equivalence of the tested isotope notations is the reviewer's inference from that identity and the application's own accepted/refused controls.

**Cause:** the general two-order element-name loop requires `num.isdigit()` (`src/query.py:181-185`), so `99m` is rejected as a mass. Its special exception checks only `a == "technetium" and b in ("99m", "99")` (`src/query.py:186-187`); the reversed order is never tested. The symbol guards do not convert the full element name. `_qualified == false`, `_resolver_blocked == {}`, `_item_has_isotope == false`, actual `_marked == None`, `_whole_name == None`, and the public linker has a positive Drug and no Refused. Thus this is a second concrete failure mechanism within the new helper.

**Required behaviour for both blockers:** recognise equivalent explicit labelling descriptions consistently with their refused controls; no unlabelled TRASTUZUMAB map or originator QA evidence may survive. No application repair was made.

## Should-fix and additional observations

- **M19-S1, new over-refusal:** `non-radiolabelled trastuzumab` now refuses, whereas HEAD^ and current `unlabelled trastuzumab` draw TRASTUZUMAB. Splitting the `non-` prefix leaves a matching label word, without negation handling. This is a new recall regression, not an originator-leak blocker, and is distinct from the user's previously accepted over-refusals.
- Full element names fused to mass remain unrecognised in several ordinary compact renderings: `iodine124 trastuzumab`, `trastuzumab iodine124`, `zirconium89 trastuzumab`, `89zirconium trastuzumab`. Their hyphenated controls refuse. Recorded as supplements; B1/B2 suffice for rejection.
- `tritiated FDG` and `FDG labelled with carbon-14` select the already-labelled F18 preferred product despite `_item_has_isotope == true`. This extends the previous isotope-compatibility concern in m18; no independent product-identity proof is supplied here, so it is not promoted to another blocker.
- Ordinary controls `trastuzumab`, `osimertinib 80 mg`, `paclitaxel 2 cycles`, and `lead compound osimertinib` remain available. The intended labelled-product control `fluorine-18 fluorodeoxyglucose` still selects FLUDEOXYGLUCOSE F 18. Broader demo and cost checks belong to the other reviewers.


## Earlier name reproductions — FIXED / NOT FIXED

Each status applies to the exact cited reproduction, not every imaginable spelling. M2 has no completed report; its partial fixtures are covered with m2b. The table includes earlier unpromoted supplements. Inherited unresolved leaks such as `b.i.o.similar bevacizumab` and `lip.osomal doxorubicin` are not in the user's accepted-exception list and are not excused as repaired; the root independently reproduced both over HTTP this round. They add to the reasons approval is unavailable, while B1/B2 provide new independent failures.

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
| M12/M15 supplementary Fragmented qualifier b.i.o.similar bevacizumab | **NOT FIXED** | The exact old supplementary input still draws BEVACIZUMAB / CHEMBL1201583 (122 live trials) and supplies 12 trial / 12 sponsor QA rows, without a refusal. Inherited originator leak; this is not among the user-accepted exceptions. [Evidence](names/m12_attacks/focused_results.json). |
| M12/M15 supplementary Fragmented qualifier lip.osomal doxorubicin | **NOT FIXED** | The exact old supplementary input still draws DOXORUBICIN / CHEMBL53463 (3 live trials) and supplies 3 trial / 3 sponsor QA rows, without a refusal. Inherited originator leak; this is not among the user-accepted exceptions. [Evidence](names/m12_attacks/focused_results.json). |
| M14/M15 supplementary Slash PET/CT presentation: 89zr-panitumumab-pet/ct | **NOT FIXED** | The exact slash-bearing input returns not_found with no centre, no refusal message and zero trial/sponsor evidence. This remains a should-fix distinction in failure presentation, not an originator leak; the glued/hyphen PETCT blocker inputs explicitly refuse. [Evidence](names/m14_exact/edge_results.json). |
| M15 M15-B1 punctuation inside adjacent isotope/chelator | **FIXED** | 89-ZrDFO trastuzumab, trastuzumab DFO89-Zr, 89Z.rDFO trastuzumab, and trastuzumab DFO89Z.r refuse with zero originator map/trial/sponsor results. Separate comma osimertinib survives. [Evidence](names/m15_exact/targeted_results.json). |
| M15 M15-B2 lower-case stored tracer; A33 corroboration | **FIXED** | 3hvinblastine, A33124i, and a33124i refuse; bare VINBLASTINE and ADAKITUG remain available. Comma-separated osimertinib survives the refused lower-case vinblastine tracer. [Evidence](names/m15_exact/targeted_results.json). |
| M15 repair note / user GS-11CAL-101 known over-refusal | **NOT FIXED** | The raw stored-alias sweep continues to refuse this alias. Explicitly user-accepted, nonblocking; no new raw-alias loss versus M18. [Evidence](names/names_m5_summary.json). |
| M15 repair note / user 3en3hg4wsw known over-refusal | **NOT FIXED** | The raw stored-alias sweep continues to refuse this alias. Explicitly user-accepted, nonblocking; no new raw-alias loss versus M18. [Evidence](names/names_m5_summary.json). |
| M16 M16-B1 element-first one-letter isotope within one word | **FIXED** | I-124-labelled trastuzumab, trastuzumab labelled with I-124, I124/i-124/[I-124] variants and H3/H-3 vinblastine corroborations now refuse with no centre and zero trial/sponsor evidence. Bare controls survive; separate comma-osimertinib remains selected with refusal disclosed. All 42 original stage cases replayed. [Evidence](names/m16_exact/new_results.json). |
| M17 M17-B1 punctuation-delimited element-first one-letter isotope | **FIXED** | Original trastuzumab labelled-I-124 and 21 punctuation/case/H3/F18/C14/Y90 corroborations now refuse without a centre and with zero trial/sponsor evidence. Separate-list osimertinib survives with refusal disclosed. All 63 original staged cases and 252 original HTTP requests replayed; dose/BKM120/AZD9291/bare controls survive. [Evidence](names/m17_exact/new_results.json). |
| M18 M18-B1 written-out element name and labelling-word originator leak | **FIXED** | trastuzumab radiolabelled with iodine-124 and 16 original element-name/tritium corroborations now refuse with no centre and zero trial/sponsor evidence. Cetuximab beside yttrium-90 is refused while the separately recognized YTTRIUM Y-90 node survives with zero QA evidence. Separate-list osimertinib, ordinary drug/code/dose controls survive. All 64 original stage cases and 256 original CLI HTTP requests replayed. [Evidence](names/m18_exact/new_results.json). |
| M18 supplementary trastuzumab labelled-I-1-24 | **NOT FIXED** | Exact previously recorded diagnostic still selects TRASTUZUMAB / CHEMBL1201585, 13 map trials, 12/12 trial/sponsor evidence, no public refusal. Split-digit spellings are artificial; whitespace form reflects current symbol-boundary scope. Not a user-accepted exception. [Evidence](names/m18_exact/new_results.json). |
| M18 supplementary trastuzumab labelled-C-1-4 | **NOT FIXED** | Exact previously recorded diagnostic still selects TRASTUZUMAB / CHEMBL1201585, 13 map trials, 12/12 trial/sponsor evidence, no public refusal. Split-digit spellings are artificial; whitespace form reflects current symbol-boundary scope. Not a user-accepted exception. [Evidence](names/m18_exact/new_results.json). |
| M18 supplementary trastuzumab labelled-I 124 | **NOT FIXED** | Exact previously recorded diagnostic still selects TRASTUZUMAB / CHEMBL1201585, 13 map trials, 12/12 trial/sponsor evidence, no public refusal. Split-digit spellings are artificial; whitespace form reflects current symbol-boundary scope. Not a user-accepted exception. [Evidence](names/m18_exact/new_results.json). |
| M18 supplementary labelled-product isotope compatibility: FDG labelled-C-14 versus FDG 14C | **NOT FIXED** | First form still selects FLUDEOXYGLUCOSE F 18 / CHEMBL2030434 without refusal, while FDG 14C refuses. This is the earlier synthetic isotope-compatibility concern, not evidence that an unlabelled originator was selected; its product identity has not been independently established. [Evidence](names/m18_exact/labelled_exception_replay.json). |


### Accepted exceptions

The following remain explicitly outside blockers as the user requested: M5-S2; 40-o-/42-o-(2-hydroxyethyl)rapamycin; Trastuzumab--vcmmae conjugate; 9-amino-20(s)-camptothecin; il-6ra; TAK-659F; GS-11CAL-101; 3en3hg4wsw; same-list-item over-refusal. ChEMBL's bevacizumab biosimilar-code synonyms are the separately accepted data limitation. Other unresolved historical entries are not silently added to this exception list. [Name replay narrative and coverage](names/FINDINGS.md).

## Database, UI and server reproductions

This table covers non-name/non-cost findings through m18, plus independent isotope corroborations. M2 has no completed report; its partial role/order cases are included. Each current disposition uses fresh evidence, not the historical script's exit code alone. Names and performance have separate worker matrices. [Historical report inventory](db_ui/historical_report_headings.json), [machine-readable matrix](db_ui/historical_findings_matrix.json).

| Earlier finding / exact reproduction | Round 19 result and evidence |
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
| M16 labelled-product qualification: `89ZrDFO 18-FDG` / `89-ZrDFO 18-FDG`, lutathera/FDG isotope variants | **NOT FIXED**, unchanged isotope-compatibility diagnostic around the preferred-name exception; not added to the user-accepted exceptions. All 17 original m16 adjudication inputs rerun. [stages](db_ui/adjudication_tracer.json). |
| M1-M18 README test-count comments, README.md:565 / README.ko.md:386 | **NOT FIXED**, inherited documentation-only: both say 317 tests. Nearby app descriptions remain accurate. [Standards](db_ui/STANDARDS.md). |
| M17-B1 punctuation-before-symbol: `trastuzumab labelled-I-124`; `iodine-I-124-labelled trastuzumab`; `trastuzumab labelled with iodine-I-124` | **FIXED**. Every original selected tracer input refuses, with zero trial/sponsor QA evidence; HEAD^ and current both refuse. Adjacent symbol pieces preserve the boundary. `src/query.py:188-197`. [Fresh m17 staged replay](db_ui/adjudication_tracer.json), [exact main input](db_ui/independent_boundary.json). |
| M18-B1 independent exact input: `trastuzumab labelled with iodine-124`; `trastuzumab labelled iodine 124` | **FIXED**. Current linker refuses and map has no centre; trial and sponsor QA have zero evidence. HEAD^ draws TRASTUZUMAB with 12/12 QA rows. `src/query.py:156-187`. [Independent stages](db_ui/independent_boundary.json). |
| M18 synthetic mass-split diagnostics: `trastuzumab labelled-I-1-24`, `trastuzumab labelled-I-12-4`, `trastuzumab labelled-I-(1)(24)` | **NOT FIXED**, unchanged diagnostic qualification, not promoted as natural scientific notation. All three continue to map TRASTUZUMAB with 12/12 QA rows. [Stages](db_ui/independent_boundary.json). |
| M16-M18 cross-word one-letter qualification: `trastuzumab labelled I 124` | **NOT FIXED**, unchanged cross-word diagnostic; not a user-accepted exception. The within-word requirement remains separate. [Stages](db_ui/independent_boundary.json). |


All six live node types and all 22 existing relation combinations are covered. The snapshot has **7 retired nodes, 142 retired edges, zero self-loops and zero live edges with retired endpoints**. PARENT_OF, STUDIES, ASSOCIATED_WITH, EVALUATES, ACTS_ON and role-aware SPONSORS agree with stored endpoints. All **3,000 stored URLs** use registry HTTPS URLs, and all node/edge props are valid JSON objects. [Snapshot](db_ui/db_snapshot_facts.json), [oracle](db_ui/db_validate.json). Self-loop behavior is an isolated fixture result.

## New HTTP-to-UI corroboration

The root's independent CLI captures were passed unchanged to the **actual page form submission callback**, then rendered by `exploreSafe`/`explore`. Both `radio-labelled trastuzumab` and `99m-technetium trastuzumab` render a **TRASTUZUMAB / CHEMBL1201585 centre**, an SVG relationship map and a trail entry, without a refusal. The paired `radiolabelled trastuzumab` and `technetium-99m trastuzumab` responses render refusal text, no SVG, and an empty trail. All **22 captured /explore responses** render without errors. This ties the root's name-resolution defects to the displayed map. [Actual generated markup and state](db_ui/ui_m19_http.json), [harness](db_ui/ui_m19_http.js), [root HTTP evidence](root_checks/independent_m19_http.json). It is a VM rendering check, not a real-browser claim.

## Cost and performance reproductions

All nine inherited cost scripts exited zero, sequentially after other audit CPU/HTTP workloads finished. The additional M16 repeated-match instrumentation and HTTP reproducer also exited zero. Unrelated host load is uncontrolled; these are measurements, not service guarantees. Counterfactuals substitute only historical `query.py` against the same current app/data. [Execution](cost/execution_isolated.json), [provenance](reuse_manifest_root.json), [M16 follow-up execution](cost/repeated_match_execution.json).

| Historical finding / exact workload | Current disposition and measured evidence |
|---|---|
| M5-S3 cubic qualifier scan, `' '.join(['x']*250)` (499 chars) | **FIXED for the original workload.** 2,224 calls to each predicate / 33,880 aggregate predicate-input characters, 0.03698 s direct. [Instrumentation](cost/perf_current.json). |
| Original 999-character plain-answer timeout, `' '.join(['x']*500)` | **FIXED.** HTTP check 200 in 0.27344 s; later map 0.02450 s. [HTTP](cost/perf_check_http.json). |
| M6/M7 repeated 2,000-piece resolver cost, `';'.join(['x']*2000)` | **FIXED for this repeated-piece control.** Current / historical `9bd7cb4` direct medians 0.16880 / 1.99613 s. HTTP check 0.44623 s, queued EGFR 0.36539 s, both 200. [Comparison](cost/fresh_cost_comparison.json), [HTTP](cost/fresh_cost_http.json), [stress](cost/cost_stress.json). |
| M8-S1 4,097th resolver-cache entry | **FIXED.** 82/82 fill requests succeed; rollover and retry return OSIMERTINIB / CHEMBL3353410 with 79 trials, no KeyError. [HTTP](cost/cache_boundary_http.json). |
| M10-M18 distinct-piece lock delay, `';'.join(f'isa x{i:04d}' for i in range(400))` | **NOT FIXED**, inherited cost concern. Cold check 2.36693 s, queued EGFR 2.29214 s, warm 0.31255 s; all 200. [HTTP](cost/isolated_unique_cost_http.json), [instrumentation](cost/unique_piece_cost.json). |
| M11-M18 Unicode expansion, answer `'\ufdfa'*4000` | **NOT FIXED**, inherited cost concern. 4,000 chars expand to 72,000 under NFKC. Cold check 2.71567 s, queued EGFR 2.63328 s, warm 3.09558 s; all 200. [HTTP](cost/isolated_unicode_cost_http.json). |
| M11-M18 punctuation normalization, `' - '.join(['x']*1000)+'xx'` | **NOT FIXED as measured overhead**, no error. Current / HEAD^ medians 0.29839 / 0.30239 s; at 499 chars 0.03717 / 0.03557 s. [Comparison](cost/normalization_cost.json). |
| M12-M18 repeated matches, `' '.join(['isa']*1000)` | **NOT FIXED as residual repeated-match overhead**; **M16-S1 added isotope rescans FIXED**, detailed below. Current / HEAD^ direct medians 1.06753 / 1.04965 s; at 499 chars 0.03591 / 0.03462 s. [Comparison](cost/normalization_cost.json). |
| M13-M18 repeated isotope alias, `';'.join(['A33 124i']*444)` | No error reproduced. Current / HEAD^ medians 0.07935 / 0.07083 s. Cached ordinary OSIMERTINIB 0.00014 / 0.00015 s. All 24 workload/version rows complete. [Comparison](cost/normalization_cost.json). |
| Disease / ordinary concurrent maps | No failure reproduced: 2,774 Trials + 300 Targets, 30 per list, **18,575 bytes / 113.019 ms**. 24 requests / 12 workers all expected HTTP200 shapes in **850.956 ms**. These ordinary early samples overlapped other audit work. [HTTP](root_checks/http_results.json). |

### M16-S1: the item's isotope state is now computed once

**FIXED for the exact reported extra work.** At 125 / 1,000 occurrences, instrumentation records **one whole-item scan** and **250 / 2,000 within-word helper calls**, respectively. M16 originally recorded 125 / 1,000 whole-item scans and 15,625 / 1,000,000 within-word calls. M17 recorded one scan with 125 / 1,000 within-word calls. The preceding M18 repair checks both the canonical word and its punctuation piece, which are identical for `isa`; this doubles those within-word calls but does not restore per-match whole-item rescanning. `@functools.lru_cache(maxsize=4096)` caches the pure tuple-keyed computation (`src/query.py:168-198`), called from `_marked` at `src/query.py:423-425`. The same single ISATUXIMAB entity survives. [Fresh instrumentation](cost/repeated_match_instrumentation.json), [reused script](cost/repeated_match_followup.py).

For the legal 3,999-character **answer** field, the fresh HTTP check takes **2.44896 s**, queues EGFR for **2.36627 s**, and takes **2.95730 s** warm. The ordinary map after completion takes 0.04612 s; all return 200. This verifies the repair without claiming all repeated-match work was removed. `_marked` still constructs/scans token lists before checking the cache and runs before entity deduplication (`src/query.py:368-396,581-591`). [HTTP](cost/isolated_repeated_match_cost_http.json), [closed owned server / unchanged DB](cost/repeated_match_cost_lifecycle.json).

`engine.lock` serializes API operations (`src/app.py:247-263`). These 3,999/4,000-character workloads use direct linking or the **answer field**; explore correctly rejects more than 500 characters. Limits precede NFKC (`src/app.py:239-243,260`; `src/query.py:117-118,282-284`). Residual costs are should-fix observations, not the reason for the verdict. **No model calls or model cost were incurred.**

## Standards

**0 documented-standard violations found.** The fixed point is `4bed79c1f170ebe1efa3d452ce4398cce17b2113`; current HEAD is `c476d9d559ce5e723c6f5d91fad5e6c3599cfe93`. The nonempty reviewed diff is `git diff 4bed79c1f170ebe1efa3d452ce4398cce17b2113...HEAD -- src tests web README.md README.ko.md CODEX_MAP_M1_VERDICT.md`. It changes the isotope helper, its regression test, and repair notes. [Latest diff](db_ui/review_diff_latest.txt). The cumulative application/UI diff from original `bfcb83d` was also inspected. [App/UI diff](db_ui/review_diff_app_ui.txt).

`git ls-files '*AGENTS.md' '*CONTRIBUTING.md' '*CODING_STANDARDS.md' 'docs/agents/*'` returns no tracked standards sources. [Inventory](db_ui/review_diff_standards.txt). The user's supplied instructions govern: evidence-based independent review; no tracked edits; scratch only under m19; fresh FIXED / NOT FIXED dispositions for historical reproductions. The reused harnesses retain original inputs and fixture logic, redirecting only scratch paths and the owned CLI port. [Manifest](db_ui/reuse_manifest.json).

SQLite mutation fixtures are isolated in memory. The all-node oracle connects with `mode=ro`. Actual page JavaScript runs in a Node VM with controlled DOM/fetch stubs: findings concern generated markup and exercised state, not browser painting or browser-executed XSS. CLI HTTP demos use port 9221 and clean up their process. The application connection is not globally read-only; write claims rely on executed paths and integrity checks. `Engine.ask` explicitly sets `use_llm=False` at `src/app.py:181`.

Issue-tracker setup was not performed because the explicit audit-only/no-tracked-edit scope takes precedence over skill setup guidance. No application code was changed, so the conditional KOA Studio/KhOpenApi original-versus-modified code comparison does not arise.

Inherited README test-count comments still say 317 (`README.md:565`, `README.ko.md:386`); adjacent application descriptions remain accurate. This is a documentation should-fix, not a new documented coding-standard violation. New refusal gaps, if reproduced, belong to the independent specification axis.

## Specification


Specification source: the user's Round 19 brief and original guarantee 3 / approval bar: “a refused product drawn as the originator” is a blocker. Diff reviewed: `git diff 4bed79c1f170ebe1efa3d452ce4398cce17b2113...HEAD -- src tests`.

**Two P1 failures.** (1) `radio-labelled trastuzumab` is a published ordinary tracer description, but every guard misses the separated label word (`src/query.py:177-179`); actual HTTP draws CHEMBL1201585 with 13 trials, and trial/sponsor questions each return 12 originator evidence rows. The joined `radiolabelled` spelling refuses. (2) `trastuzumab labelled with 99m-technetium` produces the same wrong map and evidence; reversing the isotope to `technetium-99m` refuses. The full-element loop rejects `99m` as nonnumeric and handles the special metastable form in only one order (`src/query.py:181-187`).

The exact repair examples are fixed. Both new holes reproduce on HEAD^ with current data/app modules; neither is claimed as a newly introduced originator regression. New `non-radiolabelled trastuzumab` refusal is a separate should-fix recall regression. No scope-creep finding is identified. Known over-refusals and bevacizumab biosimilar-code curation do not determine these findings.

Specification: **2 P1 findings; CHANGES REQUIRED.**


## Integrity and reproducibility

The original brief/log already existed in m19 and were preserved. Reproducer copies retain historical inputs and fixture logic, with output paths/ports recorded in manifests. Production DB mutation fixtures are isolated in memory. The application connection is not globally read-only, so the no-write conclusion relies on the inspected executed paths and final byte comparison; `Engine.ask` passes `use_llm=False` at `src/app.py:181`.

Final verification compares **7,260 tracked-file SHA-256 hashes**, unchanged HEAD, tracked/staged diffs, database bytes, local report links and closure of the run's owned server ports. [Before](integrity_before.json), [final verification](integrity_final.json). Database SHA-256: `7341c5a7089731f67356da5a588b269d4b69e8e6c4c054acf19aa4ef2837b529`. No application repair was made; the conditional KOA Studio/KhOpenApi original-versus-replacement comparison therefore does not arise.

Representative commands from repository root; historical HTTP batches are sequential and cost batches run after other audit CPU workloads:

```text
python -B audit_evidence_claims/m19/root_checks/run_all.py
python -B audit_evidence_claims/m19/root_checks/run_m18_late.py
python -B audit_evidence_claims/m19/root_checks/independent_m18_http.py
python -B audit_evidence_claims/m19/root_checks/independent_m19_http.py
python -B audit_evidence_claims/m19/names/run_round9.py
python -B audit_evidence_claims/m19/names/run_remaining.py
python -B audit_evidence_claims/m19/attacks/new_probe.py
python -B audit_evidence_claims/m19/attacks/new_http.py
python -B audit_evidence_claims/m19/cost/run_isolated.py
python -B audit_evidence_claims/m19/cost/repeated_match_followup.py
python -B audit_evidence_claims/m19/build_cost_section.py
python -B audit_evidence_claims/m19/build_report.py
python -B audit_evidence_claims/m19/finalize_integrity.py
```

Standards: **0 documented violations**. Specification: **2 new P1 findings**, both inherited holes; unresolved historical leaks remain explicitly NOT FIXED. Ordinary demo/DB checks pass, but the refusal guarantee fails.

VERDICT: CHANGES REQUIRED
