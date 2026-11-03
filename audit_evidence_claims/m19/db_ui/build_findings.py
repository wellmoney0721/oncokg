"""Assemble fresh DB/UI results, retaining exact historical finding identifiers."""
from pathlib import Path
import hashlib,json,re,socket,subprocess

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
load=lambda name:json.loads((OUT/name).read_text(encoding='utf8'))
v=load('db_validate.json'); db=load('db_assertions.json'); ui=load('ui_assertions.json')
demo=load('demo_http.json'); demos=load('demo_previous_comparison.json'); life=load('demo_http_lifecycle.json')
assert v['checks']==6469 and not v['errors'] and len(v['relation_combinations'])==22
assert db['passed']==db['total']==19 and ui['passed']==24
assert demo['total']==demo['http_200']==demo['equal']==36 and demo['served_equals_worktree']
assert all(x['equal']==36 and x['same_length'] and not x['errors'] for x in demos)
assert life['closed']
sha=lambda b:hashlib.sha256(b).hexdigest()
before=load('worker_integrity_before.json')
sock=socket.socket();port_closed=sock.connect_ex(('127.0.0.1',9221))!=0;sock.close()
final={'head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
       'db_sha256':sha((ROOT/'data/processed/oncokg.sqlite').read_bytes()),'owned_port':9221,'port_closed':port_closed,
       'tracked_status':subprocess.check_output(['git','status','--short','--untracked-files=no'],cwd=ROOT,text=True)}
assert final['head']==before['head'] and final['db_sha256']==before['db_sha256'] and not final['tracked_status'] and port_closed
(OUT/'worker_final_checks.json').write_text(json.dumps(final,indent=2),encoding='utf8')

prior=(ROOT/'audit_evidence_claims/m18/db_ui/FINDINGS.md').read_text(encoding='utf8')
table=prior.split('| Earlier finding / exact reproduction |')[1].split('\n\nAll six live node types')[0]
table='| Earlier finding / exact reproduction |'+table
table=table.replace('Round 18 result','Round 19 result')
table=table.replace('M1-M17 README','M1-M18 README')
table=table.replace('Current and HEAD^ refuse the original unlabelled-originator spellings','Current and HEAD^ refuse the original unlabelled-originator spellings')
table=table.replace('HEAD^ still leaks. Adjacent symbol pieces now preserve the boundary. `src/query.py:164-172`.','HEAD^ and current both refuse. Adjacent symbol pieces preserve the boundary. `src/query.py:188-197`.')
table+='\n| M18-B1 independent exact input: `trastuzumab labelled with iodine-124`; `trastuzumab labelled iodine 124` | **FIXED**. Current linker refuses and map has no centre; trial and sponsor QA have zero evidence. HEAD^ draws TRASTUZUMAB with 12/12 QA rows. `src/query.py:156-187`. [Independent stages](independent_boundary.json). |\n'
table+='| M18 synthetic mass-split diagnostics: `trastuzumab labelled-I-1-24`, `trastuzumab labelled-I-12-4`, `trastuzumab labelled-I-(1)(24)` | **NOT FIXED**, unchanged diagnostic qualification, not promoted as natural scientific notation. All three continue to map TRASTUZUMAB with 12/12 QA rows. [Stages](independent_boundary.json). |\n'
table+='| M16-M18 cross-word one-letter qualification: `trastuzumab labelled I 124` | **NOT FIXED**, unchanged previously excluded cross-word diagnostic. The within-word requirement remains separate. [Stages](independent_boundary.json). |\n'
(OUT/'historical_table.md').write_text(table,encoding='utf8')
matrix=[]
for line in table.splitlines():
    if not line.startswith('|') or '**FIXED' not in line and '**NOT FIXED' not in line:continue
    finding,result=line.strip().strip('|').split('|',1)
    matrix.append({'finding':finding.strip(),'status':'NOT FIXED' if '**NOT FIXED' in result else 'FIXED','evidence':result.strip()})
(OUT/'historical_findings_matrix.json').write_text(json.dumps(matrix,ensure_ascii=False,indent=2),encoding='utf8')
rows=load('ui_m19_http.json')['rows']
new_leaks=[x for x in rows if x['input'] in ['radio-labelled trastuzumab','99m-technetium trastuzumab']]
assert len(new_leaks)==2 and all(x['center']=='CHEMBL1201585' and x['has_svg'] and not x['has_refusal'] for x in new_leaks)
controls=[x for x in rows if x['input'] in ['radiolabelled trastuzumab','technetium-99m trastuzumab']]
assert len(controls)==2 and all(x['has_refusal'] and not x['has_svg'] and not x['trail'] for x in controls)

manifest={'reused_scripts':24,'reused_commands':load('execution.json')+load('execution_ui_complete.json')+load('execution_final.json'),
          'supplementary_commands':[{'command':'python -B audit_evidence_claims/m19/db_ui/'+x,'exit_code':0,'execution_evidence':'unified execution session 87739, which completed exit 0'} for x in ['demo_http.py','self_loop_unknown.py','adjudicate_tracer.py','independent_boundary.py']],
          'new_ui_command':{'command':'node audit_evidence_claims/m19/db_ui/ui_m19_http.js','exit_code':0,'output':'ui_m19_http.json'},
          'comparison_command':{'command':'python -B audit_evidence_claims/m19/db_ui/complete_review.py','exit_code':0},
          'all_outputs_under':'audit_evidence_claims/m19/db_ui','fixture_mutation':'in-memory only',
          'db_before':before['db_sha256'],'db_after':final['db_sha256']}
