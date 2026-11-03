# Independent spec-axis attacks on a12762b

Reproduce from repository root with `python -B audit_evidence_claims/r2/spec_probe.py`. All 57 exact inputs, full checks, complete retrieved statements, and parser units are in `spec_probe_results.json`. Only scratch files under `audit_evidence_claims/r2/` were written. No source files were changed.

## BLOCKERS

All unsupported examples below returned `grounded=True`, `unsupported_claims=[]` using the real graph. These are failures of stated relations, entity binding, or numeric attributes, not externally asserted clinical facts.

### S1. Repeated prepositions silently remove a second relation endpoint

- Question: `What does osimertinib target?`
- Answer: `Osimertinib acts on EGFR and on ALK.`
- Other passing answers: `Osimertinib is an inhibitor of EGFR and of ALK.` and `Osimertinib inhibits EGFR and also ALK.`
- Retrieved evidence: `OSIMERTINIB acts on EGFR (inhibitor)`, with no osimertinib--ALK relation.
- Control: `Osimertinib acts on EGFR and ALK.` returns false with `relation: OSIMERTINIB — acts — ALK`.
- Cause: `src/claims.py:328-338` does not split without a second predicate; `_group` at `src/claims.py:343-358` ends at `on`, `of`, or `also`. Relation validation at `src/claims.py:382-383` and `447-453` only visits that truncated group; attributes exempt remaining grammar at `src/claims.py:552-553`. No check verifies every linked endpoint is accounted for.
- Also reproduced nominal `target of`: union unmodified target evidence for osimertinib and crizotinib; `EGFR is a target of osimertinib and of crizotinib.` passes despite no crizotinib--EGFR edge. The new noun-form support inherits this bypass.
- Spec requirement: "A stated relation ... must hold between the same entities"; Round 2 explicitly requests clause splitting and noun-form attacks.

### S2. Copular clefts are mistaken for passive voice, reversing false relations

| Exact question | Exact passing answer |
|---|---|
| `What does osimertinib target?` | `EGFR is what inhibited osimertinib.` |
| `What does osimertinib target?` | `EGFR is what targeted osimertinib.` |
| `What trials evaluate Tagrisso?` | `Osimertinib is what evaluated NCT03909334.` |
| `What is AstraZeneca running in NSCLC?` | `Osimertinib is what sponsored AstraZeneca.` |

Evidence supports the opposite directions: osimertinib acts on EGFR, NCT03909334 evaluates osimertinib, AstraZeneca sponsors trials evaluating osimertinib. `is what inhibited/evaluated/sponsored` contains an active relative clause, not a passive construction.

Cause: `src/claims.py:401-404` flips endpoints whenever a form of BE appears in the preceding three tokens. The presence of `is` in the separate copular clause suffices. Control `Osimertinib is inhibited by EGFR.` is correctly rejected for direction. Requirement: stated direction and explicit Round-2 passive detection attack.

### S3. Within-sentence pronouns bind to the preceding sentence rather than preceding clause

- Retrieve the union of unmodified evidence for `What does osimertinib target?` and `What does crizotinib target?`.
- Answer: `Osimertinib acts on EGFR. Crizotinib acts on ALK and it inhibits EGFR.`
- Also passes with `while this drug inhibits EGFR.` in place of `and it inhibits EGFR.`.
- Evidence supports osimertinib--EGFR and crizotinib--ALK, but not crizotinib--EGFR. The second sentence makes the latter claim.
- Control: `Osimertinib acts on EGFR. Crizotinib acts on ALK. It inhibits EGFR.` is correctly rejected with `relation: CRIZOTINIB — inhibits — EGFR`.
- Cause: `src/claims.py:228` tokenizes and resolves all pronouns before iterating over clauses; `src/claims.py:299-300` uses the old antecedent, while state is updated only at `src/claims.py:259-261`. Thus the `it` in the second sentence is frozen to osimertinib.
- Requirement: claimed behavior in `src/claims.py:22-23`, "subject of the clause before".

### S4. A phase digit is accepted as a trial count

