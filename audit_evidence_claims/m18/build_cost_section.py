"""Build a report section from this round's measured, isolated cost results."""
from pathlib import Path
import json

OUT = Path(__file__).resolve().parent
def data(name):
    return json.loads((OUT / name).read_text(encoding='utf8'))
def sec(value):
    return f'{value:.5f}'

assert len(data('cost/execution_isolated.json')) == 9
assert all(r['exit_code'] == 0 for r in data('cost/execution_isolated.json'))
assert data('cost/repeated_match_execution.json')['exit_code'] == 0
norm = {(r['ref'], r['name']): r for r in data('cost/normalization_cost.json')}
assert len(norm) == 24 and all('median_seconds' in r for r in norm.values())
def med(ref, name):
    return sec(norm[ref, name]['median_seconds'])
plain = data('cost/perf_check_http.json')
perf = next(r for r in data('cost/perf_current.json') if r['kind']=='plain' and r['size']==250)
split = {r['ref']:r['median'] for r in data('cost/fresh_cost_comparison.json') if r['kind']=='split' and r['size']==2000}
repeat = data('cost/fresh_cost_http.json')
unique = data('cost/isolated_unique_cost_http.json')
unicode = data('cost/isolated_unicode_cost_http.json')
matched = data('cost/isolated_repeated_match_cost_http.json')
instrument = data('cost/repeated_match_instrumentation.json')
http = data('root_checks/http_results.json')
assert [r['helper_calls']['one_letter_false'] for r in instrument] == [1,1]
assert [r['helper_calls']['one_letter_true'] for r in instrument] == [250,2000]

