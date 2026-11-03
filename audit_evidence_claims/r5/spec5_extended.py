import sys,json
from pathlib import Path
sys.path.insert(0,str(Path("src").resolve()))
from app import Engine
e=Engine()
Q={"Q1":"Which companies are developing osimertinib?", "Q2":"What trials evaluate Tagrisso?", "Q3":"What does osimertinib target?", "Q4":"Which drugs act on ALK?", "Q5":"What is AstraZeneca running in NSCLC?"}
cases=[
("heading_wrong_kind_companies","Q3","The following companies inhibit EGFR:\n- Osimertinib"),
("heading_wrong_kind_trials","Q3","These trials:\n- Osimertinib"),
("heading_wrong_kind_drug","Q3","These drugs:\n- EGFR"),
("heading_wrong_kind_org","Q3","These organisations inhibit EGFR:\n- Osimertinib"),
("heading_wrong_kind_bare","Q3","Companies inhibiting EGFR:\n- Osimertinib"),
("heading_right_kind","Q3","The following drugs inhibit EGFR:\n- Osimertinib"),
("heading_nsclc_rel","Q3","The following NSCLC drugs inhibit EGFR:\n- Osimertinib"),
("heading_nsclc_trial","Q3","These NSCLC trials:\n- Osimertinib"),
("heading_safe","Q3","The following safe drugs inhibit EGFR:\n- Osimertinib"),
("heading_safe_company","Q3","These safe companies inhibit EGFR:\n- Osimertinib"),
("kind_relative","Q3","EGFR, which is inhibited by osimertinib, is a drug."),
("kind_relative_that","Q3","EGFR that is inhibited by osimertinib is a drug."),
("kind_relative_drug_faithful","Q3","Osimertinib, which inhibits EGFR, is a drug."),
("kind_before_noun_faithful","Q3","The drug osimertinib inhibits EGFR."),
("kind_before_noun_wrong","Q3","The company osimertinib inhibits EGFR."),
("group_shared_clinical","Q4","LORLATINIB and PLB1003 are in clinical trials."),
("group_shared_trials","Q4","LORLATINIB and PLB1003 have clinical trials in this graph."),
("group_shared_nsclc","Q4","LORLATINIB and PLB1003 have NSCLC trials."),
("group_shared_nsclc_reverse","Q4","PLB1003 and LORLATINIB have NSCLC trials."),
("group_shared_clinical_pron_survive","Q4","LORLATINIB and PLB1003 inhibit ALK. They inhibit ALK. They have clinical trials."),
("group_shared_clinical_elided","Q4","LORLATINIB and PLB1003 inhibit ALK and have clinical trials."),
("group_shared_clinical_subjectless_after_passive","Q4","ALK is targeted by LORLATINIB and PLB1003 and is approved."),
("passive_it_drug_kind","Q4","ALK is targeted by LORLATINIB and PLB1003. It is a drug."),
("passive_they_drug_kind","Q4","ALK is targeted by LORLATINIB and PLB1003. They are drugs."),
("passive_they_clinical","Q4","ALK is targeted by LORLATINIB and PLB1003. They have clinical trials."),
("passive_it_clinical","Q4","ALK is targeted by LORLATINIB and PLB1003. It has clinical trials."),
("passive_it_clinical_reverse","Q4","ALK is targeted by PLB1003 and LORLATINIB. It has clinical trials."),
("object_them_faithful","Q4","LORLATINIB and CRIZOTINIB inhibit ALK. ALK is targeted by them."),
("object_them_wrong","Q4","LORLATINIB and PLB1003 inhibit ALK. EGFR is targeted by them."),
("object_them_borrow","Q4","LORLATINIB and PLB1003 inhibit ALK. They are approved and ALK is targeted by them."),
("object_them_then_approval","Q4","LORLATINIB and PLB1003 inhibit ALK. ALK is targeted by them. They are approved."),
("object_them_then_it","Q4","LORLATINIB and PLB1003 inhibit ALK. ALK is targeted by them. It is approved."),
]
out=[]
for id,q,a in cases:
 r=e.check(Q[q],a)
 out.append(dict(id=id,question=Q[q],answer=a,**r))
 print(id,r["checks"]["grounded"],[(f["kind"],f["value"]) for f in r["checks"]["unsupported_claims"]])
Path("audit_evidence_claims/r5/spec5_extended.json").write_text(json.dumps(out,indent=2,ensure_ascii=False),encoding="utf8")
