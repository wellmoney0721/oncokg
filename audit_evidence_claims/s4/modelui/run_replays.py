"""Replay original model/UI probes without changing their input or tracked outputs."""
from pathlib import Path
import json
import os
import subprocess
import sys

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
tmp = OUT / 'tmp'
tmp.mkdir(exist_ok=True)
env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONUTF8='1', PYTHONIOENCODING='utf-8',
           TEMP=str(tmp), TMP=str(tmp), TMPDIR=str(tmp))
manifest = []
names = {
    's1': ['modelui_probe.py', 'modelui_page_probe.js'],
    's2': ['modelui_probe.py', 'modelui_page_probe.js', 'modelui_attack.py', 'modelui_attack_page_probe.js'],
    's3': ['modelui_new_attacks.py', 'modelui_new_page_probe.js'],
}
for rnd, files in names.items():
    dest = OUT / ('replay_' + rnd)
    dest.mkdir(exist_ok=True)
    for name in files:
        source = ROOT / 'audit_evidence_claims' / rnd / name
        original = source.read_text(encoding='utf-8')
        changed = original.replace('ROOT = Path(__file__).resolve().parents[2]', 'ROOT = Path(__file__).resolve().parents[4]')
        changed = changed.replace('ROOT = OUT.parents[1]', 'ROOT = OUT.parents[3]')
        changed = changed.replace("path.resolve(out, '../..')", "path.resolve(out, '../../../..')")
        target = dest / name
        target.write_text(changed, encoding='utf-8')
        command = [sys.executable, '-B', str(target)] if name.endswith('.py') else ['node', str(target)]
        run = subprocess.run(command, cwd=ROOT, env=env, capture_output=True, text=True, encoding='utf-8')
        (dest / (name + '.stdout.txt')).write_text(run.stdout + run.stderr, encoding='utf-8')
        manifest.append({'source':str(source.relative_to(ROOT)), 'copy':str(target.relative_to(ROOT)),
                         'exit':run.returncode, 'changes':'ROOT lookup only; exact original cases and inputs'})
        print(rnd, name, run.returncode, flush=True)
        if run.returncode:
            print(run.stdout[-1500:], run.stderr[-1500:], flush=True)

# The original probes only saved outages if they threw. Profile their unchanged call
# again so the repaired returned answer is captured as in the s3 audit.
source = ROOT / 'audit_evidence_claims/s3/modelui_sdk_exact_replay.py'
target = OUT / source.name
target.write_text(source.read_text(encoding='utf-8'), encoding='utf-8')
run = subprocess.run([sys.executable, '-B', str(target)], cwd=ROOT, env=env,
                     capture_output=True, text=True, encoding='utf-8')
(OUT / (target.name + '.stdout.txt')).write_text(run.stdout + run.stderr, encoding='utf-8')
manifest.append({'source':str(source.relative_to(ROOT)), 'copy':str(target.relative_to(ROOT)),
                 'exit':run.returncode, 'changes':'none'})
print('sdk_exact', run.returncode, flush=True)
(OUT / 'replay_manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
assert all(row['exit'] == 0 for row in manifest), manifest
