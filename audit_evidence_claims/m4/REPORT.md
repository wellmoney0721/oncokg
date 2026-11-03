# Independent relation-map review — round 4

Reviewed HEAD: `bf436c6e93c3eef9e115159ede951a5ecaee5472`, 2026-11-03. Immediate before/after comparison: `574097f` → `bf436c6`; accumulated repair review: `git diff bfcb83d...HEAD`. Specification: the user's round-4 brief, original approval bar, [m1](../m1/REPORT.md), [m2b](../m2b/REPORT.md), [m3](../m3/REPORT.md), and `CODEX_MAP_M1_VERDICT.md`.

**Approval remains blocked.** The exact named m3 blockers are fixed, but the new shortest-span rule can bind a qualifier to the wrong drug and map the refused product's originator. The six-token limit also admits a qualified multi-token drug alias that the previous version refused. Separately, the original single-token qualifier pass still prevents a refusal from reaching its drug. These are current-database map and QA reproductions, not malformed-data fixtures or external pharmacology assumptions.

## Verification and limits

- Requested suite: `python -m pytest tests -q -p no:cacheprovider` — **325 passed in 18.29 s**, exit 0. Bytecode/cache writes disabled; test temporary files confined to m4. [Output](pytest.txt), [environment and hashes](pytest_summary.json).
- Started the unchanged CLI server on **8880**, exercised `GET /` and `/api/explore`, `/api/resolve`, `/api/ask`, and stopped each owned server. Served HTML equals `web/try.html`. All original HTTP cases, mixed-input regressions and new attacks were executed. [Original HTTP cases](http_results.json), [prior name regressions](regression_http.json), [m3 cases](supplemental_http.json), [new attack responses](attack_http.json).
- Replayed **62 original name inputs**, 13 original comparison probes, the m3 supplemental boundary cases and stored-alias scans. Old scripts were copied/adapted into m4 before execution; prior output files were not overwritten. Fresh current results: [names_reproduction_results.json](names_reproduction_results.json), [names_regressions.json](names_regressions.json), [names_boundary_details.json](names_boundary_details.json), [names_new_boundaries.json](names_new_boundaries.json), [names_label_scan.json](names_label_scan.json).
- New focused coverage: **45 adversarial inputs**, **37 varied QA questions**, **2,584 unique multi-token alias keys**, and a separate **1,648-question no-relink isolation sweep**. [Focused before/after evidence](names_attack.json), [isolated QA sweep](qa_relink_sweep.json). The current/previous comparison restores the exact `574097f` linker **and its `_JOINERS`**, with the same database. The separate counterfactual changes only HEAD's matched-token exclusion.
- Independently checked **all 6,469 live centres**, **22 role-aware relation/direction/type combinations**: **zero adjacency, live-node, value, count, grouping or ordering mismatches**, 138.649 s. Retirement and malformed-props mutations were in-memory only. [Validator](db_recheck.py), [results](db_validate.json), [fixtures](db_fixtures.json).
- Executed the entire current page script in a Node VM with controlled DOM/fetch stubs: 16 fresh maps, all **36 page examples**, **42 example click callbacks**, four render-error entry points, and 24 aggregate assertions. Five shared current HTTP maps equal the fresh Engine payloads. [UI evidence](ui_findings.md), [assertions](ui_assertions.json).
- **No real-browser interaction or browser-executed XSS test was completed.** Browser discovery returned `The browser access host is unavailable`; selecting Chrome returned `Computer Use was not approved to use Google Chrome`. Generated markup, event/state behavior and HTTP were tested; browser paint/layout/exploit execution is not claimed. [Current attempt](browser_attempt.json). Dark mode was out of scope.

## Previous findings — exact reproduction dispositions

**FIXED** means that specific prior failure no longer reproduces. It does not certify the whole name-refusal guarantee. Regressed m3 supplementary controls are explicitly marked below.

### M1

