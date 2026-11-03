"""Run legacy model/UI inputs, changing only locations for s3 confinement."""
from pathlib import Path
import os
import subprocess
import sys
import json

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[1]
env = dict(os.environ, PYTHONDONTWRITEBYTECODE='1', PYTHONUTF8='1', PYTHONIOENCODING='utf-8')
temp = OUT / 'modelui_tmp'
temp.mkdir(exist_ok=True)
env['TEMP'] = env['TMP'] = env['TMPDIR'] = str(temp)
manifest = []
for round_name in ['s1', 's2']:
    target = OUT / ('replay_' + round_name)
    target.mkdir(exist_ok=True)
    names = ['modelui_probe.py', 'modelui_page_probe.js']
    if round_name == 's2':
        names += ['modelui_attack.py', 'modelui_attack_page_probe.js']
    for name in names:
        src = ROOT / 'audit_evidence_claims' / round_name / name
        original = src.read_text(encoding='utf-8')
        modified = original.replace('Path(__file__).resolve().parents[2]', 'Path(__file__).resolve().parents[3]')
        modified = modified.replace('ROOT = OUT.parents[1]', 'ROOT = OUT.parents[2]')
        modified = modified.replace("path.resolve(out, '../..')", "path.resolve(out, '../../..')")
        dst = target / name
        dst.write_text(modified, encoding='utf-8')
        cmd = [sys.executable, '-B', str(dst)] if name.endswith('.py') else ['node', str(dst)]
        proc = subprocess.run(cmd, cwd=ROOT, env=env, capture_output=True, text=True, encoding='utf-8')
        (target / (name + '.stdout.txt')).write_text(proc.stdout + proc.stderr, encoding='utf-8')
        manifest.append({'source': str(src.relative_to(ROOT)), 'copy': str(dst.relative_to(ROOT)), 'exit': proc.returncode,
                         'changes': 'ROOT path only; exact original cases and payloads'})
        print(round_name, name, proc.returncode, flush=True)
        if proc.returncode:
            print(proc.stdout[-1000:], proc.stderr[-1000:], flush=True)
(OUT / 'modelui_replay_manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')
