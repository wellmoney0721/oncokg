# Independent relation-map review — round 11

Reviewed **`2b9fc923f7b6f388f5babd2f998ed4c6e16d3439`** on 2026-11-03 KST. **Changes required:** all exact previously reported originator-blocking reproductions, including M10-B1–B4, are fixed, but two additional normalization holes still draw an originator for a qualified product/tracer. Both occur in the immediate predecessor query module too; they are inherited holes, not regressions attributed to this commit.

No tracked file was edited. New scripts, fixtures, logs and this report are confined to `audit_evidence_claims/m11/`. The specified M5-S2, hydroxyethyl rapamycin and `Trastuzumab--vcmmae conjugate` over-refusals are not blockers.

## Verification and limits

- **338 passed in 30.18 s**, exit 0, with `python -m pytest tests -q -p no:cacheprovider`. Bytecode is disabled and temporary paths are under m11. [Test output](root_checks/pytest.txt), [command/environment/hashes](root_checks/pytest_summary.json).
- Reused the six historical root HTTP runners, four M6 runners, M8/M9 confirmations, and both M10 confirmations. All exit 0; port-sharing runners ran sequentially. M10's exact confirmation scripts issued **57 + 38 actual HTTP requests**. [Source manifest](root_checks/reuse_manifest.json), [six runners](root_checks/execution_http.json), [remaining runners](root_checks/execution_remaining.json), [M6](root_checks/execution_m6_http.json), [M8/M9](root_checks/execution_extra.json).
- Naming replays cover the original M1 scripts, 7,511-key alias sweep, frozen 1,648-question counterfactual and cumulative M2b–M10 matrices. Per-finding dispositions and execution manifests are linked below. The frozen counterfactual now yields **68 identical / 1,556 metadata-only / 24 semantic differences / zero errors**. This diagnostic compares the current linker with a controlled no-relink counterfactual, not application versions. [Naming report](names/FINDINGS.md), [manifest](names/reuse_manifest.json), [counterfactual](names/adapted_frozen_qa_relink_sweep.json).
- Independent graph oracle: **6,469 live centres, 22 relation/direction/type/role combinations, zero errors**. **19/19 DB and 24/24 UI assertions** pass. An additional in-memory real-handler self-loop/unknown-type/retirement fixture passes **4/4** checks. [DB/UI report](db_ui/FINDINGS.md), [oracle](db_ui/db_validate.json), [DB](db_ui/db_assertions.json), [UI](db_ui/ui_assertions.json), [new fixture](db_ui/self_loop_unknown.json).
- All **36 page demos plus six map callbacks** pass. All 36 complete demo responses equal m7, m8, m9 and m10; all 36 original-CLI HTTP requests return 200 and equal Engine responses. The seven original QA evidence counts remain **12, 12, 11, 1, 12, 0, 0**. [Comparison](db_ui/demo_previous_comparison.json), [HTTP](db_ui/demo_http.json).
- Root independently confirmed the new failures through **60 HTTP responses** from the unmodified `src/app.py` CLI, including refusal controls and trial/sponsor questions. All returned 200; the served page matched `web/try.html`; the owned server closed. [Responses](root_checks/new_leaks_http.json), [lifecycle](root_checks/new_leaks_lifecycle.json), [independent stage probe](root_checks/fresh_probe.json).

UI tests execute actual page JavaScript in a Node VM with controlled DOM/fetch stubs. They establish generated markup and callback/state behavior, not browser paint or browser-executed XSS. HTTP tests exercise the actual server. No audit server used port 8765. Findings use the repository's own canonical keys, stored aliases and refused controls, without external pharmacology assumptions.

## Blocking findings

### M11-B1 — P1: a separator inside the isotope's element symbol defeats every guard

Exact request: `POST /api/explore` with `{"text":"[89Z.r] trastuzumab"}`.

**Actual:** HTTP 200, centre **TRASTUZUMAB / CHEMBL1201585**, **13 trials**, matched stored alias **`89zr-trastuzumab`**, no Refused entity or refusal notice. Trial and sponsor QA each return **12 originator evidence rows**. `89Z_r trastuzumab` and `trastuzumab [89Z.r]` also draw the same originator. Adding `, osimertinib` still selects the forbidden trastuzumab centre. [Independent HTTP](root_checks/new_leaks_http.json), [stages and exact predecessor comparison](attacks/key_equivalence_results.json).

| Stage | Result for `[89Z.r] trastuzumab` |
|---|---|
| Raw resolver | EXACT → CHEMBL1201585, `extract_parenthetical`; no blocked component |
| Resolver veto | `{}` |
| Item linker / public linker | Drug TRASTUZUMAB; no Refused |
| Whole-name shortcut | `None`; it does not override a refusal |
| Map | Originator and its stored live relationships |

