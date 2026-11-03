# Exact R1/R2/R3 replay at 2de10d9

All fourteen historical probe scripts were run from adapted copies. Inputs (case ID, exact question(s), answer) are checked against prior saved outputs. Per-script adaptation diffs, original source hashes, fresh full outputs and return codes are saved next to this report. Only path adjustments and the obsolete internal R2 `_tokenise` argument signature were changed. Historical classifications follow the reports, not overwritten snapshots.

FIXED means every exact previously reported reproduction is corrected; it is not a safety claim about related variants.

| Prior finding | Result | Prior attack inputs still passing |
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
| R3 B1 plural pronouns | **FIXED** | 0/2 |
| R3 B2 count borrowing | **FIXED** | 0/3 |
| R3 B3 headings | **FIXED** | 0/3 |
| R3 B4 clinical/kind/identity | **FIXED** | 0/7 |
| R3 weaker count-after-colon | **FIXED** | 0/1 |
| R3 weaker approval-in-NSCLC | **FIXED** | 0/1 |
| R3 weaker id-shaped citations | **FIXED** | 0/3 |

## Exact reported inputs and fresh outputs

| Finding / case | Exact question(s) | Exact answer | Fresh output |
|---|---|---|---|
| R1 B1 direction/endpoints / `reversed_target` | `What does osimertinib target?` | `EGFR acts on osimertinib.` | `grounded=False`; `[('relation_direction', 'EGFR acts OSIMERTINIB')]` |
| R1 B1 direction/endpoints / `reverse_noun` | `What does osimertinib target?` | `EGFR is an osimertinib inhibitor.` | `grounded=False`; `[('relation_direction', 'EGFR inhibitor OSIMERTINIB')]` |
| R1 B1 direction/endpoints / `reversed_trial` | `What trials evaluate Tagrisso?` | `osimertinib evaluates NCT03909334.` | `grounded=False`; `[('relation_direction', 'OSIMERTINIB evaluates NCT03909334')]` |
| R1 B1 direction/endpoints / `reversed_sponsor` | `What is AstraZeneca running in NSCLC?` | `osimertinib sponsors AstraZeneca.` | `grounded=False`; `[('relation_direction', 'OSIMERTINIB sponsors Astrazeneca')]` |
| R1 B1 direction/endpoints / `wrong_type_relation` | `What does osimertinib target?` | `Osimertinib sponsors EGFR.` | `grounded=False`; `[('relation_direction', 'OSIMERTINIB sponsors EGFR')]` |
| R1 B2 pronoun subject loss / `pronoun_target_same_line` | `What does osimertinib target?` | `osimertinib acts on EGFR. It inhibits ALK.` | `grounded=False`; `[('relation', 'OSIMERTINIB — inhibits — ALK')]` |
| R1 B2 pronoun subject loss / `pronoun_target_newline` | `What does osimertinib target?` | `osimertinib acts on EGFR.\nIt inhibits ALK.` | `grounded=False`; `[('relation', 'OSIMERTINIB — inhibits — ALK')]` |
| R1 B2 pronoun subject loss / `pronoun_this_drug` | `What does osimertinib target?` | `osimertinib acts on EGFR. This drug inhibits ALK.` | `grounded=False`; `[('relation', 'OSIMERTINIB — inhibits — ALK')]` |
| R1 B2 pronoun subject loss / `trial_pronoun_reset` | `What trials evaluate Tagrisso?` | `NCT03909334 evaluates osimertinib. It evaluates osimertinib and is phase 3.` | `grounded=False`; `[('phase', 'phase 3')]` |
| R1 B3 phase/status/count pooling / `swapped_trial_phases` | `What trials evaluate Tagrisso?` | `NCT03909334 is phase 3 and NCT07680790 is phase 2.` | `grounded=False`; `[('phase', 'phase 2'), ('phase', 'phase 3')]` |
| R1 B3 phase/status/count pooling / `pooled_trial_status2` | `What trials evaluate Tagrisso?` | `NCT03909334 and NCT07680790 are recruiting.` | `grounded=False`; `[('identity', 'NCT03909334 = NCT07680790')]` |
| R1 B3 phase/status/count pooling / `wrong_sponsor_count` | `What is AstraZeneca running in NSCLC?` | `AstraZeneca sponsors 10 NSCLC trials evaluating osimertinib.` | `grounded=False`; `[('number', '10')]` |
| R1 B3 phase/status/count pooling / `wrong_drug_count_target` | `Which drugs act on ALK?` | `PLB1003 acts on ALK with 13 NSCLC trials.` | `grounded=False`; `[('number', '13')]` |
| R1 B3 phase/status/count pooling / `clinical_from_alk` | `Which drugs act on ALK?` | `PLB1003 is approved for all lung cancer and acts on ALK.` | `grounded=False`; `[('wording', 'all'), ('wording', 'approved'), ('indication', 'lung cancer')]` |
| R1 B4 bigram laundering / `quoted_developing` | `Which companies are developing osimertinib?` | `AstraZeneca is developing the drug osimertinib.` | `grounded=False`; `[('identity', 'Astrazeneca = OSIMERTINIB'), ('development_claim', 'developing')]` |
| R1 B4 bigram laundering / `quoted_developing_2` | `Which companies are developing osimertinib?` | `AstraZeneca has evidence of developing osimertinib.` | `grounded=False`; `[('identity', 'Astrazeneca = OSIMERTINIB'), ('development_claim', 'developing')]` |
| R1 B4 bigram laundering / `quoted_absence_natural` | `Which companies are developing osimertinib?` | `This is not evidence that AstraZeneca sponsors osimertinib.` | `grounded=False`; `[('negation', 'not')]` |
| R1 B5 non- negation / `non_inhibitor` | `What does osimertinib target?` | `Osimertinib is a non-inhibitor of EGFR.` | `grounded=False`; `[('negation', 'non')]` |
| R1 B5 non- negation / `non_hyphen` | `What trials evaluate Tagrisso?` | `NCT07680790 is non-recruiting.` | `grounded=False`; `[('negation', 'non')]` |
| R1 B6 brackets/non-English / `square_bracket_claim` | `What does osimertinib target?` | `Osimertinib [is safe and discontinued] acts on EGFR.` | `grounded=False`; `[('wording', 'discontinued'), ('wording', 'safe')]` |
| R1 B6 brackets/non-English / `markdown_link_label` | `What does osimertinib target?` | `[osimertinib is safe](osimertinib) acts on EGFR.` | `grounded=False`; `[('wording', 'safe')]` |
| R1 B6 brackets/non-English / `korean_only` | `What does osimertinib target?` | `오시머티닙은 안전하며 부작용이 없다.` | `grounded=False`; `[('unreadable', '오시머티닙은 안전하며 부작용이 없다.')]` |
| R1 B6 brackets/non-English / `korean_mixed_relation` | `What does osimertinib target?` | `osimertinib 은 EGFR 을 억제하지 않는다.` | `grounded=False`; `[('unreadable', 'osimertinib 은 EGFR 을 억제하지 않는다.')]` |
| R1 B7 clinical grammar/action / `plain_clinical_grammar` | `What does osimertinib target?` | `Osimertinib is a treatment for all cancer.` | `grounded=False`; `[('wording', 'all'), ('wording', 'cancer'), ('wording', 'treatment')]` |
| R1 B7 clinical grammar/action / `activator_as_inhibitor` | `What does omaveloxolone target?` | `Omaveloxolone inhibits NFE2L2.` | `grounded=False`; `[('action', 'OMAVELOXOLONE inhibits NFE2L2')]` |
| R1 B8 numeric layouts / `phase_13_regex` | `Which drugs act on ALK?` | `PLB1003 is phase 13.` | `grounded=False`; `[('phase', 'phase 13')]` |
| R1 B8 numeric layouts / `phase_suffix` | `What trials evaluate Tagrisso?` | `NCT07680790 is phase 3b.` | `grounded=False`; `[('phase', 'phase 3b')]` |
| R1 B8 numeric layouts / `count_long_unit` | `Which drugs act on ALK?` | `PLB1003 has 13 non small cell lung cancer trials.` | `grounded=False`; `[('number', '13')]` |
| R1 B8 numeric layouts / `count_after_colon_list` | `Which drugs act on ALK?` | `- PLB1003: NSCLC trials: 13\n- lorlatinib: NSCLC trials: 0` | `grounded=False`; `[('number', '0'), ('number', '13'), ('indication', 'lung cancer'), ('wording', 'trials')]` |
| R2 B1 reversed noun/cleft / `reverse_noun` | `What does osimertinib target?` | `EGFR is an osimertinib inhibitor.` | `grounded=False`; `[('relation_direction', 'EGFR inhibitor OSIMERTINIB')]` |
| R2 B1 reversed noun/cleft / `passive_cleft` | `What does osimertinib target?` | `EGFR is what inhibited osimertinib.` | `grounded=False`; `[('relation_direction', 'EGFR inhibited OSIMERTINIB')]` |
| R2 B1 reversed noun/cleft / `passive_cleft_trial` | `What trials evaluate Tagrisso?` | `Osimertinib is what evaluated NCT03909334.` | `grounded=False`; `[('relation_direction', 'OSIMERTINIB evaluated NCT03909334')]` |
| R2 B1 reversed noun/cleft / `passive_cleft_sponsor` | `What is AstraZeneca running in NSCLC?` | `Osimertinib is what sponsored AstraZeneca.` | `grounded=False`; `[('relation_direction', 'OSIMERTINIB sponsored Astrazeneca')]` |
| R2 B2 hidden extra endpoint / `endpoint_preposition` | `What does osimertinib target?` | `Osimertinib acts on EGFR and on ALK.` | `grounded=False`; `[('relation', 'OSIMERTINIB — acts — ALK')]` |
| R2 B2 hidden extra endpoint / `endpoint_noun` | `What does osimertinib target?` | `Osimertinib is an inhibitor of EGFR and of ALK.` | `grounded=False`; `[('relation', 'OSIMERTINIB — inhibitor — ALK')]` |
| R2 B2 hidden extra endpoint / `endpoint_adverb` | `What does osimertinib target?` | `Osimertinib inhibits EGFR and also ALK.` | `grounded=False`; `[('relation', 'OSIMERTINIB — inhibits — ALK')]` |
| R2 B2 hidden extra endpoint / `noun_target_second` | `What does osimertinib target? + What does crizotinib target?` | `EGFR is a target of osimertinib and of crizotinib.` | `grounded=False`; `[('relation', 'CRIZOTINIB — target — EGFR')]` |
| R2 B3 pronoun timing/verbatim trial / `pronoun_stale` | `What does osimertinib target? + What does crizotinib target?` | `Osimertinib acts on EGFR. Crizotinib acts on ALK and it inhibits EGFR.` | `grounded=False`; `[('relation', 'CRIZOTINIB — inhibits — EGFR')]` |
| R2 B3 pronoun timing/verbatim trial / `pronoun_stale2` | `What does osimertinib target? + What does crizotinib target?` | `Osimertinib acts on EGFR. Crizotinib acts on ALK while this drug inhibits EGFR.` | `grounded=False`; `[('relation', 'CRIZOTINIB — inhibits — EGFR')]` |
| R2 B3 pronoun timing/verbatim trial / `verbatim_antecedent_trial` | `What trials evaluate Tagrisso?` | `NCT03909334 (PHASE2, ACTIVE_NOT_RECRUITING) evaluates OSIMERTINIB. It is phase 3.` | `grounded=False`; `[('phase', 'phase 3')]` |
| R2 B4 numeric ownership/count slots / `number_drug_other` | `What is AstraZeneca running in NSCLC?` | `AstraZeneca sponsors osimertinib in 10 trials with carboplatin.` | `grounded=False`; `[('unrelated_entity', 'CARBOPLATIN'), ('count_ambiguous', 'OSIMERTINIB / CARBOPLATIN')]` |
| R2 B4 numeric ownership/count slots / `count_morph` | `Which drugs act on ALK?` | `PLB1003 has 1 clinical trial.` | `grounded=False`; `[('number', '1')]` |
| R2 B5 action substring / `action_antagonist` | `What does fulvestrant target?` | `Fulvestrant activates ESR1.` | `grounded=False`; `[('action', 'FULVESTRANT activates ESR1')]` |
| R2 B5 action substring / `action_noun_agonist` | `What does fulvestrant target?` | `Fulvestrant is an agonist of ESR1.` | `grounded=False`; `[('action', 'FULVESTRANT agonist ESR1')]` |
| R2 B6 headings / `discarded_heading` | `What does osimertinib target?` | `osimertinib is safe:` | `grounded=False`; `[('wording', 'safe')]` |
| R2 B6 headings / `discarded_heading_before_prose` | `What does osimertinib target?` | `osimertinib is discontinued:\nOsimertinib acts on EGFR.` | `grounded=False`; `[('wording', 'discontinued')]` |
| R2 B6 headings / `verbatim_under_unsafe_heading` | `What does osimertinib target?` | `these drugs are safe:\n- OSIMERTINIB acts on EGFR (inhibitor)` | `grounded=False`; `[('wording', 'safe')]` |
| R2 B6 headings / `verbatim_under_negated_heading` | `What does osimertinib target?` | `these drugs do not act on EGFR:\n- OSIMERTINIB acts on EGFR (inhibitor)` | `grounded=False`; `[('negation', 'not')]` |
| R2 B6 headings / `verbatim_under_reversed_heading` | `What does osimertinib target?` | `EGFR acts on these drugs:\n- OSIMERTINIB acts on EGFR (inhibitor)` | `grounded=False`; `[('relation_direction', 'EGFR acts OSIMERTINIB')]` |
| R2 B7 META clinical claims / `meta_france_unsupported_phase` | `What is the capital of France?` | `This trial is phase 4.` | `grounded=False`; `[('no_antecedent', 'this trial')]` |
| R2 B7 META clinical claims / `meta_missing_typed_phase` | `What trials evaluate Tagrisso?` | `This trial is phase 3.` | `grounded=False`; `[('no_antecedent', 'this trial')]` |
| R2 B7 META clinical claims / `meta_missing_negation` | `What trials evaluate Tagrisso?` | `This drug is not in trials.` | `grounded=False`; `[('negation', 'not')]` |
| R2 B7 META clinical claims / `meta_missing_count` | `Which companies are developing osimertinib?` | `It has 14 trials.` | `grounded=False`; `[('number', '14')]` |
| R2 B8 refused spans / `refused_liposomal` | `What does osimertinib target?` | `osimertinib is liposomal.` | `grounded=False`; `[('distinct_product', 'is liposomal')]` |
| R2 B8 refused spans / `refused_biosimilar` | `What does osimertinib target?` | `osimertinib is a biosimilar.` | `grounded=False`; `[('distinct_product', 'a biosimilar')]` |
| R2 B8 refused spans / `refused_negation` | `What does osimertinib target?` | `Osimertinib is not liposomal.` | `grounded=False`; `[('distinct_product', 'not liposomal')]` |
| R2 B8 refused spans / `refused_alias` | `What does osimertinib target?` | `liposomal Tagrisso.` | `grounded=False`; `[('distinct_product', 'liposomal Tagrisso')]` |
| R2 B9 ORG citation content / `citation_embedded_claim` | `What does osimertinib target?` | `Osimertinib [ORG:is safe] acts on EGFR.` | `grounded=False`; `[('wording', 'org'), ('wording', 'safe')]` |
| R2 B9 ORG citation content / `citation_embedded_wrong_relation` | `What does osimertinib target?` | `Osimertinib [ORG:inhibits ALK and] acts on EGFR.` | `grounded=False`; `[('relation', 'OSIMERTINIB — inhibits — ALK'), ('wording', 'org')]` |
| R3 B1 plural pronouns / `pronoun_same_clause` | `Which drugs act on ALK?` | `LORLATINIB and PLB1003 act on ALK and they are approved.` | `grounded=False`; `[('wording', 'approved')]` |
| R3 B1 plural pronouns / `pronoun_two_sentences` | `Which drugs act on ALK?` | `LORLATINIB and PLB1003 act on ALK. they are approved.` | `grounded=False`; `[('wording', 'approved')]` |
| R3 B2 count borrowing / `count_swap_tail` | `What is AstraZeneca running in NSCLC?` | `AstraZeneca sponsors osimertinib in 10 trials evaluating carboplatin.` | `grounded=False`; `[('count_ambiguous', 'OSIMERTINIB / CARBOPLATIN')]` |
| R3 B2 count borrowing / `count_coordinated` | `What is AstraZeneca running in NSCLC?` | `AstraZeneca sponsors 10 trials evaluating carboplatin and osimertinib.` | `grounded=False`; `[('count_ambiguous', 'CARBOPLATIN / OSIMERTINIB')]` |
| R3 B2 count borrowing / `count_shared_group` | `What is AstraZeneca running in NSCLC?` | `AstraZeneca sponsors osimertinib and carboplatin in 10 trials.` | `grounded=False`; `[('count_ambiguous', 'OSIMERTINIB / CARBOPLATIN')]` |
| R3 B3 headings / `heading_sponsors_full` | `What does osimertinib target?` | `these drugs are sponsors of trials:\n- OSIMERTINIB acts on EGFR (inhibitor)` | `grounded=False`; `[('relation_incomplete', 'sponsors'), ('wording', 'trials')]` |
| R3 B3 headings / `heading_activators_full` | `What does osimertinib target?` | `these drugs are activators:\n- OSIMERTINIB acts on EGFR (inhibitor)` | `grounded=False`; `[('relation_incomplete', 'activators')]` |
| R3 B3 headings / `heading_with_alk` | `What does osimertinib target?` | `these drugs inhibit EGFR with ALK:\n- OSIMERTINIB acts on EGFR (inhibitor)` | `grounded=False`; `[('unrelated_entity', 'ALK')]` |
| R3 B4 clinical/kind/identity / `clinical_trial_unsupported` | `What does osimertinib target?` | `Osimertinib is in clinical trials.` | `grounded=False`; `[('wording', 'clinical'), ('wording', 'trials')]` |
| R3 B4 clinical/kind/identity / `nsclc_trial_unsupported` | `What does osimertinib target?` | `Osimertinib is in NSCLC trials.` | `grounded=False`; `[('indication', 'lung cancer'), ('wording', 'trials')]` |
| R3 B4 clinical/kind/identity / `indication_drug` | `What does osimertinib target?` | `Osimertinib is an NSCLC drug.` | `grounded=False`; `[('indication', 'lung cancer')]` |
| R3 B4 clinical/kind/identity / `focused_07` | `What does osimertinib target?` | `EGFR is a drug.` | `grounded=False`; `[('wording', 'drug')]` |
| R3 B4 clinical/kind/identity / `zero_evidence_clinical` | `What is the capital of France?` | `There are clinical trials.` | `grounded=False`; `[('no_subject', 'clinical trials')]` |
| R3 B4 clinical/kind/identity / `fragment_drug_identity` | `Which drugs act on ALK?` | `PLB1003 is LORLATINIB.` | `grounded=False`; `[('identity', 'PLB1003 = LORLATINIB')]` |
| R3 B4 clinical/kind/identity / `fragment_trial_identity` | `What trials evaluate Tagrisso?` | `NCT03909334 is NCT07680790.` | `grounded=False`; `[('identity', 'NCT03909334 = NCT07680790')]` |
| R3 weaker count-after-colon / `unknown_number_only` | `Which drugs act on ALK?` | `PLB1003 has NSCLC trials: 1.` | `grounded=False`; `[('number', '1'), ('indication', 'lung cancer'), ('wording', 'trials')]` |
| R3 weaker approval-in-NSCLC / `indication_approved_in` | `Which drugs act on ALK?` | `LORLATINIB is approved in NSCLC.` | `grounded=False`; `[('indication', 'lung cancer')]` |
| R3 weaker id-shaped citations / `focused_18` | `What does osimertinib target?` | `Osimertinib [ORG:is-safe] acts on EGFR.` | `grounded=False`; `[('wording', 'org'), ('wording', 'safe')]` |
| R3 weaker id-shaped citations / `focused_19` | `What does osimertinib target?` | `Osimertinib [ORG:inhibits-ALK] acts on EGFR.` | `grounded=False`; `[('wording', 'alk'), ('wording', 'org')]` |
| R3 weaker id-shaped citations / `focused_20` | `What does osimertinib target?` | `Osimertinib [ORG:does-not-inhibit] acts on EGFR.` | `grounded=False`; `[('negation', 'not'), ('wording', 'org')]` |

