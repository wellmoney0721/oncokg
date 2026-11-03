import sys,json
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'src'))
from app import Engine
from dataclasses import asdict
x=Engine(); kg=x.kg
Q={1:'Which companies are developing osimertinib?',2:'What trials evaluate Tagrisso?',3:'What does osimertinib target?',4:'Which drugs act on ALK?',5:'What is AstraZeneca running in NSCLC?',6:'What is the capital of France?'}
FAITHFUL={
1:[
'AstraZeneca is the lead sponsor of 14 trials evaluating osimertinib.',
'The evidence records AstraZeneca as a lead sponsor of 14 trials evaluating osimertinib.',
'AstraZeneca sponsors trials of osimertinib; Bristol Myers Squibb also sponsors trials of osimertinib.',
'Osimertinib is being studied in trials sponsored by AstraZeneca.',
'AstraZeneca sponsors 14 trials of osimertinib. This is evidence of sponsorship, not evidence that it develops the drug.',
'The graph records trial sponsorship. AstraZeneca is a lead sponsor for osimertinib trials.'
],
2:[
'NCT03909334 is a phase 2 trial evaluating Tagrisso. It is active, not recruiting.',
'Tagrisso is being evaluated in NCT07680790, a recruiting phase 3 trial.',
'NCT03909334 evaluates osimertinib and is phase 2; NCT07680790 evaluates osimertinib and is phase 3.',
'Phase 3 trials evaluating osimertinib include NCT07680790 and NCT02411448.',
'The trials include NCT03909334 (phase 2, active not recruiting) and NCT07680790 (phase 3, recruiting).',
'NCT03535363 is a completed phase 1 trial of osimertinib.'
],
3:[
'Osimertinib is an inhibitor of EGFR.',
'EGFR is inhibited by osimertinib.',
'The mechanism recorded for osimertinib is inhibition of EGFR.',
'Osimertinib targets EGFR and inhibits it.',
'According to the evidence, osimertinib inhibits EGFR.',
'The target of osimertinib is EGFR.'
],
4:[
'Lorlatinib, crizotinib and alectinib inhibit ALK.',
'The graph lists lorlatinib as an ALK inhibitor, with 13 NSCLC trials.',
'PLB1003 inhibits ALK; its maximum stage is phase 1, with 0 NSCLC trials in this graph.',
'ALK is inhibited by lorlatinib, crizotinib and alectinib.',
'CONTELTINIB is an ALK inhibitor with a maximum stage of phase 1/2.',
'ALK inhibitors include:\n- lorlatinib\n- crizotinib\n- alectinib'
],
5:[
'AstraZeneca sponsors 14 NSCLC trials evaluating osimertinib and 10 NSCLC trials evaluating carboplatin.',
'AstraZeneca is running NSCLC trials of osimertinib, carboplatin and gefitinib.',
'According to the graph, AstraZeneca sponsors 7 trials of durvalumab in NSCLC.',
'The graph records AstraZeneca as the sponsor of 14 trials of osimertinib and 10 trials of carboplatin.',
'Osimertinib and carboplatin are being studied in NSCLC trials sponsored by AstraZeneca.',
'AstraZeneca sponsors trials of the following drugs:\n- osimertinib\n- carboplatin\n- gefitinib'
],
6:[
'The graph does not contain the information needed to answer this question.',
'This question is outside the scope of the graph.',
'I cannot determine the capital of France from the retrieved evidence.',
'There is no supporting evidence for an answer in this graph.',
'This graph contains information about drugs and trials, so it cannot answer the question.',
'No relevant evidence was retrieved.'
]}
ATTACKS=[
(3,'EGFR is inhibited osimertinib.'),(3,'EGFR was directly inhibited osimertinib.'),(3,'EGFR was inhibited with osimertinib.'),(3,'EGFR is what inhibited osimertinib.'),
(3,'Osimertinib was inhibiting EGFR.'),(3,'Osimertinib was inhibited by EGFR.'),
(3,'EGFR has inhibited osimertinib.'),(3,'EGFR has been inhibited by osimertinib.'),(3,'EGFR is an inhibitor by osimertinib.'),
(3,'The inhibition of osimertinib by EGFR.'),(3,'The inhibition of EGFR by osimertinib.'),(3,'Osimertinib is the inhibition of EGFR.'),
(3,'Osimertinib is an EGFR blocker.'),(3,'EGFR is the blocker of osimertinib.'),
(3,'Osimertinib acts on EGFR and is the drug that EGFR inhibits.'),(3,'Osimertinib acts on EGFR, inhibited by EGFR.'),
(3,'EGFR is the target, and osimertinib is its inhibitor.'),(3,'Osimertinib targets EGFR, and EGFR inhibits it.'),
(2,'Osimertinib is evaluated at NCT03909334.'),(2,'Osimertinib is evaluated with NCT03909334.'),(2,'NCT03909334 is evaluated by osimertinib.'),
(5,'Osimertinib is sponsored with AstraZeneca.'),(5,'AstraZeneca was sponsored by osimertinib.'),
(3,'EGFR: osimertinib.'),(3,'EGFR is osimertinib.'),(3,'EGFR is a drug.'),(3,'Osimertinib is a target.'),
(4,'ALK is a company.'),(4,'Lorlatinib is an approved target.'),
(3,'OSIMERTINIB acts on EGFR (inhibitor) [ORG:safe].'),
(3,'OSIMERTINIB acts on EGFR (inhibitor) [ORG:discontinued].'),
(3,'OSIMERTINIB acts on EGFR (inhibitor) [ORG:non-inhibitor].'),
(3,'Osimertinib is safe [CHEMBL3353410].'),
(3,'Osimertinib acts on EGFR. It is noninhibitory.'),
(3,'Osimertinib acts on EGFR. It is non-inhibitory.'),
(3,'Osimertinib acts on EGFR. It is unapproved.'),
(3,'OSIMERTINIB acts on EGFR (inhibitor)?'),
(3,'OSIMERTINIB acts on EGFR (inhibitor)!'),
]
rows=[]
for family,cases in [('faithful',[(q,a) for q,aa in FAITHFUL.items() for a in aa]),('attack',ATTACKS)]:
 for i,(q,a) in enumerate(cases,1):
  r=x.check(Q[q],a)
  en=kg.link_entities(Q[q]); ev=kg.retrieve(kg.classify(Q[q],en),en)
  rows.append(dict(id=f'{family}_{i:02}',family=family,q=q,question=Q[q],answer=a,result=r,full_evidence=[asdict(e) for e in ev]))
  print(family,i,q,r['checks']['grounded'],[(f['kind'],f['value']) for f in r['checks']['unsupported_claims']],repr(a))
Path(__file__).with_name('replay4_r3_docs3_probe_results.json').write_text(json.dumps(rows,indent=2,ensure_ascii=False),encoding='utf-8')
