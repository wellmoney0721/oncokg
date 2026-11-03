# Round 10: DB, UI, demos and standards

Reviewed HEAD **`c364c84a289cfc3da5981708db3547ff6c752bde`**. No new blocker established in this worker's scope. All new files are under `audit_evidence_claims/m10/db_ui/`; no application, tracked, or earlier-audit file was edited.

The **19 reused scripts** come from the cumulative m9 DB/UI suite. The only adaptations are the output directory and the demo server port (8894 to 8893). Source and adapted-file SHA-256 hashes and exact paths are in [reuse_manifest.json](reuse_manifest.json). Scripts retain their original fixture and assertion logic. The historical reports m1, m2b, m3, m4, m5, m6, m7, m8 and m9 were checked for this scope; m2's partial role/order work is represented in its carried-forward fixtures. Naming and cost findings are handled by the other round-10 reviewers.

## Results and evidence limits

- Independent stored-row oracle: **6,469 live centres, 22 relation/direction/type/role combinations, zero errors**. Checks cover live-edge membership, endpoint identity, relation grouping, displayed stored values, drug counts, group totals, ordering weights and ordering. Oracle interval **199.623 s**, overlapping other audit work; this is not an isolated cost measurement. [Full result](db_validate.json).
- **19/19 DB assertions** pass. Retired nodes/trials, missing sponsor counts, bool and decimal scores, absent/unknown sponsor roles, malformed properties, and the **1,001-drug / three-chunk** fixture are included. Mutations are confined to in-memory databases. [Assertions](db_assertions.json), [seven-command execution record](execution.json).
- **24/24 UI assertions** pass using the actual page JavaScript, fresh Engine maps, isolated DB fixture outputs and root's fresh original-CLI HTTP responses. [Assertions](ui_assertions.json), [eight-command UI execution record](execution_ui_complete.json).
- All **36 page demos and six map example callbacks** pass; all **36 complete demo response objects equal m7, m8 and m9**, with zero Engine errors. [Previous comparisons](demo_previous_comparison.json), [current responses](ui_demos_responses.json), [render results](ui_demos_results.json), [callbacks](ui_m3_checks.json).
- All **36 original-CLI HTTP demo requests** return **200**, and each full response equals its direct Engine response. Served page bytes equal `web/try.html`; owned port 8893 is closed. [HTTP](demo_http.json), [lifecycle](demo_http_lifecycle.json), [status](worker_status.json).

UI execution uses a Node VM with controlled DOM/fetch stubs. It establishes generated-markup and callback/state behavior, not real-browser painting or browser-executed XSS. Original-CLI HTTP requests exercise the real server. Port 8765 was not used. These conclusions do not require external clinical assumptions.

## Historical findings: current dispositions

