"""Reuse historical name probes, restricting adaptations to paths and ports."""
from pathlib import Path
import ast, hashlib, json

ROOT=Path.cwd()
OUT=Path(__file__).resolve().parent
OLD=ROOT/'audit_evidence_claims/m17/names'
(OUT/'tmp').mkdir(exist_ok=True)
manifest=[]
literal_deltas=[]
for source in sorted(OLD.rglob('*.py')):
    if 'tmp' in source.parts or source.name in ['build_summary.py','run_control_repair.py']:
        continue
    target=OUT/source.relative_to(OLD)
    target.parent.mkdir(parents=True,exist_ok=True)
    code=source.read_text(encoding='utf8')
    new=code.replace('audit_evidence_claims/m17/names','audit_evidence_claims/m18/names')
    if source.name=='compare_replays.py':
        new=new.replace("prior=root/'audit_evidence_claims/m16/names'", "prior=root/'audit_evidence_claims/m17/names'")
    # These exact numeric literals are exclusively old owned ports. Validate AST below.
    new=new.replace('8981','9110').replace('8982','9111')
    if target.exists():raise RuntimeError(f'Exists: {target}')
    target.write_text(new,encoding='utf8')
    old_literals=[n.value for n in ast.walk(ast.parse(code)) if isinstance(n,ast.Constant)]
    new_literals=[n.value for n in ast.walk(ast.parse(new)) if isinstance(n,ast.Constant)]
    assert len(old_literals)==len(new_literals)
    changes=[]
    for a,b in zip(old_literals,new_literals):
        if a==b:continue
        valid=(a in [8981,8982] and b in [9110,9111]) or (isinstance(a,str) and isinstance(b,str) and (
            'audit_evidence_claims/m17/names' in a or 'audit_evidence_claims/m16/names' in a or
            '127.0.0.1:898' in a or a in ['8981','8982'] or 'owned' in a))
        assert valid,(str(source),a,b)
        changes.append(dict(before=a,after=b))
    literal_deltas.append(dict(file=str(target.relative_to(ROOT)),changed_constants=changes))
    manifest.append(dict(source=str(source.relative_to(ROOT)),destination=str(target.relative_to(ROOT)),
        source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),destination_sha256=hashlib.sha256(target.read_bytes()).hexdigest(),
        changes='output path m17/names -> m18/names; ports 8981/8982 -> 9110/9111; comparison baseline m16 -> m17 where applicable'))
for name in ['new_probe.py','new_http.py']:
    source=ROOT/'audit_evidence_claims/m17/attacks'/name
    target=OUT/'m17_exact'/name
    target.parent.mkdir(exist_ok=True)
    code=source.read_text(encoding='utf8')
    new=code.replace('OUT.parents[2]','OUT.parents[3]').replace('PORT = 8972','PORT = 9112')
    target.write_text(new,encoding='utf8')
    manifest.append(dict(source=str(source.relative_to(ROOT)),destination=str(target.relative_to(ROOT)),source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),destination_sha256=hashlib.sha256(target.read_bytes()).hexdigest(),changes='root parent depth 2 -> 3; HTTP port 8972 -> 9112; case inputs unchanged'))
(OUT/'reuse_manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf8')
(OUT/'adaptation_literal_check.json').write_text(json.dumps(literal_deltas,indent=2),encoding='utf8')
inventory=[]
for round_name in ['m1','m2','m2b']+[f'm{i}' for i in range(3,18)]:
    p=ROOT/'audit_evidence_claims'/round_name/'REPORT.md'
    if p.exists():
        txt=p.read_text(encoding='utf8')
        inventory.append(dict(round=round_name,path=str(p.relative_to(ROOT)),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),
            lines=len(txt.splitlines()),headings=[s for s in txt.splitlines() if s.startswith('#')]))
    else:inventory.append(dict(round=round_name,missing=True))
(OUT/'historical_report_inventory.json').write_text(json.dumps(inventory,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(dict(copied=len(manifest),reports=len(inventory))))
