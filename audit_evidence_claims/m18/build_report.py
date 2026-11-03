"""Assemble the audit from fresh reproductions and independent reviewer evidence."""
from pathlib import Path
import json, posixpath, re

OUT=Path(__file__).resolve().parent
def read(name): return (OUT/name).read_text(encoding='utf8')
def data(name): return json.loads(read(name))
def links(text, prefix):
    def replace(m):
        target=m.group(1)
        if re.match(r'https?://|#',target): return m.group(0)
        return ']('+posixpath.normpath(prefix+'/'+target)+')'
    return re.sub(r'\]\(([^)]+)\)',replace,text)

assert data('root_checks/pytest_summary.json')['exit_code']==0
assert data('root_checks/independent_m18_summary.json')['assertions_passed']
assert all(x['exit_code']==0 for x in data('root_checks/execution_all.json'))
assert all(x['exit_code']==0 for x in data('root_checks/execution_m18_late.json'))
before=data('integrity_before.json')
attack=read('attacks/FINDINGS.md')
primary=attack.split('## M18-B1',1)[1].split('## Earlier attack reproductions',1)[0]
primary=primary.replace('notation and clinical product distinction','notation and isotope/product distinction')
spec=attack.split('## Specification review',1)[1].split('## Execution and limits',1)[0]
extra=attack.split('## Additional observations not separately promoted',1)[1].split('## Specification review',1)[0]
db=read('db_ui/FINDINGS.md')
dbtable=db.split('| Earlier finding / exact reproduction |',1)[1].split('All six live node types',1)[0]
dbtable='| Earlier finding / exact reproduction |'+dbtable
dbtable=dbtable.replace('\n\n| M17','\n| M17')
name_table=links(read('names/historical_table.md'),'names')
# Refresh an inherited table note to the immediately preceding raw-alias comparison.
name_table=name_table.replace('no new raw-alias loss versus M16','no new raw-alias loss versus M17')

intro=f'''# Independent relation-map review — round 18

Reviewed **`{before['head']}`**. **CHANGES REQUIRED: one newly reproduced P1 originator-refusal family.** `trastuzumab radiolabelled with iodine-124` passes every refusal stage and draws unlabelled TRASTUZUMAB, with 13 map trials and 12 trial / 12 sponsor QA evidence rows. Its `I-124` spelling refuses. This is an inherited gap present in HEAD^, not a demonstrated latest-patch regression.

All exact previously promoted M1–M17 primary name blockers are **FIXED**, including M17-B1 `trastuzumab labelled-I-124`. Earlier supplemental gaps, availability limits and cost/UI/documentation qualifications retain individual **NOT FIXED** dispositions below. They are not silently counted as repaired. The user-listed over-refusals and ChEMBL bevacizumab-code limitation do not determine this verdict.

No application source or tracked file was edited. New scratch files are confined to `audit_evidence_claims/m18/`.

## Verification and scope

- **345 passed in 39.81 s**, exit 0: `python -m pytest tests -q -p no:cacheprovider`. Bytecode disabled; temporary paths confined to m18. [Test output](root_checks/pytest.txt), [command/environment/hashes](root_checks/pytest_summary.json).
- Reused cumulative originals cover m1, partial m2/completed m2b, and m3–m17. Root main, remaining and late batches exit zero; m16 independent HTTP replays 19 cases / 76 requests; m17 replays 17 cases / 68 requests. [Report inventory](historical_report_inventory.json), [root provenance](reuse_manifest_root.json), [main](root_checks/execution_all.json), [remaining](root_checks/execution_remaining.json), [late](root_checks/execution_m18_late.json), [m16 HTTP](root_checks/independent_m16_http.json), [m17 HTTP](root_checks/independent_m17_http.json).
- Historical naming: **62 scripts reused / 52 leaf reproducers executed**, all successful. **78 disposition rows: 62 FIXED / 16 NOT FIXED**. Raw **7,511-key** alias sweep has **zero new losses or recoveries versus m17**. Adapted frozen **1,648-question** comparison remains **68 identical / 1,556 metadata-only / 24 semantic / zero errors**. Diagnostic raw sweep differences are not defect counts. [Name review](names/FINDINGS.md), [execution checks](names/worker_final_checks.json), [alias delta](names/new_alias_losses.json), [QA comparison](names/adapted_frozen_qa_relink_sweep.json).
- Stored-row oracle: **6,469 live centres / 22 relation-direction-type-role combinations / zero errors**. **19/19 DB**, **24/24 UI**, **4/4 self-loop/unknown-type/retirement** checks pass. [Oracle](db_ui/db_validate.json), [DB](db_ui/db_assertions.json), [UI](db_ui/ui_assertions.json), [fixture](db_ui/self_loop_unknown.json).
- **36/36 demos** equal every m7–m17 full-response baseline, and all 36 original-CLI HTTP demo responses equal direct Engine responses. Six map callbacks pass; seven original QA evidence counts remain **12, 12, 11, 1, 12, 0, 0**. [Baseline comparisons](db_ui/demo_previous_comparison.json), [HTTP](db_ui/demo_http.json), [callbacks](db_ui/ui_m3_checks.json).
- Attack worker: **231 historical staged cases + 64 fresh current/HEAD^ paired cases**, **676 actual CLI HTTP requests**, all 200; **428 transformed aliases / 104 keys** have no centre/refusal changes versus m17. A separate name worker reran 63 m17 staged cases / 252 HTTP requests; DB/UI independently replayed 36 previous stage cases. Root independently confirmed the new family and controls with **19 cases / 76 HTTP requests**. These counts overlap by design and are not summed as unique cases. [Attack assertions](attacks/final_checks.json), [alias comparison](attacks/alias_variants_comparison.json), [name HTTP](names/m17_exact/new_http.json), [DB/UI stages](db_ui/adjudication_tracer.json), [root assertions](root_checks/independent_m18_summary.json).

UI checks execute actual page JavaScript in a Node VM with controlled DOM/fetch stubs: they verify generated markup and exercised callbacks/state, not browser painting or browser-executed XSS. HTTP uses unmodified `src/app.py` on owned ports other than 8765, or its actual handler with isolated in-memory fixtures. Counterfactuals replace only the stated query code against current remaining modules/data; they are not complete old deployments. No model was called.

## M18-B1'''

