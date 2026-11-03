# Independent relation-map review — round 8

Reviewed **`ec4eede`**, 2026-11-03 KST, against the supplied m8 design and the unchanged approval bar. **Approval is blocked by three reproduced originator-leak mechanisms.** The exact named m7 blockers are repaired, but `[89 Zr] trastuzumab` is a new regression; internal suffix wrappers and omitted Unicode dashes still evade the three-stage pipeline. Passing graph checks and demos do not establish that the selected identity is safe.

All new artifacts are under `audit_evidence_claims/m8/`; no tracked file was changed. Known **M5-S2** and explicitly intended same-item over-refusal are accepted. Loss of a valid drug alone in its item is reported separately, as requested.

## Verification and reproduction boundaries

- **334 passed in 33.83 s**, exit 0: `python -m pytest tests -q -p no:cacheprovider`. Bytecode disabled and temporary files confined to m8. [Test output](root_checks/pytest.txt), [environment and hashes](root_checks/pytest_summary.json).
- Earlier reproducers were **reused**, with output relocation/port changes documented. Ten inherited CLI HTTP runners completed successfully; the original m1 HTTP cases and seven QA demos are included. [Manifest](root_checks/reuse_manifest.json), [six runners](root_checks/execution_http.json), [four m6 runners](root_checks/execution_m6_http.json).
- The inherited name suite includes **13 scripts**, **six supplements**, **all five original m1 name scripts**, the **113-case / 7,511-key sweep**, and the frozen **1,648-question** no-relink comparison. One original alias sweep failed on a real application cache exception; the failure is preserved, and a separately documented catch-and-retry adaptation completed all inputs while recording the exception. This is not reported as an all-green replay. [Name replay report](replays/FINDINGS.md).
- The m7 attack script was rerun: **93 inputs, ten QA questions, 44 actual HTTP requests**. Its old `_whole_name` call first failed because the signature changed; the recorded mechanical adaptation supplies `found`, without changing inputs. Its old raw stage calls do not apply current NFKC normalization; current public-linker/map results determine dispositions. [Adaptation](m7_attacks/adaptation.json), [original failure](m7_attacks/signature_failure.txt), [results](m7_attacks/fresh_results.json), [HTTP](m7_attacks/http_results.json).
- Independent graph oracle: **6,469 live centres, 22 relation/direction/type/role combinations, zero stored-row mismatches**. Seven DB commands completed; **19/19 assertions** pass. Retired/malformed/numeric mutations use isolated in-memory fixtures, including the **1,001-Drug** count-chunk test. [Execution](db_ui/execution.json), [oracle](db_ui/db_validate.json), [assertions](db_ui/db_assertions.json).
- **36/36 complete page-demo responses equal m7**, all **36 demo callbacks plus six map callbacks** pass, and **24/24 UI assertions** pass. An original CLI server also returned all 36 demo responses identically over HTTP. [Demo/UI/cost report](demos_cost/FINDINGS.md).
- Fresh attacks: **174 distinct map inputs and eight QA questions**, exact prior-query-module comparison, **26 Unicode Pd characters**, and seven focused alias checks. Root independently confirmed **57 new HTTP requests** and **16 alias/control HTTP requests**, all HTTP 200 (including erroneous maps and refusals). [Stage/predecessor evidence](attacks/probe_results.json), [new HTTP](root_checks/new_http.json), [alias HTTP](alias_checks/new_http.json).
- UI scripts use Node VM with controlled DOM/fetch stubs. They verify generated markup, callbacks, escaping and response ordering; they do **not** certify browser paint/layout or browser-executed XSS behavior. The original application served worktree-identical HTML over HTTP. No use of port 8765.

## Blocking findings

### M8-B1 — P1, new regression: the resolver refuses a tracer, but its refusal is lost

Exact request: `POST /api/explore` with `{"text":"[89 Zr] trastuzumab"}`.

Actual HTTP 200 draws **TRASTUZUMAB / CHEMBL1201585**, **13 trials**, `also:[]`. There is no separately accepted originator mention.

