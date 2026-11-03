import ast, hashlib, json, sys
from pathlib import Path
sys.dont_write_bytecode = True
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
sys.path.insert(0,str(ROOT/'src'))
import query, textrules as T
load=lambda n:json.loads((OUT/n).read_text(encoding='utf8'))
summary={}
for family in ['focused','fresh','edge','targeted','previous','m17','new']:
    r=load(family+'_results.json')
    summary[family]={'count':len(r['cases']),'head':r['head'],'previous':r['previous']}
rows={r['text']:r for r in load('new_results.json')['cases']}
primary=rows['trastuzumab radiolabelled with iodine-124']
for version in ['current','previous']:
    p=primary[version]
    assert p['map']['center']['id']=='CHEMBL1201585' and p['map']['center']['trials']==13
    assert not p['blocked'] and p['whole_name'] is None
    assert not any(x['type']=='Refused' for x in p['public_linker'])
    assert all(x['result'] is None for x in p['marked_calls'])
    assert all(not x['tier'].startswith('BLOCKED') for x in p['resolver']['components'])
    assert len(p['trial_qa']['evidence'])==len(p['sponsor_qa']['evidence'])==12
assert not primary['current']['qualified'] and not primary['current']['item_has_isotope']
for text in ['trastuzumab radiolabelled with I-124','trastuzumab radiolabelled with 124I',
             'trastuzumab labelled-I-124','trastuzumab labelled-124I']:
    p=rows[text]['current']
    assert p['map'].get('refused') and not p['map'].get('center')
    assert not p['trial_qa']['evidence'] and not p['sponsor_qa']['evidence']
oldcases=load('m17_results.json')['cases']
oldprimary=next(r for r in oldcases if r['text']=='trastuzumab labelled-I-124')
assert oldprimary['current']['map'].get('refused') and not oldprimary['current']['map'].get('center')
summary['m17_primary']='FIXED; mass-first and element-first controls refuse'
summary['m17_changed_center_cases']=sum(r['current']['map'].get('center',{}).get('id')!=r['previous']['map'].get('center',{}).get('id') for r in oldcases)
for name in ['new_lifecycle.json','m17_lifecycle.json','previous_lifecycle.json']:
    life=load(name)
    assert life['port_closed'] and life['database_unchanged'] and life['all_200'] and life['page_matches_worktree']
    summary[name]=life
old=json.loads((ROOT/'audit_evidence_claims/m17/attacks/alias_variants.json').read_text(encoding='utf8'))
new=load('alias_variants.json');by_text={r['text']:r for r in old};changes=[]
for r in new:
    before=by_text[r['text']]
    if (before.get('center'),bool(before.get('refused')))!=(r.get('center'),bool(r.get('refused'))):
        changes.append({'text':r['text'],'old':before,'new':r})
comparison={'old_count':len(old),'new_count':len(new),'unique_keys':len(set(r['key'] for r in new)),'changes':changes}
(OUT/'alias_variants_comparison.json').write_text(json.dumps(comparison,indent=2,ensure_ascii=False),encoding='utf8')
assert not changes
summary['alias_variants']=comparison
literal_checks=[]
for r in load('reuse_manifest.json'):
    dest=ROOT/r['copy'];src=ROOT/r['source']
    if dest.name in ['new_probe.py','new_http.py']:continue
    def cases(p):
        tree=ast.parse(p.read_text(encoding='utf8'))
        a=next((x for x in tree.body if isinstance(x,ast.Assign) and any(isinstance(t,ast.Name) and t.id in ['cases','CASES'] for t in x.targets) and isinstance(x.value,ast.List)),None)
        return ast.literal_eval(a.value) if a else None
    same=cases(dest)==cases(src);assert same
    literal_checks.append({'source':str(src.relative_to(ROOT)),'copy':str(dest.relative_to(ROOT)),'case_literals_identical':same})
(OUT/'literal_preservation.json').write_text(json.dumps(literal_checks,indent=2),encoding='utf8')
helpers=[]
for token in ['iodine-124','I-124','124I','labelled-iodine-124','labelled-I-124','labelled-124I','labelled-I-1-24',
              'zirconium-89','Zr-89','89Zr','BKM120','AZD9291']:
    parts=[p.lower() for p in query._alnum_words(token)]
    keys=[T.canonical_key(token)]+parts+[a+b for a,b in zip(parts,parts[1:])]
    helpers.append({'token':token,'keys_checked':keys,'item_has_isotope':query._item_has_isotope((token,))})
(OUT/'helper_evidence.json').write_text(json.dumps(helpers,indent=2),encoding='utf8')
summary['checks']='Primary all-stage originator bypass; paired controls; M17 repair; unchanged alias outcomes; HTTP200; closed owned ports; DB hashes unchanged; literal case preservation.'
(OUT/'final_checks.json').write_text(json.dumps(summary,indent=2),encoding='utf8')
print(json.dumps(summary,indent=2))
