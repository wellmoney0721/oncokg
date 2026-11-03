"""Assemble round 17 from current evidence, without changing tracked files."""
from pathlib import Path
import json, posixpath, re

OUT = Path(__file__).resolve().parent
def read(rel):
    return (OUT/rel).read_text(encoding='utf8')
def data(rel):
    return json.loads(read(rel))
def links(text, prefix):
    return re.sub(r'\]\(([^)]+)\)', lambda m: ']('+(
        m.group(1) if re.match(r'https?://',m.group(1)) else
        posixpath.normpath(prefix+'/'+m.group(1)))+')',text)
def section(text, start, end):
    return text.split(start,1)[1].split(end,1)[0].strip()

head=data('integrity_before.json')['head']
assert data('root_checks/pytest_summary.json')['exit_code']==0
assert '344 passed' in read('root_checks/pytest.txt')
assert all(r['exit_code']==0 for r in data('root_checks/execution_all.json'))
assert all(r['exit_code']==0 for r in data('root_checks/execution_late.json'))
assert data('db_ui/db_validate.json')['errors']==[]
assert data('db_ui/db_assertions.json')['passed']==19
assert data('db_ui/ui_assertions.json')['passed']==24
assert data('root_checks/independent_m17_lifecycle.json')['requests']==68
assert data('root_checks/independent_m17_lifecycle.json')['all_200']
assert data('root_checks/independent_m16_lifecycle.json')['requests']==76
assert data('root_checks/independent_m16_lifecycle.json')['all_200']
assert data('attacks/alias_variants_comparison.json')['changes']==[]
names=read('names/FINDINGS.md')
dbui=read('db_ui/FINDINGS.md')
attacks=read('attacks/FINDINGS.md')

intro=f'''# Independent relation-map review — round 17

Reviewed **`{head}`**. **CHANGES REQUIRED: one new P1 originator-refusal bypass.** `trastuzumab labelled-I-124` passes every refusal stage and draws unlabelled TRASTUZUMAB with its clinical-trial evidence. The corresponding `labelled-124I` form refuses. The gap also exists in HEAD^: this is a newly reproduced inherited defect, not a demonstrated latest-patch regression.

All exact previously promoted M1–M16 name blockers are **FIXED**, including M16-B1 `I-124-labelled trastuzumab`. **M16-S1's repeated isotope computation is FIXED**: the helper now performs one whole-item scan rather than one scan per matched occurrence. Historical unresolved supplemental, availability, UI, documentation and residual cost observations retain their individual NOT FIXED dispositions below. The explicitly accepted over-refusals and ChEMBL bevacizumab-code limitation do not determine this verdict.

All new scratch files are under `audit_evidence_claims/m17/`. No application source or tracked file was edited.

## Verification and scope

- **344 passed in 34.25 s**, exit 0: `python -m pytest tests -q -p no:cacheprovider`. Bytecode disabled and temporary paths confined to m17. [Output](root_checks/pytest.txt), [execution/hashes](root_checks/pytest_summary.json).
- Cumulative original-script replays cover m1, partial m2/completed m2b, m3–m16. The root's main and late batches exit zero. Exact m16 independent HTTP covers **19 cases / 76 requests**; the new root confirmation covers **17 cases / 68 requests**. [Manifest](reuse_manifest_root.json), [main](root_checks/execution_all.json), [remaining](root_checks/execution_remaining.json), [late](root_checks/execution_late.json), [old HTTP](root_checks/independent_m16_http.json), [new HTTP](root_checks/independent_m17_http.json).
- Raw **7,511-key** alias sweep has **zero new losses versus m16**. Adapted frozen **1,648-question** comparison remains **68 identical / 1,556 metadata-only / 24 semantic / zero errors**. [Name report](names/FINDINGS.md), [worker checks](names/worker_final_checks.json), [raw differences](names/new_alias_losses.json), [counterfactual](names/adapted_frozen_qa_relink_sweep.json).
- Stored-row oracle: **6,469 live centres / 22 relation-direction-type-role combinations / zero errors**. **19/19 DB**, **24/24 UI**, and **4/4 self-loop/unknown-type/retirement** assertions pass. [Oracle](db_ui/db_validate.json), [DB](db_ui/db_assertions.json), [UI](db_ui/ui_assertions.json), [fixture](db_ui/self_loop_unknown.json).
- **36/36 demos** exactly match all m7–m16 full-response baselines; **36/36 CLI HTTP demos** return 200 and match Engine responses. Six map callbacks pass; seven original QA evidence counts remain **12, 12, 11, 1, 12, 0, 0**. [Baselines](db_ui/demo_previous_comparison.json), [HTTP](db_ui/demo_http.json), [callbacks](db_ui/ui_m3_checks.json).
- Attack worker reran **168 historical staged cases**, plus **63 new current/HEAD^ pairs**, and **420 HTTP requests**, all 200. A separate reviewer records **36 current/HEAD^ paired stage cases**, including all 17 original m16 independent adjudication inputs. **428 transformed variants / 104 stored keys** have no centre/refusal changes from m16. [Attack checks](attacks/final_checks.json), [independent stages](db_ui/adjudication_tracer.json), [alias comparison](attacks/alias_variants_comparison.json).

UI checks execute actual page JavaScript in a Node VM with controlled DOM/fetch stubs: they verify generated markup and callbacks/state, not browser painting or browser-executed XSS. HTTP uses unmodified `src/app.py` on owned ports other than 8765, or its actual handler with in-memory fixtures. Counterfactuals replace only the stated query code against current remaining modules/data; they are not full historical deployments. No model was called. Scientific sources establish the primary iodine-124/trastuzumab identity; synthetic corroborating spellings are not claimed to be marketed products.

'''

