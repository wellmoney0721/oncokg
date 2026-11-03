"""Round11 same-data HEAD^/HEAD normalization workloads; bounded subprocess workers."""
from pathlib import Path
import json, os, statistics, subprocess, sys, time, types
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2]
sys.path.insert(0,str(ROOT/'src'))
CASES={
 'matched_same_item_499': 'isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa',
 'matched_same_item_3999': 'isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa isa',
 'demo_osimertinib':'osimertinib',
 'unicode_expansion_500':'\ufdfa'*500,
 'unicode_expansion_4000':'\ufdfa'*4000,
 'plain_499':' '.join(['x']*250),
 'plain_3999':' '.join(['x']*2000),
 'separator_499':' - '.join(['x']*125)+'xx',
 'separator_3999':' - '.join(['x']*1000)+'xx',
 'isotope_neighbor_500':'trastuzumab '+('- '*240)+'89 - Zr',
 'isotope_own_repeat':';'.join(['A33 124i']*444),
 'normalized_qualifier_repeat':';'.join(['generic-version of bevacizumab']*129),
}
if len(sys.argv)>1 and sys.argv[1]=='worker':
 import query
 ref,name=sys.argv[2:4];mod=query
 if ref!='HEAD':
  mod=types.ModuleType('normalization_previous');mod.__file__=str(ROOT/'src/query.py');sys.modules[mod.__name__]=mod
  code=subprocess.check_output(['git','show',f'{ref}:src/query.py'],cwd=ROOT).decode('utf8')
  exec(compile(code,mod.__file__,'exec'),mod.__dict__)
 kg=mod.OncoKG();kg.conn.execute('PRAGMA query_only=ON');text=CASES[name];samples=[]
 for _ in range(3):
  start=time.perf_counter();entities=kg.link_entities(text);samples.append(time.perf_counter()-start)
 kg.conn.close()
 print(json.dumps({'ref':ref,'name':name,'input':text,'characters':len(text),'samples_seconds':samples,'median_seconds':statistics.median(samples),'entities':entities}))
 raise SystemExit
rows=[]
env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONUTF8='1',PYTHONIOENCODING='utf-8',TEMP=str(OUT/'tmp'),TMP=str(OUT/'tmp'),TMPDIR=str(OUT/'tmp'))
for name in CASES:
 for ref in ['HEAD^','HEAD']:
  try:
   p=subprocess.run([sys.executable,'-B',__file__,'worker',ref,name],cwd=ROOT,env=env,capture_output=True,timeout=35)
   assert p.returncode==0,p.stderr.decode('utf8','replace')
   row=json.loads(p.stdout)
  except subprocess.TimeoutExpired:
   row={'ref':ref,'name':name,'input':CASES[name],'characters':len(CASES[name]),'timeout_seconds':35}
  rows.append(row)
  (OUT/'normalization_cost.json').write_text(json.dumps(rows,indent=2,ensure_ascii=False),encoding='utf8')
  print(json.dumps({k:v for k,v in row.items() if k not in ['input','entities']}),flush=True)
