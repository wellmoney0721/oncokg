# Round 18: database, UI, demos and Standards

Reviewed HEAD **`4bed79c1f170ebe1efa3d452ce4398cce17b2113`**. **No new DB/UI/demo blocker.** The exact M17 punctuated-isotope leak is repaired. Independent staged checks corroborate the attack review's full-element-name gap: `trastuzumab labelled with iodine-124` still draws unlabelled TRASTUZUMAB. This is a specification defect; it is not a DB relationship/value or documented-standard violation.

## Verification and scope

**23 reused scripts** from m17's cumulative DB/UI suite; all output paths point to m18 and the owned CLI port is 9121. Exact historical fixture inputs and all 36 m17 adjudication cases are preserved. Demo baselines extend through m17. [Source/adaptation manifest](reuse_manifest.json), [execution](execution_manifest.json).

- Stored-row oracle: **6,469 live centres, 22 relation/direction/type/role combinations, 0 errors**. Live-edge membership, endpoint direction, metadata, trial counts, totals and ordering agree. The full DB-recheck command took 237.895 s and overlapped audit work; this is not an isolated cost result. [Oracle](db_validate.json).
- **19/19 DB assertions** and **24/24 UI assertions** pass. Seven DB, eight UI, two final assertion and four supplementary commands exit zero. [DB](db_assertions.json), [UI](ui_assertions.json).
- **36/36 page demos and six map callbacks pass**. Complete demo responses equal every m7-m17 baseline. Original QA evidence counts remain **12, 12, 11, 1, 12, 0, 0**. [Comparisons](demo_previous_comparison.json), [renders](ui_demos_results.json), [callbacks](ui_m3_checks.json), [QA counts](ui_demo_compare.json).
- **36/36 original-CLI HTTP demos** return 200 and exactly match direct Engine responses. Served page bytes equal the worktree. Owned port **9121 is closed**. Five root HTTP maps also equal direct maps. [HTTP](demo_http.json), [lifecycle](demo_http_lifecycle.json), [assertions](ui_assertions.json).
- **4/4** self-loop/unknown-type/retirement checks pass through the real HTTP handler. The self-loop appears once as outgoing; unknown values survive. [Fixture](self_loop_unknown.json).

UI checks execute actual page JavaScript in a Node VM with controlled DOM/fetch stubs. They establish generated markup and exercised state/callbacks, not browser painting or browser-executed XSS. Mutation fixtures use isolated in-memory databases. No owned server used port 8765; no model was called. Root reports pytest and isolated cost separately.

## Historical findings: individual dispositions

The table covers non-name findings from m1-m17, plus independently replayed latest isotope cases. m2 has no completed REPORT; its partial role/order cases are included. Later rounds repeated these fixtures. Other naming and cost findings belong to their respective matrices. Every disposition below is based on fresh current-HEAD evidence. [Historical report inventory](historical_report_headings.json).

| Earlier finding / exact reproduction | Round 18 result and evidence |
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
| M1-M17 README test-count comments, README.md:565 / README.ko.md:386 | **NOT FIXED**, inherited documentation-only: both say 317 tests. Nearby app descriptions remain accurate. [Standards](STANDARDS.md). |

| M17-B1 punctuation-before-symbol: `trastuzumab labelled-I-124`; `iodine-I-124-labelled trastuzumab`; `trastuzumab labelled with iodine-I-124` | **FIXED**. Every original selected tracer input refuses, with zero trial/sponsor QA evidence; HEAD^ still leaks. Adjacent symbol pieces now preserve the boundary. `src/query.py:164-172`. [Fresh m17 staged replay](adjudication_tracer.json), [exact main input](independent_boundary.json). |


All six live node types and all 22 existing relation combinations are covered. The snapshot has **7 retired nodes, 142 retired edges, zero self-loops and zero live edges with retired endpoints**. PARENT_OF, STUDIES, ASSOCIATED_WITH, EVALUATES, ACTS_ON and role-aware SPONSORS agree with stored endpoints. All 3,000 stored URLs are registry HTTPS URLs, and all node/edge props are valid JSON objects. [Snapshot](db_snapshot_facts.json), [oracle](db_validate.json). The self-loop result is a fixture result, not a snapshot claim.

## Standards

**0 documented-standard violations found.** Fixed point `bfcb83d` through current HEAD `4bed79c1f170ebe1efa3d452ce4398cce17b2113`; inspected `git diff bfcb83d...HEAD -- src/app.py web/try.html` and `git show HEAD -- src/query.py tests/test_app.py`. Both diffs are nonempty. [App/UI diff](review_diff_app_ui.txt), [latest patch](review_diff_latest.txt).

