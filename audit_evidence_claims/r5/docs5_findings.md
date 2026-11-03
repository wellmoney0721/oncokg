# R5 documentation axis, citation attack and fresh faithful corpus

Reviewed HEAD `9fda6f8`, `git diff 9fda6f8^...HEAD`, against the local graph. All new files in this sub-review are `audit_evidence_claims/r5/docs5*`. No tracked file was edited. `Engine().check(question, answer)` was used for every case, with full actual retrieved evidence saved beside each result. No external medical claim or network lookup is required: support is judged solely against these records.

## BLOCKERS

### D-B1. A kind noun before its entity borrows the kind of a later entity

Exact observed cases (all `grounded=True`, `applicable=True`, `unsupported_claims=[]`):

| Question | Exact answer |
|---|---|
| `What does osimertinib target?` | `The drug EGFR is inhibited by osimertinib.` |
| `What is AstraZeneca running in NSCLC?` | `The drug AstraZeneca sponsors osimertinib.` |
| `What is AstraZeneca running in NSCLC?` | `The company osimertinib is sponsored by AstraZeneca.` |

The relation is supported in each case, but the entity-kind assertion is not. In Q3, the entire evidence is `OSIMERTINIB acts on EGFR (inhibitor)`; the linker identifies EGFR as Target and osimertinib as Drug. The added word `drug` is absent from that statement, so this does not qualify for README item 13's one-statement rearrangement residue. The Q5 rows record AstraZeneca as the sponsor and osimertinib as the evaluated drug; the added wrong kind does not occur in those statements either.

Cause: `src/claims.py:983-988` gives a kind word to the previous entity if present, otherwise accepts that kind anywhere in the clause (`kind in present`). A noun before its own name is ordinary English, but the wrong later Drug/Company licenses it. This is a fresh variant of R4 B5, whose exact post-entity input was repaired.

Controls, all executed: `EGFR is a drug inhibited by osimertinib.` -> False, `wording: drug`; `AstraZeneca is a drug and sponsors osimertinib.` -> False, `wording: drug`; `EGFR is inhibited by osimertinib.` -> True; `The drug osimertinib inhibits EGFR.` -> True. `EGFR is inhibited by the drug osimertinib.` is a faithful false positive -> False, `wording: drug`, because nearest preceding EGFR is selected even though the noun modifies the next entity.

Artifact: `docs5_controls_results.json`, IDs `kind_prefix_target` through `kind_prefix_drug_as_company`, and `faithful_passive_kind` / `faithful_passive_nokind`.

### D-B2. Evidence that a drug is evaluated in trials licenses calling the drug a trial

Question: `What trials evaluate Tagrisso?`

- `Osimertinib is a clinical trial.` -> True; [].
- `Tagrisso is a clinical trial.` -> True; [].
- `Osimertinib is a trial.` -> True; [].

The evidence records named NCT trials evaluating OSIMERTINIB. It does not identify the drug as a trial. The only statement words are trial IDs, registry phase/status and `evaluates OSIMERTINIB`; `clinical` and `trial` in the new assertion are not borrowed statement words. This is outside the explicit one-statement residue. No medical judgment beyond the graph's Drug/Trial types is involved.

Cause: `src/claims.py:808-811` turns any subject-owned EVALUATES row into `about_trials=True`; `:1013-1018` handles `trial`, `trials` and `clinical` only via that Boolean, exempting them from the owner/kind test at `:983-988`. It cannot distinguish `is a clinical trial` from `is in clinical trials`. The identity check at `:443-449` needs entities on both sides of a verb and does not see a kind noun as a second entity.

Controls: the identical `Osimertinib is a clinical trial.` against `What does osimertinib target?` -> False, `wording: clinical`, `wording: trial`; the faithful Q2 inputs `Osimertinib is in clinical trials.` and `NCT07680790 is a clinical trial.` both pass. These controls isolate the existence-of-trials shortcut.

Artifact: `docs5_controls_results.json`, IDs `trial_identity` through `trial_identity_drugs_both`.

## SHOULD FIX

### D-S1. Fresh faithful prose still has material coverage gaps

The fixed 40-answer corpus was authored before executing it: eight answers per demo evidence question, plus six separate refusals. All 40 were checked against the actual evidence. Counts are separate per-drug counts, not new sums; no clinical indication, safety or inferred combination-trial count is introduced. `docs5_faithful_evidence_review.json` records each exact answer and the evidence basis. Some synonyms/paraphrases require ordinary reading (sponsorship/runs, inhibitor/inhibition), which is precisely the intended faithful-prose test.

