# Independent relation-map review — round 12

Reviewed **`d9260a1ea544cf7bb80415383667784e0aba146a`**, beginning 2026-11-03 KST. **Changes required:** the exact reported blocking reproductions from m1–m11 are fixed, but a stored tracer alias still passes every refusal stage and draws its originator. One additional stored-alias over-refusal was introduced by the latest repair. No tracked file was edited; all new audit artifacts are under `audit_evidence_claims/m12/`.

The verdict is based on **one P1 blocker, M12-B1**. Known accepted over-refusals, retained policy limitations and measured performance costs are reported separately and do not determine it.

## Verification and limits

- **339 passed in 38.09 s**, exit 0: `python -m pytest tests -q -p no:cacheprovider`, bytecode disabled and temporary paths confined to m12. [Output](root_checks/pytest.txt), [environment/hash record](root_checks/pytest_summary.json).
- Reused the earlier root HTTP runners sequentially: six original/cumulative runners, four M6 runners, M8/M9 confirmations, both M10 confirmations and the M11 exact confirmation. All exit 0. [Reuse manifest](reuse_manifest_root.json), [batch](root_checks/execution_all.json), [six runners](root_checks/execution_http.json), [M6](root_checks/execution_m6_http.json), [M8/M9](root_checks/execution_extra.json), [remaining](root_checks/execution_remaining.json). Original reproduction inputs and historical comparison sources were retained; output paths and owned ports were adapted.
- Naming replays executed **41 reused leaf scripts**, from **47 copied prior scripts**, all exit 0. This includes the original M1 scripts, cumulative M2b–M11 matrices, **7,511-key** alias sweep, **1,648-question** frozen no-relink counterfactual, M9's 146-input probe, M10's 1,224-input probe and 35-case focus, and M11's 26-case attack script. Counterfactual counts remain **68 identical / 1,556 metadata-only / 24 semantic / zero errors**. These are declared same-data method counterfactuals, not whole-deployment version comparisons. [Name report and 59 individual rows](names/FINDINGS.md), [manifest](names/reuse_manifest.json), [final checks](names/worker_final_checks.json).
- Independent graph oracle: **6,469 live centres, 22 relation/direction/type/role combinations, zero errors**. **19/19 DB assertions**, **24/24 UI assertions** and **4/4 self-loop/unknown-type/retirement fixture checks** pass. [DB/UI report](db_ui/FINDINGS.md), [oracle](db_ui/db_validate.json), [DB assertions](db_ui/db_assertions.json), [UI assertions](db_ui/ui_assertions.json), [fixture](db_ui/self_loop_unknown.json).
- All **36 page demos plus six map callbacks** pass. All 36 full demo responses equal m7–m11; all 36 actual CLI HTTP demo requests return 200 and equal Engine responses. The seven original QA evidence counts remain **12, 12, 11, 1, 12, 0, 0**. [Comparison](db_ui/demo_previous_comparison.json), [HTTP](db_ui/demo_http.json), [demo renders](db_ui/ui_demos_results.json), [six map callbacks](db_ui/ui_m3_checks.json).
- New attacks compare **41** inputs with current and HEAD^ query modules, and issue **76** actual HTTP requests. Root independently issued **56** further HTTP requests including the blocker, refused/bare controls, separate-osimertinib input, descriptive tracer probes and the new alias loss. All returned 200; owned servers closed; served page matches `web/try.html`. [Attack stages](attacks/focused_results.json), [attack HTTP](attacks/new_leaks_http.json), [independent HTTP](root_checks/independent_m12_http.json), [lifecycle](root_checks/independent_m12_lifecycle.json).

UI checks execute the actual page JavaScript in a Node VM with controlled DOM/fetch stubs. They prove exercised markup and callback/state behavior, not browser paint or browser-executed XSS. HTTP tests exercise unmodified `src/app.py` or its real handler with isolated in-memory fixtures. No audit used port 8765. No model was called. Findings below use repository aliases, predicates, stored data and refused controls; no external pharmacology assumption is required.

## M12-B1 — P1: a chelator-bearing stored tracer alias escapes every refusal

Exact request: `POST /api/explore` with `{"text":"[89Z.r]-DFO-daratumumab"}`.

