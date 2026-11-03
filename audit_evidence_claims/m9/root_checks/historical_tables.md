### M1

| Finding / reproduction | Current result |
|---|---|
| B1 `bevacizumab - awwb`, `89Zr - trastuzumab`, `[89Zr] trastuzumab` | **FIXED** — refusal, no centre. [Original script replay](names/m1_exact/names_product_bypass.json), [HTTP](root_checks/regression_http.json). |
| B2 collaborator called lead: `NCT00200395`, reverse `ORG:genentech` | **FIXED** — Genentech collaborator / Montefiore lead, both directions. `src/app.py:137,160-169`; `web/try.html:142-149`. [DB](db_ui_cost/db_assertions.json), [rendered UI](db_ui_cost/ui_harness_results.json). |
| B3 Investigator called institution: `NCT00754364`, `ORG:armandosantoromd` | **FIXED** — person-specific heading. `web/try.html:143,148`. [DB](db_ui_cost/db_assertions.json), [rendered UI](db_ui_cost/ui_harness_results.json). |
| B4 retire CHEMBL3353410 in memory; query name, ID, EGFR | **FIXED** — name/ID not_found; retired neighbour excluded. `src/app.py:115-118`. [Original HTTP fixture](names/m1_exact/names_retired_http_results.json). |
| Retired Trial included in live Drug count | **FIXED** — centre count and neighbour count/weight 0. `src/app.py:129-132,139,174`. [Fixtures](db_ui_cost/db_fixtures.json). |
| S1 misleading most-evidence wording/order, Disease | **FIXED** — actual start-date/score/count/A–Z sort disclosed and verified. `src/app.py:141-170`; `web/try.html:148-158,231-235`. [Oracle](db_ui_cost/db_validate.json). |
| S2 silent ring cuts: ALDESLEUKIN, Disease, AstraZeneca | **FIXED** — 22/25, 39/3,074, 41/145 drawn disclosed; cut lists say 30. [UI](db_ui_cost/ui_harness_results.json). |
| S3 stale trail after refusal/not-found/server/network error | **FIXED** — state/buttons clear, obsolete back harmless. `web/try.html:213-216,243-244`. [UI](db_ui_cost/ui_harness_results.json). |
| S4 reverse-completed EGFR/KRAS requests and concurrent duplicate EGFR | **FIXED** — latest KRAS stays, duplicate gives one trail entry. `web/try.html:211-214`. [UI](db_ui_cost/ui_harness_results.json). |
| S5 silent ambiguity: Roche, MET, osimertinib EGFR/reversal, Mvasi and bevacizumab | **FIXED for disclosure** — selected reading/alternatives/refusal visible. `src/app.py:95-114`; `web/try.html:222-226`. [Names](names/names_reproduction_results.json). |
| S6 action/class specificity | **FIXED** — specific gloss and original AGONIST/BINDING AGENT/class codes. `web/try.html:162-176`. [UI](db_ui_cost/ui_harness_results.json). |
| S7 start date, sponsor-to-Drug global count/phase, zero-trial Drug | **FIXED** — NCT00200395 start 2003-07-02; osimertinib sponsor 14/global 79/APPROVAL; CHEMBL925 count 0. [DB](db_ui_cost/db_assertions.json), [rendered UI](db_ui_cost/ui_harness_results.json). |
| S8 node/edge props null, list, broken JSON | **FIXED** — 12 original requests and restorations return 200. `src/app.py:211-217`. [Fixtures](db_ui_cost/db_fixtures.json). |
| Hostile labels/titles/IDs/URLs; scheme/host/credential/backslash probes | **FIXED for exercised markup paths** — escaping and HTTPS registry allowlist; browser limitation above. `web/try.html:104,180,199,221-235`. [Assertions](db_ui_cost/ui_assertions.json). |
| Unknown type Other / relation NEWREL | **FIXED** — raw fallback, no undefined tooltip. [UI](db_ui_cost/ui_regressions.json). |
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
| R2 missing sponsor count, Alaunos–ALDESLEUKIN edge, both endpoints and null/list/broken/empty props | **FIXED** — null/zero sort weight; UI unknown, numeric 0 stays 0. `src/app.py:141-146`; `web/try.html:173`. [Fixture](db_ui_cost/db_missing_sponsor_count.json). |
| Bool association score and hidden precision rounding | **FIXED** — bool null/weight 0; exact EGFR/KRAS decimal values retained. [DB](db_ui_cost/db_score_fixture.json), [UI](db_ui_cost/ui_regressions.json). |
| Embedded multi-ID `Sharedbrand company` fixture | **FIXED** — Roche disclosed alongside selected AstraZeneca. `src/app.py:97-102`. [Fixture](names/names_boundary_details.json). |
| Missing/unknown SPONSORS role and equal-weight A–Z | **FIXED** — neutral role wording, both directions/types; ordering verified. [DB/UI](db_ui_cost/db_assertions.json). |
| Trial phases='PHASE2' render exception, four entry routes | **FIXED** — caught error, cleared trail, recovery/stale suppression. [Callbacks](db_ui_cost/ui_m3_checks.json). |
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
| M4 no-relink QA assessment | **FIXED / retained** — exact frozen 1,648-input counterfactual, 64 identical / 1,560 metadata-only / 24 semantic differences / 0 errors; adapted matcher target is `_link`. [Result](names/adapted_frozen_qa_relink_sweep.json). |
| M3/M4 blank/whitespace form | **NOT FIXED**, unchanged usability limit: no request, previous view stays. `web/try.html:241`. [UI](db_ui_cost/ui_m3_checks.json). |
| M3/M4 positive/negative Infinity fixture | **NOT FIXED**, unchanged failure closed: controlled HTTP 400, no invalid value drawn, none in snapshot. `src/app.py:207-208,264-269`. [Fixture](db_ui_cost/db_numeric_fixture.json). |
| Repeated lowercase-ID/name and raw request qualifications | **NOT FIXED**, same individual M1 rows above. |

