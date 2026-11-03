import json, sys
from pathlib import Path
from dataclasses import asdict
sys.dont_write_bytecode = True
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'src'))
from app import Engine
from claims import _units, _tokenise, _clauses
e=Engine(); kg=e.kg
Q2='What trials evaluate Tagrisso?'
Q3='What does osimertinib target?'
Q4='Which drugs act on ALK?'
Q5='What is AstraZeneca running in NSCLC?'
QT=[Q3,'What does crizotinib target?']
rows=[]
def run(ident,qs,answer):
    if isinstance(qs,str): qs=[qs]
    entities=[]; ev=[]
    for q in qs:
        en=kg.link_entities(q); entities.extend(en)
        ev.extend(kg.retrieve(kg.classify(q,en),en))
    r=kg.check_groundedness(answer,ev,entities,True,set(kg.dic['index']),linker=kg.link_entities)
    rows.append(dict(id=ident,questions=qs,answer=answer,checks=r,evidence=[asdict(x) for x in ev],units=_units(answer)))
    print(ident,r['grounded'],[(f['kind'],f['value']) for f in r['unsupported_claims']])

CASES=[
('pronoun_stale',QT,'Osimertinib acts on EGFR. Crizotinib acts on ALK and it inhibits EGFR.'),
('pronoun_stale2',QT,'Osimertinib acts on EGFR. Crizotinib acts on ALK while this drug inhibits EGFR.'),
('pronoun_fresh',QT,'Osimertinib acts on EGFR. Crizotinib acts on ALK. It inhibits EGFR.'),
('pronoun_inline',QT,'Osimertinib acts on EGFR and it inhibits ALK.'),
('elided',QT,'Osimertinib acts on EGFR. Crizotinib acts on ALK and inhibits EGFR.'),
('count_phase',Q2,'Osimertinib has 3 trials.'),
('count_phase2',Q2,'Osimertinib has 2 trials.'),
('count_trial',Q2,'NCT03909334 has 2 trials.'),
('count_plb',Q4,'PLB1003 has 1 NSCLC trials.'),
('phase_count',Q5,'Osimertinib is phase 14.'),
('phase_sandwich',Q2,'NCT03909334 evaluates phase 3 osimertinib.'),
('number_sandwich',Q5,'AstraZeneca sponsors osimertinib in 10 trials and carboplatin.'),
('number_drug_other',Q5,'AstraZeneca sponsors osimertinib in 10 trials with carboplatin.'),
('number_group',Q5,'AstraZeneca sponsors 10 trials of osimertinib and carboplatin.'),
('noun_target',Q3,'The target of EGFR is osimertinib.'),
('noun_inhibitor',Q3,'EGFR is an inhibitor of osimertinib.'),
('noun_mid',Q3,'EGFR is the target and inhibitor of osimertinib.'),
('passive_back',Q3,'Osimertinib is inhibited by EGFR.'),
('passive_long',Q3,'EGFR is a target inhibited by osimertinib.'),
('passive_active',Q3,'EGFR was inhibited osimertinib.'),
('passive_was',Q3,'EGFR was and inhibited osimertinib.'),
('split_relative',QT,'Osimertinib acts on EGFR which crizotinib inhibits.'),
('split_switch',QT,'Osimertinib acts on EGFR, and crizotinib on ALK.'),
('split_bad_switch',QT,'Osimertinib acts on ALK, and crizotinib on EGFR.'),
('split_or',QT,'Osimertinib acts on ALK or crizotinib acts on EGFR.'),
('split_neither',QT,'Osimertinib acts on EGFR; crizotinib on EGFR.'),
('split_fragment',QT,'Crizotinib acts on ALK. On EGFR.'),
('scope_clinical',Q3,'Osimertinib is for lung cancer.'),
('scope_empty',Q3,'Lung cancer.'),
('passive_cleft',Q3,'EGFR is what inhibited osimertinib.'),
('passive_cleft_target',Q3,'EGFR is what targeted osimertinib.'),
('passive_cleft_trial',Q2,'Osimertinib is what evaluated NCT03909334.'),
('passive_cleft_sponsor',Q5,'Osimertinib is what sponsored AstraZeneca.'),
('noun_wrong_possessive',Q3,"EGFR is osimertinib's inhibitor."),
('noun_correct_possessive',Q3,"Osimertinib is EGFR's inhibitor."),
('noun_wrong_ofby',Q3,'The inhibition of osimertinib by EGFR.'),
('noun_correct_ofby',Q3,'The inhibition of EGFR by osimertinib.'),
('elided_target',QT,'Osimertinib acts on EGFR; crizotinib on EGFR.'),
('elided_trial',[Q2,'What trials evaluate crizotinib?'],'NCT03909334 evaluates osimertinib; NCT06254599 crizotinib; NCT03909334 crizotinib.'),
('elided_same',QT,'Crizotinib acts on ALK and on EGFR.'),
('elided_semicolon',QT,'Crizotinib acts on ALK; on EGFR.'),
('count_morph',Q4,'PLB1003 has 1 clinical trial.'),
('count_with',Q5,'AstraZeneca sponsors osimertinib in 10 trials with carboplatin.'),
('count_vs_14',Q5,'AstraZeneca sponsors osimertinib in 14 trials with carboplatin.'),
('count_after',Q5,'AstraZeneca sponsors osimertinib in 10 trials.'),
('count_bare',Q4,'PLB1003: 1 trial.'),
('count_enumerated',Q4,'PLB1003 has 1 trial, lorlatinib has 13 trials.'),
('endpoint_preposition',Q3,'Osimertinib acts on EGFR and on ALK.'),
('endpoint_noun',Q3,'Osimertinib is an inhibitor of EGFR and of ALK.'),
('endpoint_adverb',Q3,'Osimertinib inhibits EGFR and also ALK.'),
('endpoint_control',Q3,'Osimertinib acts on EGFR and ALK.'),
('noun_target_second',QT,'EGFR is a target of osimertinib and of crizotinib.'),
('pronoun_faithful',Q3,'Osimertinib acts on EGFR and it inhibits EGFR.'),
('pronoun_stale_faithful',QT,'Osimertinib acts on EGFR. Crizotinib acts on ALK and it inhibits ALK.'),
('action_antagonist','What does fulvestrant target?','Fulvestrant activates ESR1.'),
('action_noun_agonist','What does fulvestrant target?','Fulvestrant is an agonist of ESR1.'),
('action_control_antagonist','What does fulvestrant target?','Fulvestrant is an antagonist of ESR1.'),
]
for args in CASES:run(*args)
Path(__file__).with_name('replay6_r2_spec_probe_results.json').write_text(json.dumps(rows,indent=2,ensure_ascii=False),encoding='utf-8')
