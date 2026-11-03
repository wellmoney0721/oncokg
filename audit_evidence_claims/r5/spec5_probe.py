import sys,json
from pathlib import Path
sys.path.insert(0,str(Path("src").resolve()))
from app import Engine
e=Engine()
Q={"Q1":"Which companies are developing osimertinib?", "Q2":"What trials evaluate Tagrisso?", "Q3":"What does osimertinib target?", "Q4":"Which drugs act on ALK?", "Q5":"What is AstraZeneca running in NSCLC?"}
cases=[
("passive_it_approval","Q4","ALK is targeted by LORLATINIB and PLB1003. It is approved."),
("passive_they_approval","Q4","ALK is targeted by LORLATINIB and PLB1003. They are approved."),
("kind_intervening","Q3","EGFR, inhibited by osimertinib, is a drug."),
("kind_intervening2","Q3","EGFR is inhibited by osimertinib and is a drug."),
("kind_faithful","Q3","EGFR is inhibited by the drug osimertinib."),
("group_clinical","Q4","LORLATINIB and PLB1003 inhibit ALK in clinical trials."),
("group_clinical_reverse","Q4","PLB1003 and LORLATINIB inhibit ALK in clinical trials."),
("group_clinical_pron","Q4","LORLATINIB and PLB1003 inhibit ALK. They are in clinical trials."),
("heading_nsclc","Q3","These NSCLC drugs:\n- Osimertinib"),
("heading_nsclc_plain","Q3","Osimertinib is an NSCLC drug."),
("kind_intervening_identity","Q3","EGFR, inhibited by osimertinib, is osimertinib."),
("group_both_clinical","Q4","LORLATINIB and CRIZOTINIB inhibit ALK in clinical trials."),
]
out=[]
for id,q,a in cases:
 r=e.check(Q[q],a)
 out.append(dict(id=id,question=Q[q],answer=a,**r))
 print(id,r["checks"]["grounded"],[(f["kind"],f["value"]) for f in r["checks"]["unsupported_claims"]])
Path("audit_evidence_claims/r5/spec5_probe.json").write_text(json.dumps(out,indent=2,ensure_ascii=False),encoding="utf8")
