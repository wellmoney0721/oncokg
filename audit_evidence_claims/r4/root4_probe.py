"""Independent R4 probes. All output remains adjacent to this script."""
import json, sys
from pathlib import Path
sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'src'))
from app import Engine
engine = Engine()
Q = {
 1: 'Which companies are developing osimertinib?',
 2: 'What trials evaluate Tagrisso?',
 3: 'What does osimertinib target?',
 4: 'Which drugs act on ALK?',
 5: 'What is AstraZeneca running in NSCLC?',
 6: 'What is the capital of France?',
}
CASES = [
 ('plural_chain',4,'PLB1003 and LORLATINIB act on ALK. they act on ALK. they are approved.'),
 ('plural_chain_swap',4,'LORLATINIB and PLB1003 act on ALK. they act on ALK. they are approved.'),
 ('plural_chain_and',4,'PLB1003 and LORLATINIB act on ALK and they act on ALK and they are approved.'),
 ('plural_chain_single',4,'PLB1003 and LORLATINIB act on ALK and they are approved.'),
 ('plural_chain_caps',4,'PLB1003 and LORLATINIB act on ALK. They act on ALK. They are approved.'),
 ('plural_chain_repeated_subject',4,'PLB1003 and LORLATINIB act on ALK. they act on ALK. PLB1003 and LORLATINIB are approved.'),
 ('plural_two_pronouns',4,'PLB1003 and LORLATINIB act on ALK. they are approved and they act on ALK.'),
 ('plural_object',4,'ALK is targeted by PLB1003 and LORLATINIB. they are approved.'),
 ('plural_second_relation',4,'PLB1003 and LORLATINIB act on ALK and inhibit ALK. they are approved.'),
 ('plural_after_elided_value',4,'PLB1003 and LORLATINIB act on ALK and are approved.'),
 ('plural_after_elided_value_swap',4,'LORLATINIB and PLB1003 act on ALK and are approved.'),
 ('plural_it',4,'LORLATINIB and PLB1003 act on ALK. it is approved.'),
 ('conjunction_or_clinical',3,'Osimertinib inhibits EGFR or is safe.'),
 ('self_embedded_relation',3,'Osimertinib is EGFR and inhibits EGFR.'),
 ('relation_precedes_identity',3,'Osimertinib inhibits EGFR and is EGFR.'),
 ('relative_identity',3,'Osimertinib, which is EGFR, inhibits EGFR.'),
 ('word_clinical_target',2,'NCT03909334 evaluates osimertinib, a clinical company.'),
 ('percent',4,'LORLATINIB has 13% NSCLC trials.'),
 ('percent_zero',4,'PLB1003 has 0% NSCLC trials.'),
 ('ratio',5,'AstraZeneca sponsors 14/10 trials of osimertinib.'),
 ('drug_count_unit',4,'PLB1003 has 1 phase.'),
 ('non_ascii_hyphen',3,'Osimertinib is a non‑inhibitor of EGFR.'),
 ('negation_split',3,'Osimertinib does n o t inhibit EGFR.'),
 ('negation_underscore',3,'Osimertinib does_not inhibit EGFR.'),
 ('negation_backtick',3,'Osimertinib does `not` inhibit EGFR.'),
 ('numeric_only_line',4,'PLB1003 NSCLC trials:\n13'),
 ('word_heading_group',4,'Approved agents:\n- PLB1003 acts on ALK (inhibitor); max stage PHASE_1; 0 NSCLC trial(s) in this graph'),
 ('target_compound',3,'Osimertinib inhibits EGFR, a compound.'),
 ('target_drug',3,'Osimertinib inhibits EGFR, a drug.'),
 ('wrong_object_pronoun',3,'Osimertinib inhibits EGFR. EGFR inhibits it.'),
 ('wrong_subject_then_pronoun',3,'Osimertinib inhibits EGFR and it is EGFR.'),
 ('prior_object_pronoun',4,'LORLATINIB and PLB1003 act on ALK. ALK is targeted by them.'),
 ('object_repeated',3,'Osimertinib targets EGFR. Osimertinib inhibits it and targets it.'),
 ('faithful_plural',4,'LORLATINIB and CRIZOTINIB act on ALK. they are approved.'),
 ('faithful_plural_caps',4,'LORLATINIB and CRIZOTINIB act on ALK. They are approved.'),
 ('faithful_phase_list',2,'NCT03909334 and NCT07680790 evaluate osimertinib. The former is phase 2 and the latter is phase 3.'),
 ('faithful_sponsored',5,'AstraZeneca sponsors trials of osimertinib and carboplatin.'),
 ('faithful_trial_noun',2,'Trials of osimertinib include NCT03909334 and NCT07680790.'),
 ('faithful_trial_evaluating',2,'Trials evaluating osimertinib include NCT03909334 and NCT07680790.'),
 ('faithful_trial_noun_single',2,'NCT03909334 is a phase 2 trial of osimertinib.'),
]
rows=[]
for ident, q, answer in CASES:
    result=engine.check(Q[q],answer)
    ents=engine.kg.link_entities(Q[q])
    ev=engine.kg.retrieve(engine.kg.classify(Q[q],ents),ents)
    rows.append(dict(id=ident,question=Q[q],answer=answer,result=result,evidence=[vars(e) for e in ev]))
    print(json.dumps(dict(id=ident,grounded=result['checks']['grounded'],findings=[(f['kind'],f['value']) for f in result['checks']['unsupported_claims']]),ensure_ascii=False))
Path(__file__).with_suffix('.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
