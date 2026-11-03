# Round 12: database, UI, demos and independent adjudication

Reviewed HEAD **`d9260a1ea544cf7bb80415383667784e0aba146a`**. DB, UI and demo replays establish no new defect in those scopes. Independent adjudication **confirms the new originator leak** `[89Z.r]-DFO-daratumumab`; see [adjudication.md](adjudication.md). It is an inherited hole, not a newly introduced regression. All worker-created artifacts stay under `audit_evidence_claims/m12/db_ui/`; no application, tracked or earlier-audit file was edited.

## Reproduction coverage

The **20 reused scripts** are copied from m11's cumulative DB/UI suite. Only output path literals change from m11/db_ui to m12/db_ui, and the owned CLI demo server moves from port 8893 to 8941. Original source baselines and fixture/assertion logic remain intact. Source/adapted hashes are in [reuse_manifest.json](reuse_manifest.json). The historical report inventory is in [historical_report_headings.json](historical_report_headings.json); m2 has no completed REPORT, and its partial role/order work is represented by the cumulative fixtures. Name and cost reproductions belong to the other workers.

- Independent stored-row oracle: **6,469 live centres, 22 relation/direction/type/role combinations, zero errors**. It checks exact live-edge membership, endpoints, stored details, drug counts, totals and ordering. Oracle interval **216.781 s**, overlapping other audit work; this is not an isolated cost measurement. [Oracle](db_validate.json).
- **19/19 DB assertions** pass, including retired rows, malformed props, missing sponsor counts, bool/decimal/Infinity scores, unknown roles and 1,001-drug count chunking across three SQL chunks. Fixtures mutate only in-memory databases. [Assertions](db_assertions.json), [execution](execution.json).
- **24/24 UI assertions** pass using actual page JavaScript, fresh Engine maps, fixture responses and root's current CLI HTTP artifacts. [Assertions](ui_assertions.json), [UI execution](execution_ui_complete.json), [final checks](execution_final.json).
- **All 36 page demos plus six map callbacks** pass; all 36 complete response objects equal m7, m8, m9, m10 and m11. Seven QA evidence counts remain **12, 12, 11, 1, 12, 0, 0**. [Full comparisons](demo_previous_comparison.json), [rendered demos](ui_demos_results.json), [callback checks](ui_m3_checks.json).
- **36/36 original-CLI HTTP demo requests** return 200 and equal direct Engine results. Served page bytes equal `web/try.html`; owned port **8941 is closed**. [HTTP](demo_http.json), [lifecycle](demo_http_lifecycle.json), [status](worker_status.json).
- The reused isolated self-loop/unknown-type/retirement fixture passes **4/4** real-handler checks. A self-loop occurs once, as outgoing, and raw unknown type/relation values survive. [Fixture](self_loop_unknown.json).

UI tests execute actual JavaScript in a Node VM with controlled DOM/fetch stubs. They establish generated markup and state/callback behavior, not browser painting or browser-executed XSS. Original-CLI requests exercise the actual server. No server used port 8765.

## Historical findings: individual dispositions

These are fresh execution dispositions, not inherited test outcomes. The table structure and finding names are reused from m11 for traceability. Name-specific and performance qualifications are in their respective workers' matrices.

| Earlier finding / exact reproduction | Round 12 result and evidence |
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
| M1/M2b silent truncation: "x"*500 + " osimertinib" and "osimertinib " + "x"*600 | **FIXED**. Both exact oversized inputs return 400 with `input is longer than 500 characters`; neither silently draws the retained prefix. `src/app.py:239-243`. [Fresh root HTTP](../root_checks/http_results.json). |
| M1/M2b malformed JSON/list/null/oversized-body parser-error disclosure | **NOT FIXED**, inherited nonblocking qualification. Requests fail closed with 400; list/null bodies still expose `.get` errors and the 20,000-byte body cap can expose JSON parser text. Valid later calls succeed. `src/app.py:236-240,264-269`. [Fresh root HTTP](../root_checks/http_results.json). |

All six live node types and all 22 existing relation combinations are covered. The snapshot has **7 retired nodes, 142 retired edges, zero self-loops and zero live edges with retired endpoints**. PARENT_OF, STUDIES, ASSOCIATED_WITH, EVALUATES, ACTS_ON and role-aware SPONSORS agree with stored endpoints. All 3,000 stored URLs are registry HTTPS URLs, and all node/edge props are valid JSON objects. [Snapshot facts](db_snapshot_facts.json), [oracle facts](db_validate.json). The self-loop result is explicitly a fixture result, not a claim about the snapshot.

## Standards axis

**Zero documented-standards findings.** Reviewed `git diff bfcb83d...HEAD -- src/app.py web/try.html` and `git show HEAD -- src/query.py tests/test_app.py`. No tracked AGENTS.md, CONTRIBUTING.md, CODING_STANDARDS.md or docs/agents/issue-tracker.md was found. The user-supplied evidence-based, audit-only instructions govern. No tracked file was edited, so the conditional request for original/modified code and KOA Studio/KhOpenApi evidence does not apply. Product correctness is assessed independently and fails on the confirmed tracer alias; absence of a standards finding is not approval. [Review record](standards_review.json), [application diff](review_diff_app_ui.txt), [latest diff](review_diff_latest.txt).

## Additional source and integrity checks

README app.py descriptions (`README.md:566`, `README.ko.md:387`) accurately advertise the page. Their adjacent test-count comments still say 317, a documentation-only stale count; the root worker runs the current test suite. The map's cut notices and sorting descriptions match the implementation. Drug count/phase, trial start, action and sponsor class remain visible as stored, with raw codes retained where needed.

`Engine.ask` passes `use_llm=False` (`src/app.py:180-181`). No model was called by these checks. Snapshot reads use SQLite `mode=ro`; fixture mutations stay in memory. The app's own SQLite connection is not globally read-only, so the no-write conclusion is code-path/integrity based. DB SHA-256 is **`7341c5a7089731f67356da5a588b269d4b69e8e6c4c054acf19aa4ef2837b529`**. Global tracked-file integrity is the root report's responsibility.

Run from repository root with bytecode disabled and TMP/TEMP/TMPDIR under this folder's `tmp/`; final UI assertions require root's fresh HTTP artifacts:

```text
python -B audit_evidence_claims/m12/db_ui/run_db.py
python -B audit_evidence_claims/m12/db_ui/run_ui.py
python -B audit_evidence_claims/m12/db_ui/run_final.py
python -B audit_evidence_claims/m12/db_ui/demo_http.py
python -B audit_evidence_claims/m12/db_ui/self_loop_unknown.py
python -B audit_evidence_claims/m12/db_ui/adjudicate_tracer.py
```
