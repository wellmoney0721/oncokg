"""Independent m2b graph/value checks. Writes only sibling audit files."""
import collections
import json
import sqlite3
import sys
import threading
import time
import types
import urllib.error
import urllib.request
from http.server import ThreadingHTTPServer
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'src'))
from app import Engine, make_handler

def connect():
    c = sqlite3.connect(f'file:{(ROOT / "data/processed/oncokg.sqlite").as_posix()}?mode=ro', uri=True, check_same_thread=False)
    c.row_factory = sqlite3.Row
    return c

def save(name, data):
    (OUT / name).write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')

def http_run(engine, queries):
    server = ThreadingHTTPServer(('127.0.0.1', 0), make_handler(engine))
    worker = threading.Thread(target=server.serve_forever, daemon=True)
    worker.start()
    def post(text):
        req = urllib.request.Request(f'http://127.0.0.1:{server.server_port}/api/explore', json.dumps({'text': text}).encode(), {'Content-Type': 'application/json'})
        try:
            with urllib.request.urlopen(req, timeout=20) as r:
                return {'input': text, 'status': r.status, 'response': json.load(r)}
        except urllib.error.HTTPError as e:
            return {'input': text, 'status': e.code, 'response': json.load(e)}
    try:
        return queries(post)
    finally:
        server.shutdown()
        server.server_close()
        worker.join(timeout=3)

c = connect()
engine = Engine()
engine.kg.conn.close()
engine.kg.conn = c
nodes = {r['id']: dict(r) for r in c.execute('SELECT * FROM node')}
edges = {r['id']: dict(r) for r in c.execute('SELECT * FROM edge')}
live = {i: n for i, n in nodes.items() if n['retired_at'] is None}
adj = collections.defaultdict(list)
counts = collections.Counter()
for ed in edges.values():
    if ed['retired_at'] is not None:
        continue
    if ed['rel'] == 'EVALUATES' and ed['src'] in live and nodes[ed['src']]['type'] == 'Trial':
        counts[ed['dst']] += 1
    if ed['src'] in live and ed['dst'] in live:
        adj[ed['src']].append(ed)
        if ed['src'] != ed['dst']:
            adj[ed['dst']].append(ed)

out = {'checks': 0, 'errors': [], 'relation_combinations': {}, 'facts': {}, 'samples': {}}
out['facts'] = {
    'live_nodes': len(live), 'retired_nodes': len(nodes) - len(live),
    'retired_edges': sum(e['retired_at'] is not None for e in edges.values()),
    'self_loops': [e['id'] for e in edges.values() if e['src'] == e['dst']],
    'live_edges_with_retired_endpoint': [e['id'] for e in edges.values() if e['retired_at'] is None and (e['src'] not in live or e['dst'] not in live)],
    'sponsor_roles': dict(collections.Counter(json.loads(e['props']).get('role') for e in edges.values() if e['rel'] == 'SPONSORS' and e['retired_at'] is None)),
}
def check(condition, nid, what, detail=None):
    if not condition:
        out['errors'].append({'id': nid, 'check': what, 'detail': detail})

