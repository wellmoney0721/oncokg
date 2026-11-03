# Exact R1-R4 replay at 9fda6f8

All 23 original probe scripts were run via adapted copies. Six R1, three R2, five R3 and nine R4 scripts preserve exact questions, answers, case IDs and retrieval modes. Input identity is asserted against original saved outputs; historical classification follows the reports because some old result files were overwritten during repairs. Source SHA-256 hashes, adaptation diffs, full results and logs accompany this report. The only behavioral adaptation is disabling the R4 confirmation script assertion that outcomes must remain equal to obsolete R4 outcomes; its historic expected values remain as metadata. The earlier obsolete internal `_tokenise` call signature is also adapted.

**606 input-identity-checked answer cases**: R1: 142, R2: 104, R3: 192, R4: 168. Four additional citation transformations, templates and dictionary experiments were also replayed.
FIXED means all exact reported reproductions listed below are corrected, not that every variant of the mechanism is safe.

| Prior finding | Result | Exact prior attacks still passing |
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
| R4 B1 heading adjective erasure | **FIXED** | 0/4 |
| R4 B2 plural chaining/object/elision | **FIXED** | 0/3 |
| R4 B3 count after trial label | **FIXED** | 0/1 |
| R4 B4 shared trial phase/status | **FIXED** | 0/3 |
| R4 B5 kind/clinical ownership | **FIXED** | 0/2 |
| R4 B6 spelled-out letters | **FIXED** | 0/2 |
| R4 weaker NSCLC/identity/percentage residues | **FIXED** | 0/3 |
| R4 additional phase-as-figure diagnostic | **FIXED** | 0/1 |

## Exact previously reported attacks and fresh findings

