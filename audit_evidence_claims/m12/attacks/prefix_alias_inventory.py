import sys,json,re
from pathlib import Path
sys.dont_write_bytecode=True;sys.path.insert(0,str(Path.cwd()/'src'))
from app import Engine
import textrules as T,query
E=Engine();rows=[]
for key,hits in E.dic['index'].items():
 for h in hits:
  a=h['alias'];ws=query._alnum_words(a)
  if not ws:continue
  iso=next((' '.join(ws[:n]) for n in (1,2) if len(ws)>n and T.is_isotope_label(' '.join(ws[:n]))),None)
  if not iso:continue
  ik=T.canonical_key(iso);rest=key[len(ik):]
  if any(x['drug_id']==h['drug_id'] for x in E.dic['index'].get(rest,[])):continue
  rows.append({'alias':a,'drug':E.dic['drugs'][h['drug_id']]['name'],'id':h['drug_id'],'isotope':iso,'rest':rest})
print(json.dumps(rows,ensure_ascii=True,indent=2));Path('audit_evidence_claims/m12/attacks/prefix_alias_inventory.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf8')