| Stage/control | Observed result |
|---|---|
| `/api/resolve` | `BLOCKED_CLASS_TERM`, `radiotracer_guard`, no drug ID; cleaned component is `trastuzumab` |
| `_resolver_blocked` after input normalization | `{}` |
| `_link` | Drug / CHEMBL1201585 |
| `_whole_name` | `None`; the unsafe item-linker result survives |
| Exact previous query module, `9bd7cb4` | Refused; no centre |
| `[89Zr] trastuzumab`, `89Zr trastuzumab` | Correctly refused |
| Bare `trastuzumab` | Correctly draws the unlabelled drug |

`Which trials evaluate [89 Zr] trastuzumab?` returns **12 originator evidence rows** over HTTP, first `NCT00016367|EVALUATES|CHEMBL1201585|NCT00016367`. The bracket-without-space control returns zero. Sponsor QA independently returns 12 rows in the direct engine probe. Tab, newline and NBSP between the isotope mass and element reproduce the same new regression. [HTTP](root_checks/new_http.json), [exact predecessor/stages](attacks/probe_results.json), [detailed analysis](attacks/FINDINGS.md).

**Cause:** `src/query.py:187-190` re-tests the cleaned component instead of honoring the resolver's recorded `radiotracer_guard`. The resolver correctly checks the raw input (`src/normalize.py:738-746`), but its component has already lost the bracketed isotope. `_link` now strips the brackets from separate words (`src/query.py:239-242`), creating `89 Zr trastuzumab`. `_qualified` checks isotope labels only one word at a time (`112`); its multiword scan does not call `is_isotope_label` (`114-116`), although that predicate supports `89 Zr` (`src/textrules.py:289-298`). Aggressive alias matching still succeeds (`src/query.py:317-322`; `src/textrules.py:339-346`). The final whole-name tracer guard recognizes the original tracer and returns `None` (`src/query.py:211-212`), but that is treated only as absence of a whole-name match: it supplies no refusal and the caller returns the unsafe `found` result (`149-153`).

**Required outcome:** preserve the explicit tracer refusal and its affected molecule through cleaning and tokenization; this exact input must never display or answer from the unlabelled drug.

### M8-B2 — P1, inherited: internal suffix wrappers defeat every refusal stage

**`bevacizumab-(awwb)`** and **`bevacizumab-[awwb]`** each return HTTP 200, **BEVACIZUMAB / CHEMBL1201583**, **122 trials**, no refusal. Both also leaked in the exact predecessor. Controls `bevacizumab-awwb`, `(bevacizumab-awwb)` and spaced `bevacizumab - (awwb)` refuse.

The resolver accepts the plain molecule after parenthetical cleaning; `_resolver_blocked` is empty. The item linker leaves an interior opening bracket/parenthesis, defeating the anchored suffix guard, then removes the distinction in `canonical_key`. `_whole_name` returns `None`, leaving the leaked Drug. `awwb` is a suffix explicitly classified by the repository itself (`src/textrules.py:169-171`); no external pharmacology assumption is needed.

`Which trials evaluate bevacizumab-(awwb)?` returns **12** originator rows over HTTP, first `NCT00955305|EVALUATES|CHEMBL1201583|NCT00955305`. `bevacizumab-(awwb), osimertinib` still makes BEVACIZUMAB the centre and lists OSIMERTINIB as an alternative; the separate drug does not authorize the originator leak. [HTTP](root_checks/new_http.json), [stages and analogous trastuzumab cases](attacks/probe_results.json).

**Cause:** edge-only wrapper removal at `src/query.py:239-242`, anchored guard at `src/textrules.py:156-157`, followed by broader positive canonicalization at `src/textrules.py:339-346` / `src/query.py:320-322`. Resolver cleaning is at `src/textrules.py:358-363`.

**Required outcome:** internal wrapper variants of a refused product must not gain originator identity through the lookup key.

### M8-B3 — P1, inherited: the advertised universal dash fold omits actual dash characters

**`bevacizumab⸺awwb`**, with **U+2E3A TWO-EM DASH**, returns HTTP 200, **BEVACIZUMAB / CHEMBL1201583**, **122 trials**, no refusal. Trial QA returns the same 12 originator rows. ASCII-hyphen and U+2011 controls refuse. The exact previous query module also leaks U+2E3A.

