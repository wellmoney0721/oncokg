import json,sys
from pathlib import Path
sys.dont_write_bytecode=True
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2]
sys.path.insert(0,str(ROOT/'src'))
import query,textrules as T
load=lambda name:json.loads((OUT/name).read_text(encoding='utf8'))
summary={}
for family in ['focused','fresh','edge','targeted','new','previous']:
 r=load(family+'_results.json');summary[family]={'count':len(r['cases']),'head':r['head'],'previous':r['previous']}
rows={r['text']:r for r in load('new_results.json')['cases']}
primary=rows['trastuzumab labelled-I-124']['current']
assert primary['map']['center']['id']=='CHEMBL1201585' and primary['map']['center']['trials']==13
assert not primary['blocked'] and not primary['qualified'] and not primary['item_has_isotope']
assert not any(x['type']=='Refused' for x in primary['public_linker'])
assert primary['whole_name'] is None and all(x['result'] is None for x in primary['marked_calls'])
assert all(not x['tier'].startswith('BLOCKED') for x in primary['resolver']['components'])
assert len(primary['trial_qa']['evidence'])==len(primary['sponsor_qa']['evidence'])==12
for control in ['trastuzumab labelled-124I','I-124-labelled trastuzumab','trastuzumab labelled with I-124']:
 r=rows[control]['current'];assert r['map'].get('refused') and not r['map'].get('center')
 assert not r['trial_qa']['evidence'] and not r['sponsor_qa']['evidence']
for name in ['new_lifecycle.json','previous_lifecycle.json']:
 life=load(name);assert life['port_closed'] and life['database_unchanged'] and life['all_200'] and life['page_matches_worktree'];summary[name]=life
summary['alias_variants']=load('alias_variants_comparison.json');assert summary['alias_variants']['changes']==[]
summary['checks']='primary all-stage bypass, paired refusals, HTTP200, closed ports, same DB bytes, and same prior alias outcomes verified'
(OUT/'final_checks.json').write_text(json.dumps(summary,indent=2),encoding='utf8')
helpers=[]
for token in ['I-124','I-124-labelled','labelled-I-124','labelled-124I','iodine-I-124','BKM120','AZD9291','F18','labelled-F18','C14','labelled-C14','Y-90','labelled-Y-90']:
 helpers.append({'token':token,'canonical_key':T.canonical_key(token),'alnum_words':query._alnum_words(token),'item_has_isotope':query._item_has_isotope((token,))})
(OUT/'helper_evidence.json').write_text(json.dumps(helpers,indent=2),encoding='utf8')
print(json.dumps(summary,indent=2))