| Question | Passed |
|---|---:|
| Q1: companies developing osimertinib (answers correctly describe sponsorship) | 4/8 |
| Q2: trials evaluating Tagrisso | 7/8 |
| Q3: osimertinib target | 5/8 |
| Q4: ALK drugs | 7/8 |
| Q5: AstraZeneca in NSCLC | 5/8 |
| Evidence answers | **28/40 (70%)** |
| Q6 refusals, separate | **5/6** |

This diagnostic sample still passes a majority; it does not show that most production LLM answers fail and is not a statistically representative sample. Do not pool it with the historical curated corpora. The sponsorship-not-development caution is already explicitly documented as over-strict at README.md:525-527. Other failures are ordinary relation, pronoun, count or status phrasings.

Every failed evidence answer, with exact observed finding pairs:

| ID | Exact answer | Observed findings (grounded=False) |
|---|---|---|
| faithful_q1_5 | `The graph records sponsorship of osimertinib trials by AstraZeneca.` | fragment: OSIMERTINIB Astrazeneca |
| faithful_q1_6 | `Sponsors of osimertinib trials include AstraZeneca and Bristol Myers Squibb.` | unrelated_entity: Astrazeneca; unrelated_entity: Bristol Myers Squibb; relation_direction: OSIMERTINIB sponsors OSIMERTINIB |
| faithful_q1_7 | `AstraZeneca sponsors 14 trials of osimertinib. Bristol Myers Squibb sponsors 2 trials of it.` | number: 2; relation_direction: Bristol Myers Squibb sponsors Astrazeneca |
| faithful_q1_8 | `AstraZeneca sponsors trials evaluating osimertinib. This is evidence of trial sponsorship, not drug development.` | wording: development; wording: drug; negation: not |
| faithful_q2_7 | `NCT07680790 is recruiting. NCT03909334 is active but not recruiting.` | wording: active; wording: but; negation: not; status: recruiting |
| faithful_q3_4 | `The graph records osimertinib acting on EGFR as an inhibitor.` | relation_incomplete: inhibitor |
| faithful_q3_6 | `Reported mechanism: inhibition of EGFR by osimertinib.` | unrelated_entity: OSIMERTINIB |
| faithful_q3_8 | `Osimertinib acts on EGFR; its recorded action is inhibition.` | wording: action; relation_incomplete: inhibition |
| faithful_q4_5 | `The graph records 13 NSCLC trials of lorlatinib and 15 NSCLC trials of crizotinib.` | number: 15 |
| faithful_q5_6 | `AstraZeneca sponsors 7 NSCLC trials evaluating durvalumab and 8 evaluating gefitinib.` | relation_direction: Astrazeneca evaluating; unrelated_entity: GEFITINIB |
| faithful_q5_7 | `Reported sponsorship:\n- AstraZeneca: 14 NSCLC trials of osimertinib.\n- AstraZeneca: 10 NSCLC trials of carboplatin.` | fragment: Astrazeneca CARBOPLATIN; fragment: Astrazeneca OSIMERTINIB |
| faithful_q5_8 | `AstraZeneca runs 6 NSCLC trials of pemetrexed and 6 of cisplatin.` | count_ambiguous: PEMETREXED / CISPLATIN |

Causal controls from `docs5_controls_results.json`: naming `osimertinib` instead of `it` after `2 trials of` turns `faithful_q1_7` into True; breaking `faithful_q4_5` into two graph-count sentences turns it into True; replacing `active but not recruiting` with `active, not recruiting` turns that status claim into True. The pronoun rule at `claims.py:355-379` only infers object kind from a relation verb in the last two words, so `trials of it` inherits AstraZeneca. The count scope at `:771,784-787` forces the first named drug into the second drug's count. The status recognizer at `:928-945` requires the literal status word sequence; inserting `but` leaves `active` / `not` unsupported and separately treats `recruiting` as a positive claim.

The separate refusal `I cannot determine the capital of France from this graph.` is False (`entity: France`; `no_subject: i cannot determine capital france`) as explicitly documented in README item 13.

### D-S2. Documentation axis: improved qualifications, remaining concrete mismatch

No separate repository coding-standard violation is asserted. The user supplied the review standard, and the reviewed changes are limited to claims/query/tests/docs. The existing caveats should not be reported as absent:

- `README.md:508-531` / `README.ko.md:354-366` explicitly identify pattern reading and the accepted residues. They now mention four adversarial rounds and the relevant R4 shapes.
- `src/claims.py:10-11,48-51` labels the docstring a description, not a guarantee. `src/query.py:450-468` similarly distinguishes generated checking from template applicability and links known residue.
- `web/template.html:263-267` now says four rounds. `web/try.html:69-72,142-145` explicitly warns that no findings are not proof of truth; no blanket-success wording remains.
- Citation validation is now applied before global-name checking (`src/query.py:482-489`) and the tested claim matches the observed results below.

