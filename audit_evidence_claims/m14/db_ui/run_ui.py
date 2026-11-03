from pathlib import Path
import os,subprocess,sys,json,time
out=Path(__file__).resolve().parent
env={**os.environ,'PYTHONIOENCODING':'utf-8','PYTHONDONTWRITEBYTECODE':'1','TEMP':str(out/'tmp'),'TMP':str(out/'tmp'),'TMPDIR':str(out/'tmp')}
commands=[[sys.executable,'-B',str(out/'ui_collect.py')],['node',str(out/'ui_harness.js')],['node',str(out/'ui_regressions.js')],['node',str(out/'ui_demos.js'),'export'],[sys.executable,'-B',str(out/'ui_demos_collect.py')],['node',str(out/'ui_demos.js')],['node',str(out/'ui_m3_checks.js')],[sys.executable,'-B',str(out/'ui_demo_compare.py')]]
rows=[]
for i,c in enumerate(commands):
 t=time.perf_counter(); p=subprocess.run(c,env=env,capture_output=True,text=True,encoding='utf8',timeout=90); log=out/f'run_{i}.txt';log.write_text(p.stdout+p.stderr,encoding='utf8');rows.append({'command':c,'exit':p.returncode,'seconds':time.perf_counter()-t,'log':str(log)});print(c[-1],p.returncode,p.stdout[-500:],flush=True)
 if p.returncode:break
(out/'execution_ui_complete.json').write_text(json.dumps(rows,indent=2),encoding='utf8')
