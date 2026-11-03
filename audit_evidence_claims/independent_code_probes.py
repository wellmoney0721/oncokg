import sys, json
from pathlib import Path
sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from app import Engine
from claims import check_claims, _units
eng = Engine()
kg = eng.kg
cases = [
    ('dedup', 'What does osimertinib target?', 'osimertinib is safe. osimertinib is safe for all.'),
    ('inheritance_same_line', 'What trials evaluate Tagrisso?', 'NCT03909334 is ACTIVE_NOT_RECRUITING. It is recruiting.'),
    ('inheritance_new_line', 'What trials evaluate Tagrisso?', 'NCT03909334 is ACTIVE_NOT_RECRUITING.\nIt is recruiting.'),
    ('missing_relation_arguments', 'What does osimertinib target?', 'osimertinib is a drug. It sponsors EGFR.'),
    ('missing_relation_arguments_new_line', 'What does osimertinib target?', 'osimertinib is a drug.\nIt sponsors EGFR.'),
    ('non_negation', 'What does osimertinib target?', 'osimertinib is non-inhibiting EGFR.'),
    ('non_negation_trial', 'What trials evaluate Tagrisso?', 'NCT07680790 is non-recruiting.'),
    ('phase_suffix', 'What trials evaluate Tagrisso?', 'NCT07680790 is phase 3b.'),
    ('clinical_grammar', 'What does osimertinib target?', 'osimertinib is an EGFR inhibitor. the inhibitor acts on all cancer.'),
    ('quoted_developing', 'Which companies are developing osimertinib?', 'AstraZeneca is developing the drug osimertinib.'),
    ('quoted_development_evidence', 'Which companies are developing osimertinib?', 'AstraZeneca has evidence of developing osimertinib.'),
]
out=[]
for tag,q,a in cases:
    r=eng.check(q,a)
    ents=kg.link_entities(q)
    ev=kg.retrieve(kg.classify(q,ents),ents)
    out.append({'tag':tag,'question':q,'answer':a,'units':_units(a),'raw_claims':check_claims(a,ev,kg.link_entities),'result':r})
    print(json.dumps({'tag':tag,'question':q,'answer':a,'checks':r['checks']},ensure_ascii=False))
Path(__file__).with_suffix('.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8')
