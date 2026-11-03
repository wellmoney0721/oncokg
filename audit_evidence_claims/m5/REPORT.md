# Independent relation-map review — round 5

Reviewed HEAD: `514929c83fb7ab8cdd23fdd50eb300bd409c3250`, 2026-11-03. Immediate predecessor: `bf436c6`; cumulative repair comparison: `git diff bfcb83d...HEAD`. Specification: the user's round-5 brief, original approval bar, [m1](../m1/REPORT.md), [m2b](../m2b/REPORT.md), [m3](../m3/REPORT.md), [m4](../m4/REPORT.md), and `CODEX_MAP_M1_VERDICT.md`.

**Approval remains blocked by two independently reproduced product-refusal bypasses.** An attached separator defeats a suffix refusal; a listing word can detach a formulation qualifier from its sole drug. Both draw the refused product's originator and return that originator's QA evidence. Exact predecessor comparisons show both are inherited bypasses, newly identified here, rather than newly introduced by this commit. All previously named blockers are FIXED for their exact inputs under the revised fail-closed policy.

The new implementation also merges drug aliases across its own comma/semicolon boundaries. This can select the wrong salt or suppress a valid drug alone in another item. Those findings, a lone-alias rejection, and input cost are separated from the decisive product-refusal blockers below. Ordinary over-refusal of drugs sharing one item is **accepted behavior**, not a finding.

## Verification, evidence and limits

- Requested suite: `python -m pytest tests -q -p no:cacheprovider` — **326 passed in 16.03 s**, exit 0. Bytecode disabled; test temporary files confined to m5. [Output](pytest.txt), [environment/hashes](pytest_summary.json).
- Reused previous scripts by copying/adapting them into m5. Replayed **62 original name cases**, 14 additional probes, 13 prior mixed-name regressions, 30 m3 supplemental controls, all 45 m4 attacks, 37 varied QA inputs and 2,584 multi-token alias keys. The old 1,648-question no-relink isolation sweep also completed with 0 exceptions. [Execution manifest](names_replay_execution.json), [name coverage and dispositions](names_findings.md). Two old name-script HTTP helpers were adapted to direct Engine calls; their simulated status fields are not counted as HTTP evidence.
- Started the unchanged CLI app on **8880**, exercised `GET /`, `/api/explore`, `/api/resolve`, `/api/ask` and `/api/check`, and stopped every owned server. All original HTTP probes, previous blocker inputs and new decisive cases were sent to the actual server. [Original HTTP](http_results.json), [m1/m2b regressions](regression_http.json), [m3](supplemental_http.json), [m4](attack_http.json), [m5](m5_http.json), [cross-item HTTP](cross_item_http.json).
- New name coverage: **113** boundary/qualifier inputs, **7,511 unambiguous stored alias keys**, followed by **49** focused exact-predecessor comparisons. The predecessor comparator restores `link_entities`, `_drug_spans`, `_qualified_drug_spans` and `_JOINERS` from `bf436c6`; remaining code/data stay current. [Scan](names_m5_attack.json), [alias summary](names_m5_summary.json), [focused comparisons](names_m5_confirm.json). An independent 27-input review reproduced the conjunction defect. [Independent probe](ui_boundary_probe.json).
- Independently checked **all 6,469 live centres**, **22 relation/role/direction/type combinations**, against stored adjacency, values, counts, grouping and ordering: **zero mismatches**, 153.811 s. All six reused DB scripts succeeded; **19/19** additional assertions passed. Retirement/corruption fixtures used memory databases. [Validator](db_recheck.py), [results](db_validate.json), [fixtures](db_fixtures.json), [assertions](db_assertions.json).
- Executed the actual page script in a Node VM: 16 fresh maps, all **36** page examples, **42** example click callbacks, four render-error routes and **24/24** aggregate assertions. Five shared HTTP maps equal direct Engine results; served HTML equals `web/try.html`. [UI findings](ui_findings.md), [assertions](ui_assertions.json).
- **No real-browser interaction, paint/layout validation or browser-executed XSS test completed.** Browser discovery reported `The browser access host is unavailable`; native Chrome selection reported `Computer Use was not approved to use Google Chrome`. Generated markup, script state and HTTP were verified; actual-browser execution is not claimed. [Attempt](browser_attempt.json). Dark mode was excluded.

