"""Independent semantic adjudication of explicit labelled-product inputs."""
from pathlib import Path
import json, sqlite3, subprocess, sys, types

sys.dont_write_bytecode = True
out = Path(__file__).resolve().parent
root = out.parents[2]
sys.path.insert(0, str(root/'src'))
from app import Engine
import query, textrules as T

old = types.ModuleType('m12_adjudicate_previous_query')
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
    '[89Z.r]-DFO-daratumumab',
    '[89Zr]-DFO-daratumumab',
    '89zr-dfo-daratumumab',
    'daratumumab',
    'trastuzumab labelled with [89Zr]',
    '[89Z.r]-labelled trastuzumab',
    '[89Zr]-labelled trastuzumab',
    'trastuzumab labelled with [89Z.r]',
    '[89Zr] trastuzumab',
    'trastuzumab [89Zr]',
    '[89Z.r] trastuzumab',
    '[89Zr] labelled trastuzumab',
    'trastuzumab labelled with [89Zr], osimertinib',
    'trastuzumab',
]
cases=[]
for text in texts:
    row={'text':text,'canonical_key':T.canonical_key(text)}
    for name,e in engines.items():
        folded=query._fold(text);blocked=e.kg._resolver_blocked(folded);item=e.kg._link(folded)
        row[name]={'resolver':e.resolve(text),'resolver_blocked':blocked,
                   'qualified':query._qualified(text.split()),'item_linker':item,
                   'whole_name':e.kg._whole_name(folded,blocked,item),
                   'public_linker':e.kg.link_entities(text),'map':e.explore(text,2),
                   'trials_qa':e.ask('Which trials evaluate '+text+'?'),
                   'sponsors_qa':e.ask('Which companies sponsor '+text+'?')}
    cases.append(row)
    c=row['current'];p=row['previous_query']
    print(json.dumps({'text':text,'center':c['map'].get('center',{}).get('label'),
        'old_center':p['map'].get('center',{}).get('label'),
        'refused':any(x['type']=='Refused' for x in c['public_linker']),
        'qa_counts':[len(c['trials_qa']['evidence']),len(c['sponsors_qa']['evidence'])]},ensure_ascii=True))
result={'cases':cases,'isotope_control':T.is_isotope_label('89Zr'),
        'stored_tracer_alias':engines['current'].dic['index'].get(T.canonical_key('89zr-trastuzumab')),
        'daratumumab_alias':engines['current'].dic['index'].get(T.canonical_key('89zr-dfo-daratumumab')),
        'isotope_removed_daratumumab_hits':engines['current'].dic['index'].get('dfodaratumumab',[]),
        'comparison_scope':'Exact HEAD^ query module, current app/rules/data; standalone qualified diagnostic uses current helper.'}
(out/'adjudication_tracer.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
for e in engines.values():e.kg.conn.close()