| Finding / case | Exact question(s) | Exact answer | Fresh output |
|---|---|---|---|
| R1 B1 direction/endpoints / `adversarial_results/reversed_target` | `What does osimertinib target?` | `EGFR acts on osimertinib.` | `grounded=False`; `[('relation_direction', 'EGFR acts OSIMERTINIB')]` |
| R1 B1 direction/endpoints / `main_results/reverse_noun` | `What does osimertinib target?` | `EGFR is an osimertinib inhibitor.` | `grounded=False`; `[('relation_direction', 'EGFR inhibitor OSIMERTINIB')]` |
| R1 B1 direction/endpoints / `adversarial_results/reversed_trial` | `What trials evaluate Tagrisso?` | `osimertinib evaluates NCT03909334.` | `grounded=False`; `[('relation_direction', 'OSIMERTINIB evaluates NCT03909334')]` |
| R1 B1 direction/endpoints / `adversarial_results/reversed_sponsor` | `What is AstraZeneca running in NSCLC?` | `osimertinib sponsors AstraZeneca.` | `grounded=False`; `[('relation_direction', 'OSIMERTINIB sponsors Astrazeneca')]` |
| R1 B1 direction/endpoints / `main_results/wrong_type_relation` | `What does osimertinib target?` | `Osimertinib sponsors EGFR.` | `grounded=False`; `[('relation_direction', 'OSIMERTINIB sponsors EGFR')]` |
| R1 B2 pronoun subject loss / `adversarial_results/pronoun_target_same_line` | `What does osimertinib target?` | `osimertinib acts on EGFR. It inhibits ALK.` | `grounded=False`; `[('relation', 'OSIMERTINIB — inhibits — ALK')]` |
| R1 B2 pronoun subject loss / `adversarial_results/pronoun_target_newline` | `What does osimertinib target?` | `osimertinib acts on EGFR.\nIt inhibits ALK.` | `grounded=False`; `[('relation', 'OSIMERTINIB — inhibits — ALK')]` |
| R1 B2 pronoun subject loss / `adversarial_results/pronoun_this_drug` | `What does osimertinib target?` | `osimertinib acts on EGFR. This drug inhibits ALK.` | `grounded=False`; `[('relation', 'OSIMERTINIB — inhibits — ALK')]` |
| R1 B2 pronoun subject loss / `adversarial_results/trial_pronoun_reset` | `What trials evaluate Tagrisso?` | `NCT03909334 evaluates osimertinib. It evaluates osimertinib and is phase 3.` | `grounded=False`; `[('phase', 'phase 3')]` |
| R1 B3 phase/status/count pooling / `adversarial_results/swapped_trial_phases` | `What trials evaluate Tagrisso?` | `NCT03909334 is phase 3 and NCT07680790 is phase 2.` | `grounded=False`; `[('phase', 'phase 2'), ('phase', 'phase 3')]` |
| R1 B3 phase/status/count pooling / `adversarial_results/pooled_trial_status2` | `What trials evaluate Tagrisso?` | `NCT03909334 and NCT07680790 are recruiting.` | `grounded=False`; `[('status', 'recruiting')]` |
| R1 B3 phase/status/count pooling / `adversarial_results/wrong_sponsor_count` | `What is AstraZeneca running in NSCLC?` | `AstraZeneca sponsors 10 NSCLC trials evaluating osimertinib.` | `grounded=False`; `[('number', '10')]` |
| R1 B3 phase/status/count pooling / `adversarial_results/wrong_drug_count_target` | `Which drugs act on ALK?` | `PLB1003 acts on ALK with 13 NSCLC trials.` | `grounded=False`; `[('number', '13')]` |
| R1 B3 phase/status/count pooling / `main_results/clinical_from_alk` | `Which drugs act on ALK?` | `PLB1003 is approved for all lung cancer and acts on ALK.` | `grounded=False`; `[('wording', 'all'), ('wording', 'approved'), ('indication', 'lung cancer')]` |
| R1 B4 bigram laundering / `main_results/quoted_developing` | `Which companies are developing osimertinib?` | `AstraZeneca is developing the drug osimertinib.` | `grounded=False`; `[('identity', 'Astrazeneca = OSIMERTINIB'), ('development_claim', 'developing'), ('wording', 'drug')]` |
| R1 B4 bigram laundering / `main_results/quoted_developing_2` | `Which companies are developing osimertinib?` | `AstraZeneca has evidence of developing osimertinib.` | `grounded=False`; `[('identity', 'Astrazeneca = OSIMERTINIB'), ('development_claim', 'developing')]` |
| R1 B4 bigram laundering / `main_results/quoted_absence_natural` | `Which companies are developing osimertinib?` | `This is not evidence that AstraZeneca sponsors osimertinib.` | `grounded=False`; `[('negation', 'not')]` |
| R1 B5 non- negation / `main_results/non_inhibitor` | `What does osimertinib target?` | `Osimertinib is a non-inhibitor of EGFR.` | `grounded=False`; `[('negation', 'non')]` |
| R1 B5 non- negation / `main_results/non_hyphen` | `What trials evaluate Tagrisso?` | `NCT07680790 is non-recruiting.` | `grounded=False`; `[('negation', 'non')]` |
| R1 B6 brackets/non-English / `main_results/square_bracket_claim` | `What does osimertinib target?` | `Osimertinib [is safe and discontinued] acts on EGFR.` | `grounded=False`; `[('wording', 'discontinued'), ('wording', 'safe')]` |
| R1 B6 brackets/non-English / `main_results/markdown_link_label` | `What does osimertinib target?` | `[osimertinib is safe](osimertinib) acts on EGFR.` | `grounded=False`; `[('wording', 'safe')]` |
| R1 B6 brackets/non-English / `main_results/korean_only` | `What does osimertinib target?` | `오시머티닙은 안전하며 부작용이 없다.` | `grounded=False`; `[('unreadable', '오시머티닙은 안전하며 부작용이 없다.')]` |
| R1 B6 brackets/non-English / `main_results/korean_mixed_relation` | `What does osimertinib target?` | `osimertinib 은 EGFR 을 억제하지 않는다.` | `grounded=False`; `[('unreadable', 'osimertinib 은 EGFR 을 억제하지 않는다.')]` |
| R1 B7 clinical grammar/action / `main_results/plain_clinical_grammar` | `What does osimertinib target?` | `Osimertinib is a treatment for all cancer.` | `grounded=False`; `[('wording', 'all'), ('wording', 'cancer'), ('wording', 'treatment')]` |
| R1 B7 clinical grammar/action / `main_results/activator_as_inhibitor` | `What does omaveloxolone target?` | `Omaveloxolone inhibits NFE2L2.` | `grounded=False`; `[('action', 'OMAVELOXOLONE inhibits NFE2L2')]` |
| R1 B8 numeric layouts / `adversarial_pairs_results/phase_13_regex` | `Which drugs act on ALK?` | `PLB1003 is phase 13.` | `grounded=False`; `[('phase', 'phase 13')]` |
| R1 B8 numeric layouts / `code_probes/phase_suffix` | `What trials evaluate Tagrisso?` | `NCT07680790 is phase 3b.` | `grounded=False`; `[('phase', 'phase 3b')]` |
| R1 B8 numeric layouts / `adversarial_results/count_long_unit` | `Which drugs act on ALK?` | `PLB1003 has 13 non small cell lung cancer trials.` | `grounded=False`; `[('number', '13')]` |
| R1 B8 numeric layouts / `adversarial_pairs_results/count_after_colon_list` | `Which drugs act on ALK?` | `- PLB1003: NSCLC trials: 13\n- lorlatinib: NSCLC trials: 0` | `grounded=False`; `[('number', '0'), ('number', '13'), ('indication', 'lung cancer'), ('wording', 'trials')]` |
| R2 B1 reversed noun/cleft / `main_results/reverse_noun` | `What does osimertinib target?` | `EGFR is an osimertinib inhibitor.` | `grounded=False`; `[('relation_direction', 'EGFR inhibitor OSIMERTINIB')]` |
| R2 B1 reversed noun/cleft / `spec_probe_results/passive_cleft` | `What does osimertinib target?` | `EGFR is what inhibited osimertinib.` | `grounded=False`; `[('relation_direction', 'EGFR inhibited OSIMERTINIB')]` |
| R2 B1 reversed noun/cleft / `spec_probe_results/passive_cleft_trial` | `What trials evaluate Tagrisso?` | `Osimertinib is what evaluated NCT03909334.` | `grounded=False`; `[('relation_direction', 'OSIMERTINIB evaluated NCT03909334')]` |
| R2 B1 reversed noun/cleft / `spec_probe_results/passive_cleft_sponsor` | `What is AstraZeneca running in NSCLC?` | `Osimertinib is what sponsored AstraZeneca.` | `grounded=False`; `[('relation_direction', 'OSIMERTINIB sponsored Astrazeneca')]` |
| R2 B2 hidden extra endpoint / `spec_probe_results/endpoint_preposition` | `What does osimertinib target?` | `Osimertinib acts on EGFR and on ALK.` | `grounded=False`; `[('relation', 'OSIMERTINIB — acts — ALK')]` |
| R2 B2 hidden extra endpoint / `spec_probe_results/endpoint_noun` | `What does osimertinib target?` | `Osimertinib is an inhibitor of EGFR and of ALK.` | `grounded=False`; `[('relation', 'OSIMERTINIB — inhibitor — ALK')]` |
| R2 B2 hidden extra endpoint / `spec_probe_results/endpoint_adverb` | `What does osimertinib target?` | `Osimertinib inhibits EGFR and also ALK.` | `grounded=False`; `[('relation', 'OSIMERTINIB — inhibits — ALK')]` |
| R2 B2 hidden extra endpoint / `spec_probe_results/noun_target_second` | `What does osimertinib target? + What does crizotinib target?` | `EGFR is a target of osimertinib and of crizotinib.` | `grounded=False`; `[('relation', 'CRIZOTINIB — target — EGFR')]` |
| R2 B3 pronoun timing/verbatim trial / `spec_probe_results/pronoun_stale` | `What does osimertinib target? + What does crizotinib target?` | `Osimertinib acts on EGFR. Crizotinib acts on ALK and it inhibits EGFR.` | `grounded=False`; `[('relation', 'CRIZOTINIB — inhibits — EGFR')]` |
| R2 B3 pronoun timing/verbatim trial / `spec_probe_results/pronoun_stale2` | `What does osimertinib target? + What does crizotinib target?` | `Osimertinib acts on EGFR. Crizotinib acts on ALK while this drug inhibits EGFR.` | `grounded=False`; `[('relation', 'CRIZOTINIB — inhibits — EGFR')]` |
| R2 B3 pronoun timing/verbatim trial / `root_design_probe/verbatim_antecedent_trial` | `What trials evaluate Tagrisso?` | `NCT03909334 (PHASE2, ACTIVE_NOT_RECRUITING) evaluates OSIMERTINIB. It is phase 3.` | `grounded=False`; `[('phase', 'phase 3')]` |
| R2 B4 numeric ownership/count slots / `spec_probe_results/number_drug_other` | `What is AstraZeneca running in NSCLC?` | `AstraZeneca sponsors osimertinib in 10 trials with carboplatin.` | `grounded=False`; `[('unrelated_entity', 'CARBOPLATIN'), ('count_ambiguous', 'OSIMERTINIB / CARBOPLATIN')]` |
| R2 B4 numeric ownership/count slots / `spec_probe_results/count_morph` | `Which drugs act on ALK?` | `PLB1003 has 1 clinical trial.` | `grounded=False`; `[('number', '1')]` |
| R2 B5 action substring / `spec_probe_results/action_antagonist` | `What does fulvestrant target?` | `Fulvestrant activates ESR1.` | `grounded=False`; `[('action', 'FULVESTRANT activates ESR1')]` |
| R2 B5 action substring / `spec_probe_results/action_noun_agonist` | `What does fulvestrant target?` | `Fulvestrant is an agonist of ESR1.` | `grounded=False`; `[('action', 'FULVESTRANT agonist ESR1')]` |
| R2 B6 headings / `root_design_probe/discarded_heading` | `What does osimertinib target?` | `osimertinib is safe:` | `grounded=False`; `[('wording', 'safe')]` |
| R2 B6 headings / `root_design_probe/discarded_heading_before_prose` | `What does osimertinib target?` | `osimertinib is discontinued:\nOsimertinib acts on EGFR.` | `grounded=False`; `[('wording', 'discontinued')]` |
| R2 B6 headings / `root_design_probe/verbatim_under_unsafe_heading` | `What does osimertinib target?` | `these drugs are safe:\n- OSIMERTINIB acts on EGFR (inhibitor)` | `grounded=False`; `[('wording', 'safe')]` |
| R2 B6 headings / `root_design_probe/verbatim_under_negated_heading` | `What does osimertinib target?` | `these drugs do not act on EGFR:\n- OSIMERTINIB acts on EGFR (inhibitor)` | `grounded=False`; `[('negation', 'not')]` |
| R2 B6 headings / `root_design_probe/verbatim_under_reversed_heading` | `What does osimertinib target?` | `EGFR acts on these drugs:\n- OSIMERTINIB acts on EGFR (inhibitor)` | `grounded=False`; `[('relation_direction', 'EGFR acts OSIMERTINIB')]` |
| R2 B7 META clinical claims / `root_design_probe/meta_france_unsupported_phase` | `What is the capital of France?` | `This trial is phase 4.` | `grounded=False`; `[('no_antecedent', 'this trial')]` |
| R2 B7 META clinical claims / `root_design_probe/meta_missing_typed_phase` | `What trials evaluate Tagrisso?` | `This trial is phase 3.` | `grounded=False`; `[('no_antecedent', 'this trial')]` |
| R2 B7 META clinical claims / `root_design_probe/meta_missing_negation` | `What trials evaluate Tagrisso?` | `This drug is not in trials.` | `grounded=False`; `[('negation', 'not')]` |
| R2 B7 META clinical claims / `root_design_probe/meta_missing_count` | `Which companies are developing osimertinib?` | `It has 14 trials.` | `grounded=False`; `[('number', '14')]` |
| R2 B8 refused spans / `standards_probe/refused_liposomal` | `What does osimertinib target?` | `osimertinib is liposomal.` | `grounded=False`; `[('distinct_product', 'is liposomal')]` |
| R2 B8 refused spans / `standards_probe/refused_biosimilar` | `What does osimertinib target?` | `osimertinib is a biosimilar.` | `grounded=False`; `[('identity', 'OSIMERTINIB'), ('distinct_product', 'a biosimilar')]` |
| R2 B8 refused spans / `standards_probe/refused_negation` | `What does osimertinib target?` | `Osimertinib is not liposomal.` | `grounded=False`; `[('identity', 'OSIMERTINIB'), ('distinct_product', 'not liposomal')]` |
| R2 B8 refused spans / `standards_probe/refused_alias` | `What does osimertinib target?` | `liposomal Tagrisso.` | `grounded=False`; `[('distinct_product', 'liposomal Tagrisso')]` |
| R2 B9 ORG citation content / `root_design_probe/citation_embedded_claim` | `What does osimertinib target?` | `Osimertinib [ORG:is safe] acts on EGFR.` | `grounded=False`; `[('wording', 'org'), ('wording', 'safe')]` |
| R2 B9 ORG citation content / `root_design_probe/citation_embedded_wrong_relation` | `What does osimertinib target?` | `Osimertinib [ORG:inhibits ALK and] acts on EGFR.` | `grounded=False`; `[('relation', 'OSIMERTINIB — inhibits — ALK'), ('wording', 'org')]` |
| R3 B1 plural pronouns / `root3_probe/pronoun_same_clause` | `Which drugs act on ALK?` | `LORLATINIB and PLB1003 act on ALK and they are approved.` | `grounded=False`; `[('wording', 'approved')]` |
| R3 B1 plural pronouns / `root3_probe/pronoun_two_sentences` | `Which drugs act on ALK?` | `LORLATINIB and PLB1003 act on ALK. they are approved.` | `grounded=False`; `[('wording', 'approved')]` |
| R3 B2 count borrowing / `numeric3_probe/count_swap_tail` | `What is AstraZeneca running in NSCLC?` | `AstraZeneca sponsors osimertinib in 10 trials evaluating carboplatin.` | `grounded=False`; `[('count_ambiguous', 'OSIMERTINIB / CARBOPLATIN')]` |
| R3 B2 count borrowing / `numeric3_probe/count_coordinated` | `What is AstraZeneca running in NSCLC?` | `AstraZeneca sponsors 10 trials evaluating carboplatin and osimertinib.` | `grounded=False`; `[('count_ambiguous', 'CARBOPLATIN / OSIMERTINIB')]` |
| R3 B2 count borrowing / `root3_probe/count_shared_group` | `What is AstraZeneca running in NSCLC?` | `AstraZeneca sponsors osimertinib and carboplatin in 10 trials.` | `grounded=False`; `[('count_ambiguous', 'OSIMERTINIB / CARBOPLATIN')]` |
| R3 B3 headings / `root3_probe/heading_sponsors_full` | `What does osimertinib target?` | `these drugs are sponsors of trials:\n- OSIMERTINIB acts on EGFR (inhibitor)` | `grounded=False`; `[('relation_incomplete', 'sponsors'), ('wording', 'trials')]` |
| R3 B3 headings / `root3_probe/heading_activators_full` | `What does osimertinib target?` | `these drugs are activators:\n- OSIMERTINIB acts on EGFR (inhibitor)` | `grounded=False`; `[('relation_incomplete', 'activators')]` |
| R3 B3 headings / `root3_probe/heading_with_alk` | `What does osimertinib target?` | `these drugs inhibit EGFR with ALK:\n- OSIMERTINIB acts on EGFR (inhibitor)` | `grounded=False`; `[('unrelated_entity', 'ALK')]` |
| R3 B4 clinical/kind/identity / `root3_probe/clinical_trial_unsupported` | `What does osimertinib target?` | `Osimertinib is in clinical trials.` | `grounded=False`; `[('wording', 'clinical'), ('wording', 'trials')]` |
| R3 B4 clinical/kind/identity / `root3_probe/nsclc_trial_unsupported` | `What does osimertinib target?` | `Osimertinib is in NSCLC trials.` | `grounded=False`; `[('indication', 'lung cancer'), ('wording', 'trials')]` |
| R3 B4 clinical/kind/identity / `root3_probe/indication_drug` | `What does osimertinib target?` | `Osimertinib is an NSCLC drug.` | `grounded=False`; `[('indication', 'lung cancer')]` |
| R3 B4 clinical/kind/identity / `docs3_focused_results/focused_07` | `What does osimertinib target?` | `EGFR is a drug.` | `grounded=False`; `[('wording', 'drug')]` |
| R3 B4 clinical/kind/identity / `root3_probe/zero_evidence_clinical` | `What is the capital of France?` | `There are clinical trials.` | `grounded=False`; `[('no_subject', 'clinical trials')]` |
| R3 B4 clinical/kind/identity / `root3_probe/fragment_drug_identity` | `Which drugs act on ALK?` | `PLB1003 is LORLATINIB.` | `grounded=False`; `[('identity', 'PLB1003 = LORLATINIB')]` |
| R3 B4 clinical/kind/identity / `root3_probe/fragment_trial_identity` | `What trials evaluate Tagrisso?` | `NCT03909334 is NCT07680790.` | `grounded=False`; `[('identity', 'NCT03909334 = NCT07680790')]` |
| R3 weaker count-after-colon / `root3_probe/unknown_number_only` | `Which drugs act on ALK?` | `PLB1003 has NSCLC trials: 1.` | `grounded=False`; `[('number', '1'), ('indication', 'lung cancer'), ('wording', 'trials')]` |
| R3 weaker approval-in-NSCLC / `root3_probe/indication_approved_in` | `Which drugs act on ALK?` | `LORLATINIB is approved in NSCLC.` | `grounded=False`; `[('indication', 'lung cancer')]` |
| R3 weaker id-shaped citations / `docs3_focused_results/focused_18` | `What does osimertinib target?` | `Osimertinib [ORG:is-safe] acts on EGFR.` | `grounded=False`; `[('wording', 'org'), ('wording', 'safe')]` |
| R3 weaker id-shaped citations / `docs3_focused_results/focused_19` | `What does osimertinib target?` | `Osimertinib [ORG:inhibits-ALK] acts on EGFR.` | `grounded=False`; `[('wording', 'alk'), ('wording', 'org')]` |
| R3 weaker id-shaped citations / `docs3_focused_results/focused_20` | `What does osimertinib target?` | `Osimertinib [ORG:does-not-inhibit] acts on EGFR.` | `grounded=False`; `[('negation', 'not'), ('wording', 'org')]` |
| R4 B1 heading adjective erasure / `root4_confirmation/heading_safe` | `What does osimertinib target?` | `The following safe drugs:\n- OSIMERTINIB acts on EGFR (inhibitor).` | `grounded=False`; `[('wording', 'safe')]` |
| R4 B1 heading adjective erasure / `root4_confirmation/heading_discontinued` | `What does osimertinib target?` | `The following discontinued drugs:\n- OSIMERTINIB acts on EGFR (inhibitor).` | `grounded=False`; `[('wording', 'discontinued')]` |
| R4 B1 heading adjective erasure / `root4_confirmation/heading_safe_bare` | `What does osimertinib target?` | `The following safe drugs:\n- Osimertinib` | `grounded=False`; `[('wording', 'safe')]` |
| R4 B1 heading adjective erasure / `docs_controls_results/head_terminated` | `What trials evaluate Tagrisso?` | `The following terminated trials:\n- NCT07680790 (PHASE3, RECRUITING) evaluates OSIMERTINIB.` | `grounded=False`; `[('status', 'terminated')]` |
| R4 B2 plural chaining/object/elision / `root4_confirmation/plural_chain` | `Which drugs act on ALK?` | `PLB1003 and LORLATINIB act on ALK and they act on ALK and they are approved.` | `grounded=False`; `[('wording', 'approved')]` |
| R4 B2 plural chaining/object/elision / `root4_confirmation/plural_implicit` | `Which drugs act on ALK?` | `LORLATINIB and PLB1003 act on ALK and are approved.` | `grounded=False`; `[('wording', 'approved')]` |
| R4 B2 plural chaining/object/elision / `root4_confirmation/object_count` | `What is AstraZeneca running in NSCLC?` | `AstraZeneca sponsors osimertinib and carboplatin. It sponsors them in 10 trials.` | `grounded=False`; `[('number', '10')]` |
| R4 B3 count after trial label / `root4_confirmation/colon_count` | `What is AstraZeneca running in NSCLC?` | `AstraZeneca sponsors osimertinib and carboplatin in trials: 10.` | `grounded=False`; `[('count_ambiguous', 'OSIMERTINIB / CARBOPLATIN')]` |
| R4 B4 shared trial phase/status / `root4_confirmation/trial_group_status` | `What trials evaluate Tagrisso?` | `NCT03909334 and NCT07680790 are recruiting trials of osimertinib.` | `grounded=False`; `[('status', 'recruiting')]` |
| R4 B4 shared trial phase/status / `root4_confirmation/trial_group_phase` | `What trials evaluate Tagrisso?` | `NCT03909334 and NCT07680790 are phase 3 trials of osimertinib.` | `grounded=False`; `[('phase', 'phase 3')]` |
| R4 B4 shared trial phase/status / `root4_confirmation/trial_status_prefix` | `What trials evaluate Tagrisso?` | `Recruiting trials evaluating osimertinib include NCT07680790 and NCT03909334.` | `grounded=False`; `[('status', 'recruiting')]` |
| R4 B5 kind/clinical ownership / `root4_confirmation/kind_drug` | `What does osimertinib target?` | `EGFR is a drug inhibited by osimertinib.` | `grounded=False`; `[('wording', 'drug')]` |
| R4 B5 kind/clinical ownership / `docs_diagnostics_results/trial_graph` | `Which drugs act on ALK?` | `PLB1003 inhibits ALK in clinical trials in this graph.` | `grounded=False`; `[('wording', 'clinical'), ('wording', 'trials')]` |
| R4 B6 spelled-out letters / `root4_confirmation/split_negation` | `What does osimertinib target?` | `Osimertinib does N O T inhibit EGFR.` | `grounded=False`; `[('unreadable', 'spelled-out letters')]` |
| R4 B6 spelled-out letters / `root4_probe/negation_split` | `What does osimertinib target?` | `Osimertinib does n o t inhibit EGFR.` | `grounded=False`; `[('unreadable', 'spelled-out letters')]` |
| R4 weaker NSCLC/identity/percentage residues / `root4_confirmation/nsclc_residue` | `Which drugs act on ALK?` | `PLB1003 acts on ALK in NSCLC trials.` | `grounded=False`; `[('indication', 'lung cancer'), ('wording', 'trials')]` |
| R4 weaker NSCLC/identity/percentage residues / `root4_probe/relation_precedes_identity` | `What does osimertinib target?` | `Osimertinib inhibits EGFR and is EGFR.` | `grounded=False`; `[('identity', 'EGFR')]` |
| R4 weaker NSCLC/identity/percentage residues / `root4_probe/percent` | `Which drugs act on ALK?` | `LORLATINIB has 13% NSCLC trials.` | `grounded=False`; `[('number', '13%')]` |
| R4 additional phase-as-figure diagnostic / `root4_probe/drug_count_unit` | `Which drugs act on ALK?` | `PLB1003 has 1 phase.` | `grounded=False`; `[('number', '1')]` |

