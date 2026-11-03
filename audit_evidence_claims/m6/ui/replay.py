from pathlib import Path
import hashlib,json,subprocess,os,sys,time
OUT=Path('audit_evidence_claims/m6/ui')
SOURCE=Path('audit_evidence_claims/m5')
FILES=['ui_collect.py','ui_harness.js','ui_regressions.js','ui_missing_sponsor_count.js','ui_demos.js','ui_demos_collect.py','ui_m3_checks.js','ui_demo_compare.py','ui_assertions.py']
manifest=[]
for name in FILES:
    old=(SOURCE/name).read_text(encoding='utf8')
    new=old.replace('audit_evidence_claims/m5','audit_evidence_claims/m6/ui')
    edits=['output paths m5 to m6/ui']
    if name=='ui_missing_sponsor_count.js':
        new=new.replace("OUT+'db_missing_sponsor_count.json'","'audit_evidence_claims/m6/db/db_missing_sponsor_count.json'")
        edits.append('fresh fixture read path m6/db')
    if name=='ui_demo_compare.py':
        new=new.replace("OUT.parent / 'm4/ui_demos_responses.json'","Path('audit_evidence_claims/m5/ui_demos_responses.json')")
        edits.append('comparison baseline m5')
    if name=='ui_assertions.py':
        new=new.replace("http = load('http_results.json')","http = json.loads(Path('audit_evidence_claims/m6/http_results.json').read_text(encoding='utf-8'))")
        new=new.replace("(out/'served_try.html')","Path('audit_evidence_claims/m6/served_try.html')")
        edits.append('root fresh HTTP artifact paths')
    (OUT/name).write_text(new,encoding='utf8')
    manifest.append({'file':name,'source':str(SOURCE/name),'source_sha256':hashlib.sha256(old.encode()).hexdigest(),'adapted_sha256':hashlib.sha256(new.encode()).hexdigest(),'adaptations':edits})
(OUT/'adaptation_manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf8')
env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONIOENCODING='utf-8')
commands=[['python','-B',str(OUT/'ui_collect.py')],['node',str(OUT/'ui_harness.js')],['node',str(OUT/'ui_regressions.js')],['node',str(OUT/'ui_demos.js'),'export'],['python','-B',str(OUT/'ui_demos_collect.py')],['node',str(OUT/'ui_demos.js')],['node',str(OUT/'ui_m3_checks.js')],['python','-B',str(OUT/'ui_demo_compare.py')]]
runs=[]
for command in commands:
    start=time.perf_counter()
    p=subprocess.run(command,env=env,capture_output=True,encoding='utf8')
    name=Path(command[2] if command[0]=='python' else command[1]).name+('_export' if command[-1]=='export' else '')
    (OUT/(name+'.stdout.txt')).write_text(p.stdout,encoding='utf8')
    (OUT/(name+'.stderr.txt')).write_text(p.stderr,encoding='utf8')
    r={'command':command,'exit_code':p.returncode,'seconds':round(time.perf_counter()-start,4)}
    runs.append(r)
    print(json.dumps(r),flush=True)
    if p.returncode: print(p.stderr,flush=True); break
(OUT/'execution_manifest.json').write_text(json.dumps(runs,indent=2),encoding='utf8')
