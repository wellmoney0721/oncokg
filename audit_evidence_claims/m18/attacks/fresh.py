"""M14 rerun of M12 attacks; no application mutation. Writes only beside this file."""
import hashlib,json,os,re,sqlite3,subprocess,sys,types
from pathlib import Path
sys.dont_write_bytecode=True
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2]
sys.path.insert(0,str(ROOT/'src'))
import query,textrules as T
from app import Engine
source=subprocess.check_output(['git','show','HEAD^:src/query.py'],cwd=ROOT).decode('utf8')
mod=types.ModuleType('m18_previous_query');mod.__file__=str(ROOT/'src/query.py');sys.modules[mod.__name__]=mod
exec(compile(source,'HEAD^:src/query.py','exec'),mod.__dict__)
engines={'current':Engine(),'previous':Engine()};engines['previous'].kg.conn.close();engines['previous'].kg=mod.OncoKG()
for e in engines.values():
 e.kg.conn.close();e.kg.conn=sqlite3.connect((ROOT/'data/processed/oncokg.sqlite').as_uri()+'?mode=ro',uri=True);e.kg.conn.row_factory=sqlite3.Row
cases=['89ZrDFO-daratumumab', '89zrdfodaratumumab', '[89ZrDFO]-daratumumab', '89Z.rDFO-daratumumab', '89ZrDFO daratumumab', '89-ZrDFO-daratumumab', '89Zr-DFOdaratumumab', '89ZrDFO-daratumumab, osimertinib', '89zrdfodaratumumab and osimertinib', '89Zr-dfo-daratumumab', '[89Zr]-DFO-daratumumab', '[89Z.r]-DFO-daratumumab', '89Z_r-dfo-daratumumab', 'daratumumab', 'A33124I', 'a33[124i]', 'A33 124i', 'ADAKITUG', 'bevacizumabawwb', '89zrtrastuzumab', '[89Z.r] trastuzumab', 'osimertinib 80 mg', 'paclitaxel 2 cycles', 'cisplatin 75 mg/m2 day 1', 'rad001c', 'RAD001', 'TAK-659F']
rows=[]
for text in cases:
 row={'text':text,'canonical_key':T.canonical_key(text),'alnum_words':query._alnum_words(text),'dictionary_hits':engines['current'].dic['index'].get(T.canonical_key(text),[])}
 for label,e in engines.items():
  norm=query._fold(text);b=e.kg._resolver_blocked(norm);f=e.kg._link(norm)
  row[label]={'resolver':e.resolve(text),'blocked':b,'item_linker':f,'whole_name':e.kg._whole_name(norm,b,f),'public_linker':e.kg.link_entities(text),'map':e.explore(text,2),'trial_qa':e.ask('Which trials evaluate '+text+'?'),'sponsor_qa':e.ask('Who sponsors trials of '+text+'?')}
 row['current']['qualified']=query._qualified(text.split())
 rows.append(row)
payload={'head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'previous':subprocess.check_output(['git','rev-parse','HEAD^'],cwd=ROOT,text=True).strip(),'cases':rows,'comparison_scope':'HEAD^ query module only, current app/normalize/textrules/database; not an old deployed application.'}
(OUT/'fresh_results.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding='utf8')
summary=[]
for r in rows:
 c=r['current'];p=r['previous'];summary.append({'text':r['text'],'current':c['map'].get('center',{}).get('label'),'previous':p['map'].get('center',{}).get('label'),'refused':any(x['type']=='Refused' for x in c['public_linker']),'trial_qa':len(c['trial_qa']['evidence']),'sponsor_qa':len(c['sponsor_qa']['evidence'])})
(OUT/'fresh_summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(summary,ensure_ascii=True))
for e in engines.values():e.kg.conn.close()