NFKC preserves this character. `_DASHES` at `src/query.py:100-101` excludes it; `_resolver_blocked` returns `{}`, `_link` accepts the aggressive alias key, and `_whole_name` returns `None`. The key erases the dash at `src/textrules.py:345`. A bounded scan of this Python runtime's **26 Pd code points** records **14 originator leaks**, including U+2E3B and U+2E40. This is an exhaustive Pd scan, not a claim to cover every dash-like Unicode symbol. [Inventory](attacks/unicode_dashes.json), [HTTP](root_checks/new_http.json), [stages](attacks/probe_results.json).

**Required outcome:** the normalization/refusal representation must cover the dash equivalences accepted by positive lookup. The source's “every Unicode dash” claim currently exceeds its implementation.

## Earlier findings — individual FIXED / NOT FIXED dispositions

The following **62 historical rows are 54 FIXED / 8 NOT FIXED**; counts include repeated qualifications, not 62 independent defects. Status applies to each exact reproduction, not every variation of its broader guarantee. M2 stopped without a REPORT; its completed m2b findings and partial role/order fixtures are covered below. The m7 carry-boundary supplement remains NOT FIXED separately at M8-S2. [Machine-readable matrix](replays/historical_findings_matrix.json).

### M1

| Finding / reproduction | Current result |
|---|---|
| B1 `bevacizumab - awwb`, `89Zr - trastuzumab`, `[89Zr] trastuzumab` | **FIXED** — refusal, no centre. [Original script replay](replays/m1_exact/names_product_bypass.json), [HTTP](root_checks/regression_http.json). |
| B2 collaborator called lead: `NCT00200395`, reverse `ORG:genentech` | **FIXED** — Genentech collaborator / Montefiore lead, both directions. `src/app.py:137,160-169`; `web/try.html:142-149`. [DB/UI](db_ui/db_assertions.json). |
| B3 Investigator called institution: `NCT00754364`, `ORG:armandosantoromd` | **FIXED** — person-specific heading. `web/try.html:143,148`. [DB/UI](db_ui/db_assertions.json). |
| B4 retire CHEMBL3353410 in memory; query name, ID, EGFR | **FIXED** — name/ID not_found; retired neighbour excluded. `src/app.py:115-118`. [Original HTTP fixture](replays/m1_exact/names_retired_http_results.json). |
| Retired Trial included in live Drug count | **FIXED** — centre count and neighbour count/weight 0. `src/app.py:129-132,139,174`. [Fixtures](db_ui/db_fixtures.json). |
| S1 misleading most-evidence wording/order, Disease | **FIXED** — actual start-date/score/count/A–Z sort disclosed and verified. `src/app.py:141-170`; `web/try.html:148-158,231-235`. [Oracle](db_ui/db_validate.json). |
| S2 silent ring cuts: ALDESLEUKIN, Disease, AstraZeneca | **FIXED** — 22/25, 39/3,074, 41/145 drawn disclosed; cut lists say 30. [UI](demos_cost/ui_harness_results.json). |
| S3 stale trail after refusal/not-found/server/network error | **FIXED** — state/buttons clear, obsolete back harmless. `web/try.html:213-216,243-244`. [UI](demos_cost/ui_harness_results.json). |
| S4 reverse-completed EGFR/KRAS requests and concurrent duplicate EGFR | **FIXED** — latest KRAS stays, duplicate gives one trail entry. `web/try.html:211-214`. [UI](demos_cost/ui_harness_results.json). |
| S5 silent ambiguity: Roche, MET, osimertinib EGFR/reversal, Mvasi and bevacizumab | **FIXED for disclosure** — selected reading/alternatives/refusal visible. `src/app.py:95-114`; `web/try.html:222-226`. [Names](replays/names_reproduction_results.json). |
| S6 action/class specificity | **FIXED** — specific gloss and original AGONIST/BINDING AGENT/class codes. `web/try.html:162-176`. [UI](demos_cost/ui_harness_results.json). |
| S7 start date, sponsor-to-Drug global count/phase, zero-trial Drug | **FIXED** — NCT00200395 start 2003-07-02; osimertinib sponsor 14/global 79/APPROVAL; CHEMBL925 count 0. [DB/UI](db_ui/db_assertions.json). |
| S8 node/edge props null, list, broken JSON | **FIXED** — 12 original requests and restorations return 200. `src/app.py:211-217`. [Fixtures](db_ui/db_fixtures.json). |
| Hostile labels/titles/IDs/URLs; scheme/host/credential/backslash probes | **FIXED for exercised markup paths** — escaping and HTTPS registry allowlist; browser limitation above. `web/try.html:104,180,199,221-235`. [Assertions](demos_cost/ui_assertions.json). |
| Unknown type Other / relation NEWREL | **FIXED** — raw fallback, no undefined tooltip. [UI](demos_cost/ui_regressions.json). |
| All three / everything documentation overclaims | **FIXED** — All of them / a capped list per relation. `src/app.py:5-11`. |
| Silent 500-character cut: `"x"*500 + " osimertinib"`, `"osimertinib " + "x"*600` | **FIXED** — explicit HTTP 400, no partial map. `src/app.py:239-243`. [HTTP](root_checks/http_results.json). |
| Lowercase IDs / Investigator names: nct00200395, chembl3353410, Armando Santoro Md | **NOT FIXED**, unchanged usability limit. [Controls](replays/names_unsupported_forms.json). |
| Raw list/null/malformed JSON/oversized-body errors | **NOT FIXED**, unchanged controlled 400 exposing parse/attribute details; subsequent valid requests succeed. `src/app.py:237-239,267-269`. [HTTP](root_checks/http_results.json). |

