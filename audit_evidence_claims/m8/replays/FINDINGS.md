# Round 8 historical reproduction report

HEAD `ec4eede`. The exact named m1–m7 originator leaks and m7 list/name regressions are FIXED. Historical usability and explicit current-design qualifications remain individually recorded below. Newly found valid-alone over-refusals and a cache rollover exception are separate from those historical dispositions.

## Execution, provenance and limits

The source reports exist for m1 and m3–m7; `m2/REPORT.md` is absent. M2b findings are preserved in m3–m7 disposition tables and exercised by the inherited m2 scripts. This table retains every row of m7’s historical matrix and appends all six m7 findings.

- [Reuse manifest](reuse_manifest.json): 30 original Python scripts relocated with output-path and fixed-port changes only. Own HTTP port was 8913; server lifecycles ended.
- [13-script run](replay_execution.json): 12 exit 0; the exact 7,511-key sweep aborts on the new application cache defect, preserved in [traceback](names_m5_attack_stdout.txt). A [documented per-case exception-record/retry adaptation](alias_sweep_adaptation.json) completes the exact 113 cases and all 7,511 keys, with one recorded exception and zero wrong-ID results. [Full adapted result](adapted_names_m5_attack.json).
- [Six original supplements](supplement_execution.json) exit 0: includes 106-case / 8-QA fresh probe and 11 reversed-qualifier probes. [All five original m1 scripts](m1_exact/execution.json) also exit 0, including unchanged-CLI HTTP and isolated retired-node HTTP fixture.
- [Old m7 focused script](m7_focus.py.stdout.txt) initially fails because `_whole_name` now needs `found`. [Mechanical signature adaptation](m7_focus_adaptation.json) preserves all 23 inputs and passes every expected centre; [result](adapted_m7_focus.json). The separate [26-case m6/m7 matrix](historical_focus.json) adds all newly repaired m7 findings and four prefixed-QA controls.
- Historical no-relink scripts patch `link_entities` and are now inert counterfactuals; they are rerun but not used as evidence of no-relink. The inherited meaningful adaptation patches `_link` and reuses the exact frozen 1,648-input m5 corpus: **64 identical / 1,560 metadata-only / 24 semantic / 0 errors**. [Result](adapted_frozen_qa_relink_sweep.json).
- Coverage: 62 original name inputs + 14 probes; 30 boundary inputs + 21 joiner aliases; 45 attacks + 37 QA + 2,584 multi-token aliases; 113 attacks + 7,511 unique alias keys; 49 confirmation inputs; 13 cross-item controls. The original 39-case finding matrix has only the accepted M5-S2 mismatch. [Matrix](focused_matrix.json).
- Parent DB replays: 6,469 centres, 22 relation/direction/type/role combinations, zero oracle errors; [19/19 assertions](../db_ui/db_assertions.json). UI sibling: [24/24 assertions](../demos_cost/ui_assertions.json), [36/36 exact demo responses](../demos_cost/ui_demo_compare.json). Generated markup/Node VM evidence is not browser paint or exploit execution certification. All timings outside the cost worker’s isolated run may include concurrent audit workload.

## Every earlier finding: current disposition

### M1

