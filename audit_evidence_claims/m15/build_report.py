"""Assemble the independent round-15 report from this round's fresh evidence."""
from pathlib import Path
import json, posixpath, re

OUT = Path(__file__).resolve().parent
def read(rel):
    return (OUT/rel).read_text(encoding='utf8')
def data(rel):
    return json.loads(read(rel))
def links(text, prefix):
    return re.sub(r'\]\(([^)]+)\)', lambda m: ']('+posixpath.normpath(prefix+'/'+m.group(1))+')', text)

head = data('integrity_before.json')['head']
name_rows = data('names/historical_name_dispositions.json')
assert len(name_rows) == 69
assert data('db_ui/db_validate.json')['errors'] == []
assert data('db_ui/db_assertions.json')['passed'] == 19
assert data('db_ui/ui_assertions.json')['passed'] == 24
assert data('root_checks/pytest_summary.json')['exit_code'] == 0
assert len(data('cost/execution_isolated.json')) == 9
assert all(r['exit_code'] == 0 for r in data('cost/execution_isolated.json'))

attack = read('attacks/FINDINGS.md')
blockers = '## M15-B1'+attack.split('## M15-B1',1)[1].split('## Replays, controls and exploratory limits',1)[0]
blockers = blockers.replace('## Residual M14-B1 —', '## M15-B2 — residual M14-B1:')
blockers = links(blockers, 'attacks')
names = links(read('names/FINDINGS.md').split('## Individual historical dispositions',1)[1].split('## Repair interpretation and limits',1)[0], 'names')
db = links(read('db_ui/FINDINGS.md').split('## Historical findings: individual dispositions',1)[1].split('## Standards axis',1)[0], 'db_ui')
norm = {(r['ref'],r['name']):r for r in data('cost/normalization_cost.json')}
assert len(norm) == 24 and all('median_seconds' in r for r in norm.values())
def median(ref, name):
    return f"{norm[ref,name]['median_seconds']:.5f}"
unique = data('cost/isolated_unique_cost_http.json')
unicode = data('cost/isolated_unicode_cost_http.json')
split = {r['ref']:r['median'] for r in data('cost/fresh_cost_comparison.json') if r['kind']=='split' and r['size']==2000}
repeat = data('cost/fresh_cost_http.json')
plain = data('cost/perf_check_http.json')
http = data('root_checks/http_results.json')
perf = next(r for r in data('cost/perf_current.json') if r['kind']=='plain' and r['size']==250)

