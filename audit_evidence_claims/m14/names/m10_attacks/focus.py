"""Record every guard plus HTTP-ready inputs and exact predecessor comparisons."""
import json, sqlite3, subprocess, sys, types
from pathlib import Path
sys.dont_write_bytecode=True
OUT=Path(__file__).resolve().parent; ROOT=Path.cwd()
sys.path.insert(0,str(ROOT/'src'))
import query, textrules as T
from app import Engine
inputs=[
 'trastuzumab 89 - Zr','trastuzumab [89 - Zr]','trastuzumab 89 _ Zr',
 'trastuzumab 89 Zr','trastuzumab 89-Zr','trastuzumab [89.Zr]','89 - Zr trastuzumab',
 'A33 124i','A33 124 i','A33 [124i]','A33 124I','A33-124i','124i A33','124-I A33','A33','ADAKITUG',
 'generic-version of bevacizumab','generic_version of bevacizumab','generic version of bevacizumab',
 'albumin - bound paclitaxel','albumin_bound paclitaxel','albumin-bound paclitaxel',
 'follow-on-biologic bevacizumab','follow-on biologic bevacizumab',
 '18-F fluorothymidine','18F fluorothymidine','[18F] fluorothymidine','18-F trastuzumab',
 '18F nonexistingdrug','18f','18-F','90y somatostatin','trastuzumab','bevacizumab','paclitaxel']
source=subprocess.check_output(['git','show','HEAD^:src/query.py'],cwd=ROOT).decode('utf-8')
module=types.ModuleType('round10_previous_query');module.__file__=str(ROOT/'src/query.py');sys.modules[module.__name__]=module
exec(compile(source,'HEAD^:src/query.py','exec'),module.__dict__)
engines={'current':Engine(),'previous':Engine()}
engines['previous'].kg.conn.close();engines['previous'].kg=module.OncoKG()
for e in engines.values():
 e.kg.conn.close();e.kg.conn=sqlite3.connect((ROOT/'data/processed/oncokg.sqlite').as_uri()+'?mode=ro',uri=True);e.kg.conn.row_factory=sqlite3.Row
rows=[]
for text in inputs:
 row={'text':text}
 for version,e in engines.items():
  norm=query._fold(text);blocked=e.kg._resolver_blocked(norm);linked=e.kg._link(norm)
  mp=e.explore(text,2)
  row[version]={'resolver':e.resolve(text),'blocked':blocked,'item_linker':linked,'whole_name':e.kg._whole_name(norm,blocked,linked),
    'map':mp,'trial_qa':e.ask('Which trials evaluate '+text+'?'),'sponsor_qa':e.ask('Which companies sponsor '+text+'?')}
 rows.append(row)
e=engines['current']
dictionary={s:e.dic['index'].get(T.canonical_key(s)) for s in ['A33','A33 124i','ADAKITUG','trastuzumab','18f','fluorothymidine']}
(OUT/'focus_results.json').write_text(json.dumps({'head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
 'previous':subprocess.check_output(['git','rev-parse','HEAD^'],cwd=ROOT,text=True).strip(),'dictionary':dictionary,'cases':rows},ensure_ascii=False,indent=2),encoding='utf-8')
(OUT/'http_inputs.json').write_text(json.dumps(inputs,ensure_ascii=False,indent=2),encoding='utf-8')
for row in rows:
 c=row['current'];mp=c['map'];p=row['previous']['map']
 print(json.dumps({'text':row['text'],'now':mp.get('center',{}).get('label',mp.get('refused',mp.get('not_found'))),'previous':p.get('center',{}).get('label',p.get('refused',p.get('not_found'))),'trials':len(c['trial_qa']['evidence']),'sponsors':len(c['sponsor_qa']['evidence'])},ensure_ascii=False))
for e in engines.values(): e.kg.conn.close()
