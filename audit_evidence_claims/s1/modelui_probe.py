"""Read-only model/API robustness probes for aa5655a; outputs confined to s1."""
import contextlib
import copy
import io
import json
import sys
import threading
import types
import urllib.error
import urllib.request
from pathlib import Path
from http.server import ThreadingHTTPServer

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'src'))
import query
import app

OUT = Path(__file__).resolve().parent
Q = 'What does osimertinib target?'
EDGE = 'CHEMBL3353410|ACTS_ON|ENSG00000146648|CHEMBL3353410'
GOOD = {'kind':'relation', 'relation':'ACTS_ON', 'subject':'osimertinib', 'object':'EGFR', 'evidence':EDGE, 'action':'INHIBITOR'}
MARK = '<img src=x onerror="globalThis.MODEL_INJECTED=1"><script>globalThis.MODEL_INJECTED=2</script>&"\''
kg = query.OncoKG()
kg.conn.execute('PRAGMA query_only=ON')
ent = kg.link_entities(Q)
ev = kg.retrieve(kg.classify(Q,ent),ent)

cases = []
payloads = {
 'faithful': json.dumps({'claims':[GOOD]}),
 'fenced': '```json\n'+json.dumps({'claims':[GOOD]})+'\n```',
 'prose_around_json': MARK+'\n'+json.dumps({'claims':[GOOD]})+'\n'+MARK,
 'two_json_objects': json.dumps({'claims':[GOOD]})+'\n'+json.dumps({'claims':[]}),
 'braces_in_prefix': '{garbage}\n'+json.dumps({'claims':[GOOD]}),
 'empty_string': '',
 'malformed_json': '{"claims": [',
 'empty_claims': '{"claims": []}',
 'not_json': MARK,
 'unknown_field_injection': json.dumps({'claims':[dict(GOOD,note=MARK)]}),
 'action_injection': json.dumps({'claims':[dict(GOOD,action=MARK)]}),
 'kind_list': '{"claims":[{"kind":[]}]}',
 'kind_object': '{"claims":[{"kind":{}}]}',
 'faithful_then_kind_list': json.dumps({'claims':[GOOD,{'kind':[]}]}),
 'relation_list': json.dumps({'claims':[dict(GOOD,relation=[])]}),
 'claims51': json.dumps({'claims':[GOOD]*51}),
 'claims50_then_injection': json.dumps({'claims':[GOOD]*50+[dict(GOOD,note=MARK)]}),
 'duplicate_action_bad_then_good': json.dumps({'claims':[GOOD]}).replace('"action": "INHIBITOR"','"action":"ACTIVATOR","action":"INHIBITOR"'),
 'duplicate_action_good_then_bad': json.dumps({'claims':[GOOD]}).replace('"action": "INHIBITOR"','"action":"INHIBITOR","action":"ACTIVATOR"'),
 'nan_action': json.dumps({'claims':[dict(GOOD,action=float('nan'))]}),
 'infinity_action': json.dumps({'claims':[dict(GOOD,action=float('inf'))]}),
 'nested1100': '{"claims":'+ '['*1100+'0'+']'*1100+'}',
 'nested20000': '{"claims":'+ '['*20000+'0'+']'*20000+'}',
 'oversized_unknown': json.dumps({'claims':[dict(GOOD,note=MARK*1500)]}),
}

calls = []
response = {}
class Messages:
 def create(self, **kwargs):
  calls.append(kwargs)
  if 'exception' in response: raise RuntimeError(response['exception'])
  return types.SimpleNamespace(content=response['content'])
class Anthropic:
 def __init__(self): self.messages=Messages()
