"""Focused independent word-boundary probes; no production mutations."""
import json
from pathlib import Path
import sqlite3
import sys

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from app import Engine
import textrules as T

e = Engine()
e.kg.conn.close()
e.kg.conn = sqlite3.connect('file:data/processed/oncokg.sqlite?mode=ro', uri=True)
e.kg.conn.row_factory = sqlite3.Row
cases = [
    'liposomal and nanoparticle formulation of doxorubicin',
    'liposomal and nanoparticle formulations of doxorubicin',
    'biosimilar and investigational version of bevacizumab',
    'biosimilar and experimental versions of bevacizumab',
    'liposomal and extended-release doxorubicin',
    'liposomal and injectable doxorubicin',
    'liposomal plus injectable doxorubicin',
    'liposomal or injectable doxorubicin',
    'liposomal and nanoparticle formulations of doxorubicin and osimertinib',
    'liposomal doxorubicin and osimertinib',
    'generic version of doxorubicin and osimertinib',
    'liposomal doxorubicin',
    'doxorubicin',
    'erlotinib, hydrochloride',
    'erlotinib; hydrochloride',
    'erlotinib， hydrochloride',
    'erlotinib and hydrochloride',
    'erlotinib',
    'hydrochloride',
    'erlotinib hydrochloride',
    'Erlotinib, hydrochloride biosimilar bevacizumab',
    'osimertinib; mesylate',
    'osimertinib, mesylate',
    'osimertinib and mesylate',
    'osimertinib',
    'mesylate',
    'osimertinib mesylate',
]
rows = []
for s in cases:
    m = e.explore(s)
    question = 'Which trials evaluate ' + s + '?'
    a = e.ask(question)
    r = {'input': s, 'full_distinct_product': T.is_distinct_product(s),
         'full_radiotracer': T.is_radiotracer(s), 'entities': e.kg.link_entities(s),
         'map': m, 'resolve': e.resolve(s), 'question': question, 'answer': a}
    rows.append(r)
    print(json.dumps({'input': s, 'center': m.get('center', {}).get('id'),
                      'refused': m.get('refused'), 'also': m.get('also'),
                      'evidence_count': len(a['evidence']),
                      'resolve': [(x.get('tier'), x.get('drug_id')) for x in r['resolve']['components']]}, ensure_ascii=False))
(OUT / 'ui_boundary_probe.json').write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding='utf8')
e.kg.conn.close()
