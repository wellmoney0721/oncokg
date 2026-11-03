"""S3 name/alias attacks; persisted data query-only, fixtures strictly in memory."""
import copy
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

kg = OncoKG()
kg.conn.execute('PRAGMA query_only=ON')
out = {'cases': [], 'persisted': {}}
OSI = 'CHEMBL3353410'
EGFR = 'ENSG00000146648'
OE = f'{OSI}|ACTS_ON|{EGFR}|{OSI}'
AZ = 'ORG:astrazeneca'
GE = 'ORG:genentech'
AE = f'{AZ}|SPONSORS_TRIAL_OF|{OSI}|'
Q = 'What does osimertinib target?'
AQ = 'What is AstraZeneca running in NSCLC?'
base = {'kind': 'relation', 'relation': 'ACTS_ON', 'subject': 'osimertinib',
        'object': 'EGFR', 'evidence': OE, 'action': 'INHIBITOR'}
sponsor = {'kind': 'relation', 'relation': 'SPONSORS_TRIAL_OF', 'subject': 'AstraZeneca',
           'object': 'osimertinib', 'evidence': AE, 'trial_count': 14}

def evidence(g, q):
    entities = g.link_entities(q)
    return g.retrieve(g.classify(q, entities), entities)

def clone():
    conn = sqlite3.connect(':memory:')
    conn.row_factory = sqlite3.Row
    kg.conn.backup(conn)
    g = copy.copy(kg)
    g.conn = conn
    return g

def probe(tag, g, name, want='Drug', claim=None, question=Q, fixture=None, key='subject'):
    claim = dict(base, **{key: name}) if claim is None else dict(claim, **{key: name})
    ev = evidence(g, question)
    ids, why = Verifier(g).resolve(name, want)
    row = {'tag': tag, 'fixture': fixture, 'question': question,
           'input': {'claims': [claim]}, 'resolved_ids': sorted(ids), 'resolve_reason': why,
           'linker': g.link_entities(name), 'retrieved_ids': [e.edge_id for e in ev],
           'output': g.verify_structured({'claims': [claim]}, ev)}
    out['cases'].append(row)
    return row

out['persisted']['multi_id_company_keys'] = {k: v for k, v in kg.companies.items() if len(v) > 1}
out['persisted']['duplicate_live_labels_same_type'] = [dict(r) for r in kg.conn.execute(
    'SELECT type,lower(label) label,COUNT(*) n FROM node WHERE retired_at IS NULL GROUP BY type,lower(label) HAVING COUNT(*)>1')]
out['persisted']['company_edges'] = [dict(r) for r in kg.conn.execute(
    'SELECT id,src,dst,rel FROM edge WHERE rel=\'PARENT_OF\' AND retired_at IS NULL AND (src IN (?,?) OR dst IN (?,?))', (AZ, GE, AZ, GE))]

# Real constructor builds collision through its own graph-name indexing. No alias map injection.
g = clone()
g.conn.execute("UPDATE node SET label='Astrazeneca' WHERE id=?", (GE,))
with patch('query.sqlite3.connect', return_value=g.conn):
    g = OncoKG()
fixture = "in-memory SQL UPDATE node SET label='Astrazeneca' WHERE id='ORG:genentech'; reconstruct OncoKG with this connection (all alias-index construction is production code)"
out['constructor_collision'] = {'fixture': fixture, 'company_key': g.companies['astrazeneca'],
    'nodes': [dict(r) for r in g.conn.execute('SELECT id,type,label,props FROM node WHERE id IN (?,?)', (AZ, GE))],
    'integrity': g.conn.execute('PRAGMA integrity_check').fetchone()[0]}
for name in ['AstraZeneca', 'AstraZeneca!', 'astra-zeneca', 'ASTRAZENECA?', 'AstraZeneca is not', AZ, GE]:
    probe('constructor_company_collision:' + name, g, name, 'Company', sponsor, AQ, fixture)
# The alias now also accepts an independent Genentech edge, if it appears in this question retrieval.
ev = evidence(g, AQ)
gen = next(e for e in ev if e.edge_id.startswith(GE + '|SPONSORS_TRIAL_OF|'))
edge = dict(g.conn.execute('SELECT * FROM edge WHERE id=?', (gen.edge_id,)).fetchone())
gen_claim = dict(sponsor, object=edge['dst'], evidence=edge['id'], trial_count=json.loads(edge['props'])['evidence_trials'])
probe('constructor_company_collision:other_org_edge', g, 'AstraZeneca!', 'Company', gen_claim, AQ, fixture)

# Same-type exact-label uniqueness is case-insensitive and excludes retired duplicates.
g = clone()
g.conn.execute("UPDATE node SET label='Osimertinib' WHERE id='CHEMBL3707320'")
fixture = "in-memory duplicate Drug label Osimertinib on CHEMBL3707320"
for name in ['OSIMERTINIB', 'osimertinib', '  oSimErtinib  ', 'osimertinib!', 'Tagrisso', OSI]:
    probe('duplicate_drug_label:' + name, g, name, fixture=fixture)
g.conn.execute("UPDATE node SET retired_at='fixture' WHERE id='CHEMBL3707320'")
probe('retired_duplicate_label', g, 'OSIMERTINIB', fixture=fixture + '; duplicate retired')

# Existing organisation rename vs distinct parent/subsidiary paths in the actual graph.
for name in ['AstraZeneca', 'AstraZeneca!', 'MedImmune', 'Genentech', 'Roche', 'ORG:astrazeneca', 'ORG:medimmune', 'BeiGene', 'BeOne']:
    probe('persisted_company:' + name, kg, name, 'Company', sponsor, AQ)

# Wrong kind and salt/parent membership on the original graph.
for name in [OSI, EGFR, 'CHEMBL3545063', 'osimertinib mesylate', 'Tagrisso', 'osimertinib가 아닌', 'osimertinib NOT', 'osimertinib\u200b']:
    probe('persisted_drug:' + repr(name), kg, name)

# Retirement leaves cached dictionary aliases; this is a previously reported NOTE.
g = clone()
g.conn.execute("UPDATE node SET retired_at='fixture' WHERE id=?", (OSI,))
profile = {'kind': 'drug', 'drug': 'osimertinib', 'evidence': 'profile:' + OSI, 'max_stage': 'APPROVAL'}
for name in ['osimertinib', 'Tagrisso', OSI]:
    probe('retired_drug:' + name, g, name, claim=profile, question='What is osimertinib?',
          fixture='in-memory retirement of CHEMBL3353410; cached drug dictionary unchanged', key='drug')

out['source_integrity'] = kg.conn.execute('PRAGMA integrity_check').fetchone()[0]
(OUT / 'identity_attack_results.json').write_text(json.dumps(out, indent=2, ensure_ascii=True), encoding='utf-8')
print(json.dumps({'cases': len(out['cases']), 'persisted': out['persisted'],
                  'constructor_collision': out['constructor_collision'],
                  'results': [{'tag': r['tag'], 'ids': r['resolved_ids'], 'verified': r['output']['verified'],
                               'text': r['output']['text'], 'why': r['resolve_reason']} for r in out['cases']]}, indent=2, ensure_ascii=True))
