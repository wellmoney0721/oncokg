# Round 4 page-script review

Current HEAD: `bf436c6`. The current `web/try.html` and `src/app.py` are unchanged from `574097f`; the page was nevertheless executed again against fresh Engine responses. The diff reviewed for the accumulated repair is `git diff bfcb83d...HEAD -- src/app.py src/query.py web/try.html tests/test_app.py`. Prior findings were read from all three reports, not inferred only from the repair notes.

All prior UI reproductions below are **FIXED** for the exact tested paths. No new page-script blocker was reproduced. This does not certify name resolution: the independent names/QA review covers the new span algorithm.

## Prior findings, rerun on HEAD

| Prior finding / exact reproduction | Result | Current evidence and source |
|---|---|---|
| m1 B2: collaborator labelled trial lead, `NCT00200395`; reverse `ORG:genentech` | **FIXED** | Genentech is in `이 임상의 협력 기관 (collaborator)`; Montefiore is in the lead group. Reverse headings preserve roles. `web/try.html:142-149`; [fresh headings](ui_harness_results.json) → `real`. |
| m1 B3: Investigator described as institution, `NCT00754364` | **FIXED** | Armando Santoro Md appears under `이 임상의 책임 주관 연구자 (lead sponsor)`. `web/try.html:143,148`; same fresh headings. |
| Missing/unknown SPONSORS role defaults to collaborator | **FIXED** | Null, empty and `not_a_known_role` roles say `역할 기록 없음`, for both directions and Company/Investigator/Other types. `web/try.html:147-149`; [role checks](ui_regressions.json) → `missingRoleChecks`. |
| m1 S1: generic “most evidence” wording, `MONDO_0005233` | **FIXED** | Actual sort descriptions distinguish latest start date, association score, graph-trial count, lead-sponsor-trial count and name. `web/try.html:148-158,231-235`. Database agent independently replays ordering. |
| m1 S2: silent ring cuts, `CHEMBL1201438`, Disease, AstraZeneca | **FIXED** | Displays 22/25, 39/3074 and 41/145 drawn respectively. Disease lists each disclose 30 retained. `MAX=40` remains a soft allocation target, not a promise in the UI. `web/try.html:191-204,233`; [ring counts](ui_harness_results.json) → `real`. |
| m1 S3: stale trail after osimertinib → EGFR → `Mvasi`, `unknown-m1-entity`, server error or network error | **FIXED** | Array and rendered trail clear; obsolete back callback is harmless; normal back navigation works. `web/try.html:213-216,243-244`; [controlled outcomes](ui_harness_results.json) → `failureVariants`, `backAfterSuccess`. |
| m1 S4: out-of-order EGFR/KRAS and concurrent duplicate EGFR requests | **FIXED** | Newer KRAS remains; stale success/error cannot replace it. Concurrent duplicates leave one entry. `web/try.html:211-214`; [controlled completions](ui_harness_results.json) → `reverseResponses`, `staleError`, `doubleClick`. |
| m1 S5: silent identities, `Roche`, `MET`, `osimertinib EGFR`, reverse; refusal in `Mvasi and bevacizumab` | **FIXED for these inputs** | Selected reading and alternatives/refusal are disclosed. `web/try.html:222-226`; [fresh map/render pairs](ui_harness_results.json) → `real`. Embedded alias correctness is covered by names review. |
| m1 S6: AGONIST/BINDING AGENT and sponsor-class specificity | **FIXED** | Stored code plus specific Korean gloss survives. INDUSTRY, NIH, FED, OTHER_GOV, NETWORK, OTHER and UNKNOWN codes are visible. `web/try.html:162-176`; [details](ui_harness_results.json) → `details`. |
| m1 S7: missing Trial start, sponsor → Drug global count/phase, zero-trial Drug | **FIXED** | `NCT00200395` shows `시작 2003-07-02`; AstraZeneca → osimertinib shows sponsor count 14 plus graph count 79 and approval; `CHEMBL925` shows 0. `web/try.html:173-174,228-229`; [fresh render](ui_harness_results.json). |
| URL/markup safety qualification, hostile labels/titles/node IDs/edge IDs/alternatives and javascript/data URLs | **FIXED for exercised map paths** | Both map anchors use the registry HTTPS allowlist; scheme/host-prefix/credential/backslash spoofs are rejected, legitimate registry links retained. Tested text and attribute payloads are escaped. `web/try.html:104,180,199,221-235`; [markup](ui_harness_results.json), [assertions](ui_assertions.json). This is generated-markup verification, not browser-executed XSS. |
| Unknown-type tooltip `undefined`, fixture `Other` / `NEWREL` | **FIXED** | Raw type/relation fallbacks remain. `web/try.html:158,199,227`; [markup checks](ui_regressions.json). |
| Module “All three” / “everything” overclaims | **FIXED** | Current introduction says `All of them` and `a capped list per relation`. `src/app.py:5-11`. README command descriptions at `README.md:566`, `README.ko.md:387` remain accurate. |
| m2b R2 unavailable sponsor count: edge `ORG:alaunos|SPONSORS_TRIAL_OF|CHEMBL1201438|`, props `null`, `[]`, `{broken`, both endpoints | **FIXED** | All six fresh fixture payloads render `책임 주관한 임상 수 기록 없음`, no false zero. `{}` also unrecorded; actual 0 displays 0. `web/try.html:173`; [fresh DB-fixture renders](ui_missing_sponsor_count.json), [numeric controls](ui_m3_checks.json). |
| m2b boolean association-score render failure | **FIXED** | Current API filters bool; even injected `score:true` or false does not throw or leave loading. `web/try.html:176`; [direct and full-render checks](ui_regressions.json), [controls](ui_m3_checks.json). |
| m2b undisclosed score precision loss, EGFR/KRAS | **FIXED** | Detail and SVG tooltip retain `0.8883707400322897` / `0.8337881598550857`. `web/try.html:176`; [precision values](ui_regressions.json). |
| m2b render exceptions escape fetch catch: Trial response with `props.phases='PHASE2'` | **FIXED for UI entry points** | Form, node, trail and example callbacks show `그리지 못했습니다`, clear trail and recover on the next KRAS success. A stale malformed response is discarded. `web/try.html:238-248`; [four callback checks](ui_m3_checks.json). |
| m3 unchanged empty/whitespace form behavior | **NOT FIXED / unchanged usability qualification** | Blank form submits no request and retains the prior view, exactly as before. Not a fabricated relation or repair regression. `web/try.html:241`; [blank-submit assertion](ui_m3_checks.json). |