## SHOULD FIX dispositions and faithful answer replay

| Question | Original R1 corpus passed | R3 added corpus passed |
|---|---|---|
| Which companies are developing osimertinib? | 6/6 | 5/6 |
| What trials evaluate Tagrisso? | 6/6 | 6/6 |
| What does osimertinib target? | 6/6 | 6/6 |
| Which drugs act on ALK? | 6/6 | 6/6 |
| What is AstraZeneca running in NSCLC? | 5/6 | 6/6 |
| What is the capital of France? | 4/6 | 5/6 |

Both evidence corpora remain **29/30 (96.7%)** passing; refusals remain **4/6** and **5/6**, respectively. These are diagnostic hand-authored samples, not a production LLM error-rate estimate; they are not independent samples to pool. R1, R2 S1, R3 S1 and R4 S1 overall faithful/refusal handling remains **NOT FIXED** in the sense that some original faithful answers still fail. The five specifically cited R4 forms are **FIXED**.

Remaining historical faithful/refusal failures:

- `faithful_results/Q5P4`: `What is AstraZeneca running in NSCLC?` / `AstraZeneca supports trials studying osimertinib in NSCLC.` -> False; `[('unrelated_entity', 'Astrazeneca'), ('wording', 'supports')]`.
- `faithful_results/Q6P3`: `What is the capital of France?` / `The graph covers NSCLC drugs and trials, so it cannot answer this question.` -> False; `[('no_antecedent', 'it')]`.
- `faithful_results/Q6P6`: `What is the capital of France?` / `I cannot determine the capital of France from the retrieved evidence.` -> False; `[('entity', 'France'), ('no_subject', 'i cannot determine capital france')]`.
- `docs3_probe_results/faithful_05`: `Which companies are developing osimertinib?` / `AstraZeneca sponsors 14 trials of osimertinib. This is evidence of sponsorship, not evidence that it develops the drug.` -> False; `[('identity', 'Astrazeneca = OSIMERTINIB'), ('development_claim', 'develops'), ('negation', 'not')]`.
- `docs3_probe_results/faithful_33`: `What is the capital of France?` / `I cannot determine the capital of France from the retrieved evidence.` -> False; `[('entity', 'France'), ('no_subject', 'i cannot determine capital france')]`.

