"""R8 independent attacks. Only writes beside this script; graph opened mode=ro."""
import hashlib
import json
import re
import sqlite3
import subprocess
import sys
import types
import unicodedata
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path.cwd()
OUT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / 'src'))
import query
import textrules as T
from app import Engine


def save(name, value):
    (OUT / name).write_text(json.dumps(value, ensure_ascii=False, indent=2), encoding='utf-8')


def engine(previous=False):
    e = Engine()
    e.kg.conn.close()
    if previous:
        source = subprocess.check_output(['git', 'show', '9bd7cb4:src/query.py'], cwd=ROOT).decode('utf-8')
        module = types.ModuleType('r8_previous_query')
        module.__file__ = str(ROOT / 'src/query.py')
        sys.modules[module.__name__] = module
        exec(compile(source, '9bd7cb4:src/query.py', 'exec'), module.__dict__)
        e.kg = module.OncoKG()
        e.kg.conn.close()
    e.kg.conn = sqlite3.connect((ROOT / 'data/processed/oncokg.sqlite').as_uri()+'?mode=ro', uri=True)
    e.kg.conn.row_factory = sqlite3.Row
    return e


current, previous = engine(), engine(True)
cases = []


def add(family, values):
    for text in values:
        if not any(t == text for _, t in cases):
            cases.append((family, text))


add('tracer_space', [
    isotope + sep + 'trastuzumab'
    for isotope in ['[89 Zr]', '[89\tZr]', '[89\nZr]', '[89\u00a0Zr]', '[89  Zr]', '[89Zr]', '[89-Zr]',
                    '89 Zr', '89Zr', '(89 Zr)', '[64 Cu]', '[177 Lu]', '[99m Tc]']
    for sep in [' ', '-', ':', ': ']
])
add('tracer_suffix', ['trastuzumab (89 Zr)', 'trastuzumab [89 Zr]', 'trastuzumab (89Zr)',
                      'trastuzumab [89Zr]', 'trastuzumab (89-Zr)', '[89Zr]:trastuzumab'])
add('suffix_internal_wrapper', [
    drug + '-' + left + suffix + right
    for drug, suffix in [('bevacizumab','awwb'), ('trastuzumab','dkst'), ('rituximab','abbs')]
    for left, right in [('(',')'), ('[',']'), ('{','}'), ('"','"'), ("'", "'"), ('\u201c','\u201d'), ('<','>')]
])
add('suffix_spacing', ['bevacizumab awwb', 'bevacizumab- awwb', 'bevacizumab - awwb',
    'bevacizumab-aw wb', 'bevacizumab- aw wb', 'bevacizumab - aw wb',
    'bevacizumab-a.w.w.b', 'bevacizumab-(a.w.w.b)', 'bevacizumab - (awwb)',
    'bevacizumab-(awwb)?', '(bevacizumab)-awwb', 'bevacizumab-(awwb), osimertinib'])
# Every Unicode character whose general category is Pd, and several dash/format controls.
dashes = [chr(i) for i in range(sys.maxunicode+1) if unicodedata.category(chr(i)) == 'Pd']
add('unicode_dashes', ['bevacizumab'+dash+'awwb' for dash in dashes + ['\u2212','\u2043','\u00ad','\u200b','\u2060']])
add('unicode_suffix_format', ['bevacizumab-'+mark+'awwb' for mark in ['\u200b','\u2060','\ufeff','\u00ad']])
add('tracer_separate_valid', [
    left + sep + right for left, right in [('[89 Zr] trastuzumab','osimertinib'), ('osimertinib','[89 Zr] trastuzumab')]
    for sep in [', ', '; ', ' / ', ' | ', ' and ']
])
add('carry_cross_punctuation', [
    'biosimilar' + sep + 'osimertinib' for sep in [', ', '; ', ' / ', ' | ', ', and ', '; and ',
        ' / and ', ' | and ', ' and, ', ' and; ', ' and / ', ' and | ', '\uff0c and ', '\u3001 and ']
])
add('control_valid_molecules', ['bevacizumab', 'trastuzumab', 'osimertinib', 'cemiplimab-rwlc',
    'dostarlimab-gxly', 'tislelizumab-jsgr', 'CP-358,774', '(E/Z)-AFATINIB', 'RO 09-1978/000',
    'is a', 'Erlotinib, hydrochloride', 'osimertinib,mesylate', 'Pegylated interferon alfa-2a',
    'biosimilar anastrozole, Arimidex', 'biosimilar Prolia, xgeva', 'Mvasi and bevacizumab',
    'bevacizumab-awwb, bevacizumab', '[89Zr] trastuzumab, trastuzumab', 'EGFR biosimilar bevacizumab',
    'AstraZeneca biosimilar bevacizumab'])
