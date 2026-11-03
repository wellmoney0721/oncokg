from pathlib import Path
import json

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[1]
results={}
sdk_replays=json.loads((OUT/'modelui_legacy_sdk_failure_results.json').read_text(encoding='utf-8'))
for round_name in ['s1','s2']:
    oldbase=ROOT/'audit_evidence_claims'/round_name
    newbase=OUT/('replay_'+round_name)
    old=json.loads((oldbase/'modelui_results.json').read_text(encoding='utf-8'))
    new=json.loads((newbase/'modelui_results.json').read_text(encoding='utf-8'))
    oldinputs={r['case']:(r.get('raw_reply'),r.get('input_description')) for r in old['model_cases']}
    newinputs={r['case']:(r.get('raw_reply'),r.get('input_description')) for r in new['model_cases']}
    results[round_name]={'model_cases_recorded':len(new['model_cases']),
        'missing_cases':sorted(set(oldinputs)-set(newinputs)),
        'common_model_inputs_identical':all(oldinputs[k]==v for k,v in newinputs.items()),
        'api_requests_identical':[(r['case'],r['request']) for r in old['api_cases']]==[(r['case'],r['request']) for r in new['api_cases']],
        'api_count':len(new['api_cases'])}
    sdk=next(r for r in sdk_replays if r['source_round']==round_name)
    results[round_name]['model_cases_executed']=len(new['model_cases'])+1
    results[round_name]['legacy_sdk_failure_captured_separately']=sdk['result']['checks']['applicable'] is False
    results[round_name]['sdk_capture_artifact']='modelui_legacy_sdk_failure_results.json'
    page=json.loads((newbase/'modelui_page_results.json').read_text(encoding='utf-8'))
    results[round_name]['page_cases']=len(page)
    results[round_name]['page_no_raw_injected_elements']=all(not r['has_raw_injected_element'] for r in page)
    if round_name=='s2':
        oldattack=json.loads((oldbase/'modelui_attack_results.json').read_text(encoding='utf-8'))
        newattack=json.loads((newbase/'modelui_attack_results.json').read_text(encoding='utf-8'))
        results[round_name]['attack_inputs_identical']=[(r['case'],r.get('input',r.get('input_template'))) for r in oldattack]==[(r['case'],r.get('input',r.get('input_template'))) for r in newattack]
        results[round_name]['attack_rows']=len(newattack)
        results[round_name]['nesting_subcases']=len(next(r['result'] for r in newattack if r['case']=='near_limit_nesting'))
        ap=json.loads((newbase/'modelui_attack_api_fixtures.json').read_text(encoding='utf-8'))
        oldap=json.loads((oldbase/'modelui_attack_api_fixtures.json').read_text(encoding='utf-8'))
        results[round_name]['attack_api_requests_identical']=[(r['case'],r['request']) for r in oldap]==[(r['case'],r['request']) for r in ap]
        results[round_name]['attack_api_count']=len(ap)
        page=json.loads((newbase/'modelui_attack_page_results.json').read_text(encoding='utf-8'))
        results[round_name]['attack_page_count']=len(page)
        results[round_name]['attack_page_no_raw_injected_elements']=all(not r['has_raw_injected_element'] for r in page)
new=json.loads((OUT/'modelui_new_results.json').read_text(encoding='utf-8'))
api=json.loads((OUT/'modelui_new_api_fixtures.json').read_text(encoding='utf-8'))
page=json.loads((OUT/'modelui_new_page_results.json').read_text(encoding='utf-8'))
results['new']={'rows':len(new),'api':len(api),'page':len(page),
    'no_raw_injected_elements':all(not r['has_raw_injected_element'] for r in page),
    'exceptions':[{k:r[k] for k in ['case','exception']} for r in new if 'exception' in r],
    'strict_json_failures':[{k:r[k] for k in ['case','serialize_exception']} for r in new if r.get('strict_json_serializable') is False]}
(OUT/'modelui_comparison.json').write_text(json.dumps(results,indent=2),encoding='utf-8')
print(json.dumps(results,indent=2))