**Actual:** HTTP 200, centre **DARATUMUMAB / CHEMBL1743007**, matched alias **`89zr-dfo-daratumumab`**, **2 live trials**, and no Refused entity or refusal notice. Trial and sponsor QA each return **2 originator evidence rows**. `89Z_r-dfo-daratumumab` also leaks. Appending `, osimertinib` still selects DARATUMUMAB. [Independent HTTP](root_checks/independent_m12_http.json), [stage comparison](attacks/focused_results.json).

**Controls:** `89Zr-dfo-daratumumab` and `[89Zr]-DFO-daratumumab` refuse, with zero trial/sponsor evidence. Bare `daratumumab` correctly maps to CHEMBL1743007. Candidate and refused control have the **same canonical key `89zrdfodaratumumab`**, which the index associates with a single AACT synonym for DARATUMUMAB. Thus this is a normalized spelling of the repository's own refused tracer alias, not an unsupported drug guess. [Dictionary/predicate evidence](attacks/dictionary_evidence.json), [independent adjudication](db_ui/adjudication.md).

| Stage | Result for `[89Z.r]-DFO-daratumumab` |
|---|---|
| Raw resolver | `CONTAINED_ALIAS` to CHEMBL1743007; no blocked component (underscore variant: `ALIAS`) |
| Resolver veto | `{}` |
| Item linker | Drug DARATUMUMAB; no Refused |
| Whole-name shortcut | `None`; it is not overriding an existing refusal |
| Public linker | Drug DARATUMUMAB; no Refused |
| Map / QA | Originator centre; trial/sponsor evidence 2/2 |

The causal chain is reproducible in the current code:

1. Positive lookup discards punctuation and consumes the full stored alias (`src/query.py:404-417`; `src/textrules.py:339-346`).
2. `_alnum_words` instead produces `['89Z', 'r', 'DFO', 'daratumumab']` (`src/query.py:111-113`). Inside-name isotope checks only inspect one/two-word runs joined by spaces (`src/query.py:258,278-280`). Neither `89Z` nor `89Z r` passes `is_isotope_label`, although glued `89Zr` does (`src/textrules.py:289-298`).
3. The latest glued-neighbour checks inspect words **outside** the consumed alias; there are none containing the isotope (`src/query.py:264-277`).
4. The latest isotope-plus-same-drug-key rule recognizes prefix `89zr`, but requires remainder `dfodaratumumab` to be another same-drug dictionary key (`src/query.py:282-286`). It has no index entry. Bare `daratumumab` does, but the intervening `DFO` remains.
5. The item-wide and raw resolver guards do not reassemble the split element symbol (`src/query.py:125-141`; `src/textrules.py:303-313`; `src/normalize.py:740-745`). `Engine.explore` then selects the surviving positive hit (`src/app.py:87-95`).

**Required outcome:** equivalent punctuation accepted by positive lookup must preserve the refused tracer identity inside a matched stored name, including intervening chelator text. Refusal must not depend on the isotope-stripped remainder being an independently stored alias. Existing lone-name and accepted over-refusal controls should remain explicit. This audit makes no implementation change.

The exact HEAD^ query module also leaks against the same current app/rules/database. **This is an inherited hole, not a regression attributed to this commit.** Only query.py is swapped in that counterfactual; it is not a reconstructed old deployment. [Independent current/previous checks](db_ui/adjudication.md).

## Earlier reproductions — FIXED / NOT FIXED per finding

The tables below retain historical finding identities, but each disposition is supported by this round's executions. “FIXED” concerns the stated reproduction, not a proof of all spellings. The M2 attempt has no final REPORT; its partial cases are represented by the completed M2b/cumulative replays. Repeated rows reflect repeated qualifications. See also the machine-readable [59-row name matrix](names/historical_name_dispositions.json) and [23-row DB/UI matrix](db_ui/historical_db_ui_matrix.json).

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

