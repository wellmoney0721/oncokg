"""Independent final confirmations; no source, graph or tracked files are edited."""
import hashlib
import json
import subprocess
import sys
from pathlib import Path
sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'src'))
from app import Engine
engine = Engine()
Q = {1:'Which companies are developing osimertinib?',2:'What trials evaluate Tagrisso?',3:'What does osimertinib target?',4:'Which drugs act on ALK?',5:'What is AstraZeneca running in NSCLC?'}
CASES = [
('B1_relative_status',2,'NCT03909334 (which is phase 2) and NCT07680790 are recruiting.'),
('B1_relative_phase',2,'NCT03909334, which evaluates osimertinib, and NCT07680790 are phase 3.'),
('B1_original_fixed',2,'NCT03909334 (phase 2) and NCT07680790 (phase 3) are recruiting.'),
('B1_faithful_status',2,'NCT07738172 (which is phase 3) and NCT07680790 are recruiting.'),
('B1_faithful_phase',2,'NCT02411448, which evaluates osimertinib, and NCT07680790 are phase 3.'),
('B2_record_status',2,'The graph records NCT03909334 (phase 2) and NCT07680790 (phase 3) as recruiting trials.'),
('B2_record_status_plain',2,'The graph records NCT03909334 and NCT07680790 as recruiting trials.'),
('B2_record_status_reverse',2,'The graph records NCT07680790 (phase 3) and NCT03909334 (phase 2) as recruiting trials.'),
('B2_record_status_faithful',2,'The graph records NCT07738172 (phase 3) and NCT07680790 (phase 3) as recruiting trials.'),
('B3_count_after_entities',5,'AstraZeneca sponsors trials of osimertinib and carboplatin: 10.'),
('B3_count_after_entities_reverse',5,'AstraZeneca sponsors trials of carboplatin and osimertinib: 14.'),
('B3_count_original_fixed',5,'AstraZeneca sponsors osimertinib and carboplatin in trials in this graph: 10.'),
('B3_count_explicit_unit',5,'AstraZeneca sponsors trials of osimertinib and carboplatin: 10 trials.'),
('B3_count_faithful',5,'AstraZeneca sponsors 14 trials of osimertinib and 10 trials of carboplatin.'),
('B4_reference_interruption',5,'AstraZeneca sponsors trials of Tagrisso. AstraZeneca is a company. There are 10 such trials in this graph.'),
('B4_reference_interruption_short',5,'AstraZeneca sponsors trials of Tagrisso. It is a company. There are 10 such trials in this graph.'),
('B4_reference_original_fixed',5,'AstraZeneca sponsors trials of Tagrisso. There are 10 such trials in this graph.'),
('B4_reference_faithful',5,'AstraZeneca sponsors trials of Tagrisso. AstraZeneca is a company. There are 14 such trials in this graph.'),
('B5_record_group',4,'The graph records lorlatinib and PLB1003 in clinical trials.'),
('B5_record_group_reverse',4,'The graph records PLB1003 and lorlatinib in clinical trials.'),
('B5_record_group_faithful',4,'The graph records lorlatinib and crizotinib in clinical trials.'),
('B6_kind_relative',3,'Osimertinib inhibits EGFR, which is a drug.'),
('B6_kind_relative_faithful',3,'EGFR is inhibited by osimertinib, which is a drug.'),
('B6_kind_group',3,'Osimertinib and EGFR are drugs.'),
('B6_kind_group_reverse',3,'EGFR and osimertinib are drugs.'),
('B6_trial_kind_group',2,'NCT07680790 and osimertinib are clinical trials.'),
('B6_trial_kind_group_reverse',2,'Osimertinib and NCT07680790 are clinical trials.'),
('B6_trial_record_kind',2,'The graph records osimertinib as a clinical trial.'),
('B6_trial_record_kind_control',2,'Osimertinib is a clinical trial.'),
('B6_trial_record_faithful',2,'The graph records NCT07680790 as a clinical trial.'),
('B7_heading_sentence',3,'These drugs:\n- EGFR is inhibited by osimertinib.'),
('B7_heading_original_fixed',3,'These drugs:\n- EGFR'),
('B7_heading_faithful',3,'These drugs:\n- Osimertinib inhibits EGFR.'),
('B8_as_inhibitor_multirecord',4,'ALK is listed as an inhibitor of lorlatinib and crizotinib.'),
('B8_as_inhibitor_multirecord_bare',4,'ALK is an inhibitor of lorlatinib and crizotinib.'),
('B8_as_inhibitor_multirecord_faithful',4,'Lorlatinib and crizotinib are listed as inhibitors of ALK.'),
('N_as_inhibitor_reverse',3,'EGFR is listed as an inhibitor of osimertinib.'),
('N_as_inhibitor_plain',3,'EGFR is an inhibitor of osimertinib.'),
('N_as_inhibitor_faithful',3,'Osimertinib is listed as an inhibitor of EGFR.'),
('N_target_count_entry',4,'ALK: 13 trials of lorlatinib.'),
('S_entry_elided',5,'AstraZeneca: 14 trials of osimertinib; 10 trials of carboplatin.'),
('S_noun_include',3,'Inhibitors of EGFR include osimertinib.'),
('S_noun_by',3,'Inhibition of EGFR by osimertinib is recorded.'),
]
rows=[]
for ident, q, answer in CASES:
    result=engine.check(Q[q],answer)
    entities=engine.kg.link_entities(Q[q])
    ev=engine.kg.retrieve(engine.kg.classify(Q[q],entities),entities)
    rows.append(dict(id=ident,question=Q[q],answer=answer,result=result,evidence=[vars(e) for e in ev]))
    print(json.dumps(dict(id=ident,grounded=result['checks']['grounded'],findings=[(f['kind'],f['value']) for f in result['checks']['unsupported_claims']]),ensure_ascii=False))
Path(__file__).with_suffix('.json').write_text(json.dumps(rows,indent=2,ensure_ascii=False),encoding='utf-8')
files=['src/claims.py','src/query.py','src/app.py','data/processed/oncokg.sqlite','README.md','README.ko.md']
verification={'head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
 'tracked_diff':subprocess.check_output(['git','diff','--numstat'],cwd=ROOT,text=True),
 'staged_diff':subprocess.check_output(['git','diff','--cached','--numstat'],cwd=ROOT,text=True),
 'sha256':{f:hashlib.sha256((ROOT/f).read_bytes()).hexdigest() for f in files if (ROOT/f).exists()}}
(Path(__file__).parent/'root6_verification.json').write_text(json.dumps(verification,indent=2),encoding='utf-8')