## Prior faithful-corpus replay

| Question | Original R1 corpus pass | R3 added corpus pass |
|---|---|---|
| Which companies are developing osimertinib? | 6/6 | 5/6 |
| What trials evaluate Tagrisso? | 6/6 | 6/6 |
| What does osimertinib target? | 6/6 | 6/6 |
| Which drugs act on ALK? | 6/6 | 6/6 |
| What is AstraZeneca running in NSCLC? | 5/6 | 6/6 |
| What is the capital of France? | 4/6 | 5/6 |

Remaining faithful/refusal failures (diagnostic hand-authored samples, not production rates):

- `faithful_results/Q5P4`: `What is AstraZeneca running in NSCLC?` / `AstraZeneca supports trials studying osimertinib in NSCLC.` -> False; `[('unrelated_entity', 'Astrazeneca'), ('wording', 'supports')]`.
- `faithful_results/Q6P3`: `What is the capital of France?` / `The graph covers NSCLC drugs and trials, so it cannot answer this question.` -> False; `[('no_antecedent', 'it')]`.
- `faithful_results/Q6P6`: `What is the capital of France?` / `I cannot determine the capital of France from the retrieved evidence.` -> False; `[('entity', 'France'), ('no_subject', 'i cannot determine capital france')]`.
- `docs3_probe_results/faithful_05`: `Which companies are developing osimertinib?` / `AstraZeneca sponsors 14 trials of osimertinib. This is evidence of sponsorship, not evidence that it develops the drug.` -> False; `[('identity', 'Astrazeneca = OSIMERTINIB'), ('development_claim', 'develops'), ('negation', 'not')]`.
- `docs3_probe_results/faithful_33`: `What is the capital of France?` / `I cannot determine the capital of France from the retrieved evidence.` -> False; `[('entity', 'France'), ('no_subject', 'i cannot determine capital france')]`.

