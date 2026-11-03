"""Relocate previously reviewed reproductions without altering their case inventories."""
from pathlib import Path
import hashlib,json
root=Path.cwd()
out=Path(__file__).resolve().parent
manifest=[]
for source_base,dest_base in [(root/'audit_evidence_claims/m9/names',out),(root/'audit_evidence_claims/m9/attacks',out/'m9_attacks')]:
    for source in source_base.rglob('*.py'):
        if source.name in {'build_round9_findings.py','run_all.py','predecessor.py'}:continue
        rel=source.relative_to(source_base)
        dest=dest_base/rel
        content=source.read_text(encoding='utf-8-sig')
        replacements=[('audit_evidence_claims/m9/names','audit_evidence_claims/m10/names'),('audit_evidence_claims/m9/attacks','audit_evidence_claims/m10/names/m9_attacks'),('8891','8892'),('8901','8892'),('8895','8892')]
        for old,new in replacements:content=content.replace(old,new)
        if dest_base.name=='m9_attacks':
            content=content.replace('ROOT = Path(__file__).resolve().parents[3]','ROOT = Path.cwd()')
        dest.parent.mkdir(parents=True,exist_ok=True)
        dest.write_text(content,encoding='utf8')
        manifest.append(dict(source=str(source.relative_to(root)),destination=str(dest.relative_to(root)),source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),destination_sha256=hashlib.sha256(dest.read_bytes()).hexdigest(),adaptation='output paths m9 to m10, shared sequential HTTP port 8892; nested m9 attack ROOT becomes cwd; test inputs unchanged'))
(out/'tmp').mkdir(exist_ok=True)
(out/'reuse_manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf8')
print(json.dumps({'copied':len(manifest)}))