started = time.perf_counter()
for index, (nid, n) in enumerate(live.items()):
    result = engine.explore(nid, per_group=100000)
    out['checks'] += 1
    check(result.get('center', {}).get('id') == nid, nid, 'center_identity')
    np = json.loads(n['props'])
    center = result['center']
    check(center['type'] == n['type'] and center['label'] == n['label'], nid, 'center_metadata')
    for key in ('max_phase_overall', 'drug_type', 'phases', 'status', 'title', 'url', 'start_date'):
        check(center['props'].get(key) == np.get(key), nid, 'center_' + key)
    if n['type'] == 'Drug':
        check(center['trials'] == counts[nid], nid, 'center_trial_count', [center['trials'], counts[nid]])
    expected = collections.defaultdict(list)
    for ed in adj[nid]:
        direction = 'out' if ed['src'] == nid else 'in'
        other = ed['dst'] if direction == 'out' else ed['src']
        ep = json.loads(ed['props'])
        role = ep.get('role') if ed['rel'] == 'SPONSORS' else None
        expected[(ed['rel'], direction, nodes[other]['type'], role)].append(ed['id'])
    actual = {(g['rel'], g['dir'], g['type'], g['role']): g for g in result['groups']}
    check(set(actual) == set(expected), nid, 'group_membership')
    check([g['total'] for g in result['groups']] == sorted((g['total'] for g in result['groups']), reverse=True), nid, 'group_size_order')
    for groupkey, g in actual.items():
        check(g['total'] == len(expected[groupkey]) == len(g['items']), nid, 'group_count')
        check(collections.Counter(it['edge_id'] for it in g['items']) == collections.Counter(expected[groupkey]), nid, 'exact_edge_set')
        combo = '|'.join(str(x) for x in (n['type'],) + groupkey)
        out['relation_combinations'].setdefault(combo, {'input': nid, 'total': g['total'], 'sample': g['items'][:1]})
        expected_ranks = []
        for it in g['items']:
            ed, nn = edges[it['edge_id']], nodes[it['id']]
            ep, pp = json.loads(ed['props']), json.loads(nn['props'])
            check(ed['retired_at'] is None and nn['retired_at'] is None, nid, 'retired_exclusion')
            check((ed['dst'] if g['dir'] == 'out' else ed['src']) == it['id'], nid, 'other_endpoint')
            check(it['type'] == nn['type'] and it['label'] == nn['label'], nid, 'neighbor_metadata')
            if nn['type'] == 'Drug':
                check(it.get('trials') == counts[it['id']], nid, 'drug_global_count')
                check(it.get('max_phase') == pp.get('max_phase_overall'), nid, 'drug_max_phase')
            if nn['type'] == 'Trial':
                for key in ('phases', 'status', 'title', 'start_date', 'url'):
                    check(it.get(key) == pp.get(key), nid, 'trial_' + key)
            if ed['rel'] == 'SPONSORS':
                check(it.get('role') == ep.get('role') == g['role'], nid, 'sponsor_role')
            if ed['rel'] == 'SPONSORS_TRIAL_OF':
                check(it.get('sponsor_class') == ep.get('sponsor_class'), nid, 'sponsor_class')
                rank = ep.get('evidence_trials') or 0
            elif nn['type'] == 'Trial':
                rank = str(pp.get('start_date') or '')
            elif nn['type'] == 'Drug':
                rank = counts[it['id']]
            elif ed['rel'] == 'ASSOCIATED_WITH':
                rank = ep.get('association_score') or 0
                check(it.get('score') == ep.get('association_score'), nid, 'association_score')
            else:
                rank = 0
            if ed['rel'] == 'ACTS_ON':
                check(it.get('action') == ep.get('action_type'), nid, 'action_type')
            check(it['weight'] == rank, nid, 'sort_weight')
            expected_ranks.append((rank, nn['label'] or ''))
        expected_order = sorted(expected_ranks, key=lambda p:p[1])
        expected_order.sort(key=lambda p:p[0], reverse=True)
        check(expected_ranks == expected_order, nid, 'item_order')
    if index % 1000 == 0:
        print('checked', index, flush=True)
out['seconds'] = time.perf_counter() - started
for text in ('NCT00200395', 'NCT00754364', 'ORG:genentech', 'ORG:armandosantoromd', 'MONDO_0005233', 'CHEMBL1201438', 'ORG:astrazeneca'):
    out['samples'][text] = engine.explore(text)
out['zero_trial_drug'] = next(nid for nid, n in live.items() if n['type'] == 'Drug' and counts[nid] == 0)
out['samples'][out['zero_trial_drug']] = engine.explore(out['zero_trial_drug'])
out['http'] = http_run(engine, lambda post: [post(t) for t in ('NCT00200395', 'NCT00754364', 'ORG:genentech', 'MONDO_0005233', out['zero_trial_drug'])])
save('db_validate.json', out)
print(json.dumps({k: out[k] for k in ('checks', 'errors', 'seconds', 'facts', 'zero_trial_drug')}, ensure_ascii=False), flush=True)

# Reproduce B4 exactly in an isolated backup with the real HTTP handler.
memory = sqlite3.connect(':memory:', check_same_thread=False)
memory.row_factory = sqlite3.Row
c.backup(memory)
engine.kg.conn = memory
sql = "UPDATE node SET retired_at='AUDIT_FIXTURE' WHERE id='CHEMBL3353410'"
memory.execute(sql)
memory.commit()
retired = {'setup': 'In-memory backup only', 'mutation_sql': sql,
           'requests': http_run(engine, lambda post: [post(t) for t in ('osimertinib', 'CHEMBL3353410', 'EGFR')])}
