"""Compare fresh historical evidence with m12, keeping positive identities and refusal state."""
from pathlib import Path
import json
root=Path.cwd();out=Path(__file__).resolve().parent;prior=root/'audit_evidence_claims/m16/names'
matrix=json.loads((prior/'historical_name_dispositions.json').read_text(encoding='utf8'))
ignored={'label','matched_text','matched_alias','why','rules','resolver','resolver_blocked','blocked','qualified','canonical_key','alnum_words','dictionary_hits','dictionary','matched_aliases','normalized_input','previous','previous_map','previous_linker','old_linker','old','baseline','baseline_ask','baseline_ask_using_old_linker','baseline_explore_using_old_linker','oldmethod','old_current','seconds','elapsed','elapsed_s','milliseconds','ms','pid','owned_server_pid','server_pid','port','previous_query_sha256','head','previous_ref','comparison_scope','current_explore_seconds'}
def clean(obj):
    if isinstance(obj,list):return [clean(v) for v in obj]
    if isinstance(obj,dict):
        if obj.get('type')=='Refused':return {'type':'Refused'}
        result={}
        for k,v in obj.items():
            if k in ignored or k.startswith(('baseline_','previous_','old_')):continue
            if k=='refused':result[k]=bool(v)
            else:result[k]=clean(v)
        return result
    return obj
def diff(a,b,path=''):
    if type(a)!=type(b):return [{'path':path,'previous':a,'current':b}]
    if isinstance(a,dict):
        result=[]
        for k in sorted(a.keys()|b.keys()):
            if k not in a or k not in b:result.append({'path':path+'/'+k,'previous':a.get(k),'current':b.get(k)})
            else:result+=diff(a[k],b[k],path+'/'+k)
        return result
    if isinstance(a,list):
        if len(a)!=len(b):return [{'path':path,'previous_length':len(a),'current_length':len(b)}]
        return [d for i,(x,y) in enumerate(zip(a,b)) for d in diff(x,y,path+'/'+str(i))]
    return [] if a==b else [{'path':path,'previous':a,'current':b}]
files=sorted({r['evidence'] for r in matrix})
results=[]
for name in files:
    current_path = out / ('m14_exact/fresh_results.json' if name == '../attacks/fresh_results.json' else name)
    if not current_path.exists():
        results.append(dict(file=name,missing=True));continue
    before=json.loads((prior/name).read_text(encoding='utf8'));after=json.loads(current_path.read_text(encoding='utf8'))
    differences=diff(clean(before),clean(after))
    results.append(dict(file=name,identical=before==after,normalized_equal=not differences,differences=differences))
(out/'replay_comparison.json').write_text(json.dumps(dict(semantics='Compares current identity, map/evidence values and refusal existence, ignoring refusal wording and stated baseline outputs. Differences inspected separately; not a product correctness oracle.',ignored_keys=sorted(ignored),files=results),ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps([dict(file=r['file'],missing=r.get('missing',False),differences=len(r.get('differences',[]))) for r in results if r.get('missing') or r.get('differences')],indent=2))