| Finding / exact reproduction | Round 12 disposition |
|---|---|
| M8-B1 `[89 Zr] trastuzumab`, tab/newline/NBSP between mass and element | **FIXED** - no centre; trial/sponsor QA zero. Recorded `radiotracer_guard` honored at `src/query.py`; adjacent alnum labels checked at `249-280`. [Replayed stages](names/attacks/probe_results.json), [HTTP](root_checks/new_http.json). |
| M8-B2 `bevacizumab-(awwb)`, `bevacizumab-[awwb]`, separate-osimertinib variant | **FIXED** - product refused; separate OSIMERTINIB survives; qualified-product QA zero. `src/query.py`. [Stages](names/attacks/probe_results.json), [HTTP](root_checks/new_http.json). |
| M8-B3 U+2E3A `bevacizumab⸺awwb`; all 26 Unicode Pd characters | **FIXED** - all 26 fold to hyphen and refuse; no originator centre. `src/query.py`. [All Pd results](names/attacks/unicode_dashes.json), [HTTP](root_checks/new_http.json). |
| M8-S1 4,097th cache entry; original 7,511-key alias sweep | **FIXED** - 82 successful requests fill 4,096 distinct pieces; first `osimertinib` and retry both HTTP 200 / CHEMBL3353410 / 79 trials. Original and adapted alias sweeps finish without cache errors. `src/query.py`. [Natural HTTP](cost/cache_boundary_http.json), [name runs](names/round9_execution.json). |
| M8-S2 `biosimilar, and osimertinib`, `biosimilar; and osimertinib`, `biosimilar and, osimertinib` | **FIXED** - all preserve CHEMBL3353410; the first comma-and form has 12 trial and 12 sponsor QA rows. Carry now requires equal comma/semicolon clause IDs at `src/query.py`. [HTTP](root_checks/new_http.json), [replayed stages](names/attacks/probe_results.json). |
| M8-S3 `566C`, `9-ac`, `5ac` | **FIXED** - correct CHEMBL1450 / CHEMBL274070 / CHEMBL1489, HTTP 200. `src/query.py`. [Alias HTTP](names/alias_checks/new_http.json). |
| M8-S4 `5.BETA.,20-EPOXY-1,2.ALPHA.,4,7.BETA.` | **FIXED** - PACLITAXEL / CHEMBL428647, HTTP 200. Stored/input punctuation stripped symmetrically at `src/query.py`. [Alias HTTP](names/alias_checks/new_http.json). |

### M9

| Finding / exact reproduction | Round 12 disposition |
|---|---|
| M9-B1 `bevacizumab_awwb`, `bevacizumab__awwb`, accented/decomposed `bevácizumab-awwb`, dotted suffix | **FIXED** — exact reported forms refuse; separate osimertinib survives; trial/sponsor QA has no forbidden originator evidence. Guards now use accent/punctuation folding and same-drug suffix keys at `src/query.py`. [Exact M9 matrix](names/m9_attacks/probe_results.json), [HTTP](names/m9_attacks/http_results.json), [root confirmation](root_checks/independent_http.json). |
| M9-B2 `[89.Zr] trastuzumab`, `89:Zr trastuzumab`, `89::Zr` variants | **FIXED** — no centre and no trial/sponsor evidence for the exact inputs. `src/query.py`. The distinct M10-B3 whitespace/punctuation-token reproduction is also fixed; see M10 below. [M9 stages](names/m9_attacks/probe_results.json), [HTTP](root_checks/independent_http.json). |
| M9-B3 `bevacizumab awwb`, `bevacizumab (awwb)` / `[awwb]`, `trastuzumab dkst` | **FIXED** — known suffix forms refuse, with zero originator QA. `src/query.py`. [M9 stages](names/m9_attacks/probe_results.json), [HTTP](root_checks/independent_http.json). |
| M9-S1 `Theophylline in dextrose 5% in plastic container` | **FIXED** — correct THEOPHYLLINE / CHEMBL1355736 over HTTP 200. [Alias confirmation](names/new_alias_confirmation.json), [root HTTP](root_checks/independent_http.json). |
| M9-S1 `40-o-(2-hydroxyethyl)-rapamycin` | **NOT FIXED — accepted known over-refusal**, not a blocker. EVEROLIMUS/name ID controls work. [Alias confirmation](names/new_alias_confirmation.json). |
| M9-S1 `42-o-(2-hydroxyethyl)rapamycin` | **NOT FIXED — accepted known over-refusal**, not a blocker. [Alias confirmation](names/new_alias_confirmation.json). |
| M9-S1 `Trastuzumab--vcmmae conjugate` | **NOT FIXED — accepted known over-refusal**, not a blocker. TRASTUZUMAB VEDOTIN and its ID work. [Alias confirmation](names/new_alias_confirmation.json), [root HTTP](root_checks/independent_http.json). |

### M10

