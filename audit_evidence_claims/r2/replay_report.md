# Round 1 reproduction replay at a12762b

All six original `independent_*.py` probe scripts were rerun through adapted copies. Only import-root depth, output filenames, and the run-command comment changed. The adaptation diffs and source SHA-256 values are retained in `replay_*_adaptation.diff` and `replay_manifest.json`. All six exit codes are zero. `replay_comparison.json` covers all 142 exact question/answer cases; question and answer identity against the stored input snapshots was asserted. The dictionary probe and six template cases are additional to the 142.

Stored `independent_*_results.json` outcomes are not treated as pristine round-1 results: for example, the stored paired-clause result already says true at line 138, despite the R1 report recording false. Historical status below follows `r1_report.md`; current status follows this fresh replay.

## BLOCKERS

R1 finding 1 is **NOT FIXED**. `Engine().check("What does osimertinib target?", "EGFR is an osimertinib inhibitor.")` still yields `grounded=True`, `unsupported_claims=[]`. Retrieved evidence says `OSIMERTINIB acts on EGFR (inhibitor)`. The nearest left entity becomes osimertinib (`src/claims.py:382`); because the right endpoint is missing, the noun fallback fills it from any unused entity of target type (`src/claims.py:407-411`). This reconstructs the valid inverse relation rather than checking the written claim.

FIXED below means the exact R1 reported reproductions are now rejected; it makes no claim about every new variant of that mechanism.

| R1 finding | Status | Fresh result |
|---|---|---|
| 1 | NOT FIXED | 1/5 exact reported attacks still pass |
| 2 | FIXED | 0/4 exact reported attacks still pass |
| 3 | FIXED | 0/5 exact reported attacks still pass |
| 4 | FIXED | 0/3 exact reported attacks still pass |
| 5 | FIXED | 0/2 exact reported attacks still pass |
| 6 | FIXED | 0/4 exact reported attacks still pass |
| 7 | FIXED | 0/2 exact reported attacks still pass |
| 8 | FIXED | 0/4 exact reported attacks still pass |

Exact R1 reported inputs, including the newline pronoun variant:

