"""Summarize fresh round-six database evidence without changing application files."""
import hashlib
import json
from pathlib import Path
import subprocess

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
def read(name):
    return json.loads((OUT / name).read_text(encoding='utf-8'))

validation = read('db_validate.json')
assertions = read('db_assertions.json')
snapshot = read('db_snapshot_facts.json')
head = subprocess.check_output(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True).strip()
files = ['db_validate.json', 'db_retired_center.json', 'db_fixtures.json',
         'db_missing_sponsor_count.json', 'db_role_fallback.json',
         'db_score_fixture.json', 'db_numeric_fixture.json', 'db_snapshot_facts.json',
         'db_assertions.json']
manifest = {'reviewed_head': head, 'python_bytecode_disabled': True,
            'fixture_storage': 'SQLite :memory: only; production source connected mode=ro',
            'script_adaptations': read('replay_sources.json'),
            'oracle_checks': validation['checks'], 'oracle_errors': validation['errors'],
            'oracle_seconds': validation['seconds'],
            'assertion_passed': assertions['passed'], 'assertion_total': assertions['total'],
            'outputs': {name: {'bytes': (OUT/name).stat().st_size,
                              'sha256': hashlib.sha256((OUT/name).read_bytes()).hexdigest()}
                        for name in files}}
(OUT/'manifest.json').write_text(json.dumps(manifest, indent=2), encoding='utf-8')

