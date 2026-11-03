"""Round 7 focused repair dispositions and guard-order controls; no source edits."""
from pathlib import Path
import json,sqlite3,sys
sys.path.insert(0,str(Path('src').resolve()))
from app import Engine
import textrules as T
OUT=Path(__file__).resolve().parent
E=Engine();E.kg.conn.close();E.kg.conn=sqlite3.connect('file:data/processed/oncokg.sqlite?mode=ro',uri=True);E.kg.conn.row_factory=sqlite3.Row
cases=[
('M6-B1','bevacizumab - awwb/osimertinib','CHEMBL3353410'),
('M6-B1','bevacizumab - awwb|osimertinib','CHEMBL3353410'),
('M6-B2','bevacizumab-awwb\u3002',None),
('M6-B2','bevacizumab-awwb\u2014',None),
('M6-B2','bevacizumab-awwb-',None),
('M6-B2','-bevacizumab-awwb',None),
('M6-B3','doxorubicin (nanoparticle and liposomal formulation)',None),
('M6-B3','bevacizumab (investigational and biosimilar)',None),
('M6-S1','Usp mab 003, monoclonal igg1','CHEMBL1743008'),
('M6-S1','Usp mab 002, monoclonal igg1','CHEMBL1201583'),
('M6-S1','CP-358,774','CHEMBL553'),
('M6-S1','Rapamycin, 42-o-(2-hydroxyethyl)-','CHEMBL1908360'),
('M6-S1','12,13-desoxyepothilone b, cis','CHEMBL96172'),
('M6-S1','ENDOSTATIN, N-TERMINAL-MGGSHHHHH','CHEMBL4297946'),
('whole_alias_loss','(E/Z)-AFATINIB','CHEMBL1173655'),
('whole_alias_loss','RO 09-1978/000','CHEMBL1773'),
('whole_alias_loss','Anusol plus hc','CHEMBL389621'),
('punctuation_control','bevacizumab-awwb',None),
('whole_name_shortcut','bevacizumab-awwb?',None),
('both_guards_miss','(bevacizumab-awwb)',None),
('both_guards_miss','[bevacizumab-awwb]',None),
('whole_name_shortcut','"bevacizumab-awwb"',None),
('whole_name_shortcut','"[89Zr] trastuzumab"',None),
]
rows=[]
for finding,s,expected in cases:
 s=s.replace('\\u3002','\u3002').replace('\\u2014','\u2014')
 blocked=E.kg._resolver_blocked(s);m=E.explore(s)
 row={'finding':finding,'input':s,'expected_center':expected,'actual_center':m.get('center',{}).get('id'),'resolver':E.resolve(s),'resolver_blocked':blocked,'whole_name':E.kg._whole_name(s,blocked,E.kg._link(s)),'list_linker':E.kg._link(s),'linker':E.kg.link_entities(s),'map':{k:v for k,v in m.items() if k!='groups'},'stored_hits':E.dic['index'].get(T.canonical_key(s),[])}
 row['matches_expected']=row['actual_center']==expected
 if finding in ('M6-B1','M6-B2','M6-B3','both_guards_miss','whole_name_shortcut'):
  row['qa']=[E.ask(t.format(s)) for t in ('Which trials evaluate {}?','Which companies sponsor {}?')]
 rows.append(row)
(OUT/'adapted_m7_focus.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps([{'finding':r['finding'],'input':r['input'],'center':r['actual_center'],'expected':r['expected_center'],'list_center_ids':[e['id'] for e in r['list_linker'] if e['type']=='Drug']} for r in rows],ensure_ascii=False,indent=2))
E.kg.conn.close()
