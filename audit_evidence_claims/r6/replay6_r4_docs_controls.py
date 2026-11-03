import sys,json
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path.cwd();sys.path.insert(0,str(ROOT/'src'))
from app import Engine
from dataclasses import asdict
from claims import _strip_citations
x=Engine(); kg=x.kg
Q={1:'Which companies are developing osimertinib?',2:'What trials evaluate Tagrisso?',3:'What does osimertinib target?',4:'Which drugs act on ALK?',5:'What is AstraZeneca running in NSCLC?',6:'What is the capital of France?'}
cases=[
('head_control_safe',3,'Safe drugs:\n- OSIMERTINIB acts on EGFR (inhibitor).'),
('head_control_discontinued',3,'Discontinued drugs:\n- OSIMERTINIB acts on EGFR (inhibitor).'),
('head_control_kind',3,'The following drugs:\n- OSIMERTINIB acts on EGFR (inhibitor).'),
('head_terminated',2,'The following terminated trials:\n- NCT07680790 (PHASE3, RECRUITING) evaluates OSIMERTINIB.'),
('head_safe_explicit',3,'These safe drugs:\n- Osimertinib'),
('head_wrong_entity',3,'EGFR drugs:\n- OSIMERTINIB acts on EGFR (inhibitor).'),
('head_wrong_entity_pron',3,'Drugs for ALK:\n- OSIMERTINIB acts on EGFR (inhibitor).'),
('kind_control_target',3,'EGFR is a drug.'),
('kind_control_trial',4,'PLB1003 is in clinical trials.'),
('kind_target_nonrelation',3,'Osimertinib and EGFR are drugs.'),
('kind_company_control',5,'AstraZeneca is a drug.'),
('kind_faithful',3,'Osimertinib is a drug that inhibits EGFR.'),
('kind_trial_faithful',4,'Lorlatinib is in NSCLC trials.'),
('kind_trial_faithful_clinical',4,'Lorlatinib is in clinical trials.'),
('identity_control',4,'PLB1003 is LORLATINIB.'),
('identity_relation',4,'PLB1003 is lorlatinib, an ALK inhibitor.'),
('identity_same',3,'Osimertinib is Tagrisso.'),
('cite_valid',3,'Osimertinib acts on EGFR [CHEMBL3353410].'),
('cite_valid_list',3,'Osimertinib acts on EGFR [CHEMBL3353410, ENSG00000146648].'),
('cite_valid_space',3,'Osimertinib acts on EGFR [CHEMBL3353410 ENSG00000146648].'),
('cite_invalid_org',3,'Osimertinib [ORG:is-safe] acts on EGFR.'),
('cite_mixed_known_unknown',3,'Osimertinib [CHEMBL3353410, ORG:is-safe] acts on EGFR.'),
('cite_valid_claim',3,'Osimertinib is safe [CHEMBL3353410].'),
('cite_nonid',3,'Osimertinib [is safe] acts on EGFR.'),
('approve_nsclc',4,'Lorlatinib is approved in NSCLC.'),
('approve_nsclc_trial',4,'Lorlatinib is approved for NSCLC trials.'),
('approve_lung',4,'Lorlatinib is approved for lung cancer.'),
('approve_control',4,'Lorlatinib is approved.'),
('clinical_nonspecific',2,'Osimertinib is a clinical trial evaluated in NCT07680790.'),
('clinical_nonspecific_faithful',2,'Osimertinib is evaluated in the clinical trial NCT07680790.'),
]
rows=[]
for ident,q,a in cases:
 r=x.check(Q[q],a); en=kg.link_entities(Q[q]); ev=kg.retrieve(kg.classify(Q[q],en),en)
 rows.append(dict(id=ident,question=Q[q],answer=a,result=r,full_evidence=[asdict(e) for e in ev]))
 print(ident,r['checks']['grounded'],[(f['kind'],f['value']) for f in r['checks']['unsupported_claims']])
Path('audit_evidence_claims/r6/replay6_r4_docs_controls_results.json').write_text(json.dumps(rows,indent=2,ensure_ascii=False),encoding='utf-8')