| Finding / exact reproduction | Round 12 result |
|---|---|
| M10-B1 trailing isotope absorbed by alias: `A33 124i`, `A33 124 i`, `A33 [124i]`, `A33 124-I`, `A33-124i` | **FIXED** — no ADAKITUG centre for qualified input; refusal, zero qualified trial/sponsor evidence. ADAKITUG preferred name remains available. [Stages](names/m10_attacks/focus_results.json), [HTTP](root_checks/candidate_http.json). |
| M10-B2 isotope stands in for substance: `18F fluorothymidine`, `18-F fluorothymidine`, `[18F] fluorothymidine`, `18F nonexistingdrug` | **FIXED** — no FDG centre or QA evidence. Lone `18F` still selects CHEMBL2030434. [HTTP](root_checks/isotope_http.json). |
| M10-B3 punctuation consumes isotope-neighbour budget: `trastuzumab 89 - Zr`, `trastuzumab [89 - Zr]`, `trastuzumab 89_Zr` | **FIXED** — refusal; normalized neighbour words checked before limiting. Separate osimertinib survives. [Stages](names/m10_attacks/focus_results.json), [HTTP](root_checks/candidate_http.json). |
| M10-B4 respelt qualifier: `generic-version of bevacizumab`, `generic_version of bevacizumab`, `albumin - bound paclitaxel`, `follow-on-biologic bevacizumab` | **FIXED** — refused, with no parent QA evidence for the reported qualified requests. [Stages](names/m10_attacks/probe_results.json), [HTTP](root_checks/candidate_http.json). |
| M10 distinct-piece lock contention | **NOT FIXED**, performance should-fix; legal cold requests can queue ordinary maps for seconds. Updated isolated observations below. |
| M10 repeated known over-refusals / blank submission / Infinity / unsupported names and prefixed comma aliases | **NOT FIXED** where individually recorded above; they are not promoted into new blockers. |

### M11

| Finding / exact reproduction | Round 12 result |
|---|---|
| M11-B1 `[89Z.r] trastuzumab`, `89Z_r trastuzumab`, `trastuzumab [89Z.r]` | **FIXED** — all refuse; trial/sponsor QA zero; adding `, osimertinib` selects only OSIMERTINIB. [Exact stages](names/m11_exact.json), [original 26-case script](names/m11_attacks/key_equivalence_results.json), [60 HTTP responses](root_checks/new_leaks_http.json). |
| M11-B2 `bevacizumab a - w w b`, `bevacizumab - a - w - w - b`, `bevacizumab a_w_w_b` | **FIXED** — all refuse; trial/sponsor QA zero; separate osimertinib survives. [Literal checks](names/m11_exact.json), [HTTP](root_checks/new_leaks_http.json). |
| M11-S1 `9-amino-20(s)-camptothecin` | **NOT FIXED — explicitly accepted over-refusal**; preferred name/ID still reach CHEMBL274070. [Controls](names/alias_loss_controls.json). |
| M11-S1 `il-6ra` | **NOT FIXED — explicitly accepted over-refusal**; preferred name/ID still reach CHEMBL1237022. [Controls](names/alias_loss_controls.json). |
| M11-S1 `TAK-659F` | **NOT FIXED — explicitly accepted over-refusal**; preferred name/ID still reach CHEMBL3979920. [Controls](names/alias_loss_controls.json). |
| M11 distinct-piece lock contention / U+FDFA expansion | **NOT FIXED**, nonblocking performance concern; exact workloads rerun below. [Unique HTTP](cost/isolated_unique_cost_http.json), [Unicode HTTP](cost/isolated_unicode_cost_http.json). |
| M11 supplementary, previously unpromoted `trastuzumab labelled with 89Zr`, `trastuzumab labeled with 89Zr`, `89Zr labeled trastuzumab`, `89Zr conjugated trastuzumab` | **NOT FIXED** — same originator maps as m11; not counted as a newly introduced defect or a separate blocker. [Reused original script](root_checks/fresh_probe.json), [current/previous adjudication](db_ui/adjudication.md). |
| M11 supplementary `99MTc trastuzumab`, `[99MTc] trastuzumab` | **FIXED** — now refuse; bare trastuzumab control still maps. [Reused original script](root_checks/fresh_probe.json). |
| M11 punctuation-only cost overhead | **NOT FIXED as a cost concern** — comparable synthetic normalization overhead remains; no timeout or data error. [Same-data comparison](cost/normalization_cost.json). |

