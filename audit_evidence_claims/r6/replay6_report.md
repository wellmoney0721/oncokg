# Independent exact R1-R5 replay at 80da81b

All 31 historical probe scripts were executed through adapted copies: six R1, three R2, five R3, nine R4, and eight R5. The R1-R4 copies derive from the R5 replay, with its earlier adaptation diffs preserved in r5; new diffs show the r6 output-path redirection. Obsolete internal `_tokenise` call signatures remain adapted, and assertions requiring historic vulnerability outcomes are disabled while expected values are retained as metadata. Every question, answer, ID and saved direct/filtered evidence input was checked for identity against its original result artifact. Current `Engine.check` or direct-call outputs are preserved in the per-script JSON files.

**853 input-identity-checked answer cases**, per round: `{'R1': 142, 'R2': 104, 'R3': 192, 'R4': 168, 'R5': 247}`. Four additional citation transformations, six templates, and dictionary experiments were also replayed.

FIXED means the exact reported input now has the intended acceptance/rejection result; it does not establish that every variant of the mechanism is safe. Historical findings are classified from the reports, not inferred from old JSON acceptance flags, since some old artifacts were overwritten during repairs.

## Historical BLOCKERS and additional reported diagnostics

| Prior finding | Result | Exact attack inputs still passing |
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
| R5 B1 heading kind/disease erasure | **FIXED** | 0/3 |
| R5 B2 named-group clinical context | **FIXED** | 0/3 |
| R5 B3 passive-list it | **FIXED** | 0/1 |
| R5 B4 parenthetical trial values | **FIXED** | 0/2 |
| R5 B5 longer trial labels/such trials | **FIXED** | 0/3 |
| R5 B6 kind-word owners/trial identity | **FIXED** | 0/3 |
| R5 N2 spaced percent/comma letters | **FIXED** | 0/3 |
| R4 kind-group diagnostic (REGRESSED) | **NOT FIXED** | 1/1 |

**All mapped primary R1–R5 blocker reproductions reject, but a prior R4 rejecting kind-group control has regressed.** Do not summarize this as every old unsafe input being repaired. The four False→True transitions across the full prior 606-case corpus are:

- `spec_probe_results/noun_correct_ofby` / `The inhibition of EGFR by osimertinib.` → True/[]: **NOTE: evidence consistent**. Faithful relation, entity kind, alias, attribute/count, quotation, citation or refusal control; no unsupported claim established.
- `root3_probe/flat_question` / `OSIMERTINIB acts on EGFR? inhibitor.` → True/[]: **NOTE: evidence consistent**. Punctuation converts the same supported inhibition statement into a question/fragment.
- `docs3_probe_results/attack_11` / `The inhibition of EGFR by osimertinib.` → True/[]: **NOTE: evidence consistent**. Faithful relation, entity kind, alias, attribute/count, quotation, citation or refusal control; no unsupported claim established.
- `docs_controls_results/kind_target_nonrelation` / `Osimertinib and EGFR are drugs.` → True/[]: **BLOCKER: regression**. EGFR is a Target, not a Drug. The drug kind is absent from the sole Q3 evidence statement, so this is outside the one-statement vocabulary residue. R4 and R5 both rejected this input.

All **251 current passing cases** were dispositioned in `replay6_passing_dispositions.json`: one unsafe regression, with all other passes classified as evidence-consistent, disclosed residue, artificial encoding, or no claim. Non-obvious passing diagnostics:

