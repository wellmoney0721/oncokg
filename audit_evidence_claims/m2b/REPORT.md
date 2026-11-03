# Independent relation-map review — round 2 re-run

Reviewed HEAD: `c64f433648ad252b24254030196048fc17e81006`, 2026-11-03. Repair commits: `9db058c` and `c64f433`; comparison: `git diff bfcb83d...HEAD`. Specification: the user's round-2 brief and [m1 report](../m1/REPORT.md). The interrupted m2 scripts were inspected, relocated and rerun; their old outputs are not treated as current verification.

**Approval remains blocked.** B1–B4's exact original reproductions and the retired-trial count are fixed. However, the new refusal-window logic can discard a valid drug and draw the distinct product that the application's resolver refuses. It also changes question-answering evidence to that wrong subject. Separately, the malformed-props repair can display an unavailable sponsor count as a factual zero in an isolated fixture.

## Verification performed

- Requested command: `python -m pytest tests -q -p no:cacheprovider` — **321 passed in 13.56 s**, exit 0. Bytecode/cache writes were disabled; temporary directories were confined to m2b; UTF-8 mode avoids the earlier Windows subprocess-decoding warning. [Output](pytest.txt), [command/environment/integrity](pytest_summary.json).
- Started the unchanged application with `python -B -u src/app.py 8878`, exercised `GET /` and the APIs over HTTP, and stopped the audit server. The served page is byte-identical to `web/try.html`. Re-ran all m1 HTTP cases and 24 requests with 12 workers. [HTTP results](http_results.json), [server lifecycle](http_lifecycle.json), [independent regression HTTP results](regression_http.json).
- Re-ran **62 distinct m1/name-boundary inputs** and 13 additional regression comparisons. To isolate the linker change, comparisons restore only the exact `bfcb83d` `link_entities` method in a separate Engine; all other code/data stay current. [Name reproductions](names_reproduction_results.json), [comparisons](names_regressions.json), [boundary controls](names_boundary_details.json).
- Ran all **7 question demos** over the actual CLI server: complete response objects equal `bfcb83d`'s query implementation, with `use_llm=False`. The page/CLI/dashboard question lists are covered. [Demo comparisons](demo_results.json).
- Independently compared all **6,469 live centres**, covering **22 role-aware centre/relation/direction/neighbour-type combinations**, against stored adjacency, values, counts and sorting: **zero mismatches**. The oracle was updated to check ascending name ties, rather than reusing m2's obsolete descending-name expectation. [Validator](db_recheck.py), [results](db_validate.json).
- Executed the **entire current page script** in a Node VM with DOM stubs and controlled response order. All **36 page examples** rendered without exceptions: 13 resolver, 7 question, 9 prose-check, 7 structured-check. Ten current map payloads were also matched to actual HTTP responses. [UI harness](ui_harness.js), [results](ui_harness_results.json), [demos](ui_demos_results.json), [HTTP cross-check](ui_http_check.json).
- Real-browser verification was unavailable: browser discovery returned `The browser access host is unavailable`; selecting the existing Chrome window returned `Computer Use was not approved to use Google Chrome`. No browser input was performed. UI conclusions concern generated markup, script execution/state and HTTP behavior, **not browser layout or browser-executed XSS**. Dark mode was excluded as requested.

## Standards review

No tracked `AGENTS.md`, `CONTRIBUTING`, `CODING_STANDARDS` or `docs/agents/*` rules were found. No separate documented coding-standard violation is asserted. No tracked file was edited; all audit-created artifacts are under `audit_evidence_claims/m2b/`. Database mutations occurred only in memory; company-alias fixtures changed only an isolated Engine's index. The KOA/KhOpenApi code-change comparison instruction does not apply because this review changes no application code.

## M1 disposition — every reported finding

“FIXED” below means the specified m1 reproduction no longer fails. It does not certify a broader guarantee when a new or residual counterexample is identified later.

