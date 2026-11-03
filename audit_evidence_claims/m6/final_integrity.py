"""Verify every initially tracked byte and local evidence link without editing tracked files."""
import hashlib,json,re,socket,subprocess
from pathlib import Path
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[1]
before=json.loads((OUT/'integrity_initial.json').read_text(encoding='utf8'))
def git(*args):
    p=subprocess.run(['git',*args],cwd=ROOT,capture_output=True)
    return {'exit_code':p.returncode,'stdout':p.stdout.decode('utf8','replace'),
            'stderr':p.stderr.decode('utf8','replace')}
changed=[]
for f,expected in before['tracked_sha256'].items():
    p=ROOT/f
    current=hashlib.sha256(p.read_bytes()).hexdigest() if p.is_file() else None
    if current!=expected: changed.append({'file':f,'before':expected,'after':current})
ports={}
for port in (8896,8897,8899):
    with socket.socket() as s: ports[str(port)]=s.connect_ex(('127.0.0.1',port))!=0
report=OUT/'REPORT.md'
text=report.read_text(encoding='utf8')
refs=re.findall(r'\[[^\]]+\]\(([^)]+)\)',text)
missing=[]
for ref in sorted(set(refs)):
    if ref=='integrity_final.json': continue
    if not (OUT/ref.split('#')[0]).is_file(): missing.append(ref)
result={'head_before':before['head'],'head_after':git('rev-parse','HEAD'),
        'tracked_files_compared':len(before['tracked_sha256']),'changed_tracked_files':changed,
        'unstaged_diff':git('diff','--exit-code'),'staged_diff':git('diff','--cached','--exit-code'),
        'db_sha256':hashlib.sha256((ROOT/'data/processed/oncokg.sqlite').read_bytes()).hexdigest(),
        'owned_ports_closed':ports,'report_local_links_checked':len(set(refs)),
        'missing_report_links':missing,'report_final_line':text.strip().splitlines()[-1],
        'report_sha256':hashlib.sha256(report.read_bytes()).hexdigest()}
(OUT/'integrity_final.json').write_text(json.dumps(result,indent=2),encoding='utf8')
print(json.dumps(result,indent=2))
assert not changed and not missing and all(ports.values())
assert result['head_after']['stdout'].strip()==before['head']
assert result['unstaged_diff']['exit_code']==result['staged_diff']['exit_code']==0
assert result['report_final_line']=='VERDICT: CHANGES REQUIRED'
