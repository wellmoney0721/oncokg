# Independent relation-map review - round 9

Reviewed **`3a362eb4f156ea252301d18507ff0a733d0b601e`**, 2026-11-03 KST, against the supplied round-9 design and original approval bar. **Approval is blocked by reproducible originator leaks that every refusal stage misses.** All seven named M8 findings are fixed for their exact inputs. Four different standalone stored aliases now lose their correct drug maps.

No tracked file was edited. All new scripts, fixtures, logs and this report are under `audit_evidence_claims/m9/`; the pre-existing `brief.md` was preserved. Known **M5-S2** and the stated same-item over-refusal policy are accepted. A correct graph around the wrong selected molecule still fails the approval bar.

## Verification and limits

- **336 passed in 23.63 s**, exit 0: `python -m pytest tests -q -p no:cacheprovider`, with bytecode disabled and temporary files under m9. [Output](root_checks/pytest.txt), [environment/hashes](root_checks/pytest_summary.json).
- Reused all earlier finding reproducers, relocating outputs and owned ports. Root's six inherited HTTP runners and four M6 runners all exit 0; the original M1 HTTP cases, seven original QA demos and M8's 57-request confirmation are included. [Reuse manifest](root_checks/reuse_manifest.json), [six runners](root_checks/execution_http.json), [four runners](root_checks/execution_m6_http.json), [M8 HTTP](root_checks/new_http.json).
- Historical naming coverage includes **13 core scripts, six supplements, all five original M1 name scripts, 113 attack cases and 7,511 unique alias keys**, plus the frozen **1,648-question** no-relink counterfactual. The literal old alias sweep now finishes without the old cache crash. Known obsolete harness calls use the documented M8 adaptations; inert old monkey-patches are not used as evidence for current no-relink behavior. [Name report](names/FINDINGS.md), [manifest](names/reuse_manifest.json), [execution](names/round9_execution.json).
- Reused the distinct M7 attack script: **93 inputs / 10 QA / 44 HTTP requests**. Reused the M8 attack script: **174 inputs / 8 QA**, all **26 Unicode Pd** characters, plus **16 alias/control HTTP requests**. [M7](names/m7_attacks/fresh_results.json), [M8](names/attacks/probe_results.json), [aliases](names/alias_checks/new_http.json).
- Independent graph oracle: **6,469 live centres, 22 relation/direction/type/role combinations, zero errors**. **19/19 DB assertions** pass, including live trial counts, retired endpoints, malformed props, unknown counts, exact score precision and the 1,001-drug chunking fixture. [Oracle](db_ui_cost/db_validate.json), [assertions](db_ui_cost/db_assertions.json).
- **24/24 UI assertions**, all **36 demo callbacks plus six map callbacks** pass. All **36 complete demo responses equal M7 and M8**; all **36 original-CLI HTTP demo responses return 200 and equal direct Engine output**. [DB/UI/demo/cost report](db_ui_cost/FINDINGS.md).
- Fresh attacks cover **146 inputs / 16 QA**, **50 corrected actual HTTP requests**, and ten exact predecessor-query comparisons. Records include resolver output, normalized input, resolver veto, item linker, whole-name result, public linking and map output. An initial wrong QA payload key was a harness error, preserved and corrected before the full rerun; it is not an application finding. Root independently confirmed **54 additional actual HTTP responses** with the original CLI server. [Fresh attacks](attacks/FINDINGS.md), [adaptation](attacks/adaptation.json), [independent HTTP](root_checks/independent_http.json), [lifecycle](root_checks/independent_lifecycle.json).
- UI checks execute actual page JavaScript in a Node VM with controlled DOM/fetch stubs. They verify generated markup, callbacks and stale-response behavior, not browser paint or real-browser exploitation. Served HTML was byte-identical to the worktree. Port 8765 was not used. No clinical interpretation or external pharmacology assumption is needed for the findings below: the repository's own suffix/isotope rules and stored identities supply the controls.

