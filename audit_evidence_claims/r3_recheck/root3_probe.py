"""R3 root attacks. All writes are adjacent to this scratch script."""
import sys, json
from pathlib import Path
sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'src'))
from app import Engine
from claims import _units, _tokenise, _clauses
engine = Engine()
Q1='Which companies are developing osimertinib?'
Q2='What trials evaluate Tagrisso?'
Q3='What does osimertinib target?'
Q4='Which drugs act on ALK?'
Q5='What is AstraZeneca running in NSCLC?'
Q6='What is the capital of France?'
CASES = [
 ('heading_activate', Q3, 'these drugs activate:\n- OSIMERTINIB acts on EGFR (inhibitor)'),
 ('heading_sponsor', Q3, 'these drugs sponsor:\n- OSIMERTINIB acts on EGFR (inhibitor)'),
 ('heading_sponsors_full', Q3, 'these drugs are sponsors of trials:\n- OSIMERTINIB acts on EGFR (inhibitor)'),
 ('heading_activators_full', Q3, 'these drugs are activators:\n- OSIMERTINIB acts on EGFR (inhibitor)'),
 ('plain_sponsors_full', Q3, 'Osimertinib is a sponsor of trials.'),
 ('plain_activators_full', Q3, 'Osimertinib is an activator.'),
 ('heading_inhibitor_of_alk', Q3, 'these drugs are inhibitors of ALK:\n- OSIMERTINIB acts on EGFR (inhibitor)'),
 ('heading_with_alk', Q3, 'these drugs inhibit EGFR with ALK:\n- OSIMERTINIB acts on EGFR (inhibitor)'),
 ('heading_including_alk', Q3, 'these drugs inhibit EGFR including ALK:\n- OSIMERTINIB acts on EGFR (inhibitor)'),
 ('heading_fragment', Q3, 'these drugs with ALK:\n- OSIMERTINIB acts on EGFR (inhibitor)'),
 ('heading_lung', Q3, 'these drugs are NSCLC drugs:\n- OSIMERTINIB acts on EGFR (inhibitor)'),
 ('heading_clinical_control', Q3, 'these drugs are safe:\n- OSIMERTINIB acts on EGFR (inhibitor)'),
 ('plain_activate', Q3, 'Osimertinib activates.'),
 ('plain_sponsor', Q3, 'Osimertinib sponsors.'),
 ('plain_with_alk', Q3, 'Osimertinib inhibits EGFR with ALK.'),
 ('plain_including_alk', Q3, 'Osimertinib inhibits EGFR including ALK.'),
 ('plain_fragment', Q3, 'Osimertinib with ALK.'),
 ('indication_drug', Q3, 'Osimertinib is an NSCLC drug.'),
 ('indication_inhibits', Q3, 'Osimertinib inhibits EGFR in lung cancer.'),
 ('indication_target', Q3, 'EGFR is an NSCLC drug.'),
 ('indication_trial', Q3, 'Osimertinib has NSCLC trials.'),
 ('indication_approved', Q4, 'LORLATINIB is approved for NSCLC.'),
 ('indication_approved_in', Q4, 'LORLATINIB is approved in NSCLC.'),
 ('indication_approved_drug', Q4, 'LORLATINIB is an approved NSCLC drug.'),
 ('indication_plb', Q4, 'PLB1003 has NSCLC trials.'),
 ('indication_for_control', Q3, 'Osimertinib is for lung cancer.'),
 ('unknown_number_only', Q4, 'PLB1003 has NSCLC trials: 1.'),
 ('pronoun_subject_target', Q3, 'EGFR is inhibited by osimertinib. It inhibits EGFR.'),
 ('pronoun_subject_trial', Q2, 'Osimertinib is evaluated by NCT03909334. It is phase 2.'),
 ('pronoun_object_company', Q5, 'Osimertinib is sponsored by AstraZeneca. It sponsors carboplatin.'),
 ('pronoun_plural', Q4, 'LORLATINIB and PLB1003 act on ALK. They are approved.'),
 ('pronoun_plural_swap', Q4, 'PLB1003 and LORLATINIB act on ALK. They are approved.'),
 ('pronoun_same_clause', Q4, 'LORLATINIB and PLB1003 act on ALK and they are approved.'),
 ('pronoun_same_clause_swap', Q4, 'PLB1003 and LORLATINIB act on ALK and they are approved.'),
 ('pronoun_two_sentences', Q4, 'LORLATINIB and PLB1003 act on ALK. they are approved.'),
 ('pronoun_explicit_control', Q4, 'LORLATINIB and PLB1003 act on ALK and PLB1003 is approved.'),
 ('question_seed_good', Q3, 'It inhibits EGFR.'),
 ('question_seed_bad', Q3, 'It inhibits ALK.'),
 ('question_seed_wrong_type', Q3, 'This trial is phase 3.'),
 ('object_pronoun_faithful', Q3, 'Osimertinib targets EGFR and inhibits it.'),
 ('typed_pronoun_last', Q4, 'PLB1003 and LORLATINIB act on ALK. These drugs are approved.'),
 ('noun_possessive', Q3, "AstraZeneca's osimertinib inhibits EGFR."),
 ('noun_graph_possessive', Q5, "AstraZeneca's osimertinib."),
 ('fragment_drug_identity', Q4, 'PLB1003 is LORLATINIB.'),
 ('fragment_trial_identity', Q2, 'NCT03909334 is NCT07680790.'),
 ('fragment_entity_identity', Q3, 'Osimertinib is EGFR.'),
 ('fragment_alias_identity', Q3, 'Osimertinib is Tagrisso.'),
 ('fragment_without_be', Q4, 'PLB1003, LORLATINIB.'),
 ('plain_safety', Q3, 'Osimertinib is safe.'),
 ('bracket_dots', Q3, 'Osimertinib [ORG:is.safe] acts on EGFR.'),
 ('bracket_hyphen', Q3, 'Osimertinib [ORG:is-safe] acts on EGFR.'),
 ('markdown_korean', Q3, 'Osimertinib [안전하다] acts on EGFR.'),
 ('markdown_strong', Q3, 'Osimertinib **is safe** and acts on EGFR.'),
 ('non_simple', Q3, 'Osimertinib does not inhibit EGFR.'),
 ('un_simple', Q3, 'Osimertinib is uninhibitory of EGFR.'),
 ('number_only_line', Q4, 'PLB1003 trials:\n1'),
 ('flat_non_copied', Q3, 'OSIMERTINIB acts on EGFR (inhibitor!)'),
 ('flat_question', Q3, 'OSIMERTINIB acts on EGFR? inhibitor.'),
 ('count_cross_pair', Q5, 'AstraZeneca sponsors osimertinib in 10 trials evaluating carboplatin.'),
 ('count_cross_pair_control', Q5, 'AstraZeneca sponsors osimertinib in 14 trials evaluating carboplatin.'),
 ('count_shared_group', Q5, 'AstraZeneca sponsors osimertinib and carboplatin in 10 trials.'),
 ('count_shared_group_control', Q5, 'AstraZeneca sponsors osimertinib and carboplatin in 14 trials.'),
 ('count_elided_faithful', Q5, 'AstraZeneca sponsors 14 trials of osimertinib and 10 trials of carboplatin.'),
 ('zero_evidence_clinical', Q6, 'There are clinical trials.'),
 ('nsclc_trial_unsupported', Q3, 'Osimertinib is in NSCLC trials.'),
 ('clinical_trial_unsupported', Q3, 'Osimertinib is in clinical trials.'),
 ('faithful_relation_passive', Q3, 'EGFR is inhibited by osimertinib.'),
]
rows = []
for ident,q,a in CASES:
    result = engine.check(q,a)
    entities=engine.kg.link_entities(q)
    ev=engine.kg.retrieve(engine.kg.classify(q,entities),entities)
    rows.append(dict(id=ident, question=q, answer=a, result=result,
                     evidence=[vars(x) for x in ev], units=_units(a)))
    print(json.dumps(dict(id=ident, grounded=result['checks']['grounded'],
       findings=[(f['kind'],f['value']) for f in result['checks']['unsupported_claims']])))
Path(__file__).with_suffix('.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
