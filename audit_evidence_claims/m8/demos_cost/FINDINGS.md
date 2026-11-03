# Round 8 ? demos, UI, cost and cache boundary

Reviewed current HEAD `ec4eede`, read-only application code. All new artifacts are confined to this directory. Prior-script copies and SHA-256 provenance are in [reuse_manifest.json](reuse_manifest.json).

## New reproducible defect: cache eviction raises on an ordinary lone drug

**P2, new in HEAD; independent of originator-leak findings.** The bounded cache clears the just-inserted entry, then reads it. This was reproduced through the original unmodified CLI HTTP server, without writing or injecting cache state.

1. Start a fresh `python -B -u src/app.py 8938`.
2. Create `pieces = [f"isa x{i:04d}" for i in range(4096)]`.
3. Send 82 `POST /api/explore` requests whose `text` is `";".join(pieces[offset:offset+50])`, for offsets 0, 50, ..., 4050. The first 81 requests are 499 characters and the last is 459, all within the 500-character input cap. All 82 return HTTP 200, selecting ISATUXIMAB, and cumulatively populate 4,096 distinct drug-bearing pieces.
4. Send `{"text":"osimertinib"}` to `/api/explore`. **HTTP 400**, body **`{"error":"'osimertinib'"}`**, no centre.
5. Send the identical request again. **HTTP 200**, OSIMERTINIB / CHEMBL3353410, 79 trials.

[Exact requests/responses](cache_boundary_http.json), [reproducer](cache_boundary_http.py), [server lifecycle and unchanged DB hash](cache_boundary_lifecycle.json). The 82 fill requests took 48.108 s in aggregate during concurrent audit work; their purpose is natural cache population, not isolated performance measurement.

Cause: `src/query.py:174-182` stores a new resolution; when the dictionary length exceeds 4,096, lines 180-181 call `clear()`, and line 182 immediately evaluates `self._resolve_cache[piece]`. The key no longer exists. The exception escapes `link_entities` and becomes the controlled HTTP 400 at `src/app.py:267-269`. The fact that the next identical request succeeds is consistent with an emptied cache, not an unknown drug. The current failure is not an originator substitution or intended product refusal; a valid drug alone in its item is unavailable on the cache boundary. Preserve the computed value when evicting cache entries. No repair was applied.

## Earlier UI/demo reproductions

- **36/36 full demo responses identical to m7; 0 engine errors.** EX1 resolve 13, EX2 QA 7, EX3 check 9, EX4 structured 7. [Comparison](ui_demo_compare.json), [full responses](ui_demos_responses.json).
- **36/36 demo HTTP responses are 200 and equal direct-engine output.** Original CLI on owned port 8937 served bytes identical to current `web/try.html`; process terminated after tests. [HTTP](demo_http.json), [lifecycle](demo_http_lifecycle.json).
- **36 demo callbacks + 6 map callbacks pass**, including malformed-render recovery from all four entry routes. [Callback results](ui_m3_checks.json).
- **24/24 UI assertions pass** against current source, current maps, root's fresh HTTP payloads and root's fresh missing-count DB fixture. [Assertions](ui_assertions.json), [runner](run_ui.py), [executed commands](execution_ui_complete.json).

| Earlier concern | R8 disposition / evidence |
|---|---|
| M1 S1/S2 incorrect ordering text / silent ring cuts | **FIXED**; actual ring totals and cut notices preserved in [ui_harness_results.json](ui_harness_results.json). |
| M1 S3/S4 stale trail, reverse replies, duplicate requests | **FIXED**; refusal/not_found/server/network errors clear trail, stale network error ignored, latest KRAS wins, duplicate yields one trail entry. |
| M1 S5 alternatives/refusal disclosure | **FIXED for disclosure** in current generated markup and maps. |
| M1 S6/S7 action/class, start date, zero trials | **FIXED** in replayed UI fixtures. NCT00200395 start 2003-07-02; CHEMBL925 graph trials 0 visible. |
| M1 hostile labels/titles/IDs/URLs / unknown type | **FIXED for exercised markup paths**; escaped node IDs, no raw img/script/javascript href; unsafe schemes, host spoofing and credentials rejected. Raw unknown type fallback retained. [ui_regressions.json](ui_regressions.json). |
| M2b missing sponsor count, role, boolean score, rounded score | **FIXED**; missing count is unknown, numeric zero remains zero, unknown roles neutral, booleans do not throw, decimal precision retained. [ui_missing_sponsor_count.json](ui_missing_sponsor_count.json), [ui_regressions.json](ui_regressions.json). |
| M2b/M3 malformed phases render exception | **FIXED**; all four entry points caught and clear state, stale malformed response ignored. |
| M3/M4 blank-submit usability behavior | **NOT FIXED**, unchanged nonblocker: no HTTP request and prior view retained (`web/try.html:241`). |
| M7 demos | **FIXED / retained**; no demo regression. |

The UI tests execute the actual page script in Node VM with stub DOM/fetch. They verify generated markup, callback/state logic, request payloads and response-order behavior. They do **not** certify browser paint or real-browser exploitation. No new UI injection defect was established.

## Cost: original defect fixed; distinct cold pieces remain expensive

The old m5 instrumented worker, m6 stress cases, and m7 exact split-piece comparison/HTTP script were reused. Initial timing artifacts preserve concurrent-work results. The `isolated_*` runs were conducted only after the parent, replay and attack workers confirmed heavy work had stopped; unrelated host activity remains uncontrolled. Exact predecessor `9bd7cb4:src/query.py` was loaded in an isolated Python module using the current shared rules/data, so this compares the query implementation, not complete historical environments.

