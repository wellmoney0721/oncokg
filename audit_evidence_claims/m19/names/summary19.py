from pathlib import Path
import hashlib,json,socket,subprocess
root=Path.cwd();out=Path(__file__).resolve().parent;prior=root/'audit_evidence_claims/m18/names'
def read(n):return json.loads((out/n).read_text(encoding='utf8'))
def old(n):return json.loads((prior/n).read_text(encoding='utf8'))
qa=read('adapted_frozen_qa_relink_sweep.json')['summary']
assert qa==dict(questions=1648,identical=68,entities_only=1556,semantic_changes=24,errors=0),qa
assert [r['finding'] for r in read('focused_matrix.json') if not r['matches_expectation']]==['M5-S2-known']
assert all(r['status']=='FIXED' for r in read('historical_focus.json')['cases'])
assert all(r['actual_center']==r['expected_center'] for r in read('m11_exact.json'))
c=read('names_m5_summary.json');before={r['input'] for r in old('names_m5_summary.json')['new_lone_alias_refusals']};after={r['input'] for r in c['new_lone_alias_refusals']}
assert before==after and c['aliases_checked']==7511 and c['alias_anomalies']==320 and len(after)==71
assert not read('adapted_names_m5_summary.json')['cache_errors']
(out/'new_alias_losses.json').write_text(json.dumps(dict(description='Current versus M18 raw alias loss set; diagnostic totals, not defect counts',new_losses=sorted(after-before),recovered=sorted(before-after),current_loss_count=len(after),previous_loss_count=len(before)),indent=2),encoding='utf8')
hist=json.loads((root/'audit_evidence_claims/m7/names/names_m5_summary.json').read_text(encoding='utf8'))['new_lone_alias_refusals'];overlap=sorted(after & {r['input'] for r in hist});assert overlap==['Pegylated interferon alfa-2a']
(out/'historical_alias_set_check.json').write_text(json.dumps(dict(original_loss_set=len(hist),still_lost=overlap,all_19_non_M5_S2_restored=True),indent=2),encoding='utf8')
comparison=read('replay_comparison.json');assert not any(r.get('missing') for r in comparison['files'])
changed=[r for r in comparison['files'] if not r['normalized_equal']]
assert not changed,[(r['file'],len(r.get('differences',[]))) for r in changed]
matrix=old('historical_name_dispositions.json')
for row in matrix:
 row['detail']=row['detail'].replace('no new raw-alias loss versus M16','no new raw-alias loss versus M18')
 if 'Fragmented qualifier' in row['finding']:
  row['detail']=row['detail'].replace('Preserved as the previously recorded supplementary gap, not a newly discovered family.','Inherited originator leak; this is not among the user-accepted exceptions.')
# Every M18 exact primary and corroboration before the separate-list controls now refuses.
m18=read('m18_exact/new_results.json')['cases'];by={r['text']:r for r in m18}
primary=['trastuzumab radiolabelled with iodine-124','iodine-124 trastuzumab','trastuzumab iodine-124','trastuzumab labelled-iodine-124','trastuzumab iodinated with iodine-124','trastuzumab radiolabeled with iodine-124','trastuzumab (iodine-124)','trastuzumab [iodine-124]','trastuzumab labelled-iodine_124','trastuzumab labelled-iodine:124','TRASTUZUMAB LABELLED-IODINE-124','trastuzumab labelled with zirconium-89','trastuzumab labelled with copper-64','vinblastine labelled with hydrogen-3','vinblastine labelled with tritium','erlotinib labelled with fluorine-18','paclitaxel labelled with carbon-14']
for text in primary:
 x=by[text]['current'];assert x['map'].get('refused') and not x['map'].get('center'),text;assert not x['trial_qa']['evidence'] and not x['sponsor_qa']['evidence'],text
x=by['cetuximab labelled with yttrium-90']['current'];assert x['map']['center']['id']=='CHEMBL4650364' and any(h['type']=='Refused' for h in x['public_linker']);assert not x['trial_qa']['evidence'] and not x['sponsor_qa']['evidence']
for text in ['trastuzumab radiolabelled with iodine-124, osimertinib','osimertinib, trastuzumab radiolabelled with iodine-124','trastuzumab radiolabelled with iodine-124 and osimertinib','osimertinib and trastuzumab radiolabelled with iodine-124']:
 x=by[text]['current'];assert x['map']['center']['id']=='CHEMBL3353410' and any(h['type']=='Refused' for h in x['public_linker'])
for text in ['trastuzumab','vinblastine','erlotinib','paclitaxel','cetuximab','osimertinib 80 mg','paclitaxel 2 cycles','cisplatin 75 mg/m2 day 1','13-cis retinoic acid','BKM120','AZD9291','NSC-118218H','DX-8951F','GW572016F']:
 x=by[text]['current'];assert x['map'].get('center') and not any(h['type']=='Refused' for h in x['public_linker']),text
