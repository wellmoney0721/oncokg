import json
import sys
from dataclasses import asdict
from pathlib import Path
sys.dont_write_bytecode = True
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'src'))
from app import Engine
engine=Engine()
Q={1:'Which companies are developing osimertinib?',2:'What trials evaluate Tagrisso?',3:'What does osimertinib target?',4:'Which drugs act on ALK?',5:'What is AstraZeneca running in NSCLC?'}
cases=[
('kind_prefix_target',3,'The drug EGFR is inhibited by osimertinib.'),
('kind_suffix_target_control',3,'EGFR is a drug inhibited by osimertinib.'),
('kind_no_kind_control',3,'EGFR is inhibited by osimertinib.'),
('kind_prefix_drug_faithful',3,'The drug osimertinib inhibits EGFR.'),
('kind_prefix_company',5,'The drug AstraZeneca sponsors osimertinib.'),
('kind_prefix_company_control',5,'AstraZeneca is a drug and sponsors osimertinib.'),
('kind_prefix_drug_as_company',5,'The company osimertinib is sponsored by AstraZeneca.'),
('trial_identity',2,'Osimertinib is a clinical trial.'),
('trial_identity_noclinical',2,'Osimertinib is a trial.'),
('trial_context_faithful',2,'Osimertinib is in clinical trials.'),
('trial_identity_no_trial_evidence',3,'Osimertinib is a clinical trial.'),
('trial_subject_faithful',2,'NCT07680790 is a clinical trial.'),
('trial_identity_drugs_both',2,'Tagrisso is a clinical trial.'),
('faithful_pronoun',1,'AstraZeneca sponsors 14 trials of osimertinib. Bristol Myers Squibb sponsors 2 trials of it.'),
('faithful_pronoun_explicit',1,'AstraZeneca sponsors 14 trials of osimertinib. Bristol Myers Squibb sponsors 2 trials of osimertinib.'),
('faithful_graph_counts',4,'The graph records 13 NSCLC trials of lorlatinib and 15 NSCLC trials of crizotinib.'),
('faithful_graph_counts_separate',4,'The graph records 13 NSCLC trials of lorlatinib. The graph records 15 NSCLC trials of crizotinib.'),
('faithful_passive_kind',3,'EGFR is inhibited by the drug osimertinib.'),
('faithful_passive_nokind',3,'EGFR is inhibited by osimertinib.'),
('faithful_status_but',2,'NCT03909334 is active but not recruiting.'),
('faithful_status_comma',2,'NCT03909334 is active, not recruiting.'),
('letters_comma_negation',3,'Osimertinib does N, O, T inhibit EGFR.'),
('letters_space_negation',3,'Osimertinib does N O T inhibit EGFR.'),
('letters_comma_safe',3,'Osimertinib is S, A, F, E.'),
('letters_space_safe',3,'Osimertinib is S A F E.'),
]
rows=[]
for ident,q,a in cases:
 r=engine.check(Q[q],a)
 e=engine.kg.link_entities(Q[q]); ev=engine.kg.retrieve(engine.kg.classify(Q[q],e),e)
 rows.append(dict(id=ident,question=Q[q],answer=a,result=r,full_evidence=[asdict(x) for x in ev]))
 print(ident,r['checks']['grounded'],[(u['kind'],u['value']) for u in r['checks']['unsupported_claims']])
(ROOT/'audit_evidence_claims/r5_recheck/docs5_controls_results.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
