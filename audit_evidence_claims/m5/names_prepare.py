"""Reuse prior name probes; adapt output directory and HTTP helpers only."""
from pathlib import Path
import os, subprocess, sys, json, time
OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[1]
names = ['names_reproduction.py', 'names_regressions.py', 'names_boundary_details.py',
         'names_label_scan.py', 'names_attack.py', 'names_new_boundaries.py',
         'names_final_checks.py', 'names_separator_checks.py', 'qa_relink_sweep.py']
for name in names:
    text = (ROOT / 'audit_evidence_claims/m4' / name).read_text(encoding='utf-8')
    text = text.replace('audit_evidence_claims/m4', 'audit_evidence_claims/m5')
    if name == 'names_reproduction.py':
        start, end = text.index('servers=[]'), text.index('def map_summary')
        text = text[:start] + '''servers=[]
def post(index,path,text):
    text=text.strip()
    if len(text)>500:return {'status':400,'body':{'error':'input is longer than 500 characters'}}
    e=[E,old][index]
    return {'status':200,'body':getattr(e,path)(text)}

''' + text[end:]
    if name == 'names_regressions.py':
        start,end=text.index('servers=[]'),text.index('inputs=')
        text=text[:start]+'''servers=[]
def post(i,path,text):
    e=[E,old][i]
    b=getattr(e,path)(text.strip())
    if path=='explore':b={k:v for k,v in b.items() if k!='groups'}
    return {'status':200,'body':b}
''' +text[end:]
    # Consistent name prefix and no HTTP claim for direct replays.
    if name == 'qa_relink_sweep.py':
        text=text.replace("'qa_relink_sweep.json'", "'names_qa_relink_sweep.json'")
    dest='names_qa_relink_sweep.py' if name=='qa_relink_sweep.py' else name
    (OUT/dest).write_text(text,encoding='utf-8')
demo=(ROOT/'audit_evidence_claims/m2b/names_demo_compare.py').read_text(encoding='utf-8')
(OUT/'names_demo_compare.py').write_text(demo.replace('audit_evidence_claims/m2b','audit_evidence_claims/m5'),encoding='utf-8')
records=[]
for name in [*names, 'names_demo_compare.py']:
    dest='names_qa_relink_sweep.py' if name=='qa_relink_sweep.py' else name
    st=time.perf_counter()
    with (OUT/(dest[:-3]+'_stdout.txt')).open('wb') as fh:
        run=subprocess.run([sys.executable,'-B',str(OUT/dest)],cwd=ROOT,stdout=fh,stderr=subprocess.STDOUT,
                           env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1','PYTHONUTF8':'1','PYTHONIOENCODING':'utf-8'})
    row={'script':dest,'exit_code':run.returncode,'seconds':round(time.perf_counter()-st,3)}
    records.append(row)
    print(json.dumps(row),flush=True)
    (OUT/'names_replay_execution.json').write_text(json.dumps(records,indent=2),encoding='utf-8')