**Evidence for equivalence:** `canonical_key('[89Z.r] trastuzumab')` equals the stored `89zr-trastuzumab` key. The positive matcher consumes that alias. The controls `[89Zr] trastuzumab`, `[89.Zr] trastuzumab` and `89 Zr trastuzumab` refuse. This is the same dictionary-recognized tracer alias with punctuation inside the element symbol, not an invented drug identity.

**Cause:** `_alnum_words` makes `['89Z', 'r']` (`src/query.py:111-113`). `_marked` passes their space-joined forms to `is_isotope_label` (`src/query.py:249-265`), whose regex permits separation between the mass and element, but not inside `Zr` (`src/textrules.py:289-298`). Neither `89Z` nor `89Z r` passes; `Z` alone is not in the element set. `_qualified`'s normalization variants also miss (`src/query.py:125-141`), while positive lookup erases the separator and matches `89zrtrastuzumab` (`src/query.py:383-405`). The final map trusts the surviving positive hit (`src/app.py:87-95`).

**Required outcome:** the refusal decision must retain isotope identity across punctuation accepted by positive alias lookup, both inside a consumed alias and beside a bare drug. Preserve the existing lone-name controls. Immediate-predecessor query code also leaks this input against the same current app/rules/database; this is a query-module counterfactual, not a reconstructed old deployment. [Independent adjudication](db_ui/attack_adjudication.md).

### M11-B2 — P1: a punctuation-only token pushes a known biosimilar suffix beyond the positive window

Exact request: `POST /api/explore` with `{"text":"bevacizumab a - w w b"}`.

**Actual:** HTTP 200, centre **BEVACIZUMAB / CHEMBL1201583**, **122 trials**, no refusal. Trial and sponsor QA each return **12 originator evidence rows**. `bevacizumab - a - w - w - b` and underscore-separated variants also leak. Appending `, osimertinib` still draws bevacizumab. [Independent HTTP](root_checks/new_leaks_http.json), [current/predecessor stages](attacks/key_equivalence_results.json).

| Stage | Result for `bevacizumab a - w w b` |
|---|---|
| Raw resolver | ALIAS → CHEMBL1201583; no blocked component |
| Resolver veto | `{}` |
| Item linker / public linker | Bare BEVACIZUMAB; no Refused |
| Whole-name shortcut | `None` |
| Map | Originator with its stored live relationships |

**Evidence for equivalence:** the entire input has the same canonical key and stored alias hits as `bevacizumab-awwb`. The controls `bevacizumab-awwb`, `bevacizumab a.w.w.b` and **`bevacizumab a w w b`** refuse. Adding one standalone hyphen to the last refused input makes it pass.

**Cause:** the extra hyphen makes six raw tokens. Both drug-span detection and positive windows are limited to five (`src/query.py:378-397,446-463`), so the full suffix-bearing name is no longer matched and `_marked` receives only bare `bevacizumab`. Its same-name suffix check sees no suffix, and its next-word check sees only `a` (`src/query.py:241-265`). `_qualified` does see the whole item, including normalized `bevacizumab a w w b`, but no guard reassembles the suffix letters into the canonical `awwb` used by positive lookup (`src/query.py:125-141`). This is not a claim that the eight-word scan misses the six-token input: it scans it and still returns false.

**Required outcome:** punctuation-only tokens must not turn a recognized, refused suffix-bearing product into an accepted bare parent. Check normalized qualifier identity independently of whether the full positive window fits. Immediate-predecessor query code also leaks; do not attribute this hole to the newest commit. [Independent adjudication](db_ui/attack_adjudication.md).

## Earlier findings — individual FIXED / NOT FIXED dispositions

These tables are backed by this round's script executions, not inherited verdicts. The earlier report's table layout is reused for traceability. All original originator-blocking inputs are **FIXED**; continued limitations and accepted over-refusals remain individually **NOT FIXED**. M2 stopped without a REPORT; its partial role/order and name fixtures are included through the completed M2b/cumulative replays. Repeated rows reflect repeated qualifications rather than independent defects.

### M1

