import sys,json,sqlite3,subprocess,types
from pathlib import Path
sys.dont_write_bytecode=True
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[3]
sys.path.insert(0,str(ROOT/'src'))
import query,textrules as T
from app import Engine
src=subprocess.check_output(['git','show','HEAD^:src/query.py'],cwd=ROOT).decode('utf8')
mod=types.ModuleType('m17_previous');mod.__file__=str(ROOT/'src/query.py');sys.modules[mod.__name__]=mod;exec(compile(src,'HEAD^:src/query.py','exec'),mod.__dict__)
engines={'current':Engine(),'previous':Engine()};engines['previous'].kg.conn.close();engines['previous'].kg=mod.OncoKG()
for e in engines.values():
 e.kg.conn.close();e.kg.conn=sqlite3.connect((ROOT/'data/processed/oncokg.sqlite').as_uri()+'?mode=ro',uri=True);e.kg.conn.row_factory=sqlite3.Row
cases = ['trastuzumab labelled-I-124', 'trastuzumab labelled-124I', 'I-124-labelled trastuzumab', 'trastuzumab labelled with I-124', 'trastuzumab labelled-with-I-124', 'trastuzumab labelled-with-124I', 'trastuzumab radiolabelled-I-124', 'trastuzumab radiolabeled-I124', 'trastuzumab radiolabelled with I-124', 'iodine-I-124 trastuzumab', 'iodine I-124 trastuzumab', 'trastuzumab iodine-I-124', 'trastuzumab (iodine-I-124)', 'trastuzumab [iodine-I-124]', 'trastuzumab LABELLED-I-124', 'TRASTUZUMAB LABELLED-I-124', 'trastuzumab labelled-i-124', 'trastuzumab labelled_I_124', 'trastuzumab labelled:I-124', 'trastuzumab labelled(I-124)', 'trastuzumab labelled[I-124]', 'trastuzumab labelled-I-124, osimertinib', 'osimertinib, trastuzumab labelled-I-124', 'trastuzumab labelled-I-124 and osimertinib', 'osimertinib and trastuzumab labelled-I-124', 'trastuzumab labelled-124I, osimertinib', 'vinblastine tritium-H-3', 'vinblastine tritium-3H', 'vinblastine labelled-H3', 'vinblastine labelled-3H', 'vinblastine H3', 'vinblastine H-3', 'vinblastine 3H', 'erlotinib fluorine-F18', 'erlotinib fluorine F18', 'erlotinib labelled-F18', 'erlotinib labelled-18F', 'erlotinib F18', 'erlotinib 18F', 'paclitaxel carbon-C14', 'paclitaxel carbon C14', 'paclitaxel labelled-C14', 'paclitaxel labelled-14C', 'paclitaxel C14', 'paclitaxel 14C', 'cetuximab labelled-Y-90', 'cetuximab labelled-90Y', 'cetuximab Y-90', 'cetuximab 90Y', 'osimertinib 80 mg', 'paclitaxel 2 cycles', 'cisplatin 75 mg/m2 day 1', '13-cis retinoic acid', 'BKM120', 'AZD9291', 'trastuzumab', 'vinblastine', 'erlotinib', 'paclitaxel', 'cetuximab', '89-ZrDFO trastuzumab', '3hvinblastine', 'A33124i']
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
