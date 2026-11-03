"""Exercise all current page-demo payloads against the original CLI HTTP server."""
import json,os,socket,subprocess,sys,time,urllib.request,urllib.error
from pathlib import Path
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
PORT=8951
URL=f"http://127.0.0.1:{PORT}"
env=dict(os.environ,PYTHONDONTWRITEBYTECODE="1",PYTHONIOENCODING="utf-8",TEMP=str((OUT/"tmp").resolve()),TMP=str((OUT/"tmp").resolve()))
s=socket.socket();s.bind(("127.0.0.1",PORT));s.close()
log=(OUT/"demo_http_server.txt").open("w",encoding="utf-8")
proc=subprocess.Popen([sys.executable,"-B","-u","src/app.py",str(PORT)],cwd=ROOT,env=env,stdout=log,stderr=subprocess.STDOUT,creationflags=getattr(subprocess,"CREATE_NO_WINDOW",0))
rows=[];lifecycle={"pid":proc.pid,"port":PORT,"started_by_this_script":True}
try:
 for _ in range(200):
  if proc.poll() is not None:raise RuntimeError("owned CLI exited on startup")
  try:
   with urllib.request.urlopen(URL+"/",timeout=1) as r:served=r.read()
   if proc.poll() is not None:raise RuntimeError("owned CLI exited after GET")
   break
  except (OSError,urllib.error.URLError):time.sleep(.1)
 else:raise RuntimeError("owned CLI not ready")
 (OUT/"demo_http_served_try.html").write_bytes(served)
 inputs=json.loads((OUT/"ui_demos_responses.json").read_text(encoding="utf-8"))
 paths={"EX1":"resolve","EX2":"ask","EX3":"check","EX4":"structured"}
 for rec in inputs:
  start=time.perf_counter();request=urllib.request.Request(URL+"/api/"+paths[rec["kind"]],json.dumps(rec["request"]).encode(),{"Content-Type":"application/json"})
  try:
   with urllib.request.urlopen(request,timeout=20) as r:status=r.status;body=json.load(r)
  except urllib.error.HTTPError as e:status=e.code;body=json.load(e)
  rows.append({"kind":rec["kind"],"index":rec["index"],"input":rec["request"],"status":status,"seconds":time.perf_counter()-start,"equals_direct_engine":body==rec.get("response"),"body":body})
 result={"total":len(rows),"http_200":sum(r["status"]==200 for r in rows),"equal":sum(r["equals_direct_engine"] for r in rows),"served_equals_worktree":served==(ROOT/"web/try.html").read_bytes(),"rows":rows}
 (OUT/"demo_http.json").write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8")
 print(json.dumps({k:v for k,v in result.items() if k!="rows"}))
finally:
 proc.terminate()
 try:proc.wait(timeout=10)
 except subprocess.TimeoutExpired:proc.kill();proc.wait(timeout=10)
 log.close();lifecycle["closed"]=proc.poll() is not None;lifecycle["returncode"]=proc.returncode
 (OUT/"demo_http_lifecycle.json").write_text(json.dumps(lifecycle,indent=2),encoding="utf-8")
