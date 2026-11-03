"""Assemble this round's report from fresh, independently inspected evidence."""
from pathlib import Path
import json
import posixpath
import re

OUT = Path(__file__).resolve().parent

def read(rel):
    return (OUT / rel).read_text(encoding="utf8")

def data(rel):
    return json.loads(read(rel))

def links(text, prefix):
    return re.sub(r"\]\(([^)]+)\)", lambda m: "](" + posixpath.normpath(prefix + "/" + m.group(1)) + ")", text)

attack = read("attacks/FINDINGS.md")
blockers = attack.split("## M14-B1", 1)[1].split("## Reused earlier attacks and controls", 1)[0]
blockers = links("## M14-B1" + blockers, "attacks")
names = read("names/FINDINGS.md").split("## Individual historical dispositions", 1)[1].split("## Latest repair and remaining limits", 1)[0]
names = links(names, "names")
db = read("db_ui/FINDINGS.md").split("## Historical findings: individual dispositions", 1)[1].split("## Standards axis", 1)[0]
db = links(db, "db_ui")

norm = {(r["ref"], r["name"]): r for r in data("cost/normalization_cost.json")}
def median(ref, name):
    return f'{norm[ref, name]["median_seconds"]:.5f}'
unique = data("cost/isolated_unique_cost_http.json")
unicode = data("cost/isolated_unicode_cost_http.json")
oldnew = data("cost/fresh_cost_comparison.json")
split = {r["ref"]: r["median"] for r in oldnew if r["kind"] == "split" and r["size"] == 2000}
repeat = data("cost/fresh_cost_http.json")
plain = data("cost/perf_check_http.json")
http = data("root_checks/http_results.json")
perf = next(r for r in data("cost/perf_current.json") if r["kind"] == "plain" and r["size"] == 250)
head = data("integrity_before.json")["head"]
assert len(data("names/historical_name_dispositions.json")) == 64
assert len(norm) == 24
assert all(r["exit_code"] == 0 for r in data("cost/execution_isolated.json"))

intro = f"""# Independent relation-map review — round 14

Reviewed **`{head}`**. **Changes required: two P1 findings**, one regression introduced by the latest patch and one inherited refusal bypass. `3HVINBLASTINE` and `89Zrpanitumumab-PET-CT` pass every refusal stage and draw their originator molecules. The main M13 DARATUMUMAB reproductions are fixed; its supplementary `A33124I` example is still **NOT FIXED**.

No tracked file was edited. All new scripts, temporary files and results are under `audit_evidence_claims/m14/`. Existing m14 brief/log files were not edited by the audit. Known accepted over-refusals are retained as nonblockers. The verdict rests on reproduced originator leaks, not those over-refusals or performance observations.

## Verification and scope

- **341 passed in 30.33 s**, exit 0, using the requested `python -m pytest tests -q -p no:cacheprovider`; bytecode disabled and temporary paths confined to m14. [Output](root_checks/pytest.txt), [execution and hashes](root_checks/pytest_summary.json).
- Cumulative original HTTP reproducers were rerun, including the original m1 audit, m2b-m10 additions, exact m11 cases, and m12/m13 confirmations. All batches exit 0. Source scripts were reused with output-path/owned-port adaptations; original case inputs were retained. [Root manifest](reuse_manifest_root.json), [main batches](root_checks/execution_all.json), [m6](root_checks/execution_m6_http.json), [remaining](root_checks/execution_remaining.json), [m12/m13](root_checks/execution_rounds12_13.json).
- **55 reused name scripts / 45 executed leaf reproductions**, all exit 0, and **64 individual historical disposition rows** below. Replays include the **7,511-key** alias sweep and the **1,648-question** frozen counterfactual. Zero new lone-alias losses; `rad001c` alone recovered. The frozen comparison remains **68 identical / 1,556 metadata-only / 24 semantic / zero errors**. These comparisons swap methods against the same current data; they are not reconstructed historic deployments. [Name verification](names/FINDINGS.md), [manifest](names/reuse_manifest.json), [execution checks](names/worker_final_checks.json).
- Independent database oracle: **6,469 live centres, 22 relation/direction/type/role combinations, zero errors**. **19/19 DB assertions**, **24/24 UI assertions**, **4/4 self-loop/unknown-type/retirement fixture checks** pass. [Oracle](db_ui/db_validate.json), [DB](db_ui/db_assertions.json), [UI](db_ui/ui_assertions.json), [fixture](db_ui/self_loop_unknown.json).
- **36/36 page demos and six map callbacks pass**. All full demo objects equal each m7-m13 baseline. All 36 fresh CLI HTTP demo responses are 200 and equal direct Engine responses. Original QA evidence counts remain **12, 12, 11, 1, 12, 0, 0**. [Comparisons](db_ui/demo_previous_comparison.json), [HTTP](db_ui/demo_http.json), [callbacks](db_ui/ui_m3_checks.json).
- Attack matrices contain **97 current/HEAD^ direct comparison cases** and **308 final HTTP responses**, all HTTP 200. The root independently confirmed 24 cases through **96 HTTP requests**, and a separate reviewer traced both failures through `_marked` and the complete linker. [Attack execution](attacks/execution.json), [stages](attacks/edge_results.json), [independent HTTP](root_checks/independent_m14_http.json), [lifecycle](root_checks/independent_m14_lifecycle.json), [independent adjudication](db_ui/adjudication.md).

UI checks execute the actual page JavaScript in a Node VM with controlled DOM/fetch stubs. They verify generated markup and the exercised state/callback paths, not browser painting or browser-executed XSS. HTTP uses unmodified `src/app.py` or its real handler with isolated in-memory fixtures. No audit used port 8765 or called a model. Drug identity evidence comes from the repository dictionary, canonical keys and refused controls; no external pharmacology assumption is needed.

The successful raw-alias sweep does not cover every separator-removal/case variant of those aliases. It therefore does not contradict the transformed-alias regression below.

"""