### M2b

| Finding / reproduction | Current result |
|---|---|
| R1 `osimertinib and generic version of bevacizumab`, reverse/comma, trial/sponsor QA | **FIXED** — only separate osimertinib; correct evidence. [HTTP](root_checks/regression_http.json), [supplement](root_checks/supplemental_http.json). |
| R1 tracer/oral-product collateral refusal, both orders | **FIXED** — `[89Zr] trastuzumab and osimertinib` and `osimertinib and oral azacitidine` retain osimertinib. [Names](replays/names_regressions.json). |
| Inherited `What is the generic version of bevacizumab?` | **FIXED** — refusal, no centre; also M3-B2. [HTTP](root_checks/supplemental_http.json). |
| R2 missing sponsor count, Alaunos–ALDESLEUKIN edge, both endpoints and null/list/broken/empty props | **FIXED** — null/zero sort weight; UI unknown, numeric 0 stays 0. `src/app.py:141-146`; `web/try.html:173`. [Fixture](db_ui/db_missing_sponsor_count.json). |
| Bool association score and hidden precision rounding | **FIXED** — bool null/weight 0; exact EGFR/KRAS decimal values retained. [DB](db_ui/db_score_fixture.json), [UI](demos_cost/ui_regressions.json). |
| Embedded multi-ID `Sharedbrand company` fixture | **FIXED** — Roche disclosed alongside selected AstraZeneca. `src/app.py:97-102`. [Fixture](replays/names_boundary_details.json). |
| Missing/unknown SPONSORS role and equal-weight A–Z | **FIXED** — neutral role wording, both directions/types; ordering verified. [DB/UI](db_ui/db_assertions.json). |
| Trial phases='PHASE2' render exception, four entry routes | **FIXED** — caught error, cleared trail, recovery/stale suppression. [Callbacks](demos_cost/ui_m3_checks.json). |
| Residual module wording / successful-input truncation | **FIXED** — individual M1 rows above. |

### M3 and M4

