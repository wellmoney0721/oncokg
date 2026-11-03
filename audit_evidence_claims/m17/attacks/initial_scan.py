import json,sqlite3,sys
from pathlib import Path
sys.dont_write_bytecode=True
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2]
sys.path.insert(0,str(ROOT/'src'))
import query,textrules as T
from app import Engine
e=Engine();e.kg.conn.close();e.kg.conn=sqlite3.connect((ROOT/'data/processed/oncokg.sqlite').as_uri()+'?mode=ro',uri=True);e.kg.conn.row_factory=sqlite3.Row
cases=[
'iodine-I-124 trastuzumab','iodine-I124 trastuzumab','iodine I-124 trastuzumab','I-124-labelled trastuzumab','trastuzumab labelled-I-124','trastuzumab labelled-with-I-124','trastuzumab radiolabeled-I124','trastuzumab (iodine-I-124)','trastuzumab iodine-I-124','trastuzumab [iodine-I-124]','trastuzumab 124-Iodine','trastuzumab iodine-124','trastuzumab iodine124','trastuzumab 124iodine',
'carbon-C14 paclitaxel','carbon-C-14 paclitaxel','carbon C14 paclitaxel','fluorine-F18 erlotinib','fluorine-F-18 erlotinib','fluorine F18 erlotinib','yttrium-Y-90 cetuximab','yttrium Y-90 cetuximab',
'DFO-I-124 trastuzumab','DFO-124I trastuzumab','I-124-DFO trastuzumab','N-succinimidyl-I-124 trastuzumab','I-124 trastuzumab, osimertinib','iodine-I-124 trastuzumab, osimertinib','osimertinib, iodine-I-124 trastuzumab',
'trastuzumab I-124','trastuzumab 124I','vinblastine H3','vinblastine tritium-H3','vinblastine tritium-H-3','tritium-H-3 vinblastine','vinblastine H-3','vinblastine 3H',
'osimertinib 80 mg','paclitaxel 2 cycles','cisplatin 75 mg/m2 day 1','13-cis retinoic acid','BKM120','AZD9291',
]
rows=[]
for text in cases:
    m=e.explore(text,2);r=e.resolve(text);li=e.kg.link_entities(text)
    rows.append({'text':text,'key':T.canonical_key(text),'item_has_isotope':query._item_has_isotope(tuple(text.split())),'qualified':query._qualified(text.split()),'blocked':e.kg._resolver_blocked(text),'resolver_tiers':[x['tier'] for x in r['components']],'linker':li,'map':m})
(OUT/'initial_scan.json').write_text(json.dumps(rows,indent=2,ensure_ascii=False),encoding='utf8')
print(json.dumps([{'text':r['text'],'center':r['map'].get('center',{}).get('label'),'refused':r['map'].get('refused'),'item':r['item_has_isotope'],'qualified':r['qualified'],'blocked':r['blocked'],'tiers':r['resolver_tiers']} for r in rows],indent=2,ensure_ascii=False))
e.kg.conn.close()
