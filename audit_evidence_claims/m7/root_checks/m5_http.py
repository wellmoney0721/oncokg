"""Round-5 independent HTTP confirmations and bounded latency/lock measurements."""
import concurrent.futures
import hashlib
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.request

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
PORT = 8901
BASE = f'http://127.0.0.1:{PORT}'
DB = ROOT / 'data/processed/oncokg.sqlite'

def post(path, text):
    start = time.perf_counter()
    request = urllib.request.Request(BASE + path, data=json.dumps({'text': text}).encode(),
                                     headers={'Content-Type': 'application/json'})
    try:
        response = urllib.request.urlopen(request, timeout=30)
    except urllib.error.HTTPError as error:
        response = error
    raw = response.read()
    return {'path': path, 'text': text, 'characters': len(text), 'status': response.status,
            'seconds': time.perf_counter() - start, 'bytes': len(raw), 'body': json.loads(raw)}

with socket.socket() as sock:
    assert sock.connect_ex(('127.0.0.1', PORT)) != 0, 'audit port occupied'
before = hashlib.sha256(DB.read_bytes()).hexdigest()
env = {**os.environ, 'PYTHONDONTWRITEBYTECODE': '1', 'PYTHONUTF8': '1',
       'PYTHONIOENCODING': 'utf-8', 'TEMP': str(OUT / 'tmp'), 'TMP': str(OUT / 'tmp')}
with (OUT / 'm5_server.txt').open('w', encoding='utf-8') as log:
    proc = subprocess.Popen([sys.executable, '-B', '-u', 'src/app.py', str(PORT)],
                            cwd=ROOT, env=env, stdout=log, stderr=subprocess.STDOUT,
                            creationflags=getattr(subprocess, 'CREATE_NO_WINDOW', 0))
    try:
        for _ in range(100):
            assert proc.poll() is None
            try:
                urllib.request.urlopen(BASE, timeout=1).read()
                break
            except OSError:
                time.sleep(.1)
        else:
            raise RuntimeError('server unavailable')
        inputs = [
            'bevacizumab-awwb/ osimertinib',
            'bevacizumab - awwb/ osimertinib',
            'bevacizumab-awwb / osimertinib',
            'bevacizumab - awwb / osimertinib',
            'bevacizumab-awwb| osimertinib',
            'bevacizumab-awwb; osimertinib',
            'bevacizumab-awwb and osimertinib',
            'liposomal and nanoparticle formulation of doxorubicin',
            'liposomal and nanoparticle formulations of doxorubicin',
            'liposomal and sustained release doxorubicin',
            'biosimilar and investigational version of bevacizumab',
            'Erlotinib, hydrochloride biosimilar bevacizumab',
            'Erlotinib; hydrochloride biosimilar bevacizumab',
            'Erlotinib and hydrochloride biosimilar bevacizumab',
            'Erlotinib hydrochloride', 'erlotinib',
            'Pegylated interferon alfa-2a', 'PEGINTERFERON ALFA-2A',
            'CHEMBL1201560', 'EGFR biosimilar bevacizumab',
            'AstraZeneca biosimilar bevacizumab',
            'osimertinib\nbiosimilar bevacizumab',
        ]
        cases = [post(path, value) for value in inputs
                 for path in ['/api/explore', '/api/resolve']]
        for value in [
            'Which trials evaluate bevacizumab-awwb/ osimertinib?',
            'Which companies sponsor bevacizumab-awwb/ osimertinib?',
            'Which trials evaluate liposomal and nanoparticle formulations of doxorubicin?',
            'Which trials evaluate liposomal and sustained release doxorubicin?',
            'Which trials evaluate biosimilar and investigational version of bevacizumab?',
            'Which trials evaluate Erlotinib, hydrochloride biosimilar bevacizumab?',
            'Which trials evaluate Pegylated interferon alfa-2a?',
            'Which trials evaluate PEGINTERFERON ALFA-2A?',
            'Which trials evaluate osimertinib and biosimilar bevacizumab?',
            'Which companies sponsor osimertinib and biosimilar bevacizumab?',
        ]:
            cases.append(post('/api/ask', value))
        (OUT / 'm5_http.json').write_text(json.dumps({'base': BASE, 'cases': cases},
            ensure_ascii=False, indent=2), encoding='utf-8')
        for case in cases:
            body = case['body']
            if case['path'] != '/api/resolve':
                print(json.dumps({'text': case['text'], 'path': case['path'],
                    'center': body.get('center', {}).get('id'), 'refused': body.get('refused'),
                    'also': body.get('also'), 'evidence_count': len(body.get('evidence', [])),
                    'first_edge': (body.get('evidence') or [{}])[0].get('edge_id')},
                    ensure_ascii=False), flush=True)
        slow = ' '.join(['x'] * 250)
        sequential = []
        for path, text in [('/api/explore', 'EGFR'), ('/api/explore', slow),
                           ('/api/ask', slow), ('/api/explore', ' '.join(['x']*244+['osimertinib'])),
                           ('/api/explore', ' '.join(['x']*251))]:
            sequential.append(post(path, text))
        # Four simultaneous allowed 499-character requests contend for the actual engine lock.
        barrier = threading.Barrier(4)
        def send_slow(_):
            barrier.wait()
            return post('/api/explore', slow)
        started = time.perf_counter()
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
            concurrent_rows = list(pool.map(send_slow, range(4)))
        elapsed = time.perf_counter()-started
        # Readable normal request behind one long lookup; .1 s is a measured scheduling gap,
        # not a claim that a specific internal lock acquisition has been observed.
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
            future = pool.submit(post, '/api/explore', slow)
            time.sleep(.1)
            follower = post('/api/explore', 'EGFR')
            leader = future.result()
        result = {'sequential': sequential, 'concurrent': concurrent_rows,
                  'concurrent_wall_seconds': elapsed, 'normal_behind_slow': {'leader': leader, 'follower': follower},
                  'normal_after': post('/api/explore', 'EGFR')}
        (OUT / 'perf_http.json').write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
        print(json.dumps({'performance_seconds': [r['seconds'] for r in sequential],
                          'concurrent_seconds': [r['seconds'] for r in concurrent_rows],
                          'concurrent_wall_seconds': elapsed, 'normal_behind_slow_seconds': follower['seconds']}))
    finally:
        proc.terminate()
        proc.wait(timeout=10)
        with socket.socket() as sock:
            closed = sock.connect_ex(('127.0.0.1', PORT)) != 0
        after = hashlib.sha256(DB.read_bytes()).hexdigest()
        (OUT / 'm5_http_lifecycle.json').write_text(json.dumps({'pid': proc.pid, 'port': PORT,
            'server_exit': proc.returncode, 'port_closed': closed, 'database_unchanged': before == after,
            'db_sha256_before': before, 'db_sha256_after': after}, indent=2), encoding='utf-8')
        assert closed and before == after
