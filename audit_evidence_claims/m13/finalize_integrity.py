"""Final byte, path, lifecycle and report-link checks; never edit application files."""
from pathlib import Path
import datetime,hashlib,json,re,socket,subprocess
OUT=Path(__file__).resolve().parent;ROOT=OUT.parents[1]
before=json.loads((OUT/'integrity_before.json').read_text(encoding='utf8'))
def git(*args):
 p=subprocess.run(['git',*args],cwd=ROOT,capture_output=True)
 return dict(code=p.returncode,stdout=p.stdout.decode('utf8','replace'),stderr=p.stderr.decode('utf8','replace'))
changed=[];missing=[]
for rel,digest in before['tracked_sha256'].items():
 p=ROOT/rel
 if not p.exists():missing.append(rel)
 elif hashlib.sha256(p.read_bytes()).hexdigest()!=digest:changed.append(rel)
tracked=set(git('ls-files','-z')['stdout'].split('\0'))-{''}
ports={}
for port in [19300,19330,19331,19360,19361,19400,19401,19402,19403,19404]:
 with socket.socket() as sock:
  sock.settimeout(.2);ports[str(port)]=sock.connect_ex(('127.0.0.1',port))!=0
report=(OUT/'REPORT.md').read_text(encoding='utf8')
links=re.findall(r'\]\(([^)]+)\)',report)
broken=[s for s in links if s!='integrity_final.json' and not (OUT/s.split('#',1)[0]).exists()]
db=hashlib.sha256((ROOT/'data/processed/oncokg.sqlite').read_bytes()).hexdigest()
status=git('status','--short')
result=dict(time=datetime.datetime.now().astimezone().isoformat(),head_before=before['head'],head_after=git('rev-parse','HEAD')['stdout'].strip(),
 tracked_files_hashed=len(before['tracked_sha256']),changed_tracked_files=changed,missing_tracked_files=missing,
 new_tracked_paths=sorted(tracked-set(before['tracked_sha256'])),tracked_diff=git('diff','--exit-code'),staged_diff=git('diff','--cached','--exit-code'),
 git_status=status,initial_status=before['status'],database_sha256_before=before['db_sha256'],database_sha256_after=db,database_unchanged=db==before['db_sha256'],
 owned_ports_closed=ports,report_links_checked=len(links),broken_report_links=broken,report_final_line=report.rstrip().splitlines()[-1],
 report_sha256=hashlib.sha256((OUT/'REPORT.md').read_bytes()).hexdigest())
result['passed']=(not changed and not missing and not result['new_tracked_paths'] and result['head_before']==result['head_after']
 and result['tracked_diff']['code']==result['staged_diff']['code']==0 and result['database_unchanged'] and all(ports.values())
 and not broken and status['stdout']==before['status'] and result['report_final_line'] in ('VERDICT: CHANGES REQUIRED', 'VERDICT: APPROVE'))
(OUT/'integrity_final.json').write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps(result,ensure_ascii=False,indent=2))
assert result['passed'],'Final integrity verification failed'