| Finding / reproduction | Current result |
|---|---|
| M3-B1 `paclitaxel with albumin bound nanoparticles`, formulation variant, `generic version with bevacizumab` | **FIXED** — no originator centre/evidence. [HTTP](root_checks/supplemental_http.json), [names](replays/names_new_boundaries.json). |
| M3-B2 leading generic-version question | **FIXED** — full qualified drug refused. [HTTP](root_checks/supplemental_http.json). |
| M3 comma collateral refusal: osimertinib with separately listed liposomal/biosimilar drug; reversals/QA | **FIXED** — separate osimertinib retained, 12 trial rows. [HTTP](root_checks/supplemental_http.json). |
| M3 bare erlotinib hydrochloride / long paclitaxel-poliglumex name; nested-parent re-link | **FIXED / retained** — correct complete IDs; no nested parent; explicit separate parent survives. [Names](replays/names_attack.json). |
| M4-B1 wrong shortest-span tie: `osimertinib with generic version of bevacizumab`, reversal/added a | **FIXED under revised design** — both same-item drugs refused; zero qualified-drug QA evidence. [HTTP](root_checks/attack_http.json). |
| M4-B1 semicolon and fullwidth-comma variants | **FIXED** — separate osimertinib retained. [Separators](replays/names_separator_checks.json). |
| M4-B2 long qualified poliglumex / `generic version of the monoclonal antibody bevacizumab` | **FIXED** — refused; bare long-name control preserved. [HTTP](root_checks/attack_http.json). |
| M4-B3 consumed qualifier: biosimilar version / liposomal formulation / albumin-bound / two-product combination | **FIXED** — no parent hit/evidence. [Names](replays/names_attack.json), [HTTP](root_checks/attack_http.json). |
| M4 target/company collateral refusal: EGFR or AstraZeneca beside biosimilar bevacizumab, reverse/with controls | **FIXED** — target/company retained; drug refusal disclosed. [HTTP](root_checks/m5_http.json). |
| M4 no-relink QA assessment | **FIXED / retained** — exact frozen 1,648-input counterfactual, 64 identical / 1,560 metadata-only / 24 semantic differences / 0 errors; adapted matcher target is `_link`. [Result](replays/adapted_frozen_qa_relink_sweep.json). |
| M3/M4 blank/whitespace form | **NOT FIXED**, unchanged usability limit: no request, previous view stays. `web/try.html:241`. [UI](demos_cost/ui_m3_checks.json). |
| M3/M4 positive/negative Infinity fixture | **NOT FIXED**, unchanged failure closed: controlled HTTP 400, no invalid value drawn, none in snapshot. `src/app.py:207-208,264-269`. [Fixture](db_ui/db_numeric_fixture.json). |
| Repeated lowercase-ID/name and raw request qualifications | **NOT FIXED**, same individual M1 rows above. |

### M5 and M6

