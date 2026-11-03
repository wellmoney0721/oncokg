# R6 independent spec attacks

HEAD `80da81b`; compared `git diff 9fda6f8...HEAD -- src/claims.py tests/test_claims.py`. No tracked files changed. Scratch scripts run using `python -B` and use the real local graph, `Engine().check`, unmodified retrievals and the demo questions. No network or model calls.

Reproduce:

```powershell
python -B audit_evidence_claims/r6/spec6_probe.py
python -B audit_evidence_claims/r6/spec6_controls.py
```

`spec6_probe.json` has 45 exploratory cases. `spec6_controls.json` has 37 targeted cases, exact checks, complete retrieved evidence and token/unit diagnostics. Cases overlap deliberately; these are not independent samples or estimates of production rates.

Question keys:

- Q2: `What trials evaluate Tagrisso?`
- Q3: `What does osimertinib target?`
- Q4: `Which drugs act on ALK?`

## BLOCKERS

All attacks listed below return **`grounded=True`, `applicable=True`, `unsupported_claims=[]`**. Every control output is preserved in `spec6_controls.json` under the indicated case ID. These inputs are ordinary prose or markdown lists. Kind claims introduce words absent from the evidence; the trial-context attacks transfer support across separate records. They are not covered by README item 13's explicit one-statement rearrangement residue.

### B1. Relative-clause kind words bind to the first entity, not their subject

Q3, `relative_wrong_kind`:

```text
Osimertinib inhibits EGFR, which is a drug.
```

The Q3 evidence is only `OSIMERTINIB acts on EGFR (inhibitor)`. It supports inhibition but does not make EGFR a drug. The answer's relative clause refers to EGFR. Splitting the claim explicitly, `Osimertinib inhibits EGFR. EGFR is a drug.`, rejects `wording: drug` (`relative_wrong_explicit`).

The symmetric faithful text `EGFR is inhibited by osimertinib, which is a drug.` incorrectly rejects `wording: drug` (`relative_right_kind`). Splitting it into `EGFR is inhibited by osimertinib. Osimertinib is a drug.` passes. The exact R5 form `EGFR, which is inhibited by osimertinib, is a drug.` now rejects, and its faithful reversed form passes: the new first-entity shortcut fixes the main-clause attachment while breaking the ordinary relative-clause attachment.

Cause: `src/claims.py:1085` sets `first_e` once for the entire clause; `:1096,1104-1105` binds any detected copular kind assertion to it. `_clauses` at `:560-577` does not create relative-clause subjects. The advertised rule at `claims.py:28-29` is therefore not fulfilled for this shape.

### B2. Heterogeneous subjects only check the first entity's kind

| Q | Exact answer | Case |
|---|---|---|
| Q3 | `Osimertinib and EGFR are drugs.` | `mixed_drug_wrong` |
| Q2 | `NCT07680790 and osimertinib are clinical trials.` | `mixed_trial_wrong` |

The first calls EGFR a drug; the second calls osimertinib a clinical trial. Both pass. Reversing the order rejects (`wording: drugs` / `wording: clinical`). Faithful homogeneous groups `LORLATINIB and PLB1003 are drugs.` (Q4) and `NCT07680790 and NCT03909334 are clinical trials.` (Q2) pass.

The Q2 row is `NCT07680790 (PHASE3, RECRUITING) evaluates OSIMERTINIB`; it does not contain `clinical` or assert that the evaluated drug is a trial. This is not evidence-consistent shorthand.

Cause: the kind branch at `src/claims.py:1097-1105` only checks `first_e`; the generic per-member context setup at `:835-837` filters to that first entity's type, so it cannot enforce a kind assertion over heterogeneous groups. The no-relation identity check at `:455-463` sees no entity after `are`, and does not intervene.

### B3. Record verbs let post-verb groups borrow their first member's trial context

Q4, all pass:

```text
The graph records lorlatinib and PLB1003 in clinical trials.
```

```text
The graph includes lorlatinib and PLB1003 in clinical trials.
```

```text
The graph records NSCLC trials of lorlatinib and PLB1003.
```

Relevant retrieved records:

```text
LORLATINIB acts on ALK (inhibitor; max stage APPROVAL; 13 NSCLC trial(s) in this graph)
PLB1003 acts on ALK (inhibitor; max stage PHASE_1; 0 NSCLC trial(s) in this graph)
```