## Cost and nonblocking findings

Historical workloads were rerun sequentially after the other CPU-heavy review jobs finished. Unrelated host activity is uncontrolled; timings are observations, not service-level guarantees or proof of global linear complexity. Query-module counterfactuals use the same current database and remaining modules. [Execution](cost/execution_isolated.json), [reuse manifest](reuse_manifest_root.json).

| Reproduction | Current observation / disposition |
|---|---|
| M5-S3 cubic scan, 250 plain tokens | **FIXED for exact old workload:** 2,224 calls per predicate / 33,880 aggregate characters versus old 31,625 / 10,479,750. [Instrumentation](cost/perf_current.json). |
| Original 999-character plain-answer timeout | **FIXED:** check HTTP 200 in **0.22613 s**; ordinary follower **0.03572 s**. [HTTP](cost/perf_check_http.json). |
| M6/M7 repeated 2,000-piece input `';'.join(['x']*2000)` | **FIXED for exact workload:** current direct-link median **0.16853 s**, historical `9bd7cb4` **2.54663 s**; HTTP check **0.47434 s**, queued EGFR **0.39348 s**, both 200. [Comparison](cost/fresh_cost_comparison.json), [HTTP](cost/fresh_cost_http.json). |
| M8-S1 4,097th cache entry | **FIXED:** 82/82 fill requests create 4,096 distinct pieces; first osimertinib at rollover and retry both HTTP200/CHEMBL3353410/79 trials. Original 7,511-key sweep also completes. [HTTP](cost/cache_boundary_http.json). |
| M10/M11 400 distinct drug-bearing pieces, `';'.join(f'isa x{i:04d}' for i in range(400))` | **NOT FIXED**, inherited cost concern: cold check **3.41276 s**, queued EGFR **3.34385 s**, warm check **0.70656 s**. Resolver calls **400 cold / 0 warm**. [HTTP](cost/isolated_unique_cost_http.json), [instrumentation](cost/unique_piece_cost.json). |
| M11 Unicode expansion, answer `'\ufdfa'*4000` | **NOT FIXED:** 4,000 input characters expand to 72,000 at NFKC; check **4.13419 s**, queued EGFR **4.08618 s**, warm **4.16130 s**, all 200. [HTTP](cost/isolated_unicode_cost_http.json). |
| New repeated matches in one item, `' '.join(['isa']*1000)` (3,999 characters) | Nonblocking measured overhead: direct-link three-sample median **1.05735 s** versus HEAD^ **0.63607 s**. At 499 characters: **0.03516 / 0.03013 s**. No failure. [Inputs/comparison](cost/normalization_cost.json). |
| 3,999-character punctuation workload | Current / HEAD^ direct-link medians **0.34400 / 0.37192 s**. Cached ordinary osimertinib **0.000151 / 0.000119 s**. [Comparison](cost/normalization_cost.json). |
| Disease / ordinary concurrency | Disease: 2,774 Trials + 300 Targets, 30 per list, **18,575 bytes / 77.053 ms**. 24 requests /12 workers: all expected HTTP200 shapes, **842.766 ms** total. These ordinary samples overlap early audit work. [HTTP](root_checks/http_results.json). |

`engine.lock` serializes engine operations (`src/app.py:247-263`), so expensive legal `/api/check` answers delay maps. The 3,999/4,000-character stresses are direct-link or **answer-field** cases; `/api/explore` correctly rejects text over 500 characters. Limits precede normalization (`src/app.py:239-243,258-263`; `src/query.py:116-117,173-177`). No deadlock or invented graph value was observed.

**M12-S1 — new stored-alias over-refusal, nonblocking.** `rad001c` / `RAD001C` now refuses instead of selecting **EVEROLIMUS / CHEMBL1908360**, whereas the exact HEAD^ query module selects it. This is a stored AACT synonym. The new trailing-key rule divides `rad001c` into same-drug key `rad` and isotope-shaped `001c` (`src/query.py:282-286`; `src/textrules.py:289-298`). Raw resolver still returns ALIAS; no wrong centre is drawn. `rad`, `RAD001`, EVEROLIMUS and its ID still work. [Current/previous proof](names/new_alias_regression.json), [independent HTTP](root_checks/independent_m12_http.json).