for folder,count in [('m17_exact',252),('m18_exact',256)]:
 http=read(folder+'/new_http.json');life=read(folder+'/new_lifecycle.json');assert len(http)==count and all(r['status']==200 for r in http);assert life['port_closed'] and life['database_unchanged'] and life['page_matches_worktree']
matrix.append(dict(round='M18',finding='M18-B1 written-out element name and labelling-word originator leak',status='FIXED',detail='trastuzumab radiolabelled with iodine-124 and 16 original element-name/tritium corroborations now refuse with no centre and zero trial/sponsor evidence. Cetuximab beside yttrium-90 is refused while the separately recognized YTTRIUM Y-90 node survives with zero QA evidence. Separate-list osimertinib, ordinary drug/code/dose controls survive. All 64 original stage cases and 256 original CLI HTTP requests replayed.',evidence='m18_exact/new_results.json'))
for text in ['trastuzumab labelled-I-1-24','trastuzumab labelled-C-1-4','trastuzumab labelled-I 124']:
 x=by[text]['current'];assert x['map'].get('center',{}).get('id')=='CHEMBL1201585' and not any(h['type']=='Refused' for h in x['public_linker']),text
 assert len(x['trial_qa']['evidence'])==len(x['sponsor_qa']['evidence'])==12
 matrix.append(dict(round='M18 supplementary',finding=text,status='NOT FIXED',detail='Exact previously recorded diagnostic still selects TRASTUZUMAB / CHEMBL1201585, 13 map trials, 12/12 trial/sponsor evidence, no public refusal. Split-digit spellings are artificial; whitespace form reflects current symbol-boundary scope. Not a user-accepted exception.',evidence='m18_exact/new_results.json'))
supp={r['text']:r for r in read('m18_exact/labelled_exception_replay.json')['cases']};assert supp['FDG labelled-C-14']['map']['center']['id']=='CHEMBL2030434' and supp['FDG 14C']['map'].get('refused')
matrix.append(dict(round='M18 supplementary',finding='labelled-product isotope compatibility: FDG labelled-C-14 versus FDG 14C',status='NOT FIXED',detail='First form still selects FLUDEOXYGLUCOSE F 18 / CHEMBL2030434 without refusal, while FDG 14C refuses. This is the earlier synthetic isotope-compatibility concern, not evidence that an unlabelled originator was selected; its product identity has not been independently established.',evidence='m18_exact/labelled_exception_replay.json'))
# Set-generated order in the reused alias variant probe is nondeterministic: compare by exact input.
beforev={r['text']:r for r in json.loads((root/'audit_evidence_claims/m18/attacks/alias_variants.json').read_text(encoding='utf8'))};afterv={r['text']:r for r in read('m18_exact/alias_variants.json')};assert beforev.keys()==afterv.keys()
variant_changes=[dict(text=t,before=beforev[t],after=afterv[t]) for t in afterv if (beforev[t].get('center'),bool(beforev[t].get('refused')))!=(afterv[t].get('center'),bool(afterv[t].get('refused')))];assert not variant_changes
(out/'m18_exact/alias_variants_comparison.json').write_text(json.dumps(dict(cases=len(afterv),unique_keys=len({r['key'] for r in afterv.values()}),changes=variant_changes),indent=2),encoding='utf8')
execnames=['round9_execution.json','replay_execution.json','supplement_execution.json','final_replay_execution.json','additional_execution.json','completion_execution.json','remaining_execution.json','m17_execution.json','m19_execution.json'];executions={n:read(n) for n in execnames};assert all(r['exit_code']==0 for rows in executions.values() for r in rows);assert all(r['exit_code']==0 for r in read('m1_exact/execution.json')['scripts'])
manifest=read('reuse_manifest.json');assert all(hashlib.sha256((root/r['source']).read_bytes()).hexdigest()==r['source_sha256'] for r in manifest);assert all(hashlib.sha256((root/r['destination']).read_bytes()).hexdigest()==r['destination_sha256'] for r in manifest)
closed={}
for port in [9110,9111,9112]:
 with socket.socket() as sock:closed[str(port)]=sock.connect_ex(('127.0.0.1',port))!=0