| Finding / exact input or fixture | Result | Current evidence and source |
|---|---|---|
| B1: `bevacizumab - awwb`; `89Zr - trastuzumab`; `[89Zr] trastuzumab`, plus unspaced controls | **FIXED** | Refusal, no originator centre. `src/query.py:143-160,241-279`; [HTTP](regression_http.json), [name replay](names_reproduction_results.json). |
| B2: collaborator called lead, `NCT00200395`, reverse `ORG:genentech` | **FIXED** | Genentech is collaborator; Montefiore lead sponsor; reverse wording preserves roles. `src/app.py:137,160-169`; `web/try.html:142-149`; [DB](db_validate.json), [rendered headings](ui_harness_results.json). |
| B3: Investigator called institution, `NCT00754364`, `ORG:armandosantoromd` | **FIXED** | Person-appropriate `책임 주관 연구자 (lead sponsor)`. `web/try.html:143,148`; [UI](ui_harness_results.json). |
| B4: retire `CHEMBL3353410` in memory, then query `osimertinib`, its ID and `EGFR` | **FIXED** | Name and ID are not_found; retired neighbour excluded. `src/app.py:115-118`; [real-handler fixture](db_retired_center.json). |
| Retired-trial count: live D, retired T, live T→EVALUATES→D and D→ACTS_ON→X | **FIXED** | Centre/global count and neighbour weight are 0; T excluded. `src/app.py:129-132,139,174`; [fixture](db_fixtures.json). |
| S1: misleading evidence order, especially `MONDO_0005233` | **FIXED** | Each sort is stated; Trials use start date, disease Targets use score, equal-weight names A–Z; group totals descend. `src/app.py:141-170`; `web/try.html:148-158,231-235`; [DB](db_validate.json), [UI](ui_harness_results.json). |
| S2: silent ring cuts, `CHEMBL1201438`, Disease, AstraZeneca | **FIXED** | Ring shows 22/25, 39/3,074, 41/145 respectively; list cuts say 30 retained. No whole nonempty group omitted in exercised maps. 40 is a soft allocation target. `web/try.html:191-204,233`; [UI](ui_harness_results.json). |
| S3: osimertinib→EGFR then `Mvasi`, `unknown-m1-entity`, server/network error and old back callback | **FIXED** | Trail state/buttons clear; obsolete callback is harmless; normal back works. `web/try.html:213-216,243-244`; [UI](ui_harness_results.json). |
| S4: EGFR/KRAS completed in reverse; concurrent duplicate EGFR | **FIXED** | Latest KRAS stays; stale success/error ignored; duplicate leaves one trail entry. `web/try.html:211-214`; [controlled completion tests](ui_harness_results.json). |
| S5: silent identities, `Roche`, `MET`, `osimertinib EGFR`, reversed order; `Mvasi and bevacizumab` | **FIXED for exact inputs** | Selected reading, alternatives and refusal disclosed. Stored FOLIC ACID/METFORMIN collisions remain visible. `src/app.py:95-114`; `web/try.html:222-226`; [names](names_reproduction_results.json), [UI](ui_harness_results.json). |
| S6: AGONIST / BINDING AGENT and sponsor-class specificity | **FIXED** | Specific gloss plus stored action; sponsor class codes preserved. `web/try.html:162-176`; [UI details](ui_harness_results.json). |
| S7: Trial centre start, sponsor→Drug global count/phase, zero-trial Drug | **FIXED** | NCT00200395: `2003-07-02`; AstraZeneca→osimertinib: sponsor count 14, graph count 79, APPROVAL; CHEMBL925: 0. `src/app.py:138-149,171-177`; `web/try.html:173-174,228-229`; [DB/UI](ui_harness_results.json). |
| S8: node/edge props `null`, `[]`, `{broken` | **FIXED** | All 12 original requests and restored controls succeed. `src/app.py:135,171,211-217`; [fixtures](db_fixtures.json). |
| URL/markup qualification: javascript/data URLs, hostile labels/titles/node and edge IDs | **FIXED for exercised map paths** | Registry HTTPS allowlist rejects tested scheme/host/credential/backslash spoofs; text and attributes escaped. Browser limitation above applies. `web/try.html:104,180,199,221-235`; [payloads](ui_harness_results.json), [assertions](ui_assertions.json). |
| Unknown-type tooltip `Other` / `NEWREL` | **FIXED** | Raw fallback, no `undefined`. `web/try.html:158,199,227`; [UI](ui_regressions.json). |
| Module “All three” and “everything” overclaims | **FIXED** | Introduction states `All of them` and `a capped list per relation`. `src/app.py:5-11`. |
| Silent input truncation: `"x"*500 + " osimertinib"`; `"osimertinib " + "x"*600` | **FIXED** | Both HTTP 400, `input is longer than 500 characters`; no partial map. `src/app.py:239-242`; [HTTP](http_results.json). |
| Unsupported lowercase IDs / Investigator names, e.g. `nct00200395`, `chembl3353410`, `Armando Santoro Md` | **NOT FIXED — unchanged usability limitation** | Canonical IDs work; these forms remain not_found. [Fresh controls](names_unsupported_forms.json). |
| Raw request-shape errors: JSON list/null, malformed JSON, >20,000-byte body | **NOT FIXED — unchanged server qualification** | Controlled 400 still exposes `.get`/parse details; valid subsequent calls succeed. `src/app.py:237-239,267-269`; [HTTP](http_results.json). |

