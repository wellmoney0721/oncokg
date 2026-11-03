from pathlib import Path
import json,subprocess,os,time
out=Path('audit_evidence_claims/m6/ui')
source=Path('audit_evidence_claims/m5/ui_boundary_probe.py')
text=source.read_text(encoding='utf8').replace('ROOT = OUT.parents[1]', 'ROOT = Path.cwd()')
(out/'ui_boundary_probe.py').write_text(text,encoding='utf8')
commands=[['node',str(out/'ui_missing_sponsor_count.js')],['python','-B',str(out/'ui_boundary_probe.py')]]
runs=json.loads((out/'execution_manifest.json').read_text(encoding='utf8'))
for cmd in commands:
    start=time.perf_counter(); p=subprocess.run(cmd,capture_output=True,encoding='utf8',env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONIOENCODING='utf-8'))
    name=Path(cmd[2] if cmd[0]=='python' else cmd[1]).name
    (out/(name+'.stdout.txt')).write_text(p.stdout,encoding='utf8'); (out/(name+'.stderr.txt')).write_text(p.stderr,encoding='utf8')
    row={'command':cmd,'exit_code':p.returncode,'seconds':round(time.perf_counter()-start,4)};runs.append(row);print(json.dumps(row))
    if p.returncode: print(p.stderr)
(out/'execution_manifest.json').write_text(json.dumps(runs,indent=2),encoding='utf8')
