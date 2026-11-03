import sys,json,sqlite3
from pathlib import Path
sys.dont_write_bytecode=True
OUT=Path(__file__).resolve().parent; ROOT=OUT.parents[2]
sys.path.insert(0,str(ROOT/'src'))
import query,textrules as T
from app import Engine
e=Engine();e.kg.conn.close();e.kg.conn=sqlite3.connect((ROOT/'data/processed/oncokg.sqlite').as_uri()+'?mode=ro',uri=True);e.kg.conn.row_factory=sqlite3.Row
cases=['trastuzumab I124','trastuzumab I-124','I124 trastuzumab','I-124 trastuzumab','trastuzumab iodine-124','124I trastuzumab','trastuzumab 124I','DFOI124 trastuzumab','I124DFO trastuzumab','18FDFO trastuzumab','18-FDFO trastuzumab','18 FDFO trastuzumab','18 F DFO trastuzumab','F18DFO trastuzumab','3 Hvinblastine','3 H vinblastine','H3vinblastine','vinblastine H3','trastuzumab 63CuDFO','trastuzumab 60CuDFO','trastuzumab 67CuDFO','trastuzumab 72AsDFO','trastuzumab Ga-68','trastuzumab 89Zr','trastuzumab 89-ZrDFO','trastuzumab DFO89-Zr','18F FLUDEOXYGLUCOSE','131I IOBENGUANE','124I IOBENGUANE','IOBENGUANE I 131','177Lu DOTATATE']
rows=[]
for s in cases:
 r=e.explore(s,2)
 rows.append({'text':s,'medical':query._medical_isotope_in(T.canonical_key(s)), 'medical_two':query._medical_isotope_in(T.canonical_key(s),False),'qualified':query._qualified(s.split()),'map':r,'links':e.kg.link_entities(s)})
(OUT/'initial_scan.json').write_text(json.dumps(rows,indent=2,ensure_ascii=False),encoding='utf8')
print(json.dumps([{'text':r['text'],'center':r['map'].get('center',{}).get('label'),'refused':r['map'].get('refused'),'medical':r['medical'],'qualified':r['qualified']} for r in rows],indent=2))
labelled=[{'id':d,'name':v['name']} for d,v in e.dic['drugs'].items() if query._labelled(v['name'])]
(OUT/'labelled_names.json').write_text(json.dumps(labelled,indent=2),encoding='utf8');print('LABELLED',json.dumps(labelled))
