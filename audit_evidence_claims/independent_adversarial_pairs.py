import sys,json
from pathlib import Path
sys.path.insert(0,'src')
from app import Engine
from dataclasses import asdict
e=Engine(); kg=e.kg
def retrieve(q):
 entities=kg.link_entities(q); return entities,kg.retrieve(kg.classify(q,entities),entities)
rows=[]
def run(ident,qs,answer):
 entities=[]; ev=[]
 for q in qs:
  ee,vv=retrieve(q); entities.extend(ee); ev.extend(vv)
 r=kg.check_groundedness(answer,ev,entities,True,set(kg.dic['index']),linker=kg.link_entities)
 rows.append({'id':ident,'retrieval_questions':qs,'answer':answer,'checks':r,'evidence':[asdict(x) for x in ev]})
 print(ident,json.dumps({'answer':answer,'grounded':r['grounded'],'findings':[(x['kind'],x['value']) for x in r['unsupported_claims']]},ensure_ascii=False))
qt=['What does osimertinib target?','What does crizotinib target?']
run('wrong_target_pairs',qt,'osimertinib acts on ALK and crizotinib acts on EGFR.')
run('correct_target_pairs_same_sentence',qt,'osimertinib acts on EGFR and crizotinib acts on ALK.')
run('correct_target_pairs_split',qt,'osimertinib acts on EGFR. crizotinib acts on ALK.')
qtr=['What trials evaluate Tagrisso?','What trials evaluate crizotinib?']
run('wrong_trial_pairs',qtr,'NCT03909334 evaluates crizotinib and NCT06254599 evaluates osimertinib.')
run('correct_trial_pairs_same_sentence',qtr,'NCT03909334 evaluates osimertinib and NCT06254599 evaluates crizotinib.')
run('correct_trial_pairs_split',qtr,'NCT03909334 evaluates osimertinib. NCT06254599 evaluates crizotinib.')
qc=['What is AstraZeneca running in NSCLC?','What is Pfizer running in NSCLC?']
run('wrong_company_pairs',qc,'AstraZeneca sponsors crizotinib and Pfizer sponsors osimertinib.')
run('correct_company_pairs_same_sentence',qc,'AstraZeneca sponsors osimertinib and Pfizer sponsors crizotinib.')
run('correct_company_pairs_split',qc,'AstraZeneca sponsors osimertinib. Pfizer sponsors crizotinib.')
run('phase_13_regex',['Which drugs act on ALK?'],'PLB1003 is phase 13.')
run('phase_10_regex',['Which drugs act on ALK?'],'PLB1003 is phase 10.')
run('count_after_colon',['Which drugs act on ALK?'],'PLB1003 NSCLC trials: 13.')
run('count_after_colon_list',['Which drugs act on ALK?'],'- PLB1003: NSCLC trials: 13\n- lorlatinib: NSCLC trials: 0')
run('reversed_noun',['What does osimertinib target?'],'EGFR is an osimertinib inhibitor.')
Path('audit_evidence_claims/independent_adversarial_pairs_results.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')

