# Round 5: data, edge, retirement and ordering recheck

Reviewed HEAD: `514929c`. All previously repaired data-layer findings remain **FIXED**. The independent current-graph replay found no adjacency, value, count, grouping or ordering mismatch. Wording/rendering needs the separate page replay; data correctness alone does not establish correct presentation.

## Method and coverage

- Read the m1/m2b/m3/m4 reports and repair record. Reused six m4 `db_*.py` reproducers by copying them unchanged into m5. Each derives its output directory from its own location. Invocations used `python -B`; fixture mutations were only in SQLite memory databases, including backups of the read-only production connection. No model was called.
- [db_recheck.py](db_recheck.py) independently reconstructed adjacency and trial counts from stored rows, then checked **all 6,469 live centres**, **22 role-aware centre/relation/direction/neighbour-type combinations**, exact live edge sets, endpoints, roles, totals, group ordering, stored metadata/counts/scores/actions and item ranking. Result: **zero mismatches in 153.811 seconds**. [Results](db_validate.json).
- Replayed retirement, malformed-object, missing-count, role-fallback, boolean-score, numeric and 1,001-Drug chunk fixtures. All subprocesses exited 0. An additional independent output-check script passed **19/19 assertions**. [Assertions](db_assertions.json), [checker](db_assertions.py).
- Current snapshot has 7 retired nodes, 142 retired edges, no self-loops and no live edges with retired endpoints. Its SPONSORS edges have 3,000 lead-sponsor and 1,652 collaborator roles; 43 originate at Investigator nodes. All six current node types are covered. [Graph facts](db_validate.json), [snapshot](db_snapshot_facts.json).
- All stored node/edge props are valid JSON objects. All 300 association scores are JSON real, all 3,176 sponsor counts are JSON integer, and all 3,000 stored node URLs start with `https://clinicaltrials.gov/study/`. Database SHA-256 remains `7341c5a7089731f67356da5a588b269d4b69e8e6c4c054acf19aa4ef2837b529`. [Snapshot script](db_snapshot.py), [facts](db_snapshot_facts.json).

## Exact prior-finding dispositions

| Finding | Result | Exact replay and evidence |
|---|---|---|
| m1 B2: collaborator labelled lead | **FIXED at API**; wording requires page replay | `NCT00200395` separates Montefiore Medical Center as lead sponsor and Genentech as collaborator. Reverse `ORG:genentech` separates 38 collaborator and 15 lead trials. `src/app.py:137,160-169`; [samples and exhaustive results](db_validate.json). |
| m1 B3: Investigator institution wording | **FIXED at API**; wording requires page replay | `NCT00754364` exposes `SPONSORS/in/Investigator/lead_sponsor` with Armando Santoro Md. Reverse `ORG:armandosantoromd` has one lead Trial. `src/app.py:162-169`; [samples](db_validate.json). |
| m1 B4: retired centre through name | **FIXED** | Memory-only `UPDATE node SET retired_at='AUDIT_FIXTURE' WHERE id='CHEMBL3353410'`: `osimertinib` and `CHEMBL3353410` both return HTTP 200 `not_found`; `EGFR` excludes the retired Drug. `src/app.py:115-118`; [real-handler fixture](db_retired_center.json). |
| m1 retired Trial counted toward Drug | **FIXED** | Live D, retired Trial T, live `T-EVALUATES->D`, `D-ACTS_ON->X`: D centre count is 0; X's D neighbour has `trials:0, weight:0`; T is absent. `src/app.py:129-132,139,174`; [fixture](db_fixtures.json). |
| m1 S1: ranking and later equal-weight A-Z repair | **FIXED for actual order** | Disease `MONDO_0005233` sorts Trials by descending start date and Targets by stored score; EGFR, KRAS, ALK lead. All group sizes descend and equal-weight labels ascend in the independent oracle. `src/app.py:141-170`; [all-node results](db_validate.json). Page ordering descriptions are checked separately. |
| m1 S7: Trial start, sponsor-to-Drug global count/phase, zero count | **FIXED at API** | `NCT00200395` has centre start `2003-07-02`; AstraZeneca's osimertinib item has sponsor-specific count 14, global count 79 and `APPROVAL`; `CHEMBL925` has 0. `src/app.py:138-149,171-177`; [samples](db_validate.json). |
| m1 S8: malformed node/edge props | **FIXED** | All 12 original HTTP requests with node D or edge A props `null`, `[]`, `{broken` return 200; all six restored calls succeed. `src/app.py:135,171,211-217`; [fixtures](db_fixtures.json). |
| m2b R2: unavailable sponsor count treated as factual zero | **FIXED at API** | Memory backup mutates `ORG:alaunos\|SPONSORS_TRIAL_OF\|CHEMBL1201438\|` props to `null`, `[]`, `{broken`, `{}`. Both endpoint requests give `evidence_trials:null, weight:0`. Original numeric 1 stays 1. `src/app.py:141-146`; [baseline/current responses](db_missing_sponsor_count.json). |
| m2b boolean association score | **FIXED** | Memory X Target -> ASSOCIATED_WITH -> Y Disease: true/false becomes `score:null, weight:0` both ways; `0.8883707400322897` remains exact. `src/app.py:152-155,207-208`; [fixture](db_score_fixture.json). |
| m2b missing/unknown SPONSORS role fallback | **FIXED at API** | Both directions preserve absent/null role or `unknown_role`; all eight stored-props variants return HTTP 200. Valid lead/collaborator roles retain their values. `src/app.py:137,162-169`; [fixture](db_role_fallback.json). |
| m3/m4 Infinity qualification | **NOT FIXED — unchanged, failure closed** | `_number` accepts Infinity; HTTP JSON `allow_nan=False` produces controlled 400 for positive/negative Infinity, so no invalid numeric map is delivered. None occur in the snapshot. `src/app.py:207-208,264-269`; [numeric results](db_numeric_fixture.json). |

The **1,001-Drug count fixture** crosses three 500-ID chunks and returns all 1,001 items with `trials:1, weight:1`. Existing PARENT_OF, STUDIES, ASSOCIATED_WITH, EVALUATES, ACTS_ON and role-aware SPONSORS directions all agree with stored endpoints. [Fixtures](db_fixtures.json), [all-node results](db_validate.json).

Numeric controls preserve actual 0, 1 and 3.5. Null, booleans, string `"3"` and NaN become unknown/null with zero sorting weight. Infinity is a controlled failure rather than a wrong drawn value. [Numeric fixture](db_numeric_fixture.py), [results](db_numeric_fixture.json).

## Reproduction

Run at repository root. Each fixture owns and closes its ephemeral localhost server.

```text
python -B audit_evidence_claims/m5/db_recheck.py
python -B audit_evidence_claims/m5/db_missing_sponsor_count.py
python -B audit_evidence_claims/m5/db_role_fallback.py
python -B audit_evidence_claims/m5/db_score_fixture.py
python -B audit_evidence_claims/m5/db_numeric_fixture.py
python -B audit_evidence_claims/m5/db_snapshot.py
python -B audit_evidence_claims/m5/db_assertions.py
```

No data-layer approval blocker was found. Standards review is recorded separately in [standards_findings.md](standards_findings.md); refusal/QA and page behavior remain separate axes.
