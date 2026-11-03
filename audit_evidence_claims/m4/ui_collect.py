from pathlib import Path
import sys, json, sqlite3
sys.path.insert(0, str(Path('src').resolve()))
from app import Engine

e = Engine()
e.kg.conn.close()
e.kg.conn = sqlite3.connect('file:data/processed/oncokg.sqlite?mode=ro', uri=True)
e.kg.conn.row_factory = sqlite3.Row
names = ['osimertinib','AstraZeneca','ORG:genentech','NCT00754364','NCT00200395','CHEMBL1201438','MONDO_0005233','EGFR','KRAS','Roche','ORG:roche','MET','osimertinib EGFR','EGFR osimertinib','Mvasi and bevacizumab']
zero = e.kg.conn.execute("SELECT n.id FROM node n WHERE n.type='Drug' AND n.retired_at IS NULL AND NOT EXISTS (SELECT 1 FROM edge e JOIN node t ON t.id=e.src WHERE e.dst=n.id AND e.rel='EVALUATES' AND e.retired_at IS NULL AND t.retired_at IS NULL) LIMIT 1").fetchone()[0]
names.append(zero)
results = {n:e.explore(n) for n in names}
Path('audit_evidence_claims/m4/ui_real_maps.json').write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding='utf-8')
e.kg.conn.close()
print(json.dumps({'maps':len(results),'zero_trial_drug':zero}))
