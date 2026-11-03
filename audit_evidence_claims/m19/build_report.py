"""Assemble the final independent audit from fresh, inspectable evidence."""
from pathlib import Path
import json,posixpath,re
OUT=Path(__file__).resolve().parent
def read(p): return (OUT/p).read_text(encoding='utf8')
def data(p): return json.loads(read(p))
def links(text,prefix):
    def replace(m):
        target=m.group(1)
        if re.match(r'https?://|#',target): return m.group(0)
        return ']('+posixpath.normpath(prefix+'/'+target)+')'
    return re.sub(r'\]\(([^)]+)\)',replace,text)
assert data('root_checks/pytest_summary.json')['exit_code']==0
assert data('root_checks/independent_m19_summary.json')['assertions_passed']
assert all(x['exit_code']==0 for x in data('root_checks/execution_all.json'))
assert all(x['exit_code']==0 for x in data('root_checks/execution_m18_late.json'))
before=data('integrity_before.json')
attacks=read('attacks/FINDINGS.md')
new=attacks.split('## M19-B1',1)[1].split('## Specification review',1)[0]
spec=attacks.split('## Specification review (under 400 words)',1)[1].split('## Evidence and reproducibility',1)[0]
names=read('names/historical_table.md')
db=read('db_ui/FINDINGS.md')
db='## Database, UI and server reproductions\n\n'+db.split('## Historical findings: individual dispositions',1)[1].split('## Standards',1)[0].strip()+'\n'
db=re.sub(r'(?<=\|)\n\n(?=\|)', '\n',db)
db=db.replace('unchanged nonblocking discrepancy under the explicitly permitted labelled-product exception','unchanged isotope-compatibility diagnostic around the preferred-name exception; not added to the user-accepted exceptions')
db=db.replace('unchanged previously excluded cross-word diagnostic','unchanged cross-word diagnostic; not a user-accepted exception')
standards=read('db_ui/STANDARDS.md').split('\n',1)[1]
fixed=len(re.findall(r'\| \*\*FIXED\*\* \|',names))
not_fixed=len(re.findall(r'\| \*\*NOT FIXED\*\* \|',names))
intro=f'''# Independent relation-map review — round 19

Reviewed **`{before['head']}`**. **CHANGES REQUIRED: two P1 originator-refusal failures.** `radio-labelled trastuzumab` and `trastuzumab labelled with 99m-technetium` pass every refusal stage and draw unlabelled TRASTUZUMAB. Both show 13 map trials; trial/sponsor QA each returns 12 originator evidence rows. Their joined-label / element-first controls refuse. Both holes reproduce in HEAD^; they are not claimed as originator regressions introduced by this commit.

Exact prior promoted M1–M18 primary name findings are FIXED, including M18-B1 `trastuzumab radiolabelled with iodine-124`. Historical supplemental gaps and accepted exceptions retain individual NOT FIXED dispositions below. The user-listed over-refusals and ChEMBL bevacizumab-code limitation do not determine the verdict. New `non-radiolabelled trastuzumab` over-refusal is separately reported as a should-fix.

No production code or tracked file was edited. New scratch files are confined to `audit_evidence_claims/m19/`.

## Method, evidence, and limits

The review tests four claims separately: prior exact failures stay repaired; equivalent tracer descriptions never select an unlabelled molecule; displayed edges/values agree with live stored rows; request cost remains bounded. Paired inputs change only the relevant spelling, direct helper traces identify the missed guard, and independently owned original CLI servers establish the public response. A passing test suite alone is not treated as proof of the refusal guarantee.

- **346 passed in 36.74 s**, exit 0, using `python -m pytest tests -q -p no:cacheprovider`. Bytecode disabled and temp paths under m19. [Output](root_checks/pytest.txt), [command/environment](root_checks/pytest_summary.json).
- Cumulative historical scripts re-executed on current HEAD: m1, partial m2/completed m2b, m3–m18. Main/remaining/late root batches exit zero. [Reuse manifest](reuse_manifest_root.json), [main execution](root_checks/execution_all.json), [remaining](root_checks/execution_remaining.json), [late](root_checks/execution_m18_late.json), [M18 independent HTTP](root_checks/independent_m18_http.json). The name and DB/UI matrices below give exact per-finding dispositions and fresh artifacts rather than inferring repair from process exit codes.
- Historical naming: **83 rows, 63 FIXED / 20 NOT FIXED**; **66 scripts reused / 55 reused leaf scripts executed**, plus 15 frozen M18 supplement inputs whose original standalone generator was absent. The **7,511-key** sweep has zero new losses/recoveries versus m18. The frozen **1,648-question** comparison has 68 identical / 1,556 metadata-only / 24 semantic differences / zero errors. These frozen-comparison differences are diagnostics, not defect counts. [Coverage/assertions](names/worker_final_checks.json), [reuse/literal manifest](names/reuse_manifest.json), [QA comparison](names/adapted_frozen_qa_relink_sweep.json). DB/UI contributes 30 overlapping rows (23 FIXED / 7 NOT FIXED); matrix row counts are not unique defect counts.
- **6,469 live centres / 22 relation-direction-type-role combinations / zero oracle errors**; **19/19 DB**, **24/24 UI**, **4/4 self-loop/unknown/retirement** assertions pass. [Stored-row oracle](db_ui/db_validate.json), [DB assertions](db_ui/db_assertions.json), [UI assertions](db_ui/ui_assertions.json), [fixture](db_ui/self_loop_unknown.json).
- **36/36 original CLI HTTP demos** return 200 and equal direct Engine responses. All 36 page demos render in the JavaScript harness. [HTTP demos](db_ui/demo_http.json), [demo comparisons](db_ui/demo_previous_comparison.json), [page callback checks](db_ui/ui_m3_checks.json).
- Attack reviewer: **82 current/HEAD^ stage pairs / 328 actual HTTP requests**, all 200. Root separately confirmed **22 inputs / 88 requests**, including the two holes, paired refusals, list reversal, ordinary controls and older unresolved qualifiers. Counts overlap and are not summed as unique examples. [Stages](attacks/new_results.json), [HTTP](attacks/new_http.json), [root HTTP](root_checks/independent_m19_http.json), [root assertions](root_checks/independent_m19_summary.json).
- All 22 root map responses were exercised through the actual page form callback. The two leaks render a TRASTUZUMAB SVG centre and CHEMBL1201585 trail; their controls render refusal with no SVG and an empty trail. [Page evidence](db_ui/ui_m19_http.json), [harness](db_ui/ui_m19_http.js).

UI checks execute actual page JavaScript in a Node VM with controlled DOM/fetch stubs. They establish generated markup, state and callbacks, not browser painting or browser-executed XSS. HTTP uses unmodified `src/app.py` on owned ports other than 8765, or its real handler with in-memory fixtures. Historical counterfactuals substitute only `query.py` against current remaining modules/data; they are not complete historical deployments. No model was called. Performance samples are host measurements, not service guarantees.

## M19-B1'''
historical='''## Earlier name reproductions — FIXED / NOT FIXED

Each status applies to the exact cited reproduction, not every imaginable spelling. M2 has no completed report; its partial fixtures are covered with m2b. The table includes earlier unpromoted supplements. Inherited unresolved leaks such as `b.i.o.similar bevacizumab` and `lip.osomal doxorubicin` are not in the user's accepted-exception list and are not excused as repaired; the root independently reproduced both over HTTP this round. They add to the reasons approval is unavailable, while B1/B2 provide new independent failures.

'''
exceptions='''
### Accepted exceptions

The following remain explicitly outside blockers as the user requested: M5-S2; 40-o-/42-o-(2-hydroxyethyl)rapamycin; Trastuzumab--vcmmae conjugate; 9-amino-20(s)-camptothecin; il-6ra; TAK-659F; GS-11CAL-101; 3en3hg4wsw; same-list-item over-refusal. ChEMBL's bevacizumab biosimilar-code synonyms are the separately accepted data limitation. Other unresolved historical entries are not silently added to this exception list. [Name replay narrative and coverage](names/FINDINGS.md).

'''
integrity=f'''## Integrity and reproducibility

The original brief/log already existed in m19 and were preserved. Reproducer copies retain historical inputs and fixture logic, with output paths/ports recorded in manifests. Production DB mutation fixtures are isolated in memory. The application connection is not globally read-only, so the no-write conclusion relies on the inspected executed paths and final byte comparison; `Engine.ask` passes `use_llm=False` at `src/app.py:181`.

Final verification compares **{len(before['tracked_sha256']):,} tracked-file SHA-256 hashes**, unchanged HEAD, tracked/staged diffs, database bytes, local report links and closure of the run's owned server ports. [Before](integrity_before.json), [final verification](integrity_final.json). Database SHA-256: `{before['db_sha256']}`. No application repair was made; the conditional KOA Studio/KhOpenApi original-versus-replacement comparison therefore does not arise.

Representative commands from repository root; historical HTTP batches are sequential and cost batches run after other audit CPU workloads:

```text
python -B audit_evidence_claims/m19/root_checks/run_all.py
python -B audit_evidence_claims/m19/root_checks/run_m18_late.py
python -B audit_evidence_claims/m19/root_checks/independent_m18_http.py
python -B audit_evidence_claims/m19/root_checks/independent_m19_http.py
python -B audit_evidence_claims/m19/names/run_round9.py
python -B audit_evidence_claims/m19/names/run_remaining.py
python -B audit_evidence_claims/m19/attacks/new_probe.py
python -B audit_evidence_claims/m19/attacks/new_http.py
python -B audit_evidence_claims/m19/cost/run_isolated.py
python -B audit_evidence_claims/m19/cost/repeated_match_followup.py
python -B audit_evidence_claims/m19/build_cost_section.py
python -B audit_evidence_claims/m19/build_report.py
python -B audit_evidence_claims/m19/finalize_integrity.py
```

Standards: **0 documented violations**. Specification: **2 new P1 findings**, both inherited holes; unresolved historical leaks remain explicitly NOT FIXED. Ordinary demo/DB checks pass, but the refusal guarantee fails.

VERDICT: CHANGES REQUIRED
'''
report=intro+links(new,'attacks')+'\n'+historical+links(names,'names')+'\n'+exceptions+links(db,'db_ui')+'\n'+read('cost_section.md')+'\n## Standards\n'+links(standards,'db_ui')+'\n## Specification\n'+links(spec,'attacks')+'\n'+integrity
(OUT/'REPORT.md').write_text(report,encoding='utf8')
print(json.dumps(dict(report_lines=len(report.splitlines()),historical_name_fixed=fixed,historical_name_not_fixed=not_fixed)))