intro = f'''# Independent relation-map review — round 15

Reviewed **`{head}`**. **Changes required: one newly reproduced P1 refusal bypass, plus an unresolved P1 family from M14.** `89-ZrDFO trastuzumab` passes every refusal stage and draws TRASTUZUMAB; adding one hyphen to a refused control is sufficient. The literal earlier `3hvinblastine` also still draws VINBLASTINE. The upper-case repair cases, PANITUMUMAB PET/CT variants, and original `A33124I` are **FIXED**. No new regression introduced by this latest patch was demonstrated.

All new files are under `audit_evidence_claims/m15/`. No tracked file or application code was edited. The verdict does not count the explicitly accepted over-refusals or ChEMBL bevacizumab-development-code limitation as blockers.

## Verification and scope

- **342 passed in 30.64 s**, exit 0, with `python -m pytest tests -q -p no:cacheprovider`. Bytecode disabled; temporary paths confined to m15. [Output](root_checks/pytest.txt), [execution/hashes](root_checks/pytest_summary.json).
- Cumulative original HTTP scripts were reused for m1, partial m2/completed m2b, m3-m11, then exact m12/m13 and m14 confirmations. Every execution batch exited zero; original historical input lists were preserved. [Source/adaptation manifest](reuse_manifest_root.json), [main batches](root_checks/execution_all.json), [m6](root_checks/execution_m6_http.json), [remaining](root_checks/execution_remaining.json), [m12/m13](root_checks/execution_rounds12_13.json), [m14 HTTP](root_checks/independent_m14_http.json).
- **58 copied name scripts / 47 executed reused leaf reproductions**, plus one supplemental wrapper; **69 individual historical name dispositions** below. The **7,511-key** raw-alias sweep has no new loss or recovery versus m14. The **1,648-question** frozen counterfactual remains **68 identical / 1,556 metadata-only / 24 semantic / zero errors**. These are same-current-data method comparisons, not reconstructed historical deployments. [Name assessment](names/FINDINGS.md), [manifest](names/reuse_manifest.json), [execution checks](names/worker_final_checks.json).
- Stored-row oracle: **6,469 live centres, 22 relation/direction/type/role combinations, zero errors**. **19/19 DB assertions, 24/24 UI assertions and 4/4 self-loop/unknown-type/retirement fixture checks pass**. [Oracle](db_ui/db_validate.json), [DB](db_ui/db_assertions.json), [UI](db_ui/ui_assertions.json), [fixture](db_ui/self_loop_unknown.json).
- **36/36 page demos** equal all m7-m14 full response baselines. **36/36 fresh CLI HTTP demos** return 200 and exactly equal direct Engine responses. Six map callbacks pass; original seven QA evidence counts remain **12, 12, 11, 1, 12, 0, 0**. [Comparisons](db_ui/demo_previous_comparison.json), [HTTP](db_ui/demo_http.json), [callbacks](db_ui/ui_m3_checks.json).
- **97 original m14 direct attack cases** rerun unchanged, **29 targeted current/HEAD^ stage cases**, and **116 targeted CLI HTTP responses**, all 200. An exploratory **428 variants / 104 stored keys** scan found no additional promoted family. Its raw acceptance count includes already-labelled drugs and chemical locants, so it is not a defect count. [Attack execution](attacks/execution.json), [stages](attacks/targeted_results.json), [scan](attacks/alias_variants.json).
- The root independently repeated **11 candidate/control cases through 44 HTTP requests** and the **24-case M14 matrix through 96 requests**, all 200. Another reviewer independently captured the raw-helper versus normalized-fragment failure. [Root M15 HTTP](root_checks/independent_m15_http.json), [M15 lifecycle](root_checks/independent_m15_lifecycle.json), [M14 lifecycle](root_checks/independent_m14_lifecycle.json), [independent adjudication](db_ui/adjudication.md).

UI checks execute actual page JavaScript in a Node VM with controlled DOM/fetch stubs. They establish generated markup and exercised state/callback behavior, not browser painting or browser-executed XSS. HTTP uses unmodified `src/app.py` on owned ports other than 8765, or its real handler with isolated in-memory fixtures. No model was called. Tracer identity is established from stored aliases, normalization equivalence and refused controls; this review does not claim an external validation of the entire medical-isotope table.

The hypothesis for the naming attacks was that equivalent punctuation/case forms of an identified refused tracer retain that identity through every resolution stage. The following paired controls falsify that hypothesis. Successful demos, tests and raw-alias sweeps do not cover all transformed aliases or neighbouring label forms.

'''

independent = '''## Independent confirmation and required outcome

The new punctuation bypass is sufficient for **CHANGES REQUIRED** even without the lower-case residual. It changes neither the named drug nor the label's distance: `89ZrDFO trastuzumab` refuses, while `89-ZrDFO trastuzumab` selects CHEMBL1201585. The raw helper itself recognizes the hyphenated word. The fix therefore needs to preserve recognized adjacent isotope/chelator identity through normalization. The residual stored-tracer case needs identity preservation for a known refused alias; it does not require interpreting every lower-case chemical locant as an isotope. No repair was implemented here.

Root HTTP independently confirms TRASTUZUMAB's **13 live trials / 12 trial-QA / 12 sponsor-QA** and VINBLASTINE's **5 / 5 / 5**; the controls return zero QA evidence. `A33124i` draws ADAKITUG with zero trials; zero evidence does not make the wrong centre acceptable. With `89-ZrDFO trastuzumab, osimertinib`, the wrong TRASTUZUMAB centre remains; reversing the list selects OSIMERTINIB but still accepts the qualified TRASTUZUMAB hit without refusal. [Root responses](root_checks/independent_m15_http.json), [separate stage traces](db_ui/adjudication_tracer.json).

## Earlier reproductions — FIXED / NOT FIXED per finding

The tables classify exact historical reproductions, including nonblocking qualifications. M2 ended without a completed report; its partial fixtures and completed M2b results are included. A repaired spelling is not evidence that all equivalent spellings are fixed.

### Name resolution, m1-m14
'''

