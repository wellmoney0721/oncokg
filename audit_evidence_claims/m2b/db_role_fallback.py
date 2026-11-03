"""Compare m1 and m2 HTTP behavior for malformed SPONSORS props."""
import importlib.util
import json
import sqlite3
import subprocess
import sys
import threading
import types
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'src'))
import app

baseline = types.ModuleType('m1_app_for_role_audit')
baseline.__file__ = str(ROOT / 'src/app.py')
exec(compile(subprocess.check_output(['git', 'show', 'bfcb83d:src/app.py']), str(ROOT / 'src/app.py'), 'exec'), baseline.__dict__)
out = {'fixture': 'Isolated in-memory nodes O:Company and T:Trial, live O-SPONSORS->T', 'cases': []}

def run(module, raw):
    conn = sqlite3.connect(':memory:', check_same_thread=False)
    conn.row_factory = sqlite3.Row
    conn.executescript('CREATE TABLE node(id TEXT PRIMARY KEY,type TEXT,label TEXT,props TEXT,retired_at TEXT); CREATE TABLE edge(id TEXT PRIMARY KEY,src TEXT,dst TEXT,rel TEXT,props TEXT,retired_at TEXT);')
    conn.executemany('INSERT INTO node VALUES(?,?,?,?,?)', [('O','Company','Fixture institution','{}',None),('T','Trial','Fixture trial','{}',None)])
    conn.execute('INSERT INTO edge VALUES(?,?,?,?,?,?)', ('S','O','T','SPONSORS',raw,None))
    engine = module.Engine.__new__(module.Engine)
    engine.kg = types.SimpleNamespace(conn=conn, link_entities=lambda text: [])
    engine.lock = threading.Lock()
    server = ThreadingHTTPServer(('127.0.0.1', 0), module.make_handler(engine))
    worker = threading.Thread(target=server.serve_forever, daemon=True)
    worker.start()
    results = []
    try:
        for text in ('T', 'O'):
            req = urllib.request.Request(f'http://127.0.0.1:{server.server_port}/api/explore', json.dumps({'text': text}).encode(), {'Content-Type': 'application/json'})
            try:
                with urllib.request.urlopen(req, timeout=10) as r:
                    results.append({'input': text, 'status': r.status, 'body': json.load(r)})
            except urllib.error.HTTPError as e:
                results.append({'input': text, 'status': e.code, 'body': json.load(e)})
    finally:
        server.shutdown()
        server.server_close()
        worker.join(timeout=3)
        conn.close()
    return results

for raw in ('{"role":"lead_sponsor"}', '{"role":"collaborator"}', 'null', '[]', '{broken', '{}', '{"role":null}', '{"role":"unknown_role"}'):
    out['cases'].append({'stored_edge_props': raw, 'baseline_bfcb83d': run(baseline, raw), 'repair_HEAD': run(app, raw)})
prod = sqlite3.connect(f'file:{(ROOT / "data/processed/oncokg.sqlite").as_posix()}?mode=ro', uri=True)
out['current_roles'] = prod.execute("SELECT json_extract(props,'$.role'),count(*) FROM edge WHERE rel='SPONSORS' AND retired_at IS NULL GROUP BY 1").fetchall()
out['current_sponsor_count_types'] = prod.execute("SELECT json_type(props,'$.evidence_trials'),count(*) FROM edge WHERE rel='SPONSORS_TRIAL_OF' AND retired_at IS NULL GROUP BY 1").fetchall()
prod.close()
(OUT / 'db_role_fallback.json').write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps({'cases': [{'props': x['stored_edge_props'], 'before': [r['status'] for r in x['baseline_bfcb83d']], 'after': [r['status'] for r in x['repair_HEAD']], 'roles': [r['body'].get('groups', [{}])[0].get('role') for r in x['repair_HEAD']]} for x in out['cases']], 'current_roles': out['current_roles'], 'current_sponsor_count_types': out['current_sponsor_count_types']}, ensure_ascii=False))
