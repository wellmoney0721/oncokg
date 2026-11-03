from pathlib import Path
import json, sys, sqlite3
sys.path.insert(0,str(Path('src').resolve()))
from app import Engine
out=Path('audit_evidence_claims/m7/db_ui')
inputs=json.loads((out/'ui_demos_inputs.json').read_text(encoding='utf-8'))
e=Engine()
e.kg.conn.close()
e.kg.conn=sqlite3.connect('file:data/processed/oncokg.sqlite?mode=ro',uri=True)
e.kg.conn.row_factory=sqlite3.Row
results=[]
for kind, tests in inputs.items():
    for i,t in enumerate(tests):
        req={'text':t[0] if kind=='EX1' else t if kind=='EX2' else t[1]}
        if kind in ('EX3','EX4'):
            req['answer']=json.dumps(t[2]) if kind=='EX4' else t[2]
        rec={'kind':kind,'index':i,'request':req}
        try:
            rec['response']=(e.resolve(req['text']) if kind=='EX1' else e.ask(req['text']) if kind=='EX2' else e.check(req['text'],req['answer']) if kind=='EX3' else e.structured(req['text'],req['answer']))
        except Exception as ex:
            rec['error']=str(ex)
        results.append(rec)
(out/'ui_demos_responses.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')
e.kg.conn.close()
print(json.dumps({'total':len(results),'engine_errors':[r for r in results if 'error' in r]}))