- `main_results/punctuation_only`: `What does osimertinib target?` / `...` → True/[]; **NOTE: no claim**. Punctuation alone contains no clinical assertion.
- `root_design_probe/number_units_count_as_phase`: `Which drugs act on ALK?` / `LORLATINIB has 13 phase trials.` → True/[]; **NOTE: disclosed residue / artificial**. 13 phase trials is unnatural and reuses the same LORLATINIB row; it does not assert an unsupported numeric phase.
- `root3_probe/fragment_without_be`: `Which drugs act on ALK?` / `PLB1003, LORLATINIB.` → True/[]; **NOTE: no claim**. A comma-separated list of two known drugs does not equate them.
- `root3_probe/flat_question`: `What does osimertinib target?` / `OSIMERTINIB acts on EGFR? inhibitor.` → True/[]; **NOTE: evidence consistent**. Punctuation converts the same supported inhibition statement into a question/fragment.
- `docs3_probe_results/attack_12`: `What does osimertinib target?` / `Osimertinib is the inhibition of EGFR.` → True/[]; **NOTE: explicit README residue**. Osimertinib is the inhibition of EGFR is the exact odd-wording example disclosed in README item 13.
- `docs_controls_results/kind_target_nonrelation`: `What does osimertinib target?` / `Osimertinib and EGFR are drugs.` → True/[]; **BLOCKER: regression**. EGFR is a Target, not a Drug. The drug kind is absent from the sole Q3 evidence statement, so this is outside the one-statement vocabulary residue. R4 and R5 both rejected this input.
- `root5_numeric/phase_digit_before_roman`: `Which drugs act on ALK?` / `PLB1003 has I phase.` → True/[]; **NOTE: artificial encoding**. PLB1003 has I phase is an unnatural Roman count phrase; no independent natural claim outside the disclosed numeric/word rearrangement residue.
- `spec5_extended/passive_it_drug_kind`: `Which drugs act on ALK?` / `ALK is targeted by LORLATINIB and PLB1003. It is a drug.` → True/[]; **NOTE: documented interpretation**. The documented conservative it-after-list rule resolves the pronoun to all named drugs. LORLATINIB and PLB1003 are both drugs.
- `docs5_probe_results/cite_link_destination_claim`: `What does osimertinib target?` / `[Osimertinib](is-safe-and-discontinued) acts on EGFR.` → True/[]; **NOTE: artificial hidden encoding**. Displayed Markdown label is only Osimertinib; the destination string is not ordinary prose and does not carry a claim the documented citation-id rule says it checks.
- `docs5_probe_results/clinical_recruit_drug`: `What trials evaluate Tagrisso?` / `Osimertinib is recruiting.` → True/[]; **NOTE: disclosed residue**. Osimertinib is recruiting rearranges drug and status vocabulary from one retrieved trial statement; R5 already classified this as the one-statement residue.

## Exact inputs for every mapped finding

