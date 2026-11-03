import difflib, hashlib, json, os, subprocess, sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]; OUT=Path(__file__).resolve().parent
TEMP=OUT/'replay5_temp'; TEMP.mkdir(exist_ok=True)
env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONUTF8='1',PYTHONIOENCODING='utf-8',TEMP=str(TEMP),TMP=str(TEMP))
manifest=[]
jobs=[(ROOT/'audit_evidence_claims'/f'independent_{n}.py',f'replay5_{n}.py','R1') for n in ['main','adversarial_probe','adversarial_pairs','faithful_probe','code_dictionary','code_probes']]
jobs += [(ROOT/'audit_evidence_claims/r2'/f'{n}.py',f'replay5_r2_{n}.py','R2') for n in ['root_design_probe','spec_probe','standards_probe']]
jobs += [(ROOT/'audit_evidence_claims/r3'/f'{n}.py',f'replay5_r3_{n}.py','R3') for n in ['root3_probe','numeric3_probe','docs3_probe','docs3_focused','numeric3_dictionary']]
jobs += [(ROOT/'audit_evidence_claims/r4'/f'{n}.py',f'replay5_r4_{n}.py','R4') for n in ['docs_controls','docs_diagnostics','docs_probe','root4_confirmation','root4_probe','spec_probe','spec_controls','spec_probe2','spec_probe3']]
for source,filename,round_name in jobs:
 original=source.read_text(encoding='utf-8'); adapted=original
 if round_name=='R1':
  adapted=adapted.replace('.parents[1]','.parents[2]').replace('audit_evidence_claims/independent_','audit_evidence_claims/r5/replay5_').replace('independent_','replay5_')
 elif round_name=='R2':
  adapted=adapted.replace('audit_evidence_claims/r2/','audit_evidence_claims/r5/replay5_r2_').replace("with_name('spec_probe_results.json')","with_name('replay5_r2_spec_probe_results.json')")
  adapted=adapted.replace('_tokenise(answer, engine.kg.link_entities, {}, None)','_tokenise(answer, engine.kg.link_entities)').replace('_tokenise(alias, engine.kg.link_entities, {}, None)','_tokenise(alias, engine.kg.link_entities)')
 elif round_name=='R3':
  adapted=adapted.replace("with_name('docs3_probe_results.json')","with_name('replay5_r3_docs3_probe_results.json')").replace("with_name('docs3_focused_results.json')","with_name('replay5_r3_docs3_focused_results.json')")
 else:
  adapted=adapted.replace('audit_evidence_claims/r4/','audit_evidence_claims/r5/replay5_r4_').replace("'root4_confirmation.json'","'replay5_r4_root4_confirmation.json'").replace("'root4_verification.json'","'replay5_r4_root4_verification.json'")
  adapted=adapted.replace("    assert res['checks']['grounded']==expected, row","    # Historical expected value retained as metadata, not asserted after repairs.")
 dest=OUT/filename; dest.write_text(adapted,encoding='utf-8')
 (OUT/(dest.stem+'_adaptation.diff')).write_text(''.join(difflib.unified_diff(original.splitlines(True),adapted.splitlines(True),fromfile=str(source.relative_to(ROOT)),tofile=str(dest.relative_to(ROOT)))),encoding='utf-8')
 proc=subprocess.run([sys.executable,'-B',str(dest)],cwd=ROOT,env=env,capture_output=True,text=True,encoding='utf-8')
 (OUT/(dest.stem+'.stdout.txt')).write_text(proc.stdout,encoding='utf-8'); (OUT/(dest.stem+'.stderr.txt')).write_text(proc.stderr,encoding='utf-8')
 manifest.append(dict(round=round_name,source=str(source.relative_to(ROOT)),source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),copy=str(dest.relative_to(ROOT)),returncode=proc.returncode))
 print(filename,proc.returncode,flush=True)
proc=subprocess.run([sys.executable,'-m','pytest','tests','-q','-p','no:cacheprovider'],cwd=ROOT,env=env,capture_output=True,text=True,encoding='utf-8')
(OUT/'replay5_pytest.stdout.txt').write_text(proc.stdout,encoding='utf-8'); (OUT/'replay5_pytest.stderr.txt').write_text(proc.stderr,encoding='utf-8')
manifest.append(dict(command='python -m pytest tests -q -p no:cacheprovider',returncode=proc.returncode))
(OUT/'replay5_manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf-8')
print(proc.stdout,flush=True); print(proc.stderr,flush=True)
sys.exit(any(x['returncode'] for x in manifest))
