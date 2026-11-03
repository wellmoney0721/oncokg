# s4 faithful claims, rendering, docs, and standards

Reviewed HEAD `8adf2dd`. Eight historical faithful scripts were executed against current code: original s1 and s2 main probes, s2 additional and dictionary probes, and their four s3 replay sources. Only output destinations changed. `replay_manifest.json` records every source, execution exit code, and input comparison; all eight exited 0. The old hardcoded `commit` value inside inherited result payloads is historical metadata, not the revision executed. Current HEAD is recorded separately in the manifest. No tracked file was edited, and graph writes were confined to the original in-memory empty-phase fixture. All source connections were query-only and Python bytecode was disabled.

## Standards

No documented standards violation identified. `git ls-files '*AGENTS.md' '*STANDARDS*' '*CONTRIBUTING*' '*issue-tracker*'` returns no files. The supplied user instructions require evidence-based conclusions and no tracked changes. This review follows those constraints. No code repair was performed, so the conditional request to show old/new code with Kiwoom API references does not apply to this read-only OncoKG review. No issue-tracker setup was made because it would exceed the requested scratch-only review.

## BLOCKERS

None identified in this C/E/F slice. No tested faithful rendering introduced an unsupported fact or model-typed answer text.

## SHOULD FIX

None identified. The s3 alias/documentation finding is FIXED by the new cardinality check and corresponding wording.

## Historical findings: FIXED / NOT FIXED

| Original finding | s4 status and current evidence |
|---|---|
| s1 long sponsor labels rejected | **FIXED.** Both original long labels accept as standalone claims; `historical_input_comparison.json` preserves exact inputs and individual outputs. Full sponsor payload accepts 12/12 by labels and IDs. |
| s1 ALECTINIB HYDROCHLORIDE relation/profile rejected | **FIXED.** Both original claims accept individually. ALK payload accepts 22/22 by labels and IDs. Exact-label branch: `src/structured.py:116-127`. |
| s1 PRKCA exact target label rejected | **FIXED.** Original APRINOCARSEN / PRKCA / ANTISENSE INHIBITOR claim accepts and renders the exact stored action; `s2/faithful_additional_replay.json`. |
| s1 PROFILE described as a live graph edge | **FIXED.** Original profile claim accepts with live-edge count 0; exception documented at `src/structured.py:26-28`, `README.md:453-454`, `README.ko.md:318`. |
| s1 obsolete query/dashboard prose-check descriptions | **FIXED.** `src/query.py:12-18`, `web/template.html:261-267`, `web/dashboard.html:261-267`, and `web/index.html:271-277` describe structured claims and program rendering. |
| s1 English/Korean 22/38 contradiction | **FIXED.** `README.md:537` and `README.ko.md:370` both say 22/38 passed. Out-of-scope prose checker was not rerun. |
| s1/s2 reader-wide no-model-text wording despite diagnostics | **FIXED.** `README.md:461-462` limits the promise to the answer and explicitly identifies separately listed rejected claims as diagnostics. |
| s2 exact-label uniqueness guarantee | **FIXED.** Multiple active same-type labels reject at `src/structured.py:121-124`; independently rerun by identity reviewer. |
| s3 alias / merged-entity documentation mismatch | **FIXED.** `src/structured.py:140-145` refuses a linker alias with more than one distinct candidate ID. Docstring `:30-32`, `README.md:455-457`, and `README.ko.md:318` describe the same singleton alias contract. Constructor collision rejects below. |
| Closed schema cannot preserve every evidence metadata field | **NOT FIXED; unchanged completeness NOTE.** Original drug_type / aliases_known payloads still reject unknown keys. Docs explicitly disclaim completeness; this is not an approval failure. |

## s3 repair: exact input and observed output

The independent identity replay at `../identity/replay_s3/identity_attack_results.json`, which this reviewer read, reconstructs `OncoKG` normally against an in-memory graph after `UPDATE node SET label='Astrazeneca' WHERE id='ORG:genentech'`. No node IDs, edges, or properties are merged. The constructor's `astrazeneca` alias key contains both IDs.

