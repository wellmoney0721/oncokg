# Independent relation-map review — round 3

Reviewed HEAD: `574097f67e0719c32bfdc0526133e649b1864993`, 2026-11-03. Latest repair comparison: `git diff c64f433...HEAD`; complete relation-map repair comparison: `git diff bfcb83d...HEAD`. Specification: [round-3 brief](brief.md), [m1 report](../m1/REPORT.md), [m2b report](../m2b/REPORT.md), and `CODEX_MAP_M1_VERDICT.md`.

**Approval remains blocked.** The exact m1 blockers and m2b R1/R2 reproductions are fixed, as are the previously listed should-fix items. However, the latest joiner exclusion introduces another refused-product-to-originator bypass: `paclitaxel with albumin bound nanoparticles` now draws PACLITAXEL and answers with its trial evidence. The unchanged resolver refuses that entire product description, and the immediately preceding linker refused it too. A previously documented generic-product question bypass also remains. No new page-script blocker was reproduced.

## Verification and limits

- Ran `python -m pytest tests -q -p no:cacheprovider`: **323 passed in 15.12 s**, exit 0, no warnings. Bytecode/cache writes were disabled and test temporary files confined to m3. [Output](pytest.txt), [environment and hashes](pytest_summary.json).
- Started the unchanged application twice, sequentially, with `python -B -u src/app.py 8879`. Replayed every m1 HTTP case and the m2b regression cases, then independently confirmed new name cases and ten UI payloads. GET `/` was byte-identical to `web/try.html`; all ten HTTP map responses equalled fresh UI fixtures. Both owned servers were stopped and port closure verified. [Original HTTP replay](http_results.json), [R1 replay](regression_http.json), [new HTTP cases](supplemental_http.json), [UI cross-check](ui_http_check.json), [first lifecycle](http_lifecycle.json), [second lifecycle](supplemental_http_lifecycle.json).
- Reran **62 original name/boundary inputs**, the additional m2b name probes/comparisons and embedded-company fixture. New comparisons restore only the exact `c64f433` `link_entities` method in a separate Engine, keeping current data and all other code identical. Scanned **21 stored alias records containing joiner words**; their answers were unchanged. [Name replay](names_reproduction_results.json), [m2b comparisons](names_regressions.json), [boundary fixtures](names_boundary_details.json), [new comparisons](names_new_boundaries.json).
- All **7 question demos** returned HTTP 200 and complete answer objects identical to the original `bfcb83d` query implementation. Page, CLI and dashboard question lists are covered. Passing these demos does not cover the product-specific counterexample below. [Full comparisons](demo_results.json).
- Independently checked **all 6,469 live centres**, covering **22 role-aware relation/direction/neighbour-type combinations**: **zero adjacency, value, total or ordering mismatches**. The oracle additionally checks the new `evidence_trials` field against stored values. [Validator](db_recheck.py), [results](db_validate.json).
- Executed the **entire current page script** in a Node VM, using 16 fresh map payloads and controlled response completion. All **36** resolver/question/prose/structured demos rendered; actual example callbacks for all 36 and the **6** map examples also passed. Render-error handling was exercised through all four map entry points. [UI replay](ui_harness_results.json), [demos](ui_demos_results.json), [callback/error checks](ui_m3_checks.json).
- Real-browser verification was unavailable: current discovery returned `The browser access host is unavailable`; selecting the returned native Chrome window was rejected with `Computer Use was not approved to use Google Chrome`. No browser input occurred. UI findings establish script behavior and generated markup, **not browser layout or browser-executed XSS**. [Recorded limitation](ui_m3_checks.json).
- No tracked file was edited. Review corruption/retirement fixtures used in-memory databases; pytest-created databases stayed in the configured m3 temporary directory. Alias mutations affected isolated Engine indexes. Review outputs are confined to m3. The application paths examined call no model. Final source/database hashes and Git checks are in [integrity.json](integrity.json).

## M1 disposition — every finding and qualification

`FIXED` means the identified reproduction no longer exhibits its reported defect; broader product-refusal failures are separately identified below.

