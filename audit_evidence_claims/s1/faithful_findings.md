# Independent C/E/F review, aa5655a

No tracked files were edited. Live graph connections were made query-only. `faithful_probe.py` reproduces the main live-graph usefulness probes and `faithful_results.json` preserves exact questions, payloads, evidence and outputs. Additional outputs are in `faithful_additional.json`, `faithful_graph_dictionary.json`, and `faithful_empty_phase_fixture.json`.

## BLOCKERS

None independently identified in this C/E/F slice. Parent's independently reproduced Unicode whole-name bypass should be classified against the explicit whole-name guarantee, not as an HTML/rendering leak.

## SHOULD FIX

### Canonical evidence labels can be rejected (IDs work)

Code: `src/query.py:147` only tries entity names up to five tokens, `src/query.py:162` requires one dictionary drug ID, `src/structured.py:85-92` depends on that linker. The model prompt says use names exactly as written in evidence (`src/query.py:456-457`). Exact questions/payloads/output:

1. Question: `Which companies are developing osimertinib?`
   Input: `{"claims":[{"kind":"relation","relation":"SPONSORS_TRIAL_OF","subject":"Second Affiliated Hospital Of Nanchang University","object":"OSIMERTINIB","evidence":"ORG:secondaffiliatedhospitalofnanchanguniversity|SPONSORS_TRIAL_OF|CHEMBL3353410|","trial_count":2}]}`.
   Output for this claim: rejected, reason `'Second Affiliated Hospital Of Nanchang University' does not name exactly one company on its own`. The seven-word `Tianjin Medical University Cancer Institute And Hospital` label similarly rejects. Both are copied exactly from retrieved evidence. Changing subject to the corresponding `ORG:...` ID accepts.
2. Question: `Which drugs act on ALK?`
   Input: `{"claims":[{"kind":"relation","relation":"ACTS_ON","subject":"ALECTINIB HYDROCHLORIDE","object":"ALK","evidence":"CHEMBL3707320|ACTS_ON|ENSG00000171094|CHEMBL3707320","action":"INHIBITOR"}]}`.
   Output: rejected, reason `'ALECTINIB HYDROCHLORIDE' does not name exactly one drug on its own`. A `kind=drug` claim with this same displayed name, `max_stage=APPROVAL,trials_in_graph=1`, also rejects. Changing drug/subject to `CHEMBL3707320` accepts.
3. Outside the demos: question `What does aprinocarsen target?` yields `APRINOCARSEN acts on PRKCA (antisense inhibitor)`. Input relation `subject=APRINOCARSEN,object=PRKCA,action=ANTISENSE INHIBITOR,evidence=CHEMBL2108287|ACTS_ON|ENSG00000154229|CHEMBL2108287` rejects (`'PRKCA' does not name exactly one target on its own`). Changing object to `ENSG00000154229` accepts. `query.py:101-102` only indexes the selected target list although ACTS_ON can add additional target nodes.

These are false rejections/usefulness defects. All these facts remain expressible with IDs, so they are not unsupported assertions or an absolute schema expressiveness failure.

## NOTES

### Demo facts are expressible using IDs; rendering preserves the checked facts

Each payload includes all supported schema facts visible in the retrieved evidence, up to default 12 evidence rows. Exact inputs and full text live in `faithful_results.json`.

| Question | Claims accepted with copied labels | With IDs | Result |
|---|---:|---:|---|
| Which companies are developing osimertinib? | 10/12 | 12/12 | sponsorship only; counts preserved |
| What trials evaluate Tagrisso? | 24/24 | 24/24 | EVALUATES + phase/status for each trial |
| What does osimertinib target? | 1/1 | 1/1 | acts on EGFR (inhibitor) |
| Which drugs act on ALK? | 20/22 | 22/22 | ACTS_ON + stage/trial count |
| What is AstraZeneca running in NSCLC? | 12/12 | 12/12 | sponsor counts preserved |
| What is the capital of France? | no evidence | no evidence | refusal before calling LLM |
| What is osimertinib? | 2/2 | 2/2 | profile stage/count plus mechanism |

