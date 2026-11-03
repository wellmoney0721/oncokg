# Round 3 data, retirement, ordering and standards audit

HEAD: `574097f67e0719c32bfdc0526133e649b1864993`.

The exact prior data reproductions are **FIXED** at the API layer. No new stored-adjacency/value/order regression was found in the supplied database. Page wording/rendering is independently exercised by the UI audit; the data conclusions below do not substitute for it.

## Scope and evidence

- Reused m2b's `db_recheck.py`, `db_missing_sponsor_count.py`, `db_role_fallback.py` and `db_score_fixture.py`, copied into m3. They derive their output directory from their own path. All ran with bytecode writing disabled; memory fixtures use isolated SQLite databases, including backups of the read-only production connection.
- Added an explicit check that each current API `evidence_trials` equals the edge's stored value. Independently validated all **6,469 live centres**, **22 role-aware centre/relation/direction/neighbour-type combinations**, live edge membership, endpoint direction, roles, totals, trial metadata, Drug counts/phase, sponsor count/class, actions, scores and order. **Zero mismatches**, **130.292 s**. [db_recheck.py](db_recheck.py), [db_validate.json](db_validate.json).
- Current snapshot: 7 retired nodes, 142 retired edges, zero live edges with retired endpoints and zero self-loops. All six present node types are covered. There are 3,000 lead-sponsor SPONSORS edges and 1,652 collaborator edges. All current node/edge props are valid JSON objects. All 300 association scores are JSON real; all 3,176 sponsor counts are JSON integer. All 3,000 stored node URLs use `https://clinicaltrials.gov/study/`. [db_snapshot_facts.json](db_snapshot_facts.json), [db_validate.json](db_validate.json).

## Prior finding dispositions

| Prior finding | Result | Exact reproduction and current evidence |
|---|---|---|
| m1 B2 collaborator represented as lead | **FIXED** at API; UI audit checks wording | `explore('NCT00200395')` yields Montefiore in `SPONSORS/in/Company/lead_sponsor`, Genentech in `SPONSORS/in/Company/collaborator`. `ORG:genentech` keeps separate reverse groups: 38 collaborator trials and 15 lead trials. `src/app.py:137,160-169`; `db_validate.json` samples and all-edge checks. |
| m1 B3 Investigator institution wording | **FIXED** in underlying grouping; UI audit checks wording | `NCT00754364` yields `SPONSORS/in/Investigator/lead_sponsor`, Armando Santoro Md. Reverse `ORG:armandosantoromd` has one lead Trial. The type and role survive in the payload (`src/app.py:162-169`). |
| m1 B4 retired centre via name | **FIXED** | In-memory `UPDATE node SET retired_at='AUDIT_FIXTURE' WHERE id='CHEMBL3353410'`: both `osimertinib` and `CHEMBL3353410` return HTTP 200 `not_found`; `EGFR` excludes that Drug. `src/app.py:115-118`; [db_retired_center.json](db_retired_center.json). |
| m1 retired-trial count | **FIXED** | Live D, retired Trial T, live `T-EVALUATES->D`, `D-ACTS_ON->X`: HTTP D centre count is 0; X's D item has `trials:0, weight:0`; T is excluded. `src/app.py:129-132,139,174`; [db_fixtures.json](db_fixtures.json). |
| m1 S1 ordering and equal-weight A-Z repair | **FIXED** for order | `MONDO_0005233` Trials sort by descending start-date strings; Targets by stored scores, led by EGFR `0.8883707400322897`, KRAS `0.8337881598550857`, ALK `0.812639901007996`. All groups descend by size; label ties ascend. All-node oracle checks actual ranking, with separate label-then-weight stable sorts. `src/app.py:141-169`; `db_validate.json`. |
| m1 S7 omitted Trial start, sponsor-to-Drug count/phase, zero Drug count | **FIXED** in API; UI audit checks display | `NCT00200395` centre has `start_date:'2003-07-02'`; AstraZeneca's osimertinib item has `evidence_trials:14`, global `trials:79`, `max_phase:'APPROVAL'`; `CHEMBL925` centre has `trials:0`. `src/app.py:138-149,171-177`; `db_validate.json` samples. |
| m1 S8 malformed props raw errors | **FIXED** | All original 12 HTTP requests with node D or edge A props `null`, `[]`, `{broken` return 200; all restored calls succeed. `src/app.py:135,171,211-217`; `db_fixtures.json`. |
| m2b R2 unknown sponsor count becoming factual zero | **FIXED** | Backup fixture for `ORG:alaunos\|SPONSORS_TRIAL_OF\|CHEMBL1201438\|`; raw props `null`, `[]`, `{broken`, `{}`; both `CHEMBL1201438` and `ORG:alaunos` return `evidence_trials:null`, `weight:0`. Original stored `evidence_trials:1` remains 1. Former bfcb83d null/list/broken paths still fail 400 in comparison. The factual field is now separate from sort weight at `src/app.py:141-146`. [db_missing_sponsor_count.json](db_missing_sponsor_count.json). |
| m2b boolean score | **FIXED** | In-memory X Target → ASSOCIATED_WITH → Y Disease with `association_score:true` or `false`: both direction HTTP payloads now have `score:null, weight:0`; exact numeric `0.8883707400322897` remains unchanged. `src/app.py:152-155,207-208`; [db_score_fixture.json](db_score_fixture.json). |
| m2b missing/unknown SPONSORS role fallback | **FIXED** at data layer; UI audit checks neutral wording | Both directions preserve null/missing role or `unknown_role`; all eight raw-props variants complete HTTP 200. Actual lead/collaborator roles remain unchanged. [db_role_fallback.json](db_role_fallback.json). |
| m1/m2b module 'everything' overclaim | **FIXED** | `src/app.py:5-6` now states a capped list per relation. “All of them” remains at line 11. |

The 1,001-Drug fixture still crosses three count batches and returns exactly 1,001 items, all `trials:1, weight:1` (`src/app.py:125-132`, `db_fixtures.json`). No current live relation directions or stored values changed unexpectedly.

## Additional numeric controls

[db_numeric_fixture.py](db_numeric_fixture.py) and [db_numeric_fixture.json](db_numeric_fixture.json) exercise the real handler for association-score and sponsor-count fields with `null`, booleans, 0, 1, 3.5, string `"3"`, NaN and positive/negative Infinity. Numeric **0 remains 0**. Null, booleans, numeric strings and NaN become unknown/null, with sort weight 0. Infinity is accepted by `_number` but final `allow_nan=False` serialization returns controlled HTTP 400; it is never delivered as a drawn value. This is a failure-closed qualification, not a new approval blocker. These exceptional values do not occur in the supplied snapshot.

## Standards axis

`git ls-files '*AGENTS.md' '*STANDARDS*' '*CONTRIBUTING*' 'docs/agents/*'` finds no tracked standards files. The source-only `git diff bfcb83d...HEAD` was reviewed against the user's explicit brief and evidence requirement. No separate documented coding-standard violation is asserted. No tracked file or real database was edited; KOA/KhOpenApi change-comparison instructions do not apply because this task applies no application code repair.
