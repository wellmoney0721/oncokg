# Exact R1/R2 replay at 8d4a606

All six R1 scripts and all three additional R2 scripts were rerun through adapted copies. All nine exit codes are zero. Only output paths/import depth and the obsolete internal `_tokenise` signature in the R2 standards probe were adapted; per-script diffs and source SHA-256 values are retained. Input question(s), answer and case ID identity against saved snapshots was asserted for every answer case. Historical verdicts follow the R1/R2 reports, because several saved JSON files were overwritten after repairs.

R1: 142 exact answer cases, plus six templates and the dictionary gate experiment. R2: 104 additional exact answer cases, plus six question-punctuation cases and exhaustive dictionary-to-tokenizer comparison.

## Reported blockers

FIXED describes the exact prior reported reproductions, not every variant of the mechanism. New R3 attacks must be judged separately.

| Finding | Disposition | Prior reported attack inputs still passing |
|---|---|---|
| R1 B1 direction/endpoints | **FIXED** | 0/5 |
| R1 B2 pronoun subject loss | **FIXED** | 0/4 |
| R1 B3 phase/status/count pooling | **FIXED** | 0/5 |
| R1 B4 bigram laundering | **FIXED** | 0/3 |
| R1 B5 non- negation | **FIXED** | 0/2 |
| R1 B6 brackets/non-English | **FIXED** | 0/4 |
| R1 B7 clinical grammar/action | **FIXED** | 0/2 |
| R1 B8 numeric layouts | **FIXED** | 0/4 |
| R2 B1 reversed noun/cleft | **FIXED** | 0/4 |
| R2 B2 hidden extra endpoint | **FIXED** | 0/4 |
| R2 B3 pronoun timing/verbatim trial | **FIXED** | 0/3 |
| R2 B4 numeric ownership/count slots | **FIXED** | 0/2 |
| R2 B5 action substring | **FIXED** | 0/2 |
| R2 B6 headings | **FIXED** | 0/5 |
| R2 B7 META clinical claims | **FIXED** | 0/4 |
| R2 B8 refused spans | **FIXED** | 0/4 |
| R2 B9 ORG citation content | **FIXED** | 0/2 |

## Exact reported blocker inputs and fresh outputs