| R1 | Question | Exact answer | Observed output |
|---|---|---|---|
| 1 | `What does osimertinib target?` | `EGFR acts on osimertinib.` | `grounded=False`; `[('relation_direction', 'EGFR acts OSIMERTINIB')]` |
| 1 | `What does osimertinib target?` | `EGFR is an osimertinib inhibitor.` | `grounded=True`; `[]` |
| 1 | `What trials evaluate Tagrisso?` | `osimertinib evaluates NCT03909334.` | `grounded=False`; `[('relation_direction', 'OSIMERTINIB evaluates NCT03909334')]` |
| 1 | `What is AstraZeneca running in NSCLC?` | `osimertinib sponsors AstraZeneca.` | `grounded=False`; `[('relation_direction', 'OSIMERTINIB sponsors Astrazeneca')]` |
| 1 | `What does osimertinib target?` | `Osimertinib sponsors EGFR.` | `grounded=False`; `[('relation_direction', 'OSIMERTINIB sponsors EGFR')]` |
| 2 | `What does osimertinib target?` | `osimertinib acts on EGFR. It inhibits ALK.` | `grounded=False`; `[('relation', 'OSIMERTINIB — inhibits — ALK')]` |
| 2 | `What does osimertinib target?` | `osimertinib acts on EGFR.\nIt inhibits ALK.` | `grounded=False`; `[('relation', 'OSIMERTINIB — inhibits — ALK')]` |
| 2 | `What does osimertinib target?` | `osimertinib acts on EGFR. This drug inhibits ALK.` | `grounded=False`; `[('relation', 'OSIMERTINIB — inhibits — ALK')]` |
| 2 | `What trials evaluate Tagrisso?` | `NCT03909334 evaluates osimertinib. It evaluates osimertinib and is phase 3.` | `grounded=False`; `[('phase', 'phase 3')]` |
| 3 | `What trials evaluate Tagrisso?` | `NCT03909334 is phase 3 and NCT07680790 is phase 2.` | `grounded=False`; `[('phase', 'phase 2'), ('phase', 'phase 3')]` |
| 3 | `What trials evaluate Tagrisso?` | `NCT03909334 and NCT07680790 are recruiting.` | `grounded=False`; `[('status', 'recruiting')]` |
| 3 | `What is AstraZeneca running in NSCLC?` | `AstraZeneca sponsors 10 NSCLC trials evaluating osimertinib.` | `grounded=False`; `[('number', '10')]` |
| 3 | `Which drugs act on ALK?` | `PLB1003 acts on ALK with 13 NSCLC trials.` | `grounded=False`; `[('number', '13')]` |
| 3 | `Which drugs act on ALK?` | `PLB1003 is approved for all lung cancer and acts on ALK.` | `grounded=False`; `[('wording', 'all'), ('wording', 'approved')]` |
| 4 | `Which companies are developing osimertinib?` | `AstraZeneca is developing the drug osimertinib.` | `grounded=False`; `[('development_claim', 'developing')]` |
| 4 | `Which companies are developing osimertinib?` | `AstraZeneca has evidence of developing osimertinib.` | `grounded=False`; `[('development_claim', 'developing')]` |
| 4 | `Which companies are developing osimertinib?` | `This is not evidence that AstraZeneca sponsors osimertinib.` | `grounded=False`; `[('negation', 'not')]` |
| 5 | `What does osimertinib target?` | `Osimertinib is a non-inhibitor of EGFR.` | `grounded=False`; `[('negation', 'non')]` |
| 5 | `What trials evaluate Tagrisso?` | `NCT07680790 is non-recruiting.` | `grounded=False`; `[('negation', 'non')]` |
| 6 | `What does osimertinib target?` | `Osimertinib [is safe and discontinued] acts on EGFR.` | `grounded=False`; `[('wording', 'discontinued'), ('wording', 'safe')]` |
| 6 | `What does osimertinib target?` | `[osimertinib is safe](osimertinib) acts on EGFR.` | `grounded=False`; `[('wording', 'safe')]` |
| 6 | `What does osimertinib target?` | `오시머티닙은 안전하며 부작용이 없다.` | `grounded=False`; `[('unreadable', '오시머티닙은 안전하며 부작용이 없다.')]` |
| 6 | `What does osimertinib target?` | `osimertinib 은 EGFR 을 억제하지 않는다.` | `grounded=False`; `[('unreadable', 'osimertinib 은 EGFR 을 억제하지 않는다.')]` |
| 7 | `What does osimertinib target?` | `Osimertinib is a treatment for all cancer.` | `grounded=False`; `[('wording', 'all'), ('wording', 'cancer'), ('wording', 'treatment')]` |
| 7 | `What does omaveloxolone target?` | `Omaveloxolone inhibits NFE2L2.` | `grounded=False`; `[('action', 'OMAVELOXOLONE inhibits NFE2L2')]` |
| 8 | `Which drugs act on ALK?` | `PLB1003 is phase 13.` | `grounded=False`; `[('phase', 'phase 13')]` |
| 8 | `What trials evaluate Tagrisso?` | `NCT07680790 is phase 3b.` | `grounded=False`; `[('phase', 'phase 3b')]` |
| 8 | `Which drugs act on ALK?` | `PLB1003 has 13 non small cell lung cancer trials.` | `grounded=False`; `[('number', '13')]` |
| 8 | `Which drugs act on ALK?` | `- PLB1003: NSCLC trials: 13\n- lorlatinib: NSCLC trials: 0` | `grounded=False`; `[('number', '0'), ('number', '13')]` |

## SHOULD FIX

