import ast,json,sys,threading,urllib.request,subprocess,textwrap,types
from pathlib import Path
sys.path.insert(0,str(Path('src').resolve()))
import query
from app import Engine,make_handler
from http.server import ThreadingHTTPServer
import textrules as T
OUT=Path('audit_evidence_claims/m2')
oldsource=subprocess.check_output(['git','show','bfcb83d:src/query.py']).decode('utf8')
method=next(n for n in ast.walk(ast.parse(oldsource)) if isinstance(n,ast.FunctionDef) and n.name=='link_entities')
oldglobals=dict(query.__dict__);exec(compile(textwrap.dedent(ast.get_source_segment(oldsource,method)),'bfcb83d:src/query.py','exec'),oldglobals)
E=Engine();old=Engine();old.kg.link_entities=types.MethodType(oldglobals['link_entities'],old.kg)
servers=[]
for engine in [E,old]:
 server=ThreadingHTTPServer(('127.0.0.1',0),make_handler(engine));worker=threading.Thread(target=server.serve_forever,daemon=True);worker.start();servers.append((server,worker))
def post(i,path,text):
 req=urllib.request.Request(f'http://127.0.0.1:{servers[i][0].server_port}/api/{path}',data=json.dumps({'text':text}).encode(),headers={'Content-Type':'application/json'})
 with urllib.request.urlopen(req,timeout=20) as resp:
  b=json.load(resp)
  if path=='explore':b={k:v for k,v in b.items() if k!='groups'}
  return {'status':resp.status,'body':b}
inputs=['osimertinib and generic version of bevacizumab','osimertinib and generic version of doxorubicin','What is the generic version of bevacizumab?','Which trials evaluate [89Zr] trastuzumab and osimertinib?','Which trials evaluate osimertinib and [89Zr] trastuzumab?','osimertinib and oral azacitidine','oral azacitidine and osimertinib','Which trials evaluate osimertinib and generic version of bevacizumab?','Which companies sponsor osimertinib and generic version of bevacizumab?','bevacizumab \u2014 awwb','bevacizumab \uff0d awwb','bevacizumab awwb','[89Zr] trastuzumab and osimertinib']
try:
 out=[]
 for s in inputs:
  row={'input':s,'distinct_predicate':T.is_distinct_product(s),'tracer_predicate':T.is_radiotracer(s),'resolver':E.resolve(s),'current_explore':post(0,'explore',s),'current_ask':post(0,'ask',s),'baseline_explore_using_old_linker':post(1,'explore',s),'baseline_ask':post(1,'ask',s)};out.append(row)
 OUT.joinpath('names_regressions.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8')
 for r in out:print(json.dumps({'input':r['input'],'resolver':[(c['component'],c['tier'],c.get('drug_id')) for c in r['resolver']['components']],'current':r['current_explore']['body'],'old':r['baseline_explore_using_old_linker']['body'],'current_evidence':len(r['current_ask']['body'].get('evidence',[])),'old_evidence':len(r['baseline_ask']['body'].get('evidence',[]))},ensure_ascii=False))
finally:
 for s,w in servers:s.shutdown();s.server_close();w.join(3)
 E.kg.conn.close();old.kg.conn.close()