add('control_refusals', ['bevacizumab-awwb', '(bevacizumab-awwb)', 'bevacizumab\u2011awwb',
    'bevacizumab-awwb?', '[89Zr] trastuzumab', '89Zr trastuzumab', 'liposomal doxorubicin',
    'paclitaxel with albumin bound nanoparticles', 'doxorubicin (nanoparticle and liposomal formulation)'])


def compact(e, text):
    result = e.explore(text, 1)
    return {k:v for k,v in result.items() if k != 'groups'}


rows = []
for family, text in cases:
    normalized = re.sub(query._DASHES, '-', unicodedata.normalize('NFKC', text))
    blocked = current.kg._resolver_blocked(normalized)
    found = current.kg._link(normalized)
    rows.append({'family':family, 'text':text, 'normalized':normalized,
        'raw_resolver':current.resolve(text), 'normalized_resolver':current.resolve(normalized),
        'resolver_blocked':blocked, 'item_linker':found,
        'whole_name':current.kg._whole_name(normalized, blocked, found),
        'link_entities':current.kg.link_entities(text), 'map':compact(current,text),
        'previous_9bd7cb4':compact(previous,text)})

qas = []
for name in ['[89 Zr] trastuzumab','bevacizumab-(awwb)','bevacizumab\u2e3aawwb','biosimilar, and osimertinib']:
    for prefix in ['Which trials evaluate ', 'Which companies sponsor ']:
        text = prefix + name + '?'
        qas.append({'text':text,'current':current.ask(text),'previous_9bd7cb4':previous.ask(text)})

save('probe_results.json', {'head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT).decode().strip(),
                          'count':len(rows),'cases':rows,'qa':qas})
summary=[]
for r in rows:
    summary.append({'family':r['family'], 'text':r['text'],
      'center':r['map'].get('center',{}).get('id'), 'refused':r['map'].get('refused'),
      'raw_resolver_tiers':[c['tier'] for c in r['raw_resolver']['components']],
      'blocked':r['resolver_blocked'], 'previous_center':r['previous_9bd7cb4'].get('center',{}).get('id'),
      'previous_refused':r['previous_9bd7cb4'].get('refused')})
save('probe_summary.json', summary)
save('dictionary_evidence.json', [{'text':t,'canonical_key':T.canonical_key(t),
    'index_hits':current.kg.dic['index'].get(T.canonical_key(t),[])} for t in
    ['[89 Zr] trastuzumab','89Zr-trastuzumab','bevacizumab-(awwb)','bevacizumab-awwb','Bevacizumab awwb','bevacizumab\u2e3aawwb']])
save('unicode_dashes.json', [{'code':f'U+{ord(d):04X}', 'name':unicodedata.name(d,'UNKNOWN'),
    'nfkc':unicodedata.normalize('NFKC',d), 'folded':re.sub(query._DASHES,'-',unicodedata.normalize('NFKC',d)),
    'center':next(r['map'].get('center',{}).get('id') for r in rows if r['text']=='bevacizumab'+d+'awwb')}
    for d in dashes])
print(json.dumps({'cases':len(rows),'qa':len(qas),'families':sorted({r['family'] for r in rows})}))
current.kg.conn.close()
previous.kg.conn.close()