| Finding / reproduction | Current result |
|---|---|
| B1 `bevacizumab - awwb`, `89Zr - trastuzumab`, `[89Zr] trastuzumab` | **FIXED** — refusal, no centre. [Original script replay](names/m1_exact/names_product_bypass.json), [HTTP](root_checks/regression_http.json). |
| B2 collaborator called lead: `NCT00200395`, reverse `ORG:genentech` | **FIXED** — Genentech collaborator / Montefiore lead, both directions. `src/app.py:137,160-169`; `web/try.html:142-149`. [DB](db_ui/db_assertions.json), [rendered UI](db_ui/ui_harness_results.json). |
| B3 Investigator called institution: `NCT00754364`, `ORG:armandosantoromd` | **FIXED** — person-specific heading. `web/try.html:143,148`. [DB](db_ui/db_assertions.json), [rendered UI](db_ui/ui_harness_results.json). |
| B4 retire CHEMBL3353410 in memory; query name, ID, EGFR | **FIXED** — name/ID not_found; retired neighbour excluded. `src/app.py:115-118`. [Original HTTP fixture](names/m1_exact/names_retired_http_results.json). |
| Retired Trial included in live Drug count | **FIXED** — centre count and neighbour count/weight 0. `src/app.py:129-132,139,174`. [Fixtures](db_ui/db_fixtures.json). |
| S1 misleading most-evidence wording/order, Disease | **FIXED** — actual start-date/score/count/A–Z sort disclosed and verified. `src/app.py:141-170`; `web/try.html:148-158,231-235`. [Oracle](db_ui/db_validate.json). |
| S2 silent ring cuts: ALDESLEUKIN, Disease, AstraZeneca | **FIXED** — 22/25, 39/3,074, 41/145 drawn disclosed; cut lists say 30. [UI](db_ui/ui_harness_results.json). |
| S3 stale trail after refusal/not-found/server/network error | **FIXED** — state/buttons clear, obsolete back harmless. `web/try.html:213-216,243-244`. [UI](db_ui/ui_harness_results.json). |
| S4 reverse-completed EGFR/KRAS requests and concurrent duplicate EGFR | **FIXED** — latest KRAS stays, duplicate gives one trail entry. `web/try.html:211-214`. [UI](db_ui/ui_harness_results.json). |
| S5 silent ambiguity: Roche, MET, osimertinib EGFR/reversal, Mvasi and bevacizumab | **FIXED for disclosure** — selected reading/alternatives/refusal visible. `src/app.py:95-114`; `web/try.html:222-226`. [Names](names/names_reproduction_results.json). |
| S6 action/class specificity | **FIXED** — specific gloss and original AGONIST/BINDING AGENT/class codes. `web/try.html:162-176`. [UI](db_ui/ui_harness_results.json). |
| S7 start date, sponsor-to-Drug global count/phase, zero-trial Drug | **FIXED** — NCT00200395 start 2003-07-02; osimertinib sponsor 14/global 79/APPROVAL; CHEMBL925 count 0. [DB](db_ui/db_assertions.json), [rendered UI](db_ui/ui_harness_results.json). |
| S8 node/edge props null, list, broken JSON | **FIXED** — 12 original requests and restorations return 200. `src/app.py:211-217`. [Fixtures](db_ui/db_fixtures.json). |
| Hostile labels/titles/IDs/URLs; scheme/host/credential/backslash probes | **FIXED for exercised markup paths** — escaping and HTTPS registry allowlist; browser limitation above. `web/try.html:104,180,199,221-235`. [Assertions](db_ui/ui_assertions.json). |
| Unknown type Other / relation NEWREL | **FIXED** — raw fallback, no undefined tooltip. [UI](db_ui/ui_regressions.json). |
| All three / everything documentation overclaims | **FIXED** — All of them / a capped list per relation. `src/app.py:5-11`. |
| Silent 500-character cut: `"x"*500 + " osimertinib"`, `"osimertinib " + "x"*600` | **FIXED** — explicit HTTP 400, no partial map. `src/app.py:239-243`. [HTTP](root_checks/http_results.json). |
| Lowercase IDs / Investigator names: nct00200395, chembl3353410, Armando Santoro Md | **NOT FIXED**, unchanged usability limit. [Controls](names/names_unsupported_forms.json). |
| Raw list/null/malformed JSON/oversized-body errors | **NOT FIXED**, unchanged controlled 400 exposing parse/attribute details; subsequent valid requests succeed. `src/app.py:237-239,267-269`. [HTTP](root_checks/http_results.json). |

### M2b

| Finding / reproduction | Current result |
|---|---|
| R1 `osimertinib and generic version of bevacizumab`, reverse/comma, trial/sponsor QA | **FIXED** — only separate osimertinib; correct evidence. [HTTP](root_checks/regression_http.json), [supplement](root_checks/supplemental_http.json). |
| R1 tracer/oral-product collateral refusal, both orders | **FIXED** — `[89Zr] trastuzumab and osimertinib` and `osimertinib and oral azacitidine` retain osimertinib. [Names](names/names_regressions.json). |
| Inherited `What is the generic version of bevacizumab?` | **FIXED** — refusal, no centre; also M3-B2. [HTTP](root_checks/supplemental_http.json). |
| R2 missing sponsor count, Alaunos–ALDESLEUKIN edge, both endpoints and null/list/broken/empty props | **FIXED** — null/zero sort weight; UI unknown, numeric 0 stays 0. `src/app.py:141-146`; `web/try.html:173`. [Fixture](db_ui/db_missing_sponsor_count.json). |
| Bool association score and hidden precision rounding | **FIXED** — bool null/weight 0; exact EGFR/KRAS decimal values retained. [DB](db_ui/db_score_fixture.json), [UI](db_ui/ui_regressions.json). |
| Embedded multi-ID `Sharedbrand company` fixture | **FIXED** — Roche disclosed alongside selected AstraZeneca. `src/app.py:97-102`. [Fixture](names/names_boundary_details.json). |
| Missing/unknown SPONSORS role and equal-weight A–Z | **FIXED** — neutral role wording, both directions/types; ordering verified. [DB/UI](db_ui/db_assertions.json). |
| Trial phases='PHASE2' render exception, four entry routes | **FIXED** — caught error, cleared trail, recovery/stale suppression. [Callbacks](db_ui/ui_m3_checks.json). |
| Residual module wording / successful-input truncation | **FIXED** — individual M1 rows above. |

