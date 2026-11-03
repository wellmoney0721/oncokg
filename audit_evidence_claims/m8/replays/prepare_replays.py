"""Relocate the exact previous round reproducers, without editing originals."""
from pathlib import Path
import hashlib,json

root=Path.cwd(); src=root/'audit_evidence_claims/m7/names'; out=Path(__file__).resolve().parent
rows=[]
for f in sorted(src.rglob('*.py')):
    target=out/f.relative_to(src)
    target.parent.mkdir(parents=True,exist_ok=True)
    before=f.read_text(encoding='utf8')
    after=before.replace('audit_evidence_claims/m7/names','audit_evidence_claims/m8/replays').replace('8903','8913')
    target.write_text(after,encoding='utf8')
    rows.append({'source':f.relative_to(root).as_posix(),'destination':target.relative_to(root).as_posix(),'source_sha256':hashlib.sha256(f.read_bytes()).hexdigest(),'destination_sha256':hashlib.sha256(target.read_bytes()).hexdigest(),'changes':'output path m7/names to m8/replays; fixed HTTP port 8903 to 8913 only'})
out.joinpath('reuse_manifest.json').write_text(json.dumps(rows,indent=2),encoding='utf8')
(out/'tmp').mkdir(exist_ok=True)
print('Relocated',len(rows),'scripts')
