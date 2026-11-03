import sys,json,re
from pathlib import Path
sys.dont_write_bytecode=True;sys.path.insert(0,str(Path.cwd()/'src'))
from app import Engine
import textrules as T,query
E=Engine();found=[]
for key,hits in E.dic['index'].items():
 for h in hits:
  a=h['alias'];ws=query._alnum_words(a)
  for i,w in enumerate(ws):
   if 0<i<len(ws)-1 and T.is_isotope_label(w):
    found.append({'alias':a,'drug':E.dic['drugs'][h['drug_id']]['name'],'id':h['drug_id'],'isotope':w})
print(json.dumps(found,ensure_ascii=True,indent=2));Path('audit_evidence_claims/m12/attacks/inside_alias_inventory.json').write_text(json.dumps(found,ensure_ascii=False,indent=2),encoding='utf8')
