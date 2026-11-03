"""Independent confirmation of R5 findings on unmodified real-graph retrievals."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path
sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'src'))
from app import Engine
engine = Engine()
Q = {2:'What trials evaluate Tagrisso?',3:'What does osimertinib target?',
     4:'Which drugs act on ALK?',5:'What is AstraZeneca running in NSCLC?'}
CASES = [
 ('B1_heading_kind',3,'The following companies inhibit EGFR:\n- Osimertinib',True),
 ('B1_heading_kind_control',3,'Companies inhibiting EGFR:\n- Osimertinib',False),
 ('B1_heading_disease',3,'These NSCLC drugs:\n- Osimertinib',True),
 ('B1_heading_disease_control',3,'Osimertinib is an NSCLC drug.',False),
 ('B1_heading_adjective_fixed',3,'The following safe drugs:\n- Osimertinib',False),
 ('B1_heading_faithful',3,'The following drugs inhibit EGFR:\n- Osimertinib',True),
 ('B2_group_clinical',4,'LORLATINIB and PLB1003 are in clinical trials.',True),
 ('B2_group_clinical_reverse',4,'PLB1003 and LORLATINIB are in clinical trials.',False),
 ('B2_group_clinical_relation',4,'LORLATINIB and PLB1003 inhibit ALK in clinical trials.',True),
 ('B2_singular_clinical_control',4,'PLB1003 is in clinical trials.',False),
 ('B3_passive_it',4,'ALK is targeted by LORLATINIB and PLB1003. It is approved.',True),
 ('B3_passive_they_control',4,'ALK is targeted by LORLATINIB and PLB1003. They are approved.',False),
 ('B3_active_it_control',4,'LORLATINIB and PLB1003 target ALK. It is approved.',False),
 ('B3_passive_faithful',4,'ALK is targeted by LORLATINIB and CRIZOTINIB. They are approved.',True),
 ('B4_status_parenthetical',2,'NCT03909334 (phase 2) and NCT07680790 (phase 3) are recruiting.',True),
 ('B4_status_reverse',2,'NCT07680790 (phase 3) and NCT03909334 (phase 2) are recruiting.',False),
 ('B4_status_plain_control',2,'NCT03909334 and NCT07680790 are recruiting.',False),
 ('B4_phase_parenthetical',2,'NCT03909334 (active, not recruiting) and NCT07680790 are phase 3.',True),
 ('B4_phase_plain_control',2,'NCT03909334 and NCT07680790 are phase 3.',False),
 ('B4_phase_faithful',2,'NCT07680790 and NCT02411448 are phase 3.',True),
 ('B5_long_count_label',5,'AstraZeneca sponsors osimertinib and carboplatin in trials in this graph: 10.',True),
 ('B5_immediate_count_control',5,'AstraZeneca sponsors osimertinib and carboplatin in trials: 10.',False),
 ('B5_separate_count_faithful',5,'AstraZeneca sponsors 14 trials of osimertinib and 10 trials of carboplatin.',True),
 ('B6_relative_kind',3,'EGFR, which is inhibited by osimertinib, is a drug.',True),
 ('B6_prefix_kind',3,'The drug EGFR is inhibited by osimertinib.',True),
 ('B6_clinical_trial_identity',2,'Osimertinib is a clinical trial.',True),
 ('B6_clinical_trial_identity_scope_control',3,'Osimertinib is a clinical trial.',False),
 ('B6_simple_kind_control',3,'EGFR is a drug inhibited by osimertinib.',False),
 ('S1_faithful_relative_kind',3,'Osimertinib, which inhibits EGFR, is a drug.',False),
 ('S1_faithful_prefix_drug',3,'EGFR is inhibited by the drug osimertinib.',False),
 ('N_percent_attached',4,'LORLATINIB has 13% NSCLC trials.',False),
 ('N_percent_spaced',4,'LORLATINIB has 13 % NSCLC trials.',True),
 ('N_phase_digit_fixed',4,'PLB1003 has 1 phase.',False),
 ('N_identity_elided_fixed',3,'Osimertinib inhibits EGFR and is EGFR.',False),
]
rows=[]
for ident,q,answer,expected in CASES:
    result=engine.check(Q[q],answer)
    entities=engine.kg.link_entities(Q[q])
    ev=engine.kg.retrieve(engine.kg.classify(Q[q],entities),entities)
    row=dict(id=ident,question=Q[q],answer=answer,expected_grounded=expected,
             result=result,evidence=[vars(e) for e in ev])
    rows.append(row)
    print(('OK ' if result['checks']['grounded'] is not expected else 'SAME ') + str(result['checks']['grounded']), row['id'] if isinstance(row,dict) and 'id' in row else '', [(u['kind'],u['value']) for u in result['checks']['unsupported_claims']][:3])
    print(json.dumps(dict(id=ident,grounded=result['checks']['grounded'],
        findings=[(f['kind'],f['value']) for f in result['checks']['unsupported_claims']]),ensure_ascii=False))
OUT.joinpath('root5_confirmation.json').write_text(json.dumps(rows,indent=2,ensure_ascii=False),encoding='utf-8')
paths=['src/claims.py','src/query.py','src/app.py','tests/test_claims.py','README.md',
       'README.ko.md','web/template.html','web/try.html','CODEX_CLAIMS_R4_VERDICT.md',
       'data/processed/oncokg.sqlite']
verification=dict(head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
    cases=len(rows),
    tracked_diff_exit=subprocess.run(['git','diff','--quiet'],cwd=ROOT).returncode,
    staged_diff_exit=subprocess.run(['git','diff','--cached','--quiet'],cwd=ROOT).returncode,
    sha256={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in paths})
OUT.joinpath('root5_verification.json').write_text(json.dumps(verification,indent=2),encoding='utf-8')
