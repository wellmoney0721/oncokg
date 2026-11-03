"""Write round-15 findings from fresh evidence plus the historical disposition inventory."""
from pathlib import Path
import json,hashlib,re
out=Path(__file__).resolve().parent
root=out.parents[2]
old=(root/'audit_evidence_claims/m14/db_ui/FINDINGS.md').read_text(encoding='utf8')
table=old.split('## Historical findings: individual dispositions',1)[1].split('## Standards axis',1)[0]
table=table.replace('m1-m13','m1-m14').replace('Round 14 result','Round 15 result')
oracle=json.loads((out/'db_validate.json').read_text(encoding='utf8'))
assert not oracle['errors'] and oracle['checks']==6469
assert json.loads((out/'db_assertions.json').read_text(encoding='utf8'))['passed']==19
assert json.loads((out/'ui_assertions.json').read_text(encoding='utf8'))['passed']==24
header='''# Round 15: database, UI, demos and independent adjudication

Reviewed HEAD **`1b3896669387cbc142c12b726909231cca8658db`**. No new DB/UI/demo blocker was found. Independent staged adjudication confirms one inherited originator-leak family involving punctuation inside a neighboring chelator-label word, plus residual lowercase stored-tracer variants. [Adjudication](adjudication.md).

## Reproduction coverage

**22 scripts reused** from m14's cumulative DB/UI suite, representing the m1-m14 DB/UI reproductions. All writes and temporary files stay under `audit_evidence_claims/m15/`; prior evidence is read only. Output-path and owned-port adaptations preserve core reproductions. The independent adjudicator additionally uses the new candidate/control list. [Initial source/adapted hashes](reuse_manifest.json), [final script hashes](worker_final_checks.json).

- Independent stored-row oracle: **6,469 live centres, 22 relation/direction/type/role combinations, zero errors**. Exact live-edge sets, endpoints, stored details/counts, total counts and ordering agree. Oracle interval **222.980 s**, overlapping other audit work; this is not an isolated cost measurement. [Oracle](db_validate.json).
- **19/19 DB assertions** and **24/24 UI assertions** pass. All seven DB-runner scripts, eight UI commands and two final commands exit zero. [DB assertions](db_assertions.json), [UI assertions](ui_assertions.json), [DB execution](execution.json), [UI execution](execution_ui_complete.json), [final execution](execution_final.json).
- **36/36 page demos and six map callbacks pass**. Full demo response objects equal each m7-m14 baseline. QA evidence counts remain **12, 12, 11, 1, 12, 0, 0**. [Comparison](demo_previous_comparison.json), [demos](ui_demos_results.json), [callbacks](ui_m3_checks.json).
- **36/36 original-CLI HTTP demos** return 200 and exactly match direct Engine responses. Served page bytes equal the worktree. Owned port **8951 is closed**. [HTTP](demo_http.json), [lifecycle](demo_http_lifecycle.json), [status](worker_status.json).
- **4/4** self-loop/unknown-type/retirement fixture checks pass through the real handler. A self-loop appears once as outgoing; unknown relation/type values are preserved. [Fixture](self_loop_unknown.json).

UI tests execute the actual page JavaScript in a Node VM with controlled DOM/fetch stubs. They establish generated markup and exercised state/callback behavior, not browser painting or browser-executed XSS. Mutation fixtures use isolated in-memory databases. No audit used port 8765 or called a model.

## Historical findings: individual dispositions
'''
footer='''## Standards axis

**Zero documented-standards violations found.** Reviewed the app/UI diff from `bfcb83d` and latest query/test patch. No tracked AGENTS.md, CONTRIBUTING.md, CODING_STANDARDS.md or docs/agents/issue-tracker.md exists. User-supplied evidence-based, audit-only instructions govern. No tracked application code was changed, so the conditional original/modified-code comparison against KOA Studio/KhOpenApi does not apply. [Review record](standards_review.json), [app/UI diff](review_diff_app_ui.txt), [latest diff](review_diff_latest.txt).

## Specification axis

**No new DB/UI/demo blocker; one independently confirmed refusal family.** `89-ZrDFO trastuzumab`, `89Z.rDFO trastuzumab` and `trastuzumab DFO89-Zr` draw TRASTUZUMAB / CHEMBL1201585 with 13 live trials and 12/12 qualified trial/sponsor QA rows. Every refusal stage misses; unpunctuated controls refuse with zero evidence. Raw `_isotope_edge` already recognizes the hyphen cases, but normalization fractures them before the helper is called. This is a one-character normalization bypass beside the named drug, distinct from the old descriptive-distance supplementary forms. It is inherited in HEAD^, not introduced by this patch. [Source-cited adjudication](adjudication.md), [stage traces](adjudication_tracer.json).

Exact uppercase `3HVINBLASTINE`, `3Hvinblastine` and `A33124I` are **FIXED**. Lowercase `3hvinblastine` and `A33124i` are **NOT FIXED**: they still map the same keys as their refused stored tracer controls. These are recorded as residuals rather than additional new families. The new chelator-punctuation leak independently fails the approval bar.

## Additional source and integrity checks

README app descriptions remain accurate (`README.md:566`, `README.ko.md:387`). Adjacent **317-test** comments remain **NOT FIXED**, a documentation-only should-fix; the root reviewer ran the current suite. Map cut notices and actual sorting agree. Stored count/phase, trial start, action and sponsor class details remain visible with raw codes where needed.

`Engine.ask` sets `use_llm=False` (`src/app.py:180-181`). Snapshot reads use SQLite `mode=ro`; mutation fixtures use in-memory copies. The app connection is not globally read-only, so no-write verification rests on inspected paths, executed behavior and root integrity checks. Database SHA-256 is **`7341c5a7089731f67356da5a588b269d4b69e8e6c4c054acf19aa4ef2837b529`**. Root performs tracked-file integrity verification.

Run from repository root with bytecode disabled and TMP/TEMP/TMPDIR under this folder's `tmp/`. Final assertions require root's fresh HTTP artifacts:

```text
python -B audit_evidence_claims/m15/db_ui/run_db.py
python -B audit_evidence_claims/m15/db_ui/run_ui.py
python -B audit_evidence_claims/m15/db_ui/run_final.py
python -B audit_evidence_claims/m15/db_ui/demo_http.py
python -B audit_evidence_claims/m15/db_ui/self_loop_unknown.py
python -B audit_evidence_claims/m15/db_ui/adjudicate_tracer.py
python -B audit_evidence_claims/m15/db_ui/complete_review.py
python -B audit_evidence_claims/m15/db_ui/write_findings.py
```
'''
(out/'FINDINGS.md').write_text(header+table+footer,encoding='utf8')
scripts={p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in out.iterdir() if p.suffix in ('.py','.js')}
checks={'scripts':scripts,'db_assertions_passed':19,'ui_assertions_passed':24,'oracle_centres':6469,'oracle_errors':len(oracle['errors']),'relation_combinations':len(oracle['relation_combinations']),'all_owned_work_complete':True,'report_links_missing':[]}
for name in ['FINDINGS.md','adjudication.md']:
    for target in re.findall(r'\]\(([^)]+)\)',(out/name).read_text(encoding='utf8')):
        if target!='worker_final_checks.json' and not target.startswith('http') and not (out/target).exists(): checks['report_links_missing'].append({'source':name,'target':target})
(out/'worker_final_checks.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2),encoding='utf8')
assert not checks['report_links_missing'],checks
print(json.dumps({k:v for k,v in checks.items() if k!='scripts'}))
