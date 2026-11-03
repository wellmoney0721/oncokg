import sys,json
from pathlib import Path
sys.path.insert(0,str(Path("src").resolve()))
from app import Engine
e=Engine()
Q={"Q1":"Which companies are developing osimertinib?", "Q2":"What trials evaluate Tagrisso?", "Q3":"What does osimertinib target?", "Q4":"Which drugs act on ALK?", "Q5":"What is AstraZeneca running in NSCLC?"}
cases=[
("identity_explicit","Q4","PLB1003 is LORLATINIB."),
("identity_elided","Q3","Osimertinib inhibits EGFR and is EGFR."),
("identity_alias_faithful","Q3","Osimertinib is Tagrisso."),
("group_survival_r4","Q4","PLB1003 and LORLATINIB act on ALK and they act on ALK and they are approved."),
("group_survival_faithful","Q4","CRIZOTINIB and LORLATINIB act on ALK and they act on ALK and they are approved."),
("group_elided_r4","Q4","LORLATINIB and PLB1003 act on ALK and are approved."),
("object_them_count_r4","Q5","AstraZeneca sponsors osimertinib and carboplatin. It sponsors them in 10 trials."),
("kind_original_r4","Q3","EGFR is a drug inhibited by osimertinib."),
("clinical_original_r4","Q4","PLB1003 inhibits ALK in clinical trials in this graph."),
("clinical_group_graph","Q4","LORLATINIB and PLB1003 have clinical trials in this graph."),
("clinical_group_graph_reverse","Q4","PLB1003 and LORLATINIB have clinical trials in this graph."),
("kind_control_drug","Q3","EGFR is a drug."),
("nsclc_control","Q3","Osimertinib is an NSCLC drug."),
]
out=[]
for id,q,a in cases:
 r=e.check(Q[q],a)
 entities=e.kg.link_entities(Q[q]);ev=e.kg.retrieve(e.kg.classify(Q[q],entities),entities)
 out.append(dict(id=id,question=Q[q],answer=a,**r,full_evidence=[vars(x) for x in ev]))
 print(id,r["checks"]["grounded"],[(f["kind"],f["value"]) for f in r["checks"]["unsupported_claims"]])
Path("audit_evidence_claims/r6/replay6_r5_spec5_controls.json").write_text(json.dumps(out,indent=2,ensure_ascii=False),encoding="utf8")
