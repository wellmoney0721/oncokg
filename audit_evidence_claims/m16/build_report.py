"""Assemble this audit's report from fresh evidence; historical scripts are read only."""
from pathlib import Path
import ast,json,posixpath,re
OUT=Path(__file__).resolve().parent
def read(rel):return (OUT/rel).read_text(encoding='utf8')
def data(rel):return json.loads(read(rel))
def links(text,prefix):
    return re.sub(r'\]\(([^)]+)\)',lambda m: ']('+(
        m.group(1) if re.match(r'https?://',m.group(1)) else
        posixpath.normpath(prefix+'/'+m.group(1)))+')',text)
head=data('integrity_before.json')['head']
name_rows=data('names/historical_name_dispositions.json')
assert data('db_ui/db_validate.json')['errors']==[]
assert data('db_ui/db_assertions.json')['passed']==19
assert data('db_ui/ui_assertions.json')['passed']==24
assert data('root_checks/pytest_summary.json')['exit_code']==0
assert len(data('cost/execution_isolated.json'))==9
assert all(r['exit_code']==0 for r in data('cost/execution_isolated.json'))
assert all(r['exit_code']==0 for r in data('root_checks/execution_all.json'))
assert all(r['exit_code']==0 for r in data('root_checks/execution_late.json'))
norm={(r['ref'],r['name']):r for r in data('cost/normalization_cost.json')}
assert len(norm)==24 and all('median_seconds' in r for r in norm.values())
def median(ref,name):return f"{norm[ref,name]['median_seconds']:.5f}"
unique=data('cost/isolated_unique_cost_http.json')
unicode=data('cost/isolated_unicode_cost_http.json')
split={r['ref']:r['median'] for r in data('cost/fresh_cost_comparison.json') if r['kind']=='split' and r['size']==2000}
repeat=data('cost/fresh_cost_http.json')
plain=data('cost/perf_check_http.json')
http=data('root_checks/http_results.json')
perf=next(r for r in data('cost/perf_current.json') if r['kind']=='plain' and r['size']==250)
# Reuse only the previous report's cost-table template, evaluated with CURRENT measurements.
previous=(OUT.parent/'m15/build_report.py').read_text(encoding='utf8')
cost_node=next(n.value for n in ast.parse(previous).body if isinstance(n,ast.Assign)
    and any(isinstance(t,ast.Name) and t.id=='cost' for t in n.targets))
cost=eval(compile(ast.Expression(cost_node),'<m15 cost template>','eval'))
cost=cost.replace('M10-M14','M10-M15').replace('M11-M14','M11-M15').replace('M12-M14','M12-M15')
cost=cost.replace('M13/M14','M13-M15').replace('src/query.py:116-117,203-205','src/query.py:116-117,234-236')
cost=cost.replace('These inherited costs remain should-fix items and do not determine the verdict.',
    'These costs remain should-fix items and do not determine the verdict. The added repeated-match work is a latest-patch amplification, detailed below.')