### M2b

| Finding / exact reproduction | Result | Current evidence and source |
|---|---|---|
| R1: `osimertinib and generic version of bevacizumab`, reverse and comma variants | **FIXED** | OSIMERTINIB retained, qualified bevacizumab refused. Trial QA starts NCT03909334→EVALUATES→CHEMBL3353410; sponsor QA starts AstraZeneca→SPONSORS_TRIAL_OF→CHEMBL3353410. `src/query.py:143-152,241-279`; [HTTP](regression_http.json), [QA](supplemental_http.json). |
| R1 over-refusal: `[89Zr] trastuzumab and osimertinib`, reversed; `osimertinib and oral azacitidine` | **FIXED** | Separately named osimertinib and its evidence survive. [Name replay](names_reproduction_results.json), [comparisons](names_regressions.json). |
| Previously inherited control: `What is the generic version of bevacizumab?` | **FIXED** | Refusal now includes bevacizumab; no centre. This is also m3-B2. [HTTP](supplemental_http.json). |
| R2: `ORG:alaunos\|SPONSORS_TRIAL_OF\|CHEMBL1201438\|` props `null`, `[]`, `{broken`, both endpoints | **FIXED** | `evidence_trials:null`, weight 0; UI says `책임 주관한 임상 수 기록 없음`. `{}` unknown; actual numeric zero displayed as zero. `src/app.py:141-146`; `web/try.html:173`; [API](db_missing_sponsor_count.json), [UI](ui_missing_sponsor_count.json). |
| Boolean association-score fixture / render error | **FIXED** | API null/weight 0; injected booleans also do not crash the page. `src/app.py:152-155,207-208`; `web/try.html:176`; [API](db_score_fixture.json), [UI](ui_regressions.json). |
| Undisclosed score rounding, EGFR/KRAS | **FIXED** | Exact `0.8883707400322897` / `0.8337881598550857` in detail and tooltip. `web/try.html:176`; [precision checks](ui_regressions.json). |
| Embedded multi-ID company alias: `companies['sharedbrand']=['ORG:astrazeneca','ORG:roche']`; `Sharedbrand company` | **FIXED** | Roche disclosed in `also`; current production index has no multi-ID company key. `src/app.py:97-102`; [index-only fixture](names_boundary_details.json). |
| Residual module wording / successful-input truncation | **FIXED** | Capped-list description and explicit >500-character rejection, as above. |
| Render exceptions escape catch: Trial `props.phases='PHASE2'` | **FIXED for UI entry points** | Form/node/back/example routes display failure, clear trail and recover on KRAS; stale response ignored. `web/try.html:238-248`; [callbacks](ui_m3_checks.json). |
| Missing/unknown SPONSORS role and equal-weight A–Z follow-ups | **FIXED** | Neutral `역할 기록 없음`, both directions; valid roles intact; all-node name ordering passes. `web/try.html:147-149`; `src/app.py:166-167`; [roles](db_role_fallback.json), [UI](ui_regressions.json), [order](db_validate.json). |

### M3, including supplementary controls