| M1 finding and exact reproduction | Result | Current result, code and evidence |
|---|---|---|
| **B1**: `bevacizumab - awwb`; `89Zr - trastuzumab`; `[89Zr] trastuzumab` | **FIXED** | All return HTTP 200 refusal, no centre. Unspaced controls still refuse. The broader refusal guarantee fails at R1 below. `src/query.py:153-162`; [HTTP evidence](regression_http.json). |
| **B2**: `NCT00200395`, reverse `ORG:genentech` | **FIXED** | Genentech is grouped as collaborator; Montefiore as lead sponsor. Reverse groups also distinguish the roles. `src/app.py:131,151-160`; `web/try.html:142-149`; [DB](db_validate.json), [rendered headings](ui_harness_results.json). |
| **B3**: `NCT00754364` / `ORG:armandosantoromd` | **FIXED** | Heading is `이 임상의 책임 주관 연구자 (lead sponsor)`, not institution. `web/try.html:143,148`; [UI evidence](ui_harness_results.json). |
| **B4**: in-memory `UPDATE node SET retired_at='AUDIT_FIXTURE' WHERE id='CHEMBL3353410'`; request name and ID | **FIXED** | Both `osimertinib` and `CHEMBL3353410` return not_found; EGFR excludes that neighbour. `src/app.py:109-112`; [real-handler fixture](db_retired_center.json). |
| **Retired-trial count**: live D, retired T, live T→EVALUATES→D and D→ACTS_ON→X | **FIXED** | D's centre count and its count/weight in X's map are 0; retired T remains excluded. `src/app.py:123-126,133,165`; [fixture](db_fixtures.json). |
| **S1: “most evidence” wording/order**, especially `MONDO_0005233` | **FIXED** | Trial lists disclose latest start-date order; disease targets now use stored association score (EGFR, KRAS, ALK lead); unweighted lists are A–Z. Group sizes remain descending. `src/app.py:138-161`; `web/try.html:148-158,231-235`; [all-node ordering checks](db_validate.json). Module-introduction wording remains a separate residual below. |
| **S2: silent ring cut**, `CHEMBL1201438`; Disease; AstraZeneca | **FIXED** | ALDESLEUKIN explicitly says 22 drawn of 25; Disease 39 of 3,074, with 30-per-list notices. AstraZeneca still draws 41, but accurately discloses it; 40 remains a soft allocation target, not a UI promise. No nonempty group is wholly lost in the exercised maps. `web/try.html:54,185-204,233`; [rendered counts](ui_harness_results.json). |
| **S3: stale trail**: osimertinib→EGFR, then `Mvasi`, `unknown-m1-entity`, server/network failure | **FIXED** | Trail state and buttons clear; invoking the old handler no longer throws. Back navigation after success also works. `web/try.html:213-216,240-241`; [failure/back cases](ui_harness_results.json). |
| **S4: out-of-order/double requests**: start EGFR then KRAS, finish KRAS first; two concurrent EGFR calls | **FIXED** | Latest KRAS map remains; stale success/error cannot replace it. Concurrent duplicate EGFR calls leave one trail entry. `web/try.html:211-214`; [controlled completions](ui_harness_results.json). |
| **S5: silent identity ambiguity**: `Roche`, `MET`, `osimertinib EGFR`, reverse order | **FIXED** | Selected centres remain FOLIC ACID/METFORMIN/first named hit, but the company/target/other entity and selected reading are disclosed. `Mvasi and bevacizumab` also exposes the refused span. Embedded multi-ID company aliases remain a fixture limitation below. `src/app.py:95-108`; `web/try.html:222-226`; [names](names_reproduction_results.json), [UI](ui_harness_results.json). |
| **S6: action/class specificity**, ALDESLEUKIN's AGONIST; BINDING AGENT; sponsor classes | **FIXED** | `작용: 작용제 (AGONIST)` and the correct stored `BINDING AGENT` code appear. INDUSTRY, NIH, FED, OTHER_GOV, NETWORK, OTHER and unknown class codes remain visible. `web/try.html:162-176`; [details](ui_harness_results.json). |
| **S7: omitted details**: Trial centre start; sponsor→Drug global count/phase; zero-trial Drug | **FIXED** | `NCT00200395` shows start `2003-07-02`; AstraZeneca→osimertinib shows sponsor count 14, global count 79 and approval; `CHEMBL925` shows 0 trials. `src/app.py:132-134,165`; `web/try.html:173-174,228-229`; [DB/UI](ui_harness_results.json). |
| **S8: malformed props expose raw errors**: node/edge `null`, `[]`, `{broken` | **FIXED** | All 12 original fixture requests now return 200, as do restorations. `_obj` treats them as empty objects. This fixes the original exception but introduces R2's false-zero display in a sponsor-count fixture. `src/app.py:129,198-204`; [original fixture rerun](db_fixtures.json). |
| **URL safety qualification**: `javascript:alert(...)`, data URL, hostile labels/titles/IDs | **FIXED** | Map centre/neighbour anchors use a clinicaltrials.gov HTTPS allowlist. Scheme, host-prefix, credential and backslash spoof probes fail the allowlist; text/attributes remain escaped. This is generated-markup evidence, not browser exploit execution. `web/try.html:180,199,221,230,234-235`; [probes](ui_harness_results.json), [assertions](ui_regressions.json). |
| **Unknown-type tooltip**: synthetic `Other` node / `NEWREL` edge | **FIXED** | Raw type/relation fallback survives; no `undefined` tooltip. `web/try.html:158,199,227`; [fixture](ui_regressions.json). |
| **“All three” after four boxes** | **FIXED** | Now “All of them”, `src/app.py:10`. |
| **Module “everything” overclaim** | **NOT FIXED** | `src/app.py:5` still says “everything”; the detailed explore docstring and page now describe cuts. Documentation-only residual. |
| **Silent 500-character truncation**: `"x"*500 + " osimertinib"`; `"osimertinib " + "x"*600` | **NOT FIXED** | HTTP still reads only the first 500 characters (`src/app.py:226`). Not-found UI now mentions the limit, but successful maps can silently ignore the suffix. [HTTP cases](http_results.json), `web/try.html:216`. |