| Finding / reproduction | Current result |
|---|---|
| B1 `bevacizumab - awwb`, `89Zr - trastuzumab`, `[89Zr] trastuzumab` | **FIXED** — refusal, no centre. [Original script replay](m1_exact/names_product_bypass.json), [HTTP](../root_checks/regression_http.json). |
| B2 collaborator called lead: `NCT00200395`, reverse `ORG:genentech` | **FIXED** — Genentech collaborator / Montefiore lead, both directions. `src/app.py:137,160-169`; `web/try.html:142-149`. [DB/UI](../db_ui/db_assertions.json). |
| B3 Investigator called institution: `NCT00754364`, `ORG:armandosantoromd` | **FIXED** — person-specific heading. `web/try.html:143,148`. [DB/UI](../db_ui/db_assertions.json). |
| B4 retire CHEMBL3353410 in memory; query name, ID, EGFR | **FIXED** — name/ID not_found; retired neighbour excluded. `src/app.py:115-118`. [Original HTTP fixture](m1_exact/names_retired_http_results.json). |
| Retired Trial included in live Drug count | **FIXED** — centre count and neighbour count/weight 0. `src/app.py:129-132,139,174`. [Fixtures](../db_ui/db_fixtures.json). |
| S1 misleading most-evidence wording/order, Disease | **FIXED** — actual start-date/score/count/A–Z sort disclosed and verified. `src/app.py:141-170`; `web/try.html:148-158,231-235`. [Oracle](../db_ui/db_validate.json). |
| S2 silent ring cuts: ALDESLEUKIN, Disease, AstraZeneca | **FIXED** — 22/25, 39/3,074, 41/145 drawn disclosed; cut lists say 30. [UI](../demos_cost/ui_harness_results.json). |
| S3 stale trail after refusal/not-found/server/network error | **FIXED** — state/buttons clear, obsolete back harmless. `web/try.html:213-216,243-244`. [UI](../demos_cost/ui_harness_results.json). |
| S4 reverse-completed EGFR/KRAS requests and concurrent duplicate EGFR | **FIXED** — latest KRAS stays, duplicate gives one trail entry. `web/try.html:211-214`. [UI](../demos_cost/ui_harness_results.json). |
| S5 silent ambiguity: Roche, MET, osimertinib EGFR/reversal, Mvasi and bevacizumab | **FIXED for disclosure** — selected reading/alternatives/refusal visible. `src/app.py:95-114`; `web/try.html:222-226`. [Names](names_reproduction_results.json). |
| S6 action/class specificity | **FIXED** — specific gloss and original AGONIST/BINDING AGENT/class codes. `web/try.html:162-176`. [UI](../demos_cost/ui_harness_results.json). |
| S7 start date, sponsor-to-Drug global count/phase, zero-trial Drug | **FIXED** — NCT00200395 start 2003-07-02; osimertinib sponsor 14/global 79/APPROVAL; CHEMBL925 count 0. [DB/UI](../db_ui/db_assertions.json). |
| S8 node/edge props null, list, broken JSON | **FIXED** — 12 original requests and restorations return 200. `src/app.py:211-217`. [Fixtures](../db_ui/db_fixtures.json). |
| Hostile labels/titles/IDs/URLs; scheme/host/credential/backslash probes | **FIXED for exercised markup paths** — escaping and HTTPS registry allowlist; browser limitation above. `web/try.html:104,180,199,221-235`. [Assertions](../demos_cost/ui_assertions.json). |
| Unknown type Other / relation NEWREL | **FIXED** — raw fallback, no undefined tooltip. [UI](../demos_cost/ui_regressions.json). |
| All three / everything documentation overclaims | **FIXED** — All of them / a capped list per relation. `src/app.py:5-11`. |
| Silent 500-character cut: `"x"*500 + " osimertinib"`, `"osimertinib " + "x"*600` | **FIXED** — explicit HTTP 400, no partial map. `src/app.py:239-243`. [HTTP](../root_checks/http_results.json). |
| Lowercase IDs / Investigator names: nct00200395, chembl3353410, Armando Santoro Md | **NOT FIXED**, unchanged usability limit. [Controls](names_unsupported_forms.json). |
| Raw list/null/malformed JSON/oversized-body errors | **NOT FIXED**, unchanged controlled 400 exposing parse/attribute details; subsequent valid requests succeed. `src/app.py:237-239,267-269`. [HTTP](../root_checks/http_results.json). |
### M2b

| Finding / reproduction | Current result |
|---|---|
| R1 `osimertinib and generic version of bevacizumab`, reverse/comma, trial/sponsor QA | **FIXED** — only separate osimertinib; correct evidence. [HTTP](../root_checks/regression_http.json), [supplement](../root_checks/supplemental_http.json). |
| R1 tracer/oral-product collateral refusal, both orders | **FIXED** — `[89Zr] trastuzumab and osimertinib` and `osimertinib and oral azacitidine` retain osimertinib. [Names](names_regressions.json). |
| Inherited `What is the generic version of bevacizumab?` | **FIXED** — refusal, no centre; also M3-B2. [HTTP](../root_checks/supplemental_http.json). |
| R2 missing sponsor count, Alaunos–ALDESLEUKIN edge, both endpoints and null/list/broken/empty props | **FIXED** — null/zero sort weight; UI unknown, numeric 0 stays 0. `src/app.py:141-146`; `web/try.html:173`. [Fixture](../db_ui/db_missing_sponsor_count.json). |
| Bool association score and hidden precision rounding | **FIXED** — bool null/weight 0; exact EGFR/KRAS decimal values retained. [DB](../db_ui/db_score_fixture.json), [UI](../demos_cost/ui_regressions.json). |
| Embedded multi-ID `Sharedbrand company` fixture | **FIXED** — Roche disclosed alongside selected AstraZeneca. `src/app.py:97-102`. [Fixture](names_boundary_details.json). |
| Missing/unknown SPONSORS role and equal-weight A–Z | **FIXED** — neutral role wording, both directions/types; ordering verified. [DB/UI](../db_ui/db_assertions.json). |
| Trial phases='PHASE2' render exception, four entry routes | **FIXED** — caught error, cleared trail, recovery/stale suppression. [Callbacks](../demos_cost/ui_m3_checks.json). |
| Residual module wording / successful-input truncation | **FIXED** — individual M1 rows above. |
### M3 and M4