repeat_http=data('cost/isolated_repeated_match_cost_http.json')
assert data('cost/repeated_match_execution.json')['exit_code']==0
cost+=f'''### M16-S1 — added repeated-match work and HTTP lock delay (should-fix)

The reused same-data workload `' '.join(['isa']*1000)` (3,999 characters) has a current/HEAD^ direct-link median of **{median('HEAD','matched_same_item_3999')} / {median('HEAD^','matched_same_item_3999')} s**, about **{norm['HEAD','matched_same_item_3999']['median_seconds']/norm['HEAD^','matched_same_item_3999']['median_seconds']:.2f}x** in these three-sample observations. Unlike the inherited baseline cost, the new item-wide isotope scan adds demonstrably quadratic work to this workload: `_marked` runs before entity deduplication (`src/query.py:534-545`), and each invocation rescans all tokens of the same item (`src/query.py:375-379`).

Bounded instrumentation counts **125 whole-item / 15,625 within-word calls** at 125 occurrences (499 characters), versus **1,000 whole-item / 1,000,000 within-word calls** at 1,000 occurrences. The helper sees **6,000,000 aggregate characters** in the latter. The output remains one ISATUXIMAB entity. This establishes the additional repeated scanning directly; the timing ratio is not claimed as a universal benchmark. [Instrumentation](cost/repeated_match_instrumentation.json), [script](cost/repeated_match_followup.py), [original paired medians](cost/normalization_cost.json).

The same 3,999-character string is legal in the **answer field**: `POST /api/check` with `text='EGFR'` and that answer returns 200 in **{repeat_http['cold']['seconds']:.5f} s**, with a concurrent EGFR map queued for **{repeat_http['queued_egfr']['seconds']:.5f} s**. A warm repeat takes **{repeat_http['warm']['seconds']:.5f} s**; the ordinary map after completion takes **{repeat_http['after']['seconds']:.5f} s**. All calls return 200, the page GET remains responsive, and the owned server closes with unchanged DB bytes. No historical HTTP timing is inferred from the direct-link comparator. [HTTP responses](cost/isolated_repeated_match_cost_http.json), [lifecycle](cost/repeated_match_cost_lifecycle.json), [adaptation/execution](cost/repeated_match_execution.json).

Compute or reuse the item's isotope state without rechecking every token for every matched occurrence, while preserving the refusal outcomes. This is a performance should-fix under the given correctness-focused approval bar; it is not needed to establish the separate P1 verdict. No repair was implemented.

'''
fixed=sum(r['status']=='FIXED' for r in name_rows)
intro=f'''# Independent relation-map review — round 16

Reviewed **`{head}`**. **CHANGES REQUIRED: one new P1 originator-refusal bypass is sufficient.** `I-124-labelled trastuzumab` passes every refusal stage and draws unlabelled TRASTUZUMAB with its clinical-trial evidence. The equivalent mass-first control refuses. This gap also exists in HEAD^; it is newly reproduced here, not demonstrated to have been introduced by the latest patch.

All exact previously promoted M1–M15 name blockers are **FIXED**, including M15-B1 `89-ZrDFO trastuzumab`, M15-B2 `3hvinblastine`, and the lower-case `A33124i` corroboration. The historical tables retain unresolved supplemental/availability/UI/cost qualifications. The explicitly accepted over-refusals and ChEMBL bevacizumab-code limitation do not determine this verdict.

All new scratch files are under `audit_evidence_claims/m16/`. No application code or tracked file was edited.

## Verification and scope

- **343 passed in 39.54 s**, exit 0: `python -m pytest tests -q -p no:cacheprovider`. Bytecode disabled and temporary paths confined to m16. [Output](root_checks/pytest.txt), [execution and hashes](root_checks/pytest_summary.json).
- Reused cumulative HTTP scripts cover m1, partial m2/completed m2b, m3–m11 and literal m12–m15 confirmations. All root batches exit zero. [Original-script provenance](reuse_manifest_root.json), [main execution](root_checks/execution_all.json), [remaining](root_checks/execution_remaining.json), [late execution](root_checks/execution_late.json).
- **58 copied historical name scripts / 49 executed leaf reproductions**. The naming table has **{len(name_rows)} dispositions: {fixed} FIXED / {len(name_rows)-fixed} NOT FIXED**; status is separate from severity. Raw **7,511-key** sweep has exactly the two user-accepted new losses, `GS-11CAL-101` and `3en3hg4wsw`. Adapted frozen **1,648-question** comparison remains **68 identical / 1,556 metadata-only / 24 semantic / zero errors**. [Name assessment](names/FINDINGS.md), [checks](names/worker_final_checks.json), [raw alias differences](names/new_alias_losses.json), [counterfactual](names/adapted_frozen_qa_relink_sweep.json).
- Stored-row oracle: **6,469 live centres / 22 relation-direction-type-role combinations / zero errors**. **19/19 DB**, **24/24 UI**, and **4/4 self-loop/unknown-type/retirement** assertions pass. [Oracle](db_ui/db_validate.json), [DB](db_ui/db_assertions.json), [UI](db_ui/ui_assertions.json), [fixture](db_ui/self_loop_unknown.json).
- **36/36 demos** exactly match every m7–m15 full-response baseline; **36/36 fresh CLI HTTP demos** return 200 and equal direct Engine responses. Six map callbacks pass. Original seven QA evidence counts remain **12, 12, 11, 1, 12, 0, 0**. [Baselines](db_ui/demo_previous_comparison.json), [HTTP](db_ui/demo_http.json), [callbacks](db_ui/ui_m3_checks.json).
- Attack worker reran **97 original m14 + 29 original m15 cases**, then **42 new current/HEAD^ stage cases and 168 HTTP requests**, all 200. Root independently confirms **19 paired cases / 76 HTTP requests**; a third reviewer independently traces the stages. [Attack execution](attacks/execution_summary.json), [new stages](attacks/new_results.json), [new HTTP](attacks/new_http.json), [root HTTP](root_checks/independent_m16_http.json), [independent adjudication](db_ui/adjudication.md).

UI checks execute the actual page JavaScript in a Node VM with controlled DOM/fetch stubs. They establish generated markup and exercised callbacks/state, not browser painting or browser-executed XSS. HTTP uses unmodified `src/app.py` on owned ports other than 8765, or its actual handler with isolated in-memory fixtures. Counterfactuals swap only stated query methods/modules against current app/data, not full historical deployments. No model was called. Medical sources below establish the promoted tracer's identity and notation; the entire isotope table was not externally certified.

## M16-B1 — P1: an element-first one-letter isotope bypasses every refusal stage

'''
attack=read('attacks/FINDINGS.md')
block=attack.split('## P1: element-first one-letter isotope spelling passes every refusal stage',1)[1].split('## Prior exact reproductions',1)[0]
block=links(block,'attacks')
block=block.replace('reversing the list selects OSIMERTINIB but leaves the tracer accepted as another drug.',
    'the separately tested `osimertinib, trastuzumab I-124` selects OSIMERTINIB but leaves the tracer accepted as another drug.')
