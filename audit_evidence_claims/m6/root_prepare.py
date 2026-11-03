"""Root-owned replay copies, isolated from concurrently appearing root m6 artifacts."""
from pathlib import Path
import hashlib, json

OUT=Path(__file__).resolve().parent/'root_checks'
ROOT=OUT.parents[2]
OUT.mkdir(exist_ok=True)
(OUT/'tmp').mkdir(exist_ok=True)
names=['run_verification.py','run_http.py','http_audit.py','regression_http.py',
       'supplemental_http.py','attack_http.py','m5_http.py','cross_item_http.py',
       'perf_check_http.py','perf_probe.py']
manifest=[]
for name in names:
    p=ROOT/'audit_evidence_claims/m5'/name
    code=p.read_text(encoding='utf-8')
    code=code.replace('OUT.parents[1]','OUT.parents[2]').replace('8880','8896')
    if name=='run_http.py':
        code=code.replace('(OUT / "http_audit.py").write_text(adapted, encoding="utf-8")',
                          '(OUT / "http_audit.py").write_text(adapted.replace("OUT.parents[1]", "OUT.parents[2]"), encoding="utf-8")')
    (OUT/name).write_text(code,encoding='utf-8')
    manifest.append({'source':str(p.relative_to(ROOT)), 'copy':str((OUT/name).relative_to(ROOT)),
                     'source_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),
                     'adaptations':'root depth and port only; dynamic HTTP copy root depth'})
(OUT/'reuse_manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
print('Prepared',len(manifest),'copies')
