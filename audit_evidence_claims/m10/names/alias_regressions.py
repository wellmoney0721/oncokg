"""Confirm historical alias gains/losses against exact previous query module."""
from pathlib import Path
import hashlib,json,sqlite3,subprocess,sys,types
sys.path.insert(0,str(Path('src').resolve()))
from app import Engine
OUT=Path(__file__).resolve().parent
source=subprocess.check_output(['git','show','9bd7cb4:src/query.py']).decode('utf8')
mod=types.ModuleType('query_m7_alias_control');mod.__file__='9bd7cb4:src/query.py';sys.modules[mod.__name__]=mod
exec(compile(source,mod.__file__,'exec'),mod.__dict__)
cur,old=Engine(),Engine();old.kg.conn.close();old.kg=mod.OncoKG()
for e in (cur,old):
 e.kg.conn.close();e.kg.conn=sqlite3.connect('file:data/processed/oncokg.sqlite?mode=ro',uri=True);e.kg.conn.row_factory=sqlite3.Row
prior=json.loads(Path('audit_evidence_claims/m7/names/names_m5_summary.json').read_text(encoding='utf8'))['new_lone_alias_refusals']
current=json.loads((OUT/'adapted_names_m5_summary.json').read_text(encoding='utf8'))['new_lone_alias_refusals']
inputs={r['input']:r['stored'] for r in prior+current}
rows=[]
for name,stored in inputs.items():
 def result(e,s):
  m=e.explore(s);return {'linker':e.kg.link_entities(s),'map':{k:v for k,v in m.items() if k!='groups'}}
 rows.append({'input':name,'stored':stored,'current':result(cur,name),'m7_exact_query':result(old,name),'canonical_id_control':result(cur,stored['drug_id']),'resolver':cur.resolve(name)})
out={'previous_ref':'9bd7cb4','previous_query_sha256':hashlib.sha256(source.encode()).hexdigest(),'comparison_scope':'exact previous query module; app, rules, normalize, data current','cases':rows}
(OUT/'alias_regressions.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps([{'input':r['input'],'current':r['current']['map'].get('center',{}).get('id'),'m7':r['m7_exact_query']['map'].get('center',{}).get('id')} for r in rows],ensure_ascii=False))
for e in (cur,old):e.kg.conn.close()
