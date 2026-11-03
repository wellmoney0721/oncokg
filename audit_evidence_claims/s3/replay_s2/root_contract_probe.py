"""Independent confirmation of exact-label uniqueness contract, in memory only."""
import copy
import json
from pathlib import Path
import sqlite3
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'src'))
from query import OncoKG
from structured import Verifier

kg = OncoKG()
kg.conn.execute('PRAGMA query_only=ON')
question = 'What does osimertinib target?'
entities = kg.link_entities(question)
evidence = kg.retrieve(kg.classify(question, entities), entities)
payload = {'claims': [{'kind': 'relation', 'relation': 'ACTS_ON',
    'subject': 'OSIMERTINIB', 'object': 'EGFR',
    'evidence': 'CHEMBL3353410|ACTS_ON|ENSG00000146648|CHEMBL3353410',
    'action': 'INHIBITOR'}]}
clone = copy.copy(kg)
clone.conn = sqlite3.connect(':memory:')
clone.conn.row_factory = sqlite3.Row
kg.conn.backup(clone.conn)
clone.conn.execute("UPDATE node SET label='OSIMERTINIB' WHERE id='CHEMBL3707320'")
ids, why = Verifier(clone).resolve('OSIMERTINIB', 'Drug')
out = {'question': question, 'fixture_only': True,
    'fixture_sql': "UPDATE node SET label='OSIMERTINIB' WHERE id='CHEMBL3707320'",
    'live_duplicate_label_count': kg.conn.execute('SELECT COUNT(*) FROM (SELECT lower(label) FROM node WHERE retired_at IS NULL GROUP BY lower(label) HAVING COUNT(*)>1)').fetchone()[0],
    'input': payload, 'resolved_ids': sorted(ids), 'resolve_reason': why,
    'output': clone.verify_structured(payload, evidence),
    'source_graph_integrity': kg.conn.execute('PRAGMA integrity_check').fetchone()[0],
    'fixture_graph_integrity': clone.conn.execute('PRAGMA integrity_check').fetchone()[0]}
out['legacy_bug_assertion_holds'] = len(ids) == 2 and out['output']['verified'] is True
assert out['live_duplicate_label_count'] == 0
(Path(__file__).parent / 'root_contract_results.json').write_text(json.dumps(out, indent=2), encoding='utf-8')
clone.conn.close()
kg.conn.close()
print(json.dumps(out, indent=2))