save('db_retired_center.json', retired)
memory.close()
engine.kg.conn = c

# The m1 retired-trial, malformed JSON and count-chunk fixtures.
fc = sqlite3.connect(':memory:', check_same_thread=False)
fc.row_factory = sqlite3.Row
fc.executescript('CREATE TABLE node(id TEXT PRIMARY KEY,type TEXT,label TEXT,props TEXT,retired_at TEXT); CREATE TABLE edge(id TEXT PRIMARY KEY,src TEXT,dst TEXT,rel TEXT,props TEXT,retired_at TEXT);')
f = Engine.__new__(Engine)
f.kg = types.SimpleNamespace(conn=fc, link_entities=lambda text: [])
f.lock = threading.Lock()
fc.executemany('INSERT INTO node VALUES(?,?,?,?,?)', [('D','Drug','Fixture drug','{}',None),('T','Trial','Retired trial','{}','2026-01-01'),('X','Target','Fixture target','{}',None)])
fc.executemany('INSERT INTO edge VALUES(?,?,?,?,?,?)', [('E','T','D','EVALUATES','{}',None),('A','D','X','ACTS_ON','{}',None)])
fixtures = {'setup': 'Isolated in-memory DB only', 'retired_trial_rows': [dict(r) for r in fc.execute('SELECT * FROM node')], 'retired_trial_edges': [dict(r) for r in fc.execute('SELECT * FROM edge')]}
def fixture_http(post):
    result = {'retired_trial': [post('D'), post('X')], 'malformed': []}
    for table, identifier in [('node', 'D'), ('edge', 'A')]:
        for value in ['null', '[]', '{broken']:
            with f.lock:
                fc.execute(f'UPDATE {table} SET props=? WHERE id=?', (value, identifier))
            item = {'table': table, 'id': identifier, 'props': value, 'requests': [post('D'), post('X')]}
            with f.lock:
                fc.execute(f'UPDATE {table} SET props=? WHERE id=?', ('{}', identifier))
            item['after_restore'] = post('X')
            result['malformed'].append(item)
    return result
fixtures.update(http_run(f, fixture_http))
fc.execute('DELETE FROM edge')
fc.execute('DELETE FROM node')
fc.execute('INSERT INTO node VALUES(?,?,?,?,?)', ('X', 'Target', 'Fixture target', '{}', None))
for i in range(1001):
    fc.execute('INSERT INTO node VALUES(?,?,?,?,?)', (f'D{i}', 'Drug', f'Drug {i}', '{"max_phase_overall":"PHASE2"}', None))
    fc.execute('INSERT INTO node VALUES(?,?,?,?,?)', (f'T{i}', 'Trial', f'Trial {i}', '{}', None))
    fc.execute('INSERT INTO edge VALUES(?,?,?,?,?,?)', (f'A{i}', f'D{i}', 'X', 'ACTS_ON', '{}', None))
    fc.execute('INSERT INTO edge VALUES(?,?,?,?,?,?)', (f'E{i}', f'T{i}', f'D{i}', 'EVALUATES', '{}', None))
r = f.explore('X', 2000)
fixtures['chunking'] = {'input': 'X', 'per_group': 2000, 'expected_drugs': 1001, 'total': r['groups'][0]['total'], 'returned': len(r['groups'][0]['items']), 'weight_histogram': dict(collections.Counter(it['weight'] for it in r['groups'][0]['items'])), 'trials_histogram': dict(collections.Counter(it['trials'] for it in r['groups'][0]['items']))}
save('db_fixtures.json', fixtures)
print(json.dumps({'retired_center': [{k: r[k] for k in ('input', 'status')} | {'not_found': r['response'].get('not_found'), 'center': r['response'].get('center', {}).get('id')} for r in retired['requests']], 'retired_trial_counts': [r['response'].get('center', {}).get('trials') for r in fixtures['retired_trial']], 'malformed_statuses': [r['status'] for x in fixtures['malformed'] for r in x['requests']], 'chunking': fixtures['chunking']}, ensure_ascii=False), flush=True)
fc.close()
c.close()