independent = """Both findings were independently reproduced over the unmodified CLI server. The root responses contain the same centre IDs and **5/5** or **8/7** qualified QA evidence counts; the separated controls refuse. The second reviewer recorded `_marked` returning `None` for both current candidates. [Root confirmation](root_checks/independent_m14_http.json), [separate stage traces](db_ui/adjudication_tracer.json). No repair was implemented in this audit.

## Earlier reproductions — FIXED / NOT FIXED per finding

Dispositions classify the exact prior reproductions. A repaired spelling does not imply that every equivalent spelling is safe. m2 stopped without a completed report; its partial fixtures and the completed m2b findings are included. Known historical limitations remain visible instead of being counted as repaired.

### Name resolution, m1–m13
"""

supplement = """## Supplementary cases and accepted over-refusals

The explicitly accepted M5-S2, `40-o-(2-hydroxyethyl)-rapamycin`, `42-o-(2-hydroxyethyl)rapamycin`, `Trastuzumab--vcmmae conjugate`, `9-amino-20(s)-camptothecin`, `il-6ra` and `TAK-659F` remain **NOT FIXED / known over-refusals**, not blockers. In contrast, M12/M13 `rad001c` and `RAD001C` are now **FIXED**: EVEROLIMUS / CHEMBL1908360, nine live trials. [Fresh alias comparisons](names/new_alias_regression.json), [root HTTP](root_checks/independent_m13_http.json).

M13's supplementary **`A33124I` remains NOT FIXED**: it still maps ADAKITUG / CHEMBL5314551, while `A33 124i` refuses. Both keys are `a33124i`. This has zero trial/sponsor QA evidence but still draws the originator; it is a residual previously reported example, not a third newly counted finding. The complete M13 finding family therefore cannot be called fully repaired. [Exact previous/current stages](attacks/fresh_results.json), [root HTTP](root_checks/independent_m13_http.json).

`99MTc trastuzumab` and `[99MTc] trastuzumab` remain **FIXED**. The earlier descriptive-distance isotope and punctuated lexical-qualifier cases remain **NOT FIXED** where recorded, including `trastuzumab labelled with 89Zr`, `89Zr labeled trastuzumab`, `b.i.o.similar bevacizumab` and `lip.osomal doxorubicin`; they are retained as supplementary observations rather than newly counted findings. `Lutetium (177L.u) dotatate` remains **FIXED** (its historical centre was already isotope-labelled). [Original small replay](root_checks/fresh_probe.json), [reused 41-case matrix](attacks/focused_results.json), [attack assessment](attacks/FINDINGS.md).

Additional neighbouring-word casing boundary: `89ZRDFO trastuzumab` and `89zrDFO trastuzumab` draw TRASTUZUMAB, while `89ZrDFO trastuzumab` refuses. The helper requires exact upper/lower casing for two-letter elements too (`src/query.py:133-134`). This is recorded without inflating the two stored-alias findings. [Stage evidence](attacks/extra_neighbors.json).

The exact controls `13-cis retinoic acid`, `BKM-120NX`, `osimertinib 80 mg`, `paclitaxel 2 cycles` and `cisplatin 75 mg/m2 day 1` still select their intended Drugs. [Independent HTTP](root_checks/independent_m14_http.json).

"""