independent='''## Independent confirmation and repair assessment

The root independently started the original CLI server on port 8849, verified served page bytes, and issued resolve/explore/trial-QA/sponsor-QA requests. Four full-element-name inputs (`iodine-124 trastuzumab`, `trastuzumab radiolabelled with iodine-124`, `trastuzumab labelled with iodine-124`, `trastuzumab radiolabelled with zirconium-89`) draw CHEMBL1201585 with 13 trials and 12/12 QA evidence, without refusal. Seven paired symbol/M17 controls refuse with no centre and zero QA evidence. `BKM120`, `AZD9291`, `osimertinib 80 mg`, `paclitaxel 2 cycles`, and `13-cis retinoic acid` remain available. Comma-list reversal exposes the accepted tracer even when OSIMERTINIB is selected first. [All 76 requests/responses](root_checks/independent_m18_http.json), [explicit assertions](root_checks/independent_m18_summary.json), [server lifecycle](root_checks/independent_m18_lifecycle.json), [adaptation](root_checks/independent_m18_manifest.json).

The separate DB/UI reviewer independently captures `_qualified=false`, `_resolver_blocked={}`, `_marked=None`, `_whole_name=None`, Drug-only linking, 13 map trials and 12/12 QA for `trastuzumab labelled with iodine-124`, in current and HEAD^ code. [Independent stages](db_ui/independent_boundary.json). This corroborates M18-B1 rather than adding a blocker count.

The actual latest patch preserves punctuation boundaries for symbol notation (`src/query.py:164-172`). Twenty-four formerly leaking centre cases in the 63-case m17 attack set improve; the old primary `trastuzumab labelled-I-124` now refuses. This validates the repair while showing that the full-name identity gap remains. [M17 stage replay](attacks/m17_results.json), [M17 root HTTP](root_checks/independent_m17_http.json).

## Earlier reproductions — FIXED / NOT FIXED per finding

Status applies to the exact prior reproduction, not every possible spelling. Passing exit codes alone are not the basis for these dispositions; returned identities, refusal existence, stored values and QA evidence are inspected. M2 has no completed report: its partial fixtures are included through m2b. Matrices overlap where independent reviewers reproduced the same finding, so their row totals are not a count of unique defects.

### Name resolution, m1–m17

**78 rows: 62 FIXED / 16 NOT FIXED.**

'''

