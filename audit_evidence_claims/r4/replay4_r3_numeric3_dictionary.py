import sys, json, re
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT/'src'))
from app import Engine
from claims import _tokenise
e=Engine()
alias_rows=[]
for hits in e.dic['index'].values():
 for hit in hits:
  if re.search(r'\s',hit['alias']):
   alias_rows.append((hit['alias'],hit['drug_id']))
aliases=sorted({a for a,_ in alias_rows})
losses=[]; linked_count=0
for alias in aliases:
 linked=e.kg.link_entities(alias)
 before={x['id'] for x in linked if x['type']=='Drug'}
 expected={d for a,d in alias_rows if a==alias}
 intended=before&expected
 if not intended: continue
 linked_count+=1
 _,entities=_tokenise(alias,e.kg.link_entities)
 after={x.get('id') for x in entities if x['type']=='Drug'}
 if not intended&after:
  losses.append(dict(alias=alias,linked=linked,token_entities=entities))
out=dict(dictionary_keys=len(e.dic['index']),drugs=len(e.dic['drugs']),unique_multiword_aliases=len(aliases),intended_linked_aliases=linked_count,lost_intended_links=losses)
Path(__file__).with_suffix('.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(out,ensure_ascii=True,indent=2))
