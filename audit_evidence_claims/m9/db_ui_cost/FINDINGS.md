# Round 9 ? DB, UI, demos, cost and cache boundary

Reviewed HEAD `3a362eb4f156ea252301d18507ff0a733d0b601e`. No new blocker established in this worker's scope. All 26 reused scripts, adaptations and source/output SHA-256 hashes are recorded in [reuse_manifest.json](reuse_manifest.json). Only output directories and owned CLI ports were adapted; test logic is retained. All new files are under this directory; no application or earlier audit file was edited.

## Independent DB and UI results

The independent graph oracle checked **all 6,469 live centres with zero errors**: exact live-edge membership, endpoints, relation/direction/type/role group keys, every stored displayed value, group totals, trial-count oracle, sorting weights and ordering. [Full DB result](db_validate.json), [19/19 DB assertions](db_assertions.json), [execution records](execution.json).

The snapshot has **7 retired nodes, 142 retired edges, zero self-loops, zero live edges with retired endpoints**. All 3,000 trial URLs are registry HTTPS URLs, and current node/edge props have no malformed/non-object JSON. The independent fixtures use only in-memory databases or in-memory backups of the read-only snapshot. [Snapshot facts](db_snapshot_facts.json).

| Earlier finding / exact reproduction | Round 9 disposition |
|---|---|
| M1-B2 collaborator vs lead: `NCT00200395`, `ORG:genentech` | **FIXED**. Both directions retain lead/collaborator groups and wording; `src/app.py:137,162-169`, `web/try.html:142-149`. [DB](db_validate.json), [UI](ui_harness_results.json). |
| M1-B3 Investigator vs institution: `NCT00754364`, `ORG:armandosantoromd` | **FIXED**. Investigator heading says researcher; `web/try.html:143,148`. [UI](ui_harness_results.json). |
| M1-B4 retired centre by name/ID; isolated retirement of CHEMBL3353410 | **FIXED**. Name and ID return not_found; EGFR excludes the retired neighbor. `src/app.py:83-84,115-123`. [Real-handler fixture](db_retired_center.json). |
| M1 retired-trial counts: retired T ? EVALUATES ? live D, live D ? ACTS_ON ? X | **FIXED**. D centre count and count/weight under X are 0. `src/app.py:129-132`. [Fixture](db_fixtures.json). |
| M1-S1 misleading most-evidence wording / wrong target ordering | **FIXED**. Trials sorted by start-date strings, drugs by graph trials, sponsors by recorded counts, disease targets by recorded score; equal weights A?Z. `src/app.py:141-170`, `web/try.html:151-158,232-233`. [All-node oracle](db_validate.json). |
| M1-S2 silent ring cut: CHEMBL1201438, MONDO_0005233, AstraZeneca | **FIXED**. Actual drawn/total and per-list cuts disclosed; no nonempty group wholly omitted in exercised maps. `web/try.html:191,204,233`. [UI](ui_harness_results.json). |
| M1-S3 stale trail after Mvasi, unknown, server/network errors | **FIXED**. Trail/buttons clear; obsolete back callback harmless. `web/try.html:213-216,243-244`. [UI](ui_harness_results.json). |
| M1-S4 out-of-order completion / concurrent duplicate / stale network error | **FIXED**. Latest KRAS remains; duplicate yields one entry. `web/try.html:211-214`. [UI](ui_harness_results.json). |
| M1-S5 silent selected match and alternatives, including Roche/MET/mixed names | **FIXED for disclosure**. Selected-reading and alternative/refusal chips remain. `web/try.html:222-226`. [UI](ui_harness_results.json). Name semantics audited by other worker. |
| M1-S6 action/class specificity; AGONIST and BINDING AGENT / sponsor classes | **FIXED**. Specific gloss plus stored action/class code retained. `web/try.html:161-176`. [UI](ui_harness_results.json). |
| M1-S7 start date / sponsor-to-drug global count and phase / zero trials | **FIXED**. NCT00200395 start 2003-07-02; sponsor and global counts/phase both shown; CHEMBL925 zero shown. `src/app.py:172-177`, `web/try.html:173-174,228-229`. [UI](ui_harness_results.json). |
| M1-S8 node/edge props null, list, broken JSON; 1,001-drug chunking | **FIXED**. All original 12 malformed requests return 200 and recover; 1,001 drugs each retain trial count/weight 1. `src/app.py:127-132,211-217`. [Fixtures](db_fixtures.json). |
| M1 URL/script/ID/text injection and Other/NEWREL fallback | **FIXED for exercised generated-markup paths**. Escaping preserved; javascript/data, credential, prefix-host and backslash spoofs rejected; unknown raw type/relation preserved. `web/try.html:104,158,180,199,221-235`. [Regression fixture](ui_regressions.json). |
| M2b-R2 missing sponsor count, both Alaunos/ALDESLEUKIN endpoints and null/list/broken/empty props | **FIXED**. Missing count stays unknown and weight 0; actual numeric 0 stays 0. `src/app.py:141-146`, `web/try.html:173`. [DB](db_missing_sponsor_count.json), [UI](ui_missing_sponsor_count.json). |
| M2b boolean score / decimal precision / unknown sponsor role | **FIXED**. Boolean score becomes unknown rather than throwing; full stored decimal survives display; absent/unknown roles are neutral. [Score DB](db_score_fixture.json), [role DB](db_role_fallback.json), [UI](ui_regressions.json). |
| M2b/M3 malformed phases='PHASE2', form/node/trail/example entry routes | **FIXED**. Four route errors caught, state cleared; stale malformed response ignored and recovery works. `web/try.html:239-248`. [Callbacks](ui_m3_checks.json). |
| M3/M4 blank or whitespace form submission | **NOT FIXED**, unchanged nonblocker. No request, previous view retained; `web/try.html:241`. [Callbacks](ui_m3_checks.json). |
| M3/M4 positive/negative Infinity fixtures | **NOT FIXED**, unchanged failure closed. Controlled 400; no invalid map value displayed and none in current snapshot. `src/app.py:207-208,264-269`. [Fixture](db_numeric_fixture.json). |
| M1 module everything/all-three wording | **FIXED**. Capped list per relation and All of them at `src/app.py:5-11`. |
| M5-S3 original all-substring growth / plain-answer cost | **FIXED for exact prior workload**. 250-token plain instrumentation now 2,224 calls to each guard and 33,880 aggregate characters, versus original 31,625 calls each / 10,479,750 characters. [Instrumentation](perf_current.json), [stress inputs/results](cost_stress.json). |
| M6 split_2000 / M7-S3 repeated identical-piece full resolver overhead | **FIXED for exact repeated-piece workload**. See isolated timings below. |
| M8-S1 4,097th cache entry loses current resolution | **FIXED**. Natural original-CLI reproduction gives first boundary request HTTP 200, correct lone drug, and retry HTTP 200. See below. |