| Finding / reproduction | Current result |
|---|---|
| M3-B1 `paclitaxel with albumin bound nanoparticles`, formulation variant, `generic version with bevacizumab` | **FIXED** — no originator centre/evidence. [HTTP](../root_checks/supplemental_http.json), [names](names_new_boundaries.json). |
| M3-B2 leading generic-version question | **FIXED** — full qualified drug refused. [HTTP](../root_checks/supplemental_http.json). |
| M3 comma collateral refusal: osimertinib with separately listed liposomal/biosimilar drug; reversals/QA | **FIXED** — separate osimertinib retained, 12 trial rows. [HTTP](../root_checks/supplemental_http.json). |
| M3 bare erlotinib hydrochloride / long paclitaxel-poliglumex name; nested-parent re-link | **FIXED / retained** — correct complete IDs; no nested parent; explicit separate parent survives. [Names](names_attack.json). |
| M4-B1 wrong shortest-span tie: `osimertinib with generic version of bevacizumab`, reversal/added a | **FIXED under revised design** — both same-item drugs refused; zero qualified-drug QA evidence. [HTTP](../root_checks/attack_http.json). |
| M4-B1 semicolon and fullwidth-comma variants | **FIXED** — separate osimertinib retained. [Separators](names_separator_checks.json). |
| M4-B2 long qualified poliglumex / `generic version of the monoclonal antibody bevacizumab` | **FIXED** — refused; bare long-name control preserved. [HTTP](../root_checks/attack_http.json). |
| M4-B3 consumed qualifier: biosimilar version / liposomal formulation / albumin-bound / two-product combination | **FIXED** — no parent hit/evidence. [Names](names_attack.json), [HTTP](../root_checks/attack_http.json). |
| M4 target/company collateral refusal: EGFR or AstraZeneca beside biosimilar bevacizumab, reverse/with controls | **FIXED** — target/company retained; drug refusal disclosed. [HTTP](../root_checks/m5_http.json). |
| M4 no-relink QA assessment | **FIXED / retained** — exact frozen 1,648-input counterfactual, 64 identical / 1,560 metadata-only / 24 semantic differences / 0 errors; adapted matcher target is `_link`. [Result](adapted_frozen_qa_relink_sweep.json). |
| M3/M4 blank/whitespace form | **NOT FIXED**, unchanged usability limit: no request, previous view stays. `web/try.html:241`. [UI](../demos_cost/ui_m3_checks.json). |
| M3/M4 positive/negative Infinity fixture | **NOT FIXED**, unchanged failure closed: controlled HTTP 400, no invalid value drawn, none in snapshot. `src/app.py:207-208,264-269`. [Fixture](../db_ui/db_numeric_fixture.json). |
| Repeated lowercase-ID/name and raw request qualifications | **NOT FIXED**, same individual M1 rows above. |
### M5 and M6

