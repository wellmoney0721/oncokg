"""Focused paired controls for R6 docs findings."""
import sys,json
from pathlib import Path
from dataclasses import asdict
sys.dont_write_bytecode=True
sys.stdout.reconfigure(encoding='utf-8')
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'src'))
from app import Engine
Q={2:'What trials evaluate Tagrisso?',3:'What does osimertinib target?',4:'Which drugs act on ALK?'}
C=[
('kind_as_bare',2,'Osimertinib is a clinical trial.'),
('kind_as_listed',2,'Osimertinib is listed as a clinical trial.'),
('kind_as_recorded',2,'Osimertinib is recorded as a clinical trial.'),
('kind_as_include',2,'The graph includes osimertinib as a clinical trial.'),
('kind_as_lists',2,'The graph lists osimertinib as a clinical trial.'),
('kind_as_true',2,'NCT07680790 is listed as a clinical trial.'),
('kind_as_drug_true',2,'Osimertinib is listed as a drug in clinical trials.'),
('kind_as_context_absent',3,'Osimertinib is listed as a clinical trial.'),
('kind_as_singular',2,'Osimertinib is listed as a trial.'),
('kind_as_safe',2,'Osimertinib is listed as a safe clinical trial.'),
('inverse_as_min',3,'EGFR is listed as an inhibitor of osimertinib.'),
('inverse_as_copula',3,'EGFR is an inhibitor of osimertinib.'),
('inverse_as_record',3,'The graph records EGFR as an inhibitor of osimertinib.'),
('inverse_as_true',3,'The graph records osimertinib as an inhibitor of EGFR.'),
('inverse_as_drug',3,'EGFR is listed as a drug inhibiting osimertinib.'),
('inverse_as_wrong_action',3,'EGFR is listed as an activator of osimertinib.'),
('inverse_as_target',4,'ALK is listed as an inhibitor of lorlatinib and crizotinib.'),
('inverse_as_target_true',4,'Lorlatinib and crizotinib are listed as inhibitors of ALK.'),
('fp_noun_canonical',3,'Inhibitors of EGFR include osimertinib.'),
('fp_noun_adjective',3,'EGFR inhibitors include osimertinib.'),
('fp_noun_lower',3,'The recorded mechanism is inhibition of EGFR by osimertinib.'),
('fp_noun_sentence',3,'Inhibition of EGFR by osimertinib is recorded.'),
('fp_phase_label',2,'NCT03909334 evaluates osimertinib; phase: 2; status: active, not recruiting.'),
('fp_group_approval',4,'Lorlatinib, crizotinib and alectinib are approved ALK inhibitors.'),
('fp_group_approval_split',4,'Lorlatinib, crizotinib and alectinib inhibit ALK. They are approved.'),
]
E=Engine();rows=[]
for ident,q,a in C:
 es=E.kg.link_entities(Q[q]);ev=E.kg.retrieve(E.kg.classify(Q[q],es),es);r=E.check(Q[q],a)
 rows.append(dict(id=ident,question=Q[q],answer=a,result=r,full_evidence=[asdict(x) for x in ev]))
 print(ident,r['checks']['grounded'],[(x['kind'],x['value']) for x in r['checks']['unsupported_claims']])
(Path(__file__).parent/'docs6_controls_results.json').write_text(json.dumps(rows,indent=2,ensure_ascii=False),encoding='utf8')
