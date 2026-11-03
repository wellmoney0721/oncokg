"""Real-handler sponsor props corruption regression; memory backup only."""
import json,sqlite3,sys,types,threading,urllib.request,urllib.error,subprocess
from pathlib import Path
from http.server import ThreadingHTTPServer
ROOT=Path(__file__).resolve().parents[2];OUT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'src'));import app
base=types.ModuleType('baseline');base.__file__=str(ROOT/'src/app.py')
exec(compile(subprocess.check_output(['git','show','bfcb83d:src/app.py']),base.__file__,'exec'),base.__dict__)
source=sqlite3.connect(f'file:{(ROOT/"data/processed/oncokg.sqlite").as_posix()}?mode=ro',uri=True)
edgeid='ORG:alaunos|SPONSORS_TRIAL_OF|CHEMBL1201438|'
raw_original=source.execute('SELECT props FROM edge WHERE id=?',(edgeid,)).fetchone()[0]
def run(module):
    c=sqlite3.connect(':memory:',check_same_thread=False);source.backup(c);c.row_factory=sqlite3.Row
    e=module.Engine.__new__(module.Engine);e.kg=types.SimpleNamespace(conn=c,link_entities=lambda t:[]);e.lock=threading.Lock()
    srv=ThreadingHTTPServer(('127.0.0.1',0),module.make_handler(e));th=threading.Thread(target=srv.serve_forever,daemon=True);th.start();cases=[]
    try:
        for raw in [raw_original,'null','[]','{broken','{}']:
            with e.lock:c.execute('UPDATE edge SET props=? WHERE id=?',(raw,edgeid))
            case={'stored_props':raw,'requests':[]}
            for text in ['CHEMBL1201438','ORG:alaunos']:
                req=urllib.request.Request(f'http://127.0.0.1:{srv.server_port}/api/explore',json.dumps({'text':text}).encode(),{'Content-Type':'application/json'})
                try:
                    with urllib.request.urlopen(req,timeout=10) as r:status=r.status;body=json.load(r)
                except urllib.error.HTTPError as ex:status=ex.code;body=json.load(ex)
                found=[{'group':{k:v for k,v in g.items() if k!='items'},'item':it} for g in body.get('groups',[]) for it in g['items'] if it['edge_id']==edgeid]
                # The corrupted weight may fall outside AstraZeneca's first thirty; preserve total response for reproducibility.
                case['requests'].append({'input':text,'status':status,'matched_edge_items':found,'body':body})
            cases.append(case)
    finally:srv.shutdown();srv.server_close();th.join(3);c.close()
    return cases
out={'fixture':'read-only real database backed up into memory; mutate only one edge props','edge_id':edgeid,'sql':'UPDATE edge SET props=? WHERE id=?','baseline':run(base),'HEAD':run(app)}
source.close();(OUT/'db_missing_sponsor_count.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({k:[{'props':x['stored_props'] if len(x['stored_props'])<20 else 'original evidence_trials=1','requests':[{'input':r['input'],'status':r['status'],'weights':[m['item']['weight'] for m in r['matched_edge_items']]} for r in x['requests']]} for x in out[k]] for k in ['baseline','HEAD']}))
