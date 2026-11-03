import sys,json
from pathlib import Path
sys.dont_write_bytecode=True
sys.path.insert(0,str(Path.cwd()/'src'))
from app import Engine
from claims import _strip_citations
x=Engine(); kg=x.kg
cases=[('trial_graph','Which drugs act on ALK?','PLB1003 inhibits ALK in clinical trials in this graph.'),('heading_approved','What does osimertinib target?','The following approved drugs:\n- Osimertinib inhibits EGFR.'),('heading_nonrecruiting','What trials evaluate Tagrisso?','The following nonrecruiting trials:\n- NCT07680790 (PHASE3, RECRUITING) evaluates OSIMERTINIB.'),('kind_trial_drug','What trials evaluate Tagrisso?','NCT07680790 is a drug that evaluates osimertinib.'),('head_lower_control','What does osimertinib target?','safe drugs:\n- OSIMERTINIB acts on EGFR (inhibitor).')]
rows=[]
for ident,q,a in cases:
 r=x.check(q,a); rows.append(dict(id=ident,question=q,answer=a,result=r));print(ident,r['checks'])
q='Which drugs act on ALK?';a='PLB1003 inhibits ALK in clinical trials in this graph.'
ents=kg.link_entities(q);evidence=kg.retrieve(kg.classify(q,ents),ents)
for mode,ev in [('full',evidence),('plb_only',[e for e in evidence if e.statement.startswith('PLB1003 ')])]:
 r=kg.check_groundedness(a,ev,ents,True,set(kg.dic['index']),linker=kg.link_entities)
 rows.append(dict(id='trial_scope_'+mode,question=q,answer=a,evidence=[e.statement for e in ev],checks=r));print(mode,r)
q='What does osimertinib target?';ents=kg.link_entities(q);ev=kg.retrieve(kg.classify(q,ents),ents)
import re
known=set()
for e in ev:
 for part in [e.source_record or '',e.edge_id or '',e.statement or '']:
  known|={s.strip().lower() for s in re.split(r'[,;\s|]+',part) if s.strip()}
for a in ['[CHEMBL3353410]','[CHEMBL3353410, ENSG00000146648]','[CHEMBL3353410 ENSG00000146648]','[ORG:is-safe]']:
 rows.append(dict(id='citation_transform',input=a,output=_strip_citations(a,known),known=sorted(known)))
Path('audit_evidence_claims/r4_recheck/docs_diagnostics_results.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