Specific faithful repairs:

- **FIXED** R2 S1 inline pronoun/repeated alias/spaced code (3/3 pass).
  - `What does osimertinib target?` / `Osimertinib acts on EGFR and it inhibits EGFR.` -> True; `[]`.
  - `What does osimertinib target?` / `Osimertinib (Tagrisso) acts on EGFR.` -> True; `[]`.
  - `What does osimertinib target?` / `AZD 9291 acts on EGFR.` -> True; `[]`.
- **FIXED** R3 S1 six specifically cited faithful forms (6/6 pass).
  - `What does osimertinib target?` / `Osimertinib targets EGFR and inhibits it.` -> True; `[]`.
  - `What trials evaluate Tagrisso?` / `NCT03909334 evaluates osimertinib in phase 2.` -> True; `[]`.
  - `What trials evaluate Tagrisso?` / `NCT03909334 is a phase II trial evaluating osimertinib.` -> True; `[]`.
  - `What is AstraZeneca running in NSCLC?` / `AstraZeneca sponsors 14 NSCLC trials evaluating osimertinib and 10 NSCLC trials evaluating carboplatin.` -> True; `[]`.
  - `What does osimertinib target?` / `AZD9291 (AZD-9291) acts on EGFR.` -> True; `[]`.
  - `What does osimertinib target?` / `Osimertinib (Tagrisso, AZD 9291, AZD9291) acts on EGFR.` -> True; `[]`.