text = f'''## Cost and performance reproductions

All nine inherited cost scripts exited zero, sequentially after other audit CPU/HTTP workloads finished. The additional M16 repeated-match instrumentation and HTTP reproducer also exited zero. Unrelated host load is uncontrolled; these are measurements, not service guarantees. Counterfactuals substitute only historical `query.py` against the same current app/data. [Execution](cost/execution_isolated.json), [provenance](reuse_manifest_root.json), [M16 follow-up execution](cost/repeated_match_execution.json).

| Historical finding / exact workload | Current disposition and measured evidence |
|---|---|
| M5-S3 cubic qualifier scan, `' '.join(['x']*250)` (499 chars) | **FIXED for the original workload.** {perf['calls']['is_distinct_product']:,} calls to each predicate / {perf['calls']['characters']:,} aggregate predicate-input characters, {sec(perf['seconds'])} s direct. [Instrumentation](cost/perf_current.json). |
| Original 999-character plain-answer timeout, `' '.join(['x']*500)` | **FIXED.** HTTP check 200 in {sec(plain['slow_check_999_characters']['seconds'])} s; later map {sec(plain['normal_after_check_timeout']['seconds'])} s. [HTTP](cost/perf_check_http.json). |
| M6/M7 repeated 2,000-piece resolver cost, `';'.join(['x']*2000)` | **FIXED for this repeated-piece control.** Current / historical `9bd7cb4` direct medians {sec(split['HEAD'])} / {sec(split['9bd7cb4'])} s. HTTP check {sec(repeat['check']['seconds'])} s, queued EGFR {sec(repeat['queued_egfr']['seconds'])} s, both 200. [Comparison](cost/fresh_cost_comparison.json), [HTTP](cost/fresh_cost_http.json), [stress](cost/cost_stress.json). |
| M8-S1 4,097th resolver-cache entry | **FIXED.** 82/82 fill requests succeed; rollover and retry return OSIMERTINIB / CHEMBL3353410 with 79 trials, no KeyError. [HTTP](cost/cache_boundary_http.json). |
| M10-M17 distinct-piece lock delay, `';'.join(f'isa x{{i:04d}}' for i in range(400))` | **NOT FIXED**, inherited cost concern. Cold check {sec(unique['cold']['seconds'])} s, queued EGFR {sec(unique['queued_egfr']['seconds'])} s, warm {sec(unique['warm']['seconds'])} s; all 200. [HTTP](cost/isolated_unique_cost_http.json), [instrumentation](cost/unique_piece_cost.json). |
| M11-M17 Unicode expansion, answer `'\\ufdfa'*4000` | **NOT FIXED**, inherited cost concern. 4,000 chars expand to 72,000 under NFKC. Cold check {sec(unicode['cold']['seconds'])} s, queued EGFR {sec(unicode['queued_egfr']['seconds'])} s, warm {sec(unicode['warm']['seconds'])} s; all 200. [HTTP](cost/isolated_unicode_cost_http.json). |
| M11-M17 punctuation normalization, `' - '.join(['x']*1000)+'xx'` | **NOT FIXED as measured overhead**, no error. Current / HEAD^ medians {med('HEAD','separator_3999')} / {med('HEAD^','separator_3999')} s; at 499 chars {med('HEAD','separator_499')} / {med('HEAD^','separator_499')} s. [Comparison](cost/normalization_cost.json). |
| M12-M17 repeated matches, `' '.join(['isa']*1000)` | **NOT FIXED as residual repeated-match overhead**; **M16-S1 added isotope rescans FIXED**, detailed below. Current / HEAD^ direct medians {med('HEAD','matched_same_item_3999')} / {med('HEAD^','matched_same_item_3999')} s; at 499 chars {med('HEAD','matched_same_item_499')} / {med('HEAD^','matched_same_item_499')} s. [Comparison](cost/normalization_cost.json). |
| M13-M17 repeated isotope alias, `';'.join(['A33 124i']*444)` | No error reproduced. Current / HEAD^ medians {med('HEAD','isotope_own_repeat')} / {med('HEAD^','isotope_own_repeat')} s. Cached ordinary OSIMERTINIB {med('HEAD','demo_osimertinib')} / {med('HEAD^','demo_osimertinib')} s. All 24 workload/version rows complete. [Comparison](cost/normalization_cost.json). |
| Disease / ordinary concurrent maps | No failure reproduced: 2,774 Trials + 300 Targets, 30 per list, **{http['cases']['disease']['bytes']:,} bytes / {http['cases']['disease']['ms']:.3f} ms**. 24 requests / 12 workers all expected HTTP200 shapes in **{http['concurrency']['wall_ms']:.3f} ms**. These ordinary early samples overlapped other audit work. [HTTP](root_checks/http_results.json). |

### M16-S1: the item's isotope state is now computed once

**FIXED for the exact reported extra work.** At 125 / 1,000 occurrences, instrumentation records **one whole-item scan** and **250 / 2,000 within-word helper calls**, respectively. M16 originally recorded 125 / 1,000 whole-item scans and 15,625 / 1,000,000 within-word calls. M17 recorded one scan with 125 / 1,000 within-word calls. The latest patch checks both the canonical word and its punctuation piece, which are identical for `isa`; this doubles those within-word calls but does not restore per-match whole-item rescanning. `@functools.lru_cache(maxsize=4096)` caches the pure tuple-keyed computation (`src/query.py:154-173`), called from `_marked` at `src/query.py:398-400`. The same single ISATUXIMAB entity survives. [Fresh instrumentation](cost/repeated_match_instrumentation.json), [reused script](cost/repeated_match_followup.py).

For the legal 3,999-character **answer** field, the fresh HTTP check takes **{sec(matched['cold']['seconds'])} s**, queues EGFR for **{sec(matched['queued_egfr']['seconds'])} s**, and takes **{sec(matched['warm']['seconds'])} s** warm. The ordinary map after completion takes {sec(matched['after']['seconds'])} s; all return 200. This verifies the repair without claiming all repeated-match work was removed. `_marked` still constructs/scans token lists before checking the cache and runs before entity deduplication (`src/query.py:343-371,556-566`). [HTTP](cost/isolated_repeated_match_cost_http.json), [closed owned server / unchanged DB](cost/repeated_match_cost_lifecycle.json).

`engine.lock` serializes API operations (`src/app.py:247-263`). These 3,999/4,000-character workloads use direct linking or the **answer field**; explore correctly rejects more than 500 characters. Limits precede NFKC (`src/app.py:239-243,260`; `src/query.py:117-118,257-259`). Residual costs are should-fix observations, not the reason for the verdict. **No model calls or model cost were incurred.**
'''
(OUT/'cost_section.md').write_text(text, encoding='utf8')
print('Cost section written from fresh results.')