## Blocking findings

### M9-B1 - P1: positive name normalization remains broader than every refusal stage

Exact request: `POST /api/explore` with `{"text":"bevacizumab_awwb"}`.

Actual HTTP 200 draws **BEVACIZUMAB / CHEMBL1201583 / 122 trials**, with no refusal. `bevacizumab__awwb` does the same. The ASCII-hyphen control `bevacizumab-awwb` is correctly refused. `bevacizumab_awwb, osimertinib` still selects the forbidden BEVACIZUMAB centre; the separate valid drug does not authorize that identity.

| Stage | `bevacizumab_awwb` |
|---|---|
| Raw resolver | ALIAS to CHEMBL1201583, no refusal |
| `_resolver_blocked(_fold(text))` | `{}` |
| `_link(_fold(text))` | Drug CHEMBL1201583, no Refused entry |
| `_whole_name(...)` | `None`, supplying no veto |
| Public map / trial QA | Originator map / 12 originator evidence rows |

`Which trials evaluate bevacizumab_awwb?` returns 12 originator rows over HTTP. The hyphen control returns zero. [Independent responses](root_checks/independent_http.json), [stage matrix](attacks/probe_results.json), [additional HTTP](attacks/http_results.json).

**Cause:** the new punctuation fold at **`src/query.py:114-118`** uses `[^\w\s]+`; underscore is a word character in this regex, although Unicode classifies it as connector punctuation. It therefore remains unchanged. The suffix predicate is narrower (`src/textrules.py:156-157`), while the positive key **removes underscore** (`src/textrules.py:339-346`). The key retrieves the stored alias `Bevacizumab awwb`, and `_link` accepts it (`src/query.py:339-354`). Returning no whole-name match is not a refusal (`src/query.py:160-165`). `awwb` is explicitly a known biosimilar suffix in `src/textrules.py:169-173`.

The same representation mismatch also admits **`bevácizumab-awwb`** (U+00E1, and its decomposed equivalent): the guard sees an accented letter outside its ASCII stem pattern, but `canonical_key` removes the accent and accepts the blocked name. Exact predecessor comparisons show these are **newly reported inherited holes**, not a claim that M8's exact repaired input regressed. Additional dotted-suffix variants are retained in the attack evidence, without claiming an exhaustive Unicode proof. [Predicate details](attacks/predicate_details.json), [predecessor comparison](attacks/predecessor_results.json).

**Required outcome:** punctuation/character equivalences that recover a known refused product must not recover its originator through a more permissive positive key. Preserve the bare originator and separately listed valid-drug controls.

### M9-B2 - P1: the punctuation-folded isotope is never checked as an isotope label

**`[89.Zr] trastuzumab`** and **`89:Zr trastuzumab`** each return HTTP 200, **TRASTUZUMAB / CHEMBL1201585 / 13 trials**, no refusal. Both trial questions return **12 originator evidence rows**. Controls `89-Zr trastuzumab`, `[89 Zr] trastuzumab` and `[89Zr] trastuzumab` refuse; bare `trastuzumab` works. [Independent HTTP](root_checks/independent_http.json), [all stages](attacks/probe_results.json).

After edge stripping (`src/query.py:257-260`), the item begins `89.Zr` or `89:Zr`. Its punctuation-folded form is `89-Zr trastuzumab`. `is_isotope_label("89-Zr")` is true under **`src/textrules.py:289-298`**, and the literal folded control is refused. But the folded variant at **`src/query.py:117-118`** reaches only `is_distinct_product` / `is_radiotracer`; **the one- and two-word isotope tests at `123-126` see only the original words**. The narrower full-tracer predicate does not recognize this unbracketed, space-separated form. Positive alias matching erases the punctuation and recovers the stored `89zr-trastuzumab` alias as the unlabelled molecule (`src/textrules.py:339-346`, `src/query.py:339-354`).