Question: `What is AstraZeneca running in NSCLC?`

```json
{"claims":[{"kind":"relation","relation":"SPONSORS_TRIAL_OF","subject":"AstraZeneca!","object":"osimertinib","evidence":"ORG:astrazeneca|SPONSORS_TRIAL_OF|CHEMBL3353410|","trial_count":14}]}
```

Observed: `resolve` returns `[]` and `'AstraZeneca!' names 2 company nodes; use the id`; `verified=false`, `accepted=[]`, `text=""`, one rejection with the same reason. Replacing the object/evidence/count with `CHEMBL1201583`, `ORG:genentech|SPONSORS_TRIAL_OF|CHEMBL1201583|`, `5` also rejects identically. Thus a citation to either candidate no longer bypasses ambiguous alias refusal. `astra-zeneca` and `ASTRAZENECA?` also reject; exact IDs retain graph-supported claims.

The documented alternatives are node ID, unique graph label of the expected endpoint type, or unambiguous whole alias. A unique literal graph label takes the exact-label branch before the linker; punctuation that routes the string into alias resolution is subject to alias cardinality. This precedence is consistent with the explicitly listed alternatives, and does not reinstate the previous unfiltered `also_matching_ids` path.

## NOTES: faithful demo coverage

Each of the four main-probe executions preserves every original demo/phase/schema input and accepts **73/73 copied-label claims and 73/73 ID claims**. No accepted-count result is inferred from old artifacts. Output dictionaries for additional cases and graph-code distributions exactly match s2 and s3; original s1 action/profile/empty-phase inputs and dictionary values are independently compared in `historical_input_comparison.json`.

| Exact question | Label claims accepted | ID claims accepted |
|---|---:|---:|
| Which companies are developing osimertinib? | 12/12 | 12/12 |
| What trials evaluate Tagrisso? | 24/24 | 24/24 |
| What does osimertinib target? | 1/1 | 1/1 |
| Which drugs act on ALK? | 22/22 | 22/22 |
| What is AstraZeneca running in NSCLC? | 12/12 | 12/12 |
| What is the capital of France? | no evidence; refusal | no evidence; refusal |
| What is osimertinib? | 2/2 | 2/2 |

Long sponsor claim, question `Which companies are developing osimertinib?`:

```json
{"claims":[{"kind":"relation","relation":"SPONSORS_TRIAL_OF","subject":"Second Affiliated Hospital Of Nanchang University","object":"OSIMERTINIB","evidence":"ORG:secondaffiliatedhospitalofnanchanguniversity|SPONSORS_TRIAL_OF|CHEMBL3353410|","trial_count":2}]}
```

Observed `verified=true`, one accepted claim, no rejections; text:

```text
- Second Affiliated Hospital Of Nanchang University is lead sponsor of 2 trial(s) evaluating OSIMERTINIB - a sponsorship, not evidence of developing the drug [ORG:secondaffiliatedhospitalofnanchanguniversity|SPONSORS_TRIAL_OF|CHEMBL3353410|]
```

The other original sponsor uses subject `Tianjin Medical University Cancer Institute And Hospital`, evidence `ORG:tianjinmedicaluniversitycancerinstituteandhospital|SPONSORS_TRIAL_OF|CHEMBL3353410|`, count 2 and the same object: also verified with its own label in otherwise identical sponsorship wording. Full standalone inputs/outputs are in `historical_input_comparison.json`.

Salt claim, question `Which drugs act on ALK?`:

```json
{"claims":[{"kind":"relation","relation":"ACTS_ON","subject":"ALECTINIB HYDROCHLORIDE","object":"ALK","evidence":"CHEMBL3707320|ACTS_ON|ENSG00000171094|CHEMBL3707320","action":"INHIBITOR"}]}
```

