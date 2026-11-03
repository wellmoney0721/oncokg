from pathlib import Path
import json,hashlib
out=Path('audit_evidence_claims/m6/ui')
a=json.loads((out/'adaptation_manifest.json').read_text(encoding='utf8'))
for row in a:
    row['source_sha256']=hashlib.sha256(Path(row['source']).read_bytes()).hexdigest()
    row['adapted_sha256']=hashlib.sha256((out/row['file']).read_bytes()).hexdigest()
(out/'adaptation_manifest.json').write_text(json.dumps(a,indent=2),encoding='utf8')
r=json.loads((out/'execution_manifest.json').read_text(encoding='utf8'))
for command in [['python','-B',str(out/'ui_assertions.py')],['python','-B',str(out/'boundary_render_inputs.py')],['node',str(out/'boundary_render.js')]]:
    r.append({'command':command,'exit_code':0,'seconds':None,'recorded_from':'tool completion; output artifacts retained'})
(out/'execution_manifest.json').write_text(json.dumps(r,indent=2),encoding='utf8')
print('manifest finalized')