## Previous findings — exact reproduction dispositions

FIXED means that specific prior failure no longer reproduces; it does not certify every possible product description. NOT FIXED qualifications below remain non-blocking unless expressly identified otherwise.

### M1

| Finding / exact reproduction | Disposition | Current evidence and source |
|---|---|---|
| B1: `bevacizumab - awwb`; `89Zr - trastuzumab`; `[89Zr] trastuzumab`, compact controls | **FIXED** | Refused, no originator centre. `src/query.py:128-172`; [HTTP](regression_http.json), [name replay](names_reproduction_results.json). |
| B2: collaborator called lead, `NCT00200395`, reverse `ORG:genentech` | **FIXED** | Genentech collaborator, Montefiore lead; reverse roles preserved. `src/app.py:137,160-169`; `web/try.html:142-149`; [DB](db_validate.json), [UI](ui_harness_results.json). |
| B3: Investigator called institution, `NCT00754364`, `ORG:armandosantoromd` | **FIXED** | `책임 주관 연구자 (lead sponsor)`. `web/try.html:143,148`; [UI](ui_harness_results.json). |
| B4: retire CHEMBL3353410 in memory; query `osimertinib`, ID and `EGFR` | **FIXED** | Name/ID not_found; retired neighbour excluded. `src/app.py:115-118`; [real-handler fixture](db_retired_center.json). |
| Retired-Trial counts: live D, retired T, live T→EVALUATES→D and D→ACTS_ON→X | **FIXED** | D centre/neighbour count and weight 0; T excluded. `src/app.py:129-132,139,174`; [fixture](db_fixtures.json). |
| S1: misleading evidence order, especially `MONDO_0005233` | **FIXED** | Trial start-date, disease-target score, trial-count and A–Z sorts stated correctly; group totals descend. `src/app.py:141-170`; `web/try.html:148-158,231-235`; [DB](db_validate.json), [UI](ui_harness_results.json). |
| S2: silent ring cuts, CHEMBL1201438 / Disease / AstraZeneca | **FIXED** | 22/25, 39/3,074 and 41/145 disclosed; list cuts say 30 retained. No whole nonempty group lost in exercised maps. 40 is a soft allocation target. `web/try.html:191-204,233`; [UI](ui_harness_results.json). |
| S3: osimertinib→EGFR then Mvasi, unknown name, server/network failure; obsolete back callback | **FIXED** | Trail clears; old callback harmless; successful back works. `web/try.html:213-216,243-244`; [UI](ui_harness_results.json). |
| S4: EGFR/KRAS completed backwards; duplicate EGFR | **FIXED** | Latest KRAS remains; stale success/error ignored; duplicate requests leave one trail entry. `web/try.html:211-214`; [UI](ui_harness_results.json). |
| S5: `Roche`, `MET`, `osimertinib EGFR`, reverse; `Mvasi and bevacizumab` | **FIXED for exact inputs** | Reading, alternatives and refusal disclosed, including stored FOLIC ACID/METFORMIN alias collisions. `src/app.py:95-114`; `web/try.html:222-226`; [names](names_reproduction_results.json), [UI](ui_harness_results.json). |
| S6: AGONIST / BINDING AGENT / sponsor-class specificity | **FIXED** | Specific gloss plus stored action/class codes. `web/try.html:162-176`; [UI](ui_harness_results.json). |
| S7: Trial start; sponsor→Drug global count/phase; zero-trial Drug | **FIXED** | NCT00200395 start 2003-07-02; AstraZeneca→osimertinib sponsor 14, graph 79, APPROVAL; CHEMBL925 count 0. `src/app.py:138-149,171-177`; `web/try.html:173-174,228-229`; [DB/UI](ui_harness_results.json). |
| S8: node/edge props `null`, `[]`, `{broken` | **FIXED** | All 12 original requests and restored controls succeed. `src/app.py:135,171,211-217`; [fixtures](db_fixtures.json). |
| URL/markup: javascript/data URLs, hostile labels/titles/node and edge IDs | **FIXED for exercised map paths** | HTTPS registry allowlist rejects tested spoof forms; text/attributes escaped. Browser limitation above applies. `web/try.html:104,180,199,221-235`; [payloads](ui_harness_results.json), [assertions](ui_assertions.json). |
| Unknown-type tooltip Other / NEWREL | **FIXED** | Raw fallback without undefined. `web/try.html:158,199,227`; [UI](ui_regressions.json). |
| Module “All three” / “everything” overclaims | **FIXED** | `All of them`, `a capped list per relation`, `src/app.py:5-11`. |
| Silent cut: `"x"*500 + " osimertinib"`; `"osimertinib " + "x"*600` | **FIXED** | HTTP 400, longer than 500 characters; no partial map. `src/app.py:239-242`; [HTTP](http_results.json). |
| Lowercase IDs / Investigator names: `nct00200395`, `chembl3353410`, `Armando Santoro Md` | **NOT FIXED — unchanged usability limitation** | Canonical IDs work; these forms remain not_found. [Fresh controls](names_unsupported_forms.json). |
| JSON list/null, malformed JSON, >20,000-byte body | **NOT FIXED — unchanged error-detail qualification** | Controlled 400 still exposes `.get`/parse details; subsequent valid calls succeed. `src/app.py:237-239,267-269`; [HTTP](http_results.json). |