report = fr'''# Round 6: database, live-edge, value and ordering replay

Reviewed HEAD `{head}`. All previously repaired data-layer findings remain **FIXED**. The independent oracle checked **{validation['checks']:,} live centres**, **{len(validation['relation_combinations'])} role-aware centre/relation/direction/neighbour-type combinations**, and found **{len(validation['errors'])} mismatches** in **{validation['seconds']:.3f} seconds**. Additional assertions: **{assertions['passed']}/{assertions['total']}**. No new data-layer approval blocker was found. UI wording and product refusal require the other audit tracks.

## Method and scope

Reused the prior six m5 database scripts (themselves carrying the m1–m4 reproducers), plus the m5 assertions, under this directory. Only each script's repository-root depth changed from `parents[2]` to `parents[3]`; the assertions were unchanged. [Source/adaptation hashes](replay_sources.json), [output manifest](manifest.json). Run with `python -B`; source connections use `mode=ro`; deliberate corruptions/retirements exist only in SQLite memory backups or fresh memory databases. Every fixture server binds an ephemeral local port, and shuts down/closes in `finally`.

The independent oracle reconstructs adjacency/counts from stored rows; compares live edge IDs and endpoints, centre/neighbour types/labels, properties, roles, grouping, totals, group-size order, each item's rank, and alphabetical ties. Full lists use `per_group=100000`; the normal 30-item responses are retained for selected original inputs. [Validator](db_recheck.py), [results](db_validate.json).

## Exact prior-finding dispositions

| Prior finding | Disposition | Current reproduction and source |
|---|---|---|
| M1-B2 collaborator called lead | **FIXED at API** | `NCT00200395` separates Genentech collaborator from Montefiore lead sponsor; reverse `ORG:genentech` preserves 38 collaborator and 15 lead trials. `src/app.py:137,160-169`; [samples](db_validate.json). Page labels checked independently by UI track. |
| M1-B3 Investigator called institution | **FIXED at API** | `NCT00754364` has `SPONSORS/in/Investigator/lead_sponsor`, Armando Santoro Md; `ORG:armandosantoromd` has one lead Trial. `src/app.py:162-169`; [samples](db_validate.json). Page noun checked independently. |
| M1-B4 retired centre accepted by name | **FIXED** | In-memory retirement of `CHEMBL3353410`: `osimertinib` and canonical ID both HTTP 200/not_found; `EGFR` excludes it. `src/app.py:115-118`; [HTTP fixture](db_retired_center.json). |
| M1 retired-Trial count | **FIXED** | Live D, retired T, live T→EVALUATES→D and D→ACTS_ON→X: D centre and X's D neighbour both count 0, weight 0; T absent. `src/app.py:129-132,139,174`; [fixture](db_fixtures.json). |
| M1-S1 order, including later A–Z tie repair | **FIXED for stored order** | `MONDO_0005233` Trials rank by descending start-date string; Targets by association score, headed EGFR/KRAS/ALK. Every live centre passes descending group totals and ascending same-weight label checks. `src/app.py:141-170`; [oracle](db_validate.json). Page sort disclosures are separate. |
| M1-S7 omitted values / zero count | **FIXED at API** | NCT00200395 centre start `2003-07-02`; AstraZeneca→osimertinib has sponsor count 14, graph trials 79 and APPROVAL; CHEMBL925 zero count is 0. `src/app.py:138-149,171-177`; [samples](db_validate.json). |
| M1-S8 malformed node/edge props | **FIXED** | Node D / edge A props `null`, `[]`, `{{broken`: all 12 requests and six restored controls succeed. `src/app.py:135,171,211-217`; [fixtures](db_fixtures.json). |
| M2b-R2 unrecorded sponsor count shown as factual zero | **FIXED at API** | Mutate `ORG:alaunos\|SPONSORS_TRIAL_OF\|CHEMBL1201438\|` props to `null`, `[]`, `{{broken`, `{{}}` in memory. Both endpoints retain `evidence_trials:null`, sorting weight 0; original actual 1 stays 1. `src/app.py:141-146`; [baseline/current fixture](db_missing_sponsor_count.json). |
| M2b boolean score and rounding | **FIXED at API** | `true`/`false` score becomes null, weight 0; `0.8883707400322897` stays exact both directions. `src/app.py:152-155,207-208`; [fixture](db_score_fixture.json). Rendering checked separately. |
| M2b role fallback | **FIXED at API** | All eight stored SPONSORS props variants give 200 both directions; absent/null/unknown roles are preserved for neutral rendering; valid roles unchanged. `src/app.py:137,162-169`; [fixture](db_role_fallback.json). |
| M3/M4/M5 Infinity qualification | **NOT FIXED — unchanged, failure closed** | Positive/negative Infinity pass `_number`, but JSON serialization returns controlled HTTP 400; no invalid map is delivered. No Infinity occurs in current snapshot. `src/app.py:207-208,264-269`; [fixture](db_numeric_fixture.json). |

Numeric controls preserve 0, 1 and 3.5; null, booleans, string `"3"` and NaN become unknown with zero sort weight. The 1,001-Drug fixture crosses three 500-ID chunks and returns all 1,001 items, every one with trials/weight 1. [Assertions](db_assertions.json), [fixtures](db_fixtures.json).

## Snapshot and integrity

Current DB: {validation['facts']['retired_nodes']} retired nodes, {validation['facts']['retired_edges']} retired edges, no self-loops, no live edges with retired endpoints. Six node types; 3,000 lead-sponsor and 1,652 collaborator edges, including {snapshot['investigator_sponsors_edges']} from Investigator nodes. All current props are JSON objects; {snapshot['association_score_types'][0][1]} association scores are JSON real and {snapshot['sponsor_count_types'][0][1]} sponsor counts are integer. All {snapshot['url_count']:,} stored node URLs use the expected registry HTTPS prefix. [Snapshot](db_snapshot_facts.json).

Database SHA-256: `{snapshot['db_sha256']}`. No application remediation or tracked-file edit was performed. Standards result is in [standards_findings.md](standards_findings.md).

## Reproduction

From repository root, run each `python -B audit_evidence_claims/m6/db/<script>` in `replay_sources.json`, with `db_assertions.py` last; then `finalize.py`. All generated files stay in this directory. Self-contained fixture HTTP is genuine handler execution, not the root audit's CLI server.
'''
(OUT/'findings.md').write_text(report, encoding='utf-8')
print(json.dumps({k:manifest[k] for k in ('reviewed_head','oracle_checks','oracle_errors','oracle_seconds','assertion_passed','assertion_total')}, indent=2))