- **FIXED** R4 S1 five specifically cited faithful forms (5/5 pass).
  - `What trials evaluate Tagrisso?` / `NCT07680790 and NCT02411448 are phase 3.` -> True; `[]`.
  - `What is AstraZeneca running in NSCLC?` / `AstraZeneca sponsors 14 trials of osimertinib (Tagrisso).` -> True; `[]`.
  - `Which drugs act on ALK?` / `LORLATINIB and CRIZOTINIB act on ALK. They are approved.` -> True; `[]`.
  - `What does osimertinib target?` / `Osimertinib acts on EGFR [CHEMBL3353410, ENSG00000146648].` -> True; `[]`.
  - `What trials evaluate Tagrisso?` / `Trials of osimertinib include NCT03909334 and NCT07680790.` -> True; `[]`.

Additional R4 faithful diagnostics remain **NOT FIXED** (they already failed before R5):

- `spec_probe3/faithful_approval_coord`: `Which drugs act on ALK?` / `LORLATINIB and CRIZOTINIB are approved.` -> False; `[('wording', 'approved')]`.
- `root4_probe/faithful_phase_list`: `What trials evaluate Tagrisso?` / `NCT03909334 and NCT07680790 evaluate osimertinib. The former is phase 2 and the latter is phase 3.` -> False; `[('wording', 'former'), ('wording', 'latter'), ('phase', 'phase 2'), ('phase', 'phase 3')]`.

