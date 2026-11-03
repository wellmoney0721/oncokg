from pathlib import Path
import hashlib,json
root=Path.cwd();old=root/'audit_evidence_claims/m11/names';out=Path(__file__).resolve().parent
manifest=[]
for src in old.rglob('*.py'):
    if src.name=='build_summary.py':continue
    dst=out/src.relative_to(old)
    text=src.read_text(encoding='utf-8-sig').replace('audit_evidence_claims/m11/names','audit_evidence_claims/m12/names').replace('8892','8920')
    dst.parent.mkdir(parents=True,exist_ok=True);dst.write_text(text,encoding='utf8')
    manifest.append(dict(source=str(src.relative_to(root)),destination=str(dst.relative_to(root)),source_sha256=hashlib.sha256(src.read_bytes()).hexdigest(),destination_sha256=hashlib.sha256(dst.read_bytes()).hexdigest(),adaptation='Output/current-run read paths m11/names -> m12/names; shared HTTP port 8892 -> 8920; historical reads and exact input cases retained.'))
src=root/'audit_evidence_claims/m11/attacks/key_equivalence.py';dst=out/'m11_attacks/key_equivalence.py'
dst.parent.mkdir(exist_ok=True);dst.write_text(src.read_text(encoding='utf8'),encoding='utf8')
manifest.append(dict(source=str(src.relative_to(root)),destination=str(dst.relative_to(root)),source_sha256=hashlib.sha256(src.read_bytes()).hexdigest(),destination_sha256=hashlib.sha256(dst.read_bytes()).hexdigest(),adaptation='Unchanged; relative output location only. HEAD^ comparison is actual M11 query implementation.'))
(out/'tmp').mkdir(exist_ok=True)
(out/'reuse_manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf8')
print(json.dumps(dict(scripts=len(manifest),port=8920)))
