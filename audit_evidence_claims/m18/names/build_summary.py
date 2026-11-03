"""Validate fresh artifacts and assemble per-finding historical dispositions."""
from pathlib import Path
import hashlib,json,socket,subprocess
root=Path.cwd();out=Path(__file__).resolve().parent
prior=root/'audit_evidence_claims/m17/names'
def read(name):return json.loads((out/name).read_text(encoding='utf8'))
def old(name):return json.loads((prior/name).read_text(encoding='utf8'))
qa=read('adapted_frozen_qa_relink_sweep.json')['summary']
assert qa==dict(questions=1648,identical=68,entities_only=1556,semantic_changes=24,errors=0)
assert [r['finding'] for r in read('focused_matrix.json') if not r['matches_expectation']]==['M5-S2-known']
assert all(r['status']=='FIXED' for r in read('historical_focus.json')['cases'])
assert all(r['actual_center']==r['expected_center'] for r in read('m11_exact.json'))
current=read('names_m5_summary.json')
before={r['input'] for r in old('names_m5_summary.json')['new_lone_alias_refusals']}
after={r['input'] for r in current['new_lone_alias_refusals']}
assert before==after
assert current['aliases_checked']==7511 and current['alias_anomalies']==320
assert len(after)==71
assert not read('adapted_names_m5_summary.json')['cache_errors']
losses=dict(description='Current versus M17 raw alias loss set; diagnostic totals, not defect counts.',new_losses=sorted(after-before),recovered=sorted(before-after),current_loss_count=len(after),previous_loss_count=len(before))
(out/'new_alias_losses.json').write_text(json.dumps(losses,indent=2),encoding='utf8')
historical=json.loads((root/'audit_evidence_claims/m7/names/names_m5_summary.json').read_text(encoding='utf8'))['new_lone_alias_refusals']
overlap=sorted(after & {r['input'] for r in historical})
assert overlap==['Pegylated interferon alfa-2a']
(out/'historical_alias_set_check.json').write_text(json.dumps(dict(original_loss_set=len(historical),still_lost=overlap,all_19_non_M5_S2_restored=True),indent=2),encoding='utf8')
comparison=read('replay_comparison.json')
assert not any(r.get('missing') for r in comparison['files'])
changed=[r for r in comparison['files'] if not r['normalized_equal']]
assert not changed,[(r['file'],len(r.get('differences',[]))) for r in changed]
matrix=old('historical_name_dispositions.json')
m17=read('m17_exact/new_results.json')['cases']
bytext={r['text']:r for r in m17}
primary=['trastuzumab labelled-I-124','trastuzumab labelled-with-I-124','trastuzumab radiolabelled-I-124','trastuzumab radiolabeled-I124','iodine-I-124 trastuzumab','trastuzumab iodine-I-124','trastuzumab (iodine-I-124)','trastuzumab [iodine-I-124]','trastuzumab LABELLED-I-124','TRASTUZUMAB LABELLED-I-124','trastuzumab labelled-i-124','trastuzumab labelled_I_124','trastuzumab labelled:I-124','trastuzumab labelled(I-124)','trastuzumab labelled[I-124]','vinblastine tritium-H-3','vinblastine labelled-H3','erlotinib fluorine-F18','erlotinib labelled-F18','paclitaxel carbon-C14','paclitaxel labelled-C14','cetuximab labelled-Y-90']
for text in primary:
    x=bytext[text]['current']
    assert x['map'].get('refused') and not x['map'].get('center'),text
    assert not x['trial_qa']['evidence'] and not x['sponsor_qa']['evidence'],text
for text in ['trastuzumab labelled-I-124, osimertinib','osimertinib, trastuzumab labelled-I-124','trastuzumab labelled-I-124 and osimertinib','osimertinib and trastuzumab labelled-I-124']:
    x=bytext[text]['current']
    assert x['map']['center']['id']=='CHEMBL3353410'
    assert any(r['type']=='Refused' for r in x['public_linker'])
for text in ['osimertinib 80 mg','paclitaxel 2 cycles','cisplatin 75 mg/m2 day 1','13-cis retinoic acid','BKM120','AZD9291','trastuzumab','vinblastine','erlotinib','paclitaxel','cetuximab']:
    assert bytext[text]['current']['map'].get('center'),text
    assert not any(r['type']=='Refused' for r in bytext[text]['current']['public_linker']),text