| Finding / exact reproduction | Result | Current evidence and source |
|---|---|---|
| M3-B1: `paclitaxel with albumin bound nanoparticles`, formulation variant; `generic version with bevacizumab` | **FIXED** | Refusal includes the drug; no originator centre. Exact paclitaxel trial question has 0 evidence. `src/query.py:241-279`; [HTTP](supplemental_http.json). |
| M3-B2: `What is the generic version of bevacizumab?` | **FIXED** | Refuses `generic version of bevacizumab`, no centre. [HTTP](supplemental_http.json). |
| Comma over-refusal: `osimertinib, liposomal doxorubicin`; `osimertinib, biosimilar bevacizumab`, reverses and QA | **FIXED** | OSIMERTINIB retained; trial QA has 12 osimertinib evidence rows. `src/query.py:149-151`; [HTTP](supplemental_http.json). |
| Bare longer-name controls: `erlotinib hydrochloride`; `Paclitaxel conjugate with poly-l-glutamic acid` | **FIXED / retained** | Correct full Drug identity, no nested parent in `also`; explicit separately named parent remains linkable. `src/query.py:165-189`; [focused controls](names_attack.json). |
| Supplementary passing control: `osimertinib with generic version of bevacizumab` | **NOT FIXED — NEW REGRESSION** | Now selects BEVACIZUMAB; previous 574097f selects OSIMERTINIB. M4-B1 below. [Before/after](names_attack.json), [HTTP](attack_http.json). |
| Supplementary passing control: `generic version of Paclitaxel conjugate with poly-l-glutamic acid` | **NOT FIXED — NEW REGRESSION** | Now selects PACLITAXEL POLIGLUMEX; previous refuses. M4-B2 below. [Before/after](names_attack.json), [HTTP](attack_http.json). |
| Supplementary hyphenated control: `paclitaxel with albumin-bound nanoparticles` | **NOT FIXED — inherited bypass** | One-token `albumin-bound` refusal leaves PACLITAXEL; differs from the repaired unhyphenated case. M4-B3 below. [Replayed control](names_new_boundaries.json). |
| Supplementary semicolon/fullwidth-comma controls: `osimertinib; generic version of bevacizumab`; `osimertinib， generic version of bevacizumab` | **NOT FIXED — NEW ORIGINATOR-LEAK REGRESSIONS** | Previous version refuses the whole input (already over-broad); current selects BEVACIZUMAB. Only ASCII comma is a clause boundary at `src/query.py:128-133`. These are additional wrong-binding examples under M4-B1. [Replayed controls](names_new_boundaries.json), [exact immediate-baseline checks](names_separator_checks.json). |
| Lowercase IDs / Investigator names / raw request-shape details | **NOT FIXED — unchanged** | Same qualifications as m1 rows above. |
| Empty/whitespace map form submission | **NOT FIXED — unchanged usability qualification** | No request; previous view remains. `web/try.html:241`; [UI](ui_m3_checks.json). |
| Positive/negative Infinity numeric fixture | **NOT FIXED — unchanged, failure closed** | `_number` accepts Infinity; `allow_nan=False` produces controlled HTTP 400, so no invalid numeric value is drawn. None in snapshot. `src/app.py:207-208,264-269`; [numeric fixtures](db_numeric_fixture.json). |

## Specification blockers

### M4-B1 — P1, new regression: equal-length binding refuses the wrong drug

Exact unchanged-server request:

```text
POST /api/explore
{"text":"osimertinib with generic version of bevacizumab"}
```

HTTP 200 contains:

```json
{"center":{"id":"CHEMBL1201583","label":"BEVACIZUMAB","trials":122},
 "also":[{"refused":"osimertinib with generic version"}]}
```

This is an excerpt of the full response in [attack_http.json](attack_http.json). With the exact previous linker and previous `_JOINERS`, the centre is **OSIMERTINIB / CHEMBL3353410** and the refused span is **generic version of bevacizumab**. The current full-string resolver returns `BLOCKED_DISTINCT_PRODUCT`, no drug ID. Reversing the drugs (`bevacizumab with generic version of osimertinib`) also selects the qualified second drug. Adding just `a` — `osimertinib with a generic version of bevacizumab` — changes the current result back to OSIMERTINIB. This is a distance/tie artifact, not a product-identity distinction.

| Exact `/api/ask` text | Previous linker's first evidence | Current HTTP first evidence |
|---|---|---|
| `Which trials evaluate osimertinib with generic version of bevacizumab?` | `NCT03909334\|EVALUATES\|CHEMBL3353410\|NCT03909334` | `NCT00955305\|EVALUATES\|CHEMBL1201583\|NCT00955305` |
| `Which companies sponsor osimertinib with generic version of bevacizumab?` | `ORG:astrazeneca\|SPONSORS_TRIAL_OF\|CHEMBL3353410\|` | `ORG:roche\|SPONSORS_TRIAL_OF\|CHEMBL1201583\|` |

Both current answers have 12 evidence rows; status/evidence-count checks alone miss the subject switch. [Current HTTP](attack_http.json), [exact before/after QA](names_final_checks.json).

