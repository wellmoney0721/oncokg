"""Focused earlier-finding matrix, using direct read-only Engine calls."""
from pathlib import Path
import json,sys,sqlite3
sys.path.insert(0,str(Path('src').resolve()))
from app import Engine
OUT=Path(__file__).resolve().parent
E=Engine();E.kg.conn.close();E.kg.conn=sqlite3.connect('file:data/processed/oncokg.sqlite?mode=ro',uri=True);E.kg.conn.row_factory=sqlite3.Row
cases=[
('M1-B1','bevacizumab - awwb',None),('M1-B1','89Zr - trastuzumab',None),('M1-B1','[89Zr] trastuzumab',None),
('M2b-R1','osimertinib and generic version of bevacizumab','CHEMBL3353410'),('M2b-R1','generic version of bevacizumab and osimertinib','CHEMBL3353410'),
('M2b-R1','[89Zr] trastuzumab and osimertinib','CHEMBL3353410'),('M2b-R1','osimertinib and oral azacitidine','CHEMBL3353410'),
('M3-B1','paclitaxel with albumin bound nanoparticles',None),('M3-B1','paclitaxel with nanoparticle albumin bound formulation',None),('M3-B1','generic version with bevacizumab',None),
('M3-B2','What is the generic version of bevacizumab?',None),
('M3-S1','osimertinib, liposomal doxorubicin','CHEMBL3353410'),('M3-S1','biosimilar bevacizumab, osimertinib','CHEMBL3353410'),
('M3-long-name','erlotinib hydrochloride','CHEMBL1079742'),('M3-long-name','Paclitaxel conjugate with poly-l-glutamic acid','CHEMBL2108628'),
('M4-B1','osimertinib with generic version of bevacizumab',None),('M4-B1','bevacizumab a generic version of osimertinib',None),
('M4-B1','osimertinib; generic version of bevacizumab','CHEMBL3353410'),('M4-B1','osimertinib\uff0c generic version of bevacizumab','CHEMBL3353410'),
('M4-B2','generic version of Paclitaxel conjugate with poly-l-glutamic acid',None),('M4-B2','generic version of the monoclonal antibody bevacizumab',None),
('M4-B3','biosimilar version of bevacizumab',None),('M4-B3','liposomal formulation of doxorubicin',None),('M4-B3','paclitaxel with albumin-bound nanoparticles',None),
('M4-collateral','EGFR biosimilar bevacizumab','ENSG00000146648'),('M4-collateral','AstraZeneca biosimilar bevacizumab','ORG:astrazeneca'),
('M5-B1-reported','bevacizumab-awwb/ osimertinib','CHEMBL3353410'),('M5-B1-reported','bevacizumab - awwb/ osimertinib','CHEMBL3353410'),('M5-B1-reported','bevacizumab-awwb| osimertinib','CHEMBL3353410'),
('M5-B1-earlier-attack','bevacizumab - awwb/osimertinib','CHEMBL3353410'),('M5-B1-earlier-attack','bevacizumab - awwb|osimertinib','CHEMBL3353410'),
('M5-B2','liposomal and nanoparticle formulation of doxorubicin',None),('M5-B2','liposomal and nanoparticle formulations of doxorubicin',None),('M5-B2','liposomal and sustained release doxorubicin',None),
('M5-S1','biosimilar anastrozole, Arimidex','CHEMBL1399'),('M5-S1','biosimilar Prolia, xgeva','CHEMBL1237023'),('M5-S1','Erlotinib, hydrochloride biosimilar bevacizumab','CHEMBL553'),
('M5-S2-known','Pegylated interferon alfa-2a','CHEMBL1201560'),
('M5-S2-control','PEGINTERFERON ALFA-2A','CHEMBL1201560'),
]
rows=[]
for finding,text,expected in cases:
 m=E.explore(text);actual=m.get('center',{}).get('id')
 row={'finding':finding,'input':text,'expected_center':expected,'actual_center':actual,'matches_expectation':actual==expected,'linker':E.kg.link_entities(text),'map':{k:v for k,v in m.items() if k!='groups'}}
 rows.append(row)
(OUT/'focused_matrix.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'cases':len(rows),'mismatches':[{k:r[k] for k in ['finding','input','actual_center','expected_center']} for r in rows if not r['matches_expectation']]},ensure_ascii=False))
E.kg.conn.close()
