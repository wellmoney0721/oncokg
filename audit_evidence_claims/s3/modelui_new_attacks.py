"""s3 parser, sanitiser, LLM failure, and page attacks (read-only graph)."""
import builtins
import copy
import json
import math
import os
from pathlib import Path
import sys
import threading
from http.server import ThreadingHTTPServer
import types
import urllib.request
import urllib.error
from unittest.mock import patch

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[1]
sys.path.insert(0, str(ROOT / 'src'))
import query
import app

Q = 'What does osimertinib target?'
EDGE = 'CHEMBL3353410|ACTS_ON|ENSG00000146648|CHEMBL3353410'
GOOD = dict(kind='relation', relation='ACTS_ON', subject='osimertinib', object='EGFR', evidence=EDGE, action='INHIBITOR')
MARK = '<img src=x onerror="globalThis.MODEL_INJECTED=1"><script>globalThis.MODEL_INJECTED=2</script>&"\''
kg = query.OncoKG()
kg.conn.execute('PRAGMA query_only=ON')
ents = kg.link_entities(Q)
ev = kg.retrieve(kg.classify(Q, ents), ents)
rows = []
api = []

def capture(name, inp, fn):
    row = {'case': name, 'input': inp}
    try:
        result = fn()
        row['result'] = result
        try:
            encoded = json.dumps(result, allow_nan=False)
            row['strict_json_serializable'] = True
            row['strict_json_bytes_ascii'] = len(encoded)
        except Exception as err:
            row['strict_json_serializable'] = False
            row['serialize_exception'] = type(err).__name__ + ': ' + str(err)
            # Ensure the review artifact itself remains writable.
            row['result'] = {'verified': result.get('verified'), 'text': result.get('text'), 'rejected_count': len(result.get('rejected', []))}
        try:
            json.dumps(result, ensure_ascii=False, allow_nan=False).encode('utf-8')
            row['utf8_serializable'] = True
        except Exception as err:
            row['utf8_serializable'] = False
            row['utf8_exception'] = type(err).__name__ + ': ' + str(err)
    except Exception as err:
        row['exception'] = type(err).__name__ + ': ' + str(err)
    rows.append(row)
    return row

raws = {}
for token in ['NaN', 'Infinity', '-Infinity', '1e309', '-1e309', '1.7976931348623159e308', '-1.7976931348623159e308',
              '1.7976931348623157e308', '1e308', '-1e308', '1e-400', '-1e-400', '-0.0', '0.0', '1.0',
              '1e999999999999999999999', '1e-999999999999999999999']:
    raw = json.dumps({'claims': [dict(GOOD, action='TOKEN')]}).replace('"TOKEN"', token)
    raws[token] = raw
    capture('raw_action:' + token, raw, lambda raw=raw: kg.verify_structured(raw, ev))

for name, value in [('nan', float('nan')), ('inf', float('inf')), ('negative_inf', -float('inf'))]:
    for field in ['action', 'kind', 'subject', 'evidence', 'note']:
        payload = {'claims': [dict(GOOD, **{field: value})]}
        capture('parsed_nonfinite:' + field + ':' + name,
                json.dumps(payload), lambda payload=payload: kg.verify_structured(payload, ev))

deep = {'leaf': float('inf')}
for _ in range(100):
    deep = {'child': [deep]}
payload = {'claims': [dict(GOOD, note=deep)]}
capture('sanitiser:depth100', 'claims=[GOOD + note={child:[...]} depth 100, leaf=inf]', lambda: kg.verify_structured(payload, ev))
cycle = []
cycle.append(cycle)
payload_cycle = {'claims': [dict(GOOD, note=cycle)]}
capture('sanitiser:cycle', 'Python pre-parsed non-JSON cyclic list in note', lambda: kg.verify_structured(payload_cycle, ev))
payload = {'claims': [dict(GOOD, note={str(i): [float('nan'), MARK * 100] for i in range(100)})]}
capture('sanitiser:breadth100_strings', '100 note keys, each [NaN, MARK * 100]', lambda: kg.verify_structured(payload, ev))
payload = {'claims': [dict(GOOD, note=10**5000)]}
capture('sanitiser:parsed_5001_digit_int', 'Python pre-parsed note=10**5000 (bypasses Python JSON integer-string limit)', lambda: kg.verify_structured(payload, ev))
raw_big_int = json.dumps({'claims': [dict(GOOD, note='TOKEN')]}).replace('"TOKEN"', '1' + '0'*5000)
capture('sanitiser:raw_5001_digit_int', raw_big_int, lambda: kg.verify_structured(raw_big_int, ev))

attack_raws = {}
for field in ['kind', 'relation', 'subject', 'object', 'action', 'evidence', 'note']:
    raw = json.dumps({'claims': [dict(GOOD, **{field: MARK})]})
    attack_raws[field] = raw
    capture('injection:' + field, raw, lambda raw=raw: kg.verify_structured(raw, ev))
raw = json.dumps({'claims': [dict(GOOD, **{MARK: MARK})]})
attack_raws['key'] = raw
capture('injection:key', raw, lambda: kg.verify_structured(raw, ev))
raw = json.dumps({'claims': [GOOD, dict(GOOD, note=MARK), GOOD]})
attack_raws['mixed'] = raw
capture('injection:mixed', raw, lambda: kg.verify_structured(raw, ev))
raw = json.dumps({'claims': [dict(GOOD, subject='\ud800')]})
attack_raws['surrogate'] = raw
capture('injection:surrogate', raw, lambda: kg.verify_structured(raw, ev))

