import sys,json,sqlite3
from pathlib import Path
sys.path.insert(0,str(Path('src').resolve()))
from app import Engine
E=Engine()
rows=[dict(r) for r in E.kg.conn.execute('select id,type,label,retired_at from node where retired_at is not null')]
print(json.dumps(rows,ensure_ascii=False,indent=2))
for r in rows:
    for x in [r['id'],r['label']]:
        try:
            result=E.explore(x)
            print(json.dumps({'input':x,'result':{k:v for k,v in result.items() if k!='groups'},'groups':[(g['rel'],g['dir'],g['total']) for g in result.get('groups',[])]},ensure_ascii=False))
        except Exception as ex: print(x,repr(ex))
