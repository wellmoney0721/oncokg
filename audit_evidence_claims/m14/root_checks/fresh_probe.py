"""Independent small normalization attack matrix, read-only Engine calls."""
from pathlib import Path
import sys,json
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[2]
sys.path.insert(0,str(ROOT/'src'))
from app import Engine
import query as Q
import textrules as T
engine=Engine()
engine.kg.conn.execute('PRAGMA query_only=ON')
cases=[
 '[89Z.r] trastuzumab','89Z_r trastuzumab','trastuzumab [89Z.r]',
 '[89Zr] trastuzumab','89 Zr trastuzumab','[8.9Zr] trastuzumab',
 'trastuzumab 8 9 Zr','bevacizumab - a - w - w - b',
 'bevacizumab a w w b','bevacizumab - awwb','bevacizumab a.w.w.b',
 'trastuzumab labelled with 89Zr','trastuzumab labeled with 89Zr',
 '89Zr labeled trastuzumab','89Zr conjugated trastuzumab',
 '99MTc trastuzumab','[99MTc] trastuzumab','99mTc trastuzumab',
 'trastuzumab','bevacizumab','osimertinib',
]
rows=[]
for text in cases:
    folded=Q._fold(text)
    raw=engine.resolve(text)
    blocked=engine.kg._resolver_blocked(folded)
    item=engine.kg._link(folded)
    whole=engine.kg._whole_name(folded,blocked,item)
    public=engine.kg.link_entities(text)
    mapped=engine.explore(text)
    rows.append(dict(input=text,key=T.canonical_key(text),words=Q._alnum_words(text),
                     isotope_predicate=T.is_isotope_label(text),raw=raw,blocked=blocked,
                     item=item,whole=whole,public=public,map=mapped))
    print(json.dumps(dict(input=text,center=mapped.get('center'),refused=mapped.get('refused')),ensure_ascii=True),flush=True)
(OUT/'fresh_probe.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf8')
engine.kg.conn.close()
