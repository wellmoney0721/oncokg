"""Assemble current evidence and the reused historical DB/UI finding matrix."""
from pathlib import Path
import hashlib, json, socket, subprocess

out = Path(__file__).resolve().parent
root = out.parents[2]
load = lambda name: json.loads((out/name).read_text(encoding='utf8'))
oracle, db, ui = load('db_validate.json'), load('db_assertions.json'), load('ui_assertions.json')
assert oracle['checks'] == 6469 and not oracle['errors']
assert db['passed'] == 19 and ui['passed'] == 24
assert load('demo_http.json')['equal'] == 36
assert all(x['full_list_equal'] for x in load('demo_previous_comparison.json'))
head = subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
matrix = json.loads((root/'audit_evidence_claims/m11/db_ui/historical_db_ui_matrix.json').read_text(encoding='utf8'))
matrix += [
    {'finding': 'M1/M2b silent truncation: "x"*500 + " osimertinib" and "osimertinib " + "x"*600',
     'status': 'FIXED', 'result': '**FIXED**. Both exact oversized inputs return 400 with `input is longer than 500 characters`; neither silently draws the retained prefix. `src/app.py:239-243`. [Fresh root HTTP](../root_checks/http_results.json).'},
    {'finding': 'M1/M2b malformed JSON/list/null/oversized-body parser-error disclosure',
     'status': 'NOT FIXED', 'result': '**NOT FIXED**, inherited nonblocking qualification. Requests fail closed with 400; list/null bodies still expose `.get` errors and the 20,000-byte body cap can expose JSON parser text. Valid later calls succeed. `src/app.py:236-240,264-269`. [Fresh root HTTP](../root_checks/http_results.json).'},
]
(out/'historical_db_ui_matrix.json').write_text(json.dumps(matrix,ensure_ascii=False,indent=2),encoding='utf8')
table='\n'.join('| '+r['finding']+' | '+r['result']+' |' for r in matrix)
port=load('demo_http_lifecycle.json')['port']
sock=socket.socket();port_closed=sock.connect_ex(('127.0.0.1',port))!=0;sock.close()
status={'head':head,'db_sha256':hashlib.sha256((root/'data/processed/oncokg.sqlite').read_bytes()).hexdigest(),
        'port':port,'port_closed':port_closed,'no_application_edits_by_worker':True,
        'oracle_centres':oracle['checks'],'oracle_errors':len(oracle['errors']),
        'relation_combinations':len(oracle['relation_combinations']),
        'db_assertions':db['passed'],'ui_assertions':ui['passed'],'new_blocker_independently_confirmed':'[89Z.r]-DFO-daratumumab'}
