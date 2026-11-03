import json, sys
from pathlib import Path
from collections import Counter
ROOT=Path.cwd(); sys.path.insert(0,str(ROOT/'src'))
import query as Q
kg=Q.OncoKG();kg.conn.execute('PRAGMA query_only=ON')
counts={}
for kind,key in [('Drug','max_phase_overall'),('Trial','phases'),('Trial','status')]:
    counts[kind+'.'+key]=dict(Counter(json.dumps(json.loads(r['props']).get(key)) for r in kg.conn.execute('SELECT props FROM node WHERE type=? AND retired_at IS NULL',(kind,))))
old=json.loads((ROOT/'audit_evidence_claims/s1/faithful_graph_dictionary.json').read_text(encoding='utf-8'))
Path("C:\\Users\\geoum\\Dropbox\\GY's Formal Workspace\\2026 Job recruting\\바이오리서치에이아이\\oncokg\\audit_evidence_claims\\s4\\faithful\\s2\\faithful_graph_dictionary.json").write_text(json.dumps({'counts':counts,'matches_s1':counts==old},indent=2),encoding='utf-8')
print('Dictionary matches s1:', counts==old)
