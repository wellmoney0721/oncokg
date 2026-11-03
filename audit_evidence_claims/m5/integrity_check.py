"""Read-only final audit integrity; output confined beside this script."""
import hashlib
import json
from pathlib import Path
import re
import socket
import subprocess

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[1]

def git(*args):
    proc = subprocess.run(['git', *args], cwd=ROOT, capture_output=True)
    return {'exit_code': proc.returncode,
            'stdout': proc.stdout.decode('utf-8', 'replace'),
            'stderr': proc.stderr.decode('utf-8', 'replace')}

initial = json.loads((OUT / 'verification_initial.json').read_text(encoding='utf-8'))
hashes = {name: hashlib.sha256((ROOT / name).read_bytes()).hexdigest()
          for name in initial['hashes']}
ports = {}
for port in (8880,):
    with socket.socket() as sock:
        ports[str(port)] = sock.connect_ex(('127.0.0.1', port)) != 0
report = (OUT / 'REPORT.md').read_text(encoding='utf-8')
links = re.findall(r'\[[^\]]+\]\(([^)]+)\)', report)
missing = [link for link in links
           if not link.startswith(('http://', 'https://'))
           and link != 'integrity.json' and not (OUT / link).exists()]
result = {
    'head': git('rev-parse', 'HEAD'),
    'head_unchanged': git('rev-parse', 'HEAD')['stdout'] == initial['head']['stdout'],
    'tracked_diff': git('diff', '--exit-code'),
    'staged_diff': git('diff', '--cached', '--exit-code'),
    'status': git('status', '--short'),
    'hashes_after': hashes,
    'source_and_database_hashes_unchanged': hashes == initial['hashes'],
    'owned_ports_closed': ports,
    'report_links_checked': len(links),
    'missing_report_links': missing,
    'report_ends_with_required_verdict': report.rstrip().endswith('VERDICT: CHANGES REQUIRED'),
}
(OUT / 'integrity.json').write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding='utf-8')
print(json.dumps(result, indent=2, ensure_ascii=False))
assert result['head_unchanged'] and result['source_and_database_hashes_unchanged']
assert result['tracked_diff']['exit_code'] == result['staged_diff']['exit_code'] == 0
assert all(ports.values()) and not missing and result['report_ends_with_required_verdict']