| Finding | Question(s) | Answer | Observed output |
|---|---|---|---|
| R1 B1 / `reversed_target` | `What does osimertinib target?` | `EGFR acts on osimertinib.` | `grounded=False`; `[('relation_direction', 'EGFR acts OSIMERTINIB')]` |
| R1 B1 / `reverse_noun` | `What does osimertinib target?` | `EGFR is an osimertinib inhibitor.` | `grounded=False`; `[('relation_direction', 'EGFR inhibitor OSIMERTINIB')]` |
| R1 B1 / `reversed_trial` | `What trials evaluate Tagrisso?` | `osimertinib evaluates NCT03909334.` | `grounded=False`; `[('relation_direction', 'OSIMERTINIB evaluates NCT03909334')]` |
| R1 B1 / `reversed_sponsor` | `What is AstraZeneca running in NSCLC?` | `osimertinib sponsors AstraZeneca.` | `grounded=False`; `[('relation_direction', 'OSIMERTINIB sponsors Astrazeneca')]` |
| R1 B1 / `wrong_type_relation` | `What does osimertinib target?` | `Osimertinib sponsors EGFR.` | `grounded=False`; `[('relation_direction', 'OSIMERTINIB sponsors EGFR')]` |
| R1 B2 / `pronoun_target_same_line` | `What does osimertinib target?` | `osimertinib acts on EGFR. It inhibits ALK.` | `grounded=False`; `[('relation', 'OSIMERTINIB — inhibits — ALK')]` |
| R1 B2 / `pronoun_target_newline` | `What does osimertinib target?` | `osimertinib acts on EGFR.\nIt inhibits ALK.` | `grounded=False`; `[('relation', 'OSIMERTINIB — inhibits — ALK')]` |
| R1 B2 / `pronoun_this_drug` | `What does osimertinib target?` | `osimertinib acts on EGFR. This drug inhibits ALK.` | `grounded=False`; `[('relation', 'OSIMERTINIB — inhibits — ALK')]` |
| R1 B2 / `trial_pronoun_reset` | `What trials evaluate Tagrisso?` | `NCT03909334 evaluates osimertinib. It evaluates osimertinib and is phase 3.` | `grounded=False`; `[('phase', 'phase 3')]` |
| R1 B3 / `swapped_trial_phases` | `What trials evaluate Tagrisso?` | `NCT03909334 is phase 3 and NCT07680790 is phase 2.` | `grounded=False`; `[('phase', 'phase 2'), ('phase', 'phase 3')]` |
| R1 B3 / `pooled_trial_status2` | `What trials evaluate Tagrisso?` | `NCT03909334 and NCT07680790 are recruiting.` | `grounded=False`; `[('status', 'recruiting')]` |
| R1 B3 / `wrong_sponsor_count` | `What is AstraZeneca running in NSCLC?` | `AstraZeneca sponsors 10 NSCLC trials evaluating osimertinib.` | `grounded=False`; `[('number', '10')]` |
| R1 B3 / `wrong_drug_count_target` | `Which drugs act on ALK?` | `PLB1003 acts on ALK with 13 NSCLC trials.` | `grounded=False`; `[('number', '13')]` |
| R1 B3 / `clinical_from_alk` | `Which drugs act on ALK?` | `PLB1003 is approved for all lung cancer and acts on ALK.` | `grounded=False`; `[('wording', 'all'), ('wording', 'approved'), ('indication', 'lung cancer')]` |
| R1 B4 / `quoted_developing` | `Which companies are developing osimertinib?` | `AstraZeneca is developing the drug osimertinib.` | `grounded=False`; `[('development_claim', 'developing')]` |
| R1 B4 / `quoted_developing_2` | `Which companies are developing osimertinib?` | `AstraZeneca has evidence of developing osimertinib.` | `grounded=False`; `[('development_claim', 'developing')]` |
| R1 B4 / `quoted_absence_natural` | `Which companies are developing osimertinib?` | `This is not evidence that AstraZeneca sponsors osimertinib.` | `grounded=False`; `[('negation', 'not')]` |
| R1 B5 / `non_inhibitor` | `What does osimertinib target?` | `Osimertinib is a non-inhibitor of EGFR.` | `grounded=False`; `[('negation', 'non')]` |
| R1 B5 / `non_hyphen` | `What trials evaluate Tagrisso?` | `NCT07680790 is non-recruiting.` | `grounded=False`; `[('negation', 'non')]` |
| R1 B6 / `square_bracket_claim` | `What does osimertinib target?` | `Osimertinib [is safe and discontinued] acts on EGFR.` | `grounded=False`; `[('wording', 'discontinued'), ('wording', 'safe')]` |
| R1 B6 / `markdown_link_label` | `What does osimertinib target?` | `[osimertinib is safe](osimertinib) acts on EGFR.` | `grounded=False`; `[('wording', 'safe')]` |
| R1 B6 / `korean_only` | `What does osimertinib target?` | `오시머티닙은 안전하며 부작용이 없다.` | `grounded=False`; `[('unreadable', '오시머티닙은 안전하며 부작용이 없다.')]` |
| R1 B6 / `korean_mixed_relation` | `What does osimertinib target?` | `osimertinib 은 EGFR 을 억제하지 않는다.` | `grounded=False`; `[('unreadable', 'osimertinib 은 EGFR 을 억제하지 않는다.')]` |
| R1 B7 / `plain_clinical_grammar` | `What does osimertinib target?` | `Osimertinib is a treatment for all cancer.` | `grounded=False`; `[('wording', 'all'), ('wording', 'cancer'), ('wording', 'treatment')]` |
| R1 B7 / `activator_as_inhibitor` | `What does omaveloxolone target?` | `Omaveloxolone inhibits NFE2L2.` | `grounded=False`; `[('action', 'OMAVELOXOLONE inhibits NFE2L2')]` |
| R1 B8 / `phase_13_regex` | `Which drugs act on ALK?` | `PLB1003 is phase 13.` | `grounded=False`; `[('phase', 'phase 13')]` |
| R1 B8 / `phase_suffix` | `What trials evaluate Tagrisso?` | `NCT07680790 is phase 3b.` | `grounded=False`; `[('wording', '3b'), ('phase', 'phase 3b')]` |
| R1 B8 / `count_long_unit` | `Which drugs act on ALK?` | `PLB1003 has 13 non small cell lung cancer trials.` | `grounded=False`; `[('number', '13')]` |
| R1 B8 / `count_after_colon_list` | `Which drugs act on ALK?` | `- PLB1003: NSCLC trials: 13\n- lorlatinib: NSCLC trials: 0` | `grounded=False`; `[('number', '0'), ('number', '13')]` |
| R2 B1 / `reverse_noun` | `What does osimertinib target?` | `EGFR is an osimertinib inhibitor.` | `grounded=False`; `[('relation_direction', 'EGFR inhibitor OSIMERTINIB')]` |
| R2 B1 / `passive_cleft` | `What does osimertinib target?` | `EGFR is what inhibited osimertinib.` | `grounded=False`; `[('relation_direction', 'EGFR inhibited OSIMERTINIB')]` |
| R2 B1 / `passive_cleft_trial` | `What trials evaluate Tagrisso?` | `Osimertinib is what evaluated NCT03909334.` | `grounded=False`; `[('relation_direction', 'OSIMERTINIB evaluated NCT03909334')]` |
| R2 B1 / `passive_cleft_sponsor` | `What is AstraZeneca running in NSCLC?` | `Osimertinib is what sponsored AstraZeneca.` | `grounded=False`; `[('relation_direction', 'OSIMERTINIB sponsored Astrazeneca')]` |
| R2 B2 / `endpoint_preposition` | `What does osimertinib target?` | `Osimertinib acts on EGFR and on ALK.` | `grounded=False`; `[('relation', 'OSIMERTINIB — acts — ALK')]` |
| R2 B2 / `endpoint_noun` | `What does osimertinib target?` | `Osimertinib is an inhibitor of EGFR and of ALK.` | `grounded=False`; `[('relation', 'OSIMERTINIB — inhibitor — ALK')]` |
| R2 B2 / `endpoint_adverb` | `What does osimertinib target?` | `Osimertinib inhibits EGFR and also ALK.` | `grounded=False`; `[('relation', 'OSIMERTINIB — inhibits — ALK')]` |
| R2 B2 / `noun_target_second` | `What does osimertinib target? + What does crizotinib target?` | `EGFR is a target of osimertinib and of crizotinib.` | `grounded=False`; `[('relation', 'CRIZOTINIB — target — EGFR')]` |
| R2 B3 / `pronoun_stale` | `What does osimertinib target? + What does crizotinib target?` | `Osimertinib acts on EGFR. Crizotinib acts on ALK and it inhibits EGFR.` | `grounded=False`; `[('relation', 'CRIZOTINIB — inhibits — EGFR')]` |
| R2 B3 / `pronoun_stale2` | `What does osimertinib target? + What does crizotinib target?` | `Osimertinib acts on EGFR. Crizotinib acts on ALK while this drug inhibits EGFR.` | `grounded=False`; `[('relation', 'CRIZOTINIB — inhibits — EGFR')]` |
| R2 B3 / `verbatim_antecedent_trial` | `What trials evaluate Tagrisso?` | `NCT03909334 (PHASE2, ACTIVE_NOT_RECRUITING) evaluates OSIMERTINIB. It is phase 3.` | `grounded=False`; `[('phase', 'phase 3')]` |
| R2 B4 / `number_drug_other` | `What is AstraZeneca running in NSCLC?` | `AstraZeneca sponsors osimertinib in 10 trials with carboplatin.` | `grounded=False`; `[('unrelated_entity', 'CARBOPLATIN')]` |
| R2 B4 / `count_morph` | `Which drugs act on ALK?` | `PLB1003 has 1 clinical trial.` | `grounded=False`; `[('number', '1')]` |
| R2 B5 / `action_antagonist` | `What does fulvestrant target?` | `Fulvestrant activates ESR1.` | `grounded=False`; `[('action', 'FULVESTRANT activates ESR1')]` |
| R2 B5 / `action_noun_agonist` | `What does fulvestrant target?` | `Fulvestrant is an agonist of ESR1.` | `grounded=False`; `[('action', 'FULVESTRANT agonist ESR1')]` |
| R2 B6 / `discarded_heading` | `What does osimertinib target?` | `osimertinib is safe:` | `grounded=False`; `[('wording', 'safe')]` |
| R2 B6 / `discarded_heading_before_prose` | `What does osimertinib target?` | `osimertinib is discontinued:\nOsimertinib acts on EGFR.` | `grounded=False`; `[('wording', 'discontinued')]` |
| R2 B6 / `verbatim_under_unsafe_heading` | `What does osimertinib target?` | `these drugs are safe:\n- OSIMERTINIB acts on EGFR (inhibitor)` | `grounded=False`; `[('wording', 'safe')]` |
| R2 B6 / `verbatim_under_negated_heading` | `What does osimertinib target?` | `these drugs do not act on EGFR:\n- OSIMERTINIB acts on EGFR (inhibitor)` | `grounded=False`; `[('negation', 'not')]` |
| R2 B6 / `verbatim_under_reversed_heading` | `What does osimertinib target?` | `EGFR acts on these drugs:\n- OSIMERTINIB acts on EGFR (inhibitor)` | `grounded=False`; `[('relation_direction', 'EGFR acts OSIMERTINIB')]` |
| R2 B7 / `meta_france_unsupported_phase` | `What is the capital of France?` | `This trial is phase 4.` | `grounded=False`; `[('no_antecedent', 'this trial')]` |
| R2 B7 / `meta_missing_typed_phase` | `What trials evaluate Tagrisso?` | `This trial is phase 3.` | `grounded=False`; `[('no_antecedent', 'this trial')]` |
| R2 B7 / `meta_missing_negation` | `What trials evaluate Tagrisso?` | `This drug is not in trials.` | `grounded=False`; `[('negation', 'not')]` |
| R2 B7 / `meta_missing_count` | `Which companies are developing osimertinib?` | `It has 14 trials.` | `grounded=False`; `[('number', '14')]` |
| R2 B8 / `refused_liposomal` | `What does osimertinib target?` | `osimertinib is liposomal.` | `grounded=False`; `[('distinct_product', 'is liposomal')]` |
| R2 B8 / `refused_biosimilar` | `What does osimertinib target?` | `osimertinib is a biosimilar.` | `grounded=False`; `[('distinct_product', 'a biosimilar')]` |
| R2 B8 / `refused_negation` | `What does osimertinib target?` | `Osimertinib is not liposomal.` | `grounded=False`; `[('distinct_product', 'not liposomal')]` |
| R2 B8 / `refused_alias` | `What does osimertinib target?` | `liposomal Tagrisso.` | `grounded=False`; `[('distinct_product', 'liposomal Tagrisso')]` |
| R2 B9 / `citation_embedded_claim` | `What does osimertinib target?` | `Osimertinib [ORG:is safe] acts on EGFR.` | `grounded=False`; `[('wording', 'org'), ('wording', 'safe')]` |
| R2 B9 / `citation_embedded_wrong_relation` | `What does osimertinib target?` | `Osimertinib [ORG:inhibits ALK and] acts on EGFR.` | `grounded=False`; `[('relation', 'OSIMERTINIB — inhibits — ALK'), ('wording', 'org')]` |

