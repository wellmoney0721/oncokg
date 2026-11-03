import sys,json
from pathlib import Path
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path.cwd()/'src'))
from app import Engine
E=Engine()
Q={'Q1':'Which companies are developing osimertinib?','Q2':'What trials evaluate Tagrisso?','Q3':'What does osimertinib target?','Q4':'Which drugs act on ALK?','Q5':'What is AstraZeneca running in NSCLC?'}
cases=[
('plural_chain','Q4','PLB1003 and LORLATINIB act on ALK. They act on ALK. They are approved.'),
('plural_chain_reverse','Q4','LORLATINIB and PLB1003 act on ALK. They act on ALK. They are approved.'),
('object_plural_count','Q5','AstraZeneca sponsors osimertinib and carboplatin. It sponsors them in 10 trials.'),
('status_group','Q2','NCT03909334 and NCT07680790 are recruiting.'),
('status_group_reverse','Q2','NCT07680790 and NCT03909334 are active, not recruiting.'),
('phase_group','Q2','NCT03909334 and NCT07680790 are phase 3.'),
('phase_group_reverse','Q2','NCT07680790 and NCT03909334 are phase 2.'),
('status_object','Q2','NCT03909334 evaluates osimertinib and NCT07680790 is recruiting.'),
('trial_include_faithful','Q2','Trials evaluating osimertinib include NCT03909334 and NCT07680790.'),
('trial_of_faithful','Q2','NCT03909334 is a phase 2 trial of osimertinib.'),
('trial_of_reversed','Q2','Osimertinib is a trial of NCT03909334.'),
]
rows=[]
for ident,q,a in cases:
 r=E.check(Q[q],a)
 rows.append(dict(id=ident,question=Q[q],answer=a,result=r))
 print(ident,r['checks']['grounded'],[(x['kind'],x['value']) for x in r['checks']['unsupported_claims']])
Path('audit_evidence_claims/r5/replay5_r4_spec_probe.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
