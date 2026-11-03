# Round 19: database, UI, demos and Standards

Reviewed HEAD **`c476d9d559ce5e723c6f5d91fad5e6c3599cfe93`**. **No new graph-membership, direction, stored-value or demo regression found.** Current UI does render the two new originator leaks confirmed by the root reviewer; their causes are name resolution, not rendering. The latest full-element repair fixes the exact previous iodine examples.

## Verification and scope

**24 reused scripts** from m18's cumulative DB/UI suite, plus one new form-callback harness. Original fixture inputs are preserved; output paths point to m19 and the owned CLI port is 9221. [Reuse manifest](reuse_manifest.json), [execution manifest](execution_manifest.json).

- Stored-row oracle: **6,469 live centres, 22 relation/direction/type/role combinations, 0 errors**. Live-edge membership, endpoint direction, metadata, trial counts, totals and ordering agree. Oracle loop 216.251 s; full db_recheck command 219.727 s under overlapping audit work, not an isolated cost benchmark. [Oracle](db_validate.json).
- **19/19 DB assertions**, **24/24 UI assertions**, and **4/4 self-loop/unknown/retirement assertions** pass. Seven DB, eight UI and two final commands exit zero. [DB](db_assertions.json), [UI](ui_assertions.json), [self-loop fixture](self_loop_unknown.json).
- **36/36 page demos** and **six map example callbacks** pass. Responses equal every m7-m18 baseline; QA evidence counts remain **12, 12, 11, 1, 12, 0, 0**. [Comparisons](demo_previous_comparison.json), [renders](ui_demos_results.json), [callbacks](ui_m3_checks.json), [QA counts](ui_demo_compare.json).
- **36/36 original-CLI HTTP demos** return 200 and equal direct Engine responses. Served page bytes equal the worktree. Port **9221 is closed**. Five root HTTP maps also equal their direct map responses. [HTTP](demo_http.json), [lifecycle](demo_http_lifecycle.json), [assertions](ui_assertions.json).

UI checks execute the actual page JavaScript in a Node VM with controlled DOM/fetch stubs. They establish generated markup, exercised state and callbacks, not browser painting or browser-executed XSS. No owned server used port 8765. No model was called. Root reports pytest and isolated cost separately.

## Historical findings: individual dispositions

This table covers non-name/non-cost findings through m18, plus independent isotope corroborations. M2 has no completed report; its partial role/order cases are included. Each current disposition uses fresh evidence, not the historical script's exit code alone. Names and performance have separate worker matrices. [Historical report inventory](historical_report_headings.json), [machine-readable matrix](historical_findings_matrix.json).

| Earlier finding / exact reproduction | Round 19 result and evidence |
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
| M16-B1 exact element-first one-letter inputs: `I-124-labelled trastuzumab`, `trastuzumab labelled with I-124`, `I124 trastuzumab`, `F18 trastuzumab`, `C14 paclitaxel` | **FIXED**. Current and HEAD^ refuse the original unlabelled-originator spellings with zero QA evidence. [Independent stages](adjudication_tracer.json). |
| M16 labelled-product qualification: `89ZrDFO 18-FDG` / `89-ZrDFO 18-FDG`, lutathera/FDG isotope variants | **NOT FIXED**, unchanged nonblocking discrepancy under the explicitly permitted labelled-product exception. All 17 original m16 adjudication inputs rerun. [stages](adjudication_tracer.json). |
| M1-M18 README test-count comments, README.md:565 / README.ko.md:386 | **NOT FIXED**, inherited documentation-only: both say 317 tests. Nearby app descriptions remain accurate. [Standards](STANDARDS.md). |

| M17-B1 punctuation-before-symbol: `trastuzumab labelled-I-124`; `iodine-I-124-labelled trastuzumab`; `trastuzumab labelled with iodine-I-124` | **FIXED**. Every original selected tracer input refuses, with zero trial/sponsor QA evidence; HEAD^ and current both refuse. Adjacent symbol pieces preserve the boundary. `src/query.py:188-197`. [Fresh m17 staged replay](adjudication_tracer.json), [exact main input](independent_boundary.json). |

| M18-B1 independent exact input: `trastuzumab labelled with iodine-124`; `trastuzumab labelled iodine 124` | **FIXED**. Current linker refuses and map has no centre; trial and sponsor QA have zero evidence. HEAD^ draws TRASTUZUMAB with 12/12 QA rows. `src/query.py:156-187`. [Independent stages](independent_boundary.json). |
| M18 synthetic mass-split diagnostics: `trastuzumab labelled-I-1-24`, `trastuzumab labelled-I-12-4`, `trastuzumab labelled-I-(1)(24)` | **NOT FIXED**, unchanged diagnostic qualification, not promoted as natural scientific notation. All three continue to map TRASTUZUMAB with 12/12 QA rows. [Stages](independent_boundary.json). |
| M16-M18 cross-word one-letter qualification: `trastuzumab labelled I 124` | **NOT FIXED**, unchanged previously excluded cross-word diagnostic. The within-word requirement remains separate. [Stages](independent_boundary.json). |


