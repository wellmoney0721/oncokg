# Round 4: data, edge, retirement and ordering recheck

Reviewed HEAD: `bf436c6`. All previously identified data-layer failures remain **FIXED**. The current graph's exhaustive replay found no new adjacency, value, count, grouping or ordering mismatch. UI wording is checked separately by the page reviewer; this report does not substitute API data for rendering evidence.

## Method and coverage

- Read m1, m2b, m3 reports and `CODEX_MAP_M1_VERDICT.md`; copied the m3 data reproducers into m4 and reran them against current source. They derive output paths from their own location. Every created file is under m4. All Python invocations used `-B`; fixtures mutate isolated memory databases only, including backups from a read-only production connection.
- [db_recheck.py](db_recheck.py) checked **6,469 live centres**, **22 role-aware centre/relation/direction/neighbour-type combinations**, in **138.649 seconds**, with **zero mismatches**. It independently constructs adjacency and trial counts from stored rows, then checks exact edge sets, live endpoints, directions, role groups, totals, descending group sizes, stored metadata/counts/scores/actions and each group's ranking. [db_validate.json](db_validate.json).
- Current snapshot remains **7 retired nodes, 142 retired edges, no self-loops and no live edges with retired endpoints**. There are 3,000 lead-sponsor and 1,652 collaborator SPONSORS edges, with 43 Investigator SPONSORS edges. All six current node types are covered. [db_validate.json](db_validate.json), [db_snapshot_facts.json](db_snapshot_facts.json).
- All stored node/edge props are valid JSON objects. All 300 association scores are JSON real; all 3,176 sponsor counts are JSON integer. All 3,000 node URLs use `https://clinicaltrials.gov/study/`. The database SHA-256 is `7341c5a7089731f67356da5a588b269d4b69e8e6c4c054acf19aa4ef2837b529`. [Fresh read-only snapshot script](db_snapshot.py), [facts](db_snapshot_facts.json).

## Prior finding dispositions

| Finding | Disposition | Exact replay and evidence |
|---|---|---|
| m1 B2: collaborator labelled lead | **FIXED at API**; UI wording separately verified | `NCT00200395` separates Montefiore Medical Center as lead sponsor and Genentech as collaborator. Reverse `ORG:genentech` separates 38 collaborator and 15 lead trials. `src/app.py:137,160-169`; [samples and exhaustive check](db_validate.json). |
| m1 B3: Investigator institution wording | **FIXED at API**; UI wording separately verified | `NCT00754364` exposes `SPONSORS/in/Investigator/lead_sponsor` with Armando Santoro Md. Reverse `ORG:armandosantoromd` has one lead Trial. `src/app.py:162-169`; [samples](db_validate.json). |
| m1 B4: retired centre still resolves by name | **FIXED** | Memory-only `UPDATE node SET retired_at='AUDIT_FIXTURE' WHERE id='CHEMBL3353410'`: `osimertinib` and `CHEMBL3353410` both HTTP 200 `not_found`; `EGFR` excludes the retired Drug. `src/app.py:115-118`; [real-handler fixture](db_retired_center.json). |
| m1 retired Trial counted toward Drug | **FIXED** | Live D, retired Trial T, live `T-EVALUATES->D`, `D-ACTS_ON->X`: HTTP D centre count 0; X's D item has `trials:0, weight:0`; T is not returned. `src/app.py:129-132,139,174`; [fixture](db_fixtures.json). |
| m1 S1: ranking / later equal-weight A-Z repair | **FIXED for actual order** | Disease `MONDO_0005233` sorts Trials by descending start date and Targets by stored association score; EGFR, KRAS, ALK lead. All group sizes descend and equal-weight labels ascend in the independent oracle. `src/app.py:141-170`; [all-node results](db_validate.json). Page order descriptions are the UI review's scope. |
| m1 S7: omitted Trial start, sponsor-to-Drug global count/phase, zero count | **FIXED at API** | `NCT00200395` has centre start `2003-07-02`. AstraZeneca's osimertinib item has sponsor-specific count 14, global count 79 and `APPROVAL`. Zero-trial `CHEMBL925` has 0. `src/app.py:138-149,171-177`; [samples](db_validate.json). |
| m1 S8: malformed node/edge props | **FIXED** | All 12 original HTTP requests with node D or edge A props `null`, `[]`, `{broken` return 200; all six restored calls succeed. `src/app.py:135,171,211-217`; [fixtures](db_fixtures.json). |
| m2b R2: unavailable sponsor count displayed as factual zero | **FIXED at API** | Memory backup mutates `ORG:alaunos\|SPONSORS_TRIAL_OF\|CHEMBL1201438\|` props to `null`, `[]`, `{broken`, `{}`. Both endpoint requests retain `evidence_trials:null, weight:0`. The original numeric 1 stays 1. `src/app.py:141-146`; [before/current real-handler data](db_missing_sponsor_count.json). UI display is checked separately. |
| m2b boolean association score | **FIXED** | Memory X Target → ASSOCIATED_WITH → Y Disease: true/false becomes `score:null, weight:0` in both directions; numeric `0.8883707400322897` remains exact. `src/app.py:152-155,207-208`; [fixture](db_score_fixture.json). |
| Missing/unknown SPONSORS role fallback | **FIXED at API** | Both directions preserve absent/null role or `unknown_role`. All eight stored-props variants return HTTP 200; valid lead/collaborator roles retain their values. `src/app.py:137,162-169`; [fixture](db_role_fallback.json). Neutral displayed wording belongs to UI review. |
| m3 numeric Infinity limitation | **NOT FIXED — unchanged, failure closed** | `_number` still accepts Infinity, but HTTP JSON serialization uses `allow_nan=False`, so positive/negative Infinity return controlled 400, no map payload. No such values occur in the snapshot. `src/app.py:207-208,264-269`; [numeric controls](db_numeric_fixture.json). |

The **1,001-Drug** count-chunk fixture still crosses three 500-ID batches: 1,001 returned items, each `trials:1, weight:1`. [db_fixtures.json](db_fixtures.json). Existing `PARENT_OF`, `STUDIES`, `ASSOCIATED_WITH`, `EVALUATES`, `ACTS_ON` and role-aware `SPONSORS` directions all agree with their stored endpoints in the exhaustive replay.

Numeric controls also retain actual zero as zero, while null, booleans, string `"3"` and NaN become unknown/null. Numeric 1 and 3.5 remain the stored values. [db_numeric_fixture.py](db_numeric_fixture.py), [results](db_numeric_fixture.json). These extra cases do not add a new blocker.

## Reproduction

Run from the repository root, with bytecode disabled. The fixture scripts own and close ephemeral localhost HTTP servers.

```text
python -B audit_evidence_claims/m4/db_recheck.py
python -B audit_evidence_claims/m4/db_missing_sponsor_count.py
python -B audit_evidence_claims/m4/db_role_fallback.py
python -B audit_evidence_claims/m4/db_score_fixture.py
python -B audit_evidence_claims/m4/db_numeric_fixture.py
python -B audit_evidence_claims/m4/db_snapshot.py
```

No application code or real database was changed. No model was called.