R1 faithful-paraphrase finding: **NOT FIXED (substantially improved)**. The unchanged 36-answer corpus now flags 1/30 evidence answers (3.3%) versus the R1 report's 10/30 (33.3%). Refusals improve from 6/6 flagged to 2/6 flagged. This is a diagnostic corpus, not a production LLM rate.

| Demo question | R1 flagged | R2 flagged |
|---|---|---|
| Which companies are developing osimertinib? | 2/6 | 0/6 |
| What trials evaluate Tagrisso? | 2/6 | 0/6 |
| What does osimertinib target? | 1/6 | 0/6 |
| Which drugs act on ALK? | 3/6 | 0/6 |
| What is AstraZeneca running in NSCLC? | 2/6 | 1/6 |
| What is the capital of France? | 6/6 | 2/6 |

The remaining exact rejected corpus answers are:

- `Q5P4` / `What is AstraZeneca running in NSCLC?` / `AstraZeneca supports trials studying osimertinib in NSCLC.` => `grounded=False`, `[('wording', 'supports')]`.
- `Q6P3` / `What is the capital of France?` / `The graph covers NSCLC drugs and trials, so it cannot answer this question.` => `grounded=False`, `[('no_antecedent', 'it')]`.
- `Q6P6` / `What is the capital of France?` / `I cannot determine the capital of France from the retrieved evidence.` => `grounded=False`, `[('entity', 'France'), ('no_subject', 'i cannot determine capital france')]`.

R1 paired-clause Cartesian-product finding: **FIXED for all three exact relation-pair reproductions**. Correct drug/target, trial/drug, and company/drug clauses now pass both the same-sentence and two-sentence forms; all three swapped-pair attacks fail. See `replay_adversarial_pairs_results.json`.

R1 dedup finding: **FIXED for distinct sentence contexts**. `Osimertinib is safe. EGFR is safe.` preserves two separate `wording: safe` findings. The second dedup reproduction, `osimertinib is safe. osimertinib is safe for all.`, preserves both safe contexts plus all. `src/query.py:560-562` keys by `(value, sentence)`. Both remain `grounded=False`.

The documentation finding is assigned to the independent documentation reviewer; no status is inferred from test success here.

## NOTES

- Exact regression command: `python -m pytest tests -q -p no:cacheprovider`. Initial run: **128 passed, 1 warning in 6.26s**. The warning was a cp949 subprocess-output reader decoding UTF-8 in `test_correction_check_fails_when_a_correction_is_pending`. A second run with `PYTHONUTF8=1` gave **128 passed in 6.24s**, no warnings. Both logs are retained. TEMP/TMP were restricted to `audit_evidence_claims/r2/replay_temp`; bytecode and pytest cache writes were disabled.
- Templates: all **5/5 evidence template bodies** pass when checked as generated prose after the normal `Scope:` removal. Full Scope-inclusive templates remain rejected. The France refusal template still fails generated checking with `no_antecedent: it` and `no_subject: no entity question matched`.
- Replayed original dictionary experiment: **7,610 index keys, 1,066 drugs, 2,634 unique stored multiword aliases; zero lost intended links**. There are two removed extraneous numeric `1 ×` links. `is a` no longer maps to ISATUXIMAB; AZD 9291, AZD9291, osimertinib mesylate, trastuzumab deruxtecan, pemetrexed disodium, and nab paclitaxel retain the prior intended links.
- The original dictionary experiment removes the abbreviation gate from the current linker; it does not load 0c441e0's method and therefore does not isolate the new punctuation change. The separate R2 linker audit must cover that difference.
- All old negative controls (safe, discontinued, not, contractions, no longer, un-/non- forms, explicit wrong pairs) remain rejected. A punctuation-only answer `...` still passes, but makes no biomedical claim; this was an R1 note-level probe rather than a reported blocker.
- No tracked files were edited. Only `audit_evidence_claims/r2/replay_*` files were written by this replay work.
