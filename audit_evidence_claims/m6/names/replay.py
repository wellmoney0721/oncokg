"""Reuse M1-M5 scripts against current source; redirect scratch destinations only."""
import hashlib,json,os,subprocess,sys,time
from pathlib import Path
ROOT=Path.cwd()
OUT=ROOT/'audit_evidence_claims/m6/names'
SCRIPTS=['names_reproduction.py','names_regressions.py','names_boundary_details.py',
 'names_label_scan.py','names_attack.py','names_new_boundaries.py','names_final_checks.py',
 'names_separator_checks.py','names_qa_relink_sweep.py','names_demo_compare.py',
 'names_m5_attack.py','names_m5_confirm.py','names_cross_item_refusal.py']
records=[]
for name in SCRIPTS:
    source=ROOT/'audit_evidence_claims/m5'/name
    body=source.read_text(encoding='utf8').replace('audit_evidence_claims/m5','audit_evidence_claims/m6/names')
    destination=OUT/name
    destination.write_text(body,encoding='utf8')
    started=time.perf_counter()
    with (OUT/(name[:-3]+'_stdout.txt')).open('wb') as fh:
        p=subprocess.run([sys.executable,'-B',str(destination)],cwd=ROOT,stdout=fh,stderr=subprocess.STDOUT,
            env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1','PYTHONUTF8':'1','PYTHONIOENCODING':'utf-8'},timeout=150)
    row={'original':str(source.relative_to(ROOT)),'script':name,'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
         'adaptation':'only m5 scratch paths redirected to m6/names; original direct-Engine plumbing retained',
         'exit_code':p.returncode,'seconds':round(time.perf_counter()-started,3)}
    records.append(row)
    (OUT/'replay_manifest.json').write_text(json.dumps(records,indent=2),encoding='utf8')
    print(json.dumps(row),flush=True)
