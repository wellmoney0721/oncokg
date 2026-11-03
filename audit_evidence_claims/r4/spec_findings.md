# Round 4 independent specification attack findings

Reviewed `2de10d95295e94c24060648ee01a195496df7acb`, `src/claims.py` changes from `8d4a6060c6d48e6d1d20a2d1470238539bb8fcf9`. All checks used the real graph via `Engine().check(question, answer)`; all new files are under `audit_evidence_claims/r4/`; bytecode generation was disabled. No tracked files changed. `spec_probe.py`, `spec_probe2.py`, `spec_probe3.py`, and `spec_controls.py` reproduce all 54 cases and write same-name JSON. Run from repository root with `PYTHONDONTWRITEBYTECODE=1` and `PYTHONUTF8=1`.

## Specification-axis summary (under 400 words)

The exact R3 repairs do not satisfy the approval requirement: "no known way to make an unsupported relation, value, negation or ordinary-word clinical claim pass ... not already listed as a known residue in README item 13." Five mechanisms remain: plural-group state is lost after one expansion; object-plural pronouns select only the last matching entity; `trials: N` bypasses `count_ambiguous`; a shared phase or status validates just one trial; and a clinical-trial assertion borrows trial existence from another drug via a shared target. Exact inputs below all returned `grounded=True`, `applicable=True`, `unsupported_claims=[]`. The first four require multiple evidence statements; the clinical case adds the absent word `clinical`. Therefore these are outside the specific one-evidence-statement rearrangement residue.

The identity rule also rejects ordinary faithful coordinated statements, and count ambiguity mistakes two aliases of one drug for two drugs. Their individually stated equivalents pass. These are SHOULD FIX, without claiming most faithful outputs fail. The trial-noun and listed-trial relation edges themselves correctly reject tested wrong-drug controls; it is their shared attributes that escape. Evidence-consistent passes and the NSCLC-only rearrangement are NOTES, not independent blockers. No scope creep is asserted.

## BLOCKERS

Question aliases used below are exact:

- Q2: `What trials evaluate Tagrisso?`
- Q4: `Which drugs act on ALK?`
- Q5: `What is AstraZeneca running in NSCLC?`

Every blocker answer below returned `grounded=True`, `applicable=True`, `unsupported_claims=[]`.

### B1. Plural antecedents are lost after one successful expansion

Q4:

`PLB1003 and LORLATINIB act on ALK. they act on ALK. they are approved.`

PLB1003 has max stage PHASE_1, while LORLATINIB has APPROVAL. The first plural clause checks both, but each call to `_check_clause` invokes `st.note` (`src/claims.py:352-356`, `425-426`), replacing the group with the current singleton (`264-270`). The last pronoun checks only LORLATINIB. Reversing the initial order rejects `wording: approved`; capitalizing `They` happens to trigger an unrelated global entity false positive. Source: `spec_probe2.json`, `plural_chain_low`, `plural_chain_lowreverse`; capitalization controls in `spec_probe.json`.

### B2. Object-plural pronouns collapse a multi-drug claim to the last drug

Q5:

`AstraZeneca sponsors osimertinib and carboplatin. It sponsors them in 10 trials.`

Also passes with `AstraZeneca` instead of `It` in the second sentence. Retrieved sponsorship counts are 14 for OSIMERTINIB and 10 for CARBOPLATIN. `them` means the previously listed drugs, yet at `src/claims.py:340-350` its relation-object role sets `want='Drug'`, preventing plural expansion; `st.by_type` stores only the last drug. Thus the count and relation check only CARBOPLATIN. Replacing `them` by `osimertinib` rejects `number: 10`. Sources: `spec_probe.json`, `object_plural_count`; `spec_probe2.json`, `count_object_plural_sentence`, `count_object_plural_singular`.

### B3. Number-after-label counts escape the new ambiguity guard

Q5:

`AstraZeneca sponsors osimertinib and carboplatin in trials: 10.`

Also passes with `clinical trials: 10`. The actual 14 osimertinib trials preclude ten trials covering the combined claim; no joint trial count is provided. At `src/claims.py:798-802`, the numeric checker recognizes a preceding `trials` word, but the new ambiguity guard at `819-820` recognizes only a following trial word. Numeric ownership selects the last drug (CARBOPLATIN) and permits 10. `... in 10 trials.` correctly rejects `count_ambiguous`; `... in trials: 14.` rejects `number: 14`; correct separate 14/10 counts pass. Sources: `spec_probe2.json`, `count_label_shared_same`; `spec_probe3.json`, `trialcount_subjectgroup`; `spec_controls.json`.

