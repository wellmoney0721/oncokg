"""Independent constructor-level confirmation of the organisation-name contract."""
import json
from pathlib import Path
import sqlite3
import sys
from unittest.mock import patch

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[1]
sys.path.insert(0, str(ROOT / 'src'))
from query import OncoKG
from structured import Verifier

source = OncoKG()
source.conn.execute('PRAGMA query_only=ON')
records = []
for fixture_label in ['Astrazeneca', 'Astra-Zeneca']:
    conn = sqlite3.connect(':memory:')
    conn.row_factory = sqlite3.Row
    source.conn.backup(conn)
    conn.execute('UPDATE node SET label=? WHERE id=?', (fixture_label, 'ORG:genentech'))
    with patch('query.sqlite3.connect', return_value=conn):
        kg = OncoKG()
    question = 'What is AstraZeneca running in NSCLC?'
    entities = kg.link_entities(question)
    evidence = kg.retrieve(kg.classify(question, entities), entities)
    row = {'fixture_sql': 'UPDATE node SET label=? WHERE id=?',
           'fixture_args': [fixture_label, 'ORG:genentech'], 'question': question,
           'company_key': kg.companies['astrazeneca'],
           'entities': entities, 'retrieved_ids': [e.edge_id for e in evidence],
           'genentech_node': dict(conn.execute("SELECT * FROM node WHERE id='ORG:genentech'").fetchone()),
           'parent_edges': [dict(r) for r in conn.execute("SELECT * FROM edge WHERE rel='PARENT_OF' AND dst='ORG:genentech' AND retired_at IS NULL")],
           'cases': []}
    for name in ['AstraZeneca', 'AstraZeneca!']:
        ids, reason = Verifier(kg).resolve(name, 'Company')
        for company, drug, count in [('ORG:astrazeneca', 'CHEMBL3353410', 14),
                                      ('ORG:genentech', 'CHEMBL1201583', 5)]:
            payload = {'claims': [{'kind': 'relation', 'relation': 'SPONSORS_TRIAL_OF',
                'subject': name, 'object': drug,
                'evidence': company + '|SPONSORS_TRIAL_OF|' + drug + '|', 'trial_count': count}]}
            result = kg.verify_structured(payload, evidence)
            row['cases'].append({'name': name, 'resolved_ids': sorted(ids), 'reason': reason,
                                 'input': payload, 'output': result})
    row['integrity'] = conn.execute('PRAGMA integrity_check').fetchone()[0]
    records.append(row)
    conn.close()
result = {'cases': records,
    'production_multi_id_company_keys': {k: v for k, v in source.companies.items() if len(v) > 1},
    'source_integrity': source.conn.execute('PRAGMA integrity_check').fetchone()[0]}
source.conn.close()
(OUT / 'root_confirmation.json').write_text(json.dumps(result, indent=2, ensure_ascii=True), encoding='utf-8')
print(json.dumps([{'fixture': r['fixture_args'], 'company_key': r['company_key'],
    'cases': [{'name': c['name'], 'ids': c['resolved_ids'], 'verified': c['output']['verified'],
               'text': c['output']['text'], 'rejected': c['output']['rejected']} for c in r['cases']]} for r in records], indent=2))