| Earlier finding / exact reproduction | Round 10 result and evidence |
|---|---|
| M1-B2: collaborator described as lead; `NCT00200395`, reverse `ORG:genentech` | **FIXED**. Lead and collaborator groups retain separate role-aware labels in both directions. `src/app.py:137,160-169`; `web/try.html:142-149`. [DB](db_validate.json), [rendered UI](ui_harness_results.json). |
| M1-B3: Investigator described as institution; `NCT00754364`, `ORG:armandosantoromd` | **FIXED**. The incoming trial heading says researcher for Investigator. `web/try.html:143,148`. [DB](db_validate.json), [UI](ui_harness_results.json). |
| M1-B4: retire `CHEMBL3353410` in memory, query `osimertinib`, ID and `EGFR` | **FIXED**. Name and ID return not_found; EGFR has no retired neighbour. `src/app.py:83-84,115-123`. [Real-handler fixture](db_retired_center.json). |
| M1: retired Trial still counted for live Drug; retired T -> EVALUATES -> live D, live D -> ACTS_ON -> X | **FIXED**. D centre count and its count/weight under X are zero. `src/app.py:129-132`. [Fixture](db_fixtures.json). |
| M1-S1: misleading most-evidence wording and ordering, Disease | **FIXED**. The page states start-date ordering for Trials, graph counts for Drugs, stored counts for sponsor relations, association scores for Disease/Target, and name ordering for equal weights. All-node oracle agrees. `src/app.py:141-170`; `web/try.html:148-158,231-235`. [Oracle](db_validate.json). |
| M1-S2: silent ring cut; `CHEMBL1201438`, `MONDO_0005233`, AstraZeneca | **FIXED**. Ring counts and list cuts are disclosed. ALDESLEUKIN draws 22/25; Disease draws 39/3,074 with 30 items in each list. Every exercised nonempty group has ring representatives. `web/try.html:191,204,233`. [UI](ui_harness_results.json). |
| M1-S3: stale trail after Mvasi, unknown name, server/network errors | **FIXED**. Terminal states clear trail/buttons; stale back handlers do not throw. `web/try.html:213-216,243-244`. [UI](ui_harness_results.json). |
| M1-S4: reverse response order, duplicate clicks, stale network error | **FIXED**. Latest KRAS remains; duplicate completion yields one trail entry. `web/try.html:211-214`. [UI](ui_harness_results.json). |
| M1-S5: silent reading and alternatives; Roche, MET, `osimertinib EGFR`, `Mvasi and bevacizumab` | **FIXED for disclosure**. Selected reading, additional company/target and refused-span chips are displayed. `web/try.html:222-226`. [UI](ui_harness_results.json). Semantic name resolution is covered by the naming worker. |
| M1-S6: AGONIST/BINDING AGENT gloss and sponsor classes | **FIXED**. Specific Korean glosses retain the stored action/class codes. `web/try.html:161-176`. [UI](ui_harness_results.json). |
| M1-S7: missing Trial start, sponsor-to-drug global count/phase, zero Trial count | **FIXED**. `NCT00200395` displays start 2003-07-02; Drug details retain global count/phase alongside sponsor evidence; `CHEMBL925` displays zero. `src/app.py:172-177`; `web/try.html:173-174,228-229`. [UI](ui_harness_results.json). |
| M1-S8: node/edge props `null`, `[]`, `{broken`; restoration; 1,001-drug count chunking | **FIXED**. Twelve malformed-property requests and all restored requests return 200; all 1,001 Drugs retain count/weight 1. `src/app.py:127-132,211-217`. [Fixtures](db_fixtures.json). |
| M1 URL/script/ID/text injection | **FIXED for exercised generated-markup paths**. Unsafe javascript/data schemes and credential, prefix-host and backslash spoofs are rejected. Labels, IDs and other payload text are escaped; no raw injected image/script or javascript href appears. `web/try.html:104,180,199,221-235`. [UI](ui_regressions.json), [assertions](ui_assertions.json). |
| M1 unknown type Other / relation NEWREL | **FIXED**. Raw fallback values survive; tooltip is not undefined. [UI](ui_regressions.json). |
| M1 module all-three/everything claims | **FIXED**. The module says All of them and a capped list per relation. `src/app.py:5-11`. |
| M2 partial/M2b: missing/unknown SPONSORS role and equal-weight A-Z | **FIXED**. Eight role-property cases return 200; valid roles survive and unspecified roles receive neutral wording. All-node name ordering agrees. [DB](db_role_fallback.json), [UI](ui_regressions.json), [oracle](db_validate.json). |
| M2b-R2: Alaunos/ALDESLEUKIN derived edge props `null`, `[]`, `{broken`, `{}`, both endpoints | **FIXED**. Missing count remains `evidence_trials:null` with sort weight zero and displays not recorded. Actual numeric zero remains zero. `src/app.py:141-146`; `web/try.html:173`. [DB](db_missing_sponsor_count.json), [UI](ui_missing_sponsor_count.json), [zero controls](ui_m3_checks.json). |
| M2b: boolean association score and hidden decimal rounding | **FIXED**. Bool becomes unknown; both directions return 200; exact stored decimal 0.8883707400322897 is retained. [DB](db_score_fixture.json), [UI](ui_regressions.json). |
| M2b/M3: `phases='PHASE2'` render error through form/node/back/example | **FIXED**. All four callbacks catch the error, clear state and recover; stale malformed response is ignored. `web/try.html:239-248`. [Callbacks](ui_m3_checks.json). |
| M3/M4 repeated blank/whitespace submission qualification | **NOT FIXED**, unchanged nonblocker. No request is made; previous view remains. `web/try.html:241`. [Callbacks](ui_m3_checks.json). |
| M3/M4 repeated positive/negative Infinity qualification | **NOT FIXED**, unchanged failure closed. The real handler returns controlled 400; no invalid map value is drawn and snapshot has none. `src/app.py:207-208,264-269`. [Fixture](db_numeric_fixture.json). |

All six live node types and all 22 existing relation/direction/type/role combinations are covered. PARENT_OF, STUDIES, ASSOCIATED_WITH, EVALUATES, ACTS_ON and role-aware SPONSORS match stored endpoints. The snapshot has **7 retired nodes, 142 retired edges, zero self-loops, zero live edges with retired endpoints**. No current self-loop exists to reproduce; the SQL's one-outgoing-item self-loop behavior was inspected, not presented as observed data. All **3,000 URLs** are registry HTTPS URLs, and all node/edge properties are valid JSON objects. [Snapshot facts](db_snapshot_facts.json), [oracle facts](db_validate.json).

The seven original QA demo evidence counts remain **12, 12, 11, 1, 12, 0, 0**. Thirty-six complete demo responses match the previous rounds, so no demo regression was established. This is response-object equality, not merely matching evidence counts.

## Standards axis

**Zero documented-standards findings.** Reviewed `git diff bfcb83d...HEAD -- src/app.py web/try.html` and the latest `src/query.py`/test diff. No tracked AGENTS.md, CONTRIBUTING or CODING standards source exists. The supplied evidence-based and audit-only instructions govern this review; no tracked file was changed. The user requirement to show original and modified code with KOA Studio/KhOpenApi references is conditional on changing code, which did not occur. Product semantics belong to the separate specification review; absence of a standards violation is not approval of them.

## Integrity and reproduction

Snapshot SHA-256 remains **`7341c5a7089731f67356da5a588b269d4b69e8e6c4c054acf19aa4ef2837b529`**. Port 8893 was owned by this worker and closed. DB fixture mutations use in-memory backups; snapshot reads use SQLite `mode=ro`. The application itself does not globally enforce a read-only SQLite handle, so executed-path inspection and the overall audit's before/after hashes support the no-write claim. `Engine.ask` passes `use_llm=False` (`src/app.py:180-181`); no model was called by these paths. [Status](worker_status.json).

Run from repository root with bytecode disabled; run after root's fresh HTTP artifacts exist for the final assertions:

```text
python -B audit_evidence_claims/m10/db_ui/run_db.py
python -B audit_evidence_claims/m10/db_ui/run_ui.py
node audit_evidence_claims/m10/db_ui/ui_missing_sponsor_count.js
python -B audit_evidence_claims/m10/db_ui/ui_assertions.py
python -B audit_evidence_claims/m10/db_ui/demo_http.py
```

The runners set temporary paths under this directory's `tmp/`. `ui_assertions.py` reads root's fresh `m10/root_checks/http_results.json` and `served_try.html`. Cost, naming, full test execution and the overall verdict are intentionally left to the primary report.
