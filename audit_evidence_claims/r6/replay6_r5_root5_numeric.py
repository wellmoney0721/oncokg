"""Independent R5 numeric/attribute probes; writes only next to this script."""
import json
import sys
from pathlib import Path
sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'src'))
from app import Engine
engine = Engine()
Q = {1:'Which companies are developing osimertinib?',
     2:'What trials evaluate Tagrisso?',
     3:'What does osimertinib target?',
     4:'Which drugs act on ALK?',
     5:'What is AstraZeneca running in NSCLC?'}
CASES = [
 ('percent_attached',4,'LORLATINIB has 13% NSCLC trials.'),
 ('percent_spaced',4,'LORLATINIB has 13 % NSCLC trials.'),
 ('percent_nbsp',4,'LORLATINIB has 13\u00a0% NSCLC trials.'),
 ('percent_word',4,'LORLATINIB has 13 percent NSCLC trials.'),
 ('percent_parenthetic',5,'AstraZeneca sponsors osimertinib in 14 (%) trials.'),
 ('percent_suffix',5,'AstraZeneca sponsors osimertinib in trials: 14 %.'),
 ('count_label_original',5,'AstraZeneca sponsors osimertinib and carboplatin in trials: 10.'),
 ('count_label_graph',5,'AstraZeneca sponsors osimertinib and carboplatin in trials in this graph: 10.'),
 ('count_label_recorded',5,'AstraZeneca sponsors osimertinib and carboplatin in trials recorded: 10.'),
 ('count_label_nsclc',5,'AstraZeneca sponsors osimertinib and carboplatin in NSCLC trials in this graph: 10.'),
 ('count_alias_pass',5,'AstraZeneca sponsors 14 trials of osimertinib (Tagrisso).'),
 ('count_alias_wrong',5,'AstraZeneca sponsors 10 trials of osimertinib (Tagrisso).'),
 ('count_separate_pass',5,'AstraZeneca sponsors 14 trials of osimertinib and 10 trials of carboplatin.'),
 ('count_separate_wrong',5,'AstraZeneca sponsors 10 trials of osimertinib and 14 trials of carboplatin.'),
 ('count_alias_separate',5,'AstraZeneca sponsors 14 trials of osimertinib (Tagrisso) and 10 trials of carboplatin.'),
 ('count_such_wrong',5,'AstraZeneca sponsors trials of Tagrisso. There are 10 such trials in this graph.'),
 ('count_such_right',5,'AstraZeneca sponsors trials of Tagrisso. There are 14 such trials in this graph.'),
 ('count_such_elided_wrong',5,'AstraZeneca sponsors trials of Tagrisso and has 10 such trials.'),
 ('count_such_drug_wrong',5,'AstraZeneca sponsors trials of Tagrisso. This drug has 10 such trials in this graph.'),
 ('count_such_trials_wrong',5,'AstraZeneca sponsors trials of Tagrisso. These trials are 10 in this graph.'),
 ('status_phase_parentheses',2,'NCT03909334 (phase 2) and NCT07680790 (phase 3) are recruiting.'),
 ('status_phase_one',2,'NCT03909334 (phase 2) and NCT07680790 are recruiting.'),
 ('status_trial_apposition',2,'NCT03909334, a trial of osimertinib, and NCT07680790 are recruiting.'),
 ('status_trial_repeated',2,'Trial NCT03909334 and trial NCT07680790 are recruiting.'),
 ('status_trial_postfix',2,'NCT03909334 trial and NCT07680790 trial are recruiting.'),
 ('status_explicit',2,'NCT03909334 and NCT07680790 are recruiting.'),
 ('status_good',2,'NCT07680790 and NCT02411448 are recruiting.'),
 ('status_parentheses_swapped',2,'NCT07680790 (phase 3) and NCT03909334 (phase 2) are recruiting.'),
 ('phase_trial_repeated',2,'Trial NCT03909334 and trial NCT07680790 are phase 3.'),
 ('phase_trial_postfix',2,'NCT03909334 trial and NCT07680790 trial are phase 3.'),
 ('phase_context_parentheses',2,'NCT03909334 (active, not recruiting) and NCT07680790 are phase 3.'),
 ('phase_context_status',2,'NCT03909334, active not recruiting, and NCT07680790 are phase 3 trials of osimertinib.'),
 ('phase_both_good',2,'NCT07680790 and NCT02411448 are phase 3.'),
 ('phase_plural_wrong',2,'NCT03909334 is phases 3.'),
 ('phase_digit_before',4,'PLB1003 has 1 phase.'),
 ('phase_digit_before_roman',4,'PLB1003 has I phase.'),
 ('phase_digital_wrong',4,'PLB1003 is phase 13.'),
 ('phase_unit_copy',4,'PLB1003 has phase 1 and 1 trial.'),
 ('phase_unit_copy_plural',4,'PLB1003 has phase 1 and 1 trials.'),
 ('number_trial_id',2,'NCT03909334 has 2 trials.'),
 ('number_phase_evidence',2,'NCT03909334 has 2 phases.'),
 ('phase_ordinal',2,'NCT03909334 is a 3 phase trial of osimertinib.'),
 ('phase_compound_good',4,'CONTELTINIB is phase 1/2.'),
 ('phase_compound_bad',4,'PLB1003 is phase 1/2.'),
 ('status_split_word',2,'NCT07680790 is non recruiting.'),
 ('status_hyphen',2,'NCT07680790 is non-recruiting.'),
 ('status_underscore',2,'NCT07680790 is non_recruiting.'),
]
rows=[]
for ident, q, answer in CASES:
    result=engine.check(Q[q],answer)
    entities=engine.kg.link_entities(Q[q])
    ev=engine.kg.retrieve(engine.kg.classify(Q[q],entities),entities)
    rows.append(dict(id=ident,question=Q[q],answer=answer,result=result,evidence=[vars(e) for e in ev]))
    print(json.dumps(dict(id=ident,grounded=result['checks']['grounded'],findings=[(f['kind'],f['value']) for f in result['checks']['unsupported_claims']]),ensure_ascii=False))
Path(__file__).with_suffix('.json').write_text(json.dumps(rows,indent=2,ensure_ascii=False),encoding='utf-8')
