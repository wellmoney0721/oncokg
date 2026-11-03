"""Audit-only final hashes, links, owned ports and verdict validation."""
import hashlib, json, re, socket, subprocess
from pathlib import Path

OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[1]
initial=json.loads((OUT/'root_checks/tracked_initial.json').read_text(encoding='utf8'))
def git(*args):
    p=subprocess.run(['git',*args],cwd=ROOT,capture_output=True)
    return dict(exit_code=p.returncode,stdout=p.stdout.decode('utf8','replace'),stderr=p.stderr.decode('utf8','replace'))
changed=[]; missing=[]
for name,h in initial['hashes'].items():
    p=ROOT/name
    if not p.is_file():missing.append(name)
    elif hashlib.sha256(p.read_bytes()).hexdigest()!=h:changed.append(name)
ports={}
for port in [8913,*range(8931,8940)]:
    with socket.socket() as s:
        s.settimeout(.2)
        ports[str(port)]=s.connect_ex(('127.0.0.1',port))!=0
links=0; broken=[]
reports=[OUT/'REPORT.md',OUT/'replays/FINDINGS.md',OUT/'attacks/FINDINGS.md',OUT/'demos_cost/FINDINGS.md']
for p in reports:
    for href in re.findall(r'\]\(([^)]+)\)',p.read_text(encoding='utf8')):
        if href.startswith(('http:','https:','#')):continue
        links+=1
        target=href.split('#',1)[0]
        if not (p.parent/target).exists() and target!='integrity_final.json':
            broken.append(dict(report=str(p.relative_to(OUT)),href=href))
head=git('rev-parse','HEAD');diff=git('diff','--exit-code');staged=git('diff','--cached','--exit-code');status=git('status','--short')
final_line=(OUT/'REPORT.md').read_text(encoding='utf8').rstrip().splitlines()[-1]
result=dict(initial_head=initial['head'],final_head=head,head_unchanged=initial['head']==head['stdout'].strip(),
            tracked_files_checked=len(initial['hashes']),changed_tracked_files=changed,missing_tracked_files=missing,
            tracked_diff=diff,staged_diff=staged,status=status,owned_ports_closed=ports,
            report_local_links_checked=links,broken_report_links=broken,
            database_sha256=hashlib.sha256((ROOT/'data/processed/oncokg.sqlite').read_bytes()).hexdigest(),
            main_report_last_line=final_line)
result['pass']=bool(result['head_unchanged'] and not changed and not missing and not broken and all(ports.values())
                    and diff['exit_code']==0 and staged['exit_code']==0 and final_line=='VERDICT: CHANGES REQUIRED')
(OUT/'integrity_final.json').write_text(json.dumps(result,indent=2),encoding='utf8')
print(json.dumps(result,indent=2))
raise SystemExit(0 if result['pass'] else 1)