| Finding / reproduction | Current result |
|---|---|
| M5-B1 reported attached slash/pipe and internal both-sides-glued attack | **FIXED** — `bevacizumab-awwb/ osimertinib` and `bevacizumab - awwb/osimertinib` select only OSIMERTINIB and expose refusal; pipe counterparts too. [HTTP](root_checks/m5_http.json), [m6 replay](root_checks/confirm_http.json). |
| M5-B2 `liposomal and nanoparticle formulation of doxorubicin`, plural/sustained-release | **FIXED** — forward qualifier carry refuses product; QA 0. [HTTP](root_checks/m5_http.json). |
| M5-S1 `biosimilar anastrozole, Arimidex`; `biosimilar Prolia, xgeva` | **FIXED** — separate aliases survive; 2/3 trial rows. [HTTP](root_checks/cross_item_http.json). |
| M5-S1 `Erlotinib, hydrochloride biosimilar bevacizumab`, semicolon | **FIXED** — original qualified comma/semicolon inputs preserve CHEMBL553; the simplified comma-list M7 regression is also repaired. [Exact HTTP](root_checks/m5_http.json), [M7 controls](replays/historical_focus.json). |
| M5-S2 Pegylated interferon alfa-2a | **NOT FIXED — accepted known over-refusal**, not a new blocker. Canonical name/ID work. [HTTP](root_checks/m5_http.json). |
| M5-S3 all-substring cubic work / 999-character plain-answer timeout | **FIXED for exact previous cost cases** — bounded predicate work and original plain-answer requests complete. Repeated-piece overhead also repaired; new cache-boundary failure is recorded separately below. [Original HTTP](root_checks/perf_check_http.json), [current instrumentation](demos_cost/perf_current.json). |
| M6-B1 interior slash/pipe | **FIXED** — separate osimertinib retained; forbidden originator absent from QA. [Exact HTTP](root_checks/confirm_http.json), [39-case matrix](replays/focused_matrix.json). |
| M6-B2 U+3002 suffix punctuation, trailing em dash/hyphen, leading hyphen | **FIXED** — all four original edge-punctuation inputs refuse, as do trial/sponsor QA. [Exact HTTP](root_checks/confirm_http.json), [current focused stages](replays/historical_focus.json). |
| M6-B2 supplementary bracketed/Unicode variants | **FIXED** — whole-product wrappers `(bevacizumab-awwb)` / `[bevacizumab-awwb]` and the previously reported Unicode hyphens now refuse; question-mark and quoted shortcut cases also refuse. [Historical matrix](replays/historical_focus.json), [m7 attack HTTP](m7_attacks/http_results.json). |
| M6-B3 `doxorubicin (nanoparticle and liposomal formulation)` / `bevacizumab (investigational and biosimilar)` | **FIXED** — both parenthesized reversed qualifiers produce no centre or QA evidence. [Exact HTTP](root_checks/carry_http.json), [stages](replays/historical_focus.json). |
| M6 non-parenthetical reversed-qualifier supplement | **NOT FIXED as original expectation; accepted current item-policy consequence** — `doxorubicin in nanoparticle and liposomal formulations` still selects doxorubicin after listing-word separation. [Exact HTTP](root_checks/reverse_http.json). |
| M6-S1 six complete stored aliases returning another Drug ID | **FIXED for all six bare inputs** — intended stored IDs retained. [Current stages](replays/historical_focus.json), [HTTP](root_checks/alias_http.json). |
| M6-S1 prefixed QA using those comma-containing names | **NOT FIXED — current whole-input-only design consequence**. ENDOSTATIN prefixed QA still selects CHEMBL4297747 with 2 rows; Rapamycin prefixed QA CHEMBL413 with 5 rows. [Exact HTTP](root_checks/alias_http.json), [direct QA](replays/historical_focus.json). |
| M6 associated lone stored-alias losses | **FIXED for all 19 non-M5-S2 historical lost aliases** — slash/joiner names restored; known M5-S2 still refuses. The current sweep separately records new isotope-token over-refusals. [Exact previous/current alias comparison](replays/alias_regressions.json), [complete current sweep](replays/adapted_names_m5_summary.json). |
| M6 split_2000 / many-piece cost control | **FIXED for exact repeated-piece cost control** — current resolver skips no-drug pieces and deduplicates; the previous per-piece delay is gone. [Exact stress replay](demos_cost/cost_stress.json), [old/current samples](demos_cost/fresh_cost_comparison.json). |

### M7

| Finding / reproduction | Current result |
|---|---|
| M7-B1 Whole-name refusal bypass: `bevacizumab-awwb?`, `bevacizumab-awwb!`, quoted form | **FIXED** — All return refusal/no centre; trial and sponsor QA zero. [Current stages](replays/historical_focus.json), [original m7 HTTP replay](m7_attacks/http_results.json). |
| M7-B2 Wrappers and Unicode hyphens: `(bevacizumab-awwb)`, `[bevacizumab-awwb]`, U+2011 suffix and bio-similar | **FIXED** — All named inputs refuse after shared normalization and edge stripping; no originator QA. [Stages](replays/historical_focus.json), [HTTP](m7_attacks/http_results.json). |
| M7-B3 Whitespace isotope: `89Zr trastuzumab` | **FIXED** — No centre; both QA forms have zero evidence. [Stages](replays/historical_focus.json), [HTTP](m7_attacks/http_results.json). |
| M7-S1 Canonical equality too broad: `Erlotinib, hydrochloride`, `osimertinib,mesylate`, `is a` | **FIXED** — Respectively CHEMBL553, CHEMBL3353410 and not_found; actual exact aliases retain intended IDs. [Current controls](replays/historical_focus.json), [HTTP](m7_attacks/http_results.json). |
| M7-S2 Lone exact stored names: `(E/Z)-AFATINIB`, `RO 09-1978/000`, `Anusol plus hc` and 19-alias set | **FIXED** — All 19 old non-M5-S2 losses restored; three named controls select CHEMBL1173655 / CHEMBL1773 / CHEMBL389621. [Exact previous/current comparison](replays/alias_regressions.json), [HTTP](replays/alias_http.json). |
| M7-S3 Repeated identical-piece full resolver cost / queued ordinary map | **FIXED** — Exact old repeated-x controls and corresponding requests complete with materially reduced work. New distinct-drug workload and cache failure are separate. [Cost replay](demos_cost/cost_stress.json), [comparison](demos_cost/fresh_cost_comparison.json), [HTTP](demos_cost/fresh_cost_http.json). |