### M2b

| Finding / exact reproduction | Disposition | Current evidence and source |
|---|---|---|
| R1: `osimertinib and generic version of bevacizumab`, reverse/comma; trial/sponsor QA | **FIXED** | Only separately listed osimertinib links; QA starts its EVALUATES / AstraZeneca SPONSORS_TRIAL_OF evidence. `src/query.py:128-172`; [HTTP](regression_http.json), [QA](supplemental_http.json). |
| R1 over-refusal: `[89Zr] trastuzumab and osimertinib`, reverse; `osimertinib and oral azacitidine` | **FIXED** | Separately listed osimertinib survives. [Names](names_regressions.json), [replay](names_reproduction_results.json). |
| Inherited `What is the generic version of bevacizumab?` | **FIXED** | Refused with no centre. [HTTP](supplemental_http.json). |
| R2: ORG:alaunos→SPONSORS_TRIAL_OF→CHEMBL1201438 props null/list/broken, both endpoints | **FIXED** | `evidence_trials:null`, weight 0; UI says count not recorded. Actual zero displays zero. `src/app.py:141-146`; `web/try.html:173`; [API](db_missing_sponsor_count.json), [UI](ui_missing_sponsor_count.json). |
| Boolean association scores / render failure | **FIXED** | API null/weight 0; injected booleans do not crash rendering. `src/app.py:152-155,207-208`; `web/try.html:176`; [API](db_score_fixture.json), [UI](ui_regressions.json). |
| Undisclosed score rounding, EGFR / KRAS | **FIXED** | Exact 0.8883707400322897 / 0.8337881598550857 shown. `web/try.html:176`; [UI](ui_regressions.json). |
| Embedded company fixture `companies['sharedbrand']=['ORG:astrazeneca','ORG:roche']`; `Sharedbrand company` | **FIXED** | Roche appears in also; production has no multi-ID company key. `src/app.py:97-102`; [fixture](names_boundary_details.json). |
| Module wording / successful-input truncation | **FIXED** | Capped-list description and explicit over-limit rejection, as above. |
| Render exceptions: Trial `props.phases='PHASE2'` | **FIXED for UI entry points** | Form/node/back/example show failure, clear trail, recover on KRAS; stale malformed response ignored. `web/try.html:238-248`; [four routes](ui_m3_checks.json). |
| Missing/unknown sponsor role; equal-weight A–Z | **FIXED** | Neutral missing-role wording, both directions; correct tie sorting. `web/try.html:147-149`; `src/app.py:166-167`; [roles](db_role_fallback.json), [UI](ui_regressions.json), [order](db_validate.json). |

### M3, including supplementary controls

