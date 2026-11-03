from pathlib import Path
import ast,hashlib,json
root=Path.cwd();out=root/'audit_evidence_claims/m19/names';old=root/'audit_evidence_claims/m18/names';(out/'tmp').mkdir()
manifest=[];checks=[]
for source in sorted(old.rglob('*.py')):
 if 'tmp' in source.parts or source.name in ['prepare.py','build_summary.py']:continue
 target=out/source.relative_to(old);target.parent.mkdir(parents=True,exist_ok=True)
 code=source.read_text(encoding='utf8');new=code.replace('audit_evidence_claims/m18/names','audit_evidence_claims/m19/names')
 if source.name=='compare_replays.py':new=new.replace("prior=root/'audit_evidence_claims/m17/names'", "prior=root/'audit_evidence_claims/m18/names'")
 assert not target.exists();target.write_text(new,encoding='utf8')
 a=[n.value for n in ast.walk(ast.parse(code)) if isinstance(n,ast.Constant)];b=[n.value for n in ast.walk(ast.parse(new)) if isinstance(n,ast.Constant)];assert len(a)==len(b)
 delta=[]
 for x,y in zip(a,b):
  if x==y:continue
  assert isinstance(x,str) and ('audit_evidence_claims/m18/names' in x or (source.name=='compare_replays.py' and 'audit_evidence_claims/m17/names' in x)),(source,x,y)
  delta.append({'before':x,'after':y})
 checks.append(dict(file=str(target.relative_to(root)),changed_constants=delta))
 manifest.append(dict(source=str(source.relative_to(root)),destination=str(target.relative_to(root)),source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),destination_sha256=hashlib.sha256(target.read_bytes()).hexdigest(),changes='Output path only; compare_replays baseline m17 -> m18; exact input literals unchanged'))
for name in ['new_probe.py','new_http.py']:
 source=root/'audit_evidence_claims/m18/attacks'/name;target=out/'m18_exact'/name;target.parent.mkdir(exist_ok=True)
 code=source.read_text(encoding='utf8');new=code.replace('OUT.parents[2]','OUT.parents[3]').replace('PORT = 9132','PORT = 9112');target.write_text(new,encoding='utf8')
 manifest.append(dict(source=str(source.relative_to(root)),destination=str(target.relative_to(root)),source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),destination_sha256=hashlib.sha256(target.read_bytes()).hexdigest(),changes='Root depth 2 -> 3; port 9132 -> 9112; exact inputs unchanged'))
 checks.append(dict(file=str(target.relative_to(root)),source_cases_equal=ast.dump(next(n for n in ast.walk(ast.parse(code)) if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id.lower()=='cases' for t in n.targets)))==ast.dump(next(n for n in ast.walk(ast.parse(new)) if isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id.lower()=='cases' for t in n.targets)))))
(out/'reuse_manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf8');(out/'adaptation_literal_check.json').write_text(json.dumps(checks,ensure_ascii=False,indent=2),encoding='utf8')
inventory=[]
for r in ['m1','m2','m2b']+[f'm{i}' for i in range(3,19)]:
 p=root/'audit_evidence_claims'/r/'REPORT.md'
 if p.exists():
  lines=p.read_text(encoding='utf8').splitlines();inventory.append(dict(round=r,path=str(p.relative_to(root)),sha256=hashlib.sha256(p.read_bytes()).hexdigest(),lines=len(lines),headings=[{'line':i,'text':s} for i,s in enumerate(lines,1) if s.startswith('#')],findings=[{'line':i,'text':s} for i,s in enumerate(lines,1) if any(t in s for t in ['NOT FIXED','**B','M18-B','M17-B','M16-B','M15-B','M14-B','M13-B','M12-B','M11-B','M10-B','M9-B','M8-B','M7-B','M6-B','M5-B','M4-B','M3-B'])]))
 else:inventory.append(dict(round=r,missing=True))
(out/'historical_report_inventory.json').write_text(json.dumps(inventory,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(dict(scripts=len(manifest),reports=len(inventory))))