http=read('m17_exact/new_http.json');life=read('m17_exact/new_lifecycle.json')
assert len(m17)==63 and len(http)==252 and all(r['status']==200 for r in http)
assert life['port_closed'] and life['database_unchanged'] and life['page_matches_worktree']
matrix.append(dict(round='M17',finding='M17-B1 punctuation-delimited element-first one-letter isotope',status='FIXED',detail='Original trastuzumab labelled-I-124 and 21 punctuation/case/H3/F18/C14/Y90 corroborations now refuse without a centre and with zero trial/sponsor evidence. Separate-list osimertinib survives with refusal disclosed. All 63 original staged cases and 252 original HTTP requests replayed; dose/BKM120/AZD9291/bare controls survive.',evidence='m17_exact/new_results.json'))
(out/'historical_name_dispositions.json').write_text(json.dumps(matrix,ensure_ascii=False,indent=2),encoding='utf8')
table=['| Round / finding | Status | Fresh evidence |','|---|---|---|']
for row in matrix:
    cells=[row['round']+' '+row['finding'],'**'+row['status']+'**',row['detail']+' [Evidence]('+row['evidence']+').']
    table.append('| '+' | '.join(c.replace('|','\\|') for c in cells)+' |')
(out/'historical_table.md').write_text('\n'.join(table)+'\n',encoding='utf8')
exec_names=['round9_execution.json','replay_execution.json','supplement_execution.json','final_replay_execution.json','additional_execution.json','completion_execution.json','remaining_execution.json','m17_execution.json']
executions={f:read(f) for f in exec_names}
assert all(r['exit_code']==0 for rows in executions.values() for r in rows)
assert all(r['exit_code']==0 for r in read('m1_exact/execution.json')['scripts'])
closed={}
for port in [9110,9111,9112]:
    with socket.socket() as sock:closed[str(port)]=sock.connect_ex(('127.0.0.1',port))!=0
