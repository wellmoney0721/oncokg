from pathlib import Path
import subprocess,sys,os,json,time
out=Path(__file__).resolve().parent
env=dict(os.environ,PYTHONDONTWRITEBYTECODE="1",PYTHONIOENCODING="utf-8",TEMP=str((out/"tmp").resolve()),TMP=str((out/"tmp").resolve()))
commands=[[sys.executable,"-B",str(out/x)] for x in ("db_recheck.py","db_missing_sponsor_count.py","db_role_fallback.py","db_score_fixture.py","db_numeric_fixture.py","db_snapshot.py","db_assertions.py","ui_collect.py")]
commands += [["node",str(out/x),*args] for x,args in [("ui_harness.js",[]),("ui_regressions.js",[]),("ui_demos.js",["export"])]]
commands += [[sys.executable,"-B",str(out/"ui_demos_collect.py")]]
commands += [["node",str(out/x)] for x in ("ui_demos.js","ui_m3_checks.js","ui_missing_sponsor_count.js")]
commands += [[sys.executable,"-B",str(out/"ui_demo_compare.py")]]
rows=[]
for i,c in enumerate(commands):
 start=time.perf_counter();print("RUN",i,c[-1],flush=True)
 p=subprocess.run(c,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True,encoding="utf-8")
 name=Path(c[2] if c[1]=="-B" else c[1]).name
 log=out/(str(i)+"_"+name+".stdout.txt");log.write_text(p.stdout,encoding="utf-8")
 rows.append({"command":c,"returncode":p.returncode,"seconds":time.perf_counter()-start,"log":str(log)})
 (out/"execution.json").write_text(json.dumps(rows,indent=2),encoding="utf-8")
 print("DONE",i,p.returncode,round(rows[-1]["seconds"],3),p.stdout[-500:],flush=True)
 if p.returncode:sys.exit(p.returncode)