R3 S1 exact specifically cited faithful repairs:

- **FIXED** `What does osimertinib target?` / `Osimertinib targets EGFR and inhibits it.` -> `True`; `[]`.
- **FIXED** `What trials evaluate Tagrisso?` / `NCT03909334 evaluates osimertinib in phase 2.` -> `True`; `[]`.
- **FIXED** `What trials evaluate Tagrisso?` / `NCT03909334 is a phase II trial evaluating osimertinib.` -> `True`; `[]`.
- **FIXED** `What is AstraZeneca running in NSCLC?` / `AstraZeneca sponsors 14 NSCLC trials evaluating osimertinib and 10 NSCLC trials evaluating carboplatin.` -> `True`; `[]`.
- **FIXED** `What does osimertinib target?` / `AZD9291 (AZD-9291) acts on EGFR.` -> `True`; `[]`.
- **FIXED** `What does osimertinib target?` / `Osimertinib (Tagrisso, AZD 9291, AZD9291) acts on EGFR.` -> `True`; `[]`.

## Regression run

........................................................................ [ 33%]
........................................................................ [ 67%]
.....................................................................    [100%]
213 passed in 7.78s

Bytecode and pytest cache writes disabled; TEMP/TMP confined to `r4/replay4_temp`.

## Prior SHOULD FIX and NOTES dispositions