Reversing the names rejects clinical/trial wording; the NSCLC version additionally rejects `indication: lung cancer`. `The graph records PLB1003 in clinical trials.` rejects. Replacing PLB1003 with CRIZOTINIB passes correctly (CRIZOTINIB has 15 NSCLC trials). Cases: `record_group_*`, `include_group_*`.

Cause: R6 adds `records` and `includes` to `PREDICATE` (`src/claims.py:157-159`). `head` at `:835-836` only examines entities before the first predicate. Both named drugs are after it, so `members` at `:837` becomes only the first drug. `trials_for` / `about_trials` at `:897-908` then license trial/clinical context and NSCLC wording for the whole clause from that first drug. `:1134-1140` skips the general all-entities wording support for kind words. The extra drug has zero recorded trials, so this is cross-record support transfer.

### B4. Heading kind applies to the last entity of an item sentence

Q3, `heading_drug_wrong`:

```text
These drugs:
- EGFR is inhibited by osimertinib.
```

Passes. A natural heading says its listed subject EGFR is a drug. Explicit `EGFR is a drug inhibited by osimertinib.` rejects `wording: drug`. The faithful inverse list `These drugs:\n- Osimertinib inhibits EGFR.` incorrectly rejects `wording: drugs` (`heading_drug_faithful`).

Q2, `heading_clinical_wrong`:

```text
These clinical trials:
- Osimertinib is evaluated in NCT07680790.
```

Passes, although `Osimertinib is a clinical trial.` rejects. The faithful `These clinical trials:\n- NCT07680790 evaluates osimertinib.` passes.

Cause: the determiner-only slot replacement at `src/claims.py:262-270` concatenates the whole item with the heading noun. In the Q3 attack it produces `EGFR is inhibited by osimertinib drugs`; `:1107-1109` attaches `drugs` to osimertinib, even though the heading describes the item subject EGFR. In the faithful inverse it produces `Osimertinib inhibits EGFR drugs`, creating the opposite error. Q2's `clinical trials` are checked as contextual participation rather than item identity. These are natural original inputs; the malformed sentence is created internally by the checker.

## SHOULD FIX

The faithful failures paired with B1 and B4 demonstrate material false positives, not merely strictness on unsupported facts. Two further capitalized nominal paraphrases explicitly supported by the new relation parser still reject upstream:

| Q | Exact faithful input | Observed |
|---|---|---|
| Q3 | `Inhibitors of EGFR include osimertinib.` | False; `entity: Inhibitors` |
| Q3 | `Inhibition of EGFR by osimertinib is recorded.` | False; `entity: Inhibition` |

Adding `The ` at the start of either input makes it pass (`noun_include_faithful_article`, `noun_by_faithful_article`). Cause: `src/query.py:543-551` treats the capitalized first word as an entity; its stop list does not include these recognized relation nouns. The ordinary reversed noun controls `The inhibitors of osimertinib include EGFR.` and `The inhibition of osimertinib by EGFR is recorded.` correctly reject `relation_direction`.

## NOTES

- Q3 `EGFR is recorded as an inhibitor of osimertinib.` passes (`as_inhibitor_reversal`): `src/claims.py:680-685` selects all entities by their types, reversing the expressed owner. The faithful inverse also passes; an activator claim rejects. This is a concrete mismatch with the positional relation description, but the false inverse reuses one record's entity/action vocabulary, so conservatively classify it under the explicitly disclosed one-statement rearrangement residue rather than making it an independent verdict driver.
- Q3 `EGFR is inhibited by osimertinib as an inhibitor.` passes and is consistent with osimertinib's supported inhibitor action; it is not a blocker.
- Exact repaired R5 relative-kind forms, bare trial identity, ordinary reversed noun relations, unsupported activator action, and ordinary `safe` wording reject. Controls preserve the narrow successes rather than calling all R6 repairs ineffective.
- The standard-source requirement to show old/new source on code changes does not apply: this review changes no implementation. Source citations above identify present faulty behavior. No KOA/Kiwoom files or external clinical truth are needed to establish support in these retrieved records.

VERDICT: CHANGES REQUIRED