`git ls-files '*AGENTS.md' '*CONTRIBUTING.md' '*CODING_STANDARDS.md' 'docs/agents/*'` returns no tracked standards files. [Inventory](review_diff_standards.txt). The user's evidence-based, audit-only instructions govern: no tracked changes, fresh outputs only under m18, and FIXED / NOT FIXED for historical findings. Reused scripts preserve fixture logic and exact historical inputs; manifests record source/adapted hashes. Database mutation fixtures are isolated in-memory copies; the snapshot/oracle connection uses SQLite mode=ro. Node VM UI scope is explicitly limited to generated markup and exercised state/callbacks.

No application code was changed, so the user's conditional KOA Studio/KhOpenApi original-versus-modified code comparison does not arise. Issue-tracker setup was not performed because the explicit audit-only/no-tracked-edit scope takes precedence over skill setup guidance.

The latest patch preserves punctuation boundaries for one-letter isotope symbols, and original m17 examples now refuse. A separate specification gap remains for full element names: `trastuzumab labelled with iodine-124` misses every refusal stage and draws the unlabelled originator. This is a specification finding, not an independent standards violation; the attack reviewer owns its severity. [Independent stages](independent_boundary.json).

Inherited README comments still say 317 tests (`README.md:565`, `README.ko.md:386`); adjacent app descriptions remain accurate. This is a documentation should-fix.


## Independent specification corroboration

The exact m17 gap is **FIXED**: `trastuzumab labelled-I-124` now produces a Refused linker hit, no centre and zero trial/sponsor QA evidence. Current HEAD^ still draws it. All 36 previous independent stage cases were rerun. [m17 replay](adjudication_tracer.json), [exact main input](independent_boundary.json).

**Inherited full-element-name gap:** `trastuzumab labelled with iodine-124` returns resolver CONTAINED_ALIAS plus UNRESOLVED, `_qualified=false`, `_resolver_blocked={}`, `_marked=None`, `_whole_name=None`, and a Drug-only public linker result. The map selects **TRASTUZUMAB / CHEMBL1201585 with 13 trials**; trial and sponsor QA each return **12** rows. Current and HEAD^ both leak. The element-symbol table/checks in `src/query.py:124-128,136-172` do not canonicalize the full name iodine to I. This corroborates the root/attack finding; it is not counted as another blocker. [Fresh stage captures](independent_boundary.json).

Punctuation-split mass forms `trastuzumab labelled-I-1-24` and `trastuzumab labelled-I-12-4` also evade the adjacent-pair scan, while mass-first controls refuse. These synthetic spellings are retained only as diagnostic corroboration, not asserted to be natural scientific notation or a separately promoted defect. One-letter cross-word forms remain outside the stated within-word isotope requirement. A superscript control is encoded with Unicode escapes to preserve exact text through PowerShell, and is refused. Final stage output uses the corrected Unicode literal.

Counterfactuals replace only HEAD^ query.py against current app/rules/data, not the complete historical deployment. No fresh external biomedical claim is made here; the attack review owns primary scientific identity references.

## Integrity and reproduction

`Engine.ask` sets `use_llm=False` (`src/app.py:181`). Snapshot/oracle connections use mode=ro, and mutation fixtures use memory copies. The app handle itself is not globally read-only; no-write claims rely on inspected/executed paths and integrity hashes. DB SHA-256 remains `7341c5a7089731f67356da5a588b269d4b69e8e6c4c054acf19aa4ef2837b529`. [Worker final check](worker_final_checks.json).

Run from repository root with bytecode disabled and TMP/TEMP/TMPDIR under this directory's tmp/. Root HTTP artifacts must exist before run_final.py. All scripts are in this directory:

```text
python -B audit_evidence_claims/m18/db_ui/run_db.py
python -B audit_evidence_claims/m18/db_ui/run_ui.py
python -B audit_evidence_claims/m18/db_ui/run_final.py
python -B audit_evidence_claims/m18/db_ui/demo_http.py
python -B audit_evidence_claims/m18/db_ui/self_loop_unknown.py
python -B audit_evidence_claims/m18/db_ui/adjudicate_tracer.py
python -B audit_evidence_claims/m18/db_ui/independent_boundary.py
python -B audit_evidence_claims/m18/db_ui/complete_review.py
```
