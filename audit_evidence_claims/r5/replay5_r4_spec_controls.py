from pathlib import Path
exec(Path('audit_evidence_claims/r5/replay5_r4_spec_probe.py').read_text(encoding='utf-8-sig').split('rows=[]')[0])
cases=[
('count_label_correct_for_carbo_only','Q5','AstraZeneca sponsors carboplatin in trials: 10.'),
('count_label_group_14','Q5','AstraZeneca sponsors osimertinib and carboplatin in trials: 14.'),
('count_standard_group_10','Q5','AstraZeneca sponsors osimertinib and carboplatin in 10 trials.'),
('count_separate_faithful','Q5','AstraZeneca sponsors 14 trials of osimertinib and 10 trials of carboplatin.'),
('count_alias_control','Q5','AstraZeneca sponsors 14 trials of osimertinib.'),
('phase_list_faithful','Q2','Phase 3 trials evaluating osimertinib include NCT07680790 and NCT02411448.'),
('status_list_faithful','Q2','Recruiting trials evaluating osimertinib include NCT07680790 and NCT07738172.'),
('status_individual_wrong','Q2','NCT03909334 is a recruiting trial of osimertinib.'),
('phase_individual_wrong','Q2','NCT03909334 is a phase 3 trial of osimertinib.'),
('trial_of_wrong_drug','Q2','NCT03909334 is a trial of carboplatin.'),
('trial_list_wrong_drug','Q2','Trials evaluating carboplatin include NCT03909334 and NCT07680790.'),
('clinical_0_only','Q4','PLB1003 has clinical trials.'),
('clinical_supported','Q4','LORLATINIB acts on ALK in clinical trials.'),
('status_faithful_split','Q2','NCT07680790 is recruiting. NCT07738172 is recruiting.'),
('phase_faithful_split','Q2','NCT07680790 is phase 3. NCT02411448 is phase 3.'),
('approval_faithful_split','Q4','LORLATINIB is approved. CRIZOTINIB is approved.'),
]
rows=[]
for ident,q,a in cases:
 r=E.check(Q[q],a); rows.append(dict(id=ident,question=Q[q],answer=a,result=r))
 print(ident,r['checks']['grounded'],[(x['kind'],x['value']) for x in r['checks']['unsupported_claims']])
Path('audit_evidence_claims/r5/replay5_r4_spec_controls.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