### M3 and M4

| Finding / reproduction | Current result |
|---|---|
| M3-B1 `paclitaxel with albumin bound nanoparticles`, formulation variant, `generic version with bevacizumab` | **FIXED** — no originator centre/evidence. [HTTP](root_checks/supplemental_http.json), [names](names/names_new_boundaries.json). |
| M3-B2 leading generic-version question | **FIXED** — full qualified drug refused. [HTTP](root_checks/supplemental_http.json). |
| M3 comma collateral refusal: osimertinib with separately listed liposomal/biosimilar drug; reversals/QA | **FIXED** — separate osimertinib retained, 12 trial rows. [HTTP](root_checks/supplemental_http.json). |
| M3 bare erlotinib hydrochloride / long paclitaxel-poliglumex name; nested-parent re-link | **FIXED / retained** — correct complete IDs; no nested parent; explicit separate parent survives. [Names](names/names_attack.json). |
| M4-B1 wrong shortest-span tie: `osimertinib with generic version of bevacizumab`, reversal/added a | **FIXED under revised design** — both same-item drugs refused; zero qualified-drug QA evidence. [HTTP](root_checks/attack_http.json). |
| M4-B1 semicolon and fullwidth-comma variants | **FIXED** — separate osimertinib retained. [Separators](names/names_separator_checks.json). |
| M4-B2 long qualified poliglumex / `generic version of the monoclonal antibody bevacizumab` | **FIXED** — refused; bare long-name control preserved. [HTTP](root_checks/attack_http.json). |
| M4-B3 consumed qualifier: biosimilar version / liposomal formulation / albumin-bound / two-product combination | **FIXED** — no parent hit/evidence. [Names](names/names_attack.json), [HTTP](root_checks/attack_http.json). |
| M4 target/company collateral refusal: EGFR or AstraZeneca beside biosimilar bevacizumab, reverse/with controls | **FIXED** — target/company retained; drug refusal disclosed. [HTTP](root_checks/m5_http.json). |
| M4 no-relink QA assessment | **FIXED / retained** — exact frozen 1,648-input counterfactual, 68 identical / 1,556 metadata-only / 24 semantic differences / 0 errors; adapted matcher target is `_link`. [Result](names/adapted_frozen_qa_relink_sweep.json). |
| M3/M4 blank/whitespace form | **NOT FIXED**, unchanged usability limit: no request, previous view stays. `web/try.html:241`. [UI](db_ui/ui_m3_checks.json). |
| M3/M4 positive/negative Infinity fixture | **NOT FIXED**, unchanged failure closed: controlled HTTP 400, no invalid value drawn, none in snapshot. `src/app.py:207-208,264-269`. [Fixture](db_ui/db_numeric_fixture.json). |
| Repeated lowercase-ID/name and raw request qualifications | **NOT FIXED**, same individual M1 rows above. |

### M5 and M6

