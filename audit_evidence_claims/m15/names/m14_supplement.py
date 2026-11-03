"""Replay literal M14 supplemental inputs plus the user-recorded data limitation."""
from pathlib import Path
import json, sqlite3, sys

root = Path.cwd()
out = Path(__file__).resolve().parent
sys.path.insert(0, str(root / 'src'))
import query
from app import Engine

e = Engine()
e.kg.conn.close()
e.kg.conn = sqlite3.connect((root / 'data/processed/oncokg.sqlite').as_uri() + '?mode=ro', uri=True)
e.kg.conn.row_factory = sqlite3.Row
prior = json.loads((root / 'audit_evidence_claims/m14/attacks/extra_neighbors.json').read_text(encoding='utf8'))
inputs = list(dict.fromkeys([r['text'] for r in prior] + ['HLX04', 'HLX-04', 'HLX04-O', 'BAT1706', 'SB8', 'MB02', 'FKB238', 'BI 695502']))
rows = []
for text in inputs:
    norm = query._fold(text)
    blocked = e.kg._resolver_blocked(norm)
    found = e.kg._link(norm)
    rows.append(dict(text=text, resolver=e.resolve(text), qualified=query._qualified(norm.split()), blocked=blocked,
                     item_linker=found, whole_name=e.kg._whole_name(norm, blocked, found),
                     public_linker=e.kg.link_entities(text), map=e.explore(text, 2),
                     trial_qa=e.ask('Which trials evaluate ' + text + '?'),
                     sponsor_qa=e.ask('Who sponsors trials of ' + text + '?')))
(out / 'm14_supplement.json').write_text(json.dumps(dict(source='m14/attacks/extra_neighbors.json plus user-listed data codes', cases=rows), ensure_ascii=False, indent=2), encoding='utf8')
e.kg.conn.close()
print(json.dumps([dict(text=r['text'], center=r['map'].get('center', {}).get('id'), refused=bool(r['map'].get('refused'))) for r in rows], indent=2))