The final repair's additional two changes also pass: missing/unknown SPONSORS roles say `역할 기록 없음`, and equal-weight names sort A–Z. [Role fixtures](db_role_fallback.json), [UI role cases](ui_regressions.json), [ordering oracle](db_validate.json).

## New specification blockers

### R1 — P1, current database: refusal windows select the refused product and change QA's subject

Exact live-server request:

```json
{"text":"osimertinib and generic version of bevacizumab"}
```

`POST /api/explore` returns HTTP 200 with **BEVACIZUMAB / CHEMBL1201583, 122 trials**, and `also=[{"refused":"osimertinib and generic version of"}]`. With the exact old linker restored, the selected centre is OSIMERTINIB. Independently, the unchanged `/api/resolve` returns `osimertinib` as EXACT / CHEMBL3353410 and `generic version of bevacizumab` as **BLOCKED_DISTINCT_PRODUCT**. The map is therefore drawing the component the same application explicitly refuses. This conclusion uses repository rules, not an external pharmacology assumption.

**Causal change:** the new hunk at `src/query.py:153-162` applies a refusal predicate to longest-first windows (`146-150`) and marks the whole window refused. The first five tokens contain `generic version`, which satisfies `src/textrules.py:149`, but omit bevacizumab. Their refusal consumes osimertinib. The overlapping window containing the actual qualified product is skipped at `src/query.py:148-149`, leaving bevacizumab available for alias acceptance at `171-178`. `src/app.py:87-95` then selects that remaining hit.

The same regression reaches QA:

| Exact `/api/ask` text | Old-linker first evidence | Current first evidence |
|---|---|---|
| `Which trials evaluate osimertinib and generic version of bevacizumab?` | `NCT03909334\|EVALUATES\|CHEMBL3353410\|NCT03909334` | `NCT00955305\|EVALUATES\|CHEMBL1201583\|NCT00955305` |
| `Which companies sponsor osimertinib and generic version of bevacizumab?` | `ORG:astrazeneca\|SPONSORS_TRIAL_OF\|CHEMBL3353410\|` | `ORG:roche\|SPONSORS_TRIAL_OF\|CHEMBL1201583\|` |

Both old/current trial answers have 12 evidence rows; success codes and evidence counts alone miss the subject switch. Related over-refusal occurs for `[89Zr] trastuzumab and osimertinib`: the new linker refuses the whole input and QA produces no evidence, whereas `osimertinib and [89Zr] trastuzumab` retains osimertinib and its evidence. `osimertinib and oral azacitidine` similarly loses the separately named valid drug.

