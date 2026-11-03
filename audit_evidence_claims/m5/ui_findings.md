# Round 5 page-script and demo review

Reviewed HEAD `514929c`. Current `web/try.html` and `src/app.py` have no differences from the round-4 review commit `bf436c6`; all executions below nevertheless use fresh HEAD Engine responses. This is the UI sub-review, not the overall product-refusal verdict.

**No new UI or demo blocker reproduced.** All prior UI findings are FIXED for their exact reproductions except the unchanged blank-form usability qualification. Fresh evidence is confined to m5. No application code or production database was modified.

## Exact prior reproduction dispositions

| Prior finding / exact reproduction | Disposition | Fresh evidence and current source |
|---|---|---|
| m1 B2: collaborator labelled trial lead, `NCT00200395`; reverse `ORG:genentech` | **FIXED** | Genentech renders in `이 임상의 협력 기관 (collaborator)`; Montefiore remains the lead. Reverse headings preserve roles. `web/try.html:142-149`; [real headings](ui_harness_results.json). |
| m1 B3: Investigator labelled institution, `NCT00754364` | **FIXED** | Armando Santoro Md renders under `이 임상의 책임 주관 연구자 (lead sponsor)`. `web/try.html:143,148`; [headings](ui_harness_results.json). |
| m2/m2b missing/unknown SPONSORS role defaults to collaborator | **FIXED** | Null, empty and unknown roles say `역할 기록 없음` for both directions and Company/Investigator/Other types; known roles retain their labels. `web/try.html:147-149`; [30 role checks](ui_regressions.json). |
| m1 S1: generic evidence-order wording, `MONDO_0005233` | **FIXED** | Headings distinguish latest start date, association score, graph-trial count, lead-sponsor-trial count and name order. `web/try.html:148-158,231-235`; [fresh rendering](ui_harness_results.json). DB ordering validation is separate. |
| m1 S2: silent ring cut, `CHEMBL1201438`, Disease, AstraZeneca | **FIXED** | Ring notices disclose 22/25, 39/3,074 and 41/145 drawn. Disease lists disclose 30 retained per group. `MAX=40` remains a soft allocation target, not an asserted hard limit. `web/try.html:191-204,233`; [ring notices](ui_harness_results.json). |
| m1 S3: osimertinib → EGFR → Mvasi/not-found/server error/network error; old back callback | **FIXED** | Trail state and markup clear for all four terminal states; obsolete callback is harmless; normal back works. `web/try.html:213-216,243-244`; [controlled callbacks](ui_harness_results.json). |
| m1 S4: EGFR/KRAS reverse completion; concurrent duplicate EGFR | **FIXED** | Latest KRAS stays; stale success and stale network failure are ignored. Concurrent duplicate leaves one trail entry. `web/try.html:211-214`; [controlled requests](ui_harness_results.json). |
| m1 S5: silent reading/alternatives, `Roche`, `MET`, `osimertinib EGFR`, reversed; `Mvasi and bevacizumab` | **FIXED for exact inputs** | Reading, other entity and refusal are shown. Stored FOLIC ACID/METFORMIN alias choices are disclosed rather than hidden. `src/app.py:95-114`; `web/try.html:222-226`; [fresh maps and HTML](ui_harness_results.json). |
| m1 S6: AGONIST/BINDING AGENT and sponsor-class specificity | **FIXED** | Specific Korean gloss and stored action code shown; INDUSTRY, NIH, FED, OTHER_GOV, NETWORK, OTHER and UNKNOWN codes retained. `web/try.html:162-176`; [details](ui_harness_results.json). |
| m1 S7: Trial start; sponsor→Drug global count/phase; zero-trial Drug | **FIXED** | `NCT00200395` shows `시작 2003-07-02`; AstraZeneca→osimertinib shows sponsor count 14, graph count 79 and approval; `CHEMBL925` shows 0. `web/try.html:173-174,228-229`; [rendered details](ui_harness_results.json). |
| m1 URL/markup qualification: hostile labels/titles/node IDs/edge IDs/alternative identities; javascript/data URLs | **FIXED for exercised map paths** | Registry HTTPS allowlist rejects scheme, host-prefix, credential and backslash spoof probes. Text/attribute payloads are escaped in generated HTML/SVG. `web/try.html:104,180,199,221-235`; [payloads](ui_harness_results.json), [assertions](ui_assertions.json). Browser execution is not claimed. |
| m1 unknown-type tooltip, `Other` / `NEWREL` | **FIXED** | Raw fallback type/relation appears without `undefined`. `web/try.html:158,199,227`; [markup assertions](ui_regressions.json). |
| m1/m2b module `All three` / `everything` overclaims | **FIXED** | `All of them` and `a capped list per relation` remain in `src/app.py:5-11`. README command wording remains accurate at `README.md:566`, `README.ko.md:387`. |
| m2b R2 unrecorded sponsor count: `ORG:alaunos\|SPONSORS_TRIAL_OF\|CHEMBL1201438\|`, props `null`, `[]`, `{broken`, both endpoints | **FIXED** | All six fresh in-memory fixture responses render `책임 주관한 임상 수 기록 없음`; no false zero. Zero is displayed only when `evidence_trials` is actually 0. `web/try.html:173`; [fixture render](ui_missing_sponsor_count.json), [zero controls](ui_m3_checks.json). |
| m2b boolean association-score rendering | **FIXED** | Directly injected true/false scores do not throw or leave loading; current API filtering is covered by DB fixtures. `web/try.html:176`; [render checks](ui_regressions.json), [controls](ui_m3_checks.json). |
| m2b score rounding, EGFR/KRAS | **FIXED** | Full values `0.8883707400322897` / `0.8337881598550857` persist in detail and tooltip. `web/try.html:176`; [precision values](ui_regressions.json). |
| m2b render exception escaping catch: Trial `props.phases='PHASE2'` | **FIXED for UI entry points** | Form, node, trail and example routes show `그리지 못했습니다`, clear trail and recover on KRAS. Stale malformed response is discarded. `web/try.html:238-248`; [four routes](ui_m3_checks.json). |
| m3/m4 empty or whitespace map form | **NOT FIXED — unchanged usability qualification** | No request is sent; the previous view remains. This is not a new relation or refusal regression. `web/try.html:241`; [blank-submit check](ui_m3_checks.json). |

