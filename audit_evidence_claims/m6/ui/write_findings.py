from pathlib import Path
import json,hashlib,subprocess
out=Path('audit_evidence_claims/m6/ui')
old=Path('audit_evidence_claims/m5/ui_findings.md').read_text(encoding='utf8')
start=old.index('## Exact prior reproduction dispositions')
end=old.index('## Demo and QA verification')
table=old[start:end]
body='''# Round 6 page-script and demo review

Reviewed HEAD `b7a00f9c14e5ee0447601795d0c0f4535c2f0376`. `web/try.html` and `src/app.py` are unchanged from round 5 (`git diff 514929c...HEAD -- web/try.html src/app.py` is empty). All executions nevertheless use fresh current Engine responses. Scratch files are confined to `audit_evidence_claims/m6/ui/`; production SQLite is read-only in the collection scripts.

**Every prior UI defect is FIXED for its original reproduction except the unchanged blank-form qualification. All 36 demo responses remain identical. The current page still displays originator maps for the residual linker bypasses independently identified by the names review.** This is not a new renderer defect: it confirms the externally visible consequence of the current resolver failure.

'''+table+'''## Current design attack reaches the actual page script

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
'''
(out/'findings.md').write_text(body,encoding='utf8')
manifest={'head':subprocess.check_output(['git','rev-parse','HEAD'],text=True).strip(),'source_sha256':{p:hashlib.sha256(Path(p).read_bytes()).hexdigest() for p in ['web/try.html','src/app.py','src/query.py','src/textrules.py','data/processed/oncokg.sqlite']},'tracked_diff_empty':not bool(subprocess.check_output(['git','diff','--name-only'],text=True).strip())}
(out/'source_manifest.json').write_text(json.dumps(manifest,indent=2),encoding='utf8')
ad=json.loads((out/'adaptation_manifest.json').read_text(encoding='utf8'))
p=Path('audit_evidence_claims/m5/ui_boundary_probe.py')
ad.append({'file':'ui_boundary_probe.py','source':str(p),'source_sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'adapted_sha256':hashlib.sha256((out/p.name).read_bytes()).hexdigest(),'adaptations':['ROOT = OUT.parents[1] to ROOT = Path.cwd()']})
(out/'adaptation_manifest.json').write_text(json.dumps(ad,indent=2),encoding='utf8')
print(json.dumps({'report':str(out/'findings.md'),'head':manifest['head'],'ui_assertions':json.loads((out/'ui_assertions.json').read_text())['passed']}))