- Question: `Which drugs act on ALK?`
- Answer: `PLB1003 has 1 clinical trial.`
- Also passes: `PLB1003: 1 trial.`
- Exact evidence: `PLB1003 acts on ALK (inhibitor; max stage PHASE_1; 0 NSCLC trial(s) in this graph)`.
- Actual supported count is **0**, whereas **1** is the maximum-stage digit.
- Cause: `src/claims.py:522-527` checks any matching number in entity-scoped text, without its attribute. `_flat` converts `PHASE_1` to `phase 1`; the resulting 1 satisfies the count check.
- Requirement: "N trials must be stated for that sentence's own entities"; entity ownership alone is insufficient if the number belongs to another attribute.

### S5. Nearest-following entity still transfers a count across drugs

- Question: `What is AstraZeneca running in NSCLC?`
- Answer: `AstraZeneca sponsors osimertinib in 10 trials with carboplatin.`
- Evidence: `Astrazeneca sponsors 14 NSCLC trial(s) evaluating OSIMERTINIB`; `Astrazeneca sponsors 10 NSCLC trial(s) evaluating CARBOPLATIN`. Neither states the asserted joint trials, and 10 belongs to carboplatin's separate count.
- Controls: remove `with carboplatin` and the incorrect 10 is rejected; replace 10 with 14 while keeping `with carboplatin` and 14 is rejected.
- Cause: `src/claims.py:460-468` searches the preferred direction before considering distance or grammar; `src/claims.py:524` prefers the next entity. `src/claims.py:473-477` then checks the number against AstraZeneca+carboplatin, dropping osimertinib from numeric scope. Although full-clause wording support is empty, every remaining word is exempt grammar/relation text.
- Requirement: counts cannot migrate between entities; explicit Round-2 nearest-entity attack.

### S6. Antagonist evidence satisfies agonist/activation claims by substring

- Question: `What does fulvestrant target?`
- Answers: `Fulvestrant activates ESR1.` and `Fulvestrant is an agonist of ESR1.`
- Exact evidence: `FULVESTRANT acts on ESR1 (antagonist)`.
- Control: `Fulvestrant is an antagonist of ESR1.` also passes, correctly.
- Cause: `src/claims.py:73-74` includes `agonist` as an activation marker, and `src/claims.py:454-455` uses unrestricted substring containment. `agonist in antagonist` is true. The action type therefore verifies its opposite.
- Requirement: action type must match (repair table R1 #7; `src/claims.py:14`). This is distinct from plain generic ACTS_ON scope.

## SHOULD FIX

1. **Faithful inline pronouns fail.** Q3, `Osimertinib acts on EGFR and it inhibits EGFR.` returns false with `no_antecedent: it`. There is an unambiguous antecedent in the preceding clause; cause is S3. Using union target evidence, `Osimertinib acts on EGFR. Crizotinib acts on ALK and it inhibits ALK.` is also falsely rejected for `OSIMERTINIB — inhibits — ALK`.
2. **Faithful possessive noun relation fails.** Q3, `Osimertinib is EGFR's inhibitor.` returns false with `wording: egfr's` and `relation_incomplete: inhibitor`. This is secondary to the blocking noun endpoint omission.

## NOTES

- Elided predicates are unchecked as well: with union target evidence, `Crizotinib acts on ALK; on EGFR.` and `Osimertinib acts on EGFR; crizotinib on EGFR.` both pass. This extends S1; omitted-subject relation with an explicit verb (`... Crizotinib acts on ALK and inhibits EGFR.`) correctly fails.
- Simple reversed `target of`, `inhibitor of`, and passive `is inhibited by` attacks are caught. `The inhibition of EGFR by osimertinib.` passes; reversed `The inhibition of osimertinib by EGFR.` is rejected.
- Independent R1 replay, complete regression tests, documentation, heading/verbatim/META and linker/alias coverage are assigned to other reviewers. No claim here estimates an overall false-negative rate from this exploratory 57-case corpus.

VERDICT: CHANGES REQUIRED
