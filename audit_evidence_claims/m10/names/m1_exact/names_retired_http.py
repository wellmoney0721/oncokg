import json,sqlite3,sys,threading,urllib.request
from http.server import ThreadingHTTPServer
from pathlib import Path
sys.path.insert(0,str(Path('src').resolve()))
from app import Engine,make_handler
E=Engine()
C=sqlite3.connect(':memory:',check_same_thread=False); C.row_factory=sqlite3.Row
E.kg.conn.backup(C); E.kg.conn.close(); E.kg.conn=C
sql="UPDATE node SET retired_at='AUDIT_FIXTURE' WHERE id='CHEMBL3353410'"
C.execute(sql); C.commit()
server=ThreadingHTTPServer(('127.0.0.1',0),make_handler(E)); worker=threading.Thread(target=server.serve_forever,daemon=True); worker.start()
output={'setup':'Isolated in-memory sqlite backup; no write to source database','mutation_sql':sql,'requests':[]}
try:
    for text in ['osimertinib','CHEMBL3353410','EGFR']:
        req=urllib.request.Request(f'http://127.0.0.1:{server.server_port}/api/explore',data=json.dumps({'text':text}).encode(),headers={'Content-Type':'application/json'})
        with urllib.request.urlopen(req,timeout=10) as response:
            body=json.load(response)
            output['requests'].append({'input':text,'http_status':response.status,'response':body})
finally:
    server.shutdown(); server.server_close(); worker.join(timeout=3); C.close()
Path('audit_evidence_claims/m10/names/m1_exact/names_retired_http_results.json').write_text(json.dumps(output,ensure_ascii=False,indent=2),encoding='utf-8')
for r in output['requests']:
    b=r['response']; print(json.dumps({'input':r['input'],'http_status':r['http_status'],'center':b.get('center'),'not_found':b.get('not_found'),'groups':[(g['rel'],g['dir'],g['total']) for g in b.get('groups',[])]},ensure_ascii=False))