### B4. Shared trial phase/status checks just one trial

Q2, each exact answer passes:

1. `NCT03909334 and NCT07680790 are recruiting trials of osimertinib.`
2. `NCT03909334 and NCT07680790 are phase 3 trials of osimertinib.`
3. `Recruiting trials evaluating osimertinib include NCT07680790 and NCT03909334.`
4. `Phase 3 trials evaluating osimertinib include NCT07680790 and NCT03909334.`
5. `NCT07680790 and NCT03909334 evaluate osimertinib and are recruiting.`
6. `NCT07680790 and NCT03909334 evaluate osimertinib and are phase 3.`

NCT03909334 is PHASE2, ACTIVE_NOT_RECRUITING. NCT07680790 is PHASE3, RECRUITING. Trial noun/list relation checks correctly cover both trials (`src/claims.py:559-575`, `651-665`), suppressing the unrelated identity rejection. Phase ownership is one nearest trial (`779-785`); status ownership is one nearest trial (`848-851`). Prefix modifiers select the first listed trial and post-group modifiers the last. Elided predicate variants inherit only `st.subject` (`388-391`), losing the group. Swapping list order in examples 3/4 correctly rejects the status/phase. Single-trial false controls also reject. Sources: `spec_probe2.json`, `status_group_trialof`, `phase_group_trialof`, `status_group_evalafter_rev`, `phase_group_evalafter_rev`; `spec_probe3.json`, `status_list_prefix`, `phase_list_prefix` and their `_control` cases; `spec_controls.json`.

### B5. Trial existence is pooled through a shared target

Q4:

`PLB1003 acts on ALK in clinical trials.`

PLB1003 evidence explicitly says `0 NSCLC trial(s) in this graph`. No Q4 retrieved statement includes the word `clinical`. `wide` selects statements naming ANY entity, so the target ALK pulls in trial counts for other drugs (`src/claims.py:743-758`). `about_trials` then licenses `clinical` and `trials` (`901-907`). The ordinary-word claim that PLB1003 acts on ALK in clinical trials is unsupported by the retrieved evidence. `PLB1003 has clinical trials.` rejects both words, showing the shared-target leakage. Source: `spec_probe3.json`, `clinical_target_pool`, `clinical_target_pool_noedge`; `spec_controls.json`, `clinical_0_only`.

## SHOULD FIX

### S1. Identity rule mistakes coordinated assertions for equivalence

Exact faithful examples:

| Question | Answer | Observed |
|---|---|---|
| Q2 | `NCT07680790 and NCT02411448 are phase 3.` | False; `identity: NCT07680790 = NCT02411448` |
| Q2 | `NCT07680790 and NCT07738172 are recruiting.` | False; `identity: NCT07680790 = NCT07738172` |
| Q4 | `LORLATINIB and CRIZOTINIB are approved.` | False; `identity: LORLATINIB = CRIZOTINIB`, `wording: approved` |

The evidence supports both members in every row. `src/claims.py:401-405` reports every multi-entity non-relation predicate as identity, even when both entities are coordinated subjects. Splitting into two sentences passes (`spec_controls.json`); all grouped failures are in `spec_probe3.json`.

### S2. Count ambiguity mistakes aliases for different drugs

Q5: `AstraZeneca sponsors 14 trials of osimertinib (Tagrisso).`

Observed False; `count_ambiguous: OSIMERTINIB / OSIMERTINIB`. Without `(Tagrisso)` it passes. `src/claims.py:818-829` counts token positions rather than distinct drug IDs/labels. Source `spec_probe3.json`, `faithful_count_alias`, and `spec_controls.json`, `count_alias_control`.

## NOTES

- `Trials evaluating osimertinib include NCT03909334 and NCT07680790.` and `NCT03909334 is a phase 2 trial of osimertinib.` pass, correctly. Corresponding carboplatin claims fail. This isolates B4 to attribute coverage, not failure to compare listed trial-drug relation endpoints.
- `PLB1003 acts on ALK in NSCLC trials.` also passes. Because every content token can come from PLB1003's own statement, this plausibly fits README item 13's one-statement rearrangement residue and is NOT an independent blocker. B5 deliberately uses the additional, absent `clinical` word.
- Evidence-consistent singular object pronoun `Osimertinib acts on EGFR. Osimertinib inhibits it.` passes; no defect asserted.
- Controls are diagnostic, not an estimate of production answer failure rates. No web sources are needed: support here is exclusively the retrieved graph, not external clinical truth.
