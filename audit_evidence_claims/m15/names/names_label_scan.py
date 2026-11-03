import sys,json,collections,time
from pathlib import Path
sys.path.insert(0,str(Path('src').resolve()))
from app import Engine
E=Engine(); out=[]; counts=collections.Counter(); start=time.perf_counter()
for row in E.kg.conn.execute("select id,type,label from node where retired_at is null and type in ('Company','Investigator','Target','Disease')"):
    named=E.kg.link_entities(row['label']); hits=[r for r in named if r.get('id') and r['type']!='Refused']
    if not hits:
        counts[(row['type'],'not_found')]+=1
        if row['type']=='Investigator' and sum(x['expected']['type']=='Investigator' for x in out)<4: out.append({'expected':dict(row),'hits':named})
    elif hits[0]['id']!=row['id']:
        counts[(row['type'],'different_center')]+=1
        out.append({'expected':dict(row),'hits':named})
    else: counts[(row['type'],'same_center')]+=1
result={'counts':{str(k):v for k,v in counts.items()},'examples':out,'seconds':time.perf_counter()-start}
Path('audit_evidence_claims/m15/names/names_label_scan.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(result,ensure_ascii=False,indent=2))
