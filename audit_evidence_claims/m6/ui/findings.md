# Round 6 page-script and demo review

Reviewed HEAD `b7a00f9c14e5ee0447601795d0c0f4535c2f0376`. `web/try.html` and `src/app.py` are unchanged from round 5 (`git diff 514929c...HEAD -- web/try.html src/app.py` is empty). All executions nevertheless use fresh current Engine responses. Scratch files are confined to `audit_evidence_claims/m6/ui/`; production SQLite is read-only in the collection scripts.

**Every prior UI defect is FIXED for its original reproduction except the unchanged blank-form qualification. All 36 demo responses remain identical. The current page still displays originator maps for the residual linker bypasses independently identified by the names review.** This is not a new renderer defect: it confirms the externally visible consequence of the current resolver failure.

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

## Current design attack reaches the actual page script

[Fresh Engine inputs and full payloads](boundary_render_inputs.json) and [executed page outputs](boundary_render_results.json) retain these exact inputs:

| Input | Rendered centre | Refusal disclosure | Retained list rows |
|---|---|---|---|
| `bevacizumab - awwb/osimertinib` | BEVACIZUMAB / CHEMBL1201583 | Absent | 61 |
| `bevacizumab - awwb& osimertinib` | BEVACIZUMAB / CHEMBL1201583 | Absent | 61 |
| `bevacizumab-awwb+ osimertinib` | BEVACIZUMAB / CHEMBL1201583 | Absent | 61 |
| `bevacizumab-awwb& osimertinib` | BEVACIZUMAB / CHEMBL1201583 | Absent | 61 |
| `bevacizumab-awwb + osimertinib` | OSIMERTINIB / CHEMBL3353410 | Present for refused product | 62 |
| `bevacizumab-awwb & osimertinib` | OSIMERTINIB / CHEMBL3353410 | Present for refused product | 62 |

Each replay submits the current form callback, checks the dispatched request text, supplies a freshly collected Engine response, and executes the whole current page script. The first four produce a real SVG string, a BEVACIZUMAB centre header, the centre in the trail, and its relation lists. The raw HTML is retained. This is VM evidence, not a claim of painted browser pixels or independently gathered HTTP evidence; the parent's actual HTTP confirmation is separate.

The renderer trusts `center` after `web/try.html:215-217` refusal/not-found checks, then emits that centre at `227-236`. Thus no downstream UI guard masks the faulty positive entity. Linker cause is outside the renderer; see the names sub-review for `src/query.py:140-153,174-198,207-233` and exact resolver/QA contrasts. Source-backed details for the accepted molecule are internally correct; selection of that molecule violates the product-refusal guarantee.

## Demo, boundary and QA verification

- Re-extracted all EX1-EX4 arrays from the current page: **36** examples (13 resolver, 7 QA, 9 prose-check, 7 structured-check). Current Engine calls return **0 errors**, and all 36 forms render without UI errors. [Inputs](ui_demos_inputs.json), [fresh responses](ui_demos_responses.json), [render results](ui_demos_results.json).
- Invoked **36** actual example click callbacks plus **6** map example callbacks. Four malformed-render routes (form/node/trail/example) clear/recover; the stale malformed response is ignored. [Callbacks and error routes](ui_m3_checks.json).
- Complete fresh demo response structures are **36/36 identical to m5**; no changed refused metadata, evidence, intent, answer or check. [Comparison](ui_demo_compare.json).
- Built **16** fresh maps. All **24/24** aggregate assertions pass, including equality of five shared root HTTP responses with direct Engine maps and equality of served HTML bytes with current `web/try.html`. [Maps](ui_real_maps.json), [assertions](ui_assertions.json). The root HTTP artifacts are `../http_results.json` and `../served_try.html`.
- Reused the independent m5 **27-input boundary probe**. `liposomal and nanoparticle formulation of doxorubicin` and its plural/other qualifier variants now refuse; the exact principal map has no centre and QA returns 0 evidence. Comma/semicolon/fullwidth-comma salt fragments now select the named parent, while complete salt aliases still select salts. The mixed `Erlotinib, hydrochloride biosimilar bevacizumab` selects ERLOTINIB / CHEMBL553 and discloses the separately refused item. [Fresh full probe](ui_boundary_probe.json). These exact M5-B2/M5-S1 reproductions are **FIXED**; they do not certify all separator placements.
- Fresh missing-sponsor-count fixture rendering uses `../db/db_missing_sponsor_count.json`, not prior-round payloads. Six null/list/broken-object endpoint payloads still say count not recorded and never factual zero. [Rendered fixture](ui_missing_sponsor_count.json).

## Limits and integrity

These runs execute the entire current page script in a Node VM with controlled DOM/fetch stubs. They verify generated markup, callbacks, state and asynchronous completion, not browser layout, paint or browser-executed XSS. No actual browser was used by this sub-review. Dark mode was excluded. Existing page escaping and registry-URL allowlist pass the reused malicious payloads; no new script-injection path was found.

Old trail markup may remain visible while a new root lookup is pending, but the obsolete callback is guarded and all terminal states clear it. Empty/whitespace submissions still retain the previous view (NOT FIXED, unchanged usability qualification). Those facts do not hide the reproduced product-originator bypass.

The [adaptation manifest](adaptation_manifest.json) records prior scripts and transformations; [execution manifest](execution_manifest.json) records exits and timings. [Source manifest](source_manifest.json) pins current files. Only output/read locations and the demo comparison baseline were changed in reused scripts. The independent 27-case probe changes its root locator to `Path.cwd()` because this round adds the `ui/` subdirectory. No tracked files, previous evidence or production database were edited.

## Reproduce

From repository root, after `../db/db_missing_sponsor_count.json`, `../http_results.json` and `../served_try.html` exist:

```text
python -B audit_evidence_claims/m6/ui/replay.py
python -B audit_evidence_claims/m6/ui/replay_supplement.py
python -B audit_evidence_claims/m6/ui/ui_assertions.py
python -B audit_evidence_claims/m6/ui/boundary_render_inputs.py
node audit_evidence_claims/m6/ui/boundary_render.js
```
