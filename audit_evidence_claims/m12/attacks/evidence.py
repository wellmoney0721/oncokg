import json,sys
from pathlib import Path
sys.dont_write_bytecode=True;sys.path.insert(0,str(Path.cwd()/'src'))
import textrules as T
p=Path('audit_evidence_claims/m12/attacks');r=json.loads((p/'focused_results.json').read_text(encoding='utf8'))
c=r['cases'][0];dic=json.loads(Path('data/processed/resolved.json').read_text(encoding='utf8'))['dictionary']
orig=json.loads(Path('audit_evidence_claims/m11/root_checks/fresh_probe.json').read_text(encoding='utf8'))
evidence={'stored_alias':'89zr-dfo-daratumumab','input':'[89Z.r]-DFO-daratumumab','input_key':T.canonical_key(c['text']),'control_key':T.canonical_key('89zr-dfo-daratumumab'),'dictionary_hits':dic['index'].get(T.canonical_key(c['text'])),'rest_key':'dfodaratumumab','rest_hits':dic['index'].get('dfodaratumumab',[]),'bare_drug_hits':dic['index'].get('daratumumab'),'split_inside_words':['89Z','r','DFO','daratumumab'],'inside_predicate':{'89Z':T.is_isotope_label('89Z'),'89Z r':T.is_isotope_label('89Z r'),'89Zr':T.is_isotope_label('89Zr')},'prior_unpromoted_observations':[{'input':x['input'],'center':x['map'].get('center',{}).get('id'),'refused':[e for e in x['public'] if e['type']=='Refused']} for x in orig if 'labeled' in x['input'] or 'labelled' in x['input'] or 'conjugated' in x['input']],'cases':len(r['cases'])}
(p/'dictionary_evidence.json').write_text(json.dumps(evidence,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(evidence,ensure_ascii=True,indent=2))