Controls: `generic version of bevacizumab` alone now correctly refuses; `osimertinib and bevacizumab` selects osimertinib and discloses bevacizumab; reversing the mixed generic-product input retains osimertinib. `What is the generic version of bevacizumab?` also maps bevacizumab, but did so before: that specific bypass is inherited, not attributed to this repair.

**Required outcome:** bind refusal to the actual product/tracer span and preserve separately named valid entities regardless of order. The mixed generic-product input must never select BEVACIZUMAB. Evidence: [isolated before/after HTTP comparisons](names_regressions.json), [boundary controls](names_boundary_details.json), [independent actual-server confirmation](regression_http.json). These cases are absent from the four added tests at `tests/test_app.py:57-92`; passing the existing suite/demos does not resolve them.

### R2 — P2, isolated malformed-data state: an unknown sponsor count becomes a displayed zero

Back up the real DB into memory and change only the props of this live edge:

```text
ORG:alaunos|SPONSORS_TRIAL_OF|CHEMBL1201438|
```

Use `UPDATE edge SET props=? WHERE id=?` with each literal JSON/text value `null`, `[]`, `{broken`. Request `{"text":"CHEMBL1201438"}` and `{"text":"ORG:alaunos"}` through the real handler.

At bfcb83d these requests fail closed with 400. At HEAD each returns 200; that edge has `weight:0`, and the actual current script renders **`책임 주관한 임상 0건`**. After the fixture mutation there is **no stored numeric evidence_trials value**. The original unmutated value was 1, but it is not legitimate to treat that removed value as still stored, nor to replace the unavailable value with a factual zero.

**Cause:** new `_obj` (`src/app.py:198-204`) converts invalid/non-object props to `{}` at line 129; the existing `ep.get("evidence_trials") or 0` at line 136 now turns newly accepted invalid data into a zero; `web/try.html:173` presents the sorting weight as the stored count. This is an interaction introduced by the parser repair. Empty `{}` already defaulted to zero before; the newly demonstrated null/list/broken-JSON paths previously returned errors.

**Required outcome:** keep an unavailable count distinct from zero. A separate default sort weight is fine, but the factual detail must say unknown/not recorded or return a controlled data error. No malformed props exist in the supplied snapshot; this is a fixture-only failure within the brief's explicit malformed-JSON scope. Evidence: [baseline/current real-handler fixture](db_missing_sponsor_count.json), [reproducer](db_missing_sponsor_count.py), [actual page rendering](ui_missing_sponsor_count.json).

## Additional should-fix items and qualifications

1. **New boolean-score rendering failure, fixture only.** For a live Target→ASSOCIATED_WITH→Disease edge with `{"association_score":true}` (or false), `src/app.py:145` accepts Python bool as numeric. HTTP returns a boolean score; new `web/try.html:176` calls `.toFixed(3)` and throws. Rendering occurs outside the fetch catch (`213`), leaving `그리는 중…` and a pushed trail entry. All 300 current association scores are JSON real. Validate numeric type excluding bool and handle rendering errors. [API baseline/current fixture](db_score_fixture.json), [script reproduction](ui_regressions.json).
2. **New score precision is undisclosed.** `EGFR` has stored/API score `0.8883707400322897`, displayed `0.888`; `KRAS` has `0.8337881598550857`, displayed `0.834` (`web/try.html:176`). This is rounding, not corrupt stored data or a fabricated relationship. Mark approximation/precision and expose the exact value if the stored-value promise includes this new field. It is listed separately from R2's invented zero. [Exact/rendered pairs](ui_regressions.json).
3. **Company ambiguity repair is incomplete for embedded aliases.** Current company index has zero multi-ID aliases. An index-only fixture sets `companies['sharedbrand']=['ORG:astrazeneca','ORG:roche']`: `Sharedbrand` offers Roche, but `Sharedbrand company` returns `also=[]` despite the linker's `also_matching_ids=['ORG:roche']`. `src/app.py:95-107` checks the whole input instead of consuming the chosen hit's alternatives (`src/query.py:189-197`). No current-snapshot multi-ID case is claimed. [Fixture](names_boundary_details.json).
4. **Residual documentation/input limits** are the NOT FIXED rows above: module “everything” and successful-input truncation. The brief's README command descriptions remain accurate at `README.md:566` and `README.ko.md:387`.

