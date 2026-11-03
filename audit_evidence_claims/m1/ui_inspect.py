from pathlib import Path
import sqlite3, json
for p in [Path('src/textrules.py'), Path('src/claims.py'), Path('src/structured.py'), Path('src/graph.py')]:
    for i,s in enumerate(p.read_text(encoding='utf-8').splitlines(),1):
        if any(q in s for q in ['AGONIST','PARENT_OF','sponsor_class','ASSOCIATED_WITH','STUDIES','ANTIBODY_DRUG_CONJUGATE']):
            print(f'{p}:{i}: {s}')
c=sqlite3.connect('file:data/processed/oncokg.sqlite?mode=ro',uri=True)
c.row_factory=sqlite3.Row
print('ACTIONS', [tuple(r) for r in c.execute("select json_extract(props,'$.action_type'),count(*) from edge where rel='ACTS_ON' group by 1")])
print('SPONSOR_CLASSES', [tuple(r) for r in c.execute("select json_extract(props,'$.sponsor_class'),count(*) from edge where rel='SPONSORS_TRIAL_OF' group by 1")])
print('AGONISTS', [dict(r) for r in c.execute("select e.*,n.label from edge e join node n on n.id=e.src where e.rel='ACTS_ON' and json_extract(e.props,'$.action_type')='AGONIST' limit 3")])
print('SPONSORS', [dict(r) for r in c.execute("select e.*, n.type, n.label from edge e join node n on n.id=e.src where e.rel='SPONSORS' and n.type='Investigator' limit 5")])
print('SPONSOR_ROLE_COUNTS', [tuple(r) for r in c.execute("select json_extract(props,'$.role'),count(*) from edge where rel='SPONSORS' and retired_at is null group by 1")])
print('COLLABORATOR_SAMPLE', [dict(r) for r in c.execute("select e.*,n.label from edge e join node n on n.id=e.src where e.rel='SPONSORS' and json_extract(e.props,'$.role')='collaborator' limit 3")])