The raw resolver, resolver veto and item linker all miss the refusal; whole-name fallback supplies no veto. This is an inherited input hole still present after M8, and violates the added requirement to run the item guards on the punctuation-folded item. [Predicate evidence](attacks/predicate_details.json), [predecessor evidence](attacks/predecessor_results.json).

**Required outcome:** apply the complete item refusal policy, including isotope-label checks, to the permitted folded representation before accepting an originator identity.

### M9-B3 - P1: a known suffix without a hyphen is accepted as the originator alias

**`bevacizumab awwb`** and **`bevacizumab (awwb)`** return HTTP 200, **BEVACIZUMAB / CHEMBL1201583 / 122 trials**, with no refusal. Both trial questions return **12** originator rows. The exact repaired `bevacizumab-(awwb)` and ordinary `bevacizumab-awwb` controls refuse. [Independent HTTP](root_checks/independent_http.json).

The stored alias `Bevacizumab awwb` itself points to the originator ID. The suffix policy recognizes `awwb` but only when the pattern includes a hyphen (`src/textrules.py:156-157,169-173`). Spaces are deliberately preserved by the new punctuation fold (`src/query.py:118`), while edge wrappers are stripped (`257-260`). Thus all refusal stages miss the product distinction; the whole-name shortcut can also return Drug for the exact spaced stored alias (`229-239`). A dictionary hit does not establish product identity when the same suffix is expressly rejected in the control spelling.

This is a **newly reported inherited hole**, distinct from M8-B2's now-fixed interior-wrapper-with-hyphen reproduction. The current design's stored-name tracer exception does not authorize treating this known biosimilar suffix as the original molecule. [Stage and predecessor evidence](attacks/FINDINGS.md).

**Required outcome:** known suffix product names must not draw originator edges merely because they are stored without a hyphen or surrounded by whitespace-separated wrappers.

## Earlier findings - individual FIXED / NOT FIXED dispositions

The **62 carried-forward rows remain 54 FIXED / 8 NOT FIXED** for their exact reproductions. Adding the seven M8 findings below yields **69 rows: 61 FIXED / 8 NOT FIXED**. These counts include repeated qualifications, not 69 independent defects. M2 stopped without a REPORT; its partial role/order fixtures and completed M2b report are covered. Current re-execution, not the previous report's verdict, supplies the dispositions. [Machine-readable matrix](names/historical_findings_matrix.json).

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


### M8

| Finding / exact reproduction | Round 9 disposition |
|---|---|
| M8-B1 `[89 Zr] trastuzumab`, tab/newline/NBSP between mass and element | **FIXED** - no centre; trial/sponsor QA zero. Recorded `radiotracer_guard` honored at `src/query.py:204-207`; two-word labels checked at `125-126`. [Replayed stages](names/attacks/probe_results.json), [HTTP](root_checks/new_http.json). |
| M8-B2 `bevacizumab-(awwb)`, `bevacizumab-[awwb]`, separate-osimertinib variant | **FIXED** - product refused; separate OSIMERTINIB survives; qualified-product QA zero. `src/query.py:114-118`. [Stages](names/attacks/probe_results.json), [HTTP](root_checks/new_http.json). |
| M8-B3 U+2E3A `bevacizumab⸺awwb`; all 26 Unicode Pd characters | **FIXED** - all 26 fold to hyphen and refuse; no originator centre. `src/query.py:101-106`. [All Pd results](names/attacks/unicode_dashes.json), [HTTP](root_checks/new_http.json). |
| M8-S1 4,097th cache entry; original 7,511-key alias sweep | **FIXED** - 82 successful requests fill 4,096 distinct pieces; first `osimertinib` and retry both HTTP 200 / CHEMBL3353410 / 79 trials. Original and adapted alias sweeps finish without cache errors. `src/query.py:187-195`. [Natural HTTP](db_ui_cost/cache_boundary_http.json), [name runs](names/round9_execution.json). |
| M8-S2 `biosimilar, and osimertinib`, `biosimilar; and osimertinib`, `biosimilar and, osimertinib` | **FIXED** - all preserve CHEMBL3353410; the first comma-and form has 12 trial and 12 sponsor QA rows. Carry now requires equal comma/semicolon clause IDs at `src/query.py:300-302`. [HTTP](root_checks/new_http.json), [replayed stages](names/attacks/probe_results.json). |
| M8-S3 `566C`, `9-ac`, `5ac` | **FIXED** - correct CHEMBL1450 / CHEMBL274070 / CHEMBL1489, HTTP 200. `src/query.py:122,196-209`. [Alias HTTP](names/alias_checks/new_http.json). |
| M8-S4 `5.BETA.,20-EPOXY-1,2.ALPHA.,4,7.BETA.` | **FIXED** - PACLITAXEL / CHEMBL428647, HTTP 200. Stored/input punctuation stripped symmetrically at `src/query.py:229-235`. [Alias HTTP](names/alias_checks/new_http.json). |

