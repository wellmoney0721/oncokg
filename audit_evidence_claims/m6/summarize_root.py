import json
from pathlib import Path
OUT=Path(__file__).resolve().parent
def read(name):return json.loads((OUT/name).read_text(encoding='utf8'))
perf=read('perf_http.json')
check=read('perf_check_http.json')
summ={'http_replays':read('root_replay_execution.json'),
      'performance':{'sequential':[{k:r[k] for k in ['path','characters','status','seconds']} for r in perf['sequential']],
                     'concurrent_wall_seconds':perf['concurrent_wall_seconds'],
                     'concurrent_seconds':[r['seconds'] for r in perf['concurrent']],
                     'normal_follower_seconds':perf['normal_behind_slow']['follower']['seconds'],
                     'check_999_chars':{k:check['slow_check_999_characters'][k] for k in ['status','seconds']},
                     'extended':[{k:r[k] for k in ['kind','status','seconds']} for r in read('perf_extended_http.json')]},
      'demos':[{'question':r['question'],'status':r['http_status'],'evidence':len(r['current'].get('evidence',[])),
                'same_as_original':r['identical_to_bfcb83d']} for r in read('http_demo_results.json')['answers']]}
h=read('http_results.json')
summ['http_top_keys']=list(h)
(OUT/'root_summary.json').write_text(json.dumps(summ,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(summ,ensure_ascii=False,indent=2))