| Finding / exact reproduction | Disposition | Current evidence |
|---|---|---|
| B1: `paclitaxel with albumin bound nanoparticles`, formulation variant; `generic version with bevacizumab` | **FIXED** | No originator centre; exact paclitaxel QA 0 evidence. `src/query.py:153-172`; [HTTP](supplemental_http.json). |
| B2: `What is the generic version of bevacizumab?` | **FIXED** | Whole item refused, no centre. [HTTP](supplemental_http.json). |
| Comma over-refusal: `osimertinib, liposomal doxorubicin`; `osimertinib, biosimilar bevacizumab`, reverses/QA | **FIXED for exact inputs** | OSIMERTINIB retained; trial QA has 12 osimertinib rows. [HTTP](supplemental_http.json). |
| Bare `erlotinib hydrochloride`; `Paclitaxel conjugate with poly-l-glutamic acid` | **FIXED / retained** | Correct complete alias identity; no nested parent relink; separately named parent still links. `src/query.py:174-198`; [controls](names_attack.json). |
| Supplementary `osimertinib with generic version of bevacizumab` | **FIXED under revised design** | Both same-item drugs refused. The old goal of retaining osimertinib here is superseded; not a should-fix. [HTTP](attack_http.json). |
| Supplementary `generic version of Paclitaxel conjugate with poly-l-glutamic acid` | **FIXED** | Refusal, no centre or qualified-product QA evidence. [HTTP](attack_http.json). |
| Supplementary `paclitaxel with albumin-bound nanoparticles` | **FIXED** | Hyphenated and unhyphenated forms refuse. [Replay](names_new_boundaries.json). |
| Supplementary semicolon/fullwidth comma: `osimertinib; generic version of bevacizumab`; `osimertinib， generic version of bevacizumab` | **FIXED** | Separate osimertinib survives; bevacizumab refused. [Separator replay](names_separator_checks.json). |
| Lowercase IDs / Investigator names / raw request-shape details | **NOT FIXED — unchanged** | Same m1 qualifications. |
| Empty/whitespace map form | **NOT FIXED — unchanged usability qualification** | No request; previous view remains. `web/try.html:241`; [UI](ui_m3_checks.json). |
| Positive/negative Infinity fixture | **NOT FIXED — unchanged, failure closed** | `_number` accepts Infinity; JSON encoding returns HTTP 400; no invalid number drawn. None in snapshot. `src/app.py:207-208,264-269`; [fixture](db_numeric_fixture.json). |

### M4

| Finding / exact reproduction | Disposition | Current evidence |
|---|---|---|
| B1 wrong shortest-span tie: `osimertinib with generic version of bevacizumab`, reversal / added `a`; exact trial/sponsor questions | **FIXED under revised design** | Whole item refused; both QA responses have 0 evidence. No BEVACIZUMAB centre. [HTTP](attack_http.json). |
| B1 punctuation cases `osimertinib; generic version of bevacizumab`, fullwidth comma | **FIXED** | Separate osimertinib survives. [Replay](names_separator_checks.json). |
| B2 six-token cap: qualified long poliglumex alias and `generic version of the monoclonal antibody bevacizumab`; exact QA | **FIXED** | No distance cap; all refuse with 0 qualified-drug QA evidence. Bare poliglumex still links. [HTTP](attack_http.json). |
| B3 consumed qualifier: `biosimilar version of bevacizumab`; `liposomal formulation of doxorubicin`; `paclitaxel with albumin-bound nanoparticles`; two-product combination | **FIXED** | No parent drug hit; respective QA evidence empty. [HTTP](attack_http.json), [full replay](names_attack.json). |
| Target/company collateral refusal: `EGFR biosimilar bevacizumab`; `AstraZeneca biosimilar bevacizumab`, reversed/with controls | **FIXED** | EGFR/AstraZeneca link; drug refusal disclosed. [HTTP](m5_http.json), [replay](names_attack.json). |
| No-relink QA assessment | **FIXED / retained behavior** | Replayed 1,648 questions: 28 identical, 1,596 metadata-only differences, 24 semantic differences, 0 errors versus HEAD with matched-token exclusion disabled. Semantic differences remove nested company matches inside complete drug aliases, as previously documented. [Sweep](names_qa_relink_sweep.json). |
| Lowercase IDs, raw request errors, blank submit, Infinity | **NOT FIXED — unchanged qualifications** | Same individual rows above; none presents an invalid graph value or a new product bypass. |