| Finding / reproduction | Current result |
|---|---|
| M5-B1 reported attached slash/pipe and internal both-sides-glued attack | **FIXED** — `bevacizumab-awwb/ osimertinib` and `bevacizumab - awwb/osimertinib` select only OSIMERTINIB and expose refusal; pipe counterparts too. [HTTP](root_checks/m5_http.json), [m6 replay](root_checks/confirm_http.json). |
| M5-B2 `liposomal and nanoparticle formulation of doxorubicin`, plural/sustained-release | **FIXED** — forward qualifier carry refuses product; QA 0. [HTTP](root_checks/m5_http.json). |
| M5-S1 `biosimilar anastrozole, Arimidex`; `biosimilar Prolia, xgeva` | **FIXED** — separate aliases survive; 2/3 trial rows. [HTTP](root_checks/cross_item_http.json). |
| M5-S1 `Erlotinib, hydrochloride biosimilar bevacizumab`, semicolon | **FIXED** — original qualified comma/semicolon inputs preserve CHEMBL553; the simplified comma-list M7 regression is also repaired. [Exact HTTP](root_checks/m5_http.json), [M7 controls](names/historical_focus.json). |
| M5-S2 Pegylated interferon alfa-2a | **NOT FIXED — accepted known over-refusal**, not a new blocker. Canonical name/ID work. [HTTP](root_checks/m5_http.json). |
| M5-S3 all-substring cubic work / 999-character plain-answer timeout | **FIXED for exact previous cost cases** — bounded predicate work and original plain-answer requests complete. Repeated-piece overhead also repaired; the cache-boundary failure is now also repaired (M8-S1 below). [Original HTTP](root_checks/perf_check_http.json), [current instrumentation](cost/perf_current.json). |
| M6-B1 interior slash/pipe | **FIXED** — separate osimertinib retained; forbidden originator absent from QA. [Exact HTTP](root_checks/confirm_http.json), [39-case matrix](names/focused_matrix.json). |
| M6-B2 U+3002 suffix punctuation, trailing em dash/hyphen, leading hyphen | **FIXED** — all four original edge-punctuation inputs refuse, as do trial/sponsor QA. [Exact HTTP](root_checks/confirm_http.json), [current focused stages](names/historical_focus.json). |
| M6-B2 supplementary bracketed/Unicode variants | **FIXED** — whole-product wrappers `(bevacizumab-awwb)` / `[bevacizumab-awwb]` and the previously reported Unicode hyphens now refuse; question-mark and quoted shortcut cases also refuse. [Historical matrix](names/historical_focus.json), [m7 attack HTTP](names/m7_attacks/http_results.json). |
| M6-B3 `doxorubicin (nanoparticle and liposomal formulation)` / `bevacizumab (investigational and biosimilar)` | **FIXED** — both parenthesized reversed qualifiers produce no centre or QA evidence. [Exact HTTP](root_checks/carry_http.json), [stages](names/historical_focus.json). |
| M6 non-parenthetical reversed-qualifier supplement | **NOT FIXED as original expectation; accepted current item-policy consequence** — `doxorubicin in nanoparticle and liposomal formulations` still selects doxorubicin after listing-word separation. [Exact HTTP](root_checks/reverse_http.json). |
| M6-S1 six complete stored aliases returning another Drug ID | **FIXED for all six bare inputs** — intended stored IDs retained. [Current stages](names/historical_focus.json), [HTTP](root_checks/alias_http.json). |
| M6-S1 prefixed QA using those comma-containing names | **NOT FIXED — current whole-input-only design consequence**. ENDOSTATIN prefixed QA still selects CHEMBL4297747 with 2 rows; Rapamycin prefixed QA CHEMBL413 with 5 rows. [Exact HTTP](root_checks/alias_http.json), [direct QA](names/historical_focus.json). |
| M6 associated lone stored-alias losses | **FIXED for all 19 non-M5-S2 historical lost aliases** — slash/joiner names restored; known M5-S2 still refuses. M9-S1 is individually classified below; its three accepted over-refusals remain. [Exact previous/current alias comparison](names/alias_regressions.json), [complete current sweep](names/adapted_names_m5_summary.json). |
| M6 split_2000 / many-piece cost control | **FIXED for exact repeated-piece cost control** — current resolver skips no-drug pieces and deduplicates; the previous per-piece delay is gone. [Exact stress replay](cost/cost_stress.json), [old/current samples](cost/fresh_cost_comparison.json). |

### M7

| Finding / reproduction | Current result |
|---|---|
| M7-B1 Whole-name refusal bypass: `bevacizumab-awwb?`, `bevacizumab-awwb!`, quoted form | **FIXED** — All return refusal/no centre; trial and sponsor QA zero. [Current stages](names/historical_focus.json), [original m7 HTTP replay](names/m7_attacks/http_results.json). |
| M7-B2 Wrappers and Unicode hyphens: `(bevacizumab-awwb)`, `[bevacizumab-awwb]`, U+2011 suffix and bio-similar | **FIXED** — All named inputs refuse after shared normalization and edge stripping; no originator QA. [Stages](names/historical_focus.json), [HTTP](names/m7_attacks/http_results.json). |
| M7-B3 Whitespace isotope: `89Zr trastuzumab` | **FIXED** — No centre; both QA forms have zero evidence. [Stages](names/historical_focus.json), [HTTP](names/m7_attacks/http_results.json). |
| M7-S1 Canonical equality too broad: `Erlotinib, hydrochloride`, `osimertinib,mesylate`, `is a` | **FIXED** — Respectively CHEMBL553, CHEMBL3353410 and not_found; actual exact aliases retain intended IDs. [Current controls](names/historical_focus.json), [HTTP](names/m7_attacks/http_results.json). |
| M7-S2 Lone exact stored names: `(E/Z)-AFATINIB`, `RO 09-1978/000`, `Anusol plus hc` and 19-alias set | **FIXED** — All 19 old non-M5-S2 losses restored; three named controls select CHEMBL1173655 / CHEMBL1773 / CHEMBL389621. [Exact previous/current comparison](names/alias_regressions.json), [HTTP](names/alias_http.json). |
| M7-S3 Repeated identical-piece full resolver cost / queued ordinary map | **FIXED** — Exact old repeated-x controls and corresponding requests complete with materially reduced work. The cache failure is now repaired (M8-S1 below); unique-piece cost is reported below. [Cost replay](cost/cost_stress.json), [comparison](cost/fresh_cost_comparison.json), [HTTP](cost/fresh_cost_http.json). |


### M8

