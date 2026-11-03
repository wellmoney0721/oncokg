from pathlib import Path
import sys, json, urllib.request
sys.path.insert(0, str(Path('src').resolve()))
from app import Engine
e=Engine()
names=['osimertinib','AstraZeneca','NCT00754364','NCT00200395','CHEMBL1201438','MONDO_0005233','EGFR','KRAS']
results={n:e.explore(n) for n in names}
Path('audit_evidence_claims/m1/ui_real_maps.json').write_text(json.dumps(results, ensure_ascii=False,indent=2),encoding='utf-8')
http={}
for n in names:
    req=urllib.request.Request('http://127.0.0.1:8876/api/explore',data=json.dumps({'text':n}).encode(),headers={'Content-Type':'application/json'})
    with urllib.request.urlopen(req) as r:
        content=r.read()
        http[n]={'status':r.status,'bytes':len(content),'matches_direct_engine':json.loads(content)==results[n]}
Path('audit_evidence_claims/m1/ui_http.json').write_text(json.dumps(http,indent=2),encoding='utf-8')
e.kg.conn.close()