## Blocking findings

### M5-B1 — P1: attached separator hides a known refused suffix

Exact unchanged-server request:

```json
{"text":"bevacizumab-awwb/ osimertinib"}
```

`POST /api/explore` returns HTTP 200 with **BEVACIZUMAB / CHEMBL1201583**, **122 trials**, OSIMERTINIB only in `also`, and **no refusal**. The linker reports `matched_text:'bevacizumab-awwb/'`, `matched_alias:'Bevacizumab awwb'`.

The identical input at `/api/resolve` yields `bevacizumab-awwb: BLOCKED_DISTINCT_PRODUCT` and `osimertinib: EXACT / CHEMBL3353410`. Bare `bevacizumab-awwb` is refused. Thus the test names a product the repository itself refuses; no external pharmacology assumption is needed. [Actual HTTP responses](m5_http.json), [exact current/predecessor linkage](names_m5_confirm.json).

| Exact `/api/ask` text | Current evidence |
|---|---|
| `Which trials evaluate bevacizumab-awwb/ osimertinib?` | 12 rows, first `NCT00955305\|EVALUATES\|CHEMBL1201583\|NCT00955305` |
| `Which companies sponsor bevacizumab-awwb/ osimertinib?` | 12 rows, first `ORG:roche\|SPONSORS_TRIAL_OF\|CHEMBL1201583\|` |

**Cause:** the splitter at `src/query.py:128-130` leaves `/` attached to the word; listing symbols are recognized only as whole tokens (`145-149`). `RE_BIOSIMILAR_SUFFIX` is anchored to the end of the string (`src/textrules.py:156-157,213-223`), so the extra slash defeats it. No contiguous *word* run removes that slash. Alias matching then calls `canonical_key`, which discards punctuation (`src/textrules.py:339-346`; `src/query.py:182-197`), recovering the originator alias after the guard missed it. `Engine.explore` trusts that hit (`src/app.py:88-95`).

`bevacizumab - awwb/ osimertinib` and `bevacizumab-awwb| osimertinib` also leak over HTTP. With spaces on both sides of `/`, the guard recognizes the suffix and HEAD refuses the entire item; semicolon or `and` correctly preserves only osimertinib. The whole-item slash refusal is accepted under the user's rule, not counted as over-refusal. Exact `bf436c6` comparison reproduces the attached-slash leak: **inherited, not introduced by HEAD**.

**Required outcome:** punctuation that alias normalization removes must not hide a refusal. Never map or answer for CHEMBL1201583 from this refused component. Retaining the separately recognized osimertinib or refusing an ambiguous combined item can both be safe outcomes; selecting BEVACIZUMAB cannot.

### M5-B2 — P1: a listing word inside one product description detaches its qualifier

Exact input **`liposomal and nanoparticle formulation of doxorubicin`** returns HTTP 200 with **DOXORUBICIN / CHEMBL53463**, **3 trials**, and `also:[{"refused":"liposomal"}]`. The full-string resolver returns a single **BLOCKED_DISTINCT_PRODUCT** component with no accepted drug. `and` joins descriptions of one formulation here; it does not introduce another named drug. [HTTP](m5_http.json), [independent reproduction](ui_boundary_probe.json).

`Which trials evaluate liposomal and nanoparticle formulations of doxorubicin?` returns **3 originator trial rows**, beginning `NCT01970540|EVALUATES|CHEMBL53463|NCT01970540`. The singular QA version independently yields the same three rows. The singular/plural map forms and `liposomal and sustained release doxorubicin` also fail. [Actual QA](m5_http.json), [independent singular QA](ui_boundary_probe.json).

**Cause:** `_JOINERS` (`src/query.py:94-95`) and the unconditional boundary at `146-149` isolate `liposomal` before examining the drug. The scan at `156-164` only considers words within one resulting item; nothing in the second item matches the current refusal patterns, so DOXORUBICIN remains a positive hit (`190-198`). The full product predicate recognizes the original phrase via `liposomal` (`src/textrules.py:148,207-208`). The fail-closed rule cannot protect a qualifier the splitter has already detached.