## Prior SHOULD FIX findings

- **R1 faithful paraphrases/refusals: NOT FIXED**, substantially improved from R1 and unchanged on the original corpus since R2. Evidence answers: 29/30 pass, 1/30 flagged (3.3%). Refusals: 4/6 pass, 2/6 flagged. This hand-authored diagnostic corpus is not an estimate of a production LLM distribution.
- **R1 Cartesian-product pairing: FIXED**. All three same-sentence and all three two-sentence faithful pair examples pass; all three swapped drug/target, trial/drug, company/drug examples fail.
- **R1 distinct-sentence dedup: FIXED**. `Osimertinib is safe. EGFR is safe.` retains both sentence-specific `wording: safe` findings. Same-unit dedup remains unchanged: `Osimertinib is safe and EGFR is safe.` retains only one final finding although raw checking finds two; it remains rejected.
- **R2 S1 faithful forms: NOT FIXED overall**. The three reported defects in within-sentence pronouns, repeated aliases, and spaced-code digits are FIXED. `Osimertinib acts on EGFR and it inhibits EGFR.`, `Osimertinib (Tagrisso) acts on EGFR.`, and `AZD 9291 acts on EGFR.` now all return `grounded=True`, `unsupported_claims=[]`. The two reported refusal failures and the `supports` strictness remain (exact outputs below).
- **R1 documentation / R2 S2:** assessed by the parent documentation review, not inferred from passing tests here.

