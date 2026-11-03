"""End-to-end linker/check cost under HTTP's input and answer character caps."""
import json,statistics,sys,time
from pathlib import Path
OUT=Path(__file__).resolve().parent/'root_checks'
ROOT=OUT.parents[2]
sys.path.insert(0,str(ROOT/'src'))
from app import Engine
e=Engine();e.kg.conn.execute('PRAGMA query_only=ON')
cases=[('plain_'+str(n),' '.join(['x']*n)) for n in (250,500,1000,2000)]
cases += [('split_2000',';'.join(['x']*2000)),('many_matched',';'.join(['osimertinib']*333)),
          ('many_refused',';'.join(['Mvasi bevacizumab']*222)),
          ('many_joiners',' and '.join(['x']*666))]
rows=[]
for name,value in cases:
    times=[]
    for _ in range(3):
        start=time.perf_counter(); ents=e.kg.link_entities(value); times.append(time.perf_counter()-start)
    start=time.perf_counter(); result=e.check('EGFR',value); check=time.perf_counter()-start
    rows.append({'name':name,'text':value,'characters':len(value),'link_seconds':times,
                 'link_median_seconds':statistics.median(times),'check_seconds':check,
                 'entity_count':len(ents),'evidence_count':result['evidence_count']})
e.kg.conn.close()
(OUT/'cost_stress.json').write_text(json.dumps(rows,indent=2),encoding='utf8')
print(json.dumps([{k:v for k,v in r.items() if k not in ('text','link_seconds')} for r in rows],indent=2))