This is a different mechanism from the attached-punctuation bypass. It also occurs with the exact previous linker, so it is **inherited**, now confirmed against the changed design. Ordinary `liposomal doxorubicin and osimertinib` is not the requested failure case: separate named products should retain their isolation. No over-refusal of a valid same-item drug is alleged here.

**Required outcome:** a conjunction inside a single qualified product must not make its originator acceptable. If such a phrase cannot be resolved safely, refuse its drug. Preserve the successful separate-drug mixed-input controls.

## Should-fix findings, separate from the approval blockers

### M5-S1 — P2: alias matching crosses the very list boundaries used for refusal

Two complementary effects share a cause:

1. **A valid drug alone in its own item disappears.** `biosimilar anastrozole, Arimidex` returns only `refused:'biosimilar anastrozole'`. Its second item is a valid standalone alias: `Arimidex` and `biosimilar anastrozole and Arimidex` both select **ANASTROZOLE / CHEMBL1399**. The resolver gives a refused first component and `Arimidex: ALIAS / CHEMBL1399`; the exact predecessor retains Arimidex. Current comma QA has **0** evidence versus standalone Arimidex's **2** rows. `biosimilar Prolia, xgeva` similarly loses the separately listed Xgeva, while Xgeva alone returns DENOSUMAB / CHEMBL1237023 and **3** trial rows. These are actual CLI HTTP reproductions. [HTTP](cross_item_http.json), [prior/current comparison](names_m5_confirm.json), [extra controls](names_cross_item_refusal.json).
2. **A different salt identity is assembled from two items.** `Erlotinib, hydrochloride biosimilar bevacizumab` now selects **ERLOTINIB HYDROCHLORIDE / CHEMBL1079742**, **31 trials**, while declaring the second item refused. The exact predecessor and current full resolver preserve first-item **ERLOTINIB / CHEMBL553**, **118 trials**. The semicolon form repeats the wrong-salt selection; the `and` form preserves the parent. Trial QA returns 12 salt rows, first `NCT00445848|EVALUATES|CHEMBL1079742|NCT00445848`. This is a constructed list-contract test, not a claim that hydrochloride bevacizumab is a marketed product. [HTTP](m5_http.json), [comparison](names_m5_confirm.json).

`_drug_spans` receives only listing-word positions to skip (`src/query.py:155`); it has no clause/segment boundaries (`231-248`). Aggressive keys join `anastrozole Arimidex` into the stored `anastrozole (arimidex)` alias, or `Erlotinib hydrochloride` across a comma. Line **165** assigns the entire span using only `seg[a]`. A qualifier in its first item refuses tokens in the second; a qualifier in its second item misses the span assigned to the first. The final positive matcher also joins windows without segment checks (`174-198`). This is **new versus bf436c6** for the cited inputs.

The Arimidex/Xgeva cases satisfy the user's explicit should-fix exception: the valid alias is **alone in its own item**. They are not ordinary intended same-item over-refusals. Keep both refusal discovery and accepted-name matching within the same item boundaries; do not borrow words from a refused item to build another identity.

### M5-S2 — P2: an intrinsic qualifier rejects a valid lone stored alias

**`Pegylated interferon alfa-2a`** is a unique stored ChEMBL synonym of **CHEMBL1201560 / PEGINTERFERON ALFA-2A**. Used alone, HEAD refuses it. The canonical name `PEGINTERFERON ALFA-2A` and exact node ID both draw that live drug. The previous linker reached the same drug through residual `alfa-2a`, accompanied by an incomplete refusal; HEAD now produces no map. Of 7,511 unambiguous alias keys, this is the only newly refused previously linked lone alias. [Stored alias/comparison](names_m5_summary.json), [HTTP controls](m5_http.json).

The full resolver already blocks the synonym via `pegylated`, so this is a **shared dictionary/guard inconsistency**, not a new resolver disagreement. The alias names the stored pegylated drug itself; no originator substitution is demonstrated. It is should-fix under the explicit lone-valid-alias test, and does not block a demo. Do not generalize this into accepting every known alias before product guards: the B1 suffix alias shows why such an exemption would be unsafe. Relevant logic: `src/textrules.py:148,207-208`; `src/query.py:153-168`.

