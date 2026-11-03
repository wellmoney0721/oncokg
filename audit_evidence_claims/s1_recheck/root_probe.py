"""Independent structured-answer adversarial checks; never writes the source graph."""
import copy
import hashlib
import json
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'src'))
import query
from structured import Verifier

OUT = Path(__file__).resolve().parent
kg = query.OncoKG()
kg.conn.execute('PRAGMA query_only=ON')
q = 'What does osimertinib target?'
entities = kg.link_entities(q)
ev = kg.retrieve(kg.classify(q, entities), entities)
base = {'kind': 'relation', 'relation': 'ACTS_ON', 'subject': 'osimertinib',
        'object': 'EGFR', 'evidence': ev[0].edge_id, 'action': 'INHIBITOR'}
results = []

def probe(tag, payload, evidence=ev):
    row = {'case': tag, 'question': q, 'input': payload}
    try:
        row['output'] = kg.verify_structured(payload, evidence)
    except Exception as exc:
        row['exception'] = {'type': type(exc).__name__, 'message': str(exc)}
    results.append(row)

probe('baseline', {'claims': [base]})
for name in [' osimertinib ', 'OSIMERTINIB', 'osimertinib is safe',
             'osimertinib\u662f\u5b89\u5168\u7684', '\u975eosimertinib',
             'osimertinib\uac00 \uc544\ub2cc', 'osimertinib\u200b',
             'osimertinib / placebo', 'osimertinib,osimertinib',
             'osimertinib\x00', 'osimertinib' + ' ' * 120,
             'o' * 121, 'ＯＳＩＭＥＲＴＩＮＩＢ']:
    c = dict(base, subject=name)
    probe('name:' + repr(name), {'claims': [c]})
values = [None, True, False, 0, 1, 1.0, '1', '', [], {}, ['ACTS_ON'],
          ['INHIBITOR', 1], float('nan'), float('inf')]
for key in base:
    for value in values:
        probe('type:' + key + ':' + repr(value), {'claims': [dict(base, **{key: value})]})
for key in ['note', '<img src=x onerror=alert(1)>', 'text']:
    probe('unknown_key:' + key, {'claims': [dict(base, **{key: 'untrusted'})]})
for count in [0, 1, 50, 51, 1000]:
    probe('claim_count:' + str(count), {'claims': [base] * count})
for raw in ['{"claims": [', 'null', 'NaN', 'Infinity', '{}', '[]',
            '{"claims": [' + json.dumps(base) + '], "claims": []}',
            '{"claims": [], "claims": [' + json.dumps(base) + ']}',
            '{"claims": [' + json.dumps(base)[:-1] + ', "action":"ACTIVATOR"}]}',
            '{"claims": [' + json.dumps(base)[:-1] + ', "action":"INHIBITOR"}]}',
            '[' * 1100 + '0' + ']' * 1100]:
    probe('raw_json:' + raw[:80], raw)

manifest = {'commit': 'aa5655ae89c47631fefb9c868989ba2c1befa82e',
            'sha256': {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                       for p in [ROOT/'data/processed/oncokg.sqlite', ROOT/'data/processed/resolved.json',
                                 ROOT/'src/structured.py', ROOT/'src/query.py', ROOT/'src/app.py',
                                 ROOT/'web/try.html']}}
(OUT/'root_manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
(OUT/'root_probe_results.json').write_text(json.dumps(results, ensure_ascii=True, indent=2), encoding='utf-8')
summary = {'cases': len(results), 'verified': sum(r.get('output', {}).get('verified', False) for r in results),
           'exceptions': [{k: r[k] for k in ['case', 'exception']} for r in results if 'exception' in r],
           'accepted_names': [{'case': r['case'], 'output': r['output']} for r in results
                              if r['case'].startswith('name:') and r.get('output', {}).get('verified')]}
print(json.dumps(summary, ensure_ascii=True, indent=2))
