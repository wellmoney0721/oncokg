from pathlib import Path
exec(Path('audit_evidence_claims/r5/replay5_r4_spec_probe.py').read_text(encoding='utf-8-sig').split('rows=[]')[0])
cases=[
('status_list_prefix','Q2','Recruiting trials evaluating osimertinib include NCT07680790 and NCT03909334.'),
('phase_list_prefix','Q2','Phase 3 trials evaluating osimertinib include NCT07680790 and NCT03909334.'),
('status_list_prefix_control','Q2','Recruiting trials evaluating osimertinib include NCT03909334 and NCT07680790.'),
('phase_list_prefix_control','Q2','Phase 3 trials evaluating osimertinib include NCT03909334 and NCT07680790.'),
('faithful_phase_coord','Q2','NCT07680790 and NCT02411448 are phase 3.'),
('faithful_status_coord','Q2','NCT07680790 and NCT07738172 are recruiting.'),
('faithful_approval_coord','Q4','LORLATINIB and CRIZOTINIB are approved.'),
('faithful_count_alias','Q5','AstraZeneca sponsors 14 trials of osimertinib (Tagrisso).'),
('nsclc_target_pool','Q4','PLB1003 acts on ALK in NSCLC trials.'),
('clinical_target_pool','Q4','PLB1003 acts on ALK in clinical trials.'),
('clinical_target_pool_noedge','Q4','PLB1003 has clinical trials.'),
('trialcount_subjectgroup','Q5','AstraZeneca sponsors osimertinib and carboplatin in clinical trials: 10.'),
('object_plural_then_repeat','Q5','AstraZeneca sponsors osimertinib and carboplatin. It sponsors them. They have 10 trials.'),
('it_object_singular_good','Q3','Osimertinib acts on EGFR. Osimertinib inhibits it.'),
('it_object_singular_cross','Q4','PLB1003 and LORLATINIB act on ALK. It is approved.'),
]
rows=[]
for ident,q,a in cases:
 r=E.check(Q[q],a); rows.append(dict(id=ident,question=Q[q],answer=a,result=r))
 print(ident,r['checks']['grounded'],[(x['kind'],x['value']) for x in r['checks']['unsupported_claims']])
Path('audit_evidence_claims/r5/replay5_r4_spec_probe3.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