| Finding / exact reproduction | Round 11 disposition |
|---|---|
| M8-B1 `[89 Zr] trastuzumab`, tab/newline/NBSP between mass and element | **FIXED** - no centre; trial/sponsor QA zero. Recorded `radiotracer_guard` honored at `src/query.py:217-222`; adjacent alnum labels checked at `249-265`. [Replayed stages](names/attacks/probe_results.json), [HTTP](root_checks/new_http.json). |
| M8-B2 `bevacizumab-(awwb)`, `bevacizumab-[awwb]`, separate-osimertinib variant | **FIXED** - product refused; separate OSIMERTINIB survives; qualified-product QA zero. `src/query.py:125-141`. [Stages](names/attacks/probe_results.json), [HTTP](root_checks/new_http.json). |
| M8-B3 U+2E3A `bevacizumab⸺awwb`; all 26 Unicode Pd characters | **FIXED** - all 26 fold to hyphen and refuse; no originator centre. `src/query.py:100-117`. [All Pd results](names/attacks/unicode_dashes.json), [HTTP](root_checks/new_http.json). |
| M8-S1 4,097th cache entry; original 7,511-key alias sweep | **FIXED** - 82 successful requests fill 4,096 distinct pieces; first `osimertinib` and retry both HTTP 200 / CHEMBL3353410 / 79 trials. Original and adapted alias sweeps finish without cache errors. `src/query.py:200-208`. [Natural HTTP](cost/cache_boundary_http.json), [name runs](names/round9_execution.json). |
| M8-S2 `biosimilar, and osimertinib`, `biosimilar; and osimertinib`, `biosimilar and, osimertinib` | **FIXED** - all preserve CHEMBL3353410; the first comma-and form has 12 trial and 12 sponsor QA rows. Carry now requires equal comma/semicolon clause IDs at `src/query.py:348-350`. [HTTP](root_checks/new_http.json), [replayed stages](names/attacks/probe_results.json). |
| M8-S3 `566C`, `9-ac`, `5ac` | **FIXED** - correct CHEMBL1450 / CHEMBL274070 / CHEMBL1489, HTTP 200. `src/query.py:209-222,252-265`. [Alias HTTP](names/alias_checks/new_http.json). |
| M8-S4 `5.BETA.,20-EPOXY-1,2.ALPHA.,4,7.BETA.` | **FIXED** - PACLITAXEL / CHEMBL428647, HTTP 200. Stored/input punctuation stripped symmetrically at `src/query.py:277-282`. [Alias HTTP](names/alias_checks/new_http.json). |

### M9

| Finding / exact reproduction | Round 11 disposition |
|---|---|
| M9-B1 `bevacizumab_awwb`, `bevacizumab__awwb`, accented/decomposed `bevácizumab-awwb`, dotted suffix | **FIXED** — exact reported forms refuse; separate osimertinib survives; trial/sponsor QA has no forbidden originator evidence. Guards now use accent/punctuation folding and same-drug suffix keys at `src/query.py:125-141,238-247`. [Exact M9 matrix](names/m9_attacks/probe_results.json), [HTTP](names/m9_attacks/http_results.json), [root confirmation](root_checks/independent_http.json). |
| M9-B2 `[89.Zr] trastuzumab`, `89:Zr trastuzumab`, `89::Zr` variants | **FIXED** — no centre and no trial/sponsor evidence for the exact inputs. `src/query.py:249-265`. The distinct M10-B3 whitespace/punctuation-token reproduction is also fixed; see M10 below. [M9 stages](names/m9_attacks/probe_results.json), [HTTP](root_checks/independent_http.json). |
| M9-B3 `bevacizumab awwb`, `bevacizumab (awwb)` / `[awwb]`, `trastuzumab dkst` | **FIXED** — known suffix forms refuse, with zero originator QA. `src/query.py:241-265`. [M9 stages](names/m9_attacks/probe_results.json), [HTTP](root_checks/independent_http.json). |
| M9-S1 `Theophylline in dextrose 5% in plastic container` | **FIXED** — correct THEOPHYLLINE / CHEMBL1355736 over HTTP 200. [Alias confirmation](names/new_alias_confirmation.json), [root HTTP](root_checks/independent_http.json). |
| M9-S1 `40-o-(2-hydroxyethyl)-rapamycin` | **NOT FIXED — accepted known over-refusal**, not a blocker. EVEROLIMUS/name ID controls work. [Alias confirmation](names/new_alias_confirmation.json). |
| M9-S1 `42-o-(2-hydroxyethyl)rapamycin` | **NOT FIXED — accepted known over-refusal**, not a blocker. [Alias confirmation](names/new_alias_confirmation.json). |
| M9-S1 `Trastuzumab--vcmmae conjugate` | **NOT FIXED — accepted known over-refusal**, not a blocker. TRASTUZUMAB VEDOTIN and its ID work. [Alias confirmation](names/new_alias_confirmation.json), [root HTTP](root_checks/independent_http.json). |

