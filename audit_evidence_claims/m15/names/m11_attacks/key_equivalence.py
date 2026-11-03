"""M11 independent key-equivalence attacks. Writes only beside this script."""
import json,sqlite3,subprocess,sys,types
from pathlib import Path
sys.dont_write_bytecode=True
OUT=Path(__file__).resolve().parent; ROOT=Path.cwd()
sys.path.insert(0,str(ROOT/'src'))
import query,textrules as T
from app import Engine
source=subprocess.check_output(['git','show','HEAD^:src/query.py'],cwd=ROOT).decode('utf8')
mod=types.ModuleType('m11_previous_query');mod.__file__=str(ROOT/'src/query.py');sys.modules[mod.__name__]=mod
exec(compile(source,'HEAD^:src/query.py','exec'),mod.__dict__)
engines={'current':Engine(),'previous':Engine()};engines['previous'].kg.conn.close();engines['previous'].kg=mod.OncoKG()
for e in engines.values():
 e.kg.conn.close();e.kg.conn=sqlite3.connect((ROOT/'data/processed/oncokg.sqlite').as_uri()+'?mode=ro',uri=True);e.kg.conn.row_factory=sqlite3.Row
inputs=[
 '[89Z.r] trastuzumab','89Z.r trastuzumab','89Z_r trastuzumab','trastuzumab [89Z.r]',
 '[89Z r] trastuzumab','[89 Z r] trastuzumab','[8.9Zr] trastuzumab','[8.9.Zr] trastuzumab',
 '[177L.u] dotatate','177L_u dotatate','dotatate [177L.u]','[68G.a] edotreotide',
 'bevacizumab - a - w - w - b','bevacizumab a _ w _ w _ b','bevacizumab a - w - w - b',
 'bevacizumab a.w.w.b','bevacizumab a w w b','bevacizumab a - w w b',
 '[89Zr] trastuzumab','[89.Zr] trastuzumab','89zr-trastuzumab','trastuzumab','bevacizumab',
 'biosimilars of bevacizumab','doxorubicin liposome','follow-on biological bevacizumab']
rows=[]
for text in inputs:
 row={'text':text,'canonical_key':T.canonical_key(text),'alnum_words':query._alnum_words(text),'dictionary_hits':engines['current'].dic['index'].get(T.canonical_key(text),[])}
 for label,e in engines.items():
  norm=query._fold(text);b=e.kg._resolver_blocked(norm);f=e.kg._link(norm)
  row[label]={'resolver':e.resolve(text),'blocked':b,'item_linker':f,'whole_name':e.kg._whole_name(norm,b,f),'public_linker':e.kg.link_entities(text),'map':e.explore(text,2),'trial_qa':e.ask('Which trials evaluate '+text+'?'),'sponsor_qa':e.ask('Which companies sponsor '+text+'?')}
 row['current']['qualified']=query._qualified(text.split())
 rows.append(row)
payload={'head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'previous':subprocess.check_output(['git','rev-parse','HEAD^'],cwd=ROOT,text=True).strip(),'cases':rows}
payload['comparison_scope']='Exact HEAD^ query module; current app, rules, normalize and DB. Previous standalone qualified diagnostic omitted; previous item_linker executes old module guards.'
(OUT/'key_equivalence_results.json').write_text(json.dumps(payload,ensure_ascii=False,indent=2),encoding='utf8')
for r in rows:
 c=r['current'];p=r['previous'];print(json.dumps({'text':r['text'],'current':c['map'].get('center',{}).get('label'),'previous':p['map'].get('center',{}).get('label'),'refused':any(x['type']=='Refused' for x in c['public_linker']),'trial_qa':len(c['trial_qa']['evidence']),'sponsor_qa':len(c['sponsor_qa']['evidence'])},ensure_ascii=True),flush=True)
for e in engines.values():e.kg.conn.close()
