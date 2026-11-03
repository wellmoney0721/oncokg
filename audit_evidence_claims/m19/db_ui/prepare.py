"""Copy the prior cumulative evidence harnesses, with output-only adaptations."""
from pathlib import Path
import hashlib,json,subprocess

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
SOURCE=ROOT/'audit_evidence_claims/m18/db_ui'
(OUT/'tmp').mkdir(exist_ok=True)
sha=lambda b:hashlib.sha256(b).hexdigest()
manifest=[]
for source in sorted(SOURCE.iterdir()):
    if source.suffix not in ('.py','.js'):continue
    target=OUT/source.name
    assert not target.exists(),target
    original=source.read_text(encoding='utf8')
    changed=original.replace('audit_evidence_claims/m18/db_ui','audit_evidence_claims/m19/db_ui')
    changed=changed.replace('m18_adjudicate_previous_query','m19_adjudicate_previous_query')
    changed=changed.replace('9121','9221')
    if source.name=='complete_review.py':
        changed=changed.replace('range(7,18)','range(7,19)').replace('range(3,18)','range(3,19)')
        changed=changed.replace('All scratch output under m18','All scratch output under m19')
        changed=changed.replace("'fixed_point':'bfcb83d'","'fixed_point':'4bed79c1f170ebe1efa3d452ce4398cce17b2113'")
    target.write_text(changed,encoding='utf8')
    manifest.append({'source':str(source.relative_to(ROOT)),'adapted':str(target.relative_to(ROOT)),
                     'source_sha256':sha(source.read_bytes()),'adapted_sha256':sha(target.read_bytes()),
                     'changes':'Output directory m18 -> m19, owned CLI port 9121 -> 9221; comparison/inventory extended through m18; no input literals changed'})
(OUT/'reuse_manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf8')
commands={
 'review_diff_latest.txt':['git','diff','4bed79c1f170ebe1efa3d452ce4398cce17b2113...HEAD','--','src','tests','web','README.md','README.ko.md','CODEX_MAP_M1_VERDICT.md'],
 'review_diff_app_ui.txt':['git','diff','bfcb83d...HEAD','--','src/app.py','web/try.html'],
 'review_diff_standards.txt':['git','ls-files','*AGENTS.md','*CONTRIBUTING.md','*CODING_STANDARDS.md','docs/agents/*'],
}
for name,command in commands.items():
    run=subprocess.run(command,cwd=ROOT,capture_output=True)
    (OUT/name).write_bytes(run.stdout)
    assert run.returncode==0,run.stderr
before={'head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
        'db_sha256':sha((ROOT/'data/processed/oncokg.sqlite').read_bytes()),
        'tracked_status':subprocess.check_output(['git','status','--short','--untracked-files=no'],cwd=ROOT,text=True)}
(OUT/'worker_integrity_before.json').write_text(json.dumps(before,indent=2),encoding='utf8')
print(json.dumps({'copied_scripts':len(manifest),'before':before}))