### M5 and M6

| Finding / reproduction | Current result |
|---|---|
| M5-B1 reported attached slash/pipe and internal both-sides-glued attack | **FIXED** — `bevacizumab-awwb/ osimertinib` and `bevacizumab - awwb/osimertinib` select only OSIMERTINIB and expose refusal; pipe counterparts too. [HTTP](root_checks/m5_http.json), [m6 replay](root_checks/confirm_http.json). |
| M5-B2 `liposomal and nanoparticle formulation of doxorubicin`, plural/sustained-release | **FIXED** — forward qualifier carry refuses product; QA 0. [HTTP](root_checks/m5_http.json). |
| M5-S1 `biosimilar anastrozole, Arimidex`; `biosimilar Prolia, xgeva` | **FIXED** — separate aliases survive; 2/3 trial rows. [HTTP](root_checks/cross_item_http.json). |
| M5-S1 `Erlotinib, hydrochloride biosimilar bevacizumab`, semicolon | **FIXED** — original qualified comma/semicolon inputs preserve CHEMBL553; the simplified comma-list M7 regression is also repaired. [Exact HTTP](root_checks/m5_http.json), [M7 controls](names/historical_focus.json). |
| M5-S2 Pegylated interferon alfa-2a | **NOT FIXED — accepted known over-refusal**, not a new blocker. Canonical name/ID work. [HTTP](root_checks/m5_http.json). |
| M5-S3 all-substring cubic work / 999-character plain-answer timeout | **FIXED for exact previous cost cases** — bounded predicate work and original plain-answer requests complete. Repeated-piece overhead also repaired; the cache-boundary failure is now also repaired (M8-S1 below). [Original HTTP](root_checks/perf_check_http.json), [current instrumentation](db_ui_cost/perf_current.json). |
| M6-B1 interior slash/pipe | **FIXED** — separate osimertinib retained; forbidden originator absent from QA. [Exact HTTP](root_checks/confirm_http.json), [39-case matrix](names/focused_matrix.json). |
| M6-B2 U+3002 suffix punctuation, trailing em dash/hyphen, leading hyphen | **FIXED** — all four original edge-punctuation inputs refuse, as do trial/sponsor QA. [Exact HTTP](root_checks/confirm_http.json), [current focused stages](names/historical_focus.json). |
| M6-B2 supplementary bracketed/Unicode variants | **FIXED** — whole-product wrappers `(bevacizumab-awwb)` / `[bevacizumab-awwb]` and the previously reported Unicode hyphens now refuse; question-mark and quoted shortcut cases also refuse. [Historical matrix](names/historical_focus.json), [m7 attack HTTP](names/m7_attacks/http_results.json). |
| M6-B3 `doxorubicin (nanoparticle and liposomal formulation)` / `bevacizumab (investigational and biosimilar)` | **FIXED** — both parenthesized reversed qualifiers produce no centre or QA evidence. [Exact HTTP](root_checks/carry_http.json), [stages](names/historical_focus.json). |
| M6 non-parenthetical reversed-qualifier supplement | **NOT FIXED as original expectation; accepted current item-policy consequence** — `doxorubicin in nanoparticle and liposomal formulations` still selects doxorubicin after listing-word separation. [Exact HTTP](root_checks/reverse_http.json). |
| M6-S1 six complete stored aliases returning another Drug ID | **FIXED for all six bare inputs** — intended stored IDs retained. [Current stages](names/historical_focus.json), [HTTP](root_checks/alias_http.json). |
| M6-S1 prefixed QA using those comma-containing names | **NOT FIXED — current whole-input-only design consequence**. ENDOSTATIN prefixed QA still selects CHEMBL4297747 with 2 rows; Rapamycin prefixed QA CHEMBL413 with 5 rows. [Exact HTTP](root_checks/alias_http.json), [direct QA](names/historical_focus.json). |
| M6 associated lone stored-alias losses | **FIXED for all 19 non-M5-S2 historical lost aliases** — slash/joiner names restored; known M5-S2 still refuses. Four additional standalone stored-alias regressions are reported below. [Exact previous/current alias comparison](names/alias_regressions.json), [complete current sweep](names/adapted_names_m5_summary.json). |
| M6 split_2000 / many-piece cost control | **FIXED for exact repeated-piece cost control** — current resolver skips no-drug pieces and deduplicates; the previous per-piece delay is gone. [Exact stress replay](db_ui_cost/cost_stress.json), [old/current samples](db_ui_cost/isolated_fresh_cost_comparison.json). |