The 7,511-key sweep has **70** previous-method positives without a current Drug, versus m11's 69; **`rad001c` is the sole additional loss**. Many existing losses are intended tracer/product refusals, so 70 is not a defect count. The explicitly accepted M5-S2, hydroxyethyl rapamycin, `Trastuzumab--vcmmae conjugate`, `9-amino-20(s)-camptothecin`, `il-6ra` and `TAK-659F` refusals remain nonblockers. [Loss-set comparison](names/new_alias_losses.json).

Supplementary attacks are recorded without inflating the blocker count: `[89Z.r]-labelled trastuzumab` leaks with 12/12 trial/sponsor rows while `[89Zr]-labelled trastuzumab` refuses; ordinary labelled-distance forms were already exercised and left unpromoted in m11. Punctuated lexical qualifiers and internal-isotope forms on **already labelled** LUTETIUM OXODOTREOTIDE LU-177 are not additional originator blocker claims. [Attack assessment](attacks/FINDINGS.md), [independent adjudication](db_ui/adjudication.md). Existing blank-submit, unsupported-name, prefixed comma-alias and failure-closed Infinity/parser limitations are retained in the historical tables.

## Standards axis

**Zero documented-standards findings.** Independent review examined `git diff bfcb83d...HEAD` and the latest query/tests patch. No repository AGENTS.md/CONTRIBUTING/coding-standard source was found. The user-supplied evidence-based, no-tracked-edit and m12-only requirements govern this audit. KOA Studio / KhOpenApi original-versus-modified-code comparison is conditional on application changes; no such changes were made. [Independent standards assessment](db_ui/FINDINGS.md).

## Spec axis

**One P1 blocker, M12-B1.** A normalized spelling of the repository's refused tracer alias maps to its originator, with every refusal stage missing it. The exact m11 repairs work, but their same-drug remainder requirement leaves chelator-bearing aliases exposed. Stored-edge, stored-value, direction, cut-notice, no-model and exercised UI safety/state checks pass. Correct relationships around a wrongly chosen centre do not satisfy the refusal guarantee. Accepted over-refusals and cost observations do not determine the verdict. [Independent specification assessment](attacks/FINDINGS.md), [adjudication](db_ui/adjudication.md).

## Integrity and reproduction

Snapshot: **7 retired nodes, 142 retired edges, zero real self-loops and zero live edges with retired endpoints**. All six live node types and all 22 existing group combinations were exercised. Self-loop/unknown-type behavior was tested with an isolated in-memory fixture. [Snapshot](db_ui/db_snapshot_facts.json), [fixture](db_ui/self_loop_unknown.json).

`Engine.ask` uses `use_llm=False` (`src/app.py:180-181`). Explore follows SELECT/read paths; mutation fixtures use memory copies. The application does not globally enforce a read-only SQLite handle, so this is an executed-path/source/hash result, not a database-permission guarantee. Final verification checks **3,731 tracked-file SHA-256 hashes**, HEAD, tracked/staged diffs, DB bytes, report links and owned-port cleanup. [Initial snapshot](integrity_before.json), [final integrity](integrity_final.json). DB SHA-256: `7341c5a7089731f67356da5a588b269d4b69e8e6c4c054acf19aa4ef2837b529`. Existing m12 brief/log files were preserved.

Run from repository root with bytecode disabled and TMP/TEMP/TMPDIR inside the corresponding m12 directory. Shared-port scripts must remain sequential; run benchmarks after other review work ends.

```text
python -B audit_evidence_claims/m12/root_checks/run_all.py
python -B audit_evidence_claims/m12/root_checks/fresh_probe.py
python -B audit_evidence_claims/m12/names/run_round9.py
python -B audit_evidence_claims/m12/names/run_additional.py
python -B audit_evidence_claims/m12/names/run_final_replays.py
python -B audit_evidence_claims/m12/db_ui/run_db.py
python -B audit_evidence_claims/m12/db_ui/run_ui.py
python -B audit_evidence_claims/m12/attacks/focused.py
python -B audit_evidence_claims/m12/attacks/http_probe.py
python -B audit_evidence_claims/m12/root_checks/independent_m12_http.py
python -B audit_evidence_claims/m12/cost/run_isolated.py
```

VERDICT: CHANGES REQUIRED
