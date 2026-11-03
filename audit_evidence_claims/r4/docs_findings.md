# Round 4 documentation / headings / kind-word review

HEAD: `2de10d95295e94c24060648ee01a195496df7acb`. Read-only source review; new scripts/results only under `audit_evidence_claims/r4/docs*`. All executions set `PYTHONDONTWRITEBYTECODE=1`, `PYTHONUTF8=1`; scripts also set `sys.dont_write_bytecode=True`. No web search or medical inference was used: support means the actual retrieved graph evidence. No separate tracked AGENTS/CONTRIBUTING/CODING_STANDARDS document was found. User's no-source-edit restriction overrides setup work; no source repairs or external-reference comparison was necessary.

## Standards / documentation axis summary

No standalone violation of a repository coding standard is asserted. Documentation improved: `src/claims.py:10-11` explicitly describes rules rather than a guarantee; README item 13 describes unseen-shape failures and specific known passes/false rejections; `src/query.py:448-466`, `web/template.html:263-267`, `web/try.html:69-72,142-145` qualify the checker and distinguish nothing flagged from proof of truth.

The remaining issue is the requested **explicit known-residue approval bar**, not the old universal-guarantee criticism. `README.md:518-529`, `README.ko.md:360-365` do not list deletion of an unsupported adjective from a heading, kind claims borrowing a different entity's type, or a new clinical-trials claim borrowing evidence from other drugs via a shared target. The examples below are outside the named one-statement-rearrangement residue. A heading is technically sent to the checker, but its critical word has already been erased; the statement that headings are checked (`claims.py:37-39`, `README.md:526-527`) therefore does not describe this loss. Correct these paths or list these precise known residues before claiming the requested approval threshold.

The docstring's general nearest-entity phase description (`claims.py:22-24`) should also be aligned with the deliberate nearest-*trial* preference at `claims.py:779-780`; this is a wording precision issue, not an independent blocker. The web template still describes two adversarial rounds (`web/template.html:265`), while README documents three. Its generic caveat is present and useful.

## BLOCKERS

### D-B1: Heading substitution discards arbitrary clinical assertions

Exact question: `What does osimertinib target?`

Every answer below returns `grounded=True`, `applicable=True`, `unsupported_claims=[]`:

```text
The following safe drugs:
- OSIMERTINIB acts on EGFR (inhibitor).
```

```text
The following discontinued drugs:
- OSIMERTINIB acts on EGFR (inhibitor).
```

```text
The following approved drugs:
- Osimertinib inhibits EGFR.
```

```text
These safe drugs:
- Osimertinib
```

The only retrieved statement is `OSIMERTINIB acts on EGFR (inhibitor)`. None supports safe, discontinued, or approved. These content words do not come from that statement and thus are outside the README residue.

Cause: `src/claims.py:250-256` matches `these|the following|following` plus **any optional alphabetic word** and replaces the entire matched span with the item. It therefore removes `safe`, `discontinued`, or `approved` before tokenization. Both ordinary joined units (`:296`) and copied-line heading checks (`:319-321`) use this function. The new non-lenient check and joined-dash guard cannot inspect words already deleted.

Status example, exact question `What trials evaluate Tagrisso?`:

```text
The following terminated trials:
- NCT07680790 (PHASE3, RECRUITING) evaluates OSIMERTINIB.
```

Also returns True/[] although that trial's evidence says RECRUITING. `The following nonrecruiting trials:` with the same item also passes.

Control with Q3: `safe drugs:\n- OSIMERTINIB acts on EGFR (inhibitor).` returns False with `wording: safe`; `The following drugs:` plus the copied line passes correctly. A heading with its own incompatible entity (`EGFR drugs:` over the copied Q3 line) is rejected as `fragment`. These isolate preprocessing loss from the joined-dash exemption.

Evidence: `docs_probe_results.json` IDs `head_safe`, `head_discontinued`, `head_noninhibitor`, `head_safe_notcopied`, `head_safe_bare`; `docs_controls_results.json` IDs `head_terminated`, `head_safe_explicit`, `head_control_kind`, `head_wrong_entity`; `docs_diagnostics_results.json` IDs `heading_approved`, `heading_nonrecruiting`, `head_lower_control`.

### D-B2: Kind words need any matching entity in the clause, not their actual subject

Exact question: `What does osimertinib target?`

```text
EGFR is a drug inhibited by osimertinib.
```

Observed: True/[]; only evidence is `OSIMERTINIB acts on EGFR (inhibitor)`. EGFR is the target, and the evidence never calls it a drug. The unsupported word `drug` is absent from the sole evidence statement, so this is outside the named residue.

Cause: `src/claims.py:719-720` collects entity kinds anywhere in the clause. `:901-907` accepts `drug` if **any** Drug is present; the valid passive inhibition relation supplies osimertinib, so the incorrect kind assertion about EGFR passes. The identity guard is inapplicable because the clause also contains a recognized relation.

Controls: Q3 `EGFR is a drug.` -> False (`wording: drug`); Q3 `Osimertinib is a drug that inhibits EGFR.` -> True; Q3 `Osimertinib and EGFR are drugs.` -> False (`identity`). Q2 `NCT07680790 is a drug that evaluates osimertinib.` also returns True/[], illustrating the same defect with Trial rather than Target as the misclassified subject.