### M10

| Finding / exact reproduction | Round 11 result |
|---|---|
| M10-B1 trailing isotope absorbed by alias: `A33 124i`, `A33 124 i`, `A33 [124i]`, `A33 124-I`, `A33-124i` | **FIXED** — no ADAKITUG centre for qualified input; refusal, zero qualified trial/sponsor evidence. ADAKITUG preferred name remains available. [Stages](names/m10_attacks/focus_results.json), [HTTP](root_checks/candidate_http.json). |
| M10-B2 isotope stands in for substance: `18F fluorothymidine`, `18-F fluorothymidine`, `[18F] fluorothymidine`, `18F nonexistingdrug` | **FIXED** — no FDG centre or QA evidence. Lone `18F` still selects CHEMBL2030434. [HTTP](root_checks/isotope_http.json). |
| M10-B3 punctuation consumes isotope-neighbour budget: `trastuzumab 89 - Zr`, `trastuzumab [89 - Zr]`, `trastuzumab 89_Zr` | **FIXED** — refusal; normalized neighbour words checked before limiting. Separate osimertinib survives. [Stages](names/m10_attacks/focus_results.json), [HTTP](root_checks/candidate_http.json). |
| M10-B4 respelt qualifier: `generic-version of bevacizumab`, `generic_version of bevacizumab`, `albumin - bound paclitaxel`, `follow-on-biologic bevacizumab` | **FIXED** — refused, with no parent QA evidence for the reported qualified requests. [Stages](names/m10_attacks/probe_results.json), [HTTP](root_checks/candidate_http.json). |
| M10 distinct-piece lock contention | **NOT FIXED**, performance should-fix; legal cold requests can queue ordinary maps for seconds. Updated isolated observations below. |
| M10 repeated known over-refusals / blank submission / Infinity / unsupported names and prefixed comma aliases | **NOT FIXED** where individually recorded above; they are not promoted into new blockers. |

## Cost and nonblocking findings

Historical costs were replayed with the original workloads. Final timed suites ran sequentially after the root/name/DB workers stopped CPU-intensive execution. Unrelated host activity is uncontrolled; these are observations, not service-level guarantees or proof of global linear complexity. [Cost report](cost/FINDINGS.md), [reuse manifest](cost/reuse_manifest.json), [execution](cost/execution.json).

| Reproduction | Current observation / disposition |
|---|---|
| M5-S3 cubic scan, 250 plain tokens | **FIXED**. 2,224 predicate calls per predicate and 33,880 aggregate characters, versus the old 31,625 / 10,479,750. Current 499-character linker median **0.02647 s**. [Instrumentation](cost/perf_current.json), [comparison](cost/fresh_cost_comparison.json). |
| Original 999-character answer timeout/follower request | **FIXED**. HTTP 200 in **0.20895 s**, ordinary EGFR follower **0.02173 s**. [Exact reproduction](cost/perf_check_http.json). |
| M6 split_2000 / M7-S3 repeated-piece resolver work | **FIXED**. `';'.join(['x']*2000)` linker median **0.16096 s**, versus `9bd7cb4` **2.28857 s** on the same data. HTTP check **0.49877 s**, queued EGFR **0.41989 s**, both 200. [Comparison](cost/fresh_cost_comparison.json), [HTTP](cost/fresh_cost_http.json). |
| M8-S1 natural cache rollover | **FIXED**. **82/82** fill requests 200, 4,096 distinct pieces; first osimertinib at rollover and retry both 200 / CHEMBL3353410 / 79 trials. [HTTP](cost/cache_boundary_http.json). |
| Distinct 400 drug-bearing pieces, `';'.join(f'isa x{i:04d}' for i in range(400))` | **NOT FIXED**, inherited performance should-fix. Cold `/api/check` **2.73397 s**, queued EGFR map **2.65132 s**; warm check **0.33558 s**. Resolver calls **400 cold / 0 warm**. [HTTP](cost/isolated_unique_cost_http.json), [calls](cost/unique_piece_cost.json). |
| New Unicode expansion workload, `answer='\ufdfa'*4000`, UTF-8 JSON | **NOT FIXED**, nonblocking performance concern. Valid 4,000-character answer expands to **72,000 characters** at NFKC folding. HTTP check **2.44818 s**, queued EGFR **2.36582 s**; warm check **2.81211 s**. Both checks return 200. Current direct-link median **2.67598 s**, HEAD^ **2.34056 s**: the expensive path already existed. [HTTP](cost/isolated_unicode_cost_http.json), [comparison](cost/normalization_cost.json). |
| Added separator normalization cost, 3,999-character punctuation workload | Three-sample direct-link median **0.42502 s**, HEAD^ **0.22475 s**. This shows measurable overhead on this synthetic case; normal cached osimertinib lookup remains about **0.00009 s** in both. [Exact inputs and measurements](cost/normalization_cost.json). |
| Disease and ordinary concurrent requests | Disease: **2,774 Trials + 300 Targets**, 30 per list, **18,575 bytes / 67.137 ms**. Historical 24-request / 12-worker workload: all expected 200 shapes, **757.866 ms** total. These ordinary measurements overlap initial audit work, not the isolated timing window. [HTTP](root_checks/http_results.json). |

