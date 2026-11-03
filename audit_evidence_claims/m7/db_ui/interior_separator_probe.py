"""Round-six fresh separator probe; read-only production DB, sibling output only."""
import json
import sqlite3
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'src'))
from app import Engine

e = Engine()
e.kg.conn.close()
e.kg.conn = sqlite3.connect(f'file:{(ROOT / "data/processed/oncokg.sqlite").as_posix()}?mode=ro', uri=True)
e.kg.conn.row_factory = sqlite3.Row
rows = []
for text in [
    'bevacizumab - awwb/osimertinib',
    'bevacizumab - awwb|osimertinib',
    'bevacizumab - awwb/foo',
    'bevacizumab - awwb/ osimertinib',
    'liposomal / and doxorubicin',
]:
    result = e.explore(text)
    rows.append({'text': text, 'hits': e.kg.link_entities(text),
                 'center': result.get('center'), 'refused': result.get('refused'),
                 'resolve': e.resolve(text)})
(OUT / 'interior_separator_probe.json').write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding='utf-8')
e.kg.conn.close()
print(json.dumps([{'text': r['text'], 'center': (r['center'] or {}).get('id'), 'refused': r['refused']} for r in rows]))