Evidence: `docs_probe_results.json` ID `kind_drug_target`; `docs_controls_results.json` IDs `kind_control_target`, `kind_target_nonrelation`, `kind_faithful`; `docs_diagnostics_results.json` ID `kind_trial_drug`.

### D-B3: Other drugs' trial evidence supports a novel clinical-trials claim

Exact question: `Which drugs act on ALK?`

```text
PLB1003 inhibits ALK in clinical trials in this graph.
```

Observed: True/[] with all 11 unmodified retrieved evidence statements. PLB1003's own statement says `PLB1003 acts on ALK (inhibitor; max stage PHASE_1; 0 NSCLC trial(s) in this graph)`. The graph provides no PLB1003 trials in this evidence. No Q4 statement contains `clinical`; this new ordinary clinical concept is outside the one-statement vocabulary-rearrangement residue.

Cause: `src/claims.py:745-759` builds `wide` from statements naming **any** clause entity, including ALK. Other ALK drugs have positive trial counts, so `about_trials` becomes true and `:901-907` accepts `clinical`/`trials` for PLB1003. This contradicts the nearby zero-count comment (`:753-754`).

Causal diagnostic: the exact answer checked against only the unchanged PLB1003 evidence row returns False with `wording: clinical` and `wording: trials`. Adding back the other retrieved ALK rows changes it to True. This is an analysis-only subset control; the blocker itself uses Engine.check and the full real retrieval.

Controls: Q4 `PLB1003 is in clinical trials.` -> False; Q4 `Lorlatinib is in clinical trials.` -> True. The omission of ALK removes the unrelated-statement support pool.

Evidence: `docs_probe_results.json` ID `kind_trial_borrow`; `docs_diagnostics_results.json` IDs `trial_graph`, `trial_scope_full`, `trial_scope_plb_only`; `docs_controls_results.json` IDs `kind_control_trial`, `kind_trial_faithful_clinical`.

## SHOULD FIX

### D-S1: A graph-backed target citation is rejected by the older entity-overlap layer

Q3 exact answer: `Osimertinib acts on EGFR [CHEMBL3353410, ENSG00000146648].`

Observed: False; `entity: ENSG00000146648`. Both IDs occur in the retrieved edge ID `CHEMBL3353410|ACTS_ON|ENSG00000146648|CHEMBL3353410`. `claims._strip_citations` correctly removes this bracket, but `src/query.py:533-542` examines capitalized tokens against a haystack assembled at `:482-487` that omits edge IDs. Hence this valid citation fails before the claim check. The single source-record citation `[CHEMBL3353410]` passes.

Whitespace-separated valid IDs are additionally not stripped: `_strip_citations` (`claims.py:211-218`) splits only comma/semicolon while RE_CITE allows whitespace separators. `Osimertinib acts on EGFR [CHEMBL3353410 ENSG00000146648].` returns False with two number findings, an entity finding, and wording `chembl`, `ensg`. This is usability, not a false-acceptance blocker. The documentation says "only when every id" (a necessary condition), so failure to remove valid formats alone does not disprove that sentence.

Evidence: `docs_controls_results.json` IDs `cite_valid`, `cite_valid_list`, `cite_valid_space`; direct transforms in `docs_diagnostics_results.json` (`citation_transform`).

## NOTES / controls

- `Osimertinib [ORG:is-safe] acts on EGFR.` and mixed `[CHEMBL3353410, ORG:is-safe]` both fail; known-ID membership now prevents the earlier identifier-shaped claim deletion. Valid `[CHEMBL3353410]` does not launder explicit `Osimertinib is safe`.
- Q4 `Lorlatinib is approved in NSCLC.`, `Lorlatinib is approved for NSCLC trials.`, and `Lorlatinib is approved for lung cancer.` fail with `indication: lung cancer`. `Lorlatinib is approved.` passes consistently with its APPROVAL stage, so this is a NOTE.
- Q4 `PLB1003 inhibits ALK in NSCLC trials.` passes, but its words can be drawn from PLB1003's own zero-trial statement. Under the requested generous residue boundary, this is a known-residue NOTE, not an independent blocker. D-B3 uses the new word `clinical` and demonstrates cross-row dependence.
- Q5 `AstraZeneca is a drug sponsoring trials of osimertinib.` and `Osimertinib is a company sponsored by AstraZeneca.` also pass. They illustrate kind-owner weakness but are not needed independently; D-B2 has the clearest outside-residue evidence.
- Plain wrong identity `PLB1003 is LORLATINIB.` fails; adding an appositive relation in `PLB1003 is lorlatinib, an ALK inhibitor.` fails as `unrelated_entity: PLB1003`. Same-entity alias `Osimertinib is Tagrisso.` passes consistently.
- Faithful `Osimertinib is evaluated in the clinical trial NCT07680790.` passes. Awkward inputs are not automatically treated as unsupported merely because their prose is odd.
- Template heading source changes are at `src/query.py:403-412`; replay agent owns complete template prose reruns. The heading exploit above does not require an old template or lenient mode.
- `lenient` parameters remain in private signatures, but all production entry paths read here pass the default False. Their presence alone is not a behavioral finding.

Reproduce these focused probes from the repository root: `python audit_evidence_claims/r4/docs_probe.py`, `python audit_evidence_claims/r4/docs_controls.py`, `python audit_evidence_claims/r4/docs_diagnostics.py`, with bytecode suppression. JSON files preserve exact answers, raw check dictionaries and full retrieved evidence (except diagnostics, whose relevant subset rows are included explicitly).

