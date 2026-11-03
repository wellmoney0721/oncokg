"""M14 rerun of M12 attacks; no application mutation. Writes only beside this file."""
import hashlib,json,os,re,sqlite3,subprocess,sys,types
from pathlib import Path
sys.dont_write_bytecode=True
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2]
sys.path.insert(0,str(ROOT/'src'))
import query,textrules as T
from app import Engine
source=subprocess.check_output(['git','show','HEAD^:src/query.py'],cwd=ROOT).decode('utf8')
mod=types.ModuleType('m15_previous_query');mod.__file__=str(ROOT/'src/query.py');sys.modules[mod.__name__]=mod
exec(compile(source,'HEAD^:src/query.py','exec'),mod.__dict__)
engines={'current':Engine(),'previous':Engine()};engines['previous'].kg.conn.close();engines['previous'].kg=mod.OncoKG()
for e in engines.values():
 e.kg.conn.close();e.kg.conn=sqlite3.connect((ROOT/'data/processed/oncokg.sqlite').as_uri()+'?mode=ro',uri=True);e.kg.conn.row_factory=sqlite3.Row
cases=[
 '[89Z.r]-DFO-daratumumab','89Z_r-dfo-daratumumab','89Z.r-dfo-daratumumab',
 '89Z.r dfo daratumumab','89Z.r-dfo daratumumab','89Zr-dfo-daratumumab',
 '[89Zr]-DFO-daratumumab','[89Z.r]-DFO-daratumumab, osimertinib','daratumumab',
 'trastuzumab labelled with [89Zr]','trastuzumab labelled with [89Zr], osimertinib',
 'trastuzumab labeled with 89Zr','trastuzumab labelled 89Zr','trastuzumab (labelled with 89Zr)',
 '89Zr labelled trastuzumab','89Zr-labeled trastuzumab','[89Zr]-labelled trastuzumab',
 '[89Z.r]-labelled trastuzumab','[89Z.r]-labelled trastuzumab, osimertinib',
 '[89Z_r] labelled trastuzumab','[89Zr] labelled trastuzumab','[89Z.r] labelled trastuzumab',
 '[89Z.r]-DFO trastuzumab','[89Zr]-DFO trastuzumab','[89Z.r] trastuzumab',
 'trastuzumab [89Z.r]','[89Zr] trastuzumab','trastuzumab 89 Zr','trastuzumab',
 'bevacizumab a - w w b','bevacizumab a - w w b, osimertinib','bevacizumab',
 'b.i.o.similar bevacizumab','biosimilar bevacizumab','lip.osomal doxorubicin','liposomal doxorubicin',
 'Lutetium (177L.u) dotatate','Lutetium (177Lu) dotatate','osimertinib 80 mg','paclitaxel 2 cycles','cisplatin 75 mg/m2 day 1']
rows=[]
for text in cases:
 row={'text':text,'canonical_key':T.canonical_key(text),'alnum_words':query._alnum_words(text),'dictionary_hits':engines['current'].dic['index'].get(T.canonical_key(text),[])}
 for label,e in engines.items():
  norm=query._fold(text);b=e.kg._resolver_blocked(norm);f=e.kg._link(norm)
  row[label]={'resolver':e.resolve(text),'blocked':b,'item_linker':f,'whole_name':e.kg._whole_name(norm,b,f),'public_linker':e.kg.link_entities(text),'map':e.explore(text,2),'trial_qa':e.ask('Which trials evaluate '+text+'?'),'sponsor_qa':e.ask('Who sponsors trials of '+text+'?')}
 row['current']['qualified']=query._qualified(text.split())
 rows.append(row)
payload={'head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'previous':subprocess.check_output(['git','rev-parse','HEAD^'],cwd=ROOT,text=True).strip(),'cases':rows,'comparison_scope':'HEAD^ query module only, current app/normalize/textrules/database; not an old deployed application.'}
(OUT/'focused_results.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding='utf8')
summary=[]
for r in rows:
 c=r['current'];p=r['previous'];summary.append({'text':r['text'],'current':c['map'].get('center',{}).get('label'),'previous':p['map'].get('center',{}).get('label'),'refused':any(x['type']=='Refused' for x in c['public_linker']),'trial_qa':len(c['trial_qa']['evidence']),'sponsor_qa':len(c['sponsor_qa']['evidence'])})
(OUT/'focused_summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(summary,ensure_ascii=True))
for e in engines.values():e.kg.conn.close()
