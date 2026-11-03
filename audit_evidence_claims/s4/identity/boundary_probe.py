"""Independent s4 alias controls using the real constructor and an in-memory DB."""
import copy
import json
from pathlib import Path
import sqlite3
import sys
from unittest.mock import patch

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
sys.path.insert(0, str(ROOT / 'src'))
from query import OncoKG
from structured import Verifier

kg = OncoKG()
kg.conn.execute('PRAGMA query_only=ON')
AZ, GE, RO = 'ORG:astrazeneca', 'ORG:genentech', 'ORG:roche'
OSI = 'CHEMBL3353410'
AQ = 'What is AstraZeneca running in NSCLC?'
AE = f'{AZ}|SPONSORS_TRIAL_OF|{OSI}|'
base = dict(kind='relation', relation='SPONSORS_TRIAL_OF', subject='AstraZeneca!',
            object=OSI, evidence=AE, trial_count=14)
out = {'cases': [], 'persisted': {}}

def clone(sql=()):
    conn = sqlite3.connect(':memory:')
    conn.row_factory = sqlite3.Row
    kg.conn.backup(conn)
    for statement, params in sql:
        conn.execute(statement, params)
    with patch('query.sqlite3.connect', return_value=conn):
        return OncoKG()

def probe(tag, graph, claim, expected, fixture, question=AQ):
    ents = graph.link_entities(question)
    ev = graph.retrieve(graph.classify(question, ents), ents)
    ids, why = Verifier(graph).resolve(claim['subject'], 'Company')
    result = graph.verify_structured({'claims':[claim]}, ev)
    out['cases'].append({'tag':tag,'question':question,'fixture':fixture,
        'input': {'claims':[claim]}, 'company_candidates':graph.companies['astrazeneca'],
        'resolved_ids':sorted(ids),'resolve_reason':why,'output':result,
        'expected_verified':expected,'expectation_met':result['verified'] == expected,
        'fixture_integrity':graph.conn.execute('PRAGMA integrity_check').fetchone()[0]})
    assert result['verified'] == expected, tag

sql = [("UPDATE node SET label='Astrazeneca' WHERE id=?", (GE,))]
g = clone(sql)
for name in ['AstraZeneca!', 'astra-zeneca', 'ASTRAZENECA?', 'AstraZeneca']:
    probe('two_candidates:' + name, g, dict(base,subject=name), False, sql)
probe('two_candidates:AZ_exact_id', g, dict(base,subject=AZ), True, sql)
claim = dict(base,subject=GE,object='CHEMBL1201583',evidence=GE+'|SPONSORS_TRIAL_OF|CHEMBL1201583|',trial_count=5)
probe('two_candidates:GE_exact_id_own_edge', g, claim, True, sql)
probe('two_candidates:GE_exact_id_wrong_edge', g, dict(base,subject=GE), False, sql)

sql3 = sql + [("UPDATE node SET label='Astrazeneca' WHERE id=?", (RO,))]
g3 = clone(sql3)
probe('three_candidates:alias', g3, base, False, sql3)
probe('three_candidates:AZ_exact_id', g3, dict(base,subject=AZ), True, sql3)

sqlret = sql + [("UPDATE node SET retired_at='s4-fixture' WHERE id=?", (GE,))]
gr = clone(sqlret)
probe('retired_duplicate_then_constructor:alias', gr, base, True, sqlret)

probe('persisted_singleton:punctuation_alias', kg, base, True, None)
probe('persisted_singleton:exact_label', kg, dict(base,subject='AstraZeneca'), True, None)

question = 'What is BeiGene running in NSCLC?'
entities = kg.link_entities(question)
ev = kg.retrieve(kg.classify(question, entities), entities)
be = next(e for e in ev if e.edge_id.startswith('ORG:beonemedicines|SPONSORS_TRIAL_OF|'))
edge = dict(kg.conn.execute('SELECT * FROM edge WHERE id=?', (be.edge_id,)).fetchone())
for name in ['BeiGene', 'BeOne', 'ORG:beonemedicines']:
    claim = dict(kind='relation',relation='SPONSORS_TRIAL_OF',subject=name,
        object=edge['dst'],evidence=edge['id'],trial_count=json.loads(edge['props'])['evidence_trials'])
    probe('persisted_rename_singleton:' + name, kg, claim, True, None, question)

# Constructor candidates come from live graph Company rows, unlike stale drug aliases.
out['persisted']['company_multi_id_keys'] = {k:v for k,v in kg.companies.items() if len(set(v)) > 1}
out['persisted']['same_type_duplicate_labels'] = [dict(r) for r in kg.conn.execute(
    'SELECT type,lower(label) AS label,COUNT(*) AS n FROM node WHERE retired_at IS NULL '
    'GROUP BY type,lower(label) HAVING COUNT(*) > 1')]
out['persisted']['source_integrity'] = kg.conn.execute('PRAGMA integrity_check').fetchone()[0]
(OUT / 'boundary_results.json').write_text(json.dumps(out, indent=2, ensure_ascii=True),encoding='utf-8')
print(json.dumps({'cases':len(out['cases']), 'all_expectations_met':all(r['expectation_met'] for r in out['cases']),
                  'persisted':out['persisted']}, indent=2))