supplement = '''## Known limitations and regressions

The expressly accepted M5-S2, `40-o-(2-hydroxyethyl)-rapamycin`, `42-o-(2-hydroxyethyl)rapamycin`, `Trastuzumab--vcmmae conjugate`, `9-amino-20(s)-camptothecin`, `il-6ra` and `TAK-659F` remain **NOT FIXED / known over-refusals**, not blockers. `rad001c` and `RAD001C` remain restored to EVEROLIMUS. [Alias controls](names/alias_loss_controls.json), [current/previous controls](names/new_alias_regression.json).

`HLX04`, `HLX-04`, `HLX04-O`, `BAT1706`, `SB8`, `MB02`, `FKB238` and `BI 695502` still select BEVACIZUMAB. This is the user's explicitly recorded ChEMBL synonym limitation, **not a map defect**. [Fresh code controls](names/m14_supplement.json).

Old distant-label and fragmented-qualifier supplements remain where previously recorded: for example `trastuzumab labelled with 89Zr`, `89Zr labeled trastuzumab`, `b.i.o.similar bevacizumab` and `lip.osomal doxorubicin`. They are reported as **NOT FIXED supplementary gaps**, not newly discovered families. The old casing observations `89ZRDFO trastuzumab` and `89zrDFO trastuzumab` likewise remain. [Reused focused matrix](attacks/focused_results.json), [exact old supplements](names/m14_supplement.json). This does not weaken the independently sufficient new punctuation-only reproduction.

The raw stored-alias loss set is unchanged versus m14. Ordinary controls `13-cis retinoic acid`, `BKM-120NX`, `NSC-118218H`, `DX-8951F`, `GW572016F`, `osimertinib 80 mg`, `paclitaxel 2 cycles` and `cisplatin 75 mg/m2 day 1` preserve their identities. Upper-case M14 cases and PET/CT variants are repaired. No new demo regression or stored-value defect was observed. [Targeted controls](attacks/targeted_results.json), [independent dose controls](root_checks/independent_m14_http.json).

Failure-closed presentation qualification: the exact slash-bearing control `89zr-panitumumab-pet/ct` returns HTTP 200 with `not_found`, rather than an explicit `refused` message. It draws no centre. This should-fix distinction must not be described as an explicit refusal; the reported M14-B2 glued/hyphen PETCT reproductions do explicitly refuse. [Exact HTTP response](root_checks/independent_m14_http.json).

'''

