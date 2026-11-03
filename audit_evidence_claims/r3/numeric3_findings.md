# Round 3 numerical ownership and alias review

Read-only review at HEAD `8d4a606`. All fresh execution used `python -B` with `PYTHONDONTWRITEBYTECODE=1` and `PYTHONUTF8=1`. The scripts write only their adjacent JSON under `audit_evidence_claims/r3/`. Evidence was obtained from the real `Engine` graph; no evidence was invented or modified.

## BLOCKERS

### N1. A checked second relation restores cross-drug count borrowing

Exact question: `What is AstraZeneca running in NSCLC?`

| Exact answer | Observed `checks` |
|---|---|
| `AstraZeneca sponsors osimertinib in 10 trials evaluating carboplatin.` | `grounded=True`, `unsupported_claims=[]` |
| `AstraZeneca sponsors osimertinib in 14 trials evaluating carboplatin.` | `grounded=False`, `number: 14` |
| `AstraZeneca sponsors 10 trials evaluating carboplatin and osimertinib.` | `grounded=True`, `unsupported_claims=[]` |
| `AstraZeneca sponsors 10 trials evaluating osimertinib and carboplatin.` | `grounded=False`, `number: 10` |
| `AstraZeneca sponsors 10 trials of carboplatin and osimertinib.` | `grounded=True`, `unsupported_claims=[]` |

Retrieved statements separately say `Astrazeneca sponsors 14 NSCLC trial(s) evaluating OSIMERTINIB` and `Astrazeneca sponsors 10 NSCLC trial(s) evaluating CARBOPLATIN`. They establish neither ten osimertinib trials nor ten trials evaluating the combination. Reordering the drug names changes approval while preserving the meaning of the coordinated ten-trial claim.

`_owner` always prefers a subsequent entity (`src/claims.py:594-604`), and the numeric scope requires only that owner and the first clause entity (`:610-618`); it never assigns a count to every coordinated object. Relation checking covers each drug separately (`:561-565`, `:580-586`). The new `unrelated_entity` rule (`:345-350`) therefore has nothing left to reject, even though sponsorship of one drug and evaluation of the other have been composed into an unsupported trial-count claim. The first pair is a direct continuation of the R2 B4 mechanism: inserting an evaluation predicate makes the previously unrelated carboplatin covered.

This is **outside README item 13's listed residue** (`README.md:517-519`): these clauses mix entities and figures from *different* evidence statements. No single retrieved statement names both drugs. A generic caveat that new sentence shapes can be misread is not a listing of this specific residue under the approval bar.

Reproductions: `numeric3_probe.json`, IDs `count_swap_tail`, `count_swap_tail_control`, `count_coordinated`, `count_coordinated_reverse`, `count_coordinated_noun`. Each contains exact inputs, full outputs, full retrieved evidence and parser tokens.

## SHOULD FIX

### N2. Phase owner restriction rejects ordinary faithful trial prose

Question: `What trials evaluate Tagrisso?`

* `NCT03909334 evaluates osimertinib in phase 2.` -> False, `phase: phase 2`.
* `Osimertinib is evaluated by NCT03909334 in phase 2.` -> True, `[]`.
* `NCT03909334 is a phase II trial evaluating osimertinib.` -> False, `wording: ii`.
* `NCT04285671 is a Phase I/II trial evaluating osimertinib.` -> False, `wording: ii`.
* `NCT04285671 is a phase 1/2 trial evaluating osimertinib.` -> True, `[]`.

The evidence explicitly gives NCT03909334 PHASE2 and NCT04285671 PHASE1, PHASE2. In the first sentence, the nearest preceding entity is the drug, so `:657-664` insists on a drug maximum stage instead of the named subject trial's phase. Roman values are parsed at `:647-648` but remain in `words` and are rejected by the final wording loop (`:701-726`). These do not show unsupported phases passing; they show a practical cost of the new owner rule.

### N3. Repeated aliases are only partly repaired, including numeric aliases

Question: `What does osimertinib target?`

* `AZD9291 (AZD-9291) acts on EGFR.` -> False, global `number: 9291`.
* `AZD-9291 acts on EGFR.` -> True, `[]`.
* `Osimertinib (Tagrisso, AZD 9291) acts on EGFR.` -> True, `[]`.
* `Osimertinib (Tagrisso, AZD 9291, AZD9291) acts on EGFR.` -> False, clause `number: 9291`, `wording: azd`.

The global number exemption (`src/query.py:508-513`) calls the deduplicating linker once. The first example therefore masks `AZD9291` but leaves the hyphenated alias's 9291, even though `_tokenise` correctly identifies both occurrences as the same drug. Separately, the iterative linker is capped at three rounds (`claims.py:375`), so the fourth distinct spelling remains ordinary tokens. Digit count attacks `AZD 9291 has 9291 trials.` and `AZD 9291 acts on EGFR with 9291 trials.` are correctly rejected; the exemption did not erase standalone figures in these controls.

## NOTES

* The exact elided-repeat intended form passes: `AstraZeneca is the sponsor of 14 NSCLC trials of osimertinib and 10 NSCLC trials of carboplatin and 8 NSCLC trials of gefitinib.` Swapping the first two counts is rejected (`count_group_three`, `count_group_wrong`). This control supports the repair's intended behavior, not its general safety.
* `PLB1003: clinical trials: 1.` and `PLB1003 has NSCLC trials: 1.` still pass. The count detector only looks ahead from a number (`claims.py:673-680`), so a label-before-number layout borrows PHASE_1 despite the actual count being zero. These examples fit the explicitly acknowledged single-statement rearrangement residue and are not independently used to deny approval.
* Named-trial wrong phase and cross-trial phase controls fail as expected. `NCT03909334 evaluates osimertinib in phase 3.`, `NCT03909334 and NCT07680790 are phase 3.`, and the same coordinated clause with phase 2 all fail. No newly demonstrated out-of-residue unsupported phase passed this probe.
* Fresh dictionary-to-tokenizer sweep (`numeric3_dictionary.py/.json`): 7,610 index keys, 1,066 drugs, 2,634 unique stored multiword aliases; 2,566 link an intended drug ID. Five of these lose the intended ID in claim tokenization, the same five recorded in R2: two parenthesized chemical aliases and three longer parent/salt overlap aliases. This is an existing parser discrepancy, not evidence of a new R3 linker regression. Exact aliases and entity traces are in the JSON.

Reproduce from repository root:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
$env:PYTHONUTF8='1'
python -B audit_evidence_claims/r3/numeric3_probe.py
python -B audit_evidence_claims/r3/numeric3_dictionary.py
```