### M7

| Finding / reproduction | Current result |
|---|---|
| M7-B1 Whole-name refusal bypass: `bevacizumab-awwb?`, `bevacizumab-awwb!`, quoted form | **FIXED** — All return refusal/no centre; trial and sponsor QA zero. [Current stages](names/historical_focus.json), [original m7 HTTP replay](names/m7_attacks/http_results.json). |
| M7-B2 Wrappers and Unicode hyphens: `(bevacizumab-awwb)`, `[bevacizumab-awwb]`, U+2011 suffix and bio-similar | **FIXED** — All named inputs refuse after shared normalization and edge stripping; no originator QA. [Stages](names/historical_focus.json), [HTTP](names/m7_attacks/http_results.json). |
| M7-B3 Whitespace isotope: `89Zr trastuzumab` | **FIXED** — No centre; both QA forms have zero evidence. [Stages](names/historical_focus.json), [HTTP](names/m7_attacks/http_results.json). |
| M7-S1 Canonical equality too broad: `Erlotinib, hydrochloride`, `osimertinib,mesylate`, `is a` | **FIXED** — Respectively CHEMBL553, CHEMBL3353410 and not_found; actual exact aliases retain intended IDs. [Current controls](names/historical_focus.json), [HTTP](names/m7_attacks/http_results.json). |
| M7-S2 Lone exact stored names: `(E/Z)-AFATINIB`, `RO 09-1978/000`, `Anusol plus hc` and 19-alias set | **FIXED** — All 19 old non-M5-S2 losses restored; three named controls select CHEMBL1173655 / CHEMBL1773 / CHEMBL389621. [Exact previous/current comparison](names/alias_regressions.json), [HTTP](names/alias_http.json). |
| M7-S3 Repeated identical-piece full resolver cost / queued ordinary map | **FIXED** — Exact old repeated-x controls and corresponding requests complete with materially reduced work. The cache failure is now repaired (M8-S1 below); unique-piece cost is reported below. [Cost replay](db_ui_cost/cost_stress.json), [comparison](db_ui_cost/isolated_fresh_cost_comparison.json), [HTTP](db_ui_cost/isolated_fresh_cost_http.json). |

