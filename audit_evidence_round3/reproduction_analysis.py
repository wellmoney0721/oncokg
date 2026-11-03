import hashlib, importlib.metadata, json, re, subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parent.parent; E=ROOT/'audit_evidence_round3'

def differences(a,b,p=''):
    if type(a)!=type(b): return [dict(field=p,before=a,after=b)]
    if isinstance(a,dict):
        return [v for k in sorted(a.keys()|b.keys()) for v in differences(a.get(k),b.get(k),p+'.'+k)]
    if isinstance(a,list):
        if len(a)!=len(b):return [dict(field=p,before_length=len(a),after_length=len(b))]
        return [v for i,(x,y) in enumerate(zip(a,b)) for v in differences(x,y,f'{p}[{i}]')]
    return [] if a==b else [dict(field=p,before=a,after=b)]

changes={}
for p in (E/'original/reports').glob('*.json'):
    q=E/'reports_first'/p.name
    changes['reports/'+p.name]=differences(json.loads(p.read_text(encoding='utf-8')),json.loads(q.read_text(encoding='utf-8')))
changes['web/data.json']=differences(json.loads((E/'original/web/data.json').read_text(encoding='utf-8')),json.loads((E/'dashboard_data_first.json').read_text(encoding='utf-8')))
(E/'reproduction_semantic_changes.json').write_text(json.dumps(changes,indent=2),encoding='utf-8')
runtime=dict(python=sys.version,executable=sys.executable,packages={n:importlib.metadata.version(n) for n in ['pytest','rapidfuzz','requests']})
fresh=E/'fresh'
code="import sys,json; sys.path.insert(0,'src'); import config,normalize,graph,query; print(json.dumps({m.__name__:m.__file__ for m in [config,normalize,graph,query]},indent=2))"
p=subprocess.run([sys.executable,'-B','-c',code],cwd=fresh,capture_output=True)
(E/'fresh_import_paths.stdout.txt').write_bytes(p.stdout)
(E/'fresh_import_paths.stderr.txt').write_bytes(p.stderr)
runtime['fresh_import_exit_code']=p.returncode
(E/'runtime.json').write_text(json.dumps(runtime,indent=2),encoding='utf-8')
print(json.dumps(changes,indent=2))
