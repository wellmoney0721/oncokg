"""Round 2 model/API checks. All disk writes stay beside this file."""
import json
import math
import sys
import threading
import types
import urllib.request
import urllib.error
from pathlib import Path
from http.server import ThreadingHTTPServer
from unittest.mock import patch

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
sys.path.insert(0, str(ROOT / 'src'))
import query
import app
from structured import Verifier

Q = 'What does osimertinib target?'
EDGE = 'CHEMBL3353410|ACTS_ON|ENSG00000146648|CHEMBL3353410'
GOOD = dict(kind='relation', relation='ACTS_ON', subject='osimertinib', object='EGFR', evidence=EDGE, action='INHIBITOR')
kg = query.OncoKG()
kg.conn.execute('PRAGMA query_only=ON')
entities = kg.link_entities(Q)
ev = kg.retrieve(kg.classify(Q, entities), entities)
rows = []

def portable(value):
    if isinstance(value, float) and not math.isfinite(value):
        return '<Python ' + repr(value) + '>'
    if isinstance(value, dict):
        return {str(k): portable(v) for k, v in value.items()}
    if isinstance(value, list):
        return [portable(v) for v in value]
    return value

def capture(name, inp, fn):
    row = dict(case=name, input=inp)
    try:
        value = fn()
        try:
            json.dumps(value, allow_nan=False)
            row['strict_json_serializable'] = True
        except Exception as err:
            row['strict_json_serializable'] = False
            row['serialize_exception'] = type(err).__name__ + ': ' + str(err)
        row['result'] = portable(value)
    except Exception as err:
        row['exception'] = type(err).__name__ + ': ' + str(err)
    rows.append(row)

raws = {}
for token in ['NaN', 'Infinity', '-Infinity', '1e309', '-1e309']:
    bad = json.dumps(dict(GOOD, action='TOKEN')).replace('"TOKEN"', token)
    raw = '{"claims":[' + bad + ']}'
    raws[token] = raw
    capture('raw_nonfinite:' + token, raw, lambda raw=raw: kg.verify_structured(raw, ev))
for value in [float('nan'), float('inf'), -float('inf')]:
    payload = {'claims': [dict(GOOD, action=value)]}
    capture('parsed_nonfinite:' + repr(value), portable(payload), lambda payload=payload: kg.verify_structured(payload, ev))

for tag, bad in [('lone_surrogate', dict(GOOD, subject='\ud800')),
                 ('mixed_keys', dict(GOOD, **{'extra': 'x'}))]:
    if tag == 'mixed_keys': bad[42] = 'x'
    payload = {'claims': [GOOD, bad, GOOD]}
    capture('per_claim:' + tag, portable(payload), lambda payload=payload: kg.verify_structured(payload, ev))

original_check = Verifier.check
def failing_check(self, claim, retrieved):
    if isinstance(claim, dict) and claim.get('kind') == 'FAULT':
        raise RuntimeError('MODEL_TEXT_SHOULD_NOT_LEAK')
    return original_check(self, claim, retrieved)
payload = {'claims': [GOOD, {'kind': 'FAULT'}, GOOD]}
with patch.object(Verifier, 'check', failing_check):
    capture('per_claim:injected_runtime_error', payload, lambda: kg.verify_structured(payload, ev))

response = {}
class Messages:
    def create(self, **kwargs):
        return types.SimpleNamespace(content=response.get('content'))
class Anthropic:
    def __init__(self): self.messages = Messages()

with patch.dict(sys.modules, {'anthropic': types.SimpleNamespace(Anthropic=Anthropic)}):
    for name, raw in [('empty_claims', '{"claims":[]}'), *raws.items()]:
        response['content'] = [types.SimpleNamespace(text=raw)]
        capture('model:' + name, raw, lambda: kg.answer(Q, use_llm=True).to_dict())
    for name, content in [
            ('none_content', None),
            ('tool_then_text', [types.SimpleNamespace(type='tool_use'), types.SimpleNamespace(text=json.dumps({'claims':[GOOD]}))]),
            ('text_number', [types.SimpleNamespace(text=42)]),
            ('whitespace_then_valid', [types.SimpleNamespace(text=' '), types.SimpleNamespace(text=json.dumps({'claims':[GOOD]}))])]:
        response['content'] = content
        capture('sdk_shape:' + name, repr(content), lambda: kg.answer(Q, use_llm=True).to_dict())
    depth_results = []
    for depth in range(950, 1005):
        raw = '{"claims":[{"kind":' + '[' * depth + '0' + ']' * depth + '}]}'
        response['content'] = [types.SimpleNamespace(text=raw)]
        try:
            a = kg.answer(Q, use_llm=True).to_dict()
            depth_results.append({'depth': depth, 'accepted': a['checks']['accepted'], 'rejected': len(a['checks']['rejected'])})
        except Exception as err:
            depth_results.append({'depth':depth, 'exception':type(err).__name__ + ': ' + str(err)})
    rows.append({'case':'near_limit_nesting', 'input_template':'{"claims":[{"kind":' + "'['*depth+'0'+']'*depth" + ' }]}', 'result':depth_results})

engine = app.Engine()
engine.kg.conn.execute('PRAGMA query_only=ON')
server = ThreadingHTTPServer(('127.0.0.1', 0), app.make_handler(engine))
worker = threading.Thread(target=server.serve_forever, daemon=True)
worker.start()
api = []
try:
    for tag, raw in [*raws.items(), ('empty', '{"claims":[]}'), ('lone_surrogate', json.dumps({'claims':[dict(GOOD,subject='\ud800')]}))]:
        request = json.dumps({'text':Q, 'answer':raw})
        req = urllib.request.Request(f'http://127.0.0.1:{server.server_port}/api/structured', data=request.encode(), headers={'Content-Type':'application/json'})
        try:
            with urllib.request.urlopen(req, timeout=10) as r:
                status, body = r.status, r.read().decode()
        except urllib.error.HTTPError as err:
            status, body = err.code, err.read().decode()
        api.append({'case':tag,'request':request,'http_status':status,'response_raw':body})
finally:
    server.shutdown(); server.server_close(); worker.join()
    engine.kg.conn.close(); kg.conn.close()

(OUT/'modelui_attack_results.json').write_text(json.dumps(rows, indent=2, ensure_ascii=True, allow_nan=False), encoding='utf-8')
(OUT/'modelui_attack_api_fixtures.json').write_text(json.dumps(api, indent=2, ensure_ascii=True, allow_nan=False), encoding='utf-8')
for row in rows:
    r = row.get('result', {})
    if isinstance(r, dict):
        print(row['case'], 'exception=',row.get('exception'), 'strict=', row.get('strict_json_serializable'), 'verified=', r.get('verified'), 'text=', r.get('text',r.get('answer',''))[:100])
    elif row['case']=='near_limit_nesting':
        print(row['case'], [x for x in r if 'exception' in x])
for row in api:
    print('API',row['case'],row['http_status'],row['response_raw'][:150])