## Should-fix findings, separate from originator blockers

### M9-S1 - P2, new regressions: four exact standalone stored aliases are now refused

| Exact input | Correct stored drug | Current HTTP result |
|---|---|---|
| `Trastuzumab--vcmmae conjugate` | TRASTUZUMAB VEDOTIN / CHEMBL5315030 | 200, Refused, no centre |
| `Theophylline in dextrose 5% in plastic container` | THEOPHYLLINE / CHEMBL1355736 | 200, Refused, no centre |
| `40-o-(2-hydroxyethyl)-rapamycin` | EVEROLIMUS / CHEMBL1908360 | 200, Refused, no centre |
| `42-o-(2-hydroxyethyl)rapamycin` | EVEROLIMUS / CHEMBL1908360 | 200, Refused, no centre |

Each is an exact unique dictionary alias supplied alone. The exact M8 query module (`ec4eede`), loaded with the same app/rules/data, draws its correct live Drug; preferred-name/ID controls still work. The exact old set of **19 non-M5-S2 lost aliases remains repaired**; these are four other inputs. [Stored identities, old/current stages and ten HTTP requests](names/new_alias_confirmation.json), [independent confirmation of the first three](root_checks/independent_http.json), [old 19 check](names/historical_alias_set_check.json).

For the ADC, punctuation collapse turns the truncated word window into `Trastuzumab-vcmmae`, firing the generic suffix guard. For the chemical-locant names, collapse creates a tracer-like prefix. For theophylline, edge stripping removes `%` (`src/query.py:257-260`), and the new adjacent-word isotope rule reads **`5 in`** as mass/element (`125-126`). All four complete raw spellings have false raw distinct-product/radiotracer predicates; the new item checks create the refusal. The `42-o...` form additionally triggers a recorded resolver tracer veto after cleaning; the item refusal independently suffices. Whole-name recovery then exits because `found` contains Refused (`227-228`). The resolver exception at `196` covers only pieces tokenized as one word, not these complete stored names.

These losses fall outside the user's intended over-refusal allowance because the valid named drug is alone in its item. Preserve its stored ID without weakening the product/tracer controls. The larger alias sweep contains additional isotope/product-bearing names; they are retained in raw evidence but not all asserted to be defects. M5-S2 remains the accepted known exception.

## Demos and cost

All seven original QA demos retain evidence counts **12, 12, 11, 1, 12, 0, 0**. Six complete responses equal original `bfcb83d`; Mvasi differs only in refusal metadata. All 36 page-demo responses equal both M7 and M8. [Original QA comparison](root_checks/http_demo_results.json), [page comparison](db_ui_cost/demo_previous_comparison.json), [actual HTTP demos](db_ui_cost/demo_http.json).

The last timing interval ran after root/name workloads completed and the attack worker paused. Other host activity was uncontrolled; these are observations, not performance guarantees. The old comparator is exact `9bd7cb4` query code with current shared data/rules.