Rendering references: `src/structured.py:243-267`. Sponsor sentence explicitly limits the claim to lead sponsorship, matching the graph derivation's lead_sponsor filter (`src/graph.py:337-356`). No duplicate live EVALUATES trial/drug pairs exist in this snapshot; the edge count equals trial count here.

Exact multi-phase input: question `What trials evaluate BEXAROTENE?`, `{"claims":[{"kind":"trial","trial":"NCT00153842","evidence":"NCT00153842|EVALUATES|CHEMBL1023|NCT00153842","phase":["PHASE1","PHASE2"],"status":"TERMINATED"}]}`.
Observed: `verified=true`, text `- NCT00153842: phase PHASE1, PHASE2; status TERMINATED [NCT00153842|EVALUATES|CHEMBL1023|NCT00153842]`.

There is one live empty-phase trial (`NCT00499330`) but no EVALUATES edge, hence no live default-retrieval accepted empty-phase case. An explicitly marked in-memory fixture changed only NCT03909334 phases to []; accepted phase=[] rendered `no phase given; status ACTIVE_NOT_RECRUITING`. This is fixture coverage, not a claim about the production snapshot.

Action distinction: with question `What does aprinocarsen target?`, subject `APRINOCARSEN`, object `ENSG00000154229`, and evidence `CHEMBL2108287|ACTS_ON|ENSG00000154229|CHEMBL2108287`, action `ANTISENSE INHIBITOR` accepts and renders `(antisense inhibitor)`; changing only action to `INHIBITOR` rejects with `the graph gives the action as ANTISENSE INHIBITOR, not INHIBITOR`.

### PROFILE is supported data but is not a live graph edge

Question `What is osimertinib?`:
`{"claims":[{"kind":"drug","drug":"OSIMERTINIB","evidence":"profile:CHEMBL3353410","max_stage":"APPROVAL","trials_in_graph":79}]}` accepts and renders `- OSIMERTINIB: maximum clinical stage APPROVAL; 79 NSCLC trial(s) in this graph [profile:CHEMBL3353410]`.
SQL `SELECT COUNT(*) FROM edge WHERE id='profile:CHEMBL3353410' AND retired_at IS NULL` returns `0`.
The special case at `structured.py:113-115` is evidence-consistent because node properties and counts are checked, but `structured.py:26-27` and README.md:452-453 should qualify their literal live-edge wording to mention PROFILE citations.

### Closed schema cannot preserve all evidence metadata

`structured.py:48-55` supports only ACTS_ON, EVALUATES, SPONSORS_TRIAL_OF and trial phase/status, drug max stage/count. It cannot express drug type, alias count, sponsor class, trial title/enrollment, full mechanism descriptions, target/disease associations, parent ownership, or source confidence. Evidence can display some of these (`query.py:251,281,352,358`), but adding `drug_type` or `aliases_known` to a valid profile claim rejects as unknown keys (exact probes in `faithful_results.json`). This is a declared completeness limitation, not false support.

### Documentation inconsistencies (not additional soundness failures)

- `query.py:12-18` still says the model only changes prose and entities/numbers in generated prose are checked; the current model path chooses structured claims and the program renders them.
- `web/template.html:261` still describes a check after answer creation for names/numbers; lines 263-267 correctly describe the new structured model path and template non-applicability.
- README.md:534 says 22 of 38 faithful answers were **rejected** in round 6, while README.ko.md:370 says 22 of 38 **passed**. These cannot both be the same result. This review did not replay the auxiliary checker (explicitly out of scope).
- README.md:458 says no model text reaches the reader, immediately followed by rejected claims being listed; the precise guarantee should refer to the rendered answer. Korean README and try box 3 already use answer-specific wording. Literal rejection display is expected by the brief; no inference of HTML execution from displaying escaped text.
- README item13 and try box4 clearly label the auxiliary prose checker fallible; dashboard section06 and both README structured sections correctly limit completeness/relevance claims.