| Finding / case | Exact question(s) | Exact answer | Current output |
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
| R1 B4 bigram laundering / `main_results/quoted_developing` | `Which companies are developing osimertinib?` | `AstraZeneca is developing the drug osimertinib.` | `grounded=False`; `[('identity', 'Astrazeneca = OSIMERTINIB'), ('development_claim', 'developing')]` |
| R1 B4 bigram laundering / `main_results/quoted_developing_2` | `Which companies are developing osimertinib?` | `AstraZeneca has evidence of developing osimertinib.` | `grounded=False`; `[('development_claim', 'developing')]` |
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
| R1 B8 numeric layouts / `adversarial_pairs_results/count_after_colon_list` | `Which drugs act on ALK?` | `- PLB1003: NSCLC trials: 13\n- lorlatinib: NSCLC trials: 0` | `grounded=False`; `[('number', '0'), ('number', '13')]` |
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
| R3 B3 headings / `root3_probe/heading_sponsors_full` | `What does osimertinib target?` | `these drugs are sponsors of trials:\n- OSIMERTINIB acts on EGFR (inhibitor)` | `grounded=False`; `[('relation_direction', 'OSIMERTINIB sponsors OSIMERTINIB'), ('wording', 'trials')]` |
| R3 B3 headings / `root3_probe/heading_activators_full` | `What does osimertinib target?` | `these drugs are activators:\n- OSIMERTINIB acts on EGFR (inhibitor)` | `grounded=False`; `[('relation_incomplete', 'activators')]` |
| R3 B3 headings / `root3_probe/heading_with_alk` | `What does osimertinib target?` | `these drugs inhibit EGFR with ALK:\n- OSIMERTINIB acts on EGFR (inhibitor)` | `grounded=False`; `[('unrelated_entity', 'ALK')]` |
| R3 B4 clinical/kind/identity / `root3_probe/clinical_trial_unsupported` | `What does osimertinib target?` | `Osimertinib is in clinical trials.` | `grounded=False`; `[('wording', 'clinical'), ('wording', 'trials')]` |
| R3 B4 clinical/kind/identity / `root3_probe/nsclc_trial_unsupported` | `What does osimertinib target?` | `Osimertinib is in NSCLC trials.` | `grounded=False`; `[('indication', 'lung cancer'), ('wording', 'trials')]` |
| R3 B4 clinical/kind/identity / `root3_probe/indication_drug` | `What does osimertinib target?` | `Osimertinib is an NSCLC drug.` | `grounded=False`; `[('indication', 'lung cancer')]` |
| R3 B4 clinical/kind/identity / `docs3_focused_results/focused_07` | `What does osimertinib target?` | `EGFR is a drug.` | `grounded=False`; `[('wording', 'drug')]` |
| R3 B4 clinical/kind/identity / `root3_probe/zero_evidence_clinical` | `What is the capital of France?` | `There are clinical trials.` | `grounded=False`; `[('no_subject', 'clinical trials')]` |
| R3 B4 clinical/kind/identity / `root3_probe/fragment_drug_identity` | `Which drugs act on ALK?` | `PLB1003 is LORLATINIB.` | `grounded=False`; `[('identity', 'PLB1003 = LORLATINIB')]` |
| R3 B4 clinical/kind/identity / `root3_probe/fragment_trial_identity` | `What trials evaluate Tagrisso?` | `NCT03909334 is NCT07680790.` | `grounded=False`; `[('identity', 'NCT03909334 = NCT07680790')]` |
| R3 weaker count-after-colon / `root3_probe/unknown_number_only` | `Which drugs act on ALK?` | `PLB1003 has NSCLC trials: 1.` | `grounded=False`; `[('number', '1')]` |
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
| R4 B2 plural chaining/object/elision / `root4_confirmation/object_count` | `What is AstraZeneca running in NSCLC?` | `AstraZeneca sponsors osimertinib and carboplatin. It sponsors them in 10 trials.` | `grounded=False`; `[('number', '10'), ('count_ambiguous', 'OSIMERTINIB / CARBOPLATIN'), ('relation_direction', 'OSIMERTINIB sponsors CARBOPLATIN'), ('relation_direction', 'OSIMERTINIB sponsors OSIMERTINIB')]` |
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
| R5 B1 heading kind/disease erasure / `root5_confirmation/B1_heading_kind` | `What does osimertinib target?` | `The following companies inhibit EGFR:\n- Osimertinib` | `grounded=False`; `[('wording', 'companies')]` |
| R5 B1 heading kind/disease erasure / `root5_confirmation/B1_heading_disease` | `What does osimertinib target?` | `These NSCLC drugs:\n- Osimertinib` | `grounded=False`; `[('indication', 'lung cancer')]` |
| R5 B1 heading kind/disease erasure / `spec5_extended/heading_wrong_kind_drug` | `What does osimertinib target?` | `These drugs:\n- EGFR` | `grounded=False`; `[('wording', 'drugs')]` |
| R5 B2 named-group clinical context / `root5_confirmation/B2_group_clinical` | `Which drugs act on ALK?` | `LORLATINIB and PLB1003 are in clinical trials.` | `grounded=False`; `[('wording', 'clinical'), ('wording', 'trials')]` |
| R5 B2 named-group clinical context / `root5_confirmation/B2_group_clinical_relation` | `Which drugs act on ALK?` | `LORLATINIB and PLB1003 inhibit ALK in clinical trials.` | `grounded=False`; `[('wording', 'clinical'), ('wording', 'trials')]` |
| R5 B2 named-group clinical context / `spec5_controls/clinical_group_graph` | `Which drugs act on ALK?` | `LORLATINIB and PLB1003 have clinical trials in this graph.` | `grounded=False`; `[('wording', 'clinical'), ('wording', 'trials')]` |
| R5 B3 passive-list it / `root5_confirmation/B3_passive_it` | `Which drugs act on ALK?` | `ALK is targeted by LORLATINIB and PLB1003. It is approved.` | `grounded=False`; `[('wording', 'approved')]` |
| R5 B4 parenthetical trial values / `root5_confirmation/B4_status_parenthetical` | `What trials evaluate Tagrisso?` | `NCT03909334 (phase 2) and NCT07680790 (phase 3) are recruiting.` | `grounded=False`; `[('status', 'recruiting')]` |
| R5 B4 parenthetical trial values / `root5_confirmation/B4_phase_parenthetical` | `What trials evaluate Tagrisso?` | `NCT03909334 (active, not recruiting) and NCT07680790 are phase 3.` | `grounded=False`; `[('phase', 'phase 3')]` |
| R5 B5 longer trial labels/such trials / `root5_confirmation/B5_long_count_label` | `What is AstraZeneca running in NSCLC?` | `AstraZeneca sponsors osimertinib and carboplatin in trials in this graph: 10.` | `grounded=False`; `[('count_ambiguous', 'OSIMERTINIB / CARBOPLATIN')]` |
| R5 B5 longer trial labels/such trials / `spec5_anaphora/wrong_such` | `What is AstraZeneca running in NSCLC?` | `AstraZeneca sponsors trials of Tagrisso. There are 10 such trials in this graph.` | `grounded=False`; `[('number', '10')]` |
| R5 B5 longer trial labels/such trials / `spec5_anaphora/wrong_such_elided` | `What is AstraZeneca running in NSCLC?` | `AstraZeneca sponsors trials of Tagrisso and has 10 such trials.` | `grounded=False`; `[('number', '10')]` |
| R5 B6 kind-word owners/trial identity / `root5_confirmation/B6_relative_kind` | `What does osimertinib target?` | `EGFR, which is inhibited by osimertinib, is a drug.` | `grounded=False`; `[('wording', 'drug')]` |
| R5 B6 kind-word owners/trial identity / `root5_confirmation/B6_prefix_kind` | `What does osimertinib target?` | `The drug EGFR is inhibited by osimertinib.` | `grounded=False`; `[('wording', 'drug')]` |
| R5 B6 kind-word owners/trial identity / `root5_confirmation/B6_clinical_trial_identity` | `What trials evaluate Tagrisso?` | `Osimertinib is a clinical trial.` | `grounded=False`; `[('wording', 'clinical'), ('wording', 'trial')]` |
| R5 N2 spaced percent/comma letters / `root5_confirmation/N_percent_spaced` | `Which drugs act on ALK?` | `LORLATINIB has 13 % NSCLC trials.` | `grounded=False`; `[('number', '13%')]` |
| R5 N2 spaced percent/comma letters / `docs5_probe_results/letters_not_comma` | `What does osimertinib target?` | `Osimertinib does N, O, T inhibit EGFR.` | `grounded=False`; `[('unreadable', 'spelled-out letters')]` |
| R5 N2 spaced percent/comma letters / `docs5_probe_results/letters_safe_comma` | `What does osimertinib target?` | `Osimertinib is S, A, F, E.` | `grounded=False`; `[('unreadable', 'spelled-out letters')]` |
| R4 kind-group diagnostic (REGRESSED) / `docs_controls_results/kind_target_nonrelation` | `What does osimertinib target?` | `Osimertinib and EGFR are drugs.` | `grounded=True`; `[]` |