(OUT/'execution_manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf8')
summary=f'''# Round 19: database, UI, demos and Standards

Reviewed HEAD **`{final['head']}`**. **No new graph-membership, direction, stored-value or demo regression found.** Current UI does render the two new originator leaks confirmed by the root reviewer; their causes are name resolution, not rendering. The latest full-element repair fixes the exact previous iodine examples.

## Verification and scope

**24 reused scripts** from m18's cumulative DB/UI suite, plus one new form-callback harness. Original fixture inputs are preserved; output paths point to m19 and the owned CLI port is 9221. [Reuse manifest](reuse_manifest.json), [execution manifest](execution_manifest.json).

- Stored-row oracle: **6,469 live centres, 22 relation/direction/type/role combinations, 0 errors**. Live-edge membership, endpoint direction, metadata, trial counts, totals and ordering agree. Oracle loop {v['seconds']:.3f} s; full db_recheck command {load('execution.json')[0]['seconds']:.3f} s under overlapping audit work, not an isolated cost benchmark. [Oracle](db_validate.json).
- **19/19 DB assertions**, **24/24 UI assertions**, and **4/4 self-loop/unknown/retirement assertions** pass. Seven DB, eight UI and two final commands exit zero. [DB](db_assertions.json), [UI](ui_assertions.json), [self-loop fixture](self_loop_unknown.json).
- **36/36 page demos** and **six map example callbacks** pass. Responses equal every m7-m18 baseline; QA evidence counts remain **12, 12, 11, 1, 12, 0, 0**. [Comparisons](demo_previous_comparison.json), [renders](ui_demos_results.json), [callbacks](ui_m3_checks.json), [QA counts](ui_demo_compare.json).
- **36/36 original-CLI HTTP demos** return 200 and equal direct Engine responses. Served page bytes equal the worktree. Port **9221 is closed**. Five root HTTP maps also equal their direct map responses. [HTTP](demo_http.json), [lifecycle](demo_http_lifecycle.json), [assertions](ui_assertions.json).

UI checks execute the actual page JavaScript in a Node VM with controlled DOM/fetch stubs. They establish generated markup, exercised state and callbacks, not browser painting or browser-executed XSS. No owned server used port 8765. No model was called. Root reports pytest and isolated cost separately.

## Historical findings: individual dispositions

This table covers non-name/non-cost findings through m18, plus independent isotope corroborations. M2 has no completed report; its partial role/order cases are included. Each current disposition uses fresh evidence, not the historical script's exit code alone. Names and performance have separate worker matrices. [Historical report inventory](historical_report_headings.json), [machine-readable matrix](historical_findings_matrix.json).

{table}

All six live node types and all 22 existing relation combinations are covered. The snapshot has **7 retired nodes, 142 retired edges, zero self-loops and zero live edges with retired endpoints**. PARENT_OF, STUDIES, ASSOCIATED_WITH, EVALUATES, ACTS_ON and role-aware SPONSORS agree with stored endpoints. All **3,000 stored URLs** use registry HTTPS URLs, and all node/edge props are valid JSON objects. [Snapshot](db_snapshot_facts.json), [oracle](db_validate.json). Self-loop behavior is an isolated fixture result.

## New HTTP-to-UI corroboration

The root's independent CLI captures were passed unchanged to the **actual page form submission callback**, then rendered by `exploreSafe`/`explore`. Both `radio-labelled trastuzumab` and `99m-technetium trastuzumab` render a **TRASTUZUMAB / CHEMBL1201585 centre**, an SVG relationship map and a trail entry, without a refusal. The paired `radiolabelled trastuzumab` and `technetium-99m trastuzumab` responses render refusal text, no SVG, and an empty trail. All **22 captured /explore responses** render without errors. This ties the root's name-resolution defects to the displayed map. [Actual generated markup and state](ui_m19_http.json), [harness](ui_m19_http.js), [root HTTP evidence](../root_checks/independent_m19_http.json). It is a VM rendering check, not a real-browser claim.

## Standards

{(OUT/'STANDARDS.md').read_text(encoding='utf8').split(chr(10),2)[2]}

## Integrity and reproduction

Database SHA-256 remains **`{final['db_sha256']}`**. HEAD is unchanged and `git status --short --untracked-files=no` is empty. All scratch outputs stay in this directory. [Before](worker_integrity_before.json), [final](worker_final_checks.json). Full tracked-file hashes are checked by the root reviewer.

Run from the repository root with bytecode disabled; TMP/TEMP/TMPDIR for child processes point to this directory's tmp/. The root HTTP artifacts must exist before run_final.py.

```text
python -B audit_evidence_claims/m19/db_ui/run_db.py
python -B audit_evidence_claims/m19/db_ui/run_ui.py
python -B audit_evidence_claims/m19/db_ui/run_final.py
python -B audit_evidence_claims/m19/db_ui/demo_http.py
python -B audit_evidence_claims/m19/db_ui/self_loop_unknown.py
python -B audit_evidence_claims/m19/db_ui/adjudicate_tracer.py
python -B audit_evidence_claims/m19/db_ui/independent_boundary.py
python -B audit_evidence_claims/m19/db_ui/complete_review.py
node audit_evidence_claims/m19/db_ui/ui_m19_http.js
python -B audit_evidence_claims/m19/db_ui/build_findings.py
```
'''
(OUT/'FINDINGS.md').write_text(summary,encoding='utf8')
print(json.dumps({'historical_rows':len(matrix),'fixed':sum(x['status']=='FIXED' for x in matrix),'not_fixed':sum(x['status']=='NOT FIXED' for x in matrix),'db_assertions':db['passed'],'ui_assertions':ui['passed'],'new_http_ui_rows':len(rows),'integrity':final},ensure_ascii=False))
