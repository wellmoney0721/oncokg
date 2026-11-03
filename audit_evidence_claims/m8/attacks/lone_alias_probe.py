"""Focused R8 valid single-name regression checks; writes only beside script."""
import json
import sqlite3
import subprocess
import sys
import types
from pathlib import Path
sys.dont_write_bytecode=True
ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parent
sys.path.insert(0,str(ROOT/'src'))
import textrules as T
from app import Engine
current=Engine()
previous=Engine()
source=subprocess.check_output(['git','show','9bd7cb4:src/query.py'],cwd=ROOT).decode('utf-8')
module=types.ModuleType('r8_alias_previous')
module.__file__=str(ROOT/'src/query.py')
sys.modules[module.__name__]=module
exec(compile(source,'9bd7cb4:src/query.py','exec'),module.__dict__)
previous.kg.conn.close()
previous.kg=module.OncoKG()
for e in [current,previous]:
 e.kg.conn.close()
 e.kg.conn=sqlite3.connect((ROOT/'data/processed/oncokg.sqlite').as_uri()+'?mode=ro',uri=True)
 e.kg.conn.row_factory=sqlite3.Row
rows=[]
for text in ['566C','9-ac','5ac','5.BETA.,20-EPOXY-1,2.ALPHA.,4,7.BETA.','ATOVAQUONE','9-AMINOCAMPTOTHECIN','AZACITIDINE']:
 result=current.explore(text,1)
 prev=previous.explore(text,1)
 blocked=current.kg._resolver_blocked(text)
 found=current.kg._link(text)
 rows.append({'text':text,'index_hits':current.kg.dic['index'].get(T.canonical_key(text),[]),
    'exact_aliases':[h for h in current.kg.dic['index'].get(T.canonical_key(text),[]) if h['alias'].lower()==text.lower()],
    'is_isotope_label':T.is_isotope_label(text),'resolver':current.resolve(text),
    'resolver_blocked':blocked,'item_linker':found,'whole_name':current.kg._whole_name(text,blocked,found),
    'map':{k:v for k,v in result.items() if k!='groups'},
    'previous_9bd7cb4':{k:v for k,v in prev.items() if k!='groups'}})
(OUT/'lone_alias_results.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(rows,ensure_ascii=False,indent=2))
current.kg.conn.close();previous.kg.conn.close()
