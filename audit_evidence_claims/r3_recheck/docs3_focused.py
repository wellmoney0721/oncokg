import sys,json
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'src'))
from app import Engine
from dataclasses import asdict
x=Engine(); kg=x.kg
Q3='What does osimertinib target?';Q4='Which drugs act on ALK?';Q6='What is the capital of France?'
cases=[
(Q3,'Osimertinib is in clinical trials.'),(Q3,'This drug is in clinical trials.'),(Q3,'Osimertinib has clinical trials.'),
(Q3,'Osimertinib is a clinical trial.'),(Q3,'Osimertinib is in NSCLC trials.'),(Q3,'Osimertinib is a drug for use in NSCLC.'),
(Q3,'EGFR is a drug.'),(Q3,'EGFR is an organisation.'),(Q4,'ALK is a company.'),
(Q6,'There are clinical trials.'),(Q6,'The trial is clinical.'),
(Q3,'Osimertinib is approved in NSCLC.'),(Q4,'Lorlatinib is approved in NSCLC.'),(Q4,'Lorlatinib is approved for NSCLC drugs.'),
(Q4,'Lorlatinib is approved for NSCLC trials.'),(Q4,'Lorlatinib is approved in lung cancer.'),
(Q3,'Osimertinib is safe [ORG:safe].'),
(Q3,'Osimertinib [ORG:is-safe] acts on EGFR.'),(Q3,'Osimertinib [ORG:inhibits-ALK] acts on EGFR.'),(Q3,'Osimertinib [ORG:does-not-inhibit] acts on EGFR.'),
]
rows=[]
for i,(q,a) in enumerate(cases,1):
 r=x.check(q,a); en=kg.link_entities(q); ev=kg.retrieve(kg.classify(q,en),en)
 rows.append(dict(id=f'focused_{i:02}',question=q,answer=a,result=r,full_evidence=[asdict(e) for e in ev]))
 print(i,r['checks']['grounded'],[(f['kind'],f['value']) for f in r['checks']['unsupported_claims']],repr(a))
Path(__file__).with_name('docs3_focused_results.json').write_text(json.dumps(rows,indent=2,ensure_ascii=False),encoding='utf-8')
