import sys,json,sqlite3,subprocess,types
from pathlib import Path
sys.dont_write_bytecode=True
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2]
sys.path.insert(0,str(ROOT/'src'))
import query,textrules as T
from app import Engine
src=subprocess.check_output(['git','show','HEAD^:src/query.py'],cwd=ROOT).decode('utf8')
mod=types.ModuleType('m19_previous');mod.__file__=str(ROOT/'src/query.py');sys.modules[mod.__name__]=mod;exec(compile(src,'HEAD^:src/query.py','exec'),mod.__dict__)
engines={'current':Engine(),'previous':Engine()};engines['previous'].kg.conn.close();engines['previous'].kg=mod.OncoKG()
for e in engines.values():
 e.kg.conn.close();e.kg.conn=sqlite3.connect((ROOT/'data/processed/oncokg.sqlite').as_uri()+'?mode=ro',uri=True);e.kg.conn.row_factory=sqlite3.Row
cases = ['radio-labelled trastuzumab', 'radiolabelled trastuzumab', 'radio-labeled trastuzumab', 'radio labeled trastuzumab', 'radio-labelled trastuzumab tracer', 'trastuzumab radio-tracer', 'trastuzumab radiotracer', 'trastuzumab radioactively labelled', 'trastuzumab radioactively labeled', 'trastuzumab radioactive label', 'trastuzumab radioiodinated', 'trastuzumab radio-iodinated', 'trastuzumab radio iodinated', 'iodine124 trastuzumab', 'iodine-124 trastuzumab', '124iodine trastuzumab', '124-iodine trastuzumab', 'trastuzumab iodine124', '99m-technetium trastuzumab', 'technetium-99m trastuzumab', '99-technetium trastuzumab', 'technetium99m trastuzumab', '99mtechnetium trastuzumab', 'technetium metastable 99 trastuzumab', 'trastuzumab labelled with iodine 124', 'trastuzumab labelled with iodine (124)', 'trastuzumab labelled with iodine mass 124', 'zirconium89 trastuzumab', 'zirconium-89 trastuzumab', '89zirconium trastuzumab', 'radioconjugated trastuzumab', 'trastuzumab radioimmunoconjugates', 'trastuzumab radionuclide-labelled', 'trastuzumab radionuclide labeled', 'trastuzumab isotopically labelled', 'trastuzumab radio-labelled with iodine-124', 'trastuzumab radio-labelled with I-124', 'trastuzumab radio-labelled with 124I', 'trastuzumab (radio-labelled)', 'radio-ligand trastuzumab', 'radio-immunoconjugate trastuzumab', 'radio-pharmaceutical trastuzumab', 'osimertinib, radio-labelled trastuzumab', 'radio-labelled trastuzumab, osimertinib', 'radio-labelled trastuzumab and osimertinib', 'unlabelled trastuzumab', 'non-radiolabelled trastuzumab', 'nonradioactive trastuzumab', 'trastuzumab', 'fluorine-18 fluorodeoxyglucose', 'radio-labelled fluorodeoxyglucose', 'radio-labelled FDG', 'tritiated FDG', 'FDG labelled with carbon-14', 'osimertinib 80 mg', 'paclitaxel 2 cycles', 'lead compound osimertinib', 'radio-labelled Herceptin', 'radiolabelled Herceptin', 'radio-labelled vinblastine', 'radiolabelled vinblastine', 'radio-labelled erlotinib', 'radiolabelled erlotinib', 'trastuzumab radio-labelled', 'trastuzumab radiolabelled', 'radio‑labelled trastuzumab', 'radio_labelled trastuzumab', 'RADIO-LABELLED TRASTUZUMAB', 'radio labelled trastuzumab', 'radioactively labelled trastuzumab', '99m technetium trastuzumab', 'technetium 99m trastuzumab', 'trastuzumab labelled with 99m-technetium', 'trastuzumab labelled with technetium-99m', 'trastuzumab labelled with 99mTc', '99m-Tc trastuzumab', 'technetium99m-trastuzumab', 'trastuzumab radioligands', 'trastuzumab radioligand', 'trastuzumab radiopharmaceuticals', 'trastuzumab radiopharmaceutical', 'radio-conjugated trastuzumab']
rows=[]
for text in cases:
 row={'text':text,'canonical_key':T.canonical_key(text),'alnum_words':query._alnum_words(text),'dictionary_hits':engines['current'].dic['index'].get(T.canonical_key(text),[])}
 for label,e in engines.items():
  norm=query._fold(text);b=e.kg._resolver_blocked(norm)
  calls=[];original_marked=e.kg._marked
  def traced_marked(key,did,tokens,seg,a,z):
   result=original_marked(key,did,tokens,seg,a,z)
   calls.append({'key':key,'did':did,'tokens':tokens,'segments':seg,'a':a,'b':z,'result':result})
   return result
  e.kg._marked=traced_marked
  f=e.kg._link(norm)
  e.kg._marked=original_marked
  row[label]={'resolver':e.resolve(text),'blocked':b,'item_linker':f,'whole_name':e.kg._whole_name(norm,b,f),'public_linker':e.kg.link_entities(text),'map':e.explore(text,2),'trial_qa':e.ask('Which trials evaluate '+text+'?'),'sponsor_qa':e.ask('Who sponsors trials of '+text+'?')}
  row[label]['marked_calls']=calls
 row['current']['qualified']=query._qualified(text.split());row['current']['item_has_isotope']=query._item_has_isotope(tuple(text.split()));rows.append(row)
(OUT/'new_results.json').write_text(json.dumps({'head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),'previous':subprocess.check_output(['git','rev-parse','HEAD^'],cwd=ROOT,text=True).strip(),'cases':rows},ensure_ascii=False,indent=2),encoding='utf8')
summary=[]
for r in rows:
 c=r['current'];p=r['previous'];summary.append({'text':r['text'],'current':c['map'].get('center',{}).get('label'),'previous':p['map'].get('center',{}).get('label'),'refused':any(x['type']=='Refused' for x in c['public_linker']),'resolver_tiers':[x['tier'] for x in c['resolver']['components']],'blocked':c['blocked'],'qualified':c['qualified'],'trial_qa':len(c['trial_qa']['evidence']),'sponsor_qa':len(c['sponsor_qa']['evidence'])})
(OUT/'new_summary.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding='utf8');print(json.dumps(summary,ensure_ascii=False,indent=2))
for e in engines.values():e.kg.conn.close()
