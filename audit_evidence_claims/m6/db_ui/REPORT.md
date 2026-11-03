# Round 6: database, page-script, demos and standards

Reviewed HEAD `b7a00f9`. **All previously repaired DB/UI reproductions remain FIXED.** The blank-submit and Infinity qualifications remain NOT FIXED, with the same failure behavior as before. No new live-edge, direction, stored-value or generated-markup defect was found in these replays. A new refused-product originator leak was independently confirmed during source review; it is a specification blocker, detailed below and sent to the primary reviewer for actual CLI HTTP confirmation.

## Method and results

The m1, m2b, m3, m4 and m5 report dispositions were inspected. Six existing m5 DB reproducers and existing UI collectors/harnesses/assertions were reused in this directory. Adjustments are limited to output paths, the extra root-path depth, the primary reviewer's verified `m6/root_checks/` HTTP artifact location, and comparing demonstrations with m5. The original fixtures and expectations remain intact. No tracked file was edited. All fixture mutations are in SQLite memory databases; production queries use a read-only connection. Fixture HTTP servers bind ephemeral port 0 and close in `finally`.

- **6,469/6,469 live centres; 0 mismatches** in **224.7327 seconds**. The independent stored-row oracle checks exact live edge sets, relation/direction/role/type groups, totals, group order, item ranking, stored properties, global trial counts, sponsor counts/classes, action types and scores. **22** centre/relation/direction/neighbour-type/role combinations are covered. [Oracle](db_recheck.py), [results](db_validate.json).
- **19/19 DB assertions pass**, including retired centres and trials, 12 malformed-props requests, missing sponsor counts, boolean/precision/numeric controls and all 1,001 Drug neighbours across three count chunks. [Assertions](db_assertions.json).
- **24/24 UI aggregate assertions pass**. These include five fresh actual-HTTP/direct-Engine payload comparisons and current served-page/worktree equality using the primary reviewer's owned, completed [HTTP run](../root_checks/http_results.json) and [served HTML](../root_checks/served_try.html). Unattributed pre-existing m6-root outputs are excluded. [Assertions](ui_assertions.json).
- All **36** page demonstrations produce fresh Engine responses and render without errors: **13 resolver, 7 QA, 9 prose-check, 7 structured-check**. **36/36 complete response structures equal m5**. All **36 actual demonstration click callbacks plus 6 map callbacks** succeed. [Comparison](ui_demo_compare.json), [fresh responses](ui_demos_responses.json), [callback evidence](ui_m3_checks.json).
- Snapshot: **7 retired nodes, 142 retired edges, 0 self-loops, 0 live edges with retired endpoints**; all six current node types covered. SPONSORS has 3,000 lead and 1,652 collaborator roles, including 43 edges from Investigators. Every stored props value is a valid JSON object; all 3,000 stored URLs use the registry HTTPS prefix. DB SHA-256 is `7341c5a7089731f67356da5a588b269d4b69e8e6c4c054acf19aa4ef2837b529`. [Facts](db_snapshot_facts.json).

## Earlier finding dispositions

Repeated later-round findings are grouped by their original identity; each cited reproduction was rerun against current HEAD.

