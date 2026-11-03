import sys,json
from pathlib import Path
sys.path.insert(0,str(Path("src").resolve()))
from app import Engine
e=Engine()
q="What is AstraZeneca running in NSCLC?"
cases=[("wrong_such", "AstraZeneca sponsors trials of Tagrisso. There are 10 such trials in this graph."),("right_such", "AstraZeneca sponsors trials of Tagrisso. There are 14 such trials in this graph."),("wrong_such_elided", "AstraZeneca sponsors trials of Tagrisso and has 10 such trials."),("wrong_typed", "AstraZeneca sponsors trials of Tagrisso. This drug has 10 such trials in this graph."),("wrong_single", "AstraZeneca sponsors 10 trials of Tagrisso.")]
entities=e.kg.link_entities(q);ev=e.kg.retrieve(e.kg.classify(q,entities),entities)
out=[]
for id,a in cases:
 r=e.check(q,a)
 out.append(dict(id=id,question=q,answer=a,**r,full_evidence=[vars(x) for x in ev]))
 print(id,r["checks"]["grounded"],[(f["kind"],f["value"]) for f in r["checks"]["unsupported_claims"]])
Path("audit_evidence_claims/r6/replay6_r5_spec5_anaphora.json").write_text(json.dumps(out,indent=2,ensure_ascii=False),encoding="utf8")
