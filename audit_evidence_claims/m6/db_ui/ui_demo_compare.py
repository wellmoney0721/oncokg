"""Compare fresh round-6 actual demo answers with the recorded round-5 baseline."""
from pathlib import Path
import json

OUT = Path(__file__).resolve().parent
previous = json.loads((OUT.parents[1] / 'm5/ui_demos_responses.json').read_text(encoding='utf8'))
current = json.loads((OUT / 'ui_demos_responses.json').read_text(encoding='utf8'))
rows = []
for old, new in zip(previous, current):
    assert (old['kind'], old['index'], old['request']) == (new['kind'], new['index'], new['request'])
    row = {'kind': new['kind'], 'index': new['index'], 'request': new['request'],
           'identical': old == new, 'error': new.get('error')}
    if new['kind'] == 'EX2':
        row['current_intent'] = new['response']['intent']
        row['evidence_count'] = len(new['response']['evidence'])
        row['entities'] = new['response']['entities']
    if old != new:
        row['previous'] = old
        row['current'] = new
    rows.append(row)
result = {'total': len(current), 'identical': sum(r['identical'] for r in rows),
          'errors': sum(r['error'] is not None for r in rows), 'rows': rows}
(OUT / 'ui_demo_compare.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf8')
print(json.dumps({k: v for k, v in result.items() if k != 'rows'}, ensure_ascii=False))
for row in rows:
    if not row['identical']:
        print(row['kind'], row['index'], row['request'])
