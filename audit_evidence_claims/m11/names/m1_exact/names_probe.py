import sys,json,sqlite3,time
from pathlib import Path
sys.path.insert(0,str(Path('src').resolve()))
from app import Engine
E=Engine()
inputs=['osimertinib EGFR','EGFR osimertinib','Mvasi bevacizumab','bevacizumab Mvasi','Mvasi','Zirabev','ABP 215','liposomal doxorubicin','89Zr trastuzumab','89Zr-trastuzumab','Tarceva','erlotinib','erlotinib hydrochloride','osimertinib mesylate','Tagrisso','AstraZeneca','Roche','Genentech','BeiGene','Merck','MSD','Johnson & Johnson','Janssen','CHEMBL3353410','chembl3353410','NCT00200395','nct00200395','  osimertinib  ','OSIMERTINIB','ＯＳＩＭＥＲＴＩＮＩＢ','NSCLC','비소세포폐암','no such thing zz','null','unknown','investigator']
results=[]
for s in inputs:
    t=time.perf_counter()
    try:
        r=E.explore(s)
        results.append({'input':s,'linked':E.kg.link_entities(s),'result': {k:v for k,v in r.items() if k!='groups'},'groups':len(r.get('groups',[])),'seconds':time.perf_counter()-t})
    except Exception as ex: results.append({'input':s,'error':repr(ex)})
companies={k:v for k,v in E.kg.companies.items() if len(v)>1}
retired={t:E.kg.conn.execute('select count(*) from '+t+' where retired_at is not null').fetchone()[0] for t in ['node','edge']}
print(json.dumps({'results':results,'multi_companies':companies,'retired_counts':retired},ensure_ascii=False,indent=2))
Path('audit_evidence_claims/m11/names/m1_exact/names_results.json').write_text(json.dumps({'results':results,'multi_companies':companies,'retired_counts':retired},ensure_ascii=False,indent=2),encoding='utf-8')
