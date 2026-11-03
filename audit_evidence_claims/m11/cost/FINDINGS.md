# Round 11 cost review

Reviewed `2b9fc923f7b6f388f5babd2f998ed4c6e16d3439`; immediate predecessor `c364c84a289cfc3da5981708db3547ff6c752bde`. All script writes are under `audit_evidence_claims/m11/cost/`. No production file or database was edited; every owned CLI server on port **8894** was terminated and its port verified closed. Every DB before/after SHA-256 is `7341c5a7089731f67356da5a588b269d4b69e8e6c4c054acf19aa4ef2837b529`.

## Historical dispositions

| Earlier finding/control | Current disposition and evidence |
|---|---|
| **M5-S3**, cubic all-substring scans and exact 999-character answer timeout | **FIXED for exact reproduced defect.** The original answer (`" ".join(["x"]*500)`) returns HTTP 200 in **0.20895 s**, follower EGFR **0.02173 s**. Instrumented 250-token plain input: **2,224 calls per refusal predicate / 33,880 aggregate characters**, versus original M5 **31,625 / 10,479,750**. [HTTP](perf_check_http.json), [instrumentation](perf_current.json). |
| **M6 split_2000** control | **FIXED for exact repeated-piece control.** Same-data 3-sample median **0.16096 s**, versus buggy M7 revision `9bd7cb4` **2.28857 s**. Independent inherited stress sample median **0.23998 s** and `Engine.check` **0.63504 s**. [Comparison](fresh_cost_comparison.json), [stress](cost_stress.json). |
| **M7-S3**, repeated identical-piece resolver cost / queued map | **FIXED for exact reported defect.** Original `";".join(["x"]*2000)` HTTP check **0.49877 s**, queued EGFR **0.41989 s**, both 200; ordinary map afterward **0.02430 s**. Resolver instrumentation: repeated drug-bearing piece **1 cold / 0 warm calls**, unknown pieces **0**. [HTTP](fresh_cost_http.json), [calls](unique_piece_cost.json). |
| **M8-S1**, 4,097th resolver-cache entry | **FIXED.** **82/82** HTTP fill requests load 4,096 distinct pieces. First `osimertinib` and immediate retry both **200 / CHEMBL3353410 / 79 trials**. This correctness run overlapped other review work, so its timings are not used as isolated performance evidence. [HTTP](cache_boundary_http.json), [cleanup](cache_boundary_lifecycle.json). |
| **M8?M10 retained unique-piece contention should-fix** | **NOT FIXED**, nonblocking. `";".join(f"isa x{i:04d}" for i in range(400))` is 3,999 characters. Cold HTTP check **2.73397 s**, queued EGFR **2.65132 s**, warm check **0.33558 s**; ordinary before/after **0.03634 / 0.04164 s**, all 200. **400 cold / 0 warm** resolver calls. [HTTP](isolated_unique_cost_http.json), [instrumentation](unique_piece_cost.json). |

The bounded 8-token `_qualified` scan is at `src/query.py:119-141`; distinct-piece resolution and safe cache clearing are at `src/query.py:190-208`. Remaining full resolver work for each new drug-bearing piece occurs at `src/query.py:203`. The global HTTP engine lock and 4,000-character answer cap remain at `src/app.py:247-263`.

## New normalization cost controls

Workers load **HEAD^ and HEAD query modules against the same current dictionary/rules/database**. Values below are three-sample linker medians, not end-to-end guarantees. Other audit workers had stopped CPU-intensive scripts before these sequential runs; unrelated host activity is uncontrolled.

| Exact control | Characters | HEAD^ seconds | HEAD seconds |
|---|---:|---:|---:|
| `osimertinib` | 11 | 0.000092 | 0.000095 |
| `" ".join(["x"]*250)` | 499 | 0.02529 | 0.02784 |
| `" ".join(["x"]*2000)` | 3,999 | 0.19419 | 0.22970 |
| `" - ".join(["x"]*125)+"xx"` | 499 | 0.02761 | 0.03614 |
| `" - ".join(["x"]*1000)+"xx"` | 3,999 | 0.22475 | 0.42502 |
| `"trastuzumab "+("- "*240)+"89 - Zr"` | 499 | 0.03105 | 0.04806 |
| `";".join(["A33 124i"]*444)` | 3,995 | 0.07584 | 0.07841 |
| `";".join(["generic-version of bevacizumab"]*129)` | 3,998 | 0.02593 | 0.01468 |
| `"\ufdfa"*500` | 500 | 0.28885 | 0.41957 |
| `"\ufdfa"*4000` | 4,000 | 2.34056 | 2.67598 |

[Exact inputs/results](normalization_cost.json), [reproducer](normalization_cost.py). The initial generic-qualifier control accidentally used 133 repetitions / 4,122 characters; it was excluded from in-cap conclusions, preserved in [out-of-cap record](normalization_out_of_cap_control.json), and rerun at 129 / 3,998. The table and primary JSON use the corrected input.

The additional space-normalized representation at `src/query.py:130-134` and normalized isotope-neighbour/name checks at `src/query.py:246-266` have observable extra work on some controls. These samples do not establish a new practical timeout, nor prove overall linker complexity.

### Additional nonblocking cost case: normalization expansion

The answer `"\ufdfa"*4000` (4,000 ARABIC LIGATURE SALLALLAHOU ALAYHE WASALLAM characters) becomes **72,000 characters** after the NFKC fold (`src/query.py:116-117,170-173`). With UTF-8 JSON, the request is **12,030 bytes**, within the HTTP body-read cap as well as the answer cap. A fresh actual CLI server returns HTTP 200 in **2.44818 s**, while the queued ordinary EGFR map takes **2.36582 s**; retrying the same check takes **2.81211 s**. Ordinary maps before/after take **0.03610 / 0.04540 s**; GET remains responsive and all responses complete. [HTTP](isolated_unicode_cost_http.json), [size metadata](additional_execution.json), [cleanup](unicode_cost_lifecycle.json).

This is another input-cost/lock-contention should-fix; it already costs **2.34056 s** in the immediate-predecessor linker and is not presented as a new Round 11 defect or a blocker under the stated approval bar. A normalized-work budget should account for expansion while preserving refusal semantics.

## Reproduction and scope

[Reuse manifest](reuse_manifest.json) records the original m10 scripts (which preserve m5?m8 inputs), copies, and port/output adaptations. [Execution](execution.json), [cache execution](execution_cache.json), and [additional execution](additional_execution.json) record successful exits. Server lifecycle exit code 1 is the expected Windows `terminate()` cleanup; request scripts themselves exit 0. No model was called. Disease hub, ordinary demo responses, and the historical 24-request concurrency workload are covered by the parent/DB-UI evidence, not rerun unnecessarily here.

```powershell
python -B audit_evidence_claims/m11/cost/cache_boundary_http.py
python -B audit_evidence_claims/m11/cost/run_all.py
python -B audit_evidence_claims/m11/cost/unicode_cost_http.py
```

**Cost scope conclusion:** all exact previously repaired cost/cache reproductions remain fixed. Unique-piece contention remains a recorded nonblocker; normalized Unicode expansion adds a completed, bounded should-fix example. No cost result changes the originator-leak approval decision owned by the main report.