## Should-fix findings, separate from the originator approval blockers

### M8-S1 — P2, new: cache rollover rejects a valid lone drug

On a fresh original CLI server, send **82 successful `/api/explore` requests** containing the 4,096 distinct pieces `isa x0000` through `isa x4095`, in semicolon batches of at most 50 (each request at most **499 characters**). Then send `{"text":"osimertinib"}`:

- First request: **HTTP 400**, `{"error":"'osimertinib'"}`.
- Immediate identical retry: **HTTP 200**, **CHEMBL3353410**, **79 trials**.

No cache was injected or monkey-patched. The original inherited 7,511-key sweep independently hit the same exception at `Gallium gozetotide ga-68`; its failure transcript is retained. [Natural HTTP reproduction and exact batches](demos_cost/cache_boundary_http.json), [reproducer](demos_cost/cache_boundary_http.py), [historical replay/adaptation evidence](replays/FINDINGS.md).

`src/query.py:174-182` inserts entry 4,097, clears the entire cache at `180-181`, then immediately indexes the removed key at `182`. The HTTP wrapper turns that `KeyError` into a 400 (`src/app.py:267-269`). Keep the current resolution available across eviction. This is a new valid-input reliability defect, not accepted over-refusal or a permanent deadlock.

### M8-S2 — P2, inherited: qualifier carry crosses an explicit item boundary

`biosimilar, and osimertinib`, `biosimilar; and osimertinib`, and `biosimilar and, osimertinib` all return only Refused `biosimilar ... osimertinib`. Their controls `biosimilar, osimertinib` and bare `osimertinib` draw **CHEMBL3353410 / 79 trials**. HTTP QA for the first form yields zero evidence; the comma-only control yields 12.

The valid drug is alone in its punctuation-delimited item, so this falls outside the requested intended-over-refusal allowance. The input was already present in m7's supplemental attack; it is **NOT FIXED**, not newly introduced. `joined` checks only intervening joiner segments, ignoring `clause` boundaries (`src/query.py:282-283`), then carries the qualifier at `298-304`. [HTTP](root_checks/new_http.json), [m7-script replay](m7_attacks/fresh_results.json).

### M8-S3 — P2, new: isotope-shaped stored aliases lose valid lone-name recognition

| Exact stored alias | Stored Drug ID | Current map | Exact m7 query module |
|---|---|---|---|
| `566C` | ATOVAQUONE / CHEMBL1450 | Refused | Correct Drug |
| `9-ac` | 9-AMINOCAMPTOTHECIN / CHEMBL274070 | Refused | Correct Drug |
| `5ac` | AZACITIDINE / CHEMBL1489 | Refused | Correct Drug |

All three are exact unique dictionary aliases, supplied alone. Preferred-name controls still work. The resolver also refuses these as isotope labels; this is **shared over-refusal**, not resolver disagreement. The new unconditional one-token isotope test (`src/query.py:112`) prevents whole-name recovery (`208-209`). These additional lone-name losses are separate from explicitly accepted M5-S2. Evidence establishes the repository's stored identities; no clinical suitability claim is made. [Dictionary/stages/predecessor](attacks/lone_alias_results.json), [actual HTTP](alias_checks/new_http.json).

### M8-S4 — P2, new: a literal terminal period in a stored name is deleted before exact comparison

**`5.BETA.,20-EPOXY-1,2.ALPHA.,4,7.BETA.`** is an exact unique stored PACLITAXEL alias, **CHEMBL428647**. Current HTTP returns **not_found**; the exact previous query module draws PACLITAXEL with **234 trials**, and current preferred-name/ID controls still work. No current stage refused this input.

`src/query.py:210` strips the name's required terminal period, but `215-216` compares against the unstripped stored alias. The input really is letter-for-letter the stored name before that asymmetric operation. Preserve literal stored punctuation when applying the stated exact-name exception, without weakening product refusals. [Stored-name/predecessor evidence](attacks/lone_alias_results.json), [HTTP](alias_checks/new_http.json).

## Cost and demos