## SHOULD FIX: faithful corpora

| Question | R1 original | R3 added | R5 fresh |
|---|---:|---:|---:|
| Which companies are developing osimertinib? | 6/6 | 5/6 | 7/8 |
| What trials evaluate Tagrisso? | 6/6 | 6/6 | 8/8 |
| What does osimertinib target? | 6/6 | 6/6 | 8/8 |
| Which drugs act on ALK? | 6/6 | 6/6 | 8/8 |
| What is AstraZeneca running in NSCLC? | 5/6 | 6/6 | 8/8 |
| What is the capital of France? | 4/6 | 5/6 | 5/6 |

**Evidence-answer totals: R1 29/30 (96.7%); R3 29/30 (96.7%); R5 39/40 (97.5%). Refusals separately: 4/6, 5/6, 5/6.** These hand-authored diagnostic corpora are not production LLM error-rate estimates and must not be pooled as independent samples.

The repair table reports R5 38/40, but the unchanged fresh corpus actually yields 39/40 evidence answers, plus one refusal failure in the separate six-case Q6 corpus. This is a denominator/documentation correction, not a blocker.

| Specific prior false-positive finding | Result | Remaining rejected inputs |
|---|---|---|
| R2 S1 inline pronoun/repeated alias/spaced code | **FIXED** | 0/3 |
| R3 S1 six specifically cited faithful forms | **FIXED** | 0/6 |
| R4 S1 five specifically cited faithful forms | **FIXED** | 0/5 |
| R5 S1 twelve original fresh faithful failures | **NOT FIXED** | 1/12 |
| R5 S1 two kind-owner controls | **FIXED** | 0/2 |