| Finding / reproduction | Current result |
|---|---|
| M5-B1 reported attached slash/pipe and internal both-sides-glued attack | **FIXED** — `bevacizumab-awwb/ osimertinib` and `bevacizumab - awwb/osimertinib` select only OSIMERTINIB and expose refusal; pipe counterparts too. [HTTP](../root_checks/m5_http.json), [m6 replay](../root_checks/confirm_http.json). |
| M5-B2 `liposomal and nanoparticle formulation of doxorubicin`, plural/sustained-release | **FIXED** — forward qualifier carry refuses product; QA 0. [HTTP](../root_checks/m5_http.json). |
| M5-S1 `biosimilar anastrozole, Arimidex`; `biosimilar Prolia, xgeva` | **FIXED** — separate aliases survive; 2/3 trial rows. [HTTP](../root_checks/cross_item_http.json). |
| M5-S1 `Erlotinib, hydrochloride biosimilar bevacizumab`, semicolon | **FIXED** — original qualified comma/semicolon inputs preserve CHEMBL553; the simplified comma-list M7 regression is also repaired. [Exact HTTP](../root_checks/m5_http.json), [M7 controls](historical_focus.json). |
| M5-S2 Pegylated interferon alfa-2a | **NOT FIXED — accepted known over-refusal**, not a new blocker. Canonical name/ID work. [HTTP](../root_checks/m5_http.json). |
| M5-S3 all-substring cubic work / 999-character plain-answer timeout | **FIXED for exact previous cost cases** — bounded predicate work and original plain-answer requests complete. Repeated-piece overhead also repaired; new cache-boundary failure is recorded separately below. [Original HTTP](../root_checks/perf_check_http.json), [current instrumentation](../demos_cost/perf_current.json). |
| M6-B1 interior slash/pipe | **FIXED** — separate osimertinib retained; forbidden originator absent from QA. [Exact HTTP](../root_checks/confirm_http.json), [39-case matrix](focused_matrix.json). |
| M6-B2 U+3002 suffix punctuation, trailing em dash/hyphen, leading hyphen | **FIXED** — all four original edge-punctuation inputs refuse, as do trial/sponsor QA. [Exact HTTP](../root_checks/confirm_http.json), [current focused stages](historical_focus.json). |
| M6-B2 supplementary bracketed/Unicode variants | **FIXED** — parenthesized/bracketed suffixes and folded Unicode-hyphen cases now refuse; question-mark and quoted shortcut cases also refuse. [Historical matrix](historical_focus.json), [m7 attack HTTP](../m7_attacks/http_results.json). |
| M6-B3 `doxorubicin (nanoparticle and liposomal formulation)` / `bevacizumab (investigational and biosimilar)` | **FIXED** — both parenthesized reversed qualifiers produce no centre or QA evidence. [Exact HTTP](../root_checks/carry_http.json), [stages](historical_focus.json). |
| M6 non-parenthetical reversed-qualifier supplement | **NOT FIXED as original expectation; accepted current item-policy consequence** — `doxorubicin in nanoparticle and liposomal formulations` still selects doxorubicin after listing-word separation. [Exact HTTP](../root_checks/reverse_http.json). |
| M6-S1 six complete stored aliases returning another Drug ID | **FIXED for all six bare inputs** — intended stored IDs retained. [Current stages](historical_focus.json), [HTTP](../root_checks/alias_http.json). |
| M6-S1 prefixed QA using those comma-containing names | **NOT FIXED — current whole-input-only design consequence**. ENDOSTATIN prefixed QA still selects CHEMBL4297747 with 2 rows; Rapamycin prefixed QA CHEMBL413 with 5 rows. [Exact HTTP](../root_checks/alias_http.json), [direct QA](historical_focus.json). |
| M6 associated lone stored-alias losses | **FIXED for all 19 non-M5-S2 historical lost aliases** — slash/joiner names restored; known M5-S2 still refuses. The current sweep separately records new isotope-token over-refusals. [Exact previous/current alias comparison](alias_regressions.json), [complete current sweep](adapted_names_m5_summary.json). |
| M6 split_2000 / many-piece cost control | **FIXED for exact repeated-piece cost control** — current resolver skips no-drug pieces and deduplicates; the previous per-piece delay is gone. [Exact stress replay](../demos_cost/cost_stress.json), [old/current samples](../demos_cost/fresh_cost_comparison.json). |
### M7