| Prior finding | Disposition | Fresh evidence |
|---|---|---|
| R1 faithful paraphrases/refusals | **NOT FIXED overall**, much improved | Original corpus: 29/30 evidence answers and 4/6 refusals pass; exact remaining inputs are above. |
| R1 Cartesian-product pairing | **FIXED** | All three faithful same-sentence pairs and all three split-sentence pairs pass; all three swapped pairs fail (`replay4_adversarial_pairs_results.json`). |
| R1 distinct-sentence dedup | **FIXED** | `Osimertinib is safe. EGFR is safe.` is False and retains two sentence-specific `wording: safe` findings (`repeat_safe_dedup`). |
| R2 S1 faithful forms/refusals | **NOT FIXED overall** | The original supports/refusal failures remain. All three specifically reported inline-pronoun, repeated-alias and spaced-code inputs now pass. |
| R3 S1 faithful forms/refusals | **NOT FIXED overall**; all six specifically cited repairs **FIXED** | R3 corpus improves from 24/30 to 29/30 evidence answers and 2/6 to 5/6 refusals. Exact repaired and remaining inputs are above. |
| R1 docs / R2 S2 / R3 S2 | **NOT FIXED overall** under the parent round-4 audit | The old universal phrasing and exact historical attack omissions were repaired. New known residues found by the parent documentation/adversarial review require separate evaluation; the replay alone does not establish documentation completeness. |

