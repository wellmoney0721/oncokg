"""Compare boundary behavior with the exact immediately pre-repair linker.

Read-only Engine calls. The isolated baseline changes only link_entities.
"""
import ast
import json
import re
import subprocess
import sys
import textwrap
import types
from pathlib import Path

sys.path.insert(0, str(Path('src').resolve()))
import query
import textrules as T
from app import Engine

OUT = Path('audit_evidence_claims/m18/names')
cur, old = Engine(), Engine()
source = subprocess.check_output(['git', 'show', 'c64f433:src/query.py']).decode('utf-8')
method = next(n for n in ast.walk(ast.parse(source)) if isinstance(n, ast.FunctionDef) and n.name == 'link_entities')
namespace = dict(query.__dict__)
exec(compile(textwrap.dedent(ast.get_source_segment(source, method)), 'c64f433:src/query.py', 'exec'), namespace)
old.kg.link_entities = types.MethodType(namespace['link_entities'], old.kg)

inputs = [
    'paclitaxel with albumin bound nanoparticles',
    'paclitaxel with nanoparticle albumin bound formulation',
    'paclitaxel with albumin bound formulation',
    'What trials evaluate paclitaxel with albumin bound nanoparticles?',
    'paclitaxel with albumin-bound nanoparticles',
    'generic version with bevacizumab',
    'generic version with paclitaxel',
    'generic version with osimertinib',
    'bevacizumab with albumin-bound nanoparticles',
    'Paclitaxel conjugate with poly-l-glutamic acid',
    'generic version of Paclitaxel conjugate with poly-l-glutamic acid',
    'daratumumab and hyaluronidase-fihj',
    'osimertinib, liposomal doxorubicin',
    'Mvasi, osimertinib',
    'osimertinib, Mvasi',
    'liposomal doxorubicin, osimertinib',
    'osimertinib, biosimilar bevacizumab',
    'biosimilar bevacizumab, osimertinib',
    'osimertinib and liposomal doxorubicin',
    'osimertinib, generic version of bevacizumab',
    'generic version of bevacizumab, osimertinib',
    'osimertinib with generic version of bevacizumab',
    'generic version of bevacizumab with osimertinib',
    'bevacizumab, - awwb',
    '[89Zr], trastuzumab',
    'Paclitaxel conjugate, with poly-l-glutamic acid',
    'What is the generic version of bevacizumab?',
    'osimertinib; generic version of bevacizumab',
    'osimertinib， generic version of bevacizumab',
    'Which trials evaluate osimertinib, biosimilar bevacizumab?',
]

def result(engine, value):
    mapped = engine.explore(value)
    return {
        'linker': engine.kg.link_entities(value),
        'map': {k: v for k, v in mapped.items() if k != 'groups'},
        'answer': engine.ask(value),
    }

rows = []
for value in inputs:
    rows.append({
        'input': value,
        'distinct_product': T.is_distinct_product(value),
        'radiotracer': T.is_radiotracer(value),
        'resolver': cur.resolve(value),
        'current': result(cur, value),
        'previous_linker_c64f433': result(old, value),
    })

aliases = []
for key, hits in cur.dic['index'].items():
    for hit in hits:
        if re.search(r'\b(with|and|or|plus|vs|then|without|followed)\b', hit['alias'], re.I):
            aliases.append({
                'key': key, 'stored_hit': hit,
                'current': result(cur, hit['alias']),
                'previous_linker_c64f433': result(old, hit['alias']),
            })

data = {'baseline': 'c64f433648ad252b24254030196048fc17e81006 link_entities only',
        'cases': rows, 'joiner_aliases': aliases}
OUT.joinpath('names_new_boundaries.json').write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding='utf-8')
for row in rows:
    print(json.dumps({
        'input': row['input'],
        'current': row['current']['map'],
        'previous': row['previous_linker_c64f433']['map'],
        'resolver': [(c['component'], c['tier'], c.get('drug_id')) for c in row['resolver']['components']],
        'current_evidence': len(row['current']['answer']['evidence']),
        'previous_evidence': len(row['previous_linker_c64f433']['answer']['evidence']),
    }, ensure_ascii=False))
print(json.dumps({'joiner_alias_count': len(aliases), 'joiner_alias_answer_differences': [r['stored_hit']['alias'] for r in aliases if r['current']['answer'] != r['previous_linker_c64f433']['answer']]}))
cur.kg.conn.close()
old.kg.conn.close()