| Finding / reproduction | Current result |
|---|---|
| M7-B1 Whole-name refusal bypass: `bevacizumab-awwb?`, `bevacizumab-awwb!`, quoted form | **FIXED** — All return refusal/no centre; trial and sponsor QA zero. [Current stages](historical_focus.json), [original m7 HTTP replay](../m7_attacks/http_results.json). |
| M7-B2 Wrappers and Unicode hyphens: `(bevacizumab-awwb)`, `[bevacizumab-awwb]`, U+2011 suffix and bio-similar | **FIXED** — All named inputs refuse after shared normalization and edge stripping; no originator QA. [Stages](historical_focus.json), [HTTP](../m7_attacks/http_results.json). |
| M7-B3 Whitespace isotope: `89Zr trastuzumab` | **FIXED** — No centre; both QA forms have zero evidence. [Stages](historical_focus.json), [HTTP](../m7_attacks/http_results.json). |
| M7-S1 Canonical equality too broad: `Erlotinib, hydrochloride`, `osimertinib,mesylate`, `is a` | **FIXED** — Respectively CHEMBL553, CHEMBL3353410 and not_found; actual exact aliases retain intended IDs. [Current controls](historical_focus.json), [HTTP](../m7_attacks/http_results.json). |
| M7-S2 Lone exact stored names: `(E/Z)-AFATINIB`, `RO 09-1978/000`, `Anusol plus hc` and 19-alias set | **FIXED** — All 19 old non-M5-S2 losses restored; three named controls select CHEMBL1173655 / CHEMBL1773 / CHEMBL389621. [Exact previous/current comparison](alias_regressions.json), [HTTP](alias_http.json). |
| M7-S3 Repeated identical-piece full resolver cost / queued ordinary map | **FIXED** — Exact old repeated-x controls and corresponding requests complete with materially reduced work. New distinct-drug workload and cache failure are separate. [Cost replay](../demos_cost/cost_stress.json), [comparison](../demos_cost/fresh_cost_comparison.json), [HTTP](../demos_cost/fresh_cost_http.json). |

## New failures discovered by the historical scripts

### Valid stored aliases newly refused or lost

`566C` (ATOVAQUONE / CHEMBL1450), `9-ac` (9-AMINOCAMPTOTHECIN / CHEMBL274070), and `5ac` (AZACITIDINE / CHEMBL1489) now return no centre with Refused metadata. They are uniquely stored aliases, select their correct nodes with the exact previous query module, and their canonical IDs still draw live nodes. These are valid names alone in their input, not an intentionally dropped drug sharing a qualified item. [Exact previous-module comparison and controls](alias_regressions.json).

`src/query.py:112-113` now treats any token accepted by `is_isotope_label` as a qualifying tracer; `_link` removes edge punctuation (`240-242`) before that predicate. `_whole_name` refuses to rescue any item that produced a refusal (`208-212`). The new broad token check therefore also covers code-like aliases; the source dictionary supplies a concrete stored-name premise rather than an external pharmacology inference. Separately, `5.BETA.,20-EPOXY-1,2.ALPHA.,4,7.BETA.` (CHEMBL428647) returns **not_found with no Refused hit**. It is a different exact-name failure: `_whole_name` removes its terminal period with `text.strip(" ?!.")` at `src/query.py:210`, then compares the resulting name against the unstripped stored alias at `215-216`. The exact previous query module accepts it and its canonical ID still works. This is not an isotope-token refusal. [Separate stored-name control](alias_regressions.json).

The same 7,511-key sweep has 23 formerly linked aliases with no current Drug: accepted M5-S2, the four controls above, and 18 isotope-bearing names. The latter need product policy interpretation and are not all called defects here. Every one of the 19 non-M5-S2 losses reported at m7 is restored. No current wrong-ID result appears in this particular unique-key sweep. [Complete list](adapted_names_m5_summary.json).

### Resolver cache clears the value before reading it

The original alias sweep aborts at alias index 4,071 on `Gallium gozetotide ga-68`. Source `src/query.py:180-182` clears `_resolve_cache` when it grows past 4,096, then immediately accesses `_resolve_cache[piece]`. The exception is `KeyError`, and the recorded cache size after failure is 0. This is an application failure from a natural sequence, not a harness-signature issue. A catch-and-retry-only audit adaptation preserves the exception, then completes every original input after the application emptied its cache. [Original traceback](names_m5_attack_stdout.txt), [recorded failure](adapted_names_m5_summary.json), [separate actual HTTP confirmation](../demos_cost/cache_boundary_http.json).

## Reproduction commands

```text
python -B audit_evidence_claims/m8/replays/run_all.py
python -B audit_evidence_claims/m8/replays/adapted_names_m5_attack.py
python -B audit_evidence_claims/m8/replays/adapted_m7_focus.py
python -B audit_evidence_claims/m8/replays/historical_focus.py
python -B audit_evidence_claims/m8/replays/alias_regressions.py
```

All new files are below m8; no application or tracked file was edited. The earlier scripts’ old-revision comparisons isolate the named methods or query module, while keeping current surrounding data/code. They are not claimed to recreate the entire old application.