**Cause:** `with` was removed from `_JOINERS` (`src/query.py:91-95`). `_drug_spans` supplies the first drug before the second (`222-239`). Both `osimertinib with generic version` and `generic version of bevacizumab` are four-token candidate spans. The shortest-span selector iterates drug spans in that order and updates only on strictly shorter length (`255-272`), so the first candidate wins. Its qualifier tokens enter `out`; the correct second candidate is then disallowed by `span & out` (`264`). BEVACIZUMAB remains acceptable at `181-189`, and the map takes it at `src/app.py:88-95`.

Additional m3 controls `osimertinib; generic version of bevacizumab` and `osimertinib， generic version of bevacizumab` change from a whole-input refusal to a BEVACIZUMAB centre. Their separators are not clause boundaries, so the shortest-span algorithm consumes the left drug and leaves the qualified right drug available. The previous over-refusal was a usability failure; the new originator leak is a blocking regression. [Exact comparisons](names_separator_checks.json).

**Required outcome:** bind the qualifier to the product it describes without consuming a separately named valid drug. This input must never map or answer for generic bevacizumab as BEVACIZUMAB. Preserve the repaired albumin-bound paclitaxel case; globally reinstating `with` as a separator would reopen m3-B1.

### M4-B2 — P1: six-token cap admits qualified longer aliases and distant qualifiers

`POST /api/explore {"text":"generic version of Paclitaxel conjugate with poly-l-glutamic acid"}` now draws **PACLITAXEL POLIGLUMEX / CHEMBL2108628**, with `also:[]`. The same full input is `BLOCKED_DISTINCT_PRODUCT` at `/api/resolve`; previous `574097f` refuses with no centre. This exact string was already a m3 supplementary control. [Full current HTTP](attack_http.json), [exact previous/current comparison](names_attack.json).

**Cause:** the stored alias occupies five tokens. `_drug_spans` deliberately retains that full non-overlapping name (`src/query.py:222-239`), but `_qualified_drug_spans` only examines spans up to **six tokens** (`258`: `range(b - a, 7)`). The qualifier plus `of` plus the full alias requires eight. No tested span can contain both `generic version` and the complete drug, so nothing is refused. The map then accepts the bare full alias inside the refused product description. This is a new regression even though the bare poliglumex alias correctly remains supported.

The cap also leaves a simpler inherited bypass: `generic version of the monoclonal antibody bevacizumab` (seven tokens) draws BEVACIZUMAB with `also:[]`; the six-token control `generic version of the antibody bevacizumab` refuses. QA `Which trials evaluate generic version of the monoclonal antibody bevacizumab?` returns 12 BEVACIZUMAB trial rows. `What targets does generic version of Paclitaxel conjugate with poly-l-glutamic acid act on?` also returns current evidence for CHEMBL2108628 (12 rows, first ACTS_ON edge), despite the qualified product being unresolved. [HTTP responses](attack_http.json).

The **plain qualified phrase** is a new map/QA regression: previous refusal/0 evidence becomes a centre/7 profile-mechanism rows. The longer `What targets ... act on?` question already bypassed the previous linker (12→12 rows), as did `Which trials evaluate generic version of Paclitaxel conjugate with poly-l-glutamic acid?` (4→4). Those prefixed-question failures are inherited. [Exact before/after checks](names_final_checks.json), [plain-phrase comparison](names_attack.json).

**Required outcome:** an arbitrary token-distance ceiling must not turn a known qualified product into a positive originator match. Preserve valid bare multi-token aliases and fail safely when qualification cannot be bound reliably.

### M4-B3 — P1, inherited: the single-token prepass blocks its own extension to the drug

| Exact `/api/explore` text | Current result | Current `/api/ask` reproduction |
|---|---|---|
| `biosimilar version of bevacizumab` | BEVACIZUMAB / CHEMBL1201583; only `biosimilar version` refused | `Which trials evaluate biosimilar version of bevacizumab?` → 12 BEVACIZUMAB trial rows |
| `liposomal formulation of doxorubicin` | DOXORUBICIN / CHEMBL53463; only `liposomal formulation` refused | `Which trials evaluate liposomal formulation of doxorubicin?` → 3 DOXORUBICIN trial rows |

The existing resolver refuses both complete products. Both parent leaks also occur with `574097f`, so these are **inherited**, not attributed to the latest repair. They nevertheless defeat the approval bar and the new claim that refusal is bound to its drug. [Current HTTP](attack_http.json), [before/after](names_attack.json).

