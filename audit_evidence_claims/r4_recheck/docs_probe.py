import sys,json
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path.cwd();sys.path.insert(0,str(ROOT/'src'))
from app import Engine
from dataclasses import asdict
x=Engine(); kg=x.kg
Q={1:'Which companies are developing osimertinib?',2:'What trials evaluate Tagrisso?',3:'What does osimertinib target?',4:'Which drugs act on ALK?',5:'What is AstraZeneca running in NSCLC?',6:'What is the capital of France?'}
cases=[
('kind_trial_borrow',4,'PLB1003 inhibits ALK in clinical trials.'),
('kind_trial_borrow2',4,'PLB1003 inhibits ALK in NSCLC trials.'),
('kind_drug_target',3,'EGFR is a drug inhibited by osimertinib.'),
('kind_company_drug',5,'AstraZeneca is a drug sponsoring trials of osimertinib.'),
('kind_drug_company',5,'Osimertinib is a company sponsored by AstraZeneca.'),
('head_safe',3,'The following safe drugs:\n- OSIMERTINIB acts on EGFR (inhibitor).'),
('head_discontinued',3,'The following discontinued drugs:\n- OSIMERTINIB acts on EGFR (inhibitor).'),
('head_noninhibitor',3,'These noninhibitor drugs:\n- OSIMERTINIB acts on EGFR (inhibitor).'),
('head_safe_notcopied',3,'The following safe drugs:\n- Osimertinib inhibits EGFR.'),
('head_safe_bare',3,'The following safe drugs:\n- Osimertinib'),
('head_non',3,'These non-inhibitor drugs:\n- OSIMERTINIB acts on EGFR (inhibitor).'),
('head_no_trials',4,'The following clinical trials:\n- PLB1003 acts on ALK (inhibitor); max stage PHASE_1; 0 NSCLC trial(s) in this graph.'),
]
rows=[]
for ident,q,a in cases:
 r=x.check(Q[q],a); en=kg.link_entities(Q[q]); ev=kg.retrieve(kg.classify(Q[q],en),en)
 rows.append(dict(id=ident,question=Q[q],answer=a,result=r,full_evidence=[asdict(e) for e in ev]))
 print(ident,r['checks']['grounded'],[(f['kind'],f['value']) for f in r['checks']['unsupported_claims']])
Path('audit_evidence_claims/r4_recheck/docs_probe_results.json').write_text(json.dumps(rows,indent=2,ensure_ascii=False),encoding='utf-8')
