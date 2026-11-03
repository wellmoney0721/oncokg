import datetime, hashlib, json, os, shutil, subprocess, sys, time, zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
E = ROOT / 'audit_evidence_round3'
ORIGINAL = E / 'original'
env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONIOENCODING='utf-8', PYTHONUTF8='1', TMP=str(E / 'tmp'), TEMP=str(E / 'tmp'))
(E / 'tmp').mkdir(exist_ok=True)
records = []

def run(name, args, cwd=ROOT):
    start = time.time()
    p = subprocess.run(args, cwd=cwd, env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    (E / (name + '.stdout.txt')).write_bytes(p.stdout)
    (E / (name + '.stderr.txt')).write_bytes(p.stderr)
    r = dict(name=name, args=args, cwd=str(cwd), exit_code=p.returncode, elapsed_seconds=round(time.time()-start,3))
    records.append(r)
    (E / 'execution.json').write_text(json.dumps(records, indent=2), encoding='utf-8')
    print(json.dumps(r), flush=True)
    return p

def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest() if p.exists() else None

def capture(name):
    run('status_' + name, ['git','status','--porcelain=v1'])
    run('diff_' + name, ['git','diff','--stat'])

tracked = subprocess.check_output(['git','ls-files','-z'], cwd=ROOT).decode().split('\0')
tracked = [p for p in tracked if p]
before = {p:sha(ROOT/p) for p in tracked}
(E / 'tracked_hashes_before.json').write_text(json.dumps(before,indent=2), encoding='utf-8')
for name in tracked:
    if name.startswith('audit_evidence_'):
        continue
    target = ORIGINAL / name
    target.parent.mkdir(parents=True,exist_ok=True)
    shutil.copy2(ROOT/name, target)
for src in (ROOT/'data/processed').glob('*'):
    if src.is_file():
        target = ORIGINAL/'data/processed'/src.name
        target.parent.mkdir(parents=True,exist_ok=True)
        shutil.copy2(src,target)
(E / 'backup_complete.txt').write_text(datetime.datetime.now().isoformat(),encoding='utf-8')

try:
    capture('before')
    run('tests_original', [sys.executable,'-m','pytest','tests','-q','-o','cache_dir='+str(E/'pytest_cache')])
    run('offline_first', [sys.executable,'src/run_all.py','--offline'])
    capture('after_first')
    run('artifact_diff_first', ['git','diff','--','reports','web'])
    changed = {p:dict(before=before[p],after=sha(ROOT/p)) for p in tracked if sha(ROOT/p)!=before[p]}
    (E/'changed_first.json').write_text(json.dumps(changed,indent=2),encoding='utf-8')
    shutil.copytree(ROOT/'reports',E/'reports_first',dirs_exist_ok=True)
    shutil.copy2(ROOT/'web/data.json',E/'dashboard_data_first.json')
    run('offline_second', [sys.executable,'src/run_all.py','--offline'])
    capture('after_second')
    shutil.copytree(ROOT/'reports',E/'reports_second',dirs_exist_ok=True)
    run('curation_standalone',[sys.executable,'src/curation_effect.py'])
    p=run('archive',['git','archive','--format=zip','--output='+str(E/'fresh_HEAD.zip'),'HEAD'])
    if p.returncode==0:
        fresh=E/'fresh'
        fresh.mkdir()
        with zipfile.ZipFile(E/'fresh_HEAD.zip') as z:
            z.extractall(fresh)
        run('tests_fresh_before',[sys.executable,'-m','pytest','tests','-q','-o','cache_dir='+str(E/'pytest_cache_fresh_before')],fresh)
        run('offline_fresh_first',[sys.executable,'src/run_all.py','--offline'],fresh)
        shutil.copy2(fresh/'reports/graph_stats.json', E/'graph_stats_fresh_first.json')
        run('offline_fresh_second',[sys.executable,'src/run_all.py','--offline'],fresh)
        shutil.copy2(fresh/'reports/graph_stats.json', E/'graph_stats_fresh_second.json')
        run('tests_fresh_after',[sys.executable,'-m','pytest','tests','-q','-o','cache_dir='+str(E/'pytest_cache_fresh_after')],fresh)
        diffs={}
        for rel in ('reports/evaluation_dev.json','reports/evaluation_frozen_test.json','reports/evaluation_postfix.json','reports/curation_effect.json','reports/quality_report.json','web/data.json'):
            a=json.loads((ROOT/rel).read_text(encoding='utf-8')); b=json.loads((fresh/rel).read_text(encoding='utf-8'))
            diffs[rel]=dict(equal=a==b)
        (E/'fresh_comparison.json').write_text(json.dumps(diffs,indent=2),encoding='utf-8')
finally:
    restored=[]
    for name in tracked:
        backup=ORIGINAL/name
        if sha(ROOT/name)!=before[name] and backup.exists():
            shutil.copy2(backup,ROOT/name)
            restored.append(name)
    for backup in (ORIGINAL/'data/processed').glob('*'):
        shutil.copy2(backup,ROOT/'data/processed'/backup.name)
    after={p:sha(ROOT/p) for p in tracked}
    (E/'preservation.json').write_text(json.dumps(dict(restored=restored,tracked_bytes_unchanged=before==after,remaining_changed=[p for p in tracked if before[p]!=after[p]]),indent=2),encoding='utf-8')
    capture('final')
    print('PRESERVATION '+(E/'preservation.json').read_text(),flush=True)
