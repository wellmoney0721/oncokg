import json
from pathlib import Path
r=Path.cwd(); out=r/'audit_evidence_claims/s4/faithful'
res=json.loads((out/'s1/faithful_results.json').read_text(encoding='utf-8'))
selected=[]
for demo in res['demonstrations']:
    for c in demo['modes']['labels']['input']['claims']:
        if c.get('subject') in ['Second Affiliated Hospital Of Nanchang University','Tianjin Medical University Cancer Institute And Hospital','ALECTINIB HYDROCHLORIDE'] or c.get('drug')=='ALECTINIB HYDROCHLORIDE':
            o=demo['modes']['labels']['output']
            selected.append({'question':demo['question'],'input':{'claims':[c]},'in_full_payload_verified':o['verified'],'corresponding_rendered_lines':[line for line in o['text'].splitlines() if c['evidence'] in line]})
checks={}
old=json.loads((r/'audit_evidence_claims/s1/faithful_additional.json').read_text(encoding='utf-8'))
new=json.loads((out/'s2/faithful_additional_replay.json').read_text(encoding='utf-8'))
checks['all_original_action_inputs_unchanged']=[(x['question'],x['input']) for x in old['action_cases']]==[(x['question'],x['input']) for x in new['action_cases']]
checks['profile_input_unchanged']=old['profile']['input']==new['profile']['input']
fixture=json.loads((r/'audit_evidence_claims/s1/faithful_empty_phase_fixture.json').read_text(encoding='utf-8'))
checks['empty_phase_input_unchanged']=fixture['input']==new['empty_phase_fixture']['input']
checks['empty_phase_output_unchanged']=fixture['output']==new['empty_phase_fixture']['output']
checks['s1_dictionary_unchanged']=json.loads((out/'s2/faithful_graph_dictionary.json').read_text(encoding='utf-8'))['counts']==json.loads((r/'audit_evidence_claims/s1/faithful_graph_dictionary.json').read_text(encoding='utf-8'))
assert all(checks.values()),checks
(out/'historical_input_comparison.json').write_text(json.dumps({'checks':checks,'selected_original_false_rejections':selected},indent=2),encoding='utf-8')
print(json.dumps({'checks':checks,'selected':selected},indent=2))