assert all(closed.values())
leafs=sorted(set(r['script'] for rows in executions.values() for r in rows if not Path(r['script']).name.startswith('run_') and r['script']!='compare_replays.py')|{'m1_exact/'+r['script'] for r in read('m1_exact/execution.json')['scripts']}|{'m18_exact/alias_variants.py'})
counts={s:sum(r['status']==s for r in matrix) for s in ['FIXED','NOT FIXED']};head=subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip()
checks=dict(head=head,scripts_reused=len(manifest),executed_reused_leaf_scripts=len(leafs),leaf_scripts=leafs,additional_frozen_input_replay='15 M18 labelled-exception inputs',historical_dispositions=len(matrix),disposition_counts=counts,raw_aliases_checked=7511,raw_alias_differences=320,raw_alias_losses=71,new_alias_losses=[],alias_recoveries=[],frozen_qa=qa,replay_comparison_files=len(comparison['files']),changed_replay_files=[],m17_stage_cases=63,m17_http_requests=252,m18_stage_cases=len(m18),m18_http_requests=256,m18_primary_and_corroborations_checked=len(primary),m18_variant_cases=len(afterv),source_script_hashes_unchanged=True,adapted_script_hashes_match=True,all_execution_exit_codes_zero=True,owned_ports_closed=closed)
(out/'worker_final_checks.json').write_text(json.dumps(checks,indent=2),encoding='utf8');(out/'historical_name_dispositions.json').write_text(json.dumps(matrix,ensure_ascii=False,indent=2),encoding='utf8')
table=['| Round / finding | Status | Fresh evidence |','|---|---|---|']
for r in matrix:table.append('| '+' | '.join(x.replace('|','\\|') for x in [r['round']+' '+r['finding'],'**'+r['status']+'**',r['detail']+' [Evidence]('+r['evidence']+').'])+' |')
(out/'historical_table.md').write_text('\n'.join(table)+'\n',encoding='utf8')
summary=f'''# Round 19 historical name-resolution verification

Reviewed HEAD `{head}`. All exact promoted name-resolution blockers M1 through M18 are **FIXED**. The latest full-element-name/label-word repair passes its original corpus. Earlier supplemental originator leaks remain **NOT FIXED** and are not among the user's accepted exceptions. Exact old reproductions do not establish safety of every spelling.

## Execution

Reused {len(manifest)} original scripts; executed {len(leafs)} reused leaf scripts, plus one 15-input replay reconstructed directly from M18 recorded text fields because no standalone original generator was stored. All executions passed. Source/adapted hashes and changed literals are recorded in [manifest](reuse_manifest.json), [literal checks](adaptation_literal_check.json), [execution checks](worker_final_checks.json), [runner](m19_execution.json). Ports 9110/9111/9112 are closed.

The frozen 7,511-key alias scan has 320 diagnostic differences from its old method and 71 prior-linked aliases without a current Drug; zero new losses or recoveries versus M18. All 19 previously restored non-M5-S2 aliases stay restored. The frozen 1,648-question adapted no-relink comparison is 68 identical / 1,556 metadata-only / 24 semantic / zero errors. These diagnostic counts are not defect counts. The 39-case focused matrix mismatches only accepted M5-S2; all 26 literal M6/M7 controls pass.

All {len(comparison['files'])} inherited evidence files retain identity, map/evidence values and refusal existence against M18 after documented metadata/timing/baseline exclusions. This comparison supports carrying the old exact-input dispositions, not an independent correctness oracle. [Comparison](replay_comparison.json).

M17 63 stage cases and 252 real HTTP requests; M18 64 stage cases and 256 real HTTP requests were replayed. All HTTP requests returned 200, served page bytes matched the worktree, and DB hashes were unchanged. M18 428 alias-variant results across 104 keys also have no change by exact-input comparison. See the lifecycle artifacts in `m17_exact/` and `m18_exact/`.

## Per-finding dispositions

M2 never had a completed report; its partial cases are covered by M2b. DB/UI/server/cost dispositions are separate reviewer contributions. **{len(matrix)} name rows: {counts['FIXED']} FIXED / {counts['NOT FIXED']} NOT FIXED.** NOT FIXED denotes exact reproduction, not an automatic severity assignment.

'''
summary+='\n'.join(table)
summary+='''

## Interpretation and limits

`b.i.o.similar bevacizumab` and `lip.osomal doxorubicin` remain originator maps with 12/12 and 3/3 QA rows respectively, without refusal. The M18 split-digit and whitespace-symbol residuals also remain exact-originator selections; they are individually tabulated. None of these is an explicitly accepted user exception. The parent reviewer owns approval-bar adjudication. Lowercase-ID/investigator lookup, prefixed comma-name QA, reverse qualifier scope and slash PET/CT failure presentation also remain individually NOT FIXED.

Known named over-refusals and the ChEMBL development-code synonym limitation are preserved as nonblockers per user instruction. The 15-input labelled-product supplement is an isotope-compatibility diagnostic, not proof of an unlabelled-originator error. The raw intervention resolver still need not refuse the latest input for the public linker/map to refuse it; guarantees concern the full path.

Seven original QA demos retain 12, 12, 11, 1, 12, 0, 0 evidence rows. Six responses equal the bfcb83d-linker comparison; Mvasi differs in refusal metadata. Historical counterfactuals replace only the stated method/module against current app/data, not whole historical deployments. Mutation fixtures use in-memory copies. No model is called.

All new scratch files and temp paths are under `m19/names`; bytecode is disabled. No tracked source was modified. Prior report inventory is [recorded](historical_report_inventory.json).
'''
(out/'FINDINGS.md').write_text(summary,encoding='utf8');print(json.dumps(checks,indent=2))

