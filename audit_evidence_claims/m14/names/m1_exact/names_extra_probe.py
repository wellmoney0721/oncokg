import sys,json,sqlite3,urllib.request,urllib.error
from pathlib import Path
sys.path.insert(0,str(Path('src').resolve()))
from app import Engine
E=Engine()
inputs=['ABP 215','ABP-215','89Zr trastuzumab','89Zr-trastuzumab','Mvasi and bevacizumab','Mvasi and osimertinib','bevacizumab awwb','bevacizumab-awwb','Ｍｖａｓｉ','ｍｖａｓｉ','ＡＢＰ－２１５','ＡＢＰ ２１５','Roche','ORG:roche','Astra Zeneca','EGFR\u200b','  NCT00200395  ']
res=[]
for text in inputs:
    try:
        er=E.explore(text)
        resolve=E.resolve(text)
        res.append({'input':text,'linked':E.kg.link_entities(text),'explore':{k:v for k,v in er.items() if k!='groups'},'resolver':[{'component':r['component'],'tier':r['tier'],'drug_id':r.get('drug_id')} for r in resolve['components']]})
    except Exception as ex: res.append({'input':text,'error':str(ex)})
http=[]
for text in ['ABP 215','ABP-215','89Zr trastuzumab','89Zr-trastuzumab','Roche','ORG:roche','Mvasi bevacizumab','Mvasi and bevacizumab','nct00200395','  NCT00200395  ','x '*300+'osimertinib','osimertinib '+'x '*300]:
    try:
        rq=urllib.request.Request('http://127.0.0.1:8921/api/explore',data=json.dumps({'text':text}).encode(),headers={'Content-Type':'application/json'})
        with urllib.request.urlopen(rq,timeout=10) as rp:
            data=json.load(rp)
            http.append({'input':text,'status':rp.status,'body':{k:v for k,v in data.items() if k!='groups'},'group_count':len(data.get('groups',[]))})
    except Exception as ex: http.append({'input':text,'error':str(ex)})
# Use an isolated in-memory snapshot for retirement robustness. Live DB is not mutated.
snapshot=sqlite3.connect(':memory:'); snapshot.row_factory=sqlite3.Row; E.kg.conn.backup(snapshot); E.kg.conn.close(); E.kg.conn=snapshot
snapshot.execute("update node set retired_at='AUDIT_FIXTURE' where id='CHEMBL3353410'")
fixture=[]
for text in ['osimertinib','CHEMBL3353410']:
    er=E.explore(text); fixture.append({'input':text,'explore':{k:v for k,v in er.items() if k!='groups'},'groups':[(g['rel'],g['dir'],g['total']) for g in er.get('groups',[])]})
output={'direct':res,'http':http,'retired_node_fixture':fixture}
Path('audit_evidence_claims/m14/names/m1_exact/names_extra_results.json').write_text(json.dumps(output,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(output,ensure_ascii=False,indent=2))
