"""Assemble the independent audit from current executions, preserving finding identities."""
from pathlib import Path
import json,re
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[1]
def read(path):return json.loads((OUT/path).read_text(encoding='utf8'))
old=(ROOT/'audit_evidence_claims/m11/REPORT.md').read_text(encoding='utf8')
history=old[old.index('### M1\n'):old.index('## Cost and nonblocking findings')]
history=history.replace('Round 11 disposition','Round 12 disposition').replace('Round 11 result','Round 12 result')
# Query lines after the new insertion moved. Historical evidence links are current;
# retain unchanged app/page references, remove obsolete query line coordinates.
history=re.sub(r'`src/query\.py:[^`]+`', '`src/query.py`',history)
history=history.replace('249-265','249-280')
history += '''### M11

| Finding / exact reproduction | Round 12 result |
|---|---|
| M11-B1 `[89Z.r] trastuzumab`, `89Z_r trastuzumab`, `trastuzumab [89Z.r]` | **FIXED** — all refuse; trial/sponsor QA zero; adding `, osimertinib` selects only OSIMERTINIB. [Exact stages](names/m11_exact.json), [original 26-case script](names/m11_attacks/key_equivalence_results.json), [60 HTTP responses](root_checks/new_leaks_http.json). |
| M11-B2 `bevacizumab a - w w b`, `bevacizumab - a - w - w - b`, `bevacizumab a_w_w_b` | **FIXED** — all refuse; trial/sponsor QA zero; separate osimertinib survives. [Literal checks](names/m11_exact.json), [HTTP](root_checks/new_leaks_http.json). |
| M11-S1 `9-amino-20(s)-camptothecin` | **NOT FIXED — explicitly accepted over-refusal**; preferred name/ID still reach CHEMBL274070. [Controls](names/alias_loss_controls.json). |
| M11-S1 `il-6ra` | **NOT FIXED — explicitly accepted over-refusal**; preferred name/ID still reach CHEMBL1237022. [Controls](names/alias_loss_controls.json). |
| M11-S1 `TAK-659F` | **NOT FIXED — explicitly accepted over-refusal**; preferred name/ID still reach CHEMBL3979920. [Controls](names/alias_loss_controls.json). |
| M11 distinct-piece lock contention / U+FDFA expansion | **NOT FIXED**, nonblocking performance concern; exact workloads rerun below. [Unique HTTP](cost/isolated_unique_cost_http.json), [Unicode HTTP](cost/isolated_unicode_cost_http.json). |
| M11 supplementary, previously unpromoted `trastuzumab labelled with 89Zr`, `trastuzumab labeled with 89Zr`, `89Zr labeled trastuzumab`, `89Zr conjugated trastuzumab` | **NOT FIXED** — same originator maps as m11; not counted as a newly introduced defect or a separate blocker. [Reused original script](root_checks/fresh_probe.json), [current/previous adjudication](db_ui/adjudication.md). |
| M11 supplementary `99MTc trastuzumab`, `[99MTc] trastuzumab` | **FIXED** — now refuse; bare trastuzumab control still maps. [Reused original script](root_checks/fresh_probe.json). |
| M11 punctuation-only cost overhead | **NOT FIXED as a cost concern** — comparable synthetic normalization overhead remains; no timeout or data error. [Same-data comparison](cost/normalization_cost.json). |

'''
perf=read('cost/perf_check_http.json');unique=read('cost/isolated_unique_cost_http.json');unicode=read('cost/isolated_unicode_cost_http.json');fresh=read('cost/fresh_cost_http.json')
comparison=read('cost/fresh_cost_comparison.json');norm=read('cost/normalization_cost.json')
def med(name,ref):return next(r['median_seconds'] for r in norm if r['name']==name and r['ref']==ref)
def sec(row):return f"{row['seconds']:.5f}"
split=next(r['median'] for r in comparison if r['ref']=='HEAD' and r['kind']=='split' and r['size']==2000)
splitold=next(r['median'] for r in comparison if r['ref']=='9bd7cb4' and r['kind']=='split' and r['size']==2000)
report='''# Independent relation-map review — round 12

Reviewed **`d9260a1ea544cf7bb80415383667784e0aba146a`**, beginning 2026-11-03 KST. **Changes required:** the exact reported blocking reproductions from m1–m11 are fixed, but a stored tracer alias still passes every refusal stage and draws its originator. One additional stored-alias over-refusal was introduced by the latest repair. No tracked file was edited; all new audit artifacts are under `audit_evidence_claims/m12/`.

The verdict is based on **one P1 blocker, M12-B1**. Known accepted over-refusals, retained policy limitations and measured performance costs are reported separately and do not determine it.

## Verification and limits

- **339 passed in 38.09 s**, exit 0: `python -m pytest tests -q -p no:cacheprovider`, bytecode disabled and temporary paths confined to m12. [Output](root_checks/pytest.txt), [environment/hash record](root_checks/pytest_summary.json).
- Reused the earlier root HTTP runners sequentially: six original/cumulative runners, four M6 runners, M8/M9 confirmations, both M10 confirmations and the M11 exact confirmation. All exit 0. [Reuse manifest](reuse_manifest_root.json), [batch](root_checks/execution_all.json), [six runners](root_checks/execution_http.json), [M6](root_checks/execution_m6_http.json), [M8/M9](root_checks/execution_extra.json), [remaining](root_checks/execution_remaining.json). Original reproduction inputs and historical comparison sources were retained; output paths and owned ports were adapted.
- Naming replays executed **41 reused leaf scripts**, from **47 copied prior scripts**, all exit 0. This includes the original M1 scripts, cumulative M2b–M11 matrices, **7,511-key** alias sweep, **1,648-question** frozen no-relink counterfactual, M9's 146-input probe, M10's 1,224-input probe and 35-case focus, and M11's 26-case attack script. Counterfactual counts remain **68 identical / 1,556 metadata-only / 24 semantic / zero errors**. These are declared same-data method counterfactuals, not whole-deployment version comparisons. [Name report and 59 individual rows](names/FINDINGS.md), [manifest](names/reuse_manifest.json), [final checks](names/worker_final_checks.json).
- Independent graph oracle: **6,469 live centres, 22 relation/direction/type/role combinations, zero errors**. **19/19 DB assertions**, **24/24 UI assertions** and **4/4 self-loop/unknown-type/retirement fixture checks** pass. [DB/UI report](db_ui/FINDINGS.md), [oracle](db_ui/db_validate.json), [DB assertions](db_ui/db_assertions.json), [UI assertions](db_ui/ui_assertions.json), [fixture](db_ui/self_loop_unknown.json).
- All **36 page demos plus six map callbacks** pass. All 36 full demo responses equal m7–m11; all 36 actual CLI HTTP demo requests return 200 and equal Engine responses. The seven original QA evidence counts remain **12, 12, 11, 1, 12, 0, 0**. [Comparison](db_ui/demo_previous_comparison.json), [HTTP](db_ui/demo_http.json), [demo renders](db_ui/ui_demos_results.json), [six map callbacks](db_ui/ui_m3_checks.json).
- New attacks compare **41** inputs with current and HEAD^ query modules, and issue **76** actual HTTP requests. Root independently issued **56** further HTTP requests including the blocker, refused/bare controls, separate-osimertinib input, descriptive tracer probes and the new alias loss. All returned 200; owned servers closed; served page matches `web/try.html`. [Attack stages](attacks/focused_results.json), [attack HTTP](attacks/new_leaks_http.json), [independent HTTP](root_checks/independent_m12_http.json), [lifecycle](root_checks/independent_m12_lifecycle.json).

UI checks execute the actual page JavaScript in a Node VM with controlled DOM/fetch stubs. They prove exercised markup and callback/state behavior, not browser paint or browser-executed XSS. HTTP tests exercise unmodified `src/app.py` or its real handler with isolated in-memory fixtures. No audit used port 8765. No model was called. Findings below use repository aliases, predicates, stored data and refused controls; no external pharmacology assumption is required.

## M12-B1 — P1: a chelator-bearing stored tracer alias escapes every refusal

Exact request: `POST /api/explore` with `{"text":"[89Z.r]-DFO-daratumumab"}`.

**Actual:** HTTP 200, centre **DARATUMUMAB / CHEMBL1743007**, matched alias **`89zr-dfo-daratumumab`**, **2 live trials**, and no Refused entity or refusal notice. Trial and sponsor QA each return **2 originator evidence rows**. `89Z_r-dfo-daratumumab` also leaks. Appending `, osimertinib` still selects DARATUMUMAB. [Independent HTTP](root_checks/independent_m12_http.json), [stage comparison](attacks/focused_results.json).

**Controls:** `89Zr-dfo-daratumumab` and `[89Zr]-DFO-daratumumab` refuse, with zero trial/sponsor evidence. Bare `daratumumab` correctly maps to CHEMBL1743007. Candidate and refused control have the **same canonical key `89zrdfodaratumumab`**, which the index associates with a single AACT synonym for DARATUMUMAB. Thus this is a normalized spelling of the repository's own refused tracer alias, not an unsupported drug guess. [Dictionary/predicate evidence](attacks/dictionary_evidence.json), [independent adjudication](db_ui/adjudication.md).

| Stage | Result for `[89Z.r]-DFO-daratumumab` |
|---|---|
| Raw resolver | `CONTAINED_ALIAS` to CHEMBL1743007; no blocked component (underscore variant: `ALIAS`) |
| Resolver veto | `{}` |
| Item linker | Drug DARATUMUMAB; no Refused |
| Whole-name shortcut | `None`; it is not overriding an existing refusal |
| Public linker | Drug DARATUMUMAB; no Refused |
| Map / QA | Originator centre; trial/sponsor evidence 2/2 |

The causal chain is reproducible in the current code:

1. Positive lookup discards punctuation and consumes the full stored alias (`src/query.py:404-417`; `src/textrules.py:339-346`).
2. `_alnum_words` instead produces `['89Z', 'r', 'DFO', 'daratumumab']` (`src/query.py:111-113`). Inside-name isotope checks only inspect one/two-word runs joined by spaces (`src/query.py:258,278-280`). Neither `89Z` nor `89Z r` passes `is_isotope_label`, although glued `89Zr` does (`src/textrules.py:289-298`).
3. The latest glued-neighbour checks inspect words **outside** the consumed alias; there are none containing the isotope (`src/query.py:264-277`).
4. The latest isotope-plus-same-drug-key rule recognizes prefix `89zr`, but requires remainder `dfodaratumumab` to be another same-drug dictionary key (`src/query.py:282-286`). It has no index entry. Bare `daratumumab` does, but the intervening `DFO` remains.
5. The item-wide and raw resolver guards do not reassemble the split element symbol (`src/query.py:125-141`; `src/textrules.py:303-313`; `src/normalize.py:740-745`). `Engine.explore` then selects the surviving positive hit (`src/app.py:87-95`).

**Required outcome:** equivalent punctuation accepted by positive lookup must preserve the refused tracer identity inside a matched stored name, including intervening chelator text. Refusal must not depend on the isotope-stripped remainder being an independently stored alias. Existing lone-name and accepted over-refusal controls should remain explicit. This audit makes no implementation change.

The exact HEAD^ query module also leaks against the same current app/rules/database. **This is an inherited hole, not a regression attributed to this commit.** Only query.py is swapped in that counterfactual; it is not a reconstructed old deployment. [Independent current/previous checks](db_ui/adjudication.md).

## Earlier reproductions — FIXED / NOT FIXED per finding

The tables below retain historical finding identities, but each disposition is supported by this round's executions. “FIXED” concerns the stated reproduction, not a proof of all spellings. The M2 attempt has no final REPORT; its partial cases are represented by the completed M2b/cumulative replays. Repeated rows reflect repeated qualifications. See also the machine-readable [59-row name matrix](names/historical_name_dispositions.json) and [23-row DB/UI matrix](db_ui/historical_db_ui_matrix.json).

'''+history
report += f'''## Cost and nonblocking findings

Historical workloads were rerun sequentially after the other CPU-heavy review jobs finished. Unrelated host activity is uncontrolled; timings are observations, not service-level guarantees or proof of global linear complexity. Query-module counterfactuals use the same current database and remaining modules. [Execution](cost/execution_isolated.json), [reuse manifest](reuse_manifest_root.json).

| Reproduction | Current observation / disposition |
|---|---|
| M5-S3 cubic scan, 250 plain tokens | **FIXED for exact old workload:** 2,224 calls per predicate / 33,880 aggregate characters versus old 31,625 / 10,479,750. [Instrumentation](cost/perf_current.json). |
| Original 999-character plain-answer timeout | **FIXED:** check HTTP 200 in **{sec(perf['slow_check_999_characters'])} s**; ordinary follower **{sec(perf['normal_after_check_timeout'])} s**. [HTTP](cost/perf_check_http.json). |
| M6/M7 repeated 2,000-piece input `';'.join(['x']*2000)` | **FIXED for exact workload:** current direct-link median **{split:.5f} s**, historical `9bd7cb4` **{splitold:.5f} s**; HTTP check **{sec(fresh['check'])} s**, queued EGFR **{sec(fresh['queued_egfr'])} s**, both 200. [Comparison](cost/fresh_cost_comparison.json), [HTTP](cost/fresh_cost_http.json). |
| M8-S1 4,097th cache entry | **FIXED:** 82/82 fill requests create 4,096 distinct pieces; first osimertinib at rollover and retry both HTTP200/CHEMBL3353410/79 trials. Original 7,511-key sweep also completes. [HTTP](cost/cache_boundary_http.json). |
| M10/M11 400 distinct drug-bearing pieces, `';'.join(f'isa x{{i:04d}}' for i in range(400))` | **NOT FIXED**, inherited cost concern: cold check **{sec(unique['cold'])} s**, queued EGFR **{sec(unique['queued_egfr'])} s**, warm check **{sec(unique['warm'])} s**. Resolver calls **400 cold / 0 warm**. [HTTP](cost/isolated_unique_cost_http.json), [instrumentation](cost/unique_piece_cost.json). |
| M11 Unicode expansion, answer `'\\ufdfa'*4000` | **NOT FIXED:** 4,000 input characters expand to 72,000 at NFKC; check **{sec(unicode['cold'])} s**, queued EGFR **{sec(unicode['queued_egfr'])} s**, warm **{sec(unicode['warm'])} s**, all 200. [HTTP](cost/isolated_unicode_cost_http.json). |
| New repeated matches in one item, `' '.join(['isa']*1000)` (3,999 characters) | Nonblocking measured overhead: direct-link three-sample median **{med('matched_same_item_3999','HEAD'):.5f} s** versus HEAD^ **{med('matched_same_item_3999','HEAD^'):.5f} s**. At 499 characters: **{med('matched_same_item_499','HEAD'):.5f} / {med('matched_same_item_499','HEAD^'):.5f} s**. No failure. [Inputs/comparison](cost/normalization_cost.json). |
| 3,999-character punctuation workload | Current / HEAD^ direct-link medians **{med('separator_3999','HEAD'):.5f} / {med('separator_3999','HEAD^'):.5f} s**. Cached ordinary osimertinib **{med('demo_osimertinib','HEAD'):.6f} / {med('demo_osimertinib','HEAD^'):.6f} s**. [Comparison](cost/normalization_cost.json). |
| Disease / ordinary concurrency | Disease: 2,774 Trials + 300 Targets, 30 per list, **18,575 bytes / 77.053 ms**. 24 requests /12 workers: all expected HTTP200 shapes, **842.766 ms** total. These ordinary samples overlap early audit work. [HTTP](root_checks/http_results.json). |

`engine.lock` serializes engine operations (`src/app.py:247-263`), so expensive legal `/api/check` answers delay maps. The 3,999/4,000-character stresses are direct-link or **answer-field** cases; `/api/explore` correctly rejects text over 500 characters. Limits precede normalization (`src/app.py:239-243,258-263`; `src/query.py:116-117,173-177`). No deadlock or invented graph value was observed.

**M12-S1 — new stored-alias over-refusal, nonblocking.** `rad001c` / `RAD001C` now refuses instead of selecting **EVEROLIMUS / CHEMBL1908360**, whereas the exact HEAD^ query module selects it. This is a stored AACT synonym. The new trailing-key rule divides `rad001c` into same-drug key `rad` and isotope-shaped `001c` (`src/query.py:282-286`; `src/textrules.py:289-298`). Raw resolver still returns ALIAS; no wrong centre is drawn. `rad`, `RAD001`, EVEROLIMUS and its ID still work. [Current/previous proof](names/new_alias_regression.json), [independent HTTP](root_checks/independent_m12_http.json).

The 7,511-key sweep has **70** previous-method positives without a current Drug, versus m11's 69; **`rad001c` is the sole additional loss**. Many existing losses are intended tracer/product refusals, so 70 is not a defect count. The explicitly accepted M5-S2, hydroxyethyl rapamycin, `Trastuzumab--vcmmae conjugate`, `9-amino-20(s)-camptothecin`, `il-6ra` and `TAK-659F` refusals remain nonblockers. [Loss-set comparison](names/new_alias_losses.json).

Supplementary attacks are recorded without inflating the blocker count: `[89Z.r]-labelled trastuzumab` leaks with 12/12 trial/sponsor rows while `[89Zr]-labelled trastuzumab` refuses; ordinary labelled-distance forms were already exercised and left unpromoted in m11. Punctuated lexical qualifiers and internal-isotope forms on **already labelled** LUTETIUM OXODOTREOTIDE LU-177 are not additional originator blocker claims. [Attack assessment](attacks/FINDINGS.md), [independent adjudication](db_ui/adjudication.md). Existing blank-submit, unsupported-name, prefixed comma-alias and failure-closed Infinity/parser limitations are retained in the historical tables.

## Standards axis

**Zero documented-standards findings.** Independent review examined `git diff bfcb83d...HEAD` and the latest query/tests patch. No repository AGENTS.md/CONTRIBUTING/coding-standard source was found. The user-supplied evidence-based, no-tracked-edit and m12-only requirements govern this audit. KOA Studio / KhOpenApi original-versus-modified-code comparison is conditional on application changes; no such changes were made. [Independent standards assessment](db_ui/FINDINGS.md).

## Spec axis

**One P1 blocker, M12-B1.** A normalized spelling of the repository's refused tracer alias maps to its originator, with every refusal stage missing it. The exact m11 repairs work, but their same-drug remainder requirement leaves chelator-bearing aliases exposed. Stored-edge, stored-value, direction, cut-notice, no-model and exercised UI safety/state checks pass. Correct relationships around a wrongly chosen centre do not satisfy the refusal guarantee. Accepted over-refusals and cost observations do not determine the verdict. [Independent specification assessment](attacks/FINDINGS.md), [adjudication](db_ui/adjudication.md).

## Integrity and reproduction

Snapshot: **7 retired nodes, 142 retired edges, zero real self-loops and zero live edges with retired endpoints**. All six live node types and all 22 existing group combinations were exercised. Self-loop/unknown-type behavior was tested with an isolated in-memory fixture. [Snapshot](db_ui/db_snapshot_facts.json), [fixture](db_ui/self_loop_unknown.json).

`Engine.ask` uses `use_llm=False` (`src/app.py:180-181`). Explore follows SELECT/read paths; mutation fixtures use memory copies. The application does not globally enforce a read-only SQLite handle, so this is an executed-path/source/hash result, not a database-permission guarantee. Final verification checks **3,731 tracked-file SHA-256 hashes**, HEAD, tracked/staged diffs, DB bytes, report links and owned-port cleanup. [Initial snapshot](integrity_before.json), [final integrity](integrity_final.json). DB SHA-256: `7341c5a7089731f67356da5a588b269d4b69e8e6c4c054acf19aa4ef2837b529`. Existing m12 brief/log files were preserved.

Run from repository root with bytecode disabled and TMP/TEMP/TMPDIR inside the corresponding m12 directory. Shared-port scripts must remain sequential; run benchmarks after other review work ends.

```text
python -B audit_evidence_claims/m12/root_checks/run_all.py
python -B audit_evidence_claims/m12/root_checks/fresh_probe.py
python -B audit_evidence_claims/m12/names/run_round9.py
python -B audit_evidence_claims/m12/names/run_additional.py
python -B audit_evidence_claims/m12/names/run_final_replays.py
python -B audit_evidence_claims/m12/db_ui/run_db.py
python -B audit_evidence_claims/m12/db_ui/run_ui.py
python -B audit_evidence_claims/m12/attacks/focused.py
python -B audit_evidence_claims/m12/attacks/http_probe.py
python -B audit_evidence_claims/m12/root_checks/independent_m12_http.py
python -B audit_evidence_claims/m12/cost/run_isolated.py
```

VERDICT: CHANGES REQUIRED
'''
(OUT/'REPORT.md').write_text(report,encoding='utf8')
print('REPORT.md',len(report),'characters')
