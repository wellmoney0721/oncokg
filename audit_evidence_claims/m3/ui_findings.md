# Round 3 page-script verification

Reviewed current HEAD `574097f67e0719c32bfdc0526133e649b1864993`, including `git diff HEAD~1 HEAD -- web/try.html`. All files created by this sub-review are under `audit_evidence_claims/m3/`; no tracked file or database row was edited. Fixture response mutation below is in JavaScript memory. Fresh Engine reads use a SQLite read-only connection.

## Outcome

Every prior UI reproduction is **FIXED**, including m2b R2's unavailable sponsor count, boolean score rendering, precision loss, and the module-introduction wording. No new page-script blocker was reproduced. The separate names and database reviews determine the overall verdict; this is not approval of the linker.

## Every previous UI finding

| Finding and exact input/sequence | Disposition | Current evidence |
|---|---|---|
| m1 B2, collaborator labelled lead: `NCT00200395`, reverse `ORG:genentech` | **FIXED** | The incoming Genentech group is `이 임상의 협력 기관 (collaborator)`; Montefiore is `이 임상의 책임 주관 기관 (lead sponsor)`. Reverse groups distinguish both roles. `web/try.html:142-149`; `ui_harness_results.json` -> `real`. |
| m1 B3, Investigator labelled institution: `NCT00754364` | **FIXED** | Armando Santoro Md is shown under `이 임상의 책임 주관 연구자 (lead sponsor)`. `web/try.html:143,148`; same artifact. |
| Missing/unknown sponsor role defaults to collaborator | **FIXED** | `null`, empty string and `not_a_known_role` use `역할 기록 없음` in both directions, for Company/Investigator/Other fixtures. `web/try.html:147-149`; `ui_regressions.json` -> `missingRoleChecks`. |
| m1 S1 generic “most evidence” wording, especially `MONDO_0005233` | **FIXED** | Per-group wording says latest start date, association score, graph trial count, sponsor trial count or name as applicable. Actual ordering is independently checked by the data sub-review. `web/try.html:148-158,231-235`; `ui_harness_results.json`. |
| m1 S2 silent ring cut: `CHEMBL1201438`, Disease, AstraZeneca | **FIXED** | ALDESLEUKIN says 22 drawn of 25; Disease says 39 of 3,074 plus each 30-item list notice; AstraZeneca says 41 of 145. No page promise that 40 is a hard cap. `web/try.html:191-204,233`; `ui_harness_results.json` -> `real`. |
| m1 S3 stale trail after osimertinib -> EGFR -> `Mvasi`, `unknown-m1-entity`, server/network failure | **FIXED** | Array and markup are empty after each terminal state; invoking the obsolete back handler does not throw. Back navigation after success works. During a pending fresh-root request old buttons can remain visible, but the cleared array guard ignores them. `web/try.html:213-216,243-244`; `ui_harness_results.json` -> `failureVariants`, `backAfterSuccess`, `pendingNewLookup`. |
| m1 S4 out-of-order EGFR/KRAS responses and concurrent duplicate EGFR requests | **FIXED** | Completing KRAS first leaves KRAS; stale EGFR success/error cannot replace it. Duplicate concurrent EGFR requests yield one trail entry. `web/try.html:211-214`; `ui_harness_results.json` -> `reverseResponses`, `staleError`, `doubleClick`. |
| m1 S5 silent ambiguity: `Roche`, `MET`, `osimertinib EGFR`, `EGFR osimertinib`; refused span in `Mvasi and bevacizumab` | **FIXED for those exact inputs** | Selected reading and the other entity/refused span are displayed. `web/try.html:222-226`; `ui_harness_results.json` -> `real`. Embedded multi-ID alias behavior belongs to the name sub-review. |
| m1 S6 action/class specificity: ALDESLEUKIN AGONIST; BINDING AGENT; sponsor classes | **FIXED** | Action gloss and stored code survive; INDUSTRY, NIH, FED, OTHER_GOV, NETWORK, OTHER and UNKNOWN class codes remain visible. `web/try.html:162-176`; `ui_harness_results.json` -> `details`, `real.CHEMBL1201438`. The old synthetic class fixture supplies only a sort weight, so current output correctly says count unrecorded; real payloads supply `evidence_trials`. |
| m1 S7 omitted Trial centre start; sponsor -> Drug global count/max phase; zero-trial Drug centre | **FIXED** | `NCT00200395` shows `시작 2003-07-02`; AstraZeneca -> osimertinib shows sponsor count 14 and graph count 79/approval; `CHEMBL925` centre shows count 0. `web/try.html:173-174,228-229`; `ui_harness_results.json` -> `real`. |
| Unsafe `javascript:`/`data:` map links, hostile label/title/id markup | **FIXED for exercised map paths** | Both centre and list anchors apply `safeUrl`. Host-prefix, credential and backslash spoof URLs are rejected; exact registry URLs remain clickable. Tested labels, titles, node/edge IDs and alternative fields stay escaped. `web/try.html:180,199,221-235`; `ui_harness_results.json` -> `injectionHTML`, `urlChecks`; `ui_regressions.json` -> `markupChecks`. This is generated-markup verification, not a browser-executed exploit test. |
| Unknown node-type tooltip `undefined` | **FIXED** | Fixture type Other and relation `NEWREL|in` use raw fallbacks; no undefined tooltip. `web/try.html:158,199,227`; `ui_regressions.json` -> `markupChecks`. |
| m1 module introduction “All three” after four boxes | **FIXED** | `src/app.py:11` says `All of them`. |
| m2b module introduction “everything” despite capped output | **FIXED** | `src/app.py:5` explicitly says `a capped list per relation`. |
| m2b R2 `null`, `[]`, `{broken` sponsor edge props; requests `CHEMBL1201438` and `ORG:alaunos` | **FIXED** | All six fresh API payloads render `책임 주관한 임상 수 기록 없음`; none render false `0건`. Reverse Drug view still shows independent graph count 11 and approval. `web/try.html:173`; `db_missing_sponsor_count.json`, `ui_missing_sponsor_count.json`. `{}` control is also unrecorded. |
| m2b boolean-score render exception (`score:true`/false) | **FIXED** | Current API fixture supplies null for boolean scores. Even manually supplying either boolean to the current page produces no exception or stuck-loading state. `web/try.html:176`; `db_score_fixture.json`, `ui_regressions.json`, `ui_m3_checks.json` -> `booleanControls`. |
| m2b score precision loss: `EGFR`, `KRAS` | **FIXED** | Both detail and SVG tooltip retain `0.8883707400322897` and `0.8337881598550857`; `.toFixed(3)` is gone. `web/try.html:176`; `ui_regressions.json` -> `precision`. |
| m2b render exceptions outside fetch catch | **FIXED for all four UI entry points** | With a response whose Trial centre has `props.phases="PHASE2"`, form submit, node click, back click and example click each show `그리지 못했습니다`, clear the trail, and allow subsequent KRAS success. `web/try.html:238-248`; `ui_m3_checks.json` -> `renderErrors`. |