| Exact workload | Observed result |
|---|---|
| Link `';'.join(['x']*2000)`, 3,999 characters, three-sample median | old M7 **1.795619 s**; current **0.152050 s** |
| HTTP `/api/check`, question EGFR, same repeated-x answer | **0.395786 s**, HTTP 200 |
| Ordinary EGFR map queued behind that check | **0.313302 s**, HTTP 200; later ordinary map **0.020716 s** |
| `';'.join(f'isa x{i:04d}' for i in range(400))`, 3,999 chars, cold HTTP check | **3.110653 s**, HTTP 200 |
| Ordinary EGFR map queued behind the cold distinct-piece check | **3.051145 s**, HTTP 200 |
| Same distinct-piece check with warm cache | **0.692193 s**, HTTP 200 |

The original repeated-piece defect is repaired. Instrumentation gives **400 cold / 0 warm resolver calls** for distinct drug pieces, **1 / 0** for repeated drug pieces and **0** for non-drug pieces. Unique legal inputs still hold the shared engine lock for seconds (`src/app.py:247-263`). This is a residual cost qualification, not an established new regression, timeout or deadlock. The cache rollover exception is separately repaired. [Full cost evidence and commands](db_ui_cost/FINDINGS.md), [isolated repeated HTTP](db_ui_cost/isolated_fresh_cost_http.json), [distinct HTTP](db_ui_cost/isolated_unique_cost_http.json).

Disease returns **2,774 Trials + 300 Targets**, 30 from each group, **18,575 bytes in 74.443 ms**. The inherited **24-request / 12-worker** concurrency workload returns expected HTTP 200 shapes in **803.993 ms**. These ordinary measurements overlapped other audit work. [HTTP results](root_checks/http_results.json).

## Standards, integrity and remaining boundaries

No repository AGENTS/CONTRIBUTING/CODING_STANDARDS source was found. The supplied review and no-tracked-edit instructions govern. No application code was changed, so the conditional KOA Studio / KhOpenApi before/after-code comparison does not apply.

The DB snapshot contains **7 retired nodes, 142 retired edges, no self-loops and no live edge with a retired endpoint**. No additional wrong live-edge relationship, direction wording, stored field value, cut notice or generated-markup injection was established in the exercised paths. The refusal guarantee at `src/app.py:74-76` and the UI's product-refusal behavior at `web/try.html:215` remain unfulfilled for M9-B1-B3.

Application QA uses `use_llm=False` (`src/app.py:180-181`); no model was called. DB mutations used isolated fixtures. The application does not globally open SQLite read-only, so this review's no-write conclusion rests on executed paths and hashes rather than a database-permission guarantee.

Final HEAD, tracked/staged diffs, SHA-256 comparison of every initially present tracked file, database hash, owned-port closure and report links are recorded in [integrity_final.json](integrity_final.json). DB SHA-256: `7341c5a7089731f67356da5a588b269d4b69e8e6c4c054acf19aa4ef2837b529`.

Reproduce from the repository root with bytecode disabled. Keep runners that share a port sequential; worker manifests state path/port/instrumentation adaptations.

```text
python -B audit_evidence_claims/m9/root_checks/run_replays.py tests
python -B audit_evidence_claims/m9/root_checks/run_replays.py http
python -B audit_evidence_claims/m9/root_checks/run_m6_http.py m6_http
python -B audit_evidence_claims/m9/root_checks/new_http.py
python -B audit_evidence_claims/m9/root_checks/independent_confirm.py
python -B audit_evidence_claims/m9/names/run_round9.py
python -B audit_evidence_claims/m9/names/m7_attacks/fresh_probe.py
python -B audit_evidence_claims/m9/names/new_alias_confirmation.py
python -B audit_evidence_claims/m9/db_ui_cost/run_db.py
python -B audit_evidence_claims/m9/db_ui_cost/run_ui.py
python -B audit_evidence_claims/m9/attacks/probe.py
python -B audit_evidence_claims/m9/attacks/http_probe.py
```

VERDICT: CHANGES REQUIRED