R1–R5 overall faithful/refusal handling is **NOT FIXED** in the literal all-cases sense: documented strictness remains. The current evidence corpus results satisfy the requested mostly-pass bar. Remaining faithful/refusal rejections:

- `faithful_results/Q5P4`: `What is AstraZeneca running in NSCLC?` / `AstraZeneca supports trials studying osimertinib in NSCLC.` → `grounded=False`; `[('unrelated_entity', 'Astrazeneca'), ('wording', 'supports')]`.
- `faithful_results/Q6P3`: `What is the capital of France?` / `The graph covers NSCLC drugs and trials, so it cannot answer this question.` → `grounded=False`; `[('no_antecedent', 'it')]`.
- `faithful_results/Q6P6`: `What is the capital of France?` / `I cannot determine the capital of France from the retrieved evidence.` → `grounded=False`; `[('entity', 'France'), ('no_subject', 'i cannot determine capital france')]`.
- `docs3_probe_results/faithful_05`: `Which companies are developing osimertinib?` / `AstraZeneca sponsors 14 trials of osimertinib. This is evidence of sponsorship, not evidence that it develops the drug.` → `grounded=False`; `[('identity', 'Astrazeneca = OSIMERTINIB'), ('development_claim', 'develops'), ('negation', 'not')]`.
- `docs3_probe_results/faithful_33`: `What is the capital of France?` / `I cannot determine the capital of France from the retrieved evidence.` → `grounded=False`; `[('entity', 'France'), ('no_subject', 'i cannot determine capital france')]`.
- `docs5_probe_results/faithful_q1_8`: `Which companies are developing osimertinib?` / `AstraZeneca sponsors trials evaluating osimertinib. This is evidence of trial sponsorship, not drug development.` → `grounded=False`; `[('wording', 'development'), ('wording', 'drug'), ('negation', 'not')]`.
- `docs5_probe_results/faithful_q6_4`: `What is the capital of France?` / `I cannot determine the capital of France from this graph.` → `grounded=False`; `[('entity', 'France'), ('no_subject', 'i cannot determine capital france')]`.

Exact outcomes for specifically cited false-positive repairs:

- `spec_probe_results/pronoun_faithful`: `What does osimertinib target?` / `Osimertinib acts on EGFR and it inhibits EGFR.` → `grounded=True`; `[]`.
- `standards_probe/alias_parentheses`: `What does osimertinib target?` / `Osimertinib (Tagrisso) acts on EGFR.` → `grounded=True`; `[]`.
- `standards_probe/alias_spaced_code`: `What does osimertinib target?` / `AZD 9291 acts on EGFR.` → `grounded=True`; `[]`.
- `root3_probe/object_pronoun_faithful`: `What does osimertinib target?` / `Osimertinib targets EGFR and inhibits it.` → `grounded=True`; `[]`.
- `numeric3_probe/phase_after_eval`: `What trials evaluate Tagrisso?` / `NCT03909334 evaluates osimertinib in phase 2.` → `grounded=True`; `[]`.
- `numeric3_probe/phase_roman`: `What trials evaluate Tagrisso?` / `NCT03909334 is a phase II trial evaluating osimertinib.` → `grounded=True`; `[]`.
- `docs3_probe_results/faithful_25`: `What is AstraZeneca running in NSCLC?` / `AstraZeneca sponsors 14 NSCLC trials evaluating osimertinib and 10 NSCLC trials evaluating carboplatin.` → `grounded=True`; `[]`.
- `numeric3_probe/alias_hyphen_second`: `What does osimertinib target?` / `AZD9291 (AZD-9291) acts on EGFR.` → `grounded=True`; `[]`.
- `numeric3_probe/alias_four`: `What does osimertinib target?` / `Osimertinib (Tagrisso, AZD 9291, AZD9291) acts on EGFR.` → `grounded=True`; `[]`.
- `root4_confirmation/faithful_two_phases`: `What trials evaluate Tagrisso?` / `NCT07680790 and NCT02411448 are phase 3.` → `grounded=True`; `[]`.
- `root4_confirmation/faithful_count_alias`: `What is AstraZeneca running in NSCLC?` / `AstraZeneca sponsors 14 trials of osimertinib (Tagrisso).` → `grounded=True`; `[]`.
- `root4_confirmation/faithful_capital_they`: `Which drugs act on ALK?` / `LORLATINIB and CRIZOTINIB act on ALK. They are approved.` → `grounded=True`; `[]`.
- `docs_controls_results/cite_valid_list`: `What does osimertinib target?` / `Osimertinib acts on EGFR [CHEMBL3353410, ENSG00000146648].` → `grounded=True`; `[]`.
- `root4_probe/faithful_trial_noun`: `What trials evaluate Tagrisso?` / `Trials of osimertinib include NCT03909334 and NCT07680790.` → `grounded=True`; `[]`.
- `docs5_probe_results/faithful_q1_5`: `Which companies are developing osimertinib?` / `The graph records sponsorship of osimertinib trials by AstraZeneca.` → `grounded=True`; `[]`.
- `docs5_probe_results/faithful_q1_6`: `Which companies are developing osimertinib?` / `Sponsors of osimertinib trials include AstraZeneca and Bristol Myers Squibb.` → `grounded=True`; `[]`.
- `docs5_probe_results/faithful_q1_7`: `Which companies are developing osimertinib?` / `AstraZeneca sponsors 14 trials of osimertinib. Bristol Myers Squibb sponsors 2 trials of it.` → `grounded=True`; `[]`.
- `docs5_probe_results/faithful_q1_8`: `Which companies are developing osimertinib?` / `AstraZeneca sponsors trials evaluating osimertinib. This is evidence of trial sponsorship, not drug development.` → `grounded=False`; `[('wording', 'development'), ('wording', 'drug'), ('negation', 'not')]`.
- `docs5_probe_results/faithful_q2_7`: `What trials evaluate Tagrisso?` / `NCT07680790 is recruiting. NCT03909334 is active but not recruiting.` → `grounded=True`; `[]`.
- `docs5_probe_results/faithful_q3_4`: `What does osimertinib target?` / `The graph records osimertinib acting on EGFR as an inhibitor.` → `grounded=True`; `[]`.
- `docs5_probe_results/faithful_q3_6`: `What does osimertinib target?` / `Reported mechanism: inhibition of EGFR by osimertinib.` → `grounded=True`; `[]`.
- `docs5_probe_results/faithful_q3_8`: `What does osimertinib target?` / `Osimertinib acts on EGFR; its recorded action is inhibition.` → `grounded=True`; `[]`.
- `docs5_probe_results/faithful_q4_5`: `Which drugs act on ALK?` / `The graph records 13 NSCLC trials of lorlatinib and 15 NSCLC trials of crizotinib.` → `grounded=True`; `[]`.
- `docs5_probe_results/faithful_q5_6`: `What is AstraZeneca running in NSCLC?` / `AstraZeneca sponsors 7 NSCLC trials evaluating durvalumab and 8 evaluating gefitinib.` → `grounded=True`; `[]`.
- `docs5_probe_results/faithful_q5_7`: `What is AstraZeneca running in NSCLC?` / `Reported sponsorship:
- AstraZeneca: 14 NSCLC trials of osimertinib.
- AstraZeneca: 10 NSCLC trials of carboplatin.` → `grounded=True`; `[]`.
- `docs5_probe_results/faithful_q5_8`: `What is AstraZeneca running in NSCLC?` / `AstraZeneca runs 6 NSCLC trials of pemetrexed and 6 of cisplatin.` → `grounded=True`; `[]`.
- `root5_confirmation/S1_faithful_relative_kind`: `What does osimertinib target?` / `Osimertinib, which inhibits EGFR, is a drug.` → `grounded=True`; `[]`.
- `root5_confirmation/S1_faithful_prefix_drug`: `What does osimertinib target?` / `EGFR is inhibited by the drug osimertinib.` → `grounded=True`; `[]`.

