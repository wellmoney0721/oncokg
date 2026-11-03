"""Explicit M6/M7 dispositions; original reproducer inputs, current stage API."""
from pathlib import Path
import json,re,sqlite3,sys,unicodedata
sys.path.insert(0,str(Path('src').resolve()))
from app import Engine
import query
OUT=Path(__file__).resolve().parent
E=Engine();E.kg.conn.close();E.kg.conn=sqlite3.connect('file:data/processed/oncokg.sqlite?mode=ro',uri=True);E.kg.conn.row_factory=sqlite3.Row
cases=[
 ('M7-B1','bevacizumab-awwb?',None),('M7-B1','bevacizumab-awwb!',None),('M7-B1','"bevacizumab-awwb"',None),
 ('M7-B2','(bevacizumab-awwb)',None),('M7-B2','[bevacizumab-awwb]',None),('M7-B2','bevacizumab\u2011awwb',None),('M7-B2','bio\u2011similar bevacizumab',None),
 ('M7-B3','89Zr trastuzumab',None),
 ('M7-S1','Erlotinib, hydrochloride','CHEMBL553'),('M7-S1','osimertinib,mesylate','CHEMBL3353410'),('M7-S1','is a',None),
 ('M7-S2','(E/Z)-AFATINIB','CHEMBL1173655'),('M7-S2','RO 09-1978/000','CHEMBL1773'),('M7-S2','Anusol plus hc','CHEMBL389621'),
 ('M6-S1','Usp mab 003, monoclonal igg1','CHEMBL1743008'),('M6-S1','Usp mab 002, monoclonal igg1','CHEMBL1201583'),('M6-S1','CP-358,774','CHEMBL553'),('M6-S1','Rapamycin, 42-o-(2-hydroxyethyl)-','CHEMBL1908360'),('M6-S1','12,13-desoxyepothilone b, cis','CHEMBL96172'),('M6-S1','ENDOSTATIN, N-TERMINAL-MGGSHHHHH','CHEMBL4297946'),
 ('M6-B2','bevacizumab-awwb\u3002',None),('M6-B2','bevacizumab-awwb\u2014',None),('M6-B2','bevacizumab-awwb-',None),('M6-B2','-bevacizumab-awwb',None),
 ('M6-B3','doxorubicin (nanoparticle and liposomal formulation)',None),('M6-B3','bevacizumab (investigational and biosimilar)',None)
]
rows=[]
for finding,s,expected in cases:
 normalized=re.sub(query._DASHES,'-',unicodedata.normalize('NFKC',s))
 blocked=E.kg._resolver_blocked(normalized);found=E.kg._link(normalized);whole=E.kg._whole_name(normalized,blocked,found)
 m=E.explore(s);actual=m.get('center',{}).get('id')
 r={'finding':finding,'input':s,'normalized_input':normalized,'expected_center':expected,'actual_center':actual,'status':'FIXED' if actual==expected else 'NOT FIXED','resolver_blocked':blocked,'item_linker':found,'whole_name':whole,'linker':E.kg.link_entities(s),'map':{k:v for k,v in m.items() if k!='groups'}}
 if finding.startswith('M7-B') or finding=='M6-B3':
  r['qa']=[{'question':t.format(s),'answer':E.ask(t.format(s))} for t in ('Which trials evaluate {}?','Which companies sponsor {}?')]
 rows.append(r)
qa=[]
for name in ['ENDOSTATIN, N-TERMINAL-MGGSHHHHH','Rapamycin, 42-o-(2-hydroxyethyl)-']:
 for t in ['Which trials evaluate {}?','Which companies sponsor {}?']:
  s=t.format(name);qa.append({'finding':'M6-S1-prefixed-QA','input':s,'answer':E.ask(s)})
OUT.joinpath('historical_focus.json').write_text(json.dumps({'cases':rows,'qa':qa},ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps([{k:r[k] for k in ('finding','input','actual_center','status')} for r in rows],ensure_ascii=False))
E.kg.conn.close()
