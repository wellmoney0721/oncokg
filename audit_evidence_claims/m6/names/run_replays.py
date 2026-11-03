from pathlib import Path
import subprocess,os,sys,json,time
out=Path(__file__).resolve().parent
names=['names_reproduction.py','names_regressions.py','names_boundary_details.py','names_label_scan.py','names_attack.py','names_new_boundaries.py','names_final_checks.py','names_separator_checks.py','names_qa_relink_sweep.py','names_demo_compare.py','names_cross_item_refusal.py','names_m5_attack.py','names_m5_confirm.py']
rows=[]
for name in names:
 start=time.perf_counter()
 with (out/(name[:-3]+'_stdout.txt')).open('wb') as fh:
  r=subprocess.run([sys.executable,'-B',str(out/name)],stdout=fh,stderr=subprocess.STDOUT,env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1','PYTHONUTF8':'1','PYTHONIOENCODING':'utf-8'},timeout=300)
 row={'script':name,'exit_code':r.returncode,'seconds':round(time.perf_counter()-start,3)}
 rows.append(row);print(json.dumps(row),flush=True)
 (out/'replay_execution.json').write_text(json.dumps(rows,indent=2),encoding='utf-8')
