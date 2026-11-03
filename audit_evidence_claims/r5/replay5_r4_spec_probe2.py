from pathlib import Path
exec(Path('audit_evidence_claims/r5/replay5_r4_spec_probe.py').read_text(encoding='utf-8-sig').split('rows=[]')[0])
cases=[
('plural_chain_low','Q4','PLB1003 and LORLATINIB act on ALK. they act on ALK. they are approved.'),
('plural_chain_lowreverse','Q4','LORLATINIB and PLB1003 act on ALK. they act on ALK. they are approved.'),
('status_group_trialof','Q2','NCT03909334 and NCT07680790 are recruiting trials of osimertinib.'),
('phase_group_trialof','Q2','NCT03909334 and NCT07680790 are phase 3 trials of osimertinib.'),
('status_group_eval','Q2','NCT03909334 and NCT07680790 are recruiting and evaluate osimertinib.'),
('status_group_evalafter','Q2','NCT03909334 and NCT07680790 evaluate osimertinib and are recruiting.'),
('status_group_evalafter_rev','Q2','NCT07680790 and NCT03909334 evaluate osimertinib and are recruiting.'),
('phase_group_evalafter_rev','Q2','NCT07680790 and NCT03909334 evaluate osimertinib and are phase 3.'),
('count_object_plural_sentence','Q5','AstraZeneca sponsors osimertinib and carboplatin. AstraZeneca sponsors them in 10 trials.'),
('count_object_plural_singular','Q5','AstraZeneca sponsors osimertinib and carboplatin. It sponsors osimertinib in 10 trials.'),
('count_label_shared','Q5','AstraZeneca sponsors osimertinib and carboplatin; trials: 10.'),
('count_label_shared_same','Q5','AstraZeneca sponsors osimertinib and carboplatin in trials: 10.'),
]
rows=[]
for ident,q,a in cases:
 r=E.check(Q[q],a)
 rows.append(dict(id=ident,question=Q[q],answer=a,result=r))
 print(ident,r['checks']['grounded'],[(x['kind'],x['value']) for x in r['checks']['unsupported_claims']])
Path('audit_evidence_claims/r5/replay5_r4_spec_probe2.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
for q in ['Q2','Q4','Q5']:
 en=E.kg.link_entities(Q[q]); ev=E.kg.retrieve(E.kg.classify(Q[q],en),en)
 print(q,[e.statement for e in ev])