All **24/24 UI assertions** pass against fresh direct maps, in-memory fixture outputs and root's fresh CLI HTTP results. [Assertions](ui_assertions.json), [runner](run_ui.py), [UI execution records](execution_ui_complete.json). The harness executes actual page JavaScript in Node VM with DOM/fetch stubs; it verifies markup and callback/state behavior, **not browser paint or real-browser exploitation**.

## Demos

All **36/36 complete demo response objects equal both m7 and m8**, with no engine errors: 13 resolver, 7 QA, 9 check, 7 structured. [Previous-response comparison](demo_previous_comparison.json), [full current responses](ui_demos_responses.json). All **36/36 original-CLI HTTP demo responses return 200 and equal direct Engine output**; served page bytes equal current `web/try.html`. [HTTP](demo_http.json), [server lifecycle](demo_http_lifecycle.json). The page's 36 demo-click callbacks and 6 map-click callbacks all pass. [Callbacks](ui_m3_checks.json).

## Natural cache rollover

On a fresh original CLI, send the exact m8 sequence: 82 `/api/explore` requests containing the 4,096 distinct pieces `isa x0000` through `isa x4095`, joined by semicolon in batches of at most 50 (499 characters maximum). All 82 return HTTP 200. The first subsequent `osimertinib` request now returns **HTTP 200 / CHEMBL3353410 / 79 trials**, and the immediate retry does likewise. No cache contents were injected or monkey-patched. `src/query.py:187-195` clears before storing the newly computed value and retains that value locally. [Exact inputs/results](cache_boundary_http.json), [reproducer](cache_boundary_http.py), [closed port and unchanged DB hash](cache_boundary_lifecycle.json).