However, the explicit known-pass list in README.md:520-524 / README.ko.md:361-363 does not disclose D-B1's new kind word accepted through another entity or D-B2's false Drug-is-Trial assertion using clinical/kind words absent from the statements. The broad unseen-shape caveat does not meet this audit's requirement to disclose each *known* residue. `claims.py:26-30` describes kind checking, but the kind rules only distinguish a prefix from a previous entity and exempt trial-kind identity.

Small precision issues, separate from the verdict-driving clinical/kind passes:

- `claims.py:22-25` only summarizes phase ownership before a phase, whereas the actual `trial_run` also uses the first trial run after a prefix phase (`:814-825`). Likewise the status summary at `:26` says a singular prior trial, whereas a run is checked, including a following run.
- `CODEX_CLAIMS_R4_VERDICT.md:3` says all 438 earlier exact reproductions were rejected. The prior report's 438 counts include faithful answers and controls, so this must mean prior *attack reproductions*, not all 438 cases. The historical replay provides the exact denominators.
- `claims.py:33-34` says spelled-out letters are reported, but comma-separated examples below pass. This is a narrow documentation/rule mismatch, not needed to establish the stronger natural-language blockers.

## NOTES

### N1. Citation repair behaved as documented in these probes

All with `What does osimertinib target?`:

| Exact answer suffix or complete answer | Observed |
|---|---|
| `Osimertinib acts on EGFR [ENSG00000146648].` | True; [] |
| `Osimertinib acts on EGFR [CHEMBL3353410 ENSG00000146648].` | True; [] |
| `Osimertinib acts on EGFR [CHEMBL3353410; ENSG00000146648].` | True; [] |
| `Osimertinib acts on EGFR [CHEMBL3353410\nENSG00000146648].` | True; [] |
| `Osimertinib acts on EGFR [CHEMBL3353410,CHEMBL3353410].` | True; [] |
| `Osimertinib acts on EGFR [ENSG00000171094].` | False; number/entity/wording |
| `Osimertinib acts on EGFR [CHEMBL601719].` | False; number/entity/wording |
| `Osimertinib acts on EGFR [CHEMBL3353410, ENSG00000171094].` | False; number/entity/wording |
| `Osimertinib [CHEMBL3353410, ORG:is-safe] acts on EGFR.` | False; number/wording |
| `Osimertinib is safe [CHEMBL3353410, ENSG00000146648].` | False; wording: safe |
| `Osimertinib does not inhibit EGFR [CHEMBL3353410].` | False; negation: not |
| `Osimertinib [CHEMBL3353410 is safe] acts on EGFR.` | False; number/wording |
| `[Osimertinib is safe](CHEMBL3353410) acts on EGFR.` | False; wording: safe |

The known-ID set comes from exact source, edge and statement tokens (`claims.py:304-308`, `query.py:486-489`), and `_strip_citations` requires every parsed ID (`claims.py:216-223`). Newline and space delimiters correctly retain the same allowed IDs. Exact full outputs are in `docs5_probe_results.json`, `cite_*` IDs. The passing `[Osimertinib](is-safe-and-discontinued) acts on EGFR.` has a faithful visible claim and an artificial non-URL link destination; it is not an unsupported visible clinical claim and is not a blocker.

### N2. Comma-separated spelling is a secondary rule/documentation mismatch

Question Q3: `Osimertinib does N, O, T inhibit EGFR.` -> True; []; `Osimertinib is S, A, F, E.` -> True; []. Their whitespace-only equivalents are False with `unreadable: spelled-out letters`. The commas are `P` tokens and reset the single-letter run (`claims.py:970-979`); all leftover one-letter words are skipped (`:1020`). Slash/dot/hyphen spelling was rejected in the main probe. These are artificial encodings, so they are reported as secondary notes; the docstring's explicit spelled-letter rule is overbroad. They do not drive the verdict because D-B1/D-B2 are ordinary grammatical claims.

### N3. Evidence-consistent or explicitly disclosed passes do not block

Q2 `Osimertinib is recruiting.` passes but is a one-statement word/entity rearrangement and is not used as an independent blocker under the stated residue bar. Plain supported target relations and citations pass. Ordinary Q3 `Osimertinib is safe.` and `Osimertinib is discontinued.` remain False (`wording`).

### Reproduction

From repository root, with `PYTHONDONTWRITEBYTECODE=1` and UTF-8 output: `python -B audit_evidence_claims/r5/docs5_probe.py` and `python -B audit_evidence_claims/r5/docs5_controls.py`. Both write only their `docs5*` result files. They neither run tests nor create temporary files. Full source/evidence and output are preserved in the JSON artifacts; the parent review separately handles historical replay, pytest, and tracked-file integrity.