## Additional execution and limits

- Recreated **16** fresh maps using the actual Engine with a read-only SQLite connection. No fixture touched the production database.
- Executed the entire current page script in a Node VM. All **36** actual examples rendered: 13 resolver, 7 QA, 9 prose, 7 structured. Also invoked all 36 real example click callbacks and six map-example callbacks. Engine errors and UI errors: **0**. [Inputs](ui_demos_inputs.json), [fresh responses](ui_demos_responses.json), [renders](ui_demos_results.json), [callbacks](ui_m3_checks.json).
- Compared **5** shared map responses from the root's fresh real HTTP run with the direct Engine payloads; all equal. The served page bytes equal current `web/try.html`. [24 aggregate assertions](ui_assertions.json). This is an exact shared-input comparison; it is not a claim that all 16 maps were independently sent over HTTP by this sub-review.
- Old trail markup may briefly remain while a new root request is pending, but its callback is guarded and cannot throw. Current terminal states clear it. This unchanged transient behavior is disclosed in `ui_harness_results.json` → `pendingNewLookup`.
- This sub-review did not call a browser. VM assertions establish script/state and generated-markup behavior, not browser layout, paint or executed exploits. Any root browser attempt is separate evidence. The old script's hardcoded browser-failure text was removed rather than copied as fresh evidence.
- UI files created or adapted here stay under m4. No tracked files were edited. This is verification only; no source remediation was made.

## Reproduce

From repository root, after the data/root agents' fixture and HTTP scripts:

```text
python -B audit_evidence_claims/m4/ui_prepare.py
python -B audit_evidence_claims/m4/ui_collect.py
node audit_evidence_claims/m4/ui_harness.js
node audit_evidence_claims/m4/ui_regressions.js
node audit_evidence_claims/m4/ui_missing_sponsor_count.js
node audit_evidence_claims/m4/ui_demos.js export
python -B audit_evidence_claims/m4/ui_demos_collect.py
node audit_evidence_claims/m4/ui_demos.js
node audit_evidence_claims/m4/ui_m3_checks.js
python -B audit_evidence_claims/m4/ui_assertions.py
```