Observed `verified=true`; text `- ALECTINIB HYDROCHLORIDE acts on ALK (inhibitor) [CHEMBL3707320|ACTS_ON|ENSG00000171094|CHEMBL3707320]`. The separate drug claim `{"kind":"drug","drug":"ALECTINIB HYDROCHLORIDE","evidence":"CHEMBL3707320|ACTS_ON|ENSG00000171094|CHEMBL3707320","trials_in_graph":1,"max_stage":"APPROVAL"}` also accepts and renders `maximum clinical stage APPROVAL; 1 NSCLC trial(s) in this graph`.

Action input, question `What does aprinocarsen target?`:

```json
{"claims":[{"kind":"relation","relation":"ACTS_ON","subject":"APRINOCARSEN","object":"PRKCA","evidence":"CHEMBL2108287|ACTS_ON|ENSG00000154229|CHEMBL2108287","action":"ANTISENSE INHIBITOR"}]}
```

Observed `verified=true`; text `- APRINOCARSEN acts on PRKCA (antisense inhibitor) [CHEMBL2108287|ACTS_ON|ENSG00000154229|CHEMBL2108287]`. Changing only action to `INHIBITOR` returns `verified=false`, no accepted claims, empty text, reason `the graph gives the action as ANTISENSE INHIBITOR, not INHIBITOR`. Both cases with object `ENSG00000154229` preserve the same acceptance/rejection distinction. All four original inputs were replayed.

Multi-phase input, question `What trials evaluate BEXAROTENE?`:

```json
{"claims":[{"kind":"trial","trial":"NCT00153842","evidence":"NCT00153842|EVALUATES|CHEMBL1023|NCT00153842","phase":["PHASE1","PHASE2"],"status":"TERMINATED"}]}
```

Observed `verified=true`; text `- NCT00153842: phase PHASE1, PHASE2; status TERMINATED [NCT00153842|EVALUATES|CHEMBL1023|NCT00153842]`.

Empty-phase fixture changes only NCT03909334 phases to `[]` in an in-memory copy; exact input:

```json
{"claims":[{"kind":"trial","trial":"NCT03909334","evidence":"NCT03909334|EVALUATES|CHEMBL3353410|NCT03909334","phase":[],"status":"ACTIVE_NOT_RECRUITING"}]}
```

Observed `verified=true`; text `- NCT03909334: no phase given; status ACTIVE_NOT_RECRUITING [NCT03909334|EVALUATES|CHEMBL3353410|NCT03909334]`. This is fixture coverage, not an assertion that this trial lacks phases in persisted data.

The original two-claim PROFILE payload for `What is osimertinib?` (full input in `s2/faithful_additional_replay.json`) accepts with the PROFILE drug fields `max_stage="APPROVAL",trials_in_graph=79`, followed by its EGFR/INHIBITOR relation. The profile line is `- OSIMERTINIB: maximum clinical stage APPROVAL; 79 NSCLC trial(s) in this graph [profile:CHEMBL3353410]`. SQL still finds zero live edge rows with that profile pseudo-ID; this is expressly permitted by the documentation.

Rendering uses graph labels (`src/structured.py:300-302`), stored action (`:306-308`), trial phase/status (`:316-322`) and checked drug values (`:323-329`). Sponsorship line `:311-315` expressly means lead sponsorship rather than development, consistent with `src/graph.py:337-356`. No live `_norm` code collisions, duplicate EVALUATES trial/drug pairs or live labels longer than 120 characters were found. All these checks were re-executed, not read from prior outputs.

Closed-schema omissions remain drug type, alias count, sponsor class, trial title/enrollment, full mechanism descriptions, target/disease associations, ownership and confidence. These are permitted completeness limits (`README.md:467-470`, `README.ko.md:321-322`, `src/structured.py:41-43`, dashboard section 06). `README.md:530-539`, `README.ko.md:365-371`, and `web/try.html:79-90` identify the auxiliary prose check as fallible. Box 3 (`web/try.html:68-71`) describes the answer as program-rendered, and the page footer (`:90`) states the try page does not call a model. No claim about free-prose checker correctness is made by this review.

Spec conclusion for this slice: zero remaining approval failures. Standards conclusion: zero documented violations. Root review owns full-suite execution and final integrated verdict.
