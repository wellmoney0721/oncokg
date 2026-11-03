from pathlib import Path
import json

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
def read(path):
    return json.loads(path.read_text(encoding='utf-8'))

result = {}
sdk = read(OUT / 'modelui_legacy_sdk_failure_results.json')
for rnd in ['s1', 's2']:
    oldbase = ROOT / 'audit_evidence_claims' / rnd
    newbase = OUT / ('replay_' + rnd)
    old = read(oldbase / 'modelui_results.json')
    new = read(newbase / 'modelui_results.json')
    oldinputs = {r['case']:(r.get('raw_reply'), r.get('input_description')) for r in old['model_cases']}
    newinputs = {r['case']:(r.get('raw_reply'), r.get('input_description')) for r in new['model_cases']}
    page = read(newbase / 'modelui_page_results.json')
    result[rnd] = {
        'model_cases_executed':len(newinputs)+1,
        'recorded_model_rows':len(newinputs),
        'missing_cases':sorted(set(oldinputs)-set(newinputs)),
        'common_inputs_identical':all(oldinputs[k] == v for k,v in newinputs.items()),
        'outage_captured_separately':next(x for x in sdk if x['source_round']==rnd)['result']['checks']['applicable'] is False,
        'api_requests_identical':[(r['case'],r['request']) for r in old['api_cases']]==[(r['case'],r['request']) for r in new['api_cases']],
        'api_count':len(new['api_cases']), 'page_count':len(page),
        'no_raw_injected_elements':all(not r['has_raw_injected_element'] and not r['marker_executed'] for r in page),
        'exceptions':[r['case'] for r in new['model_cases'] if 'exception' in r]
    }
    if rnd == 's2':
        oldattack = read(oldbase / 'modelui_attack_results.json')
        attack = read(newbase / 'modelui_attack_results.json')
        ap = read(newbase / 'modelui_attack_api_fixtures.json')
        oldap = read(oldbase / 'modelui_attack_api_fixtures.json')
        page = read(newbase / 'modelui_attack_page_results.json')
        result[rnd].update({
            'attack_inputs_identical':[(r['case'],r.get('input',r.get('input_template'))) for r in oldattack]==[(r['case'],r.get('input',r.get('input_template'))) for r in attack],
            'attack_rows':len(attack),
            'nesting_subcases':len(next(r['result'] for r in attack if r['case']=='near_limit_nesting')),
            'attack_api_requests_identical':[(r['case'],r['request']) for r in oldap]==[(r['case'],r['request']) for r in ap],
            'attack_api_count':len(ap), 'attack_page_count':len(page),
            'attack_no_raw_injected_elements':all(not r['has_raw_injected_element'] and not r['marker_executed'] for r in page),
            'attack_exceptions':[{k:r[k] for k in ['case','exception']} for r in attack if 'exception' in r],
            'attack_strict_json_failures':[r['case'] for r in attack if r.get('strict_json_serializable') is False],
        })

oldbase = ROOT / 'audit_evidence_claims/s3'
newbase = OUT / 'replay_s3'
old = read(oldbase/'modelui_new_results.json')
new = read(newbase/'modelui_new_results.json')
ap = read(newbase/'modelui_new_api_fixtures.json')
oldap = read(oldbase/'modelui_new_api_fixtures.json')
page = read(newbase/'modelui_new_page_results.json')
result['s3'] = {
    'rows':len(new),'api_count':len(ap),'page_count':len(page),
    'inputs_identical':[(r['case'],r.get('input')) for r in old]==[(r['case'],r.get('input')) for r in new],
    'api_requests_identical':[(r['case'],r['request']) for r in oldap]==[(r['case'],r['request']) for r in ap],
    'all_outputs_identical':old==new,
    'all_http_outputs_identical':oldap==ap,
    'all_strict_http_json':all(r['strict_json'] for r in ap),
    'no_raw_injected_elements':all(not r['has_raw_injected_element'] and not r['marker_executed'] for r in page),
    'exceptions':[{k:r[k] for k in ['case','exception']} for r in new if 'exception' in r],
    'strict_json_failures':[{k:r[k] for k in ['case','serialize_exception']} for r in new if r.get('strict_json_serializable') is False]
}
(OUT/'comparison.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps(result,indent=2))
assert result['s1']['common_inputs_identical'] and result['s2']['common_inputs_identical']
assert result['s2']['attack_inputs_identical'] and result['s3']['inputs_identical']
assert all(r['no_raw_injected_elements'] for r in result.values())