## Additional regression checks

- Executed the entire current script, not archived HTML. `ui_collect.py` produced **16** fresh real map payloads. Existing m2b harnesses were copied, paths changed to m3, and rerun against these payloads.
- The **36** actual examples from sections 1–4 completed Engine calls and rendered without errors: **13** resolver, **7** questions, **9** prose checks, **7** structured checks. `ui_demos_inputs.json`, `ui_demos_responses.json`, `ui_demos_results.json` preserve inputs/responses/markup. Name sub-review separately checks answer semantics and pre-repair parity.
- `ui_m3_checks.js` also dispatches the actual click callbacks for all **36** examples and **6** map examples, asserting dispatched requests and successful rendering. Structured JSON is compared semantically because the click handler intentionally pretty-prints it; whitespace differences are not failures.
- R2 controls set `weight=123` while `evidence_trials` is null, 0, 1 or 14. Display is respectively unrecorded, 0, 1 and 14; no fallback weight leaks into the value. This verifies missing and measured-zero states remain distinct.
- A stale malformed Trial response completed after a newer KRAS result is discarded before rendering, leaving the KRAS map intact. No realistic request-order regression was reproduced in `exploreSafe`.
- Empty/whitespace-only map form submission issues no request and retains the previous view. This matches prior behavior and is not a newly introduced error. Server empty-input behavior is independently covered by the root HTTP run.

## Browser limitation

Current browser discovery returned `browsers=[]` and `The browser access host is unavailable`. Selecting the sole returned Chrome window via the supported native API was rejected with `Computer Use was not approved to use Google Chrome`. No browser input was performed and no controls were bypassed. Consequently this sub-review verifies produced strings, callback/state behavior and fresh backend responses, not browser layout or browser-executed XSS. The error strings are recorded in `ui_m3_checks.json` -> `browser`.

## Reproduction commands

Run from repository root. Python commands disable bytecode output. The missing-count script consumes the data review's fresh same-schema JSON.

```text
python -B audit_evidence_claims/m3/ui_collect.py
node audit_evidence_claims/m3/ui_harness.js
node audit_evidence_claims/m3/ui_regressions.js
node audit_evidence_claims/m3/ui_demos.js export
python -B audit_evidence_claims/m3/ui_demos_collect.py
node audit_evidence_claims/m3/ui_demos.js
node audit_evidence_claims/m3/ui_missing_sponsor_count.js
node audit_evidence_claims/m3/ui_m3_checks.js
```