state = {}
calls = []
class Messages:
    def create(self, **kw):
        calls.append(kw)
        if state.get('create_error'):
            raise state['create_error'](state.get('error_message', 'SENSITIVE_MODEL_OR_CREDENTIAL_TEXT ' + MARK))
        return state.get('message', types.SimpleNamespace(content=[types.SimpleNamespace(text='{"claims":[]}')]))
class Anthropic:
    def __init__(self):
        if state.get('init_error'):
            raise state['init_error']('SENSITIVE_MODEL_OR_CREDENTIAL_TEXT ' + MARK)
        self.messages = Messages()

with patch.dict(sys.modules, {'anthropic': None}):
    capture('model:missing_sdk', 'sys.modules[anthropic]=None; use_llm=True', lambda: kg.answer(Q, use_llm=True).to_dict())
with patch.dict(sys.modules, {'anthropic': types.SimpleNamespace(Anthropic=Anthropic)}):
    state.clear(); state.update(create_error=RuntimeError, error_message='simulated SDK failure')
    capture('legacy_exact:sdk_failure', "messages.create raises RuntimeError('simulated SDK failure')", lambda: kg.answer(Q, use_llm=True).to_dict())
    for stage in ['init_error', 'create_error']:
        for typ in [RuntimeError, ValueError, ConnectionError, TimeoutError]:
            state.clear(); state[stage] = typ
            capture('model:' + stage + ':' + typ.__name__, stage + '=' + typ.__name__ + '(SENSITIVE... MARK)', lambda: kg.answer(Q, use_llm=True).to_dict())
    for name, msg in [
        ('empty', types.SimpleNamespace(content=[])),
        ('none', types.SimpleNamespace(content=None)),
        ('tool', types.SimpleNamespace(content=[types.SimpleNamespace(type='tool_use')])),
        ('null_text', types.SimpleNamespace(content=[types.SimpleNamespace(text=None)])),
        ('numeric_text', types.SimpleNamespace(content=[types.SimpleNamespace(text=42)])),
        ('missing_content', types.SimpleNamespace()),
        ('none_message', None),
        ('tool_then_good', types.SimpleNamespace(content=[types.SimpleNamespace(type='tool_use'), types.SimpleNamespace(text=json.dumps({'claims':[GOOD]}))])),
        ('whitespace_then_good', types.SimpleNamespace(content=[types.SimpleNamespace(text=' '), types.SimpleNamespace(text=json.dumps({'claims':[GOOD]}))])),
        ('empty_then_good', types.SimpleNamespace(content=[types.SimpleNamespace(text=''), types.SimpleNamespace(text=json.dumps({'claims':[GOOD]}))]))]:
        state.clear(); state['message'] = msg
        capture('model:shape:' + name, repr(msg), lambda: kg.answer(Q, use_llm=True).to_dict())
    state.clear(); state['message'] = types.SimpleNamespace(content=[types.SimpleNamespace(text=raws['1e309'])])
    capture('model:overflow', raws['1e309'], lambda: kg.answer(Q, use_llm=True).to_dict())

engine = app.Engine()
engine.kg.conn.execute('PRAGMA query_only=ON')
server = ThreadingHTTPServer(('127.0.0.1', 0), app.make_handler(engine))
worker = threading.Thread(target=server.serve_forever, daemon=True)
worker.start()
try:
    for name, raw in list(raws.items()) + list(attack_raws.items()):
        request = json.dumps({'text': Q, 'answer': raw})
        req = urllib.request.Request(f'http://127.0.0.1:{server.server_port}/api/structured', data=request.encode(), headers={'Content-Type': 'application/json'})
        try:
            with urllib.request.urlopen(req, timeout=10) as response:
                status, body = response.status, response.read().decode()
        except urllib.error.HTTPError as err:
            status, body = err.code, err.read().decode()
        parsed = json.loads(body, parse_constant=lambda val: (_ for _ in ()).throw(ValueError(val)))
        api.append({'case': name, 'request': request, 'http_status': status, 'response_raw': body, 'strict_json': True})
finally:
    server.shutdown(); server.server_close(); worker.join()
    engine.kg.conn.close(); kg.conn.close()

(OUT / 'modelui_new_results.json').write_text(json.dumps(rows, indent=2, ensure_ascii=True, allow_nan=False), encoding='utf-8')
(OUT / 'modelui_new_api_fixtures.json').write_text(json.dumps(api, indent=2, ensure_ascii=True, allow_nan=False), encoding='utf-8')
for row in rows:
    r = row.get('result', {})
    print(row['case'], 'exception=', row.get('exception'), 'strict=', row.get('strict_json_serializable'),
          'verified=', r.get('verified'), 'checks=', r.get('checks', {}).get('applicable'),
          'accepted=', len(r.get('accepted', [])), 'text=', r.get('text', r.get('answer', ''))[:90])
print('api_count', len(api), 'all_strict', all(x['strict_json'] for x in api))
