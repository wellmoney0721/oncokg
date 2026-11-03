"""Fresh root-agent confirmation of independently reported R4 findings."""
import json, sys, hashlib, subprocess
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2]
OUT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'src'))
from app import Engine
engine=Engine()
Q={2:'What trials evaluate Tagrisso?',3:'What does osimertinib target?',4:'Which drugs act on ALK?',5:'What is AstraZeneca running in NSCLC?'}
cases=[
 ('heading_safe',3,'The following safe drugs:\n- OSIMERTINIB acts on EGFR (inhibitor).',True),
 ('heading_discontinued',3,'The following discontinued drugs:\n- OSIMERTINIB acts on EGFR (inhibitor).',True),
 ('heading_safe_control',3,'These drugs are safe:\n- OSIMERTINIB acts on EGFR (inhibitor).',False),
 ('heading_safe_bare',3,'The following safe drugs:\n- Osimertinib',True),
 ('plural_chain',4,'PLB1003 and LORLATINIB act on ALK and they act on ALK and they are approved.',True),
 ('plural_original_fixed',4,'LORLATINIB and PLB1003 act on ALK and they are approved.',False),
 ('plural_implicit',4,'LORLATINIB and PLB1003 act on ALK and are approved.',True),
 ('object_count',5,'AstraZeneca sponsors osimertinib and carboplatin. It sponsors them in 10 trials.',True),
 ('colon_count',5,'AstraZeneca sponsors osimertinib and carboplatin in trials: 10.',True),
 ('prefix_count_control',5,'AstraZeneca sponsors osimertinib and carboplatin in 10 trials.',False),
 ('trial_group_status',2,'NCT03909334 and NCT07680790 are recruiting trials of osimertinib.',True),
 ('trial_group_phase',2,'NCT03909334 and NCT07680790 are phase 3 trials of osimertinib.',True),
 ('trial_status_prefix',2,'Recruiting trials evaluating osimertinib include NCT07680790 and NCT03909334.',True),
 ('trial_status_swap',2,'Recruiting trials evaluating osimertinib include NCT03909334 and NCT07680790.',False),
 ('kind_drug',3,'EGFR is a drug inhibited by osimertinib.',True),
 ('kind_drug_control',3,'EGFR is a drug.',False),
 ('clinical_trial',4,'PLB1003 acts on ALK in clinical trials.',True),
 ('clinical_trial_control',4,'PLB1003 has clinical trials.',False),
 ('nsclc_residue',4,'PLB1003 acts on ALK in NSCLC trials.',True),
 ('faithful_capital_they',4,'LORLATINIB and CRIZOTINIB act on ALK. They are approved.',False),
 ('faithful_lower_they',4,'LORLATINIB and CRIZOTINIB act on ALK. they are approved.',True),
 ('faithful_two_phases',2,'NCT07680790 and NCT02411448 are phase 3.',False),
 ('faithful_count_alias',5,'AstraZeneca sponsors 14 trials of osimertinib (Tagrisso).',False),
 ('faithful_count',5,'AstraZeneca sponsors 14 trials of osimertinib.',True),
 ('split_negation',3,'Osimertinib does N O T inhibit EGFR.',True),
]
rows=[]
for ident,q,answer,expected in cases:
    res=engine.check(Q[q],answer)
    entities=engine.kg.link_entities(Q[q]); ev=engine.kg.retrieve(engine.kg.classify(Q[q],entities),entities)
    row=dict(id=ident,question=Q[q],answer=answer,expected_observed_grounded=expected,result=res,evidence=[vars(e) for e in ev])
    rows.append(row)
    # Historical expected value retained as metadata, not asserted after repairs.
    print(json.dumps(dict(id=ident,grounded=res['checks']['grounded'],findings=[(f['kind'],f['value']) for f in res['checks']['unsupported_claims']]),ensure_ascii=False))
OUT.joinpath('replay5_r4_root4_confirmation.json').write_text(json.dumps(rows,indent=2,ensure_ascii=False),encoding='utf-8')
verified={
 'head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
 'critical_cases':len(rows),
 'tracked_diff_exit':subprocess.run(['git','diff','--quiet'],cwd=ROOT).returncode,
 'staged_diff_exit':subprocess.run(['git','diff','--cached','--quiet'],cwd=ROOT).returncode,
 'sha256':{str(p):hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in ['src/claims.py','src/query.py','src/app.py','README.md','README.ko.md','web/template.html','web/try.html','tests/test_claims.py','data/processed/oncokg.sqlite']},
}
OUT.joinpath('replay5_r4_root4_verification.json').write_text(json.dumps(verified,indent=2),encoding='utf-8')