| M1 finding / exact reproduction | Result | Current evidence and source |
|---|---|---|
| **B1**: `bevacizumab - awwb`; `89Zr - trastuzumab`; `[89Zr] trastuzumab`, plus unspaced controls | **FIXED** | Refusal, no centre, through the live HTTP handler. `src/query.py:164-178`; [HTTP replay](regression_http.json), [name replay](names_reproduction_results.json). |
| **B2**: `NCT00200395`; reverse `ORG:genentech` | **FIXED** | Genentech is collaborator, Montefiore lead sponsor; both directions preserve separate roles and correct wording. `src/app.py:137,160-169`; `web/try.html:142-149`; [DB](db_validate.json), [UI](ui_harness_results.json). |
| **B3**: `NCT00754364` / `ORG:armandosantoromd` | **FIXED** | Investigator type survives; incoming heading says `책임 주관 연구자 (lead sponsor)`. `web/try.html:143,148`; [UI](ui_harness_results.json), [DB](db_validate.json). |
| **B4**: retire `CHEMBL3353410` in memory; request `osimertinib`, its ID, and `EGFR` | **FIXED** | Name and ID return not_found; EGFR excludes the retired neighbour. `src/app.py:115-118`; [real-handler fixture](db_retired_center.json). |
| **Retired-trial count**: live D, retired T, live T→EVALUATES→D and D→ACTS_ON→X | **FIXED** | D centre count and its count/weight in X are 0; T is absent. `src/app.py:129-132,139,174`; [fixture](db_fixtures.json). |
| **S1: misleading evidence ordering**, `MONDO_0005233` | **FIXED** | Trial start-date order, association-score order, graph/sponsor trial counts and name order are stated separately. Targets lead EGFR, KRAS, ALK. All group sizes/order and A–Z ties match the independent oracle. `src/app.py:141-169`; `web/try.html:148-158,231-235`; [DB](db_validate.json). |
| **S2: silent ring cut**, ALDESLEUKIN / Disease / AstraZeneca | **FIXED** | Explicitly 22/25, 39/3,074 and 41/145 drawn, respectively. Disease lists disclose 30 returned each. No exercised nonempty group is wholly lost. MAX=40 remains a soft target with no contrary UI promise. `web/try.html:185-204,233`; [UI](ui_harness_results.json). |
| **S3: stale trail**, osimertinib→EGFR→Mvasi/not-found/server/network error | **FIXED** | Trail state/markup clear; obsolete back callback is harmless. Successful back navigation works. `web/try.html:213-216,243-244`; [UI failure/back cases](ui_harness_results.json). |
| **S4: overlapping responses**, EGFR then KRAS completed in reverse; concurrent duplicate EGFR | **FIXED** | KRAS remains; stale success/error cannot overwrite it; duplicate concurrent EGFR requests yield one trail entry. `web/try.html:211-214`; [controlled completions](ui_harness_results.json). |
| **S5: silent identity ambiguity**, `Roche`, `MET`, `osimertinib EGFR`, reversed order | **FIXED** | Selected alias/reading and other entity are disclosed; `Mvasi and bevacizumab` also discloses the refused span. FOLIC ACID/METFORMIN selections themselves remain stored-alias behavior. `src/app.py:95-114`; `web/try.html:222-226`; [names](names_reproduction_results.json), [UI](ui_harness_results.json). |
| **S6: action/class specificity**, AGONIST, BINDING AGENT, sponsor classes | **FIXED** | Specific action gloss plus stored code, and INDUSTRY/NIH/FED/OTHER_GOV/NETWORK/OTHER/UNKNOWN codes are visible. `web/try.html:162-176`; [UI details](ui_harness_results.json). |
| **S7: omitted details**, Trial centre start; sponsor→Drug global count/phase; zero-trial Drug | **FIXED** | NCT00200395 shows `2003-07-02`; AstraZeneca→osimertinib shows 14 sponsor trials, 79 graph trials and approval; CHEMBL925 shows 0. `src/app.py:138-149,171-177`; `web/try.html:173-174,228-229`; [UI](ui_harness_results.json). |
| **S8: malformed props**, node/edge `null`, `[]`, `{broken` | **FIXED** | All 12 original requests and restorations return 200. Missing sponsor count no longer becomes factual zero; see R2 below. `src/app.py:135,171,211-217`; [fixtures](db_fixtures.json). |
| **URL/markup safety qualification**: javascript/data URLs; hostile labels, titles, node/edge IDs | **FIXED for exercised map paths** | Registry HTTPS allowlist protects centre/list links; scheme, host-prefix, credential and backslash spoof probes are rejected. Text/attributes stay escaped. `web/try.html:180,199,221-235`; [markup](ui_harness_results.json), [assertions](ui_regressions.json). Browser limitation above applies. |
| **Unknown-type tooltip**: `Other` / `NEWREL` fixture | **FIXED** | Raw type/relation fallback; no `undefined` tooltip. `web/try.html:158,199,227`; [UI](ui_regressions.json). |
| **“All three” and module “everything” overclaim** | **FIXED** | Introduction says `All of them` and explicitly describes a capped list per relation. `src/app.py:5-11`. |
| **Silent input truncation**: `"x"*500 + " osimertinib"`; `"osimertinib " + "x"*600` | **FIXED** | Both HTTP 400 with `input is longer than 500 characters`; no partial map. `src/app.py:239-242`; [HTTP cases](http_results.json). Direct Engine calls do not apply the HTTP input limit. |
| **Unsupported lowercase IDs / Investigator names**, e.g. `nct00200395`, `chembl3353410`, `Armando Santoro Md` | **NOT FIXED — unchanged usability limitation** | Unsupported forms remain not_found while canonical IDs work; this is not a fabricated relation or repair regression. [Direct name/ID controls](names_unsupported_forms.json). |
| **Raw request-shape errors**, JSON list/null bodies and body larger than 20,000 bytes | **NOT FIXED — unchanged server qualification** | Controlled 400 still exposes `.get`/JSON parsing errors; subsequent valid requests succeed. `src/app.py:237-239,267-269`; [HTTP cases](http_results.json). |

