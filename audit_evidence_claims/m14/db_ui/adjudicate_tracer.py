"""Independent semantic adjudication of explicit labelled-product inputs."""
from pathlib import Path
import json, sqlite3, subprocess, sys, types

sys.dont_write_bytecode = True
out = Path(__file__).resolve().parent
root = out.parents[2]
sys.path.insert(0, str(root/'src'))
from app import Engine
import query, textrules as T

old = types.ModuleType('m14_adjudicate_previous_query')
old.__file__ = str(root/'src/query.py')
sys.modules[old.__name__] = old
exec(compile(subprocess.check_output(['git','show','HEAD^:src/query.py']),
             'HEAD^:src/query.py','exec'),old.__dict__)
engines={'current':Engine(),'previous_query':Engine()}
engines['previous_query'].kg.conn.close()
engines['previous_query'].kg=old.OncoKG()
for e in engines.values():
    e.kg.conn.close()
    e.kg.conn=sqlite3.connect((root/'data/processed/oncokg.sqlite').as_uri()+'?mode=ro',uri=True)
    e.kg.conn.row_factory=sqlite3.Row
texts=[
    '3Hvinblastine', '3hvinblastine', '[3h]-vinblastine', '3H-vinblastine', 'vinblastine',
    '89Zrpanitumumab-PET-CT', '89Zr-panitumumab-PET-CT', '89zr-panitumumab-pet/ct', 'panitumumab',
    '3Hvinblastine, osimertinib', '89Zrpanitumumab-PET-CT, osimertinib',
]

cases=[]
for text in texts:
    row={'text':text,'canonical_key':T.canonical_key(text),'alnum_words':query._alnum_words(text),'radiotracer':T.is_radiotracer(text)}
    for name,e in engines.items():
        folded=query._fold(text);blocked=e.kg._resolver_blocked(folded)
        marked_trace=[];original_marked=e.kg._marked
        def traced_marked(key,did,tokens,seg,a,b):
            value=original_marked(key,did,tokens,seg,a,b)
            marked_trace.append({'key':key,'drug_id':did,'tokens':tokens,'segment':seg,'start':a,'end':b,'return':value})
            return value
        e.kg._marked=traced_marked
        try:item=e.kg._link(folded)
        finally:e.kg._marked=original_marked
        row[name]={'resolver':e.resolve(text),'resolver_blocked':blocked,
                   'qualified':(query if name=='current' else old)._qualified(text.split()),'item_linker':item,
                   'whole_name':e.kg._whole_name(folded,blocked,item),
                   'public_linker':e.kg.link_entities(text),'marked_trace':marked_trace,'map':e.explore(text,2),
                   'trials_qa':e.ask('Which trials evaluate '+text+'?'),
                   'sponsors_qa':e.ask('Which companies sponsor '+text+'?')}
    cases.append(row)
    c=row['current'];p=row['previous_query']
    print(json.dumps({'text':text,'center':c['map'].get('center',{}).get('label'),
        'old_center':p['map'].get('center',{}).get('label'),
        'refused':any(x['type']=='Refused' for x in c['public_linker']),
        'qa_counts':[len(c['trials_qa']['evidence']),len(c['sponsors_qa']['evidence'])]},ensure_ascii=True))
result={'cases':cases,'isotope_controls':{x:T.is_isotope_label(x) for x in ['3H','89Zr']},
        'dictionary_evidence':{a:engines['current'].dic['index'].get(T.canonical_key(a),[]) for a in ['[3h]-vinblastine','vinblastine','89zr-panitumumab-pet/ct','panitumumab']},
        'same_drug_key_diagnostics':{did:{'keys':sorted(engines['current'].kg._keys_of(did)),
            'remainder':rem,'keys_that_end_remainder':[k for k in engines['current'].kg._keys_of(did) if len(k)>=5 and rem.endswith(k)]}
            for did,rem in [('CHEMBL159','vinblastine'),('CHEMBL1201827','panitumumabpetct')]},
        'comparison_scope':'Exact HEAD^ query module, current app/rules/data; qualified diagnostic uses each matching query module.'}
(out/'adjudication_tracer.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
for e in engines.values():e.kg.conn.close()