original = sys.modules.get('anthropic')
sys.modules['anthropic'] = types.SimpleNamespace(Anthropic=Anthropic)
try:
 for name, raw in payloads.items():
  response.clear(); response['content']=[types.SimpleNamespace(text=raw)]
  row={'case':name,'question':Q,'raw_reply':raw}
  try:
   extracted,by=kg._llm_claims(Q,ev)
   row['extracted']=extracted
   a=kg.answer(Q,use_llm=True)
   row['result']=a.to_dict()
  except Exception as err:
   row['exception']={'type':type(err).__name__,'message':str(err)}
  cases.append(row)
 for name, content in [('no_content',[]),('non_text_block',[types.SimpleNamespace(type='tool_use')]),('null_text',[types.SimpleNamespace(text=None)])]:
  response.clear(); response['content']=content
  row={'case':name,'question':Q,'input_description':repr(content)}
  try: row['result']=kg.answer(Q,use_llm=True).to_dict()
  except Exception as err: row['exception']={'type':type(err).__name__,'message':str(err)}
  cases.append(row)
 response.clear(); response['exception']='simulated SDK failure'
 try: kg.answer(Q,use_llm=True)
 except Exception as err: cases.append({'case':'sdk_failure','exception':{'type':type(err).__name__,'message':str(err)}})
 sys.modules['anthropic']=None
 cases.append({'case':'missing_sdk','result':kg.answer(Q,use_llm=True).to_dict()})
finally:
 if original is None: sys.modules.pop('anthropic',None)
 else: sys.modules['anthropic']=original

engine=app.Engine()
engine.kg.conn.execute('PRAGMA query_only=ON')
server=ThreadingHTTPServer(('127.0.0.1',0),app.make_handler(engine))
worker=threading.Thread(target=server.serve_forever,daemon=True)
worker.start()
api=[]
try:
 for name in ['faithful','unknown_field_injection','action_injection','kind_list','relation_list','nested1100','claims51','oversized_unknown','nan_action','empty_claims']:
  body=json.dumps({'text':Q,'answer':payloads[name]}).encode('utf-8')
  req=urllib.request.Request(f'http://127.0.0.1:{server.server_port}/api/structured',data=body,headers={'Content-Type':'application/json'})
  try:
   with urllib.request.urlopen(req,timeout=10) as r: code,raw=r.status,r.read().decode('utf-8')
  except urllib.error.HTTPError as err:
   code=err.code
   try: raw=err.read().decode('utf-8')
   except Exception as neterr: raw=json.dumps({'network_read_error':type(neterr).__name__+': '+str(neterr)})
  except Exception as err: code=None;raw=json.dumps({'network_error':type(err).__name__+': '+str(err)})
  api.append({'case':name,'request_bytes':len(body),'request':body.decode('utf-8'),'http_status':code,'response_raw':raw,'result':json.loads(raw)})
finally:
 server.shutdown();server.server_close();worker.join()
 engine.kg.conn.close();kg.conn.close()

serialized=json.dumps({'model_cases':cases,'api_cases':api,'sdk_request':calls[0]},ensure_ascii=False)
portable=json.loads(serialized,parse_constant=lambda token:'<non-standard JSON token '+token+'>')
(OUT/'modelui_results.json').write_text(json.dumps(portable,indent=2,ensure_ascii=False,allow_nan=False),encoding='utf-8')
(OUT/'modelui_api_fixtures.json').write_text(json.dumps([{'case':row['case'],'http_status':row['http_status'],'request':row['request'],'response_raw':row['response_raw']} for row in api],indent=2,ensure_ascii=False),encoding='utf-8')
(OUT/'modelui_prompt.txt').write_text(calls[0]['messages'][0]['content'],encoding='utf-8')
for row in cases:
 result=row.get('result',{})
 checks=result.get('checks',{})
 print(row['case'],json.dumps(row.get('exception') or {'grounded':checks.get('grounded'),'accepted':checks.get('accepted'),'rejected':len(checks.get('rejected',[])),'answer_prefix':result.get('answer','')[:110]},ensure_ascii=True))
for row in api: print('API',row['case'],row['http_status'],str(row['result'].get('error','')))