Exact repaired R2 S1 inputs (all Q3): `Osimertinib acts on EGFR and it inhibits EGFR.`, `Osimertinib (Tagrisso) acts on EGFR.`, `AZD 9291 acts on EGFR.` All now return `grounded=True`, `unsupported_claims=[]`.

Same-unit dedup remains a NOTE: `Osimertinib is safe and EGFR is safe.` is False with one final safe finding although raw `check_claims` has two. Dedup does not turn the nonempty finding list into a pass.

## Templates, dictionary and additional replay controls

- All **5/5 evidence template bodies** pass generated-prose checking after the same `Scope:` removal used by the normal query path. The changed headings are included in these full prose inputs; they were not manually removed. All five Scope-inclusive templates still fail as in previous rounds. Full exact inputs and outputs are in `replay4_faithful_results.json` under `templates`.
- The sixth query is the France question. Its normal `ask()` refusal check passes, but checking its template as generated prose still fails. This unchanged limitation is separate from the five evidence templates.
- Dictionary gate: **7,610 keys / 1,066 drugs / 2,634 unique multiword aliases**, zero lost intended links. `is a` is unlinked; `AZD 9291`, `osimertinib mesylate`, `trastuzumab deruxtecan`, and `pemetrexed disodium` keep intended links (`replay4_code_dictionary.json`).
- Dictionary-to-tokenizer replay: **2,566/2,634** aliases link an intended ID; five unchanged tokenization discrepancies remain (two parenthesized chemical names and three parent/salt overlaps). `replay4_r3_numeric3_dictionary.json` and the R2 standards replay contain exact cases. This is not a new round-4 regression.
- Question punctuation is unchanged: `Which drugs act on ALK!`, `Which drugs act on ALK:`, and `Which drugs act on ALK;` link no target. The normal `?` works. Answer punctuation is a separate path; `Osimertinib acts on EGFR!` passes.
- Evidence-consistent prior diagnostic passes are NOTES, not blockers: `Osimertinib was inhibiting EGFR.`, `EGFR has been inhibited by osimertinib.`, `Osimertinib is an EGFR blocker.`, and `Osimertinib is evaluated at NCT03909334.`. The malformed `Osimertinib is the inhibition of EGFR.` reuses the sole supported statement and fits the stated one-statement rearrangement residue; it is not independently treated as an out-of-residue blocker.
- Original files were read only; all 14 copies, their logs/results/diffs and temporary test files are under `audit_evidence_claims/r4/`. `brief.md` and `log.txt` were not edited. Tracked/staged diffs remain empty.

## Reproduction

From the repository root, run `powershell -NoProfile -File audit_evidence_claims/r4/replay4_reproduce.ps1`. It reruns all 14 historical scripts and the 213-test regression command, then rebuilds this report and the input-identity assertions. No historical files are overwritten.
