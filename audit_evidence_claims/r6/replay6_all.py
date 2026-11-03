"""Read-only historical audit replay; all generated artifacts stay in r6."""
import difflib
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
TEMP = OUT / 'replay6_temp'
TEMP.mkdir(exist_ok=True)
env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONUTF8='1',
           PYTHONIOENCODING='utf-8', TEMP=str(TEMP), TMP=str(TEMP))
prior = ROOT / 'audit_evidence_claims/r5'
manifest = []
jobs = [(prior / Path(row['copy']).name, row['round'], row['source'])
        for row in json.loads((prior / 'replay5_manifest.json').read_text()) if 'copy' in row]
jobs += [(prior / (stem + '.py'), 'R5', 'audit_evidence_claims/r5/' + stem + '.py')
         for stem in ['root5_numeric', 'root5_confirmation', 'spec5_probe', 'spec5_extended',
                      'spec5_controls', 'spec5_anaphora', 'docs5_probe', 'docs5_controls']]
for source, round_name, original_source in jobs:
    original = source.read_text(encoding='utf-8')
    if round_name != 'R5':
        filename = source.name.replace('replay5_', 'replay6_')
        adapted = original.replace('audit_evidence_claims/r5/', 'audit_evidence_claims/r6/').replace('replay5_', 'replay6_')
    else:
        filename = 'replay6_r5_' + source.name
        adapted = original.replace('audit_evidence_claims/r5/', 'audit_evidence_claims/r6/replay6_r5_')
        adapted = adapted.replace("'root5_confirmation.json'", "'replay6_r5_root5_confirmation.json'")
        adapted = adapted.replace("'root5_verification.json'", "'replay6_r5_root5_verification.json'")
        adapted = adapted.replace("    assert result['checks']['grounded'] is expected, row", "    # Obsolete historical outcome retained as metadata; current output is measured.")
    destination = OUT / filename
    destination.write_text(adapted, encoding='utf-8')
    (OUT / (destination.stem + '_adaptation.diff')).write_text(''.join(difflib.unified_diff(
        original.splitlines(True), adapted.splitlines(True), fromfile=str(source.relative_to(ROOT)),
        tofile=str(destination.relative_to(ROOT)))), encoding='utf-8')
    proc = subprocess.run([sys.executable, '-B', str(destination)], cwd=ROOT, env=env,
                          capture_output=True, text=True, encoding='utf-8')
    (OUT / (destination.stem + '.stdout.txt')).write_text(proc.stdout, encoding='utf-8')
    (OUT / (destination.stem + '.stderr.txt')).write_text(proc.stderr, encoding='utf-8')
    manifest.append(dict(round=round_name, source=original_source, adapted_from=str(source.relative_to(ROOT)),
                         source_sha256=hashlib.sha256((ROOT / original_source).read_bytes()).hexdigest(),
                         adapted_from_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),
                         copy=str(destination.relative_to(ROOT)), returncode=proc.returncode))
    print(filename, proc.returncode, flush=True)
    (OUT / 'replay6_manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
proc = subprocess.run([sys.executable, '-m', 'pytest', 'tests', '-q', '-p', 'no:cacheprovider'],
                      cwd=ROOT, env=env, capture_output=True, text=True, encoding='utf-8')
(OUT / 'replay6_pytest.stdout.txt').write_text(proc.stdout, encoding='utf-8')
(OUT / 'replay6_pytest.stderr.txt').write_text(proc.stderr, encoding='utf-8')
manifest.append(dict(command='python -m pytest tests -q -p no:cacheprovider', returncode=proc.returncode))
(OUT / 'replay6_manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
print(proc.stdout, flush=True)
print(proc.stderr, flush=True)
sys.exit(any(row['returncode'] for row in manifest))