| Prior finding and exact reproduction | Disposition | Fresh evidence and current source |
|---|---|---|
| M1-B2 collaborator labelled lead: `NCT00200395`, reverse `ORG:genentech` | **FIXED** | Montefiore is lead; Genentech is collaborator; reverse roles remain separate. `src/app.py:137,160-169`; `web/try.html:142-149`; [DB](db_validate.json), [render](ui_harness_results.json). |
| M1-B3 Investigator institution wording: `NCT00754364`, reverse `ORG:armandosantoromd` | **FIXED** | Armando Santoro Md receives `책임 주관 연구자 (lead sponsor)`. `web/try.html:143,148`; [DB](db_validate.json), [render](ui_harness_results.json). |
| M1-B4 retired centre by name: in-memory retirement of `CHEMBL3353410`; then `osimertinib`, its ID and `EGFR` | **FIXED** | Name and ID yield not_found; EGFR excludes the retired neighbour. `src/app.py:115-118`; [real-handler fixture](db_retired_center.json). |
| M1 retired Trial count: live D, retired T, live T-EVALUATES-D and D-ACTS_ON-X | **FIXED** | D centre count and X's D neighbour count/weight are 0; retired T excluded. `src/app.py:129-132,139,174`; [fixture](db_fixtures.json). |
| M1-S1 order/wording; later equal-weight A-Z repair: `MONDO_0005233` | **FIXED** | Trials use start date; associated Targets use scores; unweighted/equal-weight labels use A-Z. Each group states its actual order. `src/app.py:141-170`; `web/try.html:148-158,231-235`; [oracle](db_validate.json), [render](ui_harness_results.json). |
| M1-S2 silent ring cuts: `CHEMBL1201438`, Disease, AstraZeneca | **FIXED** | Rendered notices are 22/25, 39/3,074 and 41/145; cut lists say 30 retained. No nonempty group lost in these maps. MAX=40 is a soft target, not a promised hard cap. `web/try.html:191-204,233`; [render](ui_harness_results.json). |
| M1-S3 stale trail: osimertinib -> EGFR -> Mvasi / unknown / server error / network error, then old back callback | **FIXED** | Trail state and markup clear in all terminal states; obsolete callback harmless; ordinary back works. `web/try.html:213-216,243-244`; [controlled callbacks](ui_harness_results.json). |
| M1-S4 reply ordering and duplicates: EGFR/KRAS completed in reverse; concurrent duplicate EGFR | **FIXED** | KRAS stays, stale success/error ignored, duplicate leaves one trail entry. `web/try.html:211-214`; [controlled completions](ui_harness_results.json). |
| M1-S5 identity disclosure: `Roche`, `MET`, `osimertinib EGFR`, reversal, `Mvasi and bevacizumab` | **FIXED for exact inputs** | Chosen reading and other identities/refused component are displayed. Stored FOLIC ACID/METFORMIN collisions remain disclosed. `src/app.py:95-114`; `web/try.html:222-226`; [render](ui_harness_results.json). Embedded multi-ID alias data replay belongs to the names review. |
| M1-S6 action/class detail: AGONIST, BINDING AGENT, sponsor codes | **FIXED** | Specific gloss plus original action code; INDUSTRY/NIH/FED/OTHER_GOV/NETWORK/OTHER/UNKNOWN preserved. `web/try.html:162-176`; [render](ui_harness_results.json). |
| M1-S7 omitted values: Trial start; sponsor-to-Drug global count/phase; zero-trial Drug | **FIXED** | `NCT00200395` start `2003-07-02`; AstraZeneca -> osimertinib sponsor count 14, global count 79, APPROVAL; `CHEMBL925` count 0. `src/app.py:138-149,171-177`; `web/try.html:173-174,228-229`; [DB](db_validate.json), [UI](ui_harness_results.json). |
| M1-S8 malformed props: node D / edge A `null`, `[]`, `{broken` | **FIXED** | All 12 original requests return 200, as do all six restored controls. `_obj` treats these as empty objects. `src/app.py:135,171,211-217`; [fixture](db_fixtures.json). |
| M1 URL/markup qualification: javascript/data URLs, hostile labels/titles/node IDs/edge IDs/alternatives | **FIXED for exercised map paths** | Registry HTTPS allowlist rejects tested scheme, host-prefix, credential and backslash spoofs. HTML/SVG text and attributes escape payloads. `web/try.html:104,180,199,221-235`; [payloads](ui_harness_results.json), [assertions](ui_assertions.json). Browser execution is not claimed. |
| M1 unknown-type tooltip: synthetic Other / NEWREL | **FIXED** | Raw fallback type/relation preserved without undefined. `web/try.html:158,199,227`; [assertions](ui_regressions.json). |
| M1/M2b docstring All three / everything claims | **FIXED** | `All of them` and `a capped list per relation` at `src/app.py:5-11`; README command lines remain accurate at `README.md:566` and `README.ko.md:387`. |
| M2b-R2 unrecorded sponsor count: `ORG:alaunos\|SPONSORS_TRIAL_OF\|CHEMBL1201438\|` props `null`, `[]`, `{broken`, `{}`, both endpoints | **FIXED** | API gives null with zero sorting weight; UI says `기록 없음`, not factual 0. Original recorded 1 stays 1; explicit numeric 0 renders 0. `src/app.py:141-146`; `web/try.html:173`; [fixture](db_missing_sponsor_count.json), [render](ui_missing_sponsor_count.json). |
| M2b missing/unknown SPONSORS role, both directions and node types | **FIXED** | All eight DB fixture variants return 200. Thirty UI role checks show `역할 기록 없음` for unknown roles; never infer collaborator. `src/app.py:137,162-169`; `web/try.html:147-149`; [DB](db_role_fallback.json), [UI](ui_regressions.json). |
| M2b boolean association scores and rounded precision | **FIXED** | True/false API scores become null/weight 0; injected UI booleans do not throw. Exact `0.8883707400322897` and `0.8337881598550857` preserved. `src/app.py:152-155,207-208`; `web/try.html:176`; [DB](db_score_fixture.json), [UI](ui_regressions.json). |
| M2b render error escape: Trial `props.phases='PHASE2'`, four entry points | **FIXED** | Form/node/trail/example display the caught rendering error, clear trail and recover; stale malformed reply discarded. `web/try.html:238-248`; [UI](ui_m3_checks.json). |
| M3-M5 Infinity numeric qualification | **NOT FIXED — unchanged, failure closed** | `_number` accepts +/-Infinity; `allow_nan=False` yields controlled HTTP 400, with no invalid numeric map. None in snapshot. `src/app.py:207-208,264-269`; [fixture](db_numeric_fixture.json). |
| M3-M5 empty/whitespace map form | **NOT FIXED — unchanged usability qualification** | Sends no request and retains previous view. `web/try.html:241`; [UI](ui_m3_checks.json). |