assert all(closed.values())
manifest=read('reuse_manifest.json')
assert all(hashlib.sha256((root/r['source']).read_bytes()).hexdigest()==r['source_sha256'] for r in manifest)
assert all(hashlib.sha256((root/r['destination']).read_bytes()).hexdigest()==r['destination_sha256'] for r in manifest)
leafs=sorted(set(r['script'] for rows in executions.values() for r in rows if not Path(r['script']).name.startswith('run_') and r['script']!='compare_replays.py')|{'m1_exact/'+r['script'] for r in read('m1_exact/execution.json')['scripts']})
counts={s:sum(r['status']==s for r in matrix) for s in ['FIXED','NOT FIXED']}
head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
checks=dict(head=head,scripts_reused=len(manifest),executed_leaf_reproductions=len(leafs),executed_leaf_scripts=leafs,historical_disposition_count=len(matrix),disposition_counts=counts,raw_aliases_checked=7511,raw_alias_differences=320,raw_alias_losses=71,new_alias_losses=[],alias_recoveries=[],original_19_non_M5_S2_aliases_restored=True,frozen_qa=qa,replay_comparison_files=len(comparison['files']),changed_replay_files=[],m17_original_stage_cases=63,m17_http_requests=252,m17_primary_and_corroboration_forms_checked=len(primary),source_script_hashes_unchanged=True,adapted_script_hashes_match=True,owned_ports_closed=closed,all_execution_exit_codes_zero=True)
(out/'worker_final_checks.json').write_text(json.dumps(checks,indent=2),encoding='utf8')
lines=[f'''# Round 18 historical name-resolution verification

Reviewed HEAD `{head}`. **All exact previously promoted name-resolution blockers from M1 through M17 are FIXED.** M17's punctuation-delimited element-first one-letter isotope inputs now refuse. Status describes exact previous reproductions, not safety of every spelling. This is a historical-name contribution; the root reviewer owns the overall verdict.

## Execution and evidence

- **{len(manifest)} original scripts reused; {len(leafs)} reused leaf reproductions executed.** All runners exit zero. Source and adapted hashes verify; ports 9110/9111/9112 are closed. [Manifest](reuse_manifest.json), [literal checks](adaptation_literal_check.json), [execution checks](worker_final_checks.json), [main batch](round9_execution.json), [remaining batch](remaining_execution.json).
- Raw **113-case / 7,511-key** scan: **320** differences from the frozen old method and **71** prior-linked aliases without a current Drug. **Zero new losses/recoveries versus M17.** These diagnostic totals are not defect counts. All 19 previously restored non-M5-S2 aliases remain restored. [Raw](names_m5_attack.json), [summary](names_m5_summary.json), [comparison](new_alias_losses.json), [historical set](historical_alias_set_check.json).
- Frozen **1,648-question** adapted no-relink comparison: **68 identical / 1,556 metadata-only / 24 semantic / zero errors**. The legacy no-longer-effective wrapper's 1,648 identical is recorded separately and not used as the meaningful counterfactual. [Adapted](adapted_frozen_qa_relink_sweep.json), [legacy](frozen_qa_relink_sweep.json).
- **39-case** focused matrix mismatches only accepted M5-S2; all **26** literal M6/M7 controls pass. [Matrix](focused_matrix.json), [controls](historical_focus.json).
- Original inventories include M9 146 inputs/16 QA; M10 1,224 inputs plus 35 focus cases; M11 26 probes plus 12 literal forms; M12 41 focus cases; M13 nine joined-label cases; M14 29 edge plus 27 inherited stage plus nine supplementals; M15 29 stage cases; M16 42 stage cases. All evidence behind the previous 77-row table was freshly replayed; **{len(comparison['files'])}/{len(comparison['files'])} compared files retain identity, map/evidence values and refusal existence**. [Comparison](replay_comparison.json).
- M17's **63 original current/HEAD^ stage cases** and **252 actual CLI HTTP requests** were rerun. All HTTP requests return 200, the served page matches the worktree, owned server closes, and DB bytes stay unchanged. Twenty-two original leaking single-product forms now refuse with no centre and zero trial/sponsor evidence; separate-list controls preserve osimertinib. [Stages](m17_exact/new_results.json), [HTTP](m17_exact/new_http.json), [lifecycle](m17_exact/new_lifecycle.json).

## Per-finding dispositions

M2 had no completed report; its partial cases are covered by completed M2b reproductions. DB/UI/server/cost findings are handled by the other reviewers. **{len(matrix)} rows: {counts['FIXED']} FIXED / {counts['NOT FIXED']} NOT FIXED.** Known exceptions, availability limits and old supplements remain explicit; NOT FIXED does not itself assign severity.

| Round / finding | Status | Fresh evidence |
|---|---|---|''']
for row in matrix:
    cells=[row['round']+' '+row['finding'],'**'+row['status']+'**',row['detail']+' [Evidence]('+row['evidence']+').']
    lines.append('| '+' | '.join(c.replace('|','\\|') for c in cells)+' |')
lines.append('''
## Limits and interpretation

Accepted known over-refusals and the ChEMBL bevacizumab-code data limitation remain nonblocking by the user instruction. Same-list-item refusal remains intentional. Earlier lower-case-ID/investigator lookup limits, non-parenthetical reversed-qualifier supplement, prefixed comma-name QA, fragmented qualifier supplements (`b.i.o.similar bevacizumab`, `lip.osomal doxorubicin`), and slash PET/CT not_found remain individually NOT FIXED. Their status is not silently promoted to repaired. The M17 control `cetuximab Y-90` still selects stored YTTRIUM Y-90 while disclosing refused cetuximab; it is not an every-stage-missed-refusal example.

Seven original QA demos retain **12, 12, 11, 1, 12, 0, 0** evidence rows. Six responses equal the bfcb83d-linker comparison; Mvasi differs in refusal metadata. [Demos](names_demo_results.json). Historical counterfactuals replace only their stated query method/module against current app/data; they are not whole historical deployments. Mutation fixtures use in-memory SQLite copies. No model is called.

The M17 repair is visible at `src/query.py:164-172`: each original word is checked in canonical form, as punctuation-separated pieces, and as adjacent concatenated pairs. The item result is used at `src/query.py:398-400`. Exact historical `trastuzumab labelled-I-124` now produces refusal, no map centre, and zero trial/sponsor evidence; ordinary BKM120/AZD9291 and dose/schedule controls survive. Cost is assessed by the root reviewer.

All new scratch files and temporary paths are under m18/names; bytecode is disabled. No tracked or application source was modified. Source report inventory is [recorded](historical_report_inventory.json).
''')
(out/'FINDINGS.md').write_text('\n'.join(lines),encoding='utf8')
print(json.dumps(checks,indent=2))