attack_section='## M17-B1 — P1: punctuation before a one-letter isotope loses its boundary\n\n'+links(
    section(attacks,'## M17-B1 — P1: punctuation before an element-first one-letter isotope is lost before its boundary check','## Historical reproductions and controls'),'attacks')+'\n\n'
root_confirm='''## Independent HTTP confirmation

The root independently started the unmodified CLI server, verified the served page bytes, and made 68 requests across resolve, explore and trial/sponsor QA. `trastuzumab labelled-I-124`, `iodine-I-124 trastuzumab`, and `trastuzumab labelled-with-I124` draw CHEMBL1201585 without refusal. Their mass-first or whitespace-separated isotope controls refuse. `vinblastine tritium-H-3` similarly draws CHEMBL159, while `vinblastine tritium-3H` refuses. Separate-list reversals show that the tracer remains an accepted Drug even when OSIMERTINIB is selected first. BKM120, AZD9291 and `osimertinib 80 mg` remain available. [Requests and complete responses](root_checks/independent_m17_http.json), [server lifecycle](root_checks/independent_m17_lifecycle.json), [source adaptation](root_checks/independent_m17_manifest.json).

The separate DB/UI reviewer independently traces the same lost boundary in `iodine-I-124-labelled trastuzumab` and `trastuzumab labelled with iodine-I-124`. Both current and HEAD^ produce 13 map trials and 12/12 QA evidence. This corroborates the primary finding; it is not counted as another blocker. [Adjudication](db_ui/adjudication.md), [stage captures](db_ui/adjudication_tracer.json).

'''
historical='''## Earlier reproductions — FIXED / NOT FIXED per finding

Status describes the exact previous reproduction, not every possible spelling. A passing script exit alone does not establish a repair. M2 has no completed report; its partial cases and completed M2b work are included. [Report inventory](historical_report_inventory.json). Recorded nonblocking limitations and accepted exceptions remain visible.

### Name resolution, m1–m16

'''+links(section(names,'## Individual historical dispositions','## Interpretation and limits'),'names')+'\n\n'
historical+='### Database, UI, server and wording\n\n'+links(section(dbui,'## Historical findings: individual dispositions','## Standards and independent specification assessment'),'db_ui')+'\n\n'
supplemental='''## Regressions and supplemental observations

No new demo regression, live-edge defect, wrong relation direction, stored-value mismatch, or demonstrated script injection was reproduced. Raw stored-alias outcomes are unchanged from m16. The transformed-alias scan retains the two fully collapsed systematic SIROLIMUS alias over-refusals: **NOT FIXED**, availability-only. The literal stored alias remains available. [428-variant comparison](attacks/alias_variants_comparison.json), [exact variant inputs/results](attacks/alias_variants.json).

The inherited already-labelled-product discrepancy remains **NOT FIXED**: `89ZrDFO 18-FDG` refuses, while `89-ZrDFO 18-FDG` draws FLUDEOXYGLUCOSE F 18. The current brief allows labelled products, so this remains a consistency/specification clarification rather than an unlabelled-originator blocker. Cross-word one-letter exploratory forms remain outside the stated within-word requirement. [Full original-case replay and adjudication](db_ui/adjudication.md).

The user-accepted M5-S2, rapamycin locant aliases, `Trastuzumab--vcmmae conjugate`, `9-amino-20(s)-camptothecin`, `il-6ra`, `TAK-659F`, `GS-11CAL-101`, `3en3hg4wsw`, same-list-item over-refusal, and ChEMBL bevacizumab development-code limitation do not determine the verdict. Other old supplemental gaps remain explicitly NOT FIXED in the naming table. The new M17-B1 independently fails the approval bar.

'''
standards='## Standards\n\n'+links(read('db_ui/STANDARDS.md').split('\n',1)[1].strip(),'db_ui')+'\n\n'
spec='## Specification\n\n'+links(read('attacks/SPEC_REVIEW.md').strip(),'attacks')+'\n\n'
end='''## Integrity and reproduction

`Engine.ask` passes `use_llm=False` (`src/app.py:181`). Mutation fixtures use in-memory copies. The application's SQLite connection is not globally read-only; no-write conclusions rely on the inspected/executed paths and before/after hashes. Final verification compares **6,119 tracked-file SHA-256 hashes**, unchanged HEAD, clean tracked/staged diffs, unchanged database bytes, report links, and closed owned ports. [Initial snapshot](integrity_before.json), [final verification](integrity_final.json). DB SHA-256: `7341c5a7089731f67356da5a588b269d4b69e8e6c4c054acf19aa4ef2837b529`.

Run from repository root with bytecode disabled and temporary paths inside each m17 family's `tmp/`. Shared-port suites must run sequentially; cost must run after other workloads. The manifests retain original/adapted hashes and path/port changes. The name worker caught an accidental scratch-only port substitution inside the `DX-8951F` control, restored the original input, and reran the affected probe; final dispositions use corrected outputs. [Literal-preservation audit](names/adaptation_literal_check.json).

```text
python -B audit_evidence_claims/m17/root_checks/run_all.py
python -B audit_evidence_claims/m17/root_checks/run_late.py
python -B audit_evidence_claims/m17/root_checks/independent_m16_http.py
python -B audit_evidence_claims/m17/root_checks/independent_m17_http.py
python -B audit_evidence_claims/m17/names/run_round9.py
python -B audit_evidence_claims/m17/names/run_additional.py
python -B audit_evidence_claims/m17/names/run_completion.py
python -B audit_evidence_claims/m17/db_ui/run_db.py
python -B audit_evidence_claims/m17/db_ui/run_ui.py
python -B audit_evidence_claims/m17/db_ui/run_final.py
python -B audit_evidence_claims/m17/attacks/new_probe.py
python -B audit_evidence_claims/m17/attacks/new_http.py
python -B audit_evidence_claims/m17/cost/run_isolated.py
python -B audit_evidence_claims/m17/cost/repeated_match_followup.py
python -B audit_evidence_claims/m17/build_cost_section.py
python -B audit_evidence_claims/m17/build_report.py
python -B audit_evidence_claims/m17/finalize_integrity.py
```

Standards: **0 documented violations**. Specification: **one new P1 family**, sufficient to reject approval.

VERDICT: CHANGES REQUIRED
'''
(OUT/'REPORT.md').write_text(intro+attack_section+root_confirm+historical+supplemental+read('cost_section.md')+'\n'+standards+spec+end,encoding='utf8')
print('REPORT.md assembled from fresh evidence.')