(out/'worker_status.json').write_text(json.dumps(status,indent=2),encoding='utf8')
report=f'''# Round 12: database, UI, demos and independent adjudication

Reviewed HEAD **`{head}`**. DB, UI and demo replays establish no new defect in those scopes. Independent adjudication **confirms the new originator leak** `[89Z.r]-DFO-daratumumab`; see [adjudication.md](adjudication.md). It is an inherited hole, not a newly introduced regression. All worker-created artifacts stay under `audit_evidence_claims/m12/db_ui/`; no application, tracked or earlier-audit file was edited.

## Reproduction coverage

The **20 reused scripts** are copied from m11's cumulative DB/UI suite. Only output path literals change from m11/db_ui to m12/db_ui, and the owned CLI demo server moves from port 8893 to 8941. Original source baselines and fixture/assertion logic remain intact. Source/adapted hashes are in [reuse_manifest.json](reuse_manifest.json). The historical report inventory is in [historical_report_headings.json](historical_report_headings.json); m2 has no completed REPORT, and its partial role/order work is represented by the cumulative fixtures. Name and cost reproductions belong to the other workers.

- Independent stored-row oracle: **6,469 live centres, 22 relation/direction/type/role combinations, zero errors**. It checks exact live-edge membership, endpoints, stored details, drug counts, totals and ordering. Oracle interval **{oracle['seconds']:.3f} s**, overlapping other audit work; this is not an isolated cost measurement. [Oracle](db_validate.json).
- **19/19 DB assertions** pass, including retired rows, malformed props, missing sponsor counts, bool/decimal/Infinity scores, unknown roles and 1,001-drug count chunking across three SQL chunks. Fixtures mutate only in-memory databases. [Assertions](db_assertions.json), [execution](execution.json).
- **24/24 UI assertions** pass using actual page JavaScript, fresh Engine maps, fixture responses and root's current CLI HTTP artifacts. [Assertions](ui_assertions.json), [UI execution](execution_ui_complete.json), [final checks](execution_final.json).
- **All 36 page demos plus six map callbacks** pass; all 36 complete response objects equal m7, m8, m9, m10 and m11. Seven QA evidence counts remain **12, 12, 11, 1, 12, 0, 0**. [Full comparisons](demo_previous_comparison.json), [rendered demos](ui_demos_results.json), [callback checks](ui_m3_checks.json).
- **36/36 original-CLI HTTP demo requests** return 200 and equal direct Engine results. Served page bytes equal `web/try.html`; owned port **8941 is closed**. [HTTP](demo_http.json), [lifecycle](demo_http_lifecycle.json), [status](worker_status.json).
- The reused isolated self-loop/unknown-type/retirement fixture passes **4/4** real-handler checks. A self-loop occurs once, as outgoing, and raw unknown type/relation values survive. [Fixture](self_loop_unknown.json).

UI tests execute actual JavaScript in a Node VM with controlled DOM/fetch stubs. They establish generated markup and state/callback behavior, not browser painting or browser-executed XSS. Original-CLI requests exercise the actual server. No server used port 8765.

## Historical findings: individual dispositions

These are fresh execution dispositions, not inherited test outcomes. The table structure and finding names are reused from m11 for traceability. Name-specific and performance qualifications are in their respective workers' matrices.

| Earlier finding / exact reproduction | Round 12 result and evidence |
|---|---|
{table}

All six live node types and all 22 existing relation combinations are covered. The snapshot has **7 retired nodes, 142 retired edges, zero self-loops and zero live edges with retired endpoints**. PARENT_OF, STUDIES, ASSOCIATED_WITH, EVALUATES, ACTS_ON and role-aware SPONSORS agree with stored endpoints. All 3,000 stored URLs are registry HTTPS URLs, and all node/edge props are valid JSON objects. [Snapshot facts](db_snapshot_facts.json), [oracle facts](db_validate.json). The self-loop result is explicitly a fixture result, not a claim about the snapshot.

## Standards axis

**Zero documented-standards findings.** Reviewed `git diff bfcb83d...HEAD -- src/app.py web/try.html` and `git show HEAD -- src/query.py tests/test_app.py`. No tracked AGENTS.md, CONTRIBUTING.md, CODING_STANDARDS.md or docs/agents/issue-tracker.md was found. The user-supplied evidence-based, audit-only instructions govern. No tracked file was edited, so the conditional request for original/modified code and KOA Studio/KhOpenApi evidence does not apply. Product correctness is assessed independently and fails on the confirmed tracer alias; absence of a standards finding is not approval. [Review record](standards_review.json), [application diff](review_diff_app_ui.txt), [latest diff](review_diff_latest.txt).

## Additional source and integrity checks

README app.py descriptions (`README.md:566`, `README.ko.md:387`) accurately advertise the page. Their adjacent test-count comments still say 317, a documentation-only stale count; the root worker runs the current test suite. The map's cut notices and sorting descriptions match the implementation. Drug count/phase, trial start, action and sponsor class remain visible as stored, with raw codes retained where needed.

`Engine.ask` passes `use_llm=False` (`src/app.py:180-181`). No model was called by these checks. Snapshot reads use SQLite `mode=ro`; fixture mutations stay in memory. The app's own SQLite connection is not globally read-only, so the no-write conclusion is code-path/integrity based. DB SHA-256 is **`{status['db_sha256']}`**. Global tracked-file integrity is the root report's responsibility.

Run from repository root with bytecode disabled and TMP/TEMP/TMPDIR under this folder's `tmp/`; final UI assertions require root's fresh HTTP artifacts:

```text
python -B audit_evidence_claims/m12/db_ui/run_db.py
python -B audit_evidence_claims/m12/db_ui/run_ui.py
python -B audit_evidence_claims/m12/db_ui/run_final.py
python -B audit_evidence_claims/m12/db_ui/demo_http.py
python -B audit_evidence_claims/m12/db_ui/self_loop_unknown.py
python -B audit_evidence_claims/m12/db_ui/adjudicate_tracer.py
```
'''
(out/'FINDINGS.md').write_text(report,encoding='utf8')
print(json.dumps(status))
