import sys, json, re
from pathlib import Path
sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'src'))
from app import Engine
from claims import _tokenise, _clauses, check_claims
e = Engine()
Q4 = 'Which drugs act on ALK?'
Q5 = 'What is AstraZeneca running in NSCLC?'
Q2 = 'What trials evaluate Tagrisso?'
Q3 = 'What does osimertinib target?'
cases = [
('count_label_phase', Q4, 'PLB1003: clinical trials: 1.'),
('count_label_phase2', Q4, 'PLB1003 has NSCLC trials: 1.'),
('count_swap_tail', Q5, 'AstraZeneca sponsors osimertinib in 10 trials evaluating carboplatin.'),
('count_swap_tail_control', Q5, 'AstraZeneca sponsors osimertinib in 14 trials evaluating carboplatin.'),
('count_coordinated', Q5, 'AstraZeneca sponsors 10 trials evaluating carboplatin and osimertinib.'),
('count_coordinated_reverse', Q5, 'AstraZeneca sponsors 10 trials evaluating osimertinib and carboplatin.'),
('count_coordinated_noun', Q5, 'AstraZeneca sponsors 10 trials of carboplatin and osimertinib.'),
('count_group_three', Q5, 'AstraZeneca is the sponsor of 14 NSCLC trials of osimertinib and 10 NSCLC trials of carboplatin and 8 NSCLC trials of gefitinib.'),
('count_group_wrong', Q5, 'AstraZeneca is the sponsor of 10 NSCLC trials of osimertinib and 14 NSCLC trials of carboplatin.'),
('count_wrong_as_phase', Q4, 'PLB1003 has 1 clinical phase trial.'),
('phase_after_eval', Q2, 'NCT03909334 evaluates osimertinib in phase 2.'),
('phase_after_eval_wrong', Q2, 'NCT03909334 evaluates osimertinib in phase 3.'),
('phase_paired_trial', Q2, 'NCT03909334 and NCT07680790 are phase 3.'),
('phase_paired_trial2', Q2, 'NCT03909334 and NCT07680790 are phase 2.'),
('phase_drug_trial', Q2, 'Osimertinib is evaluated by NCT03909334 in phase 2.'),
('phase_roman', Q2, 'NCT03909334 is a phase II trial evaluating osimertinib.'),
('phase_multi', Q2, 'NCT04285671 is a phase 1/2 trial evaluating osimertinib.'),
('phase_multi_and', Q2, 'NCT04285671 is a phase 1 and 2 trial evaluating osimertinib.'),
('phase_multi_cap', Q2, 'NCT04285671 is a Phase I/II trial evaluating osimertinib.'),
('alias_two', Q3, 'Osimertinib (Tagrisso) acts on EGFR.'),
('alias_three', Q3, 'Osimertinib (Tagrisso, AZD 9291) acts on EGFR.'),
('alias_four', Q3, 'Osimertinib (Tagrisso, AZD 9291, AZD9291) acts on EGFR.'),
('alias_digits_two', Q3, 'AZD9291 (AZD 9291) acts on EGFR.'),
('alias_digits_two_reverse', Q3, 'AZD 9291 (AZD9291) acts on EGFR.'),
('alias_hyphen_second', Q3, 'AZD9291 (AZD-9291) acts on EGFR.'),
('alias_hyphen_second_control', Q3, 'AZD-9291 acts on EGFR.'),
('alias_repetition', Q3, 'Osimertinib acts on EGFR. Tagrisso acts on EGFR. AZD 9291 acts on EGFR.'),
('alias_digits_attached', Q3, 'AZD 9291 acts on EGFR with 9291 trials.'),
('alias_digit_count', Q3, 'AZD 9291 has 9291 trials.'),
('count_subject_target', Q4, 'ALK is inhibited by PLB1003 and lorlatinib with 13 trials.'),
('count_subject_target2', Q4, 'ALK is inhibited by PLB1003 with 13 trials and lorlatinib.'),
]
rows=[]
for cid,q,a in cases:
 result=e.check(q,a)
 ents=e.kg.link_entities(q); ev=e.kg.retrieve(e.kg.classify(q,ents),ents)
 toks,entities=_tokenise(a,e.kg.link_entities)
 rows.append(dict(id=cid,question=q,answer=a,result=result,evidence=[vars(x) for x in ev],tokens=toks,token_entities=entities))
 print(cid,result['checks']['grounded'],[(x['kind'],x['value']) for x in result['checks']['unsupported_claims']])
Path(__file__).with_suffix('.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