| Demo question | R1 flagged | R2 flagged | R3 flagged |
|---|---|---|---|
| Which companies are developing osimertinib? | 2/6 | 0/6 | 0/6 |
| What trials evaluate Tagrisso? | 2/6 | 0/6 | 0/6 |
| What does osimertinib target? | 1/6 | 0/6 | 0/6 |
| Which drugs act on ALK? | 3/6 | 0/6 | 0/6 |
| What is AstraZeneca running in NSCLC? | 2/6 | 1/6 | 1/6 |
| What is the capital of France? | 6/6 | 2/6 | 2/6 |

Exact remaining original faithful/refusal failures:

- `Q5P4` / `What is AstraZeneca running in NSCLC?` / `AstraZeneca supports trials studying osimertinib in NSCLC.` => `grounded=False`, `[('unrelated_entity', 'Astrazeneca'), ('wording', 'supports')]`.
- `Q6P3` / `What is the capital of France?` / `The graph covers NSCLC drugs and trials, so it cannot answer this question.` => `grounded=False`, `[('no_antecedent', 'it')]`.
- `Q6P6` / `What is the capital of France?` / `I cannot determine the capital of France from the retrieved evidence.` => `grounded=False`, `[('entity', 'France'), ('no_subject', 'i cannot determine capital france')]`.

