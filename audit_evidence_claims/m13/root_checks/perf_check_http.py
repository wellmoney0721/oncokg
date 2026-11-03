"""Bounded probe of the answer field passed back into the new linker."""
import concurrent.futures
import hashlib
import json
import os
from pathlib import Path
import socket
import subprocess
import sys
import time
import urllib.error
import urllib.request

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
BASE = 'http://127.0.0.1:19400'
DB = ROOT / 'data/processed/oncokg.sqlite'

def post(path, payload, timeout):
    started = time.perf_counter()
    try:
        req = urllib.request.Request(BASE + path, data=json.dumps(payload).encode(),
                                     headers={'Content-Type': 'application/json'})
        try:
            response = urllib.request.urlopen(req, timeout=timeout)
        except urllib.error.HTTPError as error:
            response = error
        return {'status': response.status, 'body': json.loads(response.read()),
                'seconds': time.perf_counter()-started}
    except TimeoutError:
        return {'timeout_seconds': timeout, 'seconds': time.perf_counter()-started}

with socket.socket() as sock:
    assert sock.connect_ex(('127.0.0.1', 19400)) != 0
before = hashlib.sha256(DB.read_bytes()).hexdigest()
env = {**os.environ, 'PYTHONDONTWRITEBYTECODE': '1', 'PYTHONUTF8': '1'}
with (OUT / 'perf_check_server.txt').open('w', encoding='utf8') as log:
    proc = subprocess.Popen([sys.executable, '-B', '-u', 'src/app.py', '19400'], cwd=ROOT,
        env=env, stdout=log, stderr=subprocess.STDOUT,
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
        normal = post('/api/explore', {'text':'EGFR'}, 5)
        small = post('/api/check', {'text':'EGFR', 'answer':' '.join(['x']*100)}, 5)
        payload = {'text':'EGFR', 'answer':' '.join(['x']*500)}
        slow = post('/api/check', payload, 5)
        started = time.perf_counter()
        get = urllib.request.urlopen(BASE, timeout=2)
        get.read()
        live_get = {'status': get.status, 'seconds': time.perf_counter()-started}
        follower = post('/api/explore', {'text':'EGFR'}, 2)
        output = {'normal_before': normal, 'small_check_199_characters': small,
                  'slow_check_input': payload, 'slow_check_999_characters': slow,
                  'get_while_check_running': live_get, 'normal_after_check_timeout': follower,
                  'limitation':'Client timeouts bound the observation; not a completed latency or permanent deadlock claim.'}
        (OUT / 'perf_check_http.json').write_text(json.dumps(output, indent=2), encoding='utf8')
        print(json.dumps({k: ({x:y for x,y in v.items() if x!='body'} if isinstance(v,dict) else v)
                          for k,v in output.items() if k!='slow_check_input'}))
    finally:
        proc.terminate()
        proc.wait(timeout=10)
        with socket.socket() as sock:
            closed = sock.connect_ex(('127.0.0.1', 19400)) != 0
        after = hashlib.sha256(DB.read_bytes()).hexdigest()
        (OUT / 'perf_check_lifecycle.json').write_text(json.dumps({'pid':proc.pid, 'port':19400,
            'port_closed':closed,'database_unchanged':before==after,'server_exit':proc.returncode},indent=2),encoding='utf8')
        assert closed and before==after
