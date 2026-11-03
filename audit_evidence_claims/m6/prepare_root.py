"""Copy prior audit entrypoints; only output plumbing changes, all writes in m6."""
import hashlib, json, os, subprocess, sys
from pathlib import Path
OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[1]
names = ['run_verification.py','run_http.py','regression_http.py','supplemental_http.py',
         'attack_http.py','m5_http.py','cross_item_http.py','perf_check_http.py','perf_probe.py']
manifest = []
for name in names:
    source = ROOT/'audit_evidence_claims/m5'/name
    original = source.read_text(encoding='utf8')
    adapted = original.replace('8880','8886')
    if name == 'run_http.py':
        adapted = adapted.replace('replace("bfcb83d", "514929c")','replace("bfcb83d", "b7a00f9")')
    (OUT/name).write_text(adapted,encoding='utf8')
    manifest.append({'source':str(source.relative_to(ROOT)), 'copy':str((OUT/name).relative_to(ROOT)),
                     'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
                     'changes':'port 8880->8886; HTTP audit commit annotation updated where present'})
(OUT/'root_reuse_manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf8')
tracked = subprocess.check_output(['git','ls-files','-z'],cwd=ROOT).decode('utf8').split('\0')
hashes = {p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in tracked if p and (ROOT/p).is_file()}
(OUT/'tracked_before.json').write_text(json.dumps({'head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT).decode().strip(),'hashes':hashes},indent=2),encoding='utf8')
print(json.dumps({'copied':len(names),'tracked_hashed':len(hashes)}))
