import json
from pathlib import Path

ROOT = Path.cwd() / 'audit_evidence_claims'
OUT = ROOT / 's3'
read = lambda p: json.loads(p.read_text(encoding='utf-8'))
checks = {}
for stage in ['s1', 's2']:
    old = read(ROOT / stage / 'faithful_results.json')
    new = read(OUT / ('replay_' + stage) / 'faithful_results.json')
    for key in ['phase_examples', 'schema_limitations']:
        checks[stage + '_' + key + '_same_inputs'] = (
            [(x['question'], x['input']) for x in old[key]] ==
            [(x['question'], x['input']) for x in new[key]])
old = read(ROOT / 's1' / 'faithful_additional.json')
new = read(OUT / 'replay_s2' / 'faithful_additional_replay.json')
checks['all_four_action_inputs_unchanged'] = (
    [(x['question'], x['input']) for x in old['action_cases']] ==
    [(x['question'], x['input']) for x in new['action_cases']])
checks['profile_input_unchanged'] = old['profile']['input'] == new['profile']['input']
fixture = read(ROOT / 's1' / 'faithful_empty_phase_fixture.json')
checks['empty_phase_input_unchanged'] = fixture['input'] == new['empty_phase_fixture']['input']
checks['empty_phase_output_unchanged'] = fixture['output'] == new['empty_phase_fixture']['output']
checks['s1_dictionary_unchanged'] = read(OUT / 'replay_s2' / 'faithful_graph_dictionary.json')['counts'] == read(ROOT / 's1' / 'faithful_graph_dictionary.json')
checks['s2_dictionary_unchanged'] = read(OUT / 'replay_s2' / 'faithful_graph_dictionary.json') == read(ROOT / 's2' / 'faithful_graph_dictionary.json')
assert all(checks.values()), checks
(OUT / 'faithful_comparison.json').write_text(json.dumps(checks, indent=2), encoding='utf-8')
print(json.dumps(checks, indent=2))
