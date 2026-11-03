"""Fresh live HTTP proof of round-6 name-boundary counterexamples; no source edits."""
import hashlib,json,os,socket,subprocess,sys,time,urllib.request,urllib.error
from pathlib import Path
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
PORT=8932
BASE=f'http://127.0.0.1:{PORT}'
DB=ROOT/'data/processed/oncokg.sqlite'
def post(path,payload):
    started=time.perf_counter()
    req=urllib.request.Request(BASE+path,data=json.dumps(payload).encode(),headers={'Content-Type':'application/json'})
    try: res=urllib.request.urlopen(req,timeout=15)
    except urllib.error.HTTPError as e: res=e
    raw=res.read()
    return {'path':path,'payload':payload,'status':res.status,'seconds':time.perf_counter()-started,
            'bytes':len(raw),'body':json.loads(raw)}
before=hashlib.sha256(DB.read_bytes()).hexdigest()
with socket.socket() as s: assert s.connect_ex(('127.0.0.1',PORT))!=0
env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1','PYTHONUTF8':'1'}
with (OUT/'alias_server.txt').open('w',encoding='utf8') as log:
    proc=subprocess.Popen([sys.executable,'-B','-u','src/app.py',str(PORT)],cwd=ROOT,env=env,
        stdout=log,stderr=subprocess.STDOUT,creationflags=getattr(subprocess,'CREATE_NO_WINDOW',0))
    try:
        for _ in range(100):
            assert proc.poll() is None
            try:
                page=urllib.request.urlopen(BASE,timeout=1).read()
                break
            except OSError: time.sleep(.1)
        else: raise RuntimeError('server unavailable')
        values=['ENDOSTATIN, N-TERMINAL-MGGSHHHHH', 'CHEMBL4297946', 'Rapamycin, 42-o-(2-hydroxyethyl)-', 'CP-358,774', 'Usp mab 003, monoclonal igg1', '12,13-desoxyepothilone b, cis', 'Erlotinib/hydrochloride', 'Erlotinib|hydrochloride', 'biosimilar anastrozole/Arimidex', 'osimertinib/EGFR']
        rows=[post(path,{'text':v}) for v in values for path in ['/api/explore','/api/resolve']]
        for v in ['ENDOSTATIN, N-TERMINAL-MGGSHHHHH','Rapamycin, 42-o-(2-hydroxyethyl)-']:
            for q in ['Which trials evaluate {}?','Which companies sponsor {}?']:
                rows.append(post('/api/ask',{'text':q.format(v)}))
        perf=[]
        for n in []:
            perf.append(post('/api/check',{'text':'EGFR','answer':' '.join(['x']*n)}))
        result={'head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT).decode().strip(),
                'base':BASE,'page_matches_worktree':page==(ROOT/'web/try.html').read_bytes(),
                'cases':rows,'answer_cost':perf}
        (OUT/'alias_http.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
        for r in rows:
            b=r['body']
            print(json.dumps({'path':r['path'],'text':r['payload']['text'],'status':r['status'],
                              'center':b.get('center',{}).get('id'),'refused':b.get('refused'),
                              'evidence':len(b.get('evidence',[])),
                              'components':[(c.get('status'),c.get('drug_id')) for c in b.get('components',[])]},ensure_ascii=False))
        print('answer_cost',[(len(r['payload']['answer']),r['seconds'],r['status']) for r in perf])
    finally:
        proc.terminate(); proc.wait(timeout=10)
        with socket.socket() as s: closed=s.connect_ex(('127.0.0.1',PORT))!=0
        after=hashlib.sha256(DB.read_bytes()).hexdigest()
        (OUT/'alias_lifecycle.json').write_text(json.dumps({'pid':proc.pid,'port':PORT,
              'exit':proc.returncode,'port_closed':closed,'database_unchanged':before==after,
              'before':before,'after':after},indent=2),encoding='utf8')
        assert closed and before==after