R1 Cartesian-product pairing: **FIXED**. All three faithful joined and three split relation pairs pass; all three swapped pairs fail (see `replay5_adversarial_pairs_results.json`).

R1 distinct-sentence dedup: **FIXED**. `Osimertinib is safe. EGFR is safe.` is rejected and both sentence-specific `safe` findings survive. Same-unit dedup remains a NOTE: `Osimertinib is safe and EGFR is safe.` is rejected, although only one final `safe` finding remains; no nonempty finding list becomes acceptance (see `replay5_main_results.json` / `repeat_safe_dedup` and `replay5_r2_root_design_probe.json` / `dedup_same_unit`).

R1 documentation / R2 S2 / R3 S2 / R4 S2: behavioral replay establishes that exact earlier omissions are repaired; documentation completeness against newly discovered R5 behavior is decided separately in the parent documentation review. It must not be inferred from replay alone.

## Regression, templates and dictionary

........................................................................ [ 30%]
........................................................................ [ 60%]
........................................................................ [ 90%]
........................                                                 [100%]
240 passed in 8.01s

Exit 0, empty stderr. TEMP/TMP point to `r5/replay5_temp`; bytecode and pytest cache writes are disabled.

All **5/5 evidence template bodies pass** generated-prose checking after exactly the normal `Scope:` removal. All five Scope-inclusive templates still fail; the France template remains rejected when treated as generated prose, while the normal `ask()` refusal path passes. Exact text and results: `replay5_faithful_results.json` / `templates`.

The dictionary gate replay checks **7,610 keys / 1,066 drugs / 2,634 unique multiword aliases**, with **zero lost intended links** relative to the old short-word joining behavior. `is a` remains unlinked; `AZD 9291`, `osimertinib mesylate`, `trastuzumab deruxtecan`, and `pemetrexed disodium` retain intended links. See `replay5_code_dictionary.json`.

Separate dictionary-to-tokenizer replay: **2,566/2,634** aliases link an intended ID; the five previously documented tokenizer discrepancies (two parenthesized chemical names and three parent/salt overlaps) are unchanged. These five are not new R5 losses. See `replay5_r3_numeric3_dictionary.json`.

Question punctuation remains unchanged: ALK followed by `!`, `:` or `;` is not linked in the question; `?` works. This is independent of answer punctuation.

## Reproduction and integrity

Run `powershell -NoProfile -File audit_evidence_claims/r5/replay5_reproduce.ps1`. All source copies, outputs, diffs and temporary test files stay under `audit_evidence_claims/r5/`. Original files and pre-existing `r5/brief.md` / `r5/log.txt` are untouched.
