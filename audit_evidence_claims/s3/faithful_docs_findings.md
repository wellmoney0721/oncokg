# s3 faithful claims, rendering, documentation and standards review

Reviewed HEAD `6bcde7295e7b2292636119cd3e1b2a604324693d`. No tracked file was edited. Source graph connections are query-only; the empty-phase fixture changes only an in-memory backup. All scripts ran with bytecode disabled. `faithful_runner.py` replays **both** original faithful scripts; only output paths are changed. Their preserved `commit: aa5655a...` field is historical fixture metadata, not the execution revision. Full input comparisons are in `faithful_replay_manifest.json` and `faithful_comparison.json`.

## Standards

`git ls-files '*AGENTS.md' '*STANDARDS*' '*CONTRIBUTING*' '*issue-tracker*'` returns no tracked standards document. The supplied instructions require evidence-based reasoning and prohibit tracked edits; no violation identified. No code repair was made, so the instruction to show before/after code and consult Kiwoom API references is not triggered by this read-only OncoKG audit.

## BLOCKERS

No unsupported rendered fact or model-text leakage was identified in this slice. The remaining identity/documentation issue below is a SHOULD FIX under the explicit docs-do-not-overclaim approval bar.

## SHOULD FIX

### D1. The organisation alias rule is broader than the documented singleton/merged-entity rule

**Prior status:** the s2 exact shared-label reproduction is FIXED, but the broader singleton promise remains **NOT FIXED** for organisation aliases. `README.md:455-456` promises an alias resolving whole to "that node"; `README.ko.md:318` gives the same singular-node rule. `src/structured.py:30-32` now permits "that entity's merged ids", but the code groups every company matching a canonical label/key, without requiring that those nodes be the same organisation (`src/query.py:103-115,179-187`; returned unfiltered at `src/structured.py:139-140`).

The identity review independently executed a constructor-only fixture in `identity_attack.py`; its exact results are in `identity_attack_results.json`, case `constructor_company_collision:AstraZeneca!`. Fixture setup: in an in-memory graph, execute `UPDATE node SET label='Astrazeneca' WHERE id='ORG:genentech'`, then reconstruct `OncoKG` against that connection using its normal constructor. This changes no edge or company properties and establishes no same-entity merge. Genentech remains a separate ID with its original properties, including its Roche parent. The persisted graph has no multi-ID company alias key; this is explicitly fixture coverage of the unconditional contract.

Question: `What is AstraZeneca running in NSCLC?`

Exact input:

```json
{"claims":[{"kind":"relation","relation":"SPONSORS_TRIAL_OF","subject":"AstraZeneca!","object":"osimertinib","evidence":"ORG:astrazeneca|SPONSORS_TRIAL_OF|CHEMBL3353410|","trial_count":14}]}
```

Observed: `resolve('AstraZeneca!', 'Company')` returns `{'ORG:astrazeneca','ORG:genentech'}` with no reason; `verified=true`, one accepted claim, no rejected claims. Exact answer:

```text
- Astrazeneca is lead sponsor of 14 trial(s) evaluating OSIMERTINIB - a sponsorship, not evidence of developing the drug [ORG:astrazeneca|SPONSORS_TRIAL_OF|CHEMBL3353410|]
```

Changing only the subject to `AstraZeneca` rejects with `'AstraZeneca' is the label of 2 company nodes; use the id`. Punctuation routes the ambiguous label through the alias path; it does not prove a same-entity merge. The cited edge and rendered fact remain supported. Either enforce the documented entity condition or accurately describe candidate-set membership/evidence disambiguation in both READMEs and the docstring. This is not a claim of unsupported medical prose.

Interpretive limit: if "one entity" means only one linker result object and "merged ids" means any IDs collected in that object, the docstring can be read as describing the implementation. That broad operational meaning is not stated in the READMEs and differs from this repository's legal-entity merge terminology: `src/normalize.py:1070-1075` says same-entity names land on one node and explicitly excludes subsidiaries; `src/normalize.py:1183-1188` rewrites to one key and `src/graph.py:259` builds its one ID. In contrast, `src/query.py:103-104` expressly includes a group and subsidiary in the candidate aggregation. This finding requests an accurate common contract, not stricter support checking for its own sake. The root's independent `root_confirmation.json` also shows the same aggregation with distinct labels `Astrazeneca` and `Astra-Zeneca`, so it does not rely on an exact duplicate label alone.

## Previous reproductions: FIXED / NOT FIXED

