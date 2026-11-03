"""Verify original tracked bytes and review artifacts; never mutate the application."""
from pathlib import Path
import datetime
import hashlib
import json
import re
import socket
import subprocess

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[1]
before = json.loads((OUT / 'root_checks/integrity_before.json').read_text(encoding='utf-8'))

def git(*args):
    got = subprocess.run(['git', *args], cwd=ROOT, capture_output=True)
    return {'code': got.returncode, 'stdout': got.stdout.decode('utf-8', 'replace'),
            'stderr': got.stderr.decode('utf-8', 'replace')}

changed = []
missing = []
for rel, digest in before['files'].items():
    file = ROOT / rel
    if not file.exists():
        missing.append(rel)
    elif hashlib.sha256(file.read_bytes()).hexdigest() != digest:
        changed.append(rel)
tracked_now = set(git('ls-files', '-z')['stdout'].split('\0')) - {''}
ports = {}
for port in [8891, 8892, 8893, 8894, 8895, 8897, 8898, 8899, 8901]:
    with socket.socket() as sock:
        sock.settimeout(.2)
        ports[str(port)] = sock.connect_ex(('127.0.0.1', port)) != 0
report = (OUT / 'REPORT.md').read_text(encoding='utf-8')
links = re.findall(r'\]\(([^)]+)\)', report)
broken = [s for s in links if s != 'integrity_final.json' and not (OUT / s).exists()]
db_hash = hashlib.sha256((ROOT / 'data/processed/oncokg.sqlite').read_bytes()).hexdigest()
result = {
    'time': datetime.datetime.now().isoformat(),
    'head_before': before['head'], 'head_after': git('rev-parse', 'HEAD')['stdout'].strip(),
    'tracked_files_hashed': len(before['files']), 'changed_tracked_files': changed,
    'missing_tracked_files': missing, 'new_tracked_paths': sorted(tracked_now-set(before['files'])),
    'tracked_diff': git('diff', '--exit-code'), 'staged_diff': git('diff', '--cached', '--exit-code'),
    'git_status': git('status', '--short'),
    'database_sha256_before': before['db_sha256'], 'database_sha256_after': db_hash,
    'database_unchanged': before['db_sha256'] == db_hash,
    'owned_ports_closed': ports, 'report_links_checked': len(links),
    'broken_report_links': broken,
    'report_final_line': report.rstrip().splitlines()[-1],
    'report_sha256': hashlib.sha256((OUT / 'REPORT.md').read_bytes()).hexdigest(),
}
result['passed'] = (not changed and not missing and not result['new_tracked_paths']
    and result['head_before'] == result['head_after']
    and result['tracked_diff']['code'] == result['staged_diff']['code'] == 0
    and result['database_unchanged'] and all(ports.values()) and not broken
    and result['report_final_line'] == 'VERDICT: CHANGES REQUIRED')
(OUT / 'integrity_final.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps(result, ensure_ascii=False, indent=2))
assert result['passed'], 'Final integrity verification failed; inspect JSON'
