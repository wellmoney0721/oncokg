"""Bounded subprocess benchmarks; writes confined to m5 and never calls a model."""
import json
import os
from pathlib import Path
import subprocess
import sys
import time
import types

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[1]
sys.path.insert(0, str(ROOT / 'src'))

if len(sys.argv) > 1:
    import query
    import textrules as T
    mode, kind, size = sys.argv[1], sys.argv[2], int(sys.argv[3])
    module = query
    if mode == 'm4':
        module = types.ModuleType('perf_m4_query')
        module.__file__ = str(ROOT / 'src/query.py')
        sys.modules[module.__name__] = module
        code = subprocess.run(['git', 'show', 'bf436c6:src/query.py'], cwd=ROOT,
                              capture_output=True, check=True).stdout.decode('utf-8')
        exec(compile(code, module.__file__, 'exec'), module.__dict__)
    kg = module.OncoKG()
    kg.conn.execute('PRAGMA query_only=ON')
    text = {'plain': ' '.join(['x'] * size),
            'drug': ' '.join(['x'] * size + ['osimertinib']),
            'split': ';'.join(['x'] * size),
            'single': 'x' * size,
            'late_qualifier': ' '.join(['x'] * size + ['biosimilar', 'bevacizumab'])}[kind]
    calls = {'is_distinct_product': 0, 'is_radiotracer': 0, 'characters': 0}
    for name in ['is_distinct_product', 'is_radiotracer']:
        original = getattr(T, name)
        def wrapped(value, name=name, original=original):
            calls[name] += 1
            calls['characters'] += len(value)
            return original(value)
        setattr(T, name, wrapped)
    start = time.perf_counter()
    entities = kg.link_entities(text)
    elapsed = time.perf_counter() - start
    kg.conn.close()
    print(json.dumps({'mode': mode, 'kind': kind, 'size': size, 'characters': len(text),
                     'seconds': elapsed, 'calls': calls, 'entities': entities}))
else:
    env = {**os.environ, 'PYTHONDONTWRITEBYTECODE': '1', 'PYTHONUTF8': '1',
           'PYTHONIOENCODING': 'utf-8', 'TEMP': str(OUT / 'tmp'),
           'TMP': str(OUT / 'tmp'), 'TMPDIR': str(OUT / 'tmp')}
    cases = [('plain', n) for n in [50, 100, 200, 250, 500, 1000]]
    cases += [('drug', 244), ('split', 250), ('single', 500), ('late_qualifier', 235)]
    rows = []
    for kind, size in cases:
        for mode in ['m4', 'HEAD']:
            try:
                proc = subprocess.run([sys.executable, '-B', __file__, mode, kind, str(size)],
                                      cwd=ROOT, env=env, capture_output=True, timeout=20)
                row = json.loads(proc.stdout) if proc.returncode == 0 else {
                    'mode': mode, 'kind': kind, 'size': size, 'error': proc.stderr.decode('utf-8', 'replace')}
            except subprocess.TimeoutExpired:
                row = {'mode': mode, 'kind': kind, 'size': size, 'timeout_seconds': 20}
            rows.append(row)
            (OUT / 'perf_results.json').write_text(json.dumps(rows, indent=2), encoding='utf-8')
            print(json.dumps(row), flush=True)