M7-S3's **exact repeated non-drug piece** defect is **FIXED**. A final comparison ran after the other audit workloads finished; unrelated host activity remains uncontrolled. It loads exact `9bd7cb4` and current query modules against the same data/rules.

| Workload | Observed result |
|---|---|
| Link `";".join(["x"]*2000)` (3,999 chars), three-sample median | m7 **1.88151 s**; current **0.16277 s** |
| HTTP `/api/check`, question EGFR, same answer | **0.44761 s**, HTTP 200 |
| Ordinary EGFR map queued during that check | **0.36605 s**, HTTP 200; ordinary baseline/after about **0.02 s** |
| 400 distinct drug-bearing pieces, `";".join(f"isa x{i:04d}" for i in range(400))` (3,999 chars), cold HTTP check | **2.20771 s**, HTTP 200 |
| Ordinary EGFR queued behind that cold distinct-piece check | **2.12630 s**, HTTP 200 |
| Same distinct-piece check, warm cache | **0.35203 s**, HTTP 200 |

Direct instrumentation confirms **400 cold / 0 warm resolver calls** for the distinct pieces, **1 / 0** for 400 repeated drug-bearing pieces, and **0** for non-drug pieces. Thus repeated-piece caching works; unique legal inputs still consume seconds while `engine.lock` covers resolution/checking (`src/app.py:247-263`). This residual cost is not mislabeled as the repaired m7 defect or a newly introduced slowdown. No timeout/deadlock or global linear-complexity claim is made. [Full reproducible cost evidence](demos_cost/FINDINGS.md).

All seven original HTTP QA demos retain evidence counts **12, 12, 11, 1, 12, 0, 0**. Six complete responses equal original `bfcb83d`; Mvasi differs only in refusal metadata. All 36 page-demo responses equal m7. [Original QA comparison](root_checks/http_demo_results.json), [all demo evidence](demos_cost/FINDINGS.md).

Disease returns **2,774 Trials + 300 Targets**, 30 each, **18,575 bytes in 72.565 ms**. The inherited **24-request / 12-worker** workload returns expected HTTP 200 shapes in **620.588 ms**. These ordinary timings overlapped other audit work and are observations, not latency guarantees. [HTTP results](root_checks/http_results.json).

## Integrity, standards and remaining limits

The snapshot has **7 retired nodes, 142 retired edges, no self-loops and no live edge with a retired endpoint**. No new wrong live edge, relation/direction label, stored field value, cut notice or generated-markup injection was established in the exercised paths. The page/docstring refusal promise still fails at `src/app.py:74-76` and `web/try.html:215` for M8-B1–B3.

No repository AGENTS/CONTRIBUTING/CODING standards source was found; the supplied review/no-tracked-edit instructions govern. No application code was changed, so the conditional KOA Studio / KhOpenApi original-versus-modified-code comparison does not apply. Application paths use `use_llm=False` (`src/app.py:180-181`); no model was invoked. The application does not globally open SQLite read-only, so this review relies on inspected executed paths, isolated fixtures and hash checks, not a DB-permission guarantee.

Final HEAD, tracked/staged diffs, all **2,372 tracked-file SHA-256 comparisons**, database hash, owned-port closure and report-link validation are recorded in [integrity_final.json](integrity_final.json). Database SHA-256: `7341c5a7089731f67356da5a588b269d4b69e8e6c4c054acf19aa4ef2837b529`.

Run from the repository root with bytecode disabled; keep HTTP runners sharing a port sequential. Individual worker reports/manifests list adapted commands and exact inputs.

```text
python -B audit_evidence_claims/m8/root_checks/run_replays.py tests
python -B audit_evidence_claims/m8/root_checks/run_replays.py http
python -B audit_evidence_claims/m8/root_checks/run_m6_http.py m6_http
python -B audit_evidence_claims/m8/db_ui/run_db.py
python -B audit_evidence_claims/m8/m7_attacks/fresh_probe.py
python -B audit_evidence_claims/m8/attacks/probe.py
python -B audit_evidence_claims/m8/attacks/lone_alias_probe.py
python -B audit_evidence_claims/m8/root_checks/new_http.py
python -B audit_evidence_claims/m8/alias_checks/probe.py
```

VERDICT: CHANGES REQUIRED
