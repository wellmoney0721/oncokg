from pathlib import Path
import json
import urllib.request
import hashlib

out = Path('audit_evidence_claims/m3')
base = 'http://127.0.0.1:8879'
direct = json.loads((out / 'ui_real_maps.json').read_text(encoding='utf-8'))
page = urllib.request.urlopen(base + '/').read()
(out / 'ui_served_try.html').write_bytes(page)
results = {'served_matches_disk': page == Path('web/try.html').read_bytes(),
           'page_sha256': hashlib.sha256(page).hexdigest(), 'requests': []}
for text in ['EGFR', 'KRAS', 'NCT00200395', 'NCT00754364', 'CHEMBL1201438',
             'MONDO_0005233', 'AstraZeneca', 'Roche', 'MET', 'CHEMBL925']:
    body = json.dumps({'text': text}).encode('utf-8')
    request = urllib.request.Request(base + '/api/explore', data=body,
                                     headers={'Content-Type': 'application/json'})
    with urllib.request.urlopen(request) as response:
        data = json.load(response)
        results['requests'].append({'input': text, 'status': response.status,
                                    'equals_direct_fixture': data == direct[text]})
(out / 'ui_http_check.json').write_text(json.dumps(results, indent=2), encoding='utf-8')
print(json.dumps(results))