The shared `engine.lock` covers these operations (`src/app.py:247-263`), so expensive legal `/api/check` requests still delay unrelated maps. The Unicode stress uses the **answer** field, whose limit is 4,000; it is not a 4,000-character `/api/explore` text claim (that endpoint correctly rejects text over 500 characters). Limits are applied before normalization (`src/app.py:239-243,258-263`; `src/query.py:116-117,173-177`). No deadlock or invented graph value was observed.

**M11-S1 — additional stored-alias over-refusals, nonblocking.** The broader sweep has **69** prior-method positives without a current Drug, **37 more** than m10's loss set. Many additions are intended labelled-product refusals, including repaired `A33 124i`; these counts are not counts of defects. Additional apparently unlabelled stored aliases now refused include `9-amino-20(s)-camptothecin`, `il-6ra` (TOCILIZUMAB) and `TAK-659F` (MIVAVOTINIB). The isotope parser interprets substrings `20 s`, `6ra`, or `659F` as labels. No wrong centre is drawn, so these are should-fix lookup losses, not approval blockers. [Exact loss set](names/new_alias_losses.json), [name assessment](names/FINDINGS.md).

The explicitly accepted M5-S2 and three M9-S1 over-refusals remain separately NOT FIXED in the historical tables. Other unchanged qualifications—blank submission, controlled Infinity/parser errors, unsupported lowercase IDs/investigator labels, prefixed comma-name QA and nonparenthetical listing policy—are also retained individually. No new demo regression was established.

## Standards axis

**Zero documented-standards findings.** The separate reviewer examined original-to-current application changes and the latest query/tests change. No repository AGENTS.md, CONTRIBUTING or coding-standards source was found. The user-supplied audit-only and evidence-based instructions govern. No tracked file was changed; the KOA Studio / KhOpenApi original-versus-modified-code requirement is conditional on code changes and does not apply to this no-edit audit. [Independent standards review](db_ui/FINDINGS.md#standards-axis).

## Spec axis

**Two P1 blocking families, M11-B1 and M11-B2.** Both reach an originator centre with no refusal at any stage; existing exact cases are repaired but equivalent punctuated qualifications still fail. The no-model, stored-edge, stored-value, direction, cut-notice and exercised markup/state checks pass. That does not make a wrongly chosen centre correct. The two blockers alone determine the verdict; accepted over-refusals and performance observations do not. [Specification assessment](attacks/FINDINGS.md), [independent adjudication](db_ui/attack_adjudication.md).

## Integrity and reproduction

Snapshot facts: **7 retired nodes, 142 retired edges, zero real self-loops and zero live edges with retired endpoints**. All six live node types and all 22 existing group combinations were exercised. The new self-loop behavior is established by an in-memory fixture, not claimed as real snapshot data. [Snapshot](db_ui/db_snapshot_facts.json), [fixture](db_ui/self_loop_unknown.json).

`Engine.ask` explicitly passes `use_llm=False` (`src/app.py:180-181`). No model was called. Mutating fixtures use in-memory copies; before/after hashes establish that application data were unchanged. The application does not globally enforce a read-only SQLite handle, so this is an executed-path/integrity result, not a database-permission guarantee.

Final verification compares **3,348 tracked-file SHA-256 hashes**, HEAD, tracked/staged diffs, database bytes, report links and owned-port cleanup in [integrity_final.json](integrity_final.json). Database SHA-256: **`7341c5a7089731f67356da5a588b269d4b69e8e6c4c054acf19aa4ef2837b529`**. Existing m11 brief/log files were preserved. All new scratch artifacts are under m11.

Run from repository root with bytecode disabled and TMP/TEMP/TMPDIR under the corresponding m11 subdirectory. Port-sharing scripts must remain sequential; worker manifests record adapted paths and baseline semantics.

```text
python -B audit_evidence_claims/m11/root_checks/run_replays.py tests
python -B audit_evidence_claims/m11/root_checks/run_replays.py http
python -B audit_evidence_claims/m11/root_checks/run_remaining.py
python -B audit_evidence_claims/m11/names/run_round9.py
python -B audit_evidence_claims/m11/names/run_final_replays.py
python -B audit_evidence_claims/m11/names/m10_attacks/probe.py
python -B audit_evidence_claims/m11/names/m10_attacks/focus.py
python -B audit_evidence_claims/m11/db_ui/run_db.py
python -B audit_evidence_claims/m11/db_ui/run_ui.py
python -B audit_evidence_claims/m11/attacks/key_equivalence.py
python -B audit_evidence_claims/m11/root_checks/new_leaks_http.py
```

VERDICT: CHANGES REQUIRED