## Regressions and additional replay observations

- `python -m pytest tests -q -p no:cacheprovider`: **175 passed in 5.97s**, exit 0, empty stderr. PYTHONUTF8=1, PYTHONDONTWRITEBYTECODE=1, TEMP/TMP under `r3/replay3_temp`; no cache provider or bytecode writes.
- **5/5 evidence template prose bodies pass** after the same `Scope:` removal as the normal answer path. All five full Scope-inclusive templates fail as before. France refusal template fails generated checking with `no_antecedent: it` and `no_subject: no entity question matched`; normal `ask()` uses its separate refusal path.
- Original linker gate experiment: **7,610 keys / 1,066 drugs / 2,634 unique multiword aliases**, zero lost intended links. `is a` remains unlinked; `AZD 9291`, `osimertinib mesylate`, `trastuzumab deruxtecan`, `pemetrexed disodium` retain intended links. This is the current gate-on/gate-off comparison, not old-commit execution.
- R2 dictionary-to-tokenizer replay: **2,566/2,634** aliases link an intended ID; five still lose an intended ID during tokenization (two parenthesized chemical names, three parent/salt overlaps). Exact cases are in `replay3_r2_standards_probe.json`. These are unchanged diagnostic discrepancies.
- `Which drugs act on ALK!`, with `:` or `;`, still links no target and returns unsupported; `?` works. The answer `Osimertinib acts on EGFR!` passes. Unchanged question-linker punctuation limitation.
- R2 `no_antecedent_control`: Q3 / `It inhibits EGFR.` now passes due the intentional question-seeded antecedent. It is faithful to Q3 evidence, not an unsupported claim. The raw helper without question entities may differ from `Engine.check`; the exact public call was preserved in replay.
- The previously recorded odd wording Q4 / `LORLATINIB has 13 phase trials.` still passes. It asserts the correct trial count with malformed grammar; it is not one of the reported R2 blocker attacks.
- No tracked changes were detected by `git diff --exit-code HEAD -- .` and `git diff --cached --exit-code` after execution.
