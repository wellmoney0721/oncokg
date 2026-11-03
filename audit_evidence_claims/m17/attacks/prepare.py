import hashlib,json,sys
from pathlib import Path
sys.dont_write_bytecode=True
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
OUT.mkdir(parents=True,exist_ok=True)
manifest=[]
for name in ('new_probe.py','new_http.py'):
    src=ROOT/'audit_evidence_claims/m16/attacks'/name
    body=src.read_text(encoding='utf8').replace('m16_previous','m17_previous').replace('PORT = 8970','PORT = 8971')
    dst=OUT/('previous_'+name)
    dst.write_text(body.replace("'new_results.json'","'previous_results.json'").replace("'new_summary.json'","'previous_summary.json'").replace('"new_http.json"','"previous_http.json"').replace('"new_lifecycle.json"','"previous_lifecycle.json"').replace('"new_server.txt"','"previous_server.txt"'),encoding='utf8')
    manifest.append({'source':str(src.relative_to(ROOT)),'destination':str(dst.relative_to(ROOT)),'source_sha256':hashlib.sha256(src.read_bytes()).hexdigest(),'adapted_sha256':hashlib.sha256(dst.read_bytes()).hexdigest()})
(OUT/'reuse_manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf8')
