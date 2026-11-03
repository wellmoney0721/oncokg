import json, os, subprocess, sys
from pathlib import Path
ROOT=Path.cwd(); OUT=ROOT/'audit_evidence_claims/s4/faithful'; OUT.mkdir(exist_ok=True)
(OUT/'tmp').mkdir(exist_ok=True)
env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1',PYTHONUTF8='1',PYTHONIOENCODING='utf-8',TMP=str(OUT/'tmp'),TEMP=str(OUT/'tmp'))
jobs=[('s1','faithful_probe.py'),('s2','faithful_probe.py'),('s2','faithful_additional_replay.py'),('s2','faithful_dictionary_replay.py'),('s3/replay_s1','faithful_probe.py'),('s3/replay_s2','faithful_probe.py'),('s3/replay_s2','faithful_additional_replay.py'),('s3/replay_s2','faithful_dictionary_replay.py')]
manifest=[]
for source_dir,filename in jobs:
    source=ROOT/'audit_evidence_claims'/source_dir/filename
    dest=OUT/source_dir.replace('/','_');dest.mkdir(exist_ok=True)
    code=source.read_text(encoding='utf-8')
    if filename=='faithful_dictionary_replay.py':
        old="ROOT/'audit_evidence_claims/"+source_dir+"/faithful_graph_dictionary.json'"
        assert old in code,old
        code=code.replace(old,repr(str(dest/'faithful_graph_dictionary.json')))
        # A pathlib expression must stay a pathlib expression.
        code=code.replace('('+repr(str(dest/'faithful_graph_dictionary.json'))+')', 'Path('+repr(str(dest/'faithful_graph_dictionary.json'))+')')
    else:
        lines=code.splitlines()
        for i,line in enumerate(lines):
            if 'OUT=' in line or 'OUT =' in line:
                prefix=line.split(';')[0]+'; ' if ';' in line else ''
                lines[i]=prefix+'OUT=Path('+repr(str(dest))+')'
                break
        else:raise AssertionError('No OUT assignment')
        code='\n'.join(lines)+'\n'
    target=dest/filename;target.write_text(code,encoding='utf-8')
    run=subprocess.run([sys.executable,'-B',str(target)],cwd=ROOT,env=env,capture_output=True,text=True,encoding='utf-8')
    (dest/(filename+'.stdout.txt')).write_text(run.stdout+run.stderr,encoding='utf-8')
    manifest.append({'source':str(source.relative_to(ROOT)),'replay':str(target.relative_to(ROOT)),'returncode':run.returncode,'changes':'Output path only. Historical commit metadata unchanged.'})
    print(source_dir,filename,run.returncode,flush=True)
    if run.returncode: print(run.stdout+run.stderr)
checks={}
for directory in ['s1','s2','s3/replay_s1','s3/replay_s2']:
    old=json.loads((ROOT/'audit_evidence_claims'/directory/'faithful_results.json').read_text(encoding='utf-8'))
    new=json.loads((OUT/directory.replace('/','_')/'faithful_results.json').read_text(encoding='utf-8'))
    inputs=lambda x:[(r['question'],{k:v['input'] for k,v in r['modes'].items()}) for r in x['demonstrations']]
    checks[directory]={'same_demo_inputs':inputs(old)==inputs(new),'questions':len(new['demonstrations']),'claims_accepted':{mode:sum(len(r['modes'][mode]['output'].get('accepted',[])) for r in new['demonstrations']) for mode in ['labels','ids']},'same_phase_inputs':[(r['question'],r['input']) for r in old['phase_examples']]==[(r['question'],r['input']) for r in new['phase_examples']],'same_schema_inputs':[(r['question'],r['input']) for r in old['schema_limitations']]==[(r['question'],r['input']) for r in new['schema_limitations']]}
for directory in ['s2','s3/replay_s2']:
    old=json.loads((ROOT/'audit_evidence_claims'/directory/'faithful_additional_replay.json').read_text(encoding='utf-8'))
    new=json.loads((OUT/directory.replace('/','_')/'faithful_additional_replay.json').read_text(encoding='utf-8'))
    checks[directory]['additional_output_identical']=old==new
    old_d=json.loads((ROOT/'audit_evidence_claims'/directory/'faithful_graph_dictionary.json').read_text(encoding='utf-8'))
    new_d=json.loads((OUT/directory.replace('/','_')/'faithful_graph_dictionary.json').read_text(encoding='utf-8'))
    checks[directory]['dictionary_identical']=old_d==new_d
(OUT/'replay_manifest.json').write_text(json.dumps({'head':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'jobs':manifest,'checks':checks},indent=2),encoding='utf-8')
print(json.dumps(checks,indent=2))
assert all(x['returncode']==0 for x in manifest)