known='''### Accepted exceptions and unresolved historical qualifications

The user explicitly excludes these known over-refusals from blockers: M5-S2; 40-o-/42-o-(2-hydroxyethyl)rapamycin; Trastuzumab--vcmmae conjugate; 9-amino-20(s)-camptothecin; il-6ra; TAK-659F; GS-11CAL-101; 3en3hg4wsw; and same-list-item refusal. The ChEMBL bevacizumab biosimilar-code synonym limitation is also explicitly excluded. Fresh dispositions retain these exclusions.

Other old supplements are not presented as accepted exceptions or as fixed: `b.i.o.similar bevacizumab` still draws BEVACIZUMAB with 122 trials and 12/12 QA rows; `lip.osomal doxorubicin` still draws DOXORUBICIN with 3 trials and 3/3 QA rows. Reversed formulation wording and prefixed comma-containing drug-name QA also remain NOT FIXED as tabulated. These are inherited unresolved gaps, not newly discovered M18 families. The new natural iodine-124 description is independently sufficient for rejection under the original approval bar. [Replayed supplemental cases](names/m12_attacks/focused_results.json), [reversed wording](names/reversed_results.json), [comma-name QA](names/historical_focus.json).

Lowercase IDs/investigator-name lookup, slash PET/CT not_found wording, blank-form state, malformed-body error text, README test counts and residual costs remain separately recorded. Failure-closed observations and presentation issues are should-fix items, not the new originator blocker.

## Additional diagnostic probes

'''

integrity=f'''## Integrity and reproduction

`Engine.ask` passes `use_llm=False` (`src/app.py:181`). Database mutation fixtures use isolated in-memory copies. The app's SQLite handle is not globally read-only; no-write conclusions rely on the inspected/executed paths and byte comparisons. Final verification checks **{len(before['tracked_sha256']):,} tracked-file SHA-256 hashes**, unchanged HEAD, clean tracked/staged diffs, unchanged DB bytes, report links, and closure of ports identified in this run's server-lifecycle records. [Initial snapshot](integrity_before.json), [final verification](integrity_final.json). DB SHA-256: `{before['db_sha256']}`.

The pre-existing m18 brief/log were preserved. Bytecode is disabled and temporary files remain under each m18 family's `tmp/`. Source/adapted hashes and path/port changes are recorded in the manifests. Original scripts are reused from m18 copies, so the earlier tracked audit directories are not rewritten. No application repair was implemented; the conditional request to show original/replacement production code against KOA Studio/KhOpenApi therefore does not arise.

Representative runners, from repository root (shared-port HTTP suites run sequentially; cost runs after other workloads):

```text
python -B audit_evidence_claims/m18/root_checks/run_all.py
python -B audit_evidence_claims/m18/root_checks/run_m18_late.py
python -B audit_evidence_claims/m18/root_checks/independent_m18_http.py
python -B audit_evidence_claims/m18/names/run_round9.py
python -B audit_evidence_claims/m18/names/run_remaining.py
python -B audit_evidence_claims/m18/db_ui/run_db.py
python -B audit_evidence_claims/m18/db_ui/run_ui.py
python -B audit_evidence_claims/m18/db_ui/run_final.py
python -B audit_evidence_claims/m18/attacks/new_probe.py
python -B audit_evidence_claims/m18/attacks/new_http.py
python -B audit_evidence_claims/m18/cost/run_isolated.py
python -B audit_evidence_claims/m18/cost/repeated_match_followup.py
python -B audit_evidence_claims/m18/build_cost_section.py
python -B audit_evidence_claims/m18/build_report.py
python -B audit_evidence_claims/m18/finalize_integrity.py
```

Standards: **0 documented violations**. Specification: **one newly promoted P1 originator-refusal family**, independently sufficient for rejection; unresolved historical supplements remain explicitly NOT FIXED.

VERDICT: CHANGES REQUIRED
'''

report=(intro+links(primary,'attacks')+independent+name_table+'\n\n### DB, UI, server and documentation\n\n'
        +'**27 rows: 22 FIXED / 5 NOT FIXED**, including independent overlap with the naming matrix.\n\n'
        +links(dbtable,'db_ui')+'\n'+known+links(extra,'attacks')+'\n'+read('cost_section.md')
        +'\n## Standards\n\n'+links(read('db_ui/STANDARDS.md').split('\n',1)[1].lstrip(),'db_ui')
        +'\n## Specification\n'+links(spec,'attacks')+'\n'+integrity)
(OUT/'REPORT.md').write_text(report,encoding='utf8')
print('Report written:',len(report.splitlines()),'lines')
