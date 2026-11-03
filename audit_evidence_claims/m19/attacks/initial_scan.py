import json,sys,sqlite3,subprocess
from pathlib import Path
sys.dont_write_bytecode=True
OUT=Path(__file__).resolve().parent; ROOT=OUT.parents[2]
sys.path.insert(0,str(ROOT/'src'))
from app import Engine
import query
cases=[
 'radio-labelled trastuzumab','radiolabelled trastuzumab','radio-labeled trastuzumab','radio labeled trastuzumab','radio-labelled trastuzumab tracer','trastuzumab radio-tracer','trastuzumab radiotracer',
 'trastuzumab radioactively labelled','trastuzumab radioactively labeled','trastuzumab radioactive label','trastuzumab radioiodinated','trastuzumab radio-iodinated','trastuzumab radio iodinated',
 'iodine124 trastuzumab','iodine-124 trastuzumab','124iodine trastuzumab','124-iodine trastuzumab','trastuzumab iodine124',
 '99m-technetium trastuzumab','technetium-99m trastuzumab','99-technetium trastuzumab','technetium99m trastuzumab','99mtechnetium trastuzumab',
 'technetium metastable 99 trastuzumab','trastuzumab labelled with iodine 124','trastuzumab labelled with iodine (124)','trastuzumab labelled with iodine mass 124',
 'zirconium89 trastuzumab','zirconium-89 trastuzumab','89zirconium trastuzumab',
 'radioconjugated trastuzumab','trastuzumab radioimmunoconjugates','trastuzumab radionuclide-labelled','trastuzumab radionuclide labeled','trastuzumab isotopically labelled',
 'trastuzumab radio-labelled with iodine-124','trastuzumab radio-labelled with I-124','trastuzumab radio-labelled with 124I',
 'trastuzumab (radio-labelled)','radio-ligand trastuzumab','radio-immunoconjugate trastuzumab','radio-pharmaceutical trastuzumab',
 'osimertinib, radio-labelled trastuzumab','radio-labelled trastuzumab, osimertinib','radio-labelled trastuzumab and osimertinib',
 'unlabelled trastuzumab','non-radiolabelled trastuzumab','nonradioactive trastuzumab','trastuzumab',
 'fluorine-18 fluorodeoxyglucose','radio-labelled fluorodeoxyglucose','radio-labelled FDG','tritiated FDG','FDG labelled with carbon-14',
 'osimertinib 80 mg','paclitaxel 2 cycles','lead compound osimertinib'
]
e=Engine(); e.kg.conn.close();e.kg.conn=sqlite3.connect((ROOT/'data/processed/oncokg.sqlite').as_uri()+'?mode=ro',uri=True);e.kg.conn.row_factory=sqlite3.Row
rows=[]
for t in cases:
 r=e.explore(t,2); l=e.kg.link_entities(t); rs=e.resolve(t)
 rows.append({'text':t,'center':r.get('center',{}).get('label'),'map_refused':r.get('refused'),'link_refused':any(x['type']=='Refused' for x in l),'item_has_isotope':query._item_has_isotope(tuple(t.split())),'qualified':query._qualified(t.split()),'resolver_blocked':e.kg._resolver_blocked(query._fold(t)),'resolver_tiers':[x['tier'] for x in rs['components']],'linker':l,'map':r,'resolver':rs})
(OUT/'initial_scan.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps([{k:v for k,v in r.items() if k not in ['map','linker','resolver']} for r in rows],ensure_ascii=False,indent=2))
e.kg.conn.close()
