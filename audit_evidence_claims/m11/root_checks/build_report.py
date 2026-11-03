"""Assemble M11 from fresh results and individually rechecked historical tables."""
from pathlib import Path
import json,re
OUT=Path(__file__).resolve().parent.parent
ROOT=OUT.parents[1]
previous=(ROOT/'audit_evidence_claims/m10/REPORT.md').read_text(encoding='utf8')
tables=previous[previous.index('## Earlier findings'):previous.index('## Cost, nonblocking')]
tables=tables.replace('Round 10 disposition','Round 11 disposition')
tables=tables.replace('64 identical / 1,560 metadata-only / 24 semantic differences / 0 errors',
                      '68 identical / 1,556 metadata-only / 24 semantic differences / 0 errors')
tables=tables.replace('M10-B3 is a different whitespace/punctuation-token hole.',
                      'The distinct M10-B3 whitespace/punctuation-token reproduction is also fixed; see M10 below.')
# Application/UI locations did not change. Replace earlier query locations with current ranges.
tables=tables.replace('src/query.py:214-219','src/query.py:217-222')
tables=tables.replace('`248-255`','`249-265`').replace('src/query.py:248-255','src/query.py:249-265')
tables=tables.replace('src/query.py:125-138','src/query.py:125-141')
tables=tables.replace('src/query.py:197-205','src/query.py:200-208')
tables=tables.replace('src/query.py:337-339','src/query.py:348-350')
tables=tables.replace('src/query.py:206-219,248-252','src/query.py:209-222,252-265')
tables=tables.replace('src/query.py:266-271','src/query.py:277-282')
tables=tables.replace('src/query.py:125-138,238-247','src/query.py:125-141,241-265')
tables=tables.replace('src/query.py:238-247','src/query.py:241-265')
header='''# Independent relation-map review — round 11

Reviewed **`2b9fc923f7b6f388f5babd2f998ed4c6e16d3439`** on 2026-11-03 KST. **Changes required:** all exact previously reported originator-blocking reproductions, including M10-B1–B4, are fixed, but two additional normalization holes still draw an originator for a qualified product/tracer. Both occur in the immediate predecessor query module too; they are inherited holes, not regressions attributed to this commit.

No tracked file was edited. New scripts, fixtures, logs and this report are confined to `audit_evidence_claims/m11/`. The specified M5-S2, hydroxyethyl rapamycin and `Trastuzumab--vcmmae conjugate` over-refusals are not blockers.

## Verification and limits

- **338 passed in 30.18 s**, exit 0, with `python -m pytest tests -q -p no:cacheprovider`. Bytecode is disabled and temporary paths are under m11. [Test output](root_checks/pytest.txt), [command/environment/hashes](root_checks/pytest_summary.json).
- Reused the six historical root HTTP runners, four M6 runners, M8/M9 confirmations, and both M10 confirmations. All exit 0; port-sharing runners ran sequentially. M10's exact confirmation scripts issued **57 + 38 actual HTTP requests**. [Source manifest](root_checks/reuse_manifest.json), [six runners](root_checks/execution_http.json), [remaining runners](root_checks/execution_remaining.json), [M6](root_checks/execution_m6_http.json), [M8/M9](root_checks/execution_extra.json).
- Naming replays cover the original M1 scripts, 7,511-key alias sweep, frozen 1,648-question counterfactual and cumulative M2b–M10 matrices. Per-finding dispositions and execution manifests are linked below. The frozen counterfactual now yields **68 identical / 1,556 metadata-only / 24 semantic differences / zero errors**. This diagnostic compares the current linker with a controlled no-relink counterfactual, not application versions. [Naming report](names/FINDINGS.md), [manifest](names/reuse_manifest.json), [counterfactual](names/adapted_frozen_qa_relink_sweep.json).
- Independent graph oracle: **6,469 live centres, 22 relation/direction/type/role combinations, zero errors**. **19/19 DB and 24/24 UI assertions** pass. An additional in-memory real-handler self-loop/unknown-type/retirement fixture passes **4/4** checks. [DB/UI report](db_ui/FINDINGS.md), [oracle](db_ui/db_validate.json), [DB](db_ui/db_assertions.json), [UI](db_ui/ui_assertions.json), [new fixture](db_ui/self_loop_unknown.json).
- All **36 page demos plus six map callbacks** pass. All 36 complete demo responses equal m7, m8, m9 and m10; all 36 original-CLI HTTP requests return 200 and equal Engine responses. The seven original QA evidence counts remain **12, 12, 11, 1, 12, 0, 0**. [Comparison](db_ui/demo_previous_comparison.json), [HTTP](db_ui/demo_http.json).
- Root independently confirmed the new failures through **60 HTTP responses** from the unmodified `src/app.py` CLI, including refusal controls and trial/sponsor questions. All returned 200; the served page matched `web/try.html`; the owned server closed. [Responses](root_checks/new_leaks_http.json), [lifecycle](root_checks/new_leaks_lifecycle.json), [independent stage probe](root_checks/fresh_probe.json).

UI tests execute actual page JavaScript in a Node VM with controlled DOM/fetch stubs. They establish generated markup and callback/state behavior, not browser paint or browser-executed XSS. HTTP tests exercise the actual server. No audit server used port 8765. Findings use the repository's own canonical keys, stored aliases and refused controls, without external pharmacology assumptions.

## Blocking findings

### M11-B1 — P1: a separator inside the isotope's element symbol defeats every guard

Exact request: `POST /api/explore` with `{"text":"[89Z.r] trastuzumab"}`.

**Actual:** HTTP 200, centre **TRASTUZUMAB / CHEMBL1201585**, **13 trials**, matched stored alias **`89zr-trastuzumab`**, no Refused entity or refusal notice. Trial and sponsor QA each return **12 originator evidence rows**. `89Z_r trastuzumab` and `trastuzumab [89Z.r]` also draw the same originator. Adding `, osimertinib` still selects the forbidden trastuzumab centre. [Independent HTTP](root_checks/new_leaks_http.json), [stages and exact predecessor comparison](attacks/key_equivalence_results.json).

| Stage | Result for `[89Z.r] trastuzumab` |
|---|---|
| Raw resolver | EXACT → CHEMBL1201585, `extract_parenthetical`; no blocked component |
| Resolver veto | `{}` |
| Item linker / public linker | Drug TRASTUZUMAB; no Refused |
| Whole-name shortcut | `None`; it does not override a refusal |
| Map | Originator and its stored live relationships |

**Evidence for equivalence:** `canonical_key('[89Z.r] trastuzumab')` equals the stored `89zr-trastuzumab` key. The positive matcher consumes that alias. The controls `[89Zr] trastuzumab`, `[89.Zr] trastuzumab` and `89 Zr trastuzumab` refuse. This is the same dictionary-recognized tracer alias with punctuation inside the element symbol, not an invented drug identity.

**Cause:** `_alnum_words` makes `['89Z', 'r']` (`src/query.py:110-112`). `_marked` passes their space-joined forms to `is_isotope_label` (`src/query.py:249-265`), whose regex permits separation between the mass and element, but not inside `Zr` (`src/textrules.py:289-298`). Neither `89Z` nor `89Z r` passes; `Z` alone is not in the element set. `_qualified`'s normalization variants also miss (`src/query.py:125-141`), while positive lookup erases the separator and matches `89zrtrastuzumab` (`src/query.py:383-405`). The final map trusts the surviving positive hit (`src/app.py:87-95`).

**Required outcome:** the refusal decision must retain isotope identity across punctuation accepted by positive alias lookup, both inside a consumed alias and beside a bare drug. Preserve the existing lone-name controls. Immediate-predecessor query code also leaks this input against the same current app/rules/database; this is a query-module counterfactual, not a reconstructed old deployment. [Independent adjudication](db_ui/attack_adjudication.md).

### M11-B2 — P1: a punctuation-only token pushes a known biosimilar suffix beyond the positive window

Exact request: `POST /api/explore` with `{"text":"bevacizumab a - w w b"}`.

**Actual:** HTTP 200, centre **BEVACIZUMAB / CHEMBL1201583**, **122 trials**, no refusal. Trial and sponsor QA each return **12 originator evidence rows**. `bevacizumab - a - w - w - b` and underscore-separated variants also leak. Appending `, osimertinib` still draws bevacizumab. [Independent HTTP](root_checks/new_leaks_http.json), [current/predecessor stages](attacks/key_equivalence_results.json).

| Stage | Result for `bevacizumab a - w w b` |
|---|---|
| Raw resolver | ALIAS → CHEMBL1201583; no blocked component |
| Resolver veto | `{}` |
| Item linker / public linker | Bare BEVACIZUMAB; no Refused |
| Whole-name shortcut | `None` |
| Map | Originator with its stored live relationships |

**Evidence for equivalence:** the entire input has the same canonical key and stored alias hits as `bevacizumab-awwb`. The controls `bevacizumab-awwb`, `bevacizumab a.w.w.b` and **`bevacizumab a w w b`** refuse. Adding one standalone hyphen to the last refused input makes it pass.

**Cause:** the extra hyphen makes six raw tokens. Both drug-span detection and positive windows are limited to five (`src/query.py:374-384,446-461`), so the full suffix-bearing name is no longer matched and `_marked` receives only bare `bevacizumab`. Its same-name suffix check sees no suffix, and its next-word check sees only `a` (`src/query.py:241-265`). `_qualified` does see the whole item, including normalized `bevacizumab a w w b`, but no guard reassembles the suffix letters into the canonical `awwb` used by positive lookup (`src/query.py:125-141`). This is not a claim that the eight-word scan misses the six-token input: it scans it and still returns false.

**Required outcome:** punctuation-only tokens must not turn a recognized, refused suffix-bearing product into an accepted bare parent. Check normalized qualifier identity independently of whether the full positive window fits. Immediate-predecessor query code also leaks; do not attribute this hole to the newest commit. [Independent adjudication](db_ui/attack_adjudication.md).

'''
m10='''### M10

| Finding / exact reproduction | Round 11 result |
|---|---|
| M10-B1 trailing isotope absorbed by alias: `A33 124i`, `A33 124 i`, `A33 [124i]`, `A33 124-I`, `A33-124i` | **FIXED** — no ADAKITUG centre for qualified input; refusal, zero qualified trial/sponsor evidence. ADAKITUG preferred name remains available. [Stages](names/m10_attacks/focus_results.json), [HTTP](root_checks/candidate_http.json). |
| M10-B2 isotope stands in for substance: `18F fluorothymidine`, `18-F fluorothymidine`, `[18F] fluorothymidine`, `18F nonexistingdrug` | **FIXED** — no FDG centre or QA evidence. Lone `18F` still selects CHEMBL2030434. [HTTP](root_checks/isotope_http.json). |
| M10-B3 punctuation consumes isotope-neighbour budget: `trastuzumab 89 - Zr`, `trastuzumab [89 - Zr]`, `trastuzumab 89_Zr` | **FIXED** — refusal; normalized neighbour words checked before limiting. Separate osimertinib survives. [Stages](names/m10_attacks/focus_results.json), [HTTP](root_checks/candidate_http.json). |
| M10-B4 respelt qualifier: `generic-version of bevacizumab`, `generic_version of bevacizumab`, `albumin - bound paclitaxel`, `follow-on-biologic bevacizumab` | **FIXED** — refused, with no parent QA evidence for the reported qualified requests. [Stages](names/m10_attacks/probe_results.json), [HTTP](root_checks/candidate_http.json). |
| M10 distinct-piece lock contention | **NOT FIXED**, performance should-fix; legal cold requests can queue ordinary maps for seconds. Updated isolated observations below. |
| M10 repeated known over-refusals / blank submission / Infinity / unsupported names and prefixed comma aliases | **NOT FIXED** where individually recorded above; they are not promoted into new blockers. |

'''
footer=r'''## Cost and nonblocking findings

Historical costs were replayed with the original workloads. Final timed suites ran sequentially after the root/name/DB workers stopped CPU-intensive execution. Unrelated host activity is uncontrolled; these are observations, not service-level guarantees or proof of global linear complexity. [Cost report](cost/FINDINGS.md), [reuse manifest](cost/reuse_manifest.json), [execution](cost/execution.json).

| Reproduction | Current observation / disposition |
|---|---|
| M5-S3 cubic scan, 250 plain tokens | **FIXED**. 2,224 predicate calls per predicate and 33,880 aggregate characters, versus the old 31,625 / 10,479,750. Current 499-character linker median **0.02647 s**. [Instrumentation](cost/perf_current.json), [comparison](cost/fresh_cost_comparison.json). |
| Original 999-character answer timeout/follower request | **FIXED**. HTTP 200 in **0.20895 s**, ordinary EGFR follower **0.02173 s**. [Exact reproduction](cost/perf_check_http.json). |
| M6 split_2000 / M7-S3 repeated-piece resolver work | **FIXED**. `';'.join(['x']*2000)` linker median **0.16096 s**, versus `9bd7cb4` **2.28857 s** on the same data. HTTP check **0.49877 s**, queued EGFR **0.41989 s**, both 200. [Comparison](cost/fresh_cost_comparison.json), [HTTP](cost/fresh_cost_http.json). |
| M8-S1 natural cache rollover | **FIXED**. **82/82** fill requests 200, 4,096 distinct pieces; first osimertinib at rollover and retry both 200 / CHEMBL3353410 / 79 trials. [HTTP](cost/cache_boundary_http.json). |
| Distinct 400 drug-bearing pieces, `';'.join(f'isa x{i:04d}' for i in range(400))` | **NOT FIXED**, inherited performance should-fix. Cold `/api/check` **2.73397 s**, queued EGFR map **2.65132 s**; warm check **0.33558 s**. Resolver calls **400 cold / 0 warm**. [HTTP](cost/isolated_unique_cost_http.json), [calls](cost/unique_piece_cost.json). |
| New Unicode expansion workload, `answer='\ufdfa'*4000`, UTF-8 JSON | **NOT FIXED**, nonblocking performance concern. Valid 4,000-character answer expands to **72,000 characters** at NFKC folding. HTTP check **2.44818 s**, queued EGFR **2.36582 s**; warm check **2.81211 s**. Both checks return 200. Current direct-link median **2.67598 s**, HEAD^ **2.34056 s**: the expensive path already existed. [HTTP](cost/isolated_unicode_cost_http.json), [comparison](cost/normalization_cost.json). |
| Added separator normalization cost, 3,999-character punctuation workload | Three-sample direct-link median **0.42502 s**, HEAD^ **0.22475 s**. This shows measurable overhead on this synthetic case; normal cached osimertinib lookup remains about **0.00009 s** in both. [Exact inputs and measurements](cost/normalization_cost.json). |
| Disease and ordinary concurrent requests | Disease: **2,774 Trials + 300 Targets**, 30 per list, **18,575 bytes / 67.137 ms**. Historical 24-request / 12-worker workload: all expected 200 shapes, **757.866 ms** total. These ordinary measurements overlap initial audit work, not the isolated timing window. [HTTP](root_checks/http_results.json). |

The shared `engine.lock` covers these operations (`src/app.py:247-263`), so expensive legal `/api/check` requests still delay unrelated maps. The Unicode stress uses the **answer** field, whose limit is 4,000; it is not a 4,000-character `/api/explore` text claim (that endpoint correctly rejects text over 500 characters). Limits are applied before normalization (`src/app.py:239-243,258-263`; `src/query.py:116-117,173-177`). No deadlock or invented graph value was observed.

**M11-S1 — additional stored-alias over-refusals, nonblocking.** The broader sweep has **69** prior-method positives without a current Drug, **37 more** than m10's loss set. Many additions are intended labelled-product refusals, including repaired `A33 124i`; these counts are not counts of defects. Additional apparently unlabelled stored aliases now refused include `9-amino-20(s)-camptothecin`, `il-6ra` (TOCILIZUMAB) and `TAK-659F` (MIVAVOTINIB). The isotope parser interprets substrings `20 s`, `6ra`, or `659F` as labels. No wrong centre is drawn, so these are should-fix lookup losses, not approval blockers. [Exact loss set](names/new_alias_losses.json), [name assessment](names/FINDINGS.md).

The explicitly accepted M5-S2 and three M9-S1 over-refusals remain separately NOT FIXED in the historical tables. Other unchanged qualifications—blank submission, controlled Infinity/parser errors, unsupported lowercase IDs/investigator labels, prefixed comma-name QA and nonparenthetical listing policy—are also retained individually. No new demo regression was established.

## Standards axis

**Zero documented-standards findings.** The separate reviewer examined original-to-current application changes and the latest query/tests change. No repository AGENTS.md, CONTRIBUTING or coding-standards source was found. The user-supplied audit-only and evidence-based instructions govern. No tracked file was changed; the KOA Studio / KhOpenApi original-versus-modified-code requirement is conditional on code changes and does not apply to this no-edit audit. [Independent standards review](db_ui/FINDINGS.md#standards-axis).

## Spec axis

**Two P1 blocking families, M11-B1 and M11-B2.** Both reach an originator centre with no refusal at any stage; existing exact cases are repaired but equivalent punctuated qualifications still fail. The no-model, stored-edge, stored-value, direction, cut-notice and exercised markup/state checks pass. That does not make a wrongly chosen centre correct. The two blockers alone determine the verdict; accepted over-refusals and performance observations do not. [Specification assessment](attacks/FINDINGS.md), [independent adjudication](db_ui/attack_adjudication.md).

## Integrity and reproduction

Snapshot facts: **7 retired nodes, 142 retired edges, zero real self-loops and zero live edges with retired endpoints**. All six live node types and all 22 existing group combinations were exercised. The new self-loop behavior is established by an in-memory fixture, not claimed as real snapshot data. [Snapshot](db_ui/db_snapshot_facts.json), [fixture](db_ui/self_loop_unknown.json).

`Engine.ask` explicitly passes `use_llm=False` (`src/app.py:180-181`). No model was called. Mutating fixtures use in-memory copies; before/after hashes establish that application data were unchanged. The application does not globally enforce a read-only SQLite handle, so this is an executed-path/integrity result, not a database-permission guarantee.

Final verification compares **3,348 tracked-file SHA-256 hashes**, HEAD, tracked/staged diffs, database bytes, report links and owned-port cleanup in [integrity_final.json](integrity_final.json). Database SHA-256: **`7341c5a7089731f67356da5a588b269d4b69e8e6c4c054acf19aa4ef2837b529`**. Existing m11 brief/log files were preserved. All new scratch artifacts are under m11.

Run from repository root with bytecode disabled and TMP/TEMP/TMPDIR under the corresponding m11 subdirectory. Port-sharing scripts must remain sequential; worker manifests record adapted paths and baseline semantics.

```text
python -B audit_evidence_claims/m11/root_checks/run_replays.py tests
python -B audit_evidence_claims/m11/root_checks/run_replays.py http
python -B audit_evidence_claims/m11/root_checks/run_remaining.py
python -B audit_evidence_claims/m11/names/run_round9.py
python -B audit_evidence_claims/m11/names/run_final_replays.py
python -B audit_evidence_claims/m11/names/m10_attacks/probe.py
python -B audit_evidence_claims/m11/names/m10_attacks/focus.py
python -B audit_evidence_claims/m11/db_ui/run_db.py
python -B audit_evidence_claims/m11/db_ui/run_ui.py
python -B audit_evidence_claims/m11/attacks/key_equivalence.py
python -B audit_evidence_claims/m11/root_checks/new_leaks_http.py
```

VERDICT: CHANGES REQUIRED
'''
report=header+tables+m10+footer
report=report.replace('src/query.py:110-112','src/query.py:111-113')
report=report.replace('src/query.py:374-384,446-461','src/query.py:378-397,446-463')
report=report.replace("`answer='\\\\ufdfa'*4000`", "`answer='\\ufdfa'*4000`")
(OUT/'REPORT.md').write_text(report,encoding='utf8')
print('REPORT.md written',len(report))