## Cost and locking

The final cost interval ran after root and names heavy work completed and the attack worker explicitly paused probes. Unrelated host activity remains uncontrolled. The exact old `9bd7cb4` query module was loaded with current shared data/rules, so this compares query implementation rather than complete historical environments.

| Exact workload | Old m7 median / current median |
|---|---|
| `' '.join(['x']*250)`, 499 characters | 0.021025 / 0.019872 s |
| `';'.join(['x']*250)`, 499 characters | 0.202781 / 0.005718 s |
| `';'.join(['x']*1000)`, 1,999 characters | 0.830086 / 0.044388 s |
| `';'.join(['x']*2000)`, 3,999 characters | 1.795619 / 0.152050 s |

[Three samples per case and stage times](isolated_fresh_cost_comparison.json). Actual `/api/check` with question `EGFR` and the 3,999-character repeated-x answer completes HTTP 200 in **0.395786 s**; ordinary EGFR queued about 0.1 s later returns HTTP 200 in **0.313302 s**. The later ordinary map takes 0.020716 s. [HTTP](isolated_fresh_cost_http.json).

Distinct cold drug-bearing pieces still cost seconds. For `';'.join(f'isa x{i:04d}' for i in range(400))` (3,999 characters), direct instrumentation records **400 cold resolver calls / 0 warm calls**. Four hundred copies of one identical piece use **1 cold / 0 warm** calls; non-drug pieces use 0. [Exact strings/counts/samples](isolated_unique_piece_cost.json).

Original-CLI HTTP check for 400 distinct pieces takes **3.110653 s cold**, queued EGFR **3.051145 s**, identical warm check **0.692193 s**, with HTTP 200 throughout. Ordinary maps before/after are 0.044666 / 0.043361 s; concurrent GET is 200 in 0.130191 s. [HTTP](isolated_unique_cost_http.json). This remains a residual lock-contention cost qualification, not a demonstrated new regression or timeout/deadlock. `src/app.py:247-263` holds the engine lock across checking; `src/query.py:298` scans tokens per segment. No global linear-runtime claim is made.

## Standards, integrity and reproduction

No repository standards source was found by the primary reviewer. The supplied no-tracked-edit and evidence-based review instructions govern. No application code was changed, so the conditional KOA/KhOpenApi original-versus-modified-code requirement does not apply. Application QA explicitly sets `use_llm=False` (`src/app.py:180-181`). All DB fixtures were in memory; snapshot checks used read-only handles. The application itself does not enforce SQLite read-only permission, so the execution paths and hash evidence support this review's no-write conclusion.

All owned CLI servers (ports **8892, 8893, 8894**) are closed. Cache/cost lifecycle files confirm unchanged DB SHA-256 **7341c5a7089731f67356da5a588b269d4b69e8e6c4c054acf19aa4ef2837b529**. [Summary and port checks](summary.json), [repeated cost lifecycle](isolated_fresh_cost_lifecycle.json), [distinct cost lifecycle](unique_cost_lifecycle.json).

Run from repository root with bytecode disabled and HTTP scripts sequentially:

```text
python -B audit_evidence_claims/m9/db_ui_cost/run_db.py
python -B audit_evidence_claims/m9/db_ui_cost/run_ui.py
node audit_evidence_claims/m9/db_ui_cost/ui_missing_sponsor_count.js
python -B audit_evidence_claims/m9/db_ui_cost/ui_assertions.py
python -B audit_evidence_claims/m9/db_ui_cost/demo_http.py
python -B audit_evidence_claims/m9/db_ui_cost/cache_boundary_http.py
python -B audit_evidence_claims/m9/db_ui_cost/run_perf_current.py
python -B audit_evidence_claims/m9/db_ui_cost/cost_stress.py
python -B audit_evidence_claims/m9/db_ui_cost/fresh_cost.py isolated
python -B audit_evidence_claims/m9/db_ui_cost/unique_piece_cost.py isolated
python -B audit_evidence_claims/m9/db_ui_cost/unique_cost_http.py
```

`ui_assertions.py` uses root's fresh `m9/root_checks/http_results.json` and `served_try.html`. All Python scripts must run with `PYTHONDONTWRITEBYTECODE=1`; runners redirect temporary paths into this directory's `tmp/`.
