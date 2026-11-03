# s2 independent usefulness, rendering, and documentation review

Execution: HEAD `60b9c61`, comparison `git diff aa5655a...HEAD`. No tracked files changed. The copied `faithful_probe.py` changes only the output directory from s1 to s2; its old hardcoded `commit` field is not execution metadata. All imports were run with bytecode disabled; production graph connections were query-only. The empty-phase mutation was made only in an in-memory backup.

## Standards

No repository-specific coding standards, CONTRIBUTING, or AGENTS file appeared in `git ls-files '*AGENTS.md' '*STANDARDS*' '*CONTRIBUTING*' '*issue-tracker*'`. No documented standards violation identified. The user supplied a read-only audit, so no code repair was made.

## Spec: s1 reproductions

| s1 finding or observation | s2 status | Evidence |
|---|---|---|
| Copied long sponsor labels and ALECTINIB HYDROCHLORIDE rejected | FIXED | `faithful_results.json`: label inputs now accept 73/73, versus s1 69/73; IDs remain 73/73. |
| PRKCA absent from query dictionary rejected as an exact target name | FIXED | `faithful_additional_replay.json`: exact PRKCA with ANTISENSE INHIBITOR now accepts. |
| ANTISENSE INHIBITOR must differ from INHIBITOR | STILL CORRECT | Both PRKCA and target-id paths reject INHIBITOR with `the graph gives the action as ANTISENSE INHIBITOR, not INHIBITOR`. |
| Demo usefulness and France refusal | STILL CORRECT | All seven questions replayed; France returns no-support refusal before any LLM call. |
| Multi-phase and empty-phase rendering | STILL CORRECT | Live BEXAROTENE phase PHASE1, PHASE2; explicit in-memory empty-phase fixture renders `no phase given; status ACTIVE_NOT_RECRUITING`. |
| PROFILE cited as if a live edge | FIXED in claim-guarantee wording | `README.md:453-454`, `README.ko.md:318`, `src/structured.py:26-28` explicitly permit the retrieved drug profile. The original profile input still accepts; SQL live-edge count remains zero. |
| Obsolete query docstring and dashboard prose-check description | FIXED | `src/query.py:12-18`; `web/template.html:261-267`, dashboard same lines; index271-277. |
| 22/38 English/Korean contradiction | FIXED | README.md536 and README.ko.md370 both say only22/38 passed. |
| README says no model text reaches the reader although diagnostics display rejected claims | NOT FIXED (NOTE) | README.md460 still uses reader-wide wording; web/try.html177-178 displays escaped rejection reason and original claim. Its immediately following sentence explicitly announces rejected claims. This is diagnostic display, not answer leakage. |
| Closed schema omits metadata | UNCHANGED (NOTE) | Drug type/alias count still reject as unknown keys; the completeness limitation is documented. |

## Exact reproduced inputs and outputs

`faithful_probe.py` / `faithful_results.json` contain all original questions, evidence, exact claims and outputs. Per question, label/id accepted counts are 12/12 sponsors,24/24 Tagrisso trials,1/1 osimertinib target,22/22 ALK drugs,12/12 AstraZeneca portfolio,0/0 France refusal,2/2 osimertinib profile. No rejections occur in supported demo payloads.

Original additional action input: `{"claims":[{"kind":"relation","relation":"ACTS_ON","subject":"APRINOCARSEN","object":"PRKCA","evidence":"CHEMBL2108287|ACTS_ON|ENSG00000154229|CHEMBL2108287","action":"ANTISENSE INHIBITOR"}]}` with question `What does aprinocarsen target?` now yields verified=true, one accepted claim, no rejections, text `- APRINOCARSEN acts on PRKCA (antisense inhibitor) [CHEMBL2108287|ACTS_ON|ENSG00000154229|CHEMBL2108287]`.

The additional replay also executes every input in s1/faithful_additional.json and the empty-phase fixture in s1/faithful_empty_phase_fixture.json. `faithful_graph_dictionary.json` reproduces s1's complete stage/phase/status distributions exactly. New checks find no live stored-code normalization collisions, no duplicate live EVALUATES trial/drug pairs, and no live labels beyond the120-character limit.

## Documentation attack limits

`src/structured.py:30` continues to promise whole resolution to exactly one node id. The exact-label implementation returns all ids of the requested type (`:95-100`) and checks membership later (`:154`). Whether real shared labels violate this guarantee is investigated by the independent identity reviewer; it must not be dismissed solely because rendering remains supported. Both README versions and dashboard explicitly disclaim relevance/completeness; try boxes3/4 and README item13 distinguish structured validation from fallible auxiliary prose checking. No new unsupported rendered fact or model-text leakage was identified in this slice.

## Follow-up adjudication: unconditional singleton wording

The identity review's `identity_attack_results.json` case `shared_same_type_exact_label` renames a second live Drug (`CHEMBL3707320`) to `OSIMERTINIB` only in an in-memory graph. `resolve('OSIMERTINIB', 'Drug')` returns both `CHEMBL3353410` and `CHEMBL3707320`, and an otherwise valid osimertinib/EGFR claim accepts. Current production duplicate-label count is zero. This is an evidence-consistent runtime NOTE: its cited edge and rendered fact are still true in that fixture, and neither mixed-type resolution nor singleton cardinality is necessary to show graph support once evidence disambiguates.

The separate documentation statement at `src/structured.py:30` nevertheless says a name must resolve to exactly that node id, without restricting the promise to the present snapshot or specifying candidate-set membership. A valid graph fixture falsifies that unconditional singleton contract. Under the user's explicit docs-do-not-overclaim approval bar, this reviewer recommends CHANGES REQUIRED for that wording (or enforcing the promised singleton check), not for an invented unsupported medical assertion. The same clarification should cover the older `also_matching_ids` alias path. An approval explicitly restricted to this snapshot would narrow the submitted contract without authorization.