## NOTES: regressions, templates, dictionary, dedup

........................................................................ [ 26%]
........................................................................ [ 52%]
........................................................................ [ 78%]
...........................................................              [100%]
275 passed in 8.24s

Exit 0; stderr empty. Exact command: `python -m pytest tests -q -p no:cacheprovider`. TEMP/TMP were `r6/replay6_temp`; bytecode and pytest cache writes disabled.

**5/5 evidence template prose bodies pass**, retaining headings and removing `Scope:` exactly as the normal path does. Scope-inclusive template inputs still reject. France refusal still rejects in the generated checker and succeeds in the normal `ask()` refusal path. Full text/output: `replay6_faithful_results.json`.

**Dictionary gate: 7,610 keys / 1,066 drugs / 2,634 unique multiword aliases, zero lost intended links** versus the prior short-word joining behavior. `is a` remains unlinked; `AZD 9291`, `osimertinib mesylate`, `trastuzumab deruxtecan`, and `pemetrexed disodium` retain links (`replay6_code_dictionary.json`). Separate dictionary-to-tokenizer replay still has 2,566/2,634 aliases linking an intended ID and the same five previously documented tokenizer discrepancies (two parenthesized chemical names, three parent/salt overlaps; `replay6_r3_numeric3_dictionary.json`).

**R1 Cartesian-product paired relations: FIXED.** Three faithful joined and three split relation pairs pass; all three swapped pairs reject (`replay6_adversarial_pairs_results.json`).

**R1 distinct-sentence dedup: FIXED.** `Osimertinib is safe. EGFR is safe.` retains two sentence-specific safe findings and rejects. Same-unit `Osimertinib is safe and EGFR is safe.` still merges safe findings but rejects; dedup cannot empty a nonempty list (`replay6_main_results.json`, `replay6_r2_root_design_probe.json`).

Question punctuation after ALK (`!`, `:`, `;`) remains an unchanged linker limitation; `?` links correctly. This is distinct from answer punctuation.

R1 documentation / R2 S2 / R3 S2 / R4 S2 / R5 S2 overall: the exact historical behavior underlying those objections is repaired; current documentation completeness and any new R6 failures require the separate documentation review. Replay does not infer a universal documentation guarantee.

## Reproduction and integrity

Run `powershell -NoProfile -File audit_evidence_claims/r6/replay6_reproduce.ps1`. All writes go under r6. Original probe files, tracked files, and pre-existing r6/brief.md and r6/log.txt are not edited. `replay6_manifest.json` records sources, hashes, derived copies and exit codes; `replay6_verification.json` records HEAD, code/database hashes and clean tracked/staged diffs. Per-script JSON files preserve complete outputs, and `replay6_all_cases.json` aggregates all replayed answer checks.