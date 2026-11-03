"""Stage prior DB/UI reproduction scripts without copying old evidence."""
from pathlib import Path
import hashlib,json
root=Path(__file__).resolve().parents[2]
src=root/'audit_evidence_claims/m14/db_ui'
out=Path(__file__).resolve().parent/'db_ui'
out.mkdir(exist_ok=True)
(out/'tmp').mkdir(exist_ok=True)
rows=[]
for p in src.iterdir():
    if p.suffix not in ('.py','.js'): continue
    original=p.read_text(encoding='utf8')
    adapted=original.replace('audit_evidence_claims/m14/db_ui','audit_evidence_claims/m15/db_ui').replace('PORT=8931','PORT=8951')
    target=out/p.name
    if target.exists(): raise RuntimeError(f'refusing overwrite {target}')
    target.write_text(adapted,encoding='utf8')
    rows.append(dict(source=str(p.relative_to(root)),destination=str(target.relative_to(root)),source_sha256=hashlib.sha256(p.read_bytes()).hexdigest(),adapted_sha256=hashlib.sha256(target.read_bytes()).hexdigest(),adaptations=['m15 output path','owned CLI port 8951'] if adapted!=original else []))
(out/'reuse_manifest.json').write_text(json.dumps(rows,indent=2),encoding='utf8')
print(json.dumps({'scripts_staged':len(rows)}))