**Cause:** `src/query.py:143-151` marks the qualifier and immediate neighbour before binding. `_drug_spans(tokens, refused)` skips those tokens (`252`, `225-229`), and every candidate crossing them is rejected by `span & refused` (`264`). Thus the helper cannot extend a previously recognized qualifier across `version of` or `formulation of` to its drug. These examples fit within six tokens; raising only the cap does not fix them.

The two-product input `liposomal formulation of doxorubicin and biosimilar version of bevacizumab` links **both parent drugs**, selects DOXORUBICIN and puts BEVACIZUMAB in `also`. By contrast, adjacent `liposomal doxorubicin and biosimilar bevacizumab` correctly refuses both. [Two-product controls](names_attack.json). The m3 hyphenated control `paclitaxel with albumin-bound nanoparticles` also still leaks PACLITAXEL: its one-token qualifier cannot extend across the pre-refused neighbour `with`. The unhyphenated fixed example is therefore not a general solution. [Exact prior control](names_new_boundaries.json).

**Required outcome:** single-token and multi-token qualification need one consistent binding process; already refused qualifier tokens must not make their own qualified drug available as a positive hit.

## No-relink and question-answering assessment

The refusal blockers above reproduce even when matched spans may be relinked in an otherwise identical HEAD linker. They are not caused by the no-relink repair.

- All **7 actual demo questions**, sent over HTTP, have complete response objects identical to the original `bfcb83d` query module. They are also identical to immediate predecessor `574097f` in the focused QA comparison. [HTTP demo evidence](demo_results.json), [focused comparison](names_attack.json).
- Across **2,584 unique multi-token alias keys**, 402 entity lists change; none changes the first accepted identity or introduces a new Drug. The common change removes an embedded parent Drug/company name. Bare salt/full-name identity is preserved. [Alias comparison](names_attack.json).
- The isolated counterfactual uses HEAD's exact helpers, dictionaries and data, and changes only `(refused | matched)` back to `refused` in the overlap guard (`src/query.py:168`). **1,648 questions**: 28 completely identical, 1,596 entity-metadata-only changes, 24 semantic changes, 0 exceptions. It covers the **400 alias keys changed specifically by this toggle × four QA templates, plus 48 company/target/mixed controls**. This differs from the 402 aliases changed by the full previous-to-current repair comparison above. [Reproducer](qa_relink_sweep.py), [all inputs and changed answers](qa_relink_sweep.json).
- The 24 semantic changes remove a Company read from inside a stored full Drug alias, switching `company_portfolio` to `drug_profile`. For example `Tell me about GSK 1120212` previously used nested GSK and returned 12 GlaxoSmithKline portfolio rows; current returns TRAMETINIB's three profile/mechanism rows. `Tell me about EPOETIN BETA` stops treating BETA as company `ORG:beta`. These changes agree with the stored full aliases; they are not adverse regressions found by this review.
- Explicit `What trials evaluate erlotinib hydrochloride and erlotinib?` still links both separately named records. Multi-entity target/company questions and mixed accepted/refused inputs were checked separately; passing demo/salt checks do not excuse the subject-switch failures above.

**Conclusion for this isolated change:** no adverse no-relink QA regression was found in the exercised corpus. This is a bounded result, not proof for every possible sentence.

## Should-fix items and remaining successful checks