cost = f"""## Cost and performance reproductions

All nine inherited cost scripts exited 0, sequentially after the other reviewers finished their CPU/HTTP workloads. Unrelated host activity is uncontrolled. Timings are observations, not service-level guarantees or proof of global complexity. Historical comparisons substitute only `query.py` against the same current remaining modules and database. [Execution](cost/execution_isolated.json), [source provenance](reuse_manifest_root.json).

| Historical reproduction / exact workload | Current observation and disposition |
|---|---|
| M5-S3 cubic all-runs scan, `' '.join(['x']*250)` (499 characters) | **FIXED for the original workload**: 2,224 calls per predicate, 33,880 aggregate predicate-input characters; direct linking **{perf['seconds']:.5f} s**. [Instrumentation](cost/perf_current.json). |
| Original 999-character plain-answer timeout, `' '.join(['x']*500)` | **FIXED**: `/api/check` HTTP 200 in **{plain['slow_check_999_characters']['seconds']:.5f} s**; subsequent ordinary map **{plain['normal_after_check_timeout']['seconds']:.5f} s**. [HTTP](cost/perf_check_http.json). |
| M6/M7 repeated 2,000-piece resolver cost, `';'.join(['x']*2000)` | **FIXED for this exact repeated-piece control**: current direct-link median **{split['HEAD']:.5f} s** versus historical `9bd7cb4` **{split['9bd7cb4']:.5f} s**. HTTP check **{repeat['check']['seconds']:.5f} s**, queued EGFR **{repeat['queued_egfr']['seconds']:.5f} s**, both 200. [Comparison](cost/fresh_cost_comparison.json), [HTTP](cost/fresh_cost_http.json), [stress](cost/cost_stress.json). |
| M8-S1 natural 4,097th resolver-cache entry | **FIXED**: 82/82 fill requests create 4,096 distinct entries; first osimertinib at rollover and retry both HTTP 200 / CHEMBL3353410 / 79 trials. No KeyError. [HTTP](cost/cache_boundary_http.json). Original 7,511-key sweep also completes. |
| M10/M11/M12/M13 distinct-piece lock contention, `';'.join(f'isa x{{i:04d}}' for i in range(400))` (3,999 answer characters) | **NOT FIXED**, inherited cost concern: cold check **{unique['cold']['seconds']:.5f} s**, queued ordinary EGFR **{unique['queued_egfr']['seconds']:.5f} s**, warm check **{unique['warm']['seconds']:.5f} s**, all 200. Instrumentation: 400 cold / 0 warm resolver calls. [HTTP](cost/isolated_unique_cost_http.json), [instrumentation](cost/unique_piece_cost.json). |
| M11–M13 Unicode expansion, answer `'\\ufdfa'*4000` | **NOT FIXED**, inherited cost concern: 4,000 input characters become 72,000 under NFKC; check **{unicode['cold']['seconds']:.5f} s**, queued EGFR **{unicode['queued_egfr']['seconds']:.5f} s**, warm **{unicode['warm']['seconds']:.5f} s**, all 200. [HTTP](cost/isolated_unicode_cost_http.json). |
| M11–M13 punctuation normalization, `' - '.join(['x']*1000)+'xx'` (3,999 characters) | **NOT FIXED as measured overhead**, no timeout/data error: current / HEAD^ direct-link medians **{median('HEAD','separator_3999')} / {median('HEAD^','separator_3999')} s**; at 499 characters **{median('HEAD','separator_499')} / {median('HEAD^','separator_499')} s**. [Comparison](cost/normalization_cost.json). |
| M12/M13 repeated matches in one item, `' '.join(['isa']*1000)` | **NOT FIXED as measured overhead**, no failure: current / HEAD^ medians **{median('HEAD','matched_same_item_3999')} / {median('HEAD^','matched_same_item_3999')} s**. At 499 characters: **{median('HEAD','matched_same_item_499')} / {median('HEAD^','matched_same_item_499')} s**. [Comparison](cost/normalization_cost.json). |
| M13 repeated isotope alias, `';'.join(['A33 124i']*444)` | Current / HEAD^ medians **{median('HEAD','isotope_own_repeat')} / {median('HEAD^','isotope_own_repeat')} s**. No error. Cached osimertinib **{median('HEAD','demo_osimertinib')} / {median('HEAD^','demo_osimertinib')} s**. All 24 version/workload rows complete; three samples each do not establish a statistical regression/speedup. [Comparison](cost/normalization_cost.json). |
| Disease / ordinary concurrent map requests | Disease: 2,774 Trials + 300 Targets, 30 per list, **{http['cases']['disease']['bytes']:,} bytes / {http['cases']['disease']['ms']:.3f} ms**. 24 requests / 12 workers all expected HTTP 200 shapes, **{http['concurrency']['wall_ms']:.3f} ms** total. These ordinary samples overlapped early audit work. [HTTP](root_checks/http_results.json). |

`engine.lock` serializes engine operations (`src/app.py:247-263`), so costly legal check-answer requests delay maps. The 3,999/4,000-character stresses are direct-link or **answer-field** cases; `/api/explore` correctly rejects text over 500 characters. Limits precede NFKC (`src/app.py:239-243,260`; `src/query.py:116-117,190-192`). No deadlock or invented graph value was observed. These costs remain should-fix items; they do not determine the refusal verdict. No model cost was incurred.

"""