cost = f'''## Cost and performance reproductions

All **nine inherited cost scripts** exited zero, run sequentially after the other reviewers' CPU/HTTP work finished. Unrelated host activity is uncontrolled. Timings are observations, not service-level guarantees or proof of global complexity. Historical comparisons substitute only `query.py` against the same current remaining modules and database. [Execution](cost/execution_isolated.json), [provenance](reuse_manifest_root.json).

| Historical reproduction / exact workload | Current result and disposition |
|---|---|
| M5-S3 cubic scan, `' '.join(['x']*250)` (499 characters) | **FIXED for this original workload**: {perf['calls']['is_distinct_product']:,} calls to each predicate, {perf['calls']['characters']:,} aggregate predicate-input characters, **{perf['seconds']:.5f} s** direct linking. [Instrumentation](cost/perf_current.json). |
| Original 999-character plain-answer timeout, `' '.join(['x']*500)` | **FIXED**: `/api/check` 200 in **{plain['slow_check_999_characters']['seconds']:.5f} s**; subsequent ordinary map **{plain['normal_after_check_timeout']['seconds']:.5f} s**. [HTTP](cost/perf_check_http.json). |
| M6/M7 repeated 2,000-piece resolver cost, `';'.join(['x']*2000)` | **FIXED for this exact repeated-piece control**: current direct median **{split['HEAD']:.5f} s**, historical `9bd7cb4` **{split['9bd7cb4']:.5f} s**. HTTP check **{repeat['check']['seconds']:.5f} s**, queued EGFR **{repeat['queued_egfr']['seconds']:.5f} s**, both 200. [Comparison](cost/fresh_cost_comparison.json), [HTTP](cost/fresh_cost_http.json), [stress](cost/cost_stress.json). |
| M8-S1 natural 4,097th cache entry | **FIXED**: 82/82 fill requests create 4,096 entries; first OSIMERTINIB at rollover and retry both 200 / CHEMBL3353410 / 79 trials. No KeyError. [HTTP](cost/cache_boundary_http.json). |
| M10-M14 distinct-piece lock contention, `';'.join(f'isa x{{i:04d}}' for i in range(400))` (3,999 answer characters) | **NOT FIXED**, inherited cost concern: cold check **{unique['cold']['seconds']:.5f} s**, queued EGFR **{unique['queued_egfr']['seconds']:.5f} s**, warm **{unique['warm']['seconds']:.5f} s**, all 200. 400 cold / 0 warm resolver calls. [HTTP](cost/isolated_unique_cost_http.json), [instrumentation](cost/unique_piece_cost.json). |
| M11-M14 Unicode expansion, answer `'\\ufdfa'*4000` | **NOT FIXED**, inherited cost concern: 4,000 characters expand to 72,000 under NFKC; cold check **{unicode['cold']['seconds']:.5f} s**, queued EGFR **{unicode['queued_egfr']['seconds']:.5f} s**, warm **{unicode['warm']['seconds']:.5f} s**, all 200. [HTTP](cost/isolated_unicode_cost_http.json). |
| M11-M14 punctuation normalization, `' - '.join(['x']*1000)+'xx'` | **NOT FIXED as measured overhead**, no failure: current / HEAD^ medians **{median('HEAD','separator_3999')} / {median('HEAD^','separator_3999')} s**; at 499 characters **{median('HEAD','separator_499')} / {median('HEAD^','separator_499')} s**. [Comparison](cost/normalization_cost.json). |
| M12-M14 repeated matches, `' '.join(['isa']*1000)` | **NOT FIXED as measured overhead**, no failure: current / HEAD^ medians **{median('HEAD','matched_same_item_3999')} / {median('HEAD^','matched_same_item_3999')} s**; at 499 characters **{median('HEAD','matched_same_item_499')} / {median('HEAD^','matched_same_item_499')} s**. [Comparison](cost/normalization_cost.json). |
| M13/M14 repeated isotope alias, `';'.join(['A33 124i']*444)` | **No error reproduced**: current / HEAD^ medians **{median('HEAD','isotope_own_repeat')} / {median('HEAD^','isotope_own_repeat')} s**. Cached OSIMERTINIB **{median('HEAD','demo_osimertinib')} / {median('HEAD^','demo_osimertinib')} s**. All 24 version/workload rows finish; three samples each do not establish a statistical regression/speedup. [Comparison](cost/normalization_cost.json). |
| Disease / ordinary concurrent maps | **No failure reproduced**: 2,774 Trials + 300 Targets, 30 per list, **{http['cases']['disease']['bytes']:,} bytes / {http['cases']['disease']['ms']:.3f} ms**. 24 requests / 12 workers all expected HTTP 200 shapes, **{http['concurrency']['wall_ms']:.3f} ms** total. These early ordinary samples overlapped other audit work. [HTTP](root_checks/http_results.json). |

`engine.lock` serializes operations (`src/app.py:247-263`), so costly legal check-answer requests delay maps. The 3,999/4,000-character stresses are direct-link or **answer-field** cases; explore correctly rejects input longer than 500 characters. Input limits precede NFKC (`src/app.py:239-243,260`; `src/query.py:116-117,203-205`). No deadlock or invented value was observed. These inherited costs remain should-fix items and do not determine the verdict. **No model call or model cost was incurred.**

'''