## M2b disposition — R1, R2 and every should-fix

| M2b finding / reproduction | Result | Current evidence and source |
|---|---|---|
| **R1 exact mixed input**: `osimertinib and generic version of bevacizumab`; reversed order; comma variant | **FIXED** | OSIMERTINIB remains selected; the qualified bevacizumab product is refused. Trial QA's first edge is `NCT03909334|EVALUATES|CHEMBL3353410|NCT03909334`; sponsor QA starts `ORG:astrazeneca|SPONSORS_TRIAL_OF|CHEMBL3353410|`. `src/query.py:167-178`; [old cases](regression_http.json), [independent QA](supplemental_http.json). |
| **R1 related over-refusal**: `[89Zr] trastuzumab and osimertinib`, reverse; `osimertinib and oral azacitidine` | **FIXED** | Separately named osimertinib and its evidence survive. [Name replay](names_reproduction_results.json), [HTTP](regression_http.json). |
| **R1's already documented inherited control**: `What is the generic version of bevacizumab?` | **NOT FIXED** | Still maps BEVACIZUMAB while refusing only `What is the generic version`. Detailed blocker M3-B2 below. [HTTP](supplemental_http.json). |
| **R2 unavailable sponsor count**: mutate `ORG:alaunos|SPONSORS_TRIAL_OF|CHEMBL1201438|` props to `null`, `[]`, `{broken`; request both endpoints | **FIXED** | All six results have `evidence_trials:null, weight:0` and display `책임 주관한 임상 수 기록 없음`. `{}` also stays unknown; numeric 0 remains an actual displayed 0. `src/app.py:141-146`; `web/try.html:173`; [API](db_missing_sponsor_count.json), [rendering](ui_missing_sponsor_count.json), [zero controls](ui_m3_checks.json). |
| **Boolean association score**: true/false fixture | **FIXED** | API returns null/weight 0; page also safely ignores directly injected bool score. `src/app.py:152-155,207-208`; `web/try.html:176`; [API](db_score_fixture.json), [UI](ui_regressions.json). |
| **Undisclosed score rounding**, EGFR/KRAS | **FIXED** | Detail and SVG tooltip show full `0.8883707400322897` / `0.8337881598550857`. `web/try.html:176`; [precision checks](ui_regressions.json). |
| **Embedded multi-ID company alias**: fixture `companies['sharedbrand']=['ORG:astrazeneca','ORG:roche']`; `Sharedbrand company` | **FIXED** | Roche is disclosed in `also`, as for bare Sharedbrand. No current production multi-ID alias exists. `src/app.py:97-102`; [fixture](names_boundary_details.json). |
| **Residual module wording / successful-input truncation** | **FIXED** | Capped-list docstring and explicit >500-character HTTP rejection, as in the m1 rows. |
| **Render errors escape fetch catch** | **FIXED for UI entry points** | `props.phases='PHASE2'` malformed response now shows `그리지 못했습니다` and clears trail for form, node, back and example callbacks; next KRAS response renders. `web/try.html:238-248`; [error/recovery checks](ui_m3_checks.json). |
| **Missing/unknown SPONSORS role and equal-weight A–Z follow-ups** | **FIXED** | Neutral `역할 기록 없음` for missing/unknown roles, both directions; stored valid roles remain intact. A–Z ties pass all-node validation. `web/try.html:147-149`; `src/app.py:166-167`; [role fixture](db_role_fallback.json), [UI](ui_regressions.json), [ordering](db_validate.json). |

