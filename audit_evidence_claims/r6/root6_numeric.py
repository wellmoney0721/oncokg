"""Independent round-6 probes of numeric scope, relatives and reference carry."""
import json
import sys
from pathlib import Path
sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'src'))
from app import Engine
engine = Engine()
Q = {1:'Which companies are developing osimertinib?',2:'What trials evaluate Tagrisso?',3:'What does osimertinib target?',4:'Which drugs act on ALK?',5:'What is AstraZeneca running in NSCLC?'}
CASES = [
('relative_status',2,'NCT03909334, which evaluates osimertinib, and NCT07680790 are recruiting.'),
('relative_phase',2,'NCT03909334, which evaluates osimertinib, and NCT07680790 are phase 3.'),
('relative_status_is',2,'NCT03909334, which is phase 2, and NCT07680790 are recruiting.'),
('relative_phase_is',2,'NCT03909334, which is active but not recruiting, and NCT07680790 are phase 3.'),
('relative_status_correct',2,'NCT07680790, which evaluates osimertinib, and NCT02411448 are recruiting.'),
('relative_phase_correct',2,'NCT07680790, which evaluates osimertinib, and NCT02411448 are phase 3.'),
('trial_group_attr_pred',2,'NCT03909334 and NCT07680790 evaluate osimertinib and are recruiting.'),
('trial_group_attr_pred_phase',2,'NCT03909334 and NCT07680790 evaluate osimertinib and are phase 3.'),
('trial_group_record',2,'The graph records NCT03909334 (phase 2) and NCT07680790 (phase 3) as recruiting trials.'),
('trial_group_record_phase',2,'The graph records NCT03909334 and NCT07680790 as phase 3 trials.'),
('trial_group_include',2,'Recruiting trials include NCT03909334 (phase 2) and NCT07680790 (phase 3).'),
('trial_group_phase_include',2,'Phase 3 trials include NCT03909334 (active, not recruiting) and NCT07680790.'),
('count_reference_intervening',5,'AstraZeneca sponsors trials of Tagrisso. AstraZeneca is a company. There are 10 such trials in this graph.'),
('count_reference_intervening_good',5,'AstraZeneca sponsors trials of Tagrisso. AstraZeneca is a company. There are 14 such trials in this graph.'),
('count_reference_meta',5,'AstraZeneca sponsors trials of Tagrisso. This graph records trials. There are 10 such trials.'),
('count_reference_company',5,'AstraZeneca sponsors trials of Tagrisso. This company sponsors 10 such trials.'),
('count_reference_pronoun',5,'AstraZeneca sponsors trials of Tagrisso. It sponsors 10 such trials.'),
('count_reference_group',5,'AstraZeneca sponsors trials of Tagrisso and carboplatin. AstraZeneca is a company. There are 10 such trials.'),
('count_trials_x_are',5,'AstraZeneca sponsors trials of osimertinib: 10.'),
('count_trials_x_number',5,'AstraZeneca trials of osimertinib: 10.'),
('count_trials_pair',5,'AstraZeneca sponsors trials of osimertinib and carboplatin: 10.'),
('count_trials_pair_num_word',5,'AstraZeneca sponsors trials of osimertinib and carboplatin: 10 trials.'),
('count_trials_pair_good',5,'AstraZeneca: 14 trials of osimertinib; 10 trials of carboplatin.'),
('count_entry_wrong',5,'AstraZeneca: 10 trials of osimertinib.'),
('count_entry_pair_wrong',5,'AstraZeneca: 14 trials of carboplatin; 10 trials of osimertinib.'),
('count_entry_subject_target',4,'ALK: 13 trials of lorlatinib.'),
('count_subject_group',4,'LORLATINIB and PLB1003 have NSCLC trials: 13.'),
('count_subject_group_meta',4,'LORLATINIB and PLB1003 have trials in this graph: 13.'),
('count_object_changed',5,'AstraZeneca sponsors trials of osimertinib. Carboplatin is a drug. It sponsors 10 such trials.'),
('count_ordinal',2,'NCT03909334 is a phase third trial.'),
('count_modifier',5,'AstraZeneca sponsors 10 recorded NSCLC clinical trials of osimertinib.'),
('count_drug_prefix',4,'13 trials of PLB1003 and 0 trials of LORLATINIB are recorded in this graph.'),
('count_drug_suffix',4,'Trials of LORLATINIB: 0. Trials of PLB1003: 13.'),
('phase_before_group',2,'Phase 3 trials: NCT03909334 (active, not recruiting), NCT07680790.'),
('status_before_group',2,'Recruiting trials: NCT03909334 (phase 2), NCT07680790.'),
('status_cleft',2,'It is NCT03909334 and NCT07680790 that are recruiting.'),
('object_it_good',1,'AstraZeneca sponsors 14 trials of osimertinib. Bristol Myers Squibb sponsors 2 trials of it.'),
('object_it_wrong',1,'AstraZeneca sponsors 14 trials of osimertinib. Bristol Myers Squibb sponsors 14 trials of it.'),
('object_them_wrong',5,'AstraZeneca sponsors osimertinib and carboplatin. There are 10 trials of them.'),
('object_them_entry',5,'AstraZeneca sponsors osimertinib and carboplatin. AstraZeneca: 10 trials of them.'),
('object_them_count',5,'AstraZeneca sponsors osimertinib and carboplatin. It sponsors 10 trials of them.'),
('carried_target_wrong',4,'PLB1003 acts on ALK. LORLATINIB acts on ROS1. Its action is inhibition of ALK.'),
('carried_target',3,'Osimertinib acts on EGFR. Its recorded action is inhibition.'),
('carried_target_activation',3,'Osimertinib acts on EGFR. Its recorded action is activation.'),
('status_front_nominal',2,'The recruiting trials are NCT03909334 (phase 2) and NCT07680790 (phase 3).'),
('phase_after_evaluate',2,'NCT03909334 and NCT07680790 evaluate osimertinib in phase 3.'),
]
rows=[]
for ident, q, answer in CASES:
    result=engine.check(Q[q],answer)
    entities=engine.kg.link_entities(Q[q])
    ev=engine.kg.retrieve(engine.kg.classify(Q[q],entities),entities)
    rows.append(dict(id=ident,question=Q[q],answer=answer,result=result,evidence=[vars(e) for e in ev]))
    print(json.dumps(dict(id=ident,grounded=result['checks']['grounded'],findings=[(f['kind'],f['value']) for f in result['checks']['unsupported_claims']]),ensure_ascii=False))
Path(__file__).with_suffix('.json').write_text(json.dumps(rows,indent=2,ensure_ascii=False),encoding='utf-8')
