import sys,json
from pathlib import Path
sys.path.insert(0,'src')
from app import Engine
e=Engine()
qs={
 'target':'What does osimertinib target?',
 'trials':'What trials evaluate Tagrisso?',
 'alk':'Which drugs act on ALK?',
 'sponsors':'Which companies are developing osimertinib?',
 'portfolio':'What is AstraZeneca running in NSCLC?',
 'profile':'Profile of osimertinib'}
cases=[
('reversed_target','target','EGFR acts on osimertinib.'),
('reversed_inhibition','target','EGFR inhibits osimertinib.'),
('reversed_trial','trials','osimertinib evaluates NCT03909334.'),
('reversed_sponsor','portfolio','osimertinib sponsors AstraZeneca.'),
('wrong_target','target','osimertinib inhibits ALK.'),
('pronoun_target_same_line','target','osimertinib acts on EGFR. It inhibits ALK.'),
('pronoun_target_newline','target','osimertinib acts on EGFR.\nIt inhibits ALK.'),
('pronoun_this_drug','target','osimertinib acts on EGFR. This drug inhibits ALK.'),
('noun_inhibitor','target','osimertinib is an ALK inhibitor.'),
('noun_egfr_inhibitor','target','osimertinib is an EGFR inhibitor.'),
('possessive','portfolio',"AstraZeneca's osimertinib."),
('possessive_relation','portfolio',"AstraZeneca's osimertinib targets NSCLC."),
('wrong_trial_phase','trials','NCT03909334 is phase 3.'),
('swapped_trial_phases','trials','NCT03909334 is phase 3 and NCT07680790 is phase 2.'),
('swapped_trial_phases_split','trials','NCT03909334 is phase 3; NCT07680790 is phase 2.'),
('wrong_trial_status','trials','NCT03909334 is recruiting.'),
('pooled_trial_status','trials','NCT03909334 is recruiting and NCT03535363 is completed.'),
('pooled_trial_status2','trials','NCT03909334 and NCT07680790 are recruiting.'),
('wrong_drug_count','alk','PLB1003 has 13 NSCLC trials.'),
('wrong_drug_count_target','alk','PLB1003 acts on ALK with 13 NSCLC trials.'),
('swapped_drug_counts','alk','PLB1003 has 13 NSCLC trials and lorlatinib has 0 NSCLC trials.'),
('swapped_sponsor_counts','portfolio','AstraZeneca sponsors 10 NSCLC trials evaluating osimertinib and 14 NSCLC trials evaluating carboplatin.'),
('wrong_sponsor_count','portfolio','AstraZeneca sponsors 10 NSCLC trials evaluating osimertinib.'),
('wrong_trial_status_list','trials','- NCT03909334: recruiting\n- NCT07680790: recruiting'),
('clinical_grammar_only','target','osimertinib is the therapy for all lung cancer.'),
('clinical_word_reuse','profile','osimertinib is a clinical inhibitor for all cancer.'),
('empty_endpoint','target','EGFR is a drug inhibitor.'),
('targetless_relation','target','osimertinib sponsors trials.'),
('missing_all_endpoints','target','This drug targets all cancer.'),
('count_long_unit','alk','PLB1003 has 13 non small cell lung cancer trials.'),
('trial_pronoun_reset','trials','NCT03909334 evaluates osimertinib. It evaluates osimertinib and is phase 3.'),
('trial_pronoun_control','trials','NCT03909334 evaluates osimertinib. It is phase 3.'),
('wrong_relation_type','portfolio','osimertinib evaluates AstraZeneca.'),
]
rows=[]
for ident,qid,a in cases:
 r=e.check(qs[qid],a)
 row={'id':ident,'question':qs[qid],'answer':a,'grounded':r['checks']['grounded'],'unsupported_claims':r['checks']['unsupported_claims'],'checks':r['checks'],'evidence':[{'relation':x.relation,'statement':x.statement,'source_record':x.source_record} for x in e.kg.retrieve(r['intent'],r['entities'])]}
 rows.append(row)
 print(ident, json.dumps({'answer':a,'grounded':row['grounded'],'findings':[(x['kind'],x['value']) for x in row['unsupported_claims']]},ensure_ascii=False))
Path('audit_evidence_claims/r3_recheck/old/independent_adversarial_results.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
