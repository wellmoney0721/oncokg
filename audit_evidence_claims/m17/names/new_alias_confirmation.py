"""Confirm newly lost exact stored names against exact M8 and actual CLI HTTP."""
import hashlib,json,os,re,socket,sqlite3,subprocess,sys,time,types,urllib.request
from pathlib import Path
ROOT=Path.cwd();OUT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'src'))
import query,textrules as T
from app import Engine
source=subprocess.check_output(['git','show','ec4eede:src/query.py']).decode('utf8')
mod=types.ModuleType('m8_exact_aliases');mod.__file__=str(ROOT/'src/query.py');sys.modules[mod.__name__]=mod
exec(compile(source,'ec4eede:src/query.py','exec'),mod.__dict__)
cur,old=Engine(),Engine();old.kg.conn.close();old.kg=mod.OncoKG()
for e in (cur,old):
 e.kg.conn.close();e.kg.conn=sqlite3.connect((ROOT/'data/processed/oncokg.sqlite').as_uri()+'?mode=ro',uri=True);e.kg.conn.row_factory=sqlite3.Row
texts=['Trastuzumab--vcmmae conjugate','Theophylline in dextrose 5% in plastic container','40-o-(2-hydroxyethyl)-rapamycin','42-o-(2-hydroxyethyl)rapamycin','TRASTUZUMAB VEDOTIN','THEOPHYLLINE','EVEROLIMUS','CHEMBL5315030','CHEMBL1355736','CHEMBL1908360']
rows=[]
for s in texts:
 norm=query._fold(s);blocked=cur.kg._resolver_blocked(norm);found=cur.kg._link(norm)
 words=[re.sub(r'^[^\w]+|[^\w]+$','',w) for w in norm.split()]
 maps=[]
 for e in (cur,old):
  m=e.explore(s,1);maps.append({k:v for k,v in m.items() if k!='groups'})
 rows.append(dict(input=s,stored_aliases=[h for h in cur.dic['index'].get(T.canonical_key(s),[]) if h['alias'].lower()==s.lower()],resolver=cur.resolve(s),resolver_blocked=blocked,item_linker=found,whole_name=cur.kg._whole_name(norm,blocked,found),guards=dict(distinct=T.is_distinct_product(s),radiotracer=T.is_radiotracer(s),qualified=query._qualified(words),words=words,isotope_pairs=[f'{a} {b}' for a,b in zip(words,words[1:]) if T.is_isotope_label(f'{a} {b}')]),current=maps[0],m8_exact=maps[1]))
port=8982
with socket.socket() as sock:assert sock.connect_ex(('127.0.0.1',port))!=0
env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONUTF8='1',PYTHONIOENCODING='utf-8',TMP=str(OUT/'tmp'),TEMP=str(OUT/'tmp'))
http=[]
with (OUT/'new_alias_server.txt').open('wb') as log:
 p=subprocess.Popen([sys.executable,'-B','-u','src/app.py',str(port)],stdout=log,stderr=subprocess.STDOUT,env=env,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
 try:
  for _ in range(100):
   if p.poll() is not None:raise RuntimeError('server exited')
   try:
    with urllib.request.urlopen(f'http://127.0.0.1:{port}/',timeout=1) as r:page=r.read()
    break
   except OSError:time.sleep(.1)
  else:raise RuntimeError('server timeout')
  for s in texts:
   req=urllib.request.Request(f'http://127.0.0.1:{port}/api/explore',json.dumps({'text':s}).encode(),{'Content-Type':'application/json'})
   with urllib.request.urlopen(req,timeout=20) as r:http.append(dict(input=s,status=r.status,response=json.load(r)))
 finally:p.terminate();p.wait(timeout=10)
with socket.socket() as sock:closed=sock.connect_ex(('127.0.0.1',port))!=0
out=dict(previous_ref='ec4eede',previous_query_sha256=hashlib.sha256(source.encode()).hexdigest(),comparison_scope='exact previous query module; app/rules/data current',cases=rows,http=http,lifecycle=dict(pid=p.pid,port=port,port_closed=closed,served_html_equals_worktree=page==(ROOT/'web/try.html').read_bytes()))
(OUT/'new_alias_confirmation.json').write_text(json.dumps(out,indent=2,ensure_ascii=False),encoding='utf8')
for r in rows:print(json.dumps(dict(input=r['input'],current=r['current'].get('center',{}).get('id'),m8=r['m8_exact'].get('center',{}).get('id'),guard=r['guards']),ensure_ascii=False))
for e in (cur,old):e.kg.conn.close()