Silent text truncation and raw request-shape errors are replayed by the primary HTTP review. Lowercase IDs, Investigator names, embedded alias alternatives and all refusal findings are covered by the independent names review. These are not implicitly certified by this DB/UI table.

## Fresh blocker independently confirmed

**`bevacizumab - awwb/osimertinib` draws BEVACIZUMAB / CHEMBL1201583 with 122 trials and no refusal.** The same Engine's resolver splits it into `bevacizumab - awwb: BLOCKED_DISTINCT_PRODUCT` and `osimertinib: EXACT / CHEMBL3353410`. `bevacizumab - awwb/foo` has the same originator leak. The control `bevacizumab - awwb/ osimertinib` correctly refuses the qualified first component and selects only osimertinib. [Reproducer](interior_separator_probe.py), [raw results](interior_separator_probe.json).

`src/query.py:143-154` handles slash/pipe only at the ends of a whitespace token. Interior `awwb/osimertinib` survives unsplit; the anchored suffix guard misses it, and the accepted bare `bevacizumab` token at `212-236` becomes the originator. This violates the current explicit glued-separator design. `bevacizumab - awwb|osimertinib` also leaks, although the resolver itself likewise misses the pipe, so the slash case is the strongest independent refusal comparison. The primary report supplies actual server HTTP and QA confirmation.

## Limits, integrity and reproduction

UI scripts execute the current entire page script in a Node VM with controlled DOM/fetch stubs. This verifies generated markup, event handlers, asynchronous sequencing and output data, not browser paint/layout or browser-executed XSS. The current stored data contain no self-loops or unknown node types; the latter uses a synthetic UI fixture. Positive/negative Infinity is a controlled failure, not a drawn wrong value. No application model call was made; `Engine.ask` uses `use_llm=False` (`src/app.py:180-181`). The application itself opens SQLite read/write, so read-only guarantees here are path/integrity evidence, not a global SQLite permission guarantee.

Replay commands are preserved in [fixture_runs.json](fixture_runs.json) and [ui_runs.json](ui_runs.json). Additional commands:

```text
python -B audit_evidence_claims/m6/db_ui/db_recheck.py
python -B audit_evidence_claims/m6/db_ui/db_assertions.py
node audit_evidence_claims/m6/db_ui/ui_missing_sponsor_count.js
python -B audit_evidence_claims/m6/db_ui/ui_assertions.py
python -B audit_evidence_claims/m6/db_ui/interior_separator_probe.py
```

**Standards axis: 0 documented violations**, separate from the originator-leak specification blocker. [Standards review](standards_findings.md).
