"""Cold/warm measurements and exact resolver-call counts for repeated/unique legal input."""
from pathlib import Path
import json,sys,time,statistics
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2];sys.path.insert(0,str(ROOT/'src'))
from app import Engine
import normalize as N
original=N.resolve_drug_string
counter={'count':0}
def counted(*args,**kwargs):counter['count']+=1;return original(*args,**kwargs)
N.resolve_drug_string=counted
rows=[]
for name,text in [('repeat_unknown_250',';'.join(['x']*250)),('unique_unknown_400',';'.join(f'x{i:04d}' for i in range(400))),('repeat_drug_400',';'.join(['isa x0000']*400)),('unique_drug_50',';'.join(f'isa x{i:04d}' for i in range(50))),('unique_drug_400',';'.join(f'isa x{i:04d}' for i in range(400)))]:
 e=Engine();e.kg.conn.execute('pragma query_only=on');samples=[]
 for i in range(3):
  before=counter['count'];t=time.perf_counter();result=e.kg.link_entities(text);samples.append({'seconds':time.perf_counter()-t,'resolver_calls':counter['count']-before,'entities':len(result),'cache_size':len(e.kg._resolve_cache)})
 e.kg.conn.close();e=Engine();e.kg.conn.execute('pragma query_only=on');before=counter['count'];t=time.perf_counter();r=e.check('EGFR',text);check={'seconds':time.perf_counter()-t,'resolver_calls':counter['count']-before,'evidence_count':r['evidence_count']};e.kg.conn.close()
 row={'name':name,'input':text,'characters':len(text),'link_samples':samples,'check_cold':check};rows.append(row);print(json.dumps({k:v for k,v in row.items() if k!='input'}),flush=True)
(OUT/('isolated_unique_piece_cost.json' if len(sys.argv)>1 and sys.argv[1]=='isolated' else 'unique_piece_cost.json')).write_text(json.dumps(rows,indent=2),encoding='utf8')