ending = '''## Standards and specification

**Standards axis: zero documented violations found.** The app/UI diff from `bfcb83d` and latest query/test patch were reviewed. No tracked repository AGENTS.md, CONTRIBUTING.md, CODING_STANDARDS.md or issue-tracker instructions were found. User-provided evidence-based, m15-only and no-tracked-edit requirements govern. The requested KOA Studio / KhOpenApi original-versus-modified-code comparison is conditional on changing application code; none was changed. [Standards record](db_ui/standards_review.json).

**Specification axis: one new P1 family and one unresolved P1 family.** M15-B1 is a new reproduction of an inherited neighbouring-label normalization defect; M15-B2 records the lower-case residual of M14-B1 with an A33 corroboration. The latest upper-case, PET/CT and `A33124I` repairs work as described, but the original no-originator-leak approval bar remains unmet. The new finding alone suffices. [Independent attack assessment](attacks/FINDINGS.md), [separate adjudication](db_ui/adjudication.md).

README app descriptions remain accurate (`README.md:566`, `README.ko.md:387`). Nearby comments still say 317 tests: **NOT FIXED**, documentation-only should-fix; the actual suite has 342 passing tests. [Source assessment](db_ui/FINDINGS.md).

## Integrity and reproduction

`Engine.ask` explicitly sets `use_llm=False` (`src/app.py:180-181`); explore follows SELECT paths. Mutation fixtures use in-memory copies. The application does not enforce a globally read-only SQLite handle; the no-write conclusion rests on inspected/executed paths and byte equality, not a DB-permission guarantee.

Final verification compares **5,104 tracked-file SHA-256 hashes**, HEAD, tracked/staged diffs, database bytes, report links and owned-port cleanup. [Initial snapshot](integrity_before.json), [final verification](integrity_final.json). Database SHA-256: `7341c5a7089731f67356da5a588b269d4b69e8e6c4c054acf19aa4ef2837b529`.

Run from repository root with bytecode disabled and TMP/TEMP/TMPDIR under each m15 family's `tmp/`. Run shared-port suites sequentially and cost after other workloads. The manifests identify original scripts and adaptations; do not overwrite the initial integrity snapshot.

```text
python -B audit_evidence_claims/m15/root_checks/run_all.py
python -B audit_evidence_claims/m15/root_checks/run_rounds12_13.py
python -B audit_evidence_claims/m15/root_checks/independent_m14_http.py
python -B audit_evidence_claims/m15/root_checks/independent_m15_http.py
python -B audit_evidence_claims/m15/names/run_round9.py
python -B audit_evidence_claims/m15/names/run_additional.py
python -B audit_evidence_claims/m15/names/run_completion.py
python -B audit_evidence_claims/m15/db_ui/run_db.py
python -B audit_evidence_claims/m15/db_ui/run_ui.py
python -B audit_evidence_claims/m15/db_ui/run_final.py
python -B audit_evidence_claims/m15/attacks/targeted_probe.py
python -B audit_evidence_claims/m15/attacks/targeted_http.py
python -B audit_evidence_claims/m15/cost/run_isolated.py
python -B audit_evidence_claims/m15/build_report.py
python -B audit_evidence_claims/m15/finalize_integrity.py
```

VERDICT: CHANGES REQUIRED
'''

report = intro+blockers+independent+names+'\n### Database, UI and server, m1-m14\n'+db+supplement+cost+ending
(OUT/'REPORT.md').write_text(report,encoding='utf8')
print(json.dumps(dict(bytes=len(report.encode('utf8')),historical_name_rows=len(name_rows),verdict=report.rstrip().splitlines()[-1])))