All six live node types and all 22 existing relation combinations are covered. The snapshot has **7 retired nodes, 142 retired edges, zero self-loops and zero live edges with retired endpoints**. PARENT_OF, STUDIES, ASSOCIATED_WITH, EVALUATES, ACTS_ON and role-aware SPONSORS agree with stored endpoints. All **3,000 stored URLs** use registry HTTPS URLs, and all node/edge props are valid JSON objects. [Snapshot](db_snapshot_facts.json), [oracle](db_validate.json). Self-loop behavior is an isolated fixture result.

## New HTTP-to-UI corroboration

The root's independent CLI captures were passed unchanged to the **actual page form submission callback**, then rendered by `exploreSafe`/`explore`. Both `radio-labelled trastuzumab` and `99m-technetium trastuzumab` render a **TRASTUZUMAB / CHEMBL1201585 centre**, an SVG relationship map and a trail entry, without a refusal. The paired `radiolabelled trastuzumab` and `technetium-99m trastuzumab` responses render refusal text, no SVG, and an empty trail. All **22 captured /explore responses** render without errors. This ties the root's name-resolution defects to the displayed map. [Actual generated markup and state](ui_m19_http.json), [harness](ui_m19_http.js), [root HTTP evidence](../root_checks/independent_m19_http.json). It is a VM rendering check, not a real-browser claim.

## Standards

**0 documented-standard violations found.** The fixed point is `4bed79c1f170ebe1efa3d452ce4398cce17b2113`; current HEAD is `c476d9d559ce5e723c6f5d91fad5e6c3599cfe93`. The nonempty reviewed diff is `git diff 4bed79c1f170ebe1efa3d452ce4398cce17b2113...HEAD -- src tests web README.md README.ko.md CODEX_MAP_M1_VERDICT.md`. It changes the isotope helper, its regression test, and repair notes. [Latest diff](review_diff_latest.txt). The cumulative application/UI diff from original `bfcb83d` was also inspected. [App/UI diff](review_diff_app_ui.txt).

`git ls-files '*AGENTS.md' '*CONTRIBUTING.md' '*CODING_STANDARDS.md' 'docs/agents/*'` returns no tracked standards sources. [Inventory](review_diff_standards.txt). The user's supplied instructions govern: evidence-based independent review; no tracked edits; scratch only under m19; fresh FIXED / NOT FIXED dispositions for historical reproductions. The reused harnesses retain original inputs and fixture logic, redirecting only scratch paths and the owned CLI port. [Manifest](reuse_manifest.json).

SQLite mutation fixtures are isolated in memory. The all-node oracle connects with `mode=ro`. Actual page JavaScript runs in a Node VM with controlled DOM/fetch stubs: findings concern generated markup and exercised state, not browser painting or browser-executed XSS. CLI HTTP demos use port 9221 and clean up their process. The application connection is not globally read-only; write claims rely on executed paths and integrity checks. `Engine.ask` explicitly sets `use_llm=False` at `src/app.py:181`.

Issue-tracker setup was not performed because the explicit audit-only/no-tracked-edit scope takes precedence over skill setup guidance. No application code was changed, so the conditional KOA Studio/KhOpenApi original-versus-modified code comparison does not arise.

Inherited README test-count comments still say 317 (`README.md:565`, `README.ko.md:386`); adjacent application descriptions remain accurate. This is a documentation should-fix, not a new documented coding-standard violation. New refusal gaps, if reproduced, belong to the independent specification axis.


## Integrity and reproduction

Database SHA-256 remains **`7341c5a7089731f67356da5a588b269d4b69e8e6c4c054acf19aa4ef2837b529`**. HEAD is unchanged and `git status --short --untracked-files=no` is empty. All scratch outputs stay in this directory. [Before](worker_integrity_before.json), [final](worker_final_checks.json). Full tracked-file hashes are checked by the root reviewer.

Run from the repository root with bytecode disabled; TMP/TEMP/TMPDIR for child processes point to this directory's tmp/. The root HTTP artifacts must exist before run_final.py.

```text
python -B audit_evidence_claims/m19/db_ui/run_db.py
python -B audit_evidence_claims/m19/db_ui/run_ui.py
python -B audit_evidence_claims/m19/db_ui/run_final.py
python -B audit_evidence_claims/m19/db_ui/demo_http.py
python -B audit_evidence_claims/m19/db_ui/self_loop_unknown.py
python -B audit_evidence_claims/m19/db_ui/adjudicate_tracer.py
python -B audit_evidence_claims/m19/db_ui/independent_boundary.py
python -B audit_evidence_claims/m19/db_ui/complete_review.py
node audit_evidence_claims/m19/db_ui/ui_m19_http.js
python -B audit_evidence_claims/m19/db_ui/build_findings.py
```