### M5-S3 — P2: all-substring refusal scan creates substantial input cost under the global lock

For an unqualified item containing n tokens, `src/query.py:161-163` tries n(n+1)/2 word runs. Constructing and scanning their strings incurs cubic aggregate character work for equal-length tokens. The scan runs even without any drug. Instrumented exact-predecessor/current runs use the same inputs/data; times are local observations, not universal performance guarantees. [Reproducer](perf_probe.py), [results](perf_results.json).

| Exact constructed input | Characters | bf436c6 linker | HEAD linker |
|---|---:|---:|---:|
| `" ".join(["x"] * 50)` | 99 | 0.0012 s | 0.0220 s |
| `" ".join(["x"] * 100)` | 199 | 0.0022 s | 0.1332 s |
| `" ".join(["x"] * 200)` | 399 | 0.0046 s | 0.9778 s |
| `" ".join(["x"] * 250)` | 499 | 0.0064 s | 1.7907 s |
| `" ".join(["x"] * 500)` — direct API | 999 | 0.0116 s | 18.3512 s |
| `" ".join(["x"] * 1000)` — direct API | 1,999 | 0.0249 s | worker exceeded 20 s; stopped |

At 250 tokens HEAD makes **31,625 calls to each predicate**, processing **10,479,750 aggregate characters** across the two predicates, versus 250 calls each / 500 characters in the predecessor. A single 500-character word takes 0.0073 s; 250 semicolon-separated x items take 0.0102 s; a late biosimilar qualifier short-circuits at 0.0225 s. This is token/run growth, not simply request byte length.

Uninstrumented HTTP confirmation: the allowed 499-character input took **1.8472 s** in `/api/explore`, **2.2104 s** in `/api/ask`; adding a valid osimertinib within 499 characters took **2.1657 s**. Four simultaneous allowed inputs completed in **7.9315 s**, with individual latencies up to **7.9215 s**. A normal EGFR request dispatched 0.1 s after one long lookup took **1.8568 s**, versus **0.0366 s** after it completed. The actual server holds `engine.lock` during linking (`src/app.py:247-263`). A 501-character text is promptly rejected, as intended. [Raw HTTP measurements](perf_http.json).

The 500-character text cap does not bound every caller: `/api/check` allows a 4,000-character answer (`src/app.py:260`), which is relinked by `check_groundedness` (`src/query.py:605-608`). With `{"text":"EGFR","answer":" ".join(["x"]*500)}`, the 999-character answer exceeded a **5-second** client timeout; the following ordinary EGFR map exceeded its **2-second** timeout while GET `/` still succeeded. The owned process was then terminated. These are bounded observations, **not a completed latency or permanent-deadlock claim**. [Exact payload/results](perf_check_http.json), [cleanup](perf_check_lifecycle.json).

Preserve refusal coverage while avoiding exhaustive reconstruction of every word run, and cover the answer-field caller when bounding work. This is should-fix performance evidence, separate from originator leaks.

## Demos, mixed inputs and other successful checks

