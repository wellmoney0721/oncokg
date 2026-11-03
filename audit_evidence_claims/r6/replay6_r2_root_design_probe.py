"""Round 2 independent attacks; reads local graph, writes only adjacent JSON."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'src'))
from app import Engine
from claims import _units, _tokenise, _clauses, check_claims

engine = Engine()
QT = 'What does osimertinib target?'
QR = 'What trials evaluate Tagrisso?'
QS = 'Which companies are developing osimertinib?'
QA = 'Which drugs act on ALK?'
cases = [
    ('discarded_heading', QT, 'osimertinib is safe:'),
    ('discarded_heading_before_prose', QT, 'osimertinib is discontinued:\nOsimertinib acts on EGFR.'),
    ('verbatim_under_unsafe_heading', QT, 'these drugs are safe:\n- OSIMERTINIB acts on EGFR (inhibitor)'),
    ('verbatim_under_negated_heading', QT, 'these drugs do not act on EGFR:\n- OSIMERTINIB acts on EGFR (inhibitor)'),
    ('verbatim_under_reversed_heading', QT, 'EGFR acts on these drugs:\n- OSIMERTINIB acts on EGFR (inhibitor)'),
    ('ordinary_bullet_heading_control', QT, 'these drugs are safe:\n- osimertinib'),
    ('verbatim_heading_blank', QT, 'osimertinib is safe:\n\nOSIMERTINIB acts on EGFR (inhibitor)'),
    ('meta_missing_phase', QR, 'It is phase 3.'),
    ('meta_missing_typed_phase', QR, 'This trial is phase 3.'),
    ('meta_missing_negation', QR, 'This drug is not in trials.'),
    ('meta_missing_count', QS, 'It has 14 trials.'),
    ('meta_no_subject_phase', QR, 'phase 3.'),
    ('meta_no_subject_negation', QR, 'No trials.'),
    ('meta_context_phase', QR, 'NCT03909334 evaluates osimertinib.\nThis trial is phase 3.'),
    ('verbatim_antecedent_trial', QR, 'NCT03909334 (PHASE2, ACTIVE_NOT_RECRUITING) evaluates OSIMERTINIB. It is phase 3.'),
    ('verbatim_antecedent_typed_trial', QR, 'NCT03909334 (PHASE2, ACTIVE_NOT_RECRUITING) evaluates OSIMERTINIB. This trial is phase 3.'),
    ('verbatim_phase_changed_punctuation', QR, 'NCT03909334 (PHASE2, ACTIVE NOT RECRUITING) evaluates OSIMERTINIB.'),
    ('citation_embedded_claim', QT, 'Osimertinib [ORG:is safe] acts on EGFR.'),
    ('citation_embedded_negation', QT, 'Osimertinib [ORG:does not] act on EGFR.'),
    ('citation_embedded_wrong_relation', QT, 'Osimertinib [ORG:inhibits ALK and] acts on EGFR.'),
    ('clinical_removed_scope', QT, 'Osimertinib is for lung cancer.'),
    ('disease_as_assertion', QT, 'Osimertinib is lung cancer.'),
    ('number_units_count_as_phase', QA, 'LORLATINIB has 13 phase trials.'),
    ('partial_phase_1_from_12', QA, 'CONTELTINIB is phase 1.'),
    ('question_not_claim', QT, 'Does osimertinib act on EGFR?'),
    ('no_antecedent_control', QT, 'It inhibits EGFR.'),
    ('safe_control', QT, 'Osimertinib is safe.'),
    ('verbatim_control', QT, 'OSIMERTINIB acts on EGFR (inhibitor)'),
    ('verbatim_trial_control', QR, 'NCT03909334 (PHASE2, ACTIVE_NOT_RECRUITING) evaluates OSIMERTINIB. It is phase 2.'),
    ('paraphrase_trial_wrong_phase_control', QR, 'NCT03909334 evaluates osimertinib. It is phase 3.'),
    ('refusal_context_control', QT, 'This graph cannot answer that question.'),
    ('meta_missing_unsupported_phase', QR, 'This trial is phase 4.'),
    ('meta_france_unsupported_phase', 'What is the capital of France?', 'This trial is phase 4.'),
    ('dedup_same_unit', QT, 'Osimertinib is safe and EGFR is safe.'),
]

rows = []
for cid, q, answer in cases:
    result = engine.check(q, answer)
    entities = engine.kg.link_entities(q)
    evidence = engine.kg.retrieve(engine.kg.classify(q, entities), entities)
    row = {'id': cid, 'question': q, 'answer': answer, 'result': result,
           'units': _units(answer), 'raw_findings': check_claims(answer, evidence, engine.kg.link_entities),
           'answer_entities': engine.kg.link_entities(answer),
           'evidence': [vars(e) for e in evidence]}
    rows.append(row)
    print(json.dumps({'id': cid, 'grounded': result['checks']['grounded'],
                      'findings': [(f['kind'], f['value']) for f in result['checks']['unsupported_claims']]}, ensure_ascii=True))
Path(__file__).with_suffix('.json').write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding='utf-8')