ending = """## Standards and specification

**Standards axis: zero documented violations found.** The application/UI diff from `bfcb83d` and latest query/test patch were inspected. No tracked repository AGENTS.md, CONTRIBUTING.md, CODING_STANDARDS.md or issue-tracker instructions were found. User-provided evidence-based, m14-only and no-tracked-edit requirements govern. KOA Studio / KhOpenApi original-versus-modified-code comparison applies when changing application code; none was changed. [Standards record](db_ui/standards_review.json).

**Specification axis: two P1 findings**, M14-B1 (regression) and M14-B2 (inherited). The main M13 repair works, but every refusal stage misses these stored-tracer variants. Correct edges around an incorrectly chosen originator do not meet the approval bar. The residual M13 `A33124I` example also remains unresolved. [Independent specification assessment](attacks/FINDINGS.md), [separate adjudication](db_ui/adjudication.md).

README app descriptions remain accurate (`README.md:566`, `README.ko.md:387`). The nearby test-count comments still say 317: **NOT FIXED**, a documentation-only should-fix; the actual suite has 341 passing tests. [Source assessment](db_ui/FINDINGS.md).

## Integrity and reproduction

`Engine.ask` sets `use_llm=False` (`src/app.py:180-181`); explore follows SELECT paths. Mutation fixtures use in-memory database copies. The app does not globally enforce a read-only SQLite handle, so the no-write result rests on source inspection, executed paths and byte equality rather than a database-permission guarantee.

Final checks compare **4,632 tracked-file SHA-256 hashes**, HEAD, tracked/staged diffs, database bytes, report links and owned-port cleanup. [Initial snapshot](integrity_before.json), [final verification](integrity_final.json). Database SHA-256: `7341c5a7089731f67356da5a588b269d4b69e8e6c4c054acf19aa4ef2837b529`.

Run from the repository root with bytecode disabled and TMP/TEMP/TMPDIR under the corresponding m14 family. Run shared-port suites sequentially and benchmarks after other suites. The manifests preserve original sources and adaptations; do not overwrite the initial integrity snapshot.

```text
python -B audit_evidence_claims/m14/root_checks/run_all.py
python -B audit_evidence_claims/m14/root_checks/run_rounds12_13.py
python -B audit_evidence_claims/m14/root_checks/independent_m14_http.py
python -B audit_evidence_claims/m14/names/run_round9.py
python -B audit_evidence_claims/m14/names/run_additional.py
python -B audit_evidence_claims/m14/names/run_completion.py
python -B audit_evidence_claims/m14/names/joined_label_probe.py
python -B audit_evidence_claims/m14/db_ui/run_db.py
python -B audit_evidence_claims/m14/db_ui/run_ui.py
python -B audit_evidence_claims/m14/db_ui/run_final.py
python -B audit_evidence_claims/m14/attacks/run.py
python -B audit_evidence_claims/m14/cost/run_isolated.py
python -B audit_evidence_claims/m14/build_report.py
python -B audit_evidence_claims/m14/finalize_integrity.py
```

VERDICT: CHANGES REQUIRED
"""

report = intro + blockers + independent + names + "\n### Database, UI and server, m1–m13\n" + db + supplement + cost + ending
(OUT / "REPORT.md").write_text(report, encoding="utf8")
print(json.dumps({"report_bytes": len(report.encode("utf8")), "historical_name_rows": 64, "verdict": report.rstrip().splitlines()[-1]}))
