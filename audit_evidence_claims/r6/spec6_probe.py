import sys,json
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'src'))
from app import Engine
e=Engine()
Q={1:'Which companies are developing osimertinib?',2:'What trials evaluate Tagrisso?',3:'What does osimertinib target?',4:'Which drugs act on ALK?',5:'What is AstraZeneca running in NSCLC?'}
cases=[
('mixed_trial_group',2,'NCT07680790 and osimertinib are clinical trials.'),
('mixed_trial_group_reverse',2,'Osimertinib and NCT07680790 are clinical trials.'),
('mixed_trial_heading',2,'These clinical trials:\n- NCT07680790 and osimertinib'),
('trial_among',2,'Osimertinib is among the clinical trials.'),
('trial_kind_of',2,'Osimertinib is a trial of NCT07680790.'),
('kind_group_drug',3,'Osimertinib and EGFR are drugs.'),
('kind_group_drug_reverse',3,'EGFR and osimertinib are drugs.'),
('kind_group_heading',3,'These drugs:\n- Osimertinib and EGFR'),
('kind_relative_owner',3,'Osimertinib inhibits EGFR, which is a drug.'),
('kind_relative_owner_target',3,'EGFR is inhibited by osimertinib, which is a company.'),
('kind_relative_control',3,'EGFR is inhibited by osimertinib, which is a drug.'),
('kind_include_wrong',3,'Drugs include osimertinib and EGFR.'),
('kind_include_right',3,'Drugs include osimertinib.'),
('kind_reversed_relative',3,'Osimertinib, whose target is EGFR, is a drug.'),
('kind_as_company',3,'Osimertinib acts on EGFR as a company.'),
('kind_parenthetic',3,'Osimertinib (a company) inhibits EGFR.'),
('group_clinical_by',4,'LORLATINIB is in clinical trials with PLB1003.'),
('group_nsclc_by',4,'LORLATINIB is in NSCLC trials with PLB1003.'),
('group_clinical_like',4,'Clinical trials include lorlatinib and PLB1003.'),
('group_clinical_reversed',4,'Clinical trials include PLB1003 and lorlatinib.'),
('group_clinical_single',4,'Clinical trials include PLB1003.'),
('group_clinical_header',4,'These clinical trials include:\n- LORLATINIB and PLB1003'),
('group_approval_record',4,'The graph records lorlatinib and PLB1003 as approved drugs.'),
('group_clinical_record',4,'The graph records lorlatinib and PLB1003 in clinical trials.'),
('group_clinical_record_reverse',4,'The graph records PLB1003 and lorlatinib in clinical trials.'),
('group_nsclc_record',4,'The graph records lorlatinib and PLB1003 in NSCLC trials.'),
('group_nsclc_record_bare',4,'The graph records NSCLC trials of lorlatinib and PLB1003.'),
('group_clinical_it',4,'Clinical trials include LORLATINIB and PLB1003. It is approved.'),
('noun_include_correct',3,'Inhibitors of EGFR include osimertinib.'),
('noun_include_wrong',3,'Inhibitors of osimertinib include EGFR.'),
('noun_by_correct',3,'Inhibition of EGFR by osimertinib is recorded.'),
('noun_by_wrong',3,'Inhibition of osimertinib by EGFR is recorded.'),
('as_noun_bad_owner',3,'EGFR is inhibited by osimertinib as an inhibitor.'),
('as_noun_is',3,'EGFR is recorded as an inhibitor of osimertinib.'),
('as_noun_is_control',3,'Osimertinib is recorded as an inhibitor of EGFR.'),
('as_noun_bad_action',3,'Osimertinib acts on EGFR as an activator.'),
('identity_records',3,'Osimertinib records EGFR.'),
('identity_includes',3,'Osimertinib includes EGFR.'),
('identity_has',3,'Osimertinib has EGFR.'),
('identity_be_rel',3,'Osimertinib is EGFR and acts on EGFR.'),
('identity_be_embedded',3,'Osimertinib, an inhibitor of EGFR, is EGFR.'),
('identity_be_type',3,'Osimertinib is EGFR, an inhibitor.'),
('kind_header_drug_item_sentence',3,'These drugs:\n- EGFR is inhibited by osimertinib.'),
('kind_header_company_item_sentence',3,'These companies:\n- Osimertinib inhibits EGFR.'),
('kind_header_2entities',3,'The following drugs inhibit EGFR:\n- EGFR and osimertinib'),
]
out=[]
for id,q,a in cases:
 r=e.check(Q[q],a)
 ee=e.kg.retrieve(r['intent'],r['entities'])
 out.append(dict(id=id,question=Q[q],answer=a,**r,full_evidence=[dict(statement=x.statement,relation=x.relation,source_record=x.source_record) for x in ee]))
 print(id,r['checks']['grounded'],[(f['kind'],f['value']) for f in r['checks']['unsupported_claims']])
(Path(__file__).parent/'spec6_probe.json').write_text(json.dumps(out,indent=2,ensure_ascii=False),encoding='utf8')
