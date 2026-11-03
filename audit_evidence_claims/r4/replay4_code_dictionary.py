import sys, inspect, textwrap, json, re
from pathlib import Path
sys.dont_write_bytecode = True
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / 'src'))
import query
import normalize as N

kg = query.OncoKG()
src = textwrap.dedent(inspect.getsource(query.OncoKG.link_entities))
gate = '            if hits and size > 1 and not re.search(r"[\\s\\-/]", hits[0]["alias"]):\n                hits = None\n'
assert gate in src
ns = dict(query.__dict__)
exec(src.replace(gate, ''), ns)
old_link = ns['link_entities']
rows = []
for key, hits in kg.dic['index'].items():
    for h in hits:
        if re.search(r'\s', h['alias']):
            rows.append((key, h['alias'], hits[0]['alias'], h['drug_id']))
aliases = sorted({r[1] for r in rows})
changes=[]
lost=[]
for alias in aliases:
    old=old_link(kg, alias)
    new=kg.link_entities(alias)
    oi={(e['type'],e['id']) for e in old}
    ni={(e['type'],e['id']) for e in new}
    if oi != ni:
        changes.append({'input':alias,'before':old,'after':new})
    expected={r[3] for r in rows if r[1]==alias}
    if {e['id'] for e in old if e['type']=='Drug'} & expected and not ({e['id'] for e in new if e['type']=='Drug'} & expected):
        lost.append({'input':alias,'before':old,'after':new})

variants=['is a','AZD 9291','AZD9291','osimertinib mesylate','trastuzumab deruxtecan','pemetrexed disodium','nab paclitaxel']
variant_results=[{'input':a,'before':old_link(kg,a),'after':kg.link_entities(a)} for a in variants]
result={'index_keys':len(kg.dic['index']),'drugs':len(kg.dic['drugs']), 'multiword_index_rows':len(rows),'unique_multiword_aliases':len(aliases),'stored_alias_changes':changes,'lost_intended_links':lost,'variants':variant_results}
out=Path(__file__).with_suffix('.json')
out.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'summary':{k:v for k,v in result.items() if not isinstance(v,list)}, 'change_count':len(changes),'lost_count':len(lost),'changes':changes[:15],'variants':variant_results},ensure_ascii=False,indent=2))