## Demo and QA verification

- Re-extracted the actual EX1–EX4 arrays from the current page script: **36** examples, comprising 13 resolver, 7 QA, 9 prose-check and 7 structured-check examples. Current Engine calls return **0 errors**, and all 36 forms render without UI errors. [Inputs](ui_demos_inputs.json), [fresh responses](ui_demos_responses.json), [render results](ui_demos_results.json).
- Invoked all **36** actual example click callbacks and the **6** map example callbacks. All passed, including the Mvasi refusal. [Callbacks](ui_m3_checks.json).
- Compared complete fresh demo responses with recorded m4 responses: **35/36 byte-equivalent data structures**. The sole difference is `What trials evaluate Mvasi?`: refused metadata changes from `evaluate Mvasi` to `What trials evaluate Mvasi`. Intent, answer, checks, and the empty evidence list are unchanged. No demo has acquired an unexpected refusal or changed evidence. [Exact comparison](ui_demo_compare.json).
- Built **16** fresh maps with the actual Engine and read-only SQLite connection. All **24** aggregate assertions pass, including full equality of five shared root HTTP responses with these Engine responses and equality of served HTML bytes with current `web/try.html`. [Map payloads](ui_real_maps.json), [assertions](ui_assertions.json).

## Limits

These runs execute the entire current page script in a Node VM with controlled DOM/fetch stubs. They verify generated markup, event/state handling and asynchronous completion, not browser layout, paint or browser-executed XSS. No browser was used by this sub-review. Any parent browser attempt is separate evidence.

Old trail markup can remain visible while a new root lookup is pending; its callback is guarded and harmless, and all terminal states clear it. This unchanged transient behavior is retained in `pendingNewLookup` in the harness result.

The independent names review covers mixed-input QA, listing-word/qualifier boundaries, valid aliases and arbitrary refusal bypasses. This page-script result cannot certify those linker guarantees.

## Reproduce

Run from the repository root after the fresh DB and HTTP fixture scripts have populated m5:

```text
python -B audit_evidence_claims/m5/ui_collect.py
node audit_evidence_claims/m5/ui_harness.js
node audit_evidence_claims/m5/ui_regressions.js
node audit_evidence_claims/m5/ui_missing_sponsor_count.js
node audit_evidence_claims/m5/ui_demos.js export
python -B audit_evidence_claims/m5/ui_demos_collect.py
node audit_evidence_claims/m5/ui_demos.js
node audit_evidence_claims/m5/ui_m3_checks.js
python -B audit_evidence_claims/m5/ui_demo_compare.py
python -B audit_evidence_claims/m5/ui_assertions.py
```