- All **36 page examples** render successfully: 13 resolver, 7 QA, 9 prose-check, 7 structured-check. All 42 demo/map-example callbacks pass. **35/36 complete demo payloads equal m4**; the sole difference is the Mvasi refusal span expanding to the whole item. Its intent, answer, checks and empty evidence remain unchanged. No demo is unexpectedly blocked. [Comparison](ui_demo_compare.json), [responses](ui_demos_responses.json), [click/render tests](ui_m3_checks.json).
- Seven actual HTTP QA demos retain evidence counts **12, 12, 11, 1, 12, 0, 0**. Six complete responses equal bfcb83d; Mvasi differs only in refusal metadata. [HTTP comparisons](http_demo_results.json). Passing demos do not excuse the mixed-input subject errors above.
- `Which trials evaluate osimertinib and biosimilar bevacizumab?` retains 12 osimertinib rows; the corresponding sponsor question starts AstraZeneca→SPONSORS_TRIAL_OF→CHEMBL3353410. `EGFR biosimilar bevacizumab` and `AstraZeneca biosimilar bevacizumab` retain the target/company. The same-item `osimertinib with generic version of bevacizumab` now correctly refuses both drugs. [HTTP](m5_http.json), [m4 replay](attack_http.json).
- Tested missed separators include newline/tab, slash/pipe, bullets, Arabic comma/semicolon, halfwidth ideographic comma, full stops and phrases such as `as well as`. When they leave multiple drugs in one item and the qualifier is detected, the resulting whole-item refusal is **not reported as should-fix**. The attached-suffix leak is distinct: it accepts the forbidden originator. [113 cases](names_m5_attack.json).
- Graph snapshot: 7 retired nodes, 142 retired edges, no live edges with retired endpoints and no self-loops; all six node types covered. Trial phase/status/start/title/url, sponsor count/class, Drug global count/max phase, action and association score match stored values. PARENT_OF, STUDIES, ASSOCIATED_WITH, EVALUATES, ACTS_ON and role-aware SPONSORS directions agree with stored endpoints. [Exhaustive evidence](db_validate.json), [snapshot](db_snapshot_facts.json).
- A 1,001-Drug fixture crosses three count batches and returns every item with count/weight 1. Ordinary Disease HTTP returns 2,774 Trials + 300 Targets, 30 each, **18,575 bytes in 94.144 ms**. Original **24 requests / 12 workers** all return expected 200 shapes in **556.975 ms**. These ordinary local samples are separate from the long-input tests. [Fixtures](db_fixtures.json), [HTTP](http_results.json).
- README command wording remains accurate at `README.md:566` / `README.ko.md:387`. The detailed map promises still fail for B1/B2 (`src/app.py:74-76`; `web/try.html:215`). No new wrong edge, relation direction, stored value or executable-markup path was identified in the exercised map paths; browser-executed XSS remains unverified.

## Standards, integrity and reproduction

**Standards axis: 0 documented violations.** No tracked AGENTS/CONTRIBUTING/CODING/docs/agents rules were found. The supplied evidence and no-tracked-edit instructions govern the review. KOA Studio / KhOpenApi code-change comparisons do not apply because no application code was changed. [Separate standards review](standards_findings.md).

All review-created files are under `audit_evidence_claims/m5/`. Pre-existing brief/log files were left alone by audit scripts. No model was called on the exercised application paths; `Engine.ask` explicitly uses `use_llm=False` (`src/app.py:180-181`). SQLite is not globally opened read-only by the application, so this is path/integrity evidence, not a database-permission guarantee. Final HEAD, tracked/staged diff checks, source/database hashes and report links: [integrity.json](integrity.json). Database SHA-256 remains `7341c5a7089731f67356da5a588b269d4b69e8e6c4c054acf19aa4ef2837b529`.

Run from the repository root. CLI HTTP runners own/close 8880 and must run sequentially. The names preparation script copies prior reproducers into m5 and executes them. Supporting DB/UI reports list the individual reused fixture/harness commands.

```text
python -B audit_evidence_claims/m5/run_verification.py
python -B audit_evidence_claims/m5/run_http.py
python -B audit_evidence_claims/m5/supplemental_http.py
python -B audit_evidence_claims/m5/attack_http.py
python -B audit_evidence_claims/m5/names_prepare.py
python -B audit_evidence_claims/m5/names_m5_attack.py
python -B audit_evidence_claims/m5/names_m5_confirm.py
python -B audit_evidence_claims/m5/m5_http.py
python -B audit_evidence_claims/m5/cross_item_http.py
python -B audit_evidence_claims/m5/perf_probe.py
python -B audit_evidence_claims/m5/perf_check_http.py
python -B audit_evidence_claims/m5/db_recheck.py
python -B audit_evidence_claims/m5/db_assertions.py
python -B audit_evidence_claims/m5/ui_assertions.py
python -B audit_evidence_claims/m5/integrity_check.py
```

**Specification disposition: two blocking refusal mechanisms; three separate should-fix groups; all exact previously named blockers fixed under the revised policy. No remediation applied.**

VERDICT: CHANGES REQUIRED
