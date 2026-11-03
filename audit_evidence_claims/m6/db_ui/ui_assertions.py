"""Assert the recorded fresh page-script results, without altering app files."""
from pathlib import Path
import json

out = Path('audit_evidence_claims/m6/db_ui')
load = lambda name: json.loads((out / name).read_text(encoding='utf-8'))
h = load('ui_harness_results.json')
r = load('ui_regressions.json')
m = load('ui_m3_checks.json')
counts = load('ui_missing_sponsor_count.json')
maps = load('ui_real_maps.json')
# Primary reviewer confirmed ownership and completion of this CLI HTTP run.
http_dir = out.parent / 'root_checks'
http = json.loads((http_dir / 'http_results.json').read_text(encoding='utf-8'))
checks = []

def check(name, condition):
    checks.append({'name': name, 'pass': bool(condition)})
    assert condition, name

check('served page equals worktree', (http_dir/'served_try.html').read_bytes() == Path('web/try.html').read_bytes())
check('all terminal states clear trail and obsolete back is harmless', all(
    x['trail'] == [] and x['trailHTML'] == '' and x['oldButtonThrows'] is False
    for x in h['failureVariants'].values()))
check('concurrent duplicate has one trail entry', len(h['doubleClick']['trail']) == 1)
check('reverse completion preserves KRAS', h['reverseResponses']['trail'] == [['ENSG00000133703', 'KRAS']])
check('stale network error preserves KRAS', h['staleError']['trail'] == [['ENSG00000133703', 'KRAS']])
check('unsafe URL schemes/host spoofs rejected', all(v == '' for u,v in h['urlChecks'].items()
    if u not in ['https://clinicaltrials.gov/study/NCT00200395', 'https://www.clinicaltrials.gov/study/NCT00200395']))
check('safe registry links remain clickable', h['urlChecks']['https://clinicaltrials.gov/study/NCT00200395'] != '')
check('no raw injected img/script/javascript href', all(r['markupChecks'][k] is False for k in
    ['injectionHasRawImg', 'injectionHasRawScript', 'injectionHasJavascriptHref']))
check('node ID escaped and unknown type fallback', all(r['markupChecks'][k] is True for k in
    ['escapedNodeId', 'unknownTypeTooltipPreserved', 'unknownTypeNotUndefined']))
check('all score precisions are retained', all(str(x['stored_api_score']) in x['rendered'] for x in r['precision']))
check('boolean score cannot throw', all('error' not in x for x in r['scoreTypeChecks']) and r['fullRenderBoolean']['ok'])
check('unknown sponsor roles never guessed', all('역할 기록 없음' in x['heading'][0]
    for x in r['missingRoleChecks'] if x['group']['role'] not in ('lead_sponsor','collaborator')))
check('unknown sponsor counts never become 0', all(not x['displayedZero'] and all('기록 없음' in d['detail'] for d in x['details'])
    for x in counts['results'] if x['stored_props'] in ('null','[]','{broken','{}')))
check('Trial start displayed', '시작 2003-07-02' in h['real']['NCT00200395']['html'])
check('zero trial count displayed', '이 그래프 안 임상 0건' in h['real']['CHEMBL925']['html'])
check('all actual demo form renders succeed', len(load('ui_demos_results.json')) == 36 and not any(x['hasUiError'] for x in load('ui_demos_results.json')))
check('all actual example click callbacks tested', len(m['demoClicks']) == 36 and len(m['mapClicks']) == 6)
check('all render error entry points handled', len(m['renderErrors']) == 4 and all(x['trail'] == [] and x['trailHTML'] == '' for x in m['renderErrors']))
check('blank submit retains previous state', m['blankSubmit'] == {'requestCount':0,'preservedPreviousView':True})
same=[]
for case in http['cases'].values():
    request=case.get('input')
    if case.get('status') == 200 and isinstance(request,dict) and request.get('text') in maps:
        name=request['text']
        check('HTTP map matches direct map: '+name, case['body'] == maps[name])
        same.append(name)
result={'checks':checks,'passed':len(checks),'http_map_matches':same,
        'ui_fixture_rendering_only':True,'browser_execution_claim':False}
(out/'ui_assertions.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'passed':len(checks),'http_map_matches':same},ensure_ascii=False))
