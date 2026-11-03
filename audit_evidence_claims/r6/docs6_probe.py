"""Independent R6 docs and fresh faithful corpus. All writes local to this directory."""
import json,sys
from pathlib import Path
from dataclasses import asdict
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'src'))
from app import Engine
Q={1:'Which companies are developing osimertinib?',2:'What trials evaluate Tagrisso?',3:'What does osimertinib target?',4:'Which drugs act on ALK?',5:'What is AstraZeneca running in NSCLC?',6:'What is the capital of France?'}
FAITHFUL={
1:[
'AstraZeneca sponsors trials evaluating osimertinib; the graph records 14 trials for this company and this drug.',
'Osimertinib trial sponsors include AstraZeneca, Bristol Myers Squibb and Eli Lilly.',
'AstraZeneca: 14 trials of Tagrisso. Bristol Myers Squibb: 2 trials of Tagrisso. Eli Lilly: 2 trials of Tagrisso.',
'AstraZeneca is a sponsor of osimertinib trials, as are Bristol Myers Squibb and Eli Lilly.',
'Osimertinib is evaluated in trials sponsored by AstraZeneca and by Eli Lilly.',
'The graph includes AstraZeneca as a sponsor of 14 trials evaluating osimertinib.',
'Trials evaluating osimertinib are sponsored by Bristol Myers Squibb. It sponsors 2 trials of this drug.',
'AstraZeneca leads trials evaluating osimertinib. Eli Lilly also sponsors trials of it.'
],
2:[
'Osimertinib trials include NCT07680790, which is recruiting in phase 3, and NCT03535363, which is completed in phase 1.',
'NCT07680790 evaluates osimertinib in phase 3 and is recruiting.',
'NCT03909334 evaluates Tagrisso; its phase is 2 and its status is active, not recruiting.',
'The phase 3 trials NCT07680790 and NCT07738172 evaluate osimertinib and are recruiting.',
'NCT03909334 and NCT02411448 are active but not recruiting trials evaluating osimertinib.',
'The graph lists NCT03535363 as a completed phase 1 trial of osimertinib.',
'Osimertinib is tested by NCT03909334, a phase 2 trial, and by NCT07680790, a phase 3 trial.',
'Trials evaluating Tagrisso:\n- NCT07680790: phase 3; recruiting.\n- NCT03535363: phase 1; completed.'
],
3:[
'Inhibition of EGFR by Tagrisso is recorded in the graph.',
'The drug osimertinib is listed as an inhibitor of EGFR.',
'EGFR inhibitors include the drug osimertinib.',
'The graph records EGFR as the target of Tagrisso.',
'Tagrisso acts on EGFR. Its mechanism is inhibition of this target.',
'Osimertinib acts on EGFR as an inhibitor; EGFR is its target.',
'Osimertinib inhibits EGFR, and this target is inhibited by the drug.',
'EGFR is the reported target. Osimertinib inhibits it.'
],
4:[
'The graph lists lorlatinib and crizotinib as inhibitors of ALK.',
'ALK inhibitors include lorlatinib, crizotinib and brigatinib.',
'Lorlatinib is approved and has 13 NSCLC trials in this graph; crizotinib is approved and has 15.',
'PLB1003 and ASP-3026 inhibit ALK and have a maximum stage of phase 1.',
'Lorlatinib, crizotinib and alectinib are approved ALK inhibitors.',
'For lorlatinib, the graph records 13 NSCLC trials. For crizotinib, it records 15 NSCLC trials.',
'ALK is inhibited by lorlatinib. Its maximum stage is approval.',
'Lorlatinib targets ALK, as does crizotinib.'
],
5:[
'AstraZeneca sponsors trials of osimertinib, carboplatin and gefitinib, with 14, 10 and 8 trials in this graph.',
'AstraZeneca: 14 NSCLC trials of Tagrisso; 10 NSCLC trials of carboplatin.',
'AstraZeneca runs trials evaluating osimertinib and trials evaluating durvalumab in NSCLC.',
'The graph records AstraZeneca as a sponsor of 7 NSCLC trials of durvalumab and 8 NSCLC trials of gefitinib.',
'Osimertinib is evaluated in 14 NSCLC trials sponsored by AstraZeneca.',
'AstraZeneca sponsors 6 NSCLC trials of cisplatin, 6 of pemetrexed and 6 of paclitaxel.',
'AstraZeneca sponsors trials of durvalumab. It sponsors 7 such trials in this graph.',
'Trials of osimertinib and carboplatin are sponsored by AstraZeneca in NSCLC.'
],
6:[
'There are no records in this graph that answer this question.',
'The available evidence cannot answer the question.',
'This question is outside the scope of the graph.',
'I found no relevant information in the retrieved evidence.',
'The graph does not contain the information needed for an answer.',
'The capital of France is not covered by this graph.'
]}
PROBES=[
('as_inverse',3,'EGFR is listed as an inhibitor of osimertinib.'),
('as_inverse_bare',3,'EGFR is an inhibitor of osimertinib.'),
('as_inverse_by',3,'EGFR is recorded as an inhibitor by osimertinib.'),
('as_inverse_true',3,'Osimertinib is recorded as an inhibitor of EGFR.'),
('as_reverse_trial',2,'Osimertinib is listed as a trial of NCT07680790.'),
('record_false_relation',3,'EGFR includes osimertinib.'),
('record_false_identity',3,'EGFR records osimertinib.'),
('trial_group_noun_status',2,'Recruiting trials of osimertinib include NCT03909334 and NCT07680790.'),
('trial_group_noun_phase',2,'Phase 3 trials of osimertinib include NCT03909334 and NCT07680790.'),
('trial_group_noun_true',2,'Recruiting trials of osimertinib include NCT07738172 and NCT07680790.'),
('trial_by_group_status',2,'Osimertinib is evaluated by the recruiting trials NCT03909334 and NCT07680790.'),
('trial_by_group_status_true',2,'Osimertinib is evaluated by the recruiting trials NCT07738172 and NCT07680790.'),
('trial_identity_plural',2,'Osimertinib and Tagrisso are clinical trials.'),
('clinical_after_record',2,'The graph records osimertinib as a clinical trial.'),
('kind_after_record',3,'The graph records EGFR as a drug inhibited by osimertinib.'),
('kind_after_record_true',3,'The graph records osimertinib as a drug inhibiting EGFR.'),
('noun_counts_after_include',1,'Sponsors of 2 trials of osimertinib include AstraZeneca and Bristol Myers Squibb.'),
('noun_counts_after_include_true',1,'Sponsors of 2 trials of osimertinib include Eli Lilly and Bristol Myers Squibb.'),
('object_passive',3,'Osimertinib inhibits EGFR. It is inhibited by EGFR.'),
('object_carried_false',4,'Lorlatinib inhibits ALK. PLB1003 has a maximum stage of approval. Its recorded action is inhibition.'),
]
E=Engine(); rows=[]
for cat, cases in [('faithful',[(f'fresh_q{q}_{i+1}',q,a) for q,aa in FAITHFUL.items() for i,a in enumerate(aa)]),('probe',PROBES)]:
 for ident,q,a in cases:
  ents=E.kg.link_entities(Q[q]); ev=E.kg.retrieve(E.kg.classify(Q[q],ents),ents); result=E.check(Q[q],a)
  rows.append(dict(id=ident,category=cat,question_key=q,question=Q[q],answer=a,result=result,full_evidence=[asdict(e) for e in ev]))
  print(ident,result['checks']['grounded'],[(u['kind'],u['value']) for u in result['checks']['unsupported_claims']])
p=Path(__file__).parent
(p/'docs6_probe_results.json').write_text(json.dumps(rows,indent=2,ensure_ascii=False),encoding='utf8')
summary={q:dict(passed=sum(r['result']['checks']['grounded'] for r in rows if r['category']=='faithful' and r['question_key']==q),total=len(aa)) for q,aa in FAITHFUL.items()}
(p/'docs6_summary.json').write_text(json.dumps(summary,indent=2),encoding='utf8'); print(summary)