## Specification blockers

### M3-B1 — P1: the new joiner exclusion lets a refused product description draw its originator

Exact unchanged-server requests:

```text
POST /api/explore
{"text":"paclitaxel with albumin bound nanoparticles"}
```

HTTP 200 returns:

```json
{"center":{"id":"CHEMBL428647","label":"PACLITAXEL","trials":234},
 "also":[{"refused":"albumin bound nanoparticles"}]}
```

This is an excerpt; [supplemental_http.json](supplemental_http.json) preserves the complete response. `/api/resolve` for the **same complete input** returns `BLOCKED_DISTINCT_PRODUCT`, no drug ID. The unmodified local predicate `is_distinct_product` also returns true. Restoring only the immediately prior `c64f433` linker makes the map refuse the whole input, with no centre. Thus this is a repair regression on the supplied database, not a fixture or an external pharmacology inference. `paclitaxel with albumin bound formulation` and `generic version with bevacizumab` are additional same-cause reproductions.

The regression also changes QA: `What trials evaluate paclitaxel with albumin bound nanoparticles?` now returns **12 PACLITAXEL trial evidence rows**, first `NCT00019019|EVALUATES|CHEMBL428647|NCT00019019`; the immediately prior linker returns **0**. [Isolated before/after comparison](names_new_boundaries.json), [independent actual-server evidence](supplemental_http.json).

**Causal hunk:** `src/query.py:92-93` includes `with` in `_JOINERS`; `src/query.py:170-172` suppresses the multi-token refusal whenever any token is a joiner. The previous condition checked `is_distinct_product(window)` without that exemption. For this five-token input, the entire product is no longer refused; the later three-token suffix is refused, leaving `paclitaxel` available to the alias acceptance at `src/query.py:181-195`. `src/app.py:88-95` selects that hit. The predicate's `albumin[\s\-]?bound` rule is at `src/textrules.py:145`, applied at `207-208`.

The control `Paclitaxel conjugate with poly-l-glutamic acid` still correctly selects the stored PACLITAXEL POLIGLUMEX alias (`CHEMBL2108628`) in both revisions. All 21 joiner-containing stored alias records retain identical answers. This does **not** establish that every `with` is an entity separator; the failed example is a refused full product description, not a broken ordinary alias. [Alias scan and control](names_new_boundaries.json).

**Required outcome:** distinguish separators between named entities from words inside a single qualified product. Refusal must cover the product's parent drug, while preserving separately named accepted entities. The exact product description above must not select CHEMBL428647 or answer with its trial evidence. Keep the repaired mixed-osimertinib cases and the valid poliglumex alias working.

### M3-B2 — P1, inherited: a leading question phrase still detaches the generic qualifier from its drug

`POST /api/explore {"text":"What is the generic version of bevacizumab?"}` returns **BEVACIZUMAB / CHEMBL1201583, 122 trials**, with `also=[{"refused":"What is the generic version"}]`. The same full input at `/api/resolve` is `BLOCKED_DISTINCT_PRODUCT`. This exact bypass was explicitly documented in m2b and remains reproduced; it is **not introduced by HEAD**. [HTTP evidence](supplemental_http.json), [previous/current linker comparison](names_new_boundaries.json).

The five-token longest-first refusal at `src/query.py:157-178` consumes the question prefix because it contains `generic version`, before reaching the qualified drug. The overlapping actual product span is then skipped, and the remaining bevacizumab token links. Qualifier recognition alone is insufficient: the refused span must include the substance it qualifies. This is another known path violating the same approval bar, independently of the new `with` regression.

## Additional should-fix and unchanged limitations

1. **Comma boundary repair is incomplete in the single-token refusal pass.** `osimertinib, liposomal doxorubicin` returns `refused:'osimertinib liposomal doxorubicin'`; reversing the order retains OSIMERTINIB. The same occurs for `osimertinib, biosimilar bevacizumab`. The unchanged resolver separates osimertinib as EXACT and refuses only the second product. QA `Which trials evaluate osimertinib, biosimilar bevacizumab?` returns no evidence. `src/query.py:139-143` unconditionally adds adjacent token indexes without checking the new `clause` boundary; the new guard applies only later at `170-172`. This is inherited over-refusal, not a new originator bypass. `CODEX_MAP_M1_VERDICT.md:27` therefore overstates that a refused span never crosses a comma. [Before/after](names_new_boundaries.json), [HTTP](supplemental_http.json).
2. Lowercase IDs / Investigator-name lookup and raw malformed-request error details remain the unchanged qualifications marked NOT FIXED above. Empty/whitespace map form submissions still make no request and leave the previous view; this is unchanged, not a repair regression. [UI checks](ui_m3_checks.json).
3. `_number` excludes bool and NaN but still accepts positive/negative infinity; `allow_nan=False` then returns controlled HTTP 400. No invalid numeric value is drawn, and none occurs in the supplied snapshot. This is a failure-closed limitation, not a blocker. [Numeric controls](db_numeric_fixture.json).