**M5-S3 FIXED for the original all-substring growth / plain-answer reproduction.** The 250-token plain case has 4,197 calls to each product/tracer predicate and 66,262 aggregate characters in the current instrumented worker; the double whole-input check makes counts differ from m6. These counts remain bounded-window work, not the prior 31,625 each / 10,479,750 characters. [Instrumentation](perf_current.json), [stress cases](cost_stress.json). Do not infer global linear runtime: `_link` also rescans tokens for each segment (`src/query.py:279-285`).

**M7-S3 FIXED for the exact repeated `x` split-piece reproduction.** Three-sample isolated linker medians:

| Exact construction | Characters | Previous m7 query | Current HEAD |
|---|---:|---:|---:|
| `" ".join(["x"]*250)` | 499 | 0.020764 s | 0.025255 s |
| `";".join(["x"]*250)` | 499 | 0.203726 s | 0.005110 s |
| `";".join(["x"]*1000)` | 1,999 | 0.860844 s | 0.048204 s |
| `";".join(["x"]*2000)` | 3,999 | 1.881507 s | 0.162771 s |

[Raw samples and stage times](isolated_fresh_cost_comparison.json). The last input spends 0.000182 s in `_resolver_blocked` and 0.154133 s in `_link` in separate stage calls.

Actual original-CLI HTTP `/api/check` for `{"text":"EGFR","answer":";".join(["x"]*2000)}` completes in **0.447614 s**, HTTP 200. An EGFR explore dispatched about 0.1 s later completes in **0.366048 s**, versus baseline **0.024895 s** and after **0.020281 s**. GET stays HTTP 200. [Isolated HTTP](isolated_fresh_cost_http.json), [lifecycle](isolated_fresh_cost_lifecycle.json).

The cache helps repeated pieces, not distinct unseen drug-bearing pieces. Exact instrumented cold/warm results from fresh engines:

| Input | Cold resolver calls | Warm resolver calls | Cold linker / warm samples |
|---|---:|---:|---|
| 250 repeated unknown `x` pieces | 0 | 0 | 0.006010 / 0.005439, 0.005412 s |
| 400 distinct unknown `x0000`... pieces | 0 | 0 | 0.018877 / 0.018812, 0.018086 s |
| 400 copies of `isa x0000` | 1 | 0 | 0.098599 / 0.090217, 0.089640 s |
| 50 distinct `isa x0000`... pieces, 499 chars | 50 | 0 | 0.247858 / 0.009476, 0.009784 s |
| 400 distinct `isa x0000`... pieces, 3,999 chars | 400 | 0 | 3.003448 / 0.182520, 0.126672 s |

[Exact input strings, timings and counts](isolated_unique_piece_cost.json). Cold direct `Engine.check` varied from 2.794 s in the first concurrent run to 4.677 s in the isolated audit run; these are local timing observations, not a uniform latency guarantee.

A separate fresh original-CLI HTTP run confirms the practical cold-piece cost: `/api/check` with 400 distinct pieces is **200 in 2.207713 s**; queued EGFR is **200 in 2.126304 s**; the identical warm check is **0.352029 s**; baseline/after EGFR are **0.034930 / 0.035340 s**. GET `/` remains 200 in 0.167720 s. [HTTP](isolated_unique_cost_http.json), [reproducer](unique_cost_http.py), [lifecycle](unique_cost_lifecycle.json). `src/app.py:247-263` holds the shared engine lock throughout checking. This is a residual cost qualification, not evidence that the exact M7-S3 reproduction remains unfixed or that cold distinct-piece work newly regressed from m7.

## Scope and replay commands

No application/tracked file was edited. No model is invoked by the demo paths (`Engine.ask` sets `use_llm=False`). DB mutation fixtures were provided by the parent worker and isolated from the snapshot. Each owned HTTP run terminated its own server; the cost/cache lifecycle records verify unchanged DB SHA-256 `7341c5a7089731f67356da5a588b269d4b69e8e6c4c054acf19aa4ef2837b529`. Ports used here: 8936, 8937, 8938, 8939. No use of 8765.

```text
python -B audit_evidence_claims/m8/demos_cost/run_ui.py
node audit_evidence_claims/m8/demos_cost/ui_missing_sponsor_count.js
python -B audit_evidence_claims/m8/demos_cost/ui_assertions.py
python -B audit_evidence_claims/m8/demos_cost/demo_http.py
python -B audit_evidence_claims/m8/demos_cost/run_perf_current.py
python -B audit_evidence_claims/m8/demos_cost/cost_stress.py
python -B audit_evidence_claims/m8/demos_cost/fresh_cost.py isolated
python -B audit_evidence_claims/m8/demos_cost/unique_piece_cost.py isolated
python -B audit_evidence_claims/m8/demos_cost/unique_cost_http.py
python -B audit_evidence_claims/m8/demos_cost/cache_boundary_http.py
```

UI assertions require the parent's freshly generated `m8/root_checks/http_results.json`, `served_try.html` and the copied `m8/db_ui/db_missing_sponsor_count.json`. Cost and cache scripts use fresh owned original-CLI processes; run sequentially to avoid shared ports. All Python execution disables bytecode; owned server temporary paths and all new outputs are inside m8.