| Finding | s3 status and observed result |
|---|---|
| s1 copied long sponsor names rejected | **FIXED.** Both long labels now accept; the full sponsor payload accepts 12/12 using labels and IDs. |
| s1 ALECTINIB HYDROCHLORIDE label rejected | **FIXED.** Both relation and drug profile claims accept; full ALK payload accepts 22/22 by labels and IDs. |
| s1 PRKCA exact label rejected | **FIXED.** `APRINOCARSEN` / `PRKCA` / `ANTISENSE INHIBITOR` accepts and renders the graph action. |
| s1 PROFILE incorrectly described as a live edge | **FIXED.** The old profile payload still accepts with live edge count zero; explicit exception exists at `README.md:453-454`, `README.ko.md:318`, `src/structured.py:26-28`. |
| s1 obsolete query/dashboard prose-check descriptions | **FIXED.** `src/query.py:12-18`; `web/template.html:261-267`, `web/dashboard.html:261-267`, `web/index.html:271-277` describe structured claims and rendered answers. |
| s1 22/38 English/Korean contradiction | **FIXED.** `README.md:536` and `README.ko.md:370` both say 22 of 38 passed. This audit does not rerun the out-of-scope prose checker. |
| s1/s2 "nothing ... reaches the reader" despite diagnostic echoes | **FIXED.** `README.md:460-461` now says "reaches the answer" and explicitly calls rejected claims diagnostics. |
| s2 unconditional singleton resolution wording | **FIXED** for the original exact-label reproduction; **NOT FIXED** as a general alias/merged-entity promise, D1 above. |

## NOTES and exact replay coverage

`replay_s1/faithful_results.json` and `replay_s2/faithful_results.json` contain every original question, exact payload, retrieved evidence and output. Both replays preserve all original demo, phase and schema-limitation inputs. All supported demo facts still accept: **73/73 by copied label and 73/73 by ID**, separately for each replay.

| Exact question | Copied-label claims accepted | ID claims accepted |
|---|---:|---:|
| Which companies are developing osimertinib? | 12/12 | 12/12 |
| What trials evaluate Tagrisso? | 24/24 | 24/24 |
| What does osimertinib target? | 1/1 | 1/1 |
| Which drugs act on ALK? | 22/22 | 22/22 |
| What is AstraZeneca running in NSCLC? | 12/12 | 12/12 |
| What is the capital of France? | no evidence; refusal | no evidence; refusal |
| What is osimertinib? | 2/2 | 2/2 |

Each original faithful script also reruns one live multi-phase case and two schema-limit cases. `replay_s2/faithful_additional_replay.json` replays all four original action cases, the original two-claim PROFILE payload and the original empty-phase fixture. `replay_s2/faithful_graph_dictionary.json` exactly matches the original s1 distribution and s2 dictionary result. No live `_norm` stored-code collisions, duplicate live EVALUATES trial/drug pairs, or labels longer than 120 characters were found.

Additional exact action input, question `What does aprinocarsen target?`:

```json
{"claims":[{"kind":"relation","relation":"ACTS_ON","subject":"APRINOCARSEN","object":"PRKCA","evidence":"CHEMBL2108287|ACTS_ON|ENSG00000154229|CHEMBL2108287","action":"ANTISENSE INHIBITOR"}]}
```

Output: `verified=true`, one accepted claim, text `- APRINOCARSEN acts on PRKCA (antisense inhibitor) [CHEMBL2108287|ACTS_ON|ENSG00000154229|CHEMBL2108287]`. With only `action` changed to `INHIBITOR`, output is `verified=false`, no accepted claims, empty answer, reason `the graph gives the action as ANTISENSE INHIBITOR, not INHIBITOR`. Replacing `object` with `ENSG00000154229` preserves those two results. This is STILL CORRECT evidence/value distinction.

Exact multi-phase input, question `What trials evaluate BEXAROTENE?`:

```json
{"claims":[{"kind":"trial","trial":"NCT00153842","evidence":"NCT00153842|EVALUATES|CHEMBL1023|NCT00153842","phase":["PHASE1","PHASE2"],"status":"TERMINATED"}]}
```

Output: `verified=true`, text `- NCT00153842: phase PHASE1, PHASE2; status TERMINATED [NCT00153842|EVALUATES|CHEMBL1023|NCT00153842]`. The original fixture changes only NCT03909334's phases to `[]` in an in-memory backup and verifies `{"claims":[{"kind":"trial","trial":"NCT03909334","evidence":"NCT03909334|EVALUATES|CHEMBL3353410|NCT03909334","phase":[],"status":"ACTIVE_NOT_RECRUITING"}]}`. It still accepts and renders `- NCT03909334: no phase given; status ACTIVE_NOT_RECRUITING [NCT03909334|EVALUATES|CHEMBL3353410|NCT03909334]`.

Sponsorship rendering (`src/structured.py:306-310`) says lead sponsorship and explicitly disclaims drug development, matching the lead-sponsor derivation (`src/graph.py:337-356`). Empty/multi-phase, trial status, action wording, drug stage and counts remain faithful to accepted graph values (`src/structured.py:301-324`).

The closed schema still omits drug type, alias count, sponsor class, trial title/enrollment, full mechanism description, target/disease associations, ownership and confidence. For example, adding `drug_type:"Small molecule"` or `aliases_known` to the original valid osimertinib profile payload rejects as unknown keys and produces no answer. These are unchanged completeness NOTES, not support failures. The relevance/completeness limitations remain explicit at `README.md:466-469`, `README.ko.md:321-322`, `src/structured.py:41-43`, and dashboard section 06. `README.md:529-538`, `README.ko.md:365-371`, and `web/try.html:79-90` clearly identify the auxiliary prose check as fallible. Box 3's description at `web/try.html:68-71` distinguishes the rendered answer from diagnostic claims.

The advertised test count is now 315 at `README.md:564` and `README.ko.md:386`; the root review owns fresh suite execution. No test-count claim is inferred solely from documentation.
