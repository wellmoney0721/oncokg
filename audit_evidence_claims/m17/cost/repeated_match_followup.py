"""Bounded causal/cost follow-up for the changed repeated-match workload."""
from pathlib import Path
import json,os,subprocess,sys,time,types
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[2]
sys.path.insert(0,str(ROOT/'src'))
import query
rows=[]
for n in [125,1000]:
    kg=query.OncoKG();kg.conn.execute('PRAGMA query_only=ON')
    original=query._medical_isotope_in
    calls={'one_letter_false':0,'one_letter_true':0,'characters':0}
    def counted(key,one_letter=True):
        calls['one_letter_true' if one_letter else 'one_letter_false']+=1
        calls['characters']+=len(key)
        return original(key,one_letter)
    query._medical_isotope_in=counted
    try:
        value=' '.join(['isa']*n)
        start=time.perf_counter();entities=kg.link_entities(value);elapsed=time.perf_counter()-start
        rows.append(dict(matches=n,characters=len(value),helper_calls=calls,seconds_with_instrumentation=elapsed,entities=entities))
    finally:
        query._medical_isotope_in=original;kg.conn.close()
(OUT/'repeated_match_instrumentation.json').write_text(json.dumps(rows,indent=2),encoding='utf8')
source=OUT/'unique_cost_http.py'
code=source.read_text(encoding='utf8')
old="';'.join(f'isa x{i:04d}' for i in range(400))"
assert old in code
code=code.replace(old,"' '.join(['isa']*1000)")
code=code.replace('unique_cost','repeated_match_cost')
(OUT/'repeated_match_cost_http.py').write_text(code,encoding='utf8')
env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONUTF8='1',PYTHONIOENCODING='utf-8',
    TMP=str(OUT/'tmp'),TEMP=str(OUT/'tmp'),TMPDIR=str(OUT/'tmp'))
p=subprocess.run([sys.executable,'-B',str(OUT/'repeated_match_cost_http.py')],cwd=ROOT,env=env,capture_output=True,timeout=90)
(OUT/'repeated_match_cost_http.py.stdout.txt').write_bytes(p.stdout+p.stderr)
(OUT/'repeated_match_execution.json').write_text(json.dumps(dict(exit_code=p.returncode,
    source='audit_evidence_claims/m16/cost/unique_cost_http.py',
    changes=['exact answer replaced by 1000 space-separated isa tokens','unique_cost output prefix replaced by repeated_match_cost']),indent=2),encoding='utf8')
print(json.dumps(rows,indent=2));print(p.stdout.decode('utf8','replace'))
raise SystemExit(p.returncode)