1. **Inherited over-refusal of a neighbouring target/company.** `EGFR biosimilar bevacizumab` and `AstraZeneca biosimilar bevacizumab` refuse the entire input; the reversed forms retain EGFR/AstraZeneca. The generic-version equivalents now retain the target/company. This follows the unconditional immediate-neighbour rule at `src/query.py:149-151`; it does not identify the neighbour's type or syntactic role. A `with` between the target/company and qualifier also preserves them. No invented edge is needed for this usability failure. [Order comparisons](names_attack.json), [HTTP with controls](attack_http.json).
2. **Unchanged qualifications:** unsupported lowercase IDs/Investigator names, raw malformed-request errors, empty-form retention and numeric Infinity are marked NOT FIXED above. None is treated as a new repair regression or an invalid numeric value actually drawn.
3. **Stored graph guarantees hold in the checked snapshot.** Seven retired nodes, 142 retired edges, zero live edges with retired endpoints, no self-loops. All six node types are covered. PARENT_OF, STUDIES, ASSOCIATED_WITH, EVALUATES, ACTS_ON and role-aware SPONSORS match their endpoints. Trial details, sponsor count/class, Drug global count/max phase and actions match stored values. [Exhaustive evidence](db_validate.json), [snapshot facts](db_snapshot_facts.json).
4. **Chunking and size:** the 1,001-Drug fixture crosses three count batches with count/weight 1 for every item. Disease MONDO_0005233 returns 2,774 Trials + 300 Targets, 30 each, **18,575 bytes in 72.117 ms** in the recorded call. **24 concurrent requests / 12 workers**, all expected 200 shapes, **598.259 ms** total. These are local samples, not load benchmarks. [Fixtures](db_fixtures.json), [HTTP](http_results.json).
5. **No writes or model calls on exercised application paths.** Explore issues reads; `Engine.ask` explicitly uses `use_llm=False` (`src/app.py:180-181`). The app does not globally open SQLite read-only, so this is a path/integrity observation rather than a database-permission guarantee.

## Standards axis and integrity

No tracked AGENTS/CONTRIBUTING/CODING/docs/agents standards source was found. **Standards findings: 0 documented violations.** User evidence/no-tracked-edit instructions were followed. KOA Studio / KhOpenApi code-change comparisons do not apply because no application code was changed. [Separate standards review](standards_findings.md).

All review-created files are under `audit_evidence_claims/m4/`; pre-existing `brief.md` and the live session `log.txt` were not edited by audit scripts. No tracked/staged diff was introduced. Real DB SHA-256 remains `7341c5a7089731f67356da5a588b269d4b69e8e6c4c054acf19aa4ef2837b529`. Audit-owned servers on 8880 and 8881 are closed. [Final integrity](integrity.json), [main server](http_lifecycle.json), [supplemental server](supplemental_http_lifecycle.json), [attack server](attack_http_lifecycle.json), [browser-test server](browser_lifecycle.json).

**Specification findings: 3 blocking mechanisms — two new regression mechanisms plus an inherited qualifier-extension bypass — and the separately listed should-fix qualifications.** The exact old named m1/m2b/m3 blockers pass; four m3 supplementary inputs develop originator leaks (the two punctuation cases previously refused too broadly). No remediation was applied.

## Reproduction entry points

Run from repository root. All outputs remain under m4; fixtures are in memory. The three CLI HTTP runners own port 8880 and must run sequentially. Supporting scripts and their commands are also documented in [data findings](db_findings.md), [names/QA findings](names_findings.md), and [UI findings](ui_findings.md).

```text
python -B audit_evidence_claims/m4/run_verification.py
python -B audit_evidence_claims/m4/run_http.py
python -B audit_evidence_claims/m4/supplemental_http.py
python -B audit_evidence_claims/m4/attack_http.py
python -B audit_evidence_claims/m4/db_recheck.py
python -B audit_evidence_claims/m4/db_role_fallback.py
python -B audit_evidence_claims/m4/db_missing_sponsor_count.py
python -B audit_evidence_claims/m4/db_score_fixture.py
python -B audit_evidence_claims/m4/db_numeric_fixture.py
python -B audit_evidence_claims/m4/names_reproduction.py
python -B audit_evidence_claims/m4/names_regressions.py
python -B audit_evidence_claims/m4/names_boundary_details.py
python -B audit_evidence_claims/m4/names_new_boundaries.py
python -B audit_evidence_claims/m4/names_attack.py
python -B audit_evidence_claims/m4/names_final_checks.py
python -B audit_evidence_claims/m4/names_separator_checks.py
python -B audit_evidence_claims/m4/qa_relink_sweep.py
python -B audit_evidence_claims/m4/ui_collect.py
node audit_evidence_claims/m4/ui_harness.js
node audit_evidence_claims/m4/ui_regressions.js
node audit_evidence_claims/m4/ui_missing_sponsor_count.js
node audit_evidence_claims/m4/ui_demos.js export
python -B audit_evidence_claims/m4/ui_demos_collect.py
node audit_evidence_claims/m4/ui_demos.js
node audit_evidence_claims/m4/ui_m3_checks.js
python -B audit_evidence_claims/m4/ui_assertions.py
python -B audit_evidence_claims/m4/integrity_check.py
```

VERDICT: CHANGES REQUIRED