independent='''## Independent confirmation

The root's separate CLI HTTP reproducer confirms `I-124 trastuzumab`, `I124 trastuzumab`, `trastuzumab I-124`, `trastuzumab I124`, and lower-case `i-124 trastuzumab` all select CHEMBL1201585 with no refusal. `124I trastuzumab` / `trastuzumab 124I` refuse. `H3 vinblastine` and `C11 erlotinib` similarly select unlabelled drugs, while their mass-first controls refuse. `Cu64 trastuzumab` refuses as expected for the implemented two-letter reverse form. [19-case / 76-request evidence](root_checks/independent_m16_http.json), [lifecycle](root_checks/independent_m16_lifecycle.json).

With `I-124 trastuzumab, osimertinib`, the wrong TRASTUZUMAB is selected first. Reversing the list selects OSIMERTINIB but leaves the tracer accepted as another Drug. Root also independently confirms `89-ZrDFO trastuzumab`, `3hvinblastine`, and `A33124i` now refuse. These are independent responses, not conclusions inferred from the standalone helper. The separate reviewer captures the same failed stages and old-case repairs. [Staged adjudication](db_ui/adjudication_tracer.json).

## Earlier reproductions — FIXED / NOT FIXED per finding

The tables classify exact earlier reproductions, with fresh evidence links. A fixed spelling does not prove every isotope notation is safe. M2 ended without a completed report; its partial cases and completed M2b reproductions are included. Nonblocking status is not inferred from a passing script exit code.

### Name resolution, m1–m15

'''
names=links(read('names/FINDINGS.md').split('## Individual historical dispositions',1)[1].split('## Interpretation and limits',1)[0],'names')
db='\n### Database, UI, values, wording and server\n\n'+links(read('db_ui/FINDINGS.md').split('## Historical findings: individual dispositions',1)[1].split('## Standards and specification',1)[0],'db_ui')
limits='''## Regressions, accepted limitations and should-fix observations

No new demo regression, live-edge defect, stored-value mismatch, or demonstrated script injection was found. The raw stored-alias sweep changes only the two newly accepted over-refusals. The explicitly accepted M5-S2, rapamycin locant aliases, `Trastuzumab--vcmmae conjugate`, `9-amino-20(s)-camptothecin`, `il-6ra`, `TAK-659F`, `GS-11CAL-101`, `3en3hg4wsw`, same-list-item over-refusal, and bevacizumab development-code limitation remain outside the blocker count. `osimertinib with [89Zr] trastuzumab` now refuses both as specified; a comma-separated osimertinib survives. [Fresh alias controls](names/alias_loss_controls.json), [raw sweep](names/names_m5_summary.json), [development codes](names/m14_supplement.json).

The separate **428 transformed variants / 104 stored keys** scan has five changed responses versus m15: three repaired lower-case tracer forms, and two newly refused fully collapsed systematic SIROLIMUS alias variants containing `3h`. The exact stored SIROLIMUS alias remains available. This is an additional **availability should-fix**, not an originator leak; it is distinct from the raw-alias sweep. Exact long inputs and outputs are retained in [comparison](attacks/alias_variants_comparison.json). Its accepted-variant total is not a defect count.

Already-labelled products retain an inherited normalization discrepancy: `89ZrDFO 18-FDG` refuses but `89-ZrDFO 18-FDG`, with the same canonical key, draws FLUDEOXYGLUCOSE F 18 / CHEMBL2030434 (one trial, 1/1 QA rows). `_labelled` exempts the latter from the new rule, while an earlier guard catches the former. The 14 preferred names classified as labelled all visibly carry isotope designations. This merits **consistency/specification clarification**, but is not promoted to an unlabelled-originator blocker because the brief expressly allows labelled products and the extra-isotope semantics are ambiguous. [Full staged analysis](db_ui/adjudication.md), [preferred-name scan](db_ui/labelled_preferred_names.json).

Cross-word one-letter exploratory inputs such as `18 FDFO trastuzumab` are likewise not promoted: this round expressly limits that check to within a word. The promoted `I-124-labelled trastuzumab` meets the within-word condition. README comments still say 317 tests (`README.md:565`, `README.ko.md:386`): **NOT FIXED**, documentation-only. The app descriptions immediately below remain accurate.

'''
standards='## Standards\n\n'+links(read('db_ui/STANDARDS.md').split('\n',1)[1],'db_ui')
spec='\n## Specification\n\n'+links(read('attacks/SPEC_REVIEW.md').split('\n',1)[1],'attacks')
# SPEC_REVIEW uses two plain relative filenames; retain them with explicit evidence links.
spec+='\n[Specification evidence and source references](attacks/FINDINGS.md). Standards: **0 documented violations**. Specification: **1 newly promoted P1 family**; its inherited originator leak independently requires changes.\n\n'
ending=f'''## Integrity and reproduction

`Engine.ask` explicitly passes `use_llm=False` (`src/app.py:181`). Explore follows read paths; mutation fixtures use in-memory databases. The app's SQLite handle is not globally read-only, so the no-write conclusion relies on inspected/executed paths and before/after bytes, not a permission guarantee.

Final verification compares **{len(data('integrity_before.json')['tracked_sha256']):,} tracked-file SHA-256 hashes**, unchanged HEAD, tracked/staged diffs, database bytes, local report links and owned-port closure. [Initial snapshot](integrity_before.json), [final verification](integrity_final.json). Database SHA-256: `7341c5a7089731f67356da5a588b269d4b69e8e6c4c054acf19aa4ef2837b529`.

Run from repository root with bytecode disabled and temporary paths inside each m16 family's `tmp/`. Reused shared-port suites are sequential; run cost after other CPU/HTTP work. Preparation creates new files and should not overwrite an initial snapshot. Manifests identify the original scripts and every path/port adaptation.

```text
python -B audit_evidence_claims/m16/root_checks/run_all.py
python -B audit_evidence_claims/m16/root_checks/run_late.py
python -B audit_evidence_claims/m16/root_checks/independent_m16_http.py
python -B audit_evidence_claims/m16/names/run_round9.py
python -B audit_evidence_claims/m16/names/run_additional.py
python -B audit_evidence_claims/m16/names/run_completion.py
python -B audit_evidence_claims/m16/db_ui/run_db.py
python -B audit_evidence_claims/m16/db_ui/run_ui.py
python -B audit_evidence_claims/m16/db_ui/run_final.py
python -B audit_evidence_claims/m16/attacks/new_probe.py
python -B audit_evidence_claims/m16/attacks/new_http.py
python -B audit_evidence_claims/m16/cost/run_isolated.py
python -B audit_evidence_claims/m16/cost/repeated_match_followup.py
python -B audit_evidence_claims/m16/build_report.py
python -B audit_evidence_claims/m16/finalize_integrity.py
```

VERDICT: CHANGES REQUIRED
'''
report=intro+block+independent+names+db+limits+cost+standards+spec+ending
(OUT/'REPORT.md').write_text(report,encoding='utf8')
print(json.dumps(dict(characters=len(report),name_dispositions=len(name_rows),fixed=fixed,verdict='CHANGES REQUIRED')))