## Remaining successful checks and integrity

- Current snapshot: **7 retired nodes, 142 retired edges, no live edges with retired endpoints, no self-loops**. All six node types are covered. PARENT_OF, STUDIES, ASSOCIATED_WITH, EVALUATES, ACTS_ON and role-aware SPONSORS directions match their stored endpoints. [All-node results](db_validate.json).
- Trial phases/status/start/title/url, sponsor count/class, Drug global count/max phase, action and association score agree with stored values. All current props are valid objects; 300 association scores are JSON real and 3,176 sponsor counts integer. All 3,000 stored node URLs use the expected registry HTTPS prefix. [Snapshot facts](db_snapshot_facts.json).
- The **1,001-Drug** fixture crosses three count chunks: 1,001 returned items, each count/weight 1. Retired endpoint and malformed-props fixtures use actual HTTP handlers and isolated memory databases. [Fixtures](db_fixtures.json).
- Salt/parent separation remains: Tarceva / erlotinib hydrochloride → CHEMBL1079742; erlotinib → CHEMBL553; osimertinib mesylate → CHEMBL3545063. Whitespace/case/fullwidth controls pass. [Name replay](names_reproduction_results.json).
- Disease MONDO_0005233 returns **2,774 Trials + 300 Targets**, 30 per list, **18,575 bytes in 72.639 ms** in the recorded ordinary HTTP call. All **24 concurrent requests / 12 workers** returned expected 200 shapes in **558.15 ms**. These are local samples, not load benchmarks. [HTTP results](http_results.json).
- README command descriptions remain accurate at `README.md:566` and `README.ko.md:387`. No tracked AGENTS/CONTRIBUTING/coding standards or docs/agents rules were found. **Standards axis: no documented violations.** The user's evidence/no-edit constraints were followed. KOA/KhOpenApi repair comparisons do not apply because this review applies no application-code changes.
- **Specification axis: one new product/QA blocker, one previously documented product bypass still present, and the separate comma over-refusal should-fix above.** Other exact prior blocker and should-fix reproductions pass. Supporting independent notes: [names/QA](names_findings.md), [data](db_findings.md), [page](ui_findings.md).
- The real DB SHA-256 remains `7341c5a7089731f67356da5a588b269d4b69e8e6c4c054acf19aa4ef2837b529`. No application remediation was applied. [Final integrity checks](integrity.json).

## Reproduction entry points

Run from repository root. These scripts write only under m3; corruption/retirement fixture mutations are in memory. The two CLI HTTP runners each own/close port 8879 and must run sequentially.

```text
python -B audit_evidence_claims/m3/run_verification.py
python -B audit_evidence_claims/m3/run_http.py
python -B audit_evidence_claims/m3/db_recheck.py
python -B audit_evidence_claims/m3/db_role_fallback.py
python -B audit_evidence_claims/m3/db_missing_sponsor_count.py
python -B audit_evidence_claims/m3/db_score_fixture.py
python -B audit_evidence_claims/m3/db_numeric_fixture.py
python -B audit_evidence_claims/m3/names_reproduction.py
python -B audit_evidence_claims/m3/names_regressions.py
python -B audit_evidence_claims/m3/names_boundary_details.py
python -B audit_evidence_claims/m3/names_new_boundaries.py
python -B audit_evidence_claims/m3/ui_collect.py
node audit_evidence_claims/m3/ui_harness.js
node audit_evidence_claims/m3/ui_regressions.js
node audit_evidence_claims/m3/ui_missing_sponsor_count.js
node audit_evidence_claims/m3/ui_demos.js export
python -B audit_evidence_claims/m3/ui_demos_collect.py
node audit_evidence_claims/m3/ui_demos.js
node audit_evidence_claims/m3/ui_m3_checks.js
python -B audit_evidence_claims/m3/supplemental_http.py
python -B audit_evidence_claims/m3/integrity_check.py
```

VERDICT: CHANGES REQUIRED
