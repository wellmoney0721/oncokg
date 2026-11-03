"""Independent Round 10 lexical attacks; every write remains beside this script."""
import json, re, sqlite3, string, sys, time
from pathlib import Path
sys.dont_write_bytecode = True
OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
sys.path.insert(0, str(ROOT / 'src'))
import query
import textrules as T
from app import Engine
e = Engine()
e.kg.conn.close()
e.kg.conn = sqlite3.connect((ROOT / 'data/processed/oncokg.sqlite').as_uri()+'?mode=ro',uri=True)
e.kg.conn.row_factory = sqlite3.Row
cases = {}
def add(family, text):
    cases.setdefault(text, family)
seps = [' ', '-', '_', '.', ':', '/', '|', ',', ';', '+', '&', '\u200b', '\u00ad', '\u0301', ' - ', ' _ ', ' : ', ' . ', ' / ', ' + ']
for drug,sfx in [('bevacizumab','awwb'),('trastuzumab','dkst'),('rituximab','abbs')]:
    for sep in seps:
        for s in [drug+sep+sfx, drug+' '+sep+sfx, drug+sep+sfx+' EGFR', drug+' ('+sfx+')']:
            add('suffix',s)
    for s in ['awwb bevacizumab','bevacizumab a w w b','bevacizumab (a w w b)','bevacizumab - Pfizer','bevacizumab Pfizer']:
        add('suffix_extra',s)
for iso,drug in [('89Zr','trastuzumab'),('177Lu','dotatate'),('68Ga','edotreotide'),('18F','fluorothymidine')]:
    num,el = re.match(r'(\d+)(\w+)',iso).groups()
    for sep in seps:
        label = num+sep+el
        for s in [label+' '+drug, '['+label+'] '+drug, drug+' '+label, drug+' ['+label+']', label+'-'+drug, drug+'-'+label]:
            add('isotope',s)
    for s in [f'{iso} labeled {drug}', f'{iso} labelled {drug}',f'{drug} labeled with {iso}', f'{drug} {iso} tracer',f'{el}-{num} {drug}',f'{drug} ({el}-{num})']:
        add('isotope_extra',s)
for qualifier,drug in [('generic version','bevacizumab'),('follow on biologic','bevacizumab'),('oral','azacitidine'),('albumin bound','paclitaxel'),('nanoparticle albumin bound','paclitaxel'),('bio similar','bevacizumab'),('liposomal','doxorubicin')]:
    for sep in seps:
        add('qualifier_separator',qualifier.replace(' ',sep)+' '+drug)
        add('qualifier_separator',qualifier.replace(' ',sep)+' of '+drug)
        add('qualifier_separator',drug+' ('+qualifier.replace(' ',sep)+')')
for s in ['osimertinib','bevacizumab','trastuzumab','cemiplimab-rwlc','dostarlimab-gxly', 'bevacizumab-awwb', '89Zr trastuzumab', '[89.Zr] trastuzumab', 'generic version of bevacizumab','oral azacitidine','albumin-bound paclitaxel','liposomal doxorubicin']:
    add('control',s)
# Complete stored tracer/suffixed aliases and spelling changes test positive-key equivalence.
alias_candidates=[]
for key,hits in e.dic['index'].items():
    for h in hits:
        alias=h['alias']
        words=query._alnum_words(alias)
        iso=any(T.is_isotope_label(' '.join(words[i:i+n])) for n in [1,2] for i in range(len(words)-n+1))
        suffix=any(key.endswith(s) and e.dic['index'].get(key[:-len(s)]) for s in T.BIOSIMILAR_FDA_SUFFIXES)
        if iso or suffix:
            alias_candidates.append({'alias':alias,'drug_id':h['drug_id'],'key':key,'isotope':iso,'suffix':bool(suffix)})
            add('stored_marked_alias',alias)
            add('stored_marked_alias_fold',re.sub(r'[^\w\s]+','_',alias))
rows=[]
start=time.perf_counter()
for i,(text,family) in enumerate(cases.items()):
    norm=query._fold(text)
    blocked=e.kg._resolver_blocked(norm)
    linked=e.kg._link(norm)
    mapped=e.explore(text,1)
    rows.append({'family':family,'text':text,'resolver':e.resolve(text),'blocked':blocked,'item_linker':linked,
        'whole_name':e.kg._whole_name(norm,blocked,linked),'public_linker':e.kg.link_entities(text),
        'map':{k:v for k,v in mapped.items() if k!='groups'},'key':T.canonical_key(text),
        'dictionary':e.dic['index'].get(T.canonical_key(text),[])})
    if (i+1)%200==0: print('completed',i+1,flush=True)
(OUT/'probe_results.json').write_text(json.dumps({'seconds':time.perf_counter()-start,'cases':rows,'alias_candidates':alias_candidates},ensure_ascii=False,indent=2),encoding='utf-8')
leaks=[{'family':r['family'],'text':r['text'],'id':r['map'].get('center',{}).get('id'),'label':r['map'].get('center',{}).get('label'),'blocked':r['blocked'],'refused':any(x['type']=='Refused' for x in r['public_linker'])} for r in rows if r['map'].get('center',{}).get('type')=='Drug']
(OUT/'positive_summary.json').write_text(json.dumps(leaks,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'cases':len(rows),'drug_maps':len(leaks),'seconds':time.perf_counter()-start}))
e.kg.conn.close()
