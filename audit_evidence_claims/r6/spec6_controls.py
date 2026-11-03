import sys,json
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'src'))
from app import Engine
from claims import _tokenise,_clauses,_units,_join
e=Engine()
Q={1:'Which companies are developing osimertinib?',2:'What trials evaluate Tagrisso?',3:'What does osimertinib target?',4:'Which drugs act on ALK?',5:'What is AstraZeneca running in NSCLC?'}
cases=[
('relative_wrong_kind',3,'Osimertinib inhibits EGFR, which is a drug.'),
('relative_wrong_explicit',3,'Osimertinib inhibits EGFR. EGFR is a drug.'),
('relative_right_kind',3,'EGFR is inhibited by osimertinib, which is a drug.'),
('relative_right_explicit',3,'EGFR is inhibited by osimertinib. Osimertinib is a drug.'),
('relative_r5_wrong',3,'EGFR, which is inhibited by osimertinib, is a drug.'),
('relative_r5_right',3,'Osimertinib, which inhibits EGFR, is a drug.'),
('mixed_drug_wrong',3,'Osimertinib and EGFR are drugs.'),
('mixed_drug_reverse',3,'EGFR and osimertinib are drugs.'),
('mixed_drug_faithful',4,'LORLATINIB and PLB1003 are drugs.'),
('mixed_trial_wrong',2,'NCT07680790 and osimertinib are clinical trials.'),
('mixed_trial_reverse',2,'Osimertinib and NCT07680790 are clinical trials.'),
('mixed_trial_faithful',2,'NCT07680790 and NCT03909334 are clinical trials.'),
('record_group_wrong',4,'The graph records lorlatinib and PLB1003 in clinical trials.'),
('record_group_reverse',4,'The graph records PLB1003 and lorlatinib in clinical trials.'),
('record_group_faithful',4,'The graph records lorlatinib and crizotinib in clinical trials.'),
('record_group_one_wrong',4,'The graph records PLB1003 in clinical trials.'),
('record_group_nsclc',4,'The graph records NSCLC trials of lorlatinib and PLB1003.'),
('record_group_nsclc_reverse',4,'The graph records NSCLC trials of PLB1003 and lorlatinib.'),
('record_group_nsclc_faithful',4,'The graph records NSCLC trials of lorlatinib and crizotinib.'),
('include_group_wrong',4,'The graph includes lorlatinib and PLB1003 in clinical trials.'),
('include_group_reverse',4,'The graph includes PLB1003 and lorlatinib in clinical trials.'),
('heading_drug_wrong',3,'These drugs:\n- EGFR is inhibited by osimertinib.'),
('heading_drug_explicit',3,'EGFR is a drug inhibited by osimertinib.'),
('heading_drug_faithful',3,'These drugs:\n- Osimertinib inhibits EGFR.'),
('heading_clinical_wrong',2,'These clinical trials:\n- Osimertinib is evaluated in NCT07680790.'),
('heading_clinical_explicit',2,'Osimertinib is a clinical trial.'),
('heading_clinical_faithful',2,'These clinical trials:\n- NCT07680790 evaluates osimertinib.'),
('noun_include_faithful_capitalized',3,'Inhibitors of EGFR include osimertinib.'),
('noun_include_faithful_article',3,'The inhibitors of EGFR include osimertinib.'),
('noun_by_faithful_capitalized',3,'Inhibition of EGFR by osimertinib is recorded.'),
('noun_by_faithful_article',3,'The inhibition of EGFR by osimertinib is recorded.'),
('noun_include_unsupported',3,'The inhibitors of osimertinib include EGFR.'),
('noun_by_unsupported',3,'The inhibition of osimertinib by EGFR is recorded.'),
('as_inhibitor_reversal',3,'EGFR is recorded as an inhibitor of osimertinib.'),
('as_inhibitor_faithful',3,'Osimertinib is recorded as an inhibitor of EGFR.'),
('as_inhibitor_wrong_action',3,'Osimertinib acts on EGFR as an activator.'),
('as_inhibitor_wrong_word',3,'Osimertinib acts on EGFR as a safe inhibitor.'),
]
out=[]
for id,q,a in cases:
 r=e.check(Q[q],a)
 ee=e.kg.retrieve(r['intent'],r['entities'])
 units=[]
 for u in _units(a):
  unit=_join(u['text'].rstrip('.'),u['heading']) if u.get('heading') else u['text']
  toks,ents=_tokenise(unit,e.kg.link_entities)
  units.append(dict(text=unit,tokens=toks,entities=ents,clauses=_clauses(toks)))
 out.append(dict(id=id,question=Q[q],answer=a,**r,full_evidence=[dict(statement=x.statement,relation=x.relation,source_record=x.source_record) for x in ee],units=units))
 print(id,r['checks']['grounded'],[(f['kind'],f['value']) for f in r['checks']['unsupported_claims']])
(Path(__file__).parent/'spec6_controls.json').write_text(json.dumps(out,indent=2,ensure_ascii=False),encoding='utf8')