## Remaining coverage and integrity

- Current DB has **7 retired nodes, 142 retired edges, zero live edges with retired endpoints and no self-loops**. Retired rows do not leak in the exhaustive run. All six present node types are covered. PARENT_OF, STUDIES, ASSOCIATED_WITH, EVALUATES and ACTS_ON retain correct endpoint directions; SPONSORS now adds correct role/type wording. [DB audit](db_validate.json).
- Stored trial phase/status/start/title/url, sponsor evidence count/class, Drug global count/max phase and action agree with current API data. A **1,001-Drug** fixture crosses three 500-ID count chunks, returning 1,001 items with count/weight 1. [Fixture results](db_fixtures.json).
- Salt/parent boundaries remain distinct: Tarceva / erlotinib hydrochloride → CHEMBL1079742; erlotinib → CHEMBL553; osimertinib mesylate → CHEMBL3545063. Case/whitespace/fullwidth controls pass. Lowercase NCT/CHEMBL IDs and investigator names remain unsupported, as before. Other Unicode/product boundary variants accepted by both the unchanged resolver and linker are not misrepresented as repair regressions. [Name results](names_reproduction_results.json), [notes](names_findings.md).
- Disease `MONDO_0005233` returns 2,774 Trials + 300 Targets, 30 items each, **18,575 UTF-8 bytes in 71.398 ms** in the ordinary recorded HTTP call. This is a local sample, not a load benchmark. All **24 concurrent requests / 12 workers** returned expected 200 shapes, **605.796 ms** total. [HTTP results](http_results.json).
- Empty/whitespace/null text and malformed JSON still return 400; valid unknown-route input returns 404. JSON list/null bodies still expose raw `.get` errors; oversized bodies fail JSON parsing at the 20,000-byte cap. Subsequent valid requests succeed. These inherited server behavior qualifications remain; no new deadlock was reproduced. `src/app.py:223-254`; [HTTP cases](http_results.json).
- The explored code paths perform reads and call no model; `Engine.ask` explicitly uses `use_llm=False` (`src/app.py:171-172`). Real DB SHA-256 is unchanged: `7341c5a7089731f67356da5a588b269d4b69e8e6c4c054acf19aa4ef2837b529`. SQLite is not globally opened read-only by the application, so this is verified path behavior/integrity, not a database permission guarantee.
- Final HEAD, tracked/staged diff checks, database/source hashes, report links and audit-port closure are recorded in [integrity.json](integrity.json). No application remediation was applied.

## Reproduction entry points

All commands below write only within m2b; use the repository root as the working directory. The HTTP runner owns and closes port 8878; `regression_http.py` and `ui_http_check.py` expect the unchanged app already running there. Other fixture scripts own their ephemeral HTTP servers.

```text
python -B audit_evidence_claims/m2b/run_verification.py
python -B audit_evidence_claims/m2b/run_http.py
python -B audit_evidence_claims/m2b/db_recheck.py
python -B audit_evidence_claims/m2b/db_role_fallback.py
python -B audit_evidence_claims/m2b/db_missing_sponsor_count.py
python -B audit_evidence_claims/m2b/db_score_fixture.py
python -B audit_evidence_claims/m2b/names_reproduction.py
python -B audit_evidence_claims/m2b/names_regressions.py
python -B audit_evidence_claims/m2b/names_boundary_details.py
python -B audit_evidence_claims/m2b/ui_collect.py
node audit_evidence_claims/m2b/ui_harness.js
node audit_evidence_claims/m2b/ui_regressions.js
node audit_evidence_claims/m2b/ui_missing_sponsor_count.js
```

Supporting independent reviews: [DB](db_findings.md), [names/QA](names_findings.md), [page/standards](ui_findings.md). Standards axis: 0 documented violations. Specification axis: 2 blockers (R1 current-data product/QA subject switch; R2 fixture-only false sponsor count), with should-fix items separated above.

VERDICT: CHANGES REQUIRED
