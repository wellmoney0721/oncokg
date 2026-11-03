"""Verify owned evidence, report links, tracked content and owned port without mutations."""
import hashlib,json,re,socket,subprocess
from pathlib import Path
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[1]
before=json.loads((OUT/'tracked_before.json').read_text(encoding='utf8'))
changed=[]
for p,digest in before['hashes'].items():
    f=ROOT/p
    if not f.is_file() or hashlib.sha256(f.read_bytes()).hexdigest()!=digest:changed.append(p)
def git(*args):
    p=subprocess.run(['git',*args],cwd=ROOT,capture_output=True)
    return {'exit':p.returncode,'stdout':p.stdout.decode('utf8','replace'),'stderr':p.stderr.decode('utf8','replace')}
head=git('rev-parse','HEAD')['stdout'].strip()
report=(OUT/'REPORT.md').read_text(encoding='utf8')
links=re.findall(r'\]\(([^)]+)\)',report)
missing=[x for x in links if not x.startswith(('http:','https:','#')) and not (OUT/x.split('#')[0]).exists() and x!='integrity.json']
with socket.socket() as s:port_closed=s.connect_ex(('127.0.0.1',8886))!=0
owned_sources=['src/app.py','src/query.py','web/try.html','tests/test_app.py','data/processed/oncokg.sqlite']
lifecycles={p.name:json.loads(p.read_text(encoding='utf8')) for p in [OUT/x for x in ['http_lifecycle.json','supplemental_http_lifecycle.json','attack_http_lifecycle.json','m5_http_lifecycle.json','cross_item_http_lifecycle.json','perf_check_lifecycle.json','confirm_lifecycle.json']]}
result={'head_before':before['head'],'head_after':head,'head_unchanged':head==before['head'],
        'tracked_files_checked':len(before['hashes']),'changed_tracked_content':changed,
        'tracked_diff':git('diff','--name-only'),'staged_diff':git('diff','--cached','--name-only'),
        'hashes':{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in owned_sources},
        'owned_port_8886_closed':port_closed,'lifecycles':lifecycles,
        'report_link_count':len(links),'missing_report_links':missing,
        'report_sha256':hashlib.sha256((OUT/'REPORT.md').read_bytes()).hexdigest(),
        'report_final_line':report.rstrip().splitlines()[-1],
        'scope':'Only this audit owned port 8886 and its named source/adaptation manifests. Concurrently appearing m6/root_checks, db_ui, attacks and associated files were not created, changed, stopped or used as this audit evidence.'}
(OUT/'integrity.json').write_text(json.dumps(result,indent=2),encoding='utf8')
print(json.dumps({k:v for k,v in result.items() if k not in ['lifecycles','hashes']},indent=2))
assert not changed and not missing and port_closed and head==before['head']
assert not result['tracked_diff']['stdout'].strip() and not result['staged_diff']['stdout'].strip()
assert result['report_final_line']=='VERDICT: CHANGES REQUIRED'
