# Independent claim-check audit, round 2

Reviewed HEAD **a12762b**, against the real local graph, with diff `git diff 0c441e0...HEAD`. No tracked files were edited. All new scratch files are under `audit_evidence_claims/r2/`; the pre-existing `brief.md` and `log.txt` were left alone.

## BLOCKERS

**Unsupported claims still return `grounded=True`, `applicable=True`, `unsupported_claims=[]`.** Every attack below was executed; these are not hypothetical parser concerns. Except the explicitly identified union-evidence cases, they use `Engine().check(question, answer)` or the equivalent direct `check_groundedness` call with that question's unmodified retrieved evidence. Truth here means support in the retrieved evidence, not an external medical judgment.

Question keys are exact inputs:

| Key | Question |
|---|---|
| Q1 | `Which companies are developing osimertinib?` |
| Q2 | `What trials evaluate Tagrisso?` |
| Q3 | `What does osimertinib target?` |
| Q4 | `Which drugs act on ALK?` |
| Q5 | `What is AstraZeneca running in NSCLC?` |
| Q6 | `What is the capital of France?` |
| QC | `What does crizotinib target?` |
| QF | `What does fulvestrant target?` |

### B1. The original reversed noun relation is NOT FIXED; passive detection also reverses active claims

| Question | Exact answer | Observed |
|---|---|---|
| Q3 | `EGFR is an osimertinib inhibitor.` | True; `[]` |
| Q3 | `EGFR is what inhibited osimertinib.` | True; `[]` |
| Q2 | `Osimertinib is what evaluated NCT03909334.` | True; `[]` |
| Q5 | `Osimertinib is what sponsored AstraZeneca.` | True; `[]` |

The sole Q3 evidence is `OSIMERTINIB acts on EGFR (inhibitor)`, the opposite direction. Q2 says the trial evaluates the drug; Q5 says the company sponsors trials of the drug.

The noun fallback at `src/claims.py:407-411` fills an absent endpoint using entity type after `_group` selects the nearest entity (`:382-383`), reconstructing the supported inverse instead of checking the written subject. The passive heuristic at `:401-404` treats any `BE` token within three words as an auxiliary. In `is what inhibited`, `inhibited` is an active past-tense verb in a cleft, but the checker reverses it.

The first answer is **an exact R1 reproduction**, not a new variant. It is absent from the regression attack list at `tests/test_claims.py:81-122`, despite the repair table's statement that all five R1 direction examples were repaired. Sources: `replay_main_results.json` (`reverse_noun`), `spec_probe_results.json` (`passive_cleft`, `passive_cleft_trial`, `passive_cleft_sponsor`).

### B2. A repeated preposition or an adverb hides an additional relation endpoint

All with Q3:

| Exact answer | Observed |
|---|---|
| `Osimertinib acts on EGFR and on ALK.` | True; `[]` |
| `Osimertinib is an inhibitor of EGFR and of ALK.` | True; `[]` |
| `Osimertinib inhibits EGFR and also ALK.` | True; `[]` |
| Control: `Osimertinib acts on EGFR and ALK.` | False; `relation: OSIMERTINIB — acts — ALK` |

No Q3 evidence mentions ALK. `_group` stops at `on`, `of`, or `also` (`src/claims.py:342-357`). `_clauses` does not split an elided predicate fragment (`:324-341`), and the later wording pass exempts all these grammar/relation words (`:552-553`). The extra named entity is left with no relation obligation. This also affects `target of`: with Q3+QC evidence, `EGFR is a target of osimertinib and of crizotinib.` passes although there is no retrieved crizotinib–EGFR edge. Sources: `spec_probe_results.json`, IDs `endpoint_preposition`, `endpoint_noun`, `endpoint_adverb`, `endpoint_control`, `noun_target_second`.

### B3. Pronouns resolve before the preceding clause is processed; verbatim evidence loses trial subjects

**Clause timing.** Use the unmodified union of evidence retrieved for Q3 and QC, with their linked question entities and the normal vocabulary/linker:

```text
Osimertinib acts on EGFR. Crizotinib acts on ALK and it inhibits EGFR.
```

Observed: True; `[]`. The union contains osimertinib–EGFR and crizotinib–ALK, but no crizotinib–EGFR edge. Replacing `and` with `.`, so that the last sentence is `It inhibits EGFR.`, gives False with `relation: CRIZOTINIB — inhibits — EGFR`. Omitting `it` (`... and inhibits EGFR.`) also correctly fails. The typed variant `... while this drug inhibits EGFR.` wrongly passes.

`_tokenise` resolves the entire unit at `src/claims.py:228`, before `_clauses` and the antecedent updates at `:259-261`; resolution at `:299-300` therefore uses the previous unit's osimertinib. The clause reader updates state too late to change the already substituted pronoun. Sources: `spec_probe_results.json`, IDs `pronoun_stale`, `pronoun_stale2`, `pronoun_fresh`, `elided`.

**Verbatim antecedent.** With Q2:

```text
NCT03909334 (PHASE2, ACTIVE_NOT_RECRUITING) evaluates OSIMERTINIB. It is phase 3.
```

Observed: True; `[]`. The named trial is PHASE2. In contrast, `NCT03909334 evaluates osimertinib. It is phase 3.` correctly fails. At `src/claims.py:221-226`, the exact-statement shortcut chooses the first result of `linker(bare)` as subject. The linker does not produce trial entities; NCT handling exists separately at `:274-275`. Thus the copied statement installs OSIMERTINIB as antecedent, admitting phase 3 from other trials of that drug. Sources: `root_design_probe.json`, IDs `verbatim_antecedent_trial`, `paraphrase_trial_wrong_phase_control`.

### B4. Numeric ownership still migrates between drugs and between attribute types

| Question | Exact answer | Observed |
|---|---|---|
| Q5 | `AstraZeneca sponsors osimertinib in 10 trials with carboplatin.` | True; `[]` |
| Q5 | Control: `AstraZeneca sponsors osimertinib in 10 trials.` | False; `number: 10` |
| Q5 | Diagnostic: `AstraZeneca sponsors osimertinib in 14 trials with carboplatin.` | False; `number: 14` |
| Q4 | `PLB1003 has 1 clinical trial.` | True; `[]` |

The retrieved AstraZeneca count is **14 for osimertinib**, **10 for carboplatin**; it does not establish ten trials combining them. `_owner` searches after a number before looking before it (`src/claims.py:460-468`, `:524`). The appended carboplatin captures the count even though the claim is about osimertinib; the incorrect 10 passes and the osimertinib count 14 fails. The 14 example is a diagnostic of assignment, not a claim that the combination is supported.

PLB1003 evidence explicitly says `max stage PHASE_1; 0 NSCLC trial(s) in this graph`. Numeric checking matches any number in a scoped statement (`:524-525`), so phase **1** satisfies a claimed count of **1** despite the count being **0**. This is a specific, reproducible limitation of counting, not merely a distant-entity issue. Sources: `spec_probe_results.json`, IDs `number_drug_other`, `count_after`, `count_vs_14`, `count_morph`.

### B5. Action validation matches `agonist` inside `antagonist`

Question QF; sole evidence: `FULVESTRANT acts on ESR1 (antagonist)`.

- `Fulvestrant activates ESR1.` → True; `[]`.
- `Fulvestrant is an agonist of ESR1.` → True; `[]`.
- Control: `Fulvestrant is an antagonist of ESR1.` → True, correctly.

`ACTION_WORDS` includes `agonist` (`src/claims.py:73-74`); `:454-455` uses substring containment rather than matching the action token/field. Consequently the action described in the evidence satisfies its opposite. Sources: `spec_probe_results.json`, IDs `action_antagonist`, `action_noun_agonist`, `action_control_antagonist`.

### B6. Heading handling discards claims; the bare-item verbatim pass bypasses joined headings

All with Q3 and its sole EGFR-inhibition statement:

| Exact answer (`\n` denotes a newline) | Observed |
|---|---|
| `osimertinib is safe:` | True; `[]` |
| `osimertinib is discontinued:\nOsimertinib acts on EGFR.` | True; `[]` |
| `these drugs are safe:\n- OSIMERTINIB acts on EGFR (inhibitor)` | True; `[]` |
| `these drugs do not act on EGFR:\n- OSIMERTINIB acts on EGFR (inhibitor)` | True; `[]` |
| `EGFR acts on these drugs:\n- OSIMERTINIB acts on EGFR (inhibitor)` | True; `[]` |
| Control: `these drugs are safe:\n- osimertinib` | False; `wording: safe` |

`_units` defers any non-bullet line ending in a colon and never emits it if no bullet follows (`src/claims.py:170-188`). Thus ordinary content words can disappear entirely. When a bullet does follow, joining does retain the heading (`:177-183`), but the shortcut tests **either** the combined unit **or the original bare item** against evidence (`:221`). A verbatim evidence item exempts an unsafe, negated, or reversed heading. These are separate paths; fixing dangling headings alone would leave the bare-item bypass. Sources: `root_design_probe.json`, IDs `discarded_heading`, `discarded_heading_before_prose`, `verbatim_under_unsafe_heading`, `verbatim_under_negated_heading`, `verbatim_under_reversed_heading`, `ordinary_bullet_heading_control`.

### B7. The META exception accepts biomedical claims, including an invented phase with zero evidence

| Question | Exact answer | Observed |
|---|---|---|
| Q6 | `This trial is phase 4.` | True; `[]`; **evidence_count=0** |
| Q2 | `This trial is phase 3.` | True; `[]` |
| Q2 | `This drug is not in trials.` | True; `[]` |
| Q1 | `It has 14 trials.` | True; `[]` |

These are not graph refusals. An unresolved pronoun should be reported, as the docstring explicitly says (`src/claims.py:22-24`). The early pass at `:233-236` permits every `FUNCTION`/negation word and examines only word tokens, ignoring numbers. `phase` and `trials` are grammar words. The global phase check also skips any one-digit phase whenever a linker is present (`src/query.py:504-508`), even if evidence is empty. A missing-subject phase fragment takes a similar early exit (`claims.py:247-254`).

Control: Q3 / `It inhibits EGFR.` correctly produces `no_antecedent: it`; the bug is the overbroad refusal exception, not an intentional general policy to accept unresolved claims. A legitimate `This graph cannot answer that question.` passes. Sources: `root_design_probe.json`, IDs `meta_france_unsupported_phase`, `meta_missing_typed_phase`, `meta_missing_negation`, `meta_missing_count`, `no_antecedent_control`.

### B8. Refused product spans become opaque entities, swallowing qualifiers and negation

All with Q3; all return True; `[]`:

- `osimertinib is liposomal.`
- `osimertinib is a biosimilar.`
- `Osimertinib is not liposomal.`
- `liposomal Tagrisso.`

The retrieved statement establishes only the EGFR action, not these product claims. `src/query.py:128-141` deliberately emits `Refused` spans and includes neighboring words. `src/claims.py:278-288` accepts them as entity placeholders; `:231-240` rejects `Missing` but does not reject `Refused`. The consumed span, including `not`, is no longer checked as wording or negation. In the Tagrisso example, the new alias exception (`query.py:495-499`, `:543-544`) admits the isolated brand token even though its enclosing product was refused. Sources: `standards_probe.json`, cases `refused_liposomal`, `refused_biosimilar`, `refused_negation`, `refused_alias`.

### B9. Citation stripping still accepts arbitrary content after `ORG:`

Q3 / `Osimertinib [ORG:is safe] acts on EGFR.` → True; `[]`.

Q3 / `Osimertinib [ORG:inhibits ALK and] acts on EGFR.` → True; `[]`.

The regex `ORG:[^\]]+` (`src/claims.py:136-137`) treats arbitrary bracket text as a citation, and `_units` deletes it at `:167`. It neither validates a source identifier nor checks membership in retrieved records. The ordinary R1 bracket example is now caught, but adding the citation prefix restores a text-deletion bypass. Sources: `root_design_probe.json`, IDs `citation_embedded_claim`, `citation_embedded_wrong_relation`.

## SHOULD FIX

### S1. False positives are much lower on the original corpus, but ordinary faithful forms still fail

The exact R1 corpus was rerun without rewriting its answers:

| Demo question | R1 faithful answers flagged | R2 faithful answers flagged |
|---|---:|---:|
| Q1 | 2/6 | 0/6 |
| Q2 | 2/6 | 0/6 |
| Q3 | 1/6 | 0/6 |
| Q4 | 3/6 | 0/6 |
| Q5 | 2/6 | 1/6 |
| Q6, refusals separately | 6/6 | 2/6 |

Evidence-answer false positives improved from **10/30 (33.3%) to 1/30 (3.3%)**. This small hand-authored diagnostic corpus does not estimate a production LLM rate or support saying that most faithful answers fail. The remaining evidence-answer rejection is Q5 / `AstraZeneca supports trials studying osimertinib in NSCLC.` → False, `wording: supports`; the repair notes explicitly identify this as intentional strictness.

Other confirmed faithful/refusal failures:

| Question | Exact answer | Observed |
|---|---|---|
| Q3 | `Osimertinib acts on EGFR and it inhibits EGFR.` | False; `no_antecedent: it` |
| Q3 | `Osimertinib (Tagrisso) acts on EGFR.` | False; `wording: tagrisso` |
| Q3 | `AZD 9291 acts on EGFR.` | False; `number: 9291` |
| Q6 | `The graph covers NSCLC drugs and trials, so it cannot answer this question.` | False; `no_antecedent: it` |
| Q6 | `I cannot determine the capital of France from the retrieved evidence.` | False; `entity: France`, `no_subject: i cannot determine capital france` |

The first is the same within-unit antecedent timing error as B3. Repeated aliases are lost because the linker deduplicates by drug ID (`src/query.py:163-168`) before the tokenizer replaces all surface forms (`claims.py:281-288`). The spaced development code links correctly, but the global numeric pass does not exempt digits inside entity spans (`query.py:506-511`). Controls `Tagrisso acts on EGFR.` and `AZD9291 acts on EGFR.` pass. Evidence is in `replay_faithful_results.json`, `standards_probe.json`, and `spec_probe_results.json`.

### S2. Documentation and the repair table still promise more than the code establishes

- `README.md:508-520` and `README.ko.md:354-360` make categorical direction/action/ownership claims and say negations are always reported. B1–B9 contradict these claims. The acknowledged residual case—rearranging one evidence statement's words—does not explain discarded headings, source-like text, new words in refused spans, or stale antecedents. Even intended verbatim and META exceptions contradict “always”.
- `src/claims.py:10-24` promises checked relations and reported unresolved pronouns; B1, B2, B3 and B7 refute those statements. `:15-17` says attribute evidence names every clause entity, whereas numeric `scoped()` (`:473-477`) uses only the first clause entity and heuristic owner.
- `src/query.py:447` says a generated answer is verified to say nothing absent from evidence; `:461-466` retains categorical sentence-level guarantees. It was not updated to explain the clause parser's failure modes.
- `web/template.html:263-265` and `web/try.html:69-71` retain categorical guarantees about unsupported relations/clinical claims. The softer success text at `web/try.html:142` is an improvement, but still says checked relations and values match when B1/B4/B5 demonstrate the contrary.
- `CODEX_CLAIMS_R1_VERDICT.md:9` says the five R1 direction examples were repaired. The exact reversed noun still passes and is missing from `tests/test_claims.py:81-122`. Preserve the actual R1 cases, rather than treating the 33-case regression list as exhaustive.

The independent standards review found no separate coding-standard document to enforce and no hard style violation. Its behavioral/documentation findings are recorded separately in [standards_findings.md](standards_findings.md); the independent spec analysis is in [spec_findings.md](spec_findings.md). Those axes do not substitute for each other.

## NOTES

### Round-1 finding-by-finding disposition

**FIXED means the exact R1 reproductions are fixed, not that all variants of the mechanism are safe.** Every original probe was rerun: six scripts, **142 exact question/answer cases**, plus the dictionary experiment and six template cases. See [replay_report.md](replay_report.md) for all 29 reported blocker inputs and their exact current findings, and [replay_comparison.json](replay_comparison.json) for all 142 cases.

| R1 finding | R2 disposition | Evidence |
|---|---|---|
| B1 direction/endpoints | **NOT FIXED** | 1/5 exact examples still passes: reversed noun, B1 above. |
| B2 pronoun subject loss | **FIXED** | 0/4 exact examples pass, including newline; new timing/verbatim failures are B3. |
| B3 cross-entity phases/status/counts | **FIXED** | 0/5 exact examples pass; new count ownership failure is B4. |
| B4 bigram quotation laundering | **FIXED** | 0/3 exact examples pass; bigram exemption removed. New verbatim interactions are B3/B6. |
| B5 `non-` negation | **FIXED** | 0/2 exact examples pass; new refused-span loss is B8. |
| B6 brackets/non-English | **FIXED** | 0/4 exact examples pass; new `ORG:` citation route is B9. |
| B7 clinical grammar/action type | **FIXED** | 0/2 exact examples pass; new antagonist/agonist action failure is B5. |
| B8 numeric layouts/partial phases | **FIXED** | 0/4 exact examples pass; new semantic-slot failure is B4. |
| SF faithful paraphrases/refusals | **NOT FIXED**, substantially improved | 1/30 evidence answers and 2/6 refusals still flagged; S1 gives exact inputs. |
| SF Cartesian-product pair checks | **FIXED** | All three faithful drug/target, trial/drug, company/drug paired clauses now pass; swapped pairs fail. |
| SF dedup loses other sentences | **FIXED** | `Osimertinib is safe. EGFR is safe.` now retains both contexts; both are `wording: safe`. |
| SF documentation honesty | **NOT FIXED** | S2, with current file:line references and reproduced counterexamples. |

Historical outcomes above use `r1_report.md`, not the saved original JSON outputs: some `independent_*_results.json` files already reflect repaired behavior (for example the paired-clause result), so they are not a pristine R1 baseline. Fresh input identity was checked; replay source hashes and output-path/import-root adaptation diffs are retained in `replay_manifest.json` and `replay_*_adaptation.diff`.

### Regressions, templates, linker and scope

- **Tests:** `python -m pytest tests -q -p no:cacheprovider` → **128 passed**. The brief's 79 is the older suite size. The initial run had a cp949 subprocess-reader warning; the UTF-8 rerun passed all 128 in 6.24s without warnings (`replay_pytest_utf8.txt`). TEMP/TMP stayed under `r2/replay_temp`, with bytecode and pytest cache disabled.
- **Templates:** all **5/5 evidence template bodies** pass generated-prose checking after the same `Scope:` removal as the normal answer path. Full Scope-inclusive templates still fail. The France refusal template fails generated checking (`no_antecedent: it`, `no_subject: no entity question matched`); ordinary `ask()` uses its separate refusal path. All exact template texts/outputs are in `replay_faithful_results.json`.
- **Original linker experiment:** **7,610 dictionary keys / 1,066 drugs / 2,634 unique multiword aliases**, zero lost intended links from the abbreviation gate. `is a` stays unlinked; `AZD 9291`, `osimertinib mesylate`, `trastuzumab deruxtecan`, and `pemetrexed disodium` retain intended links. This replays the original gate-on/gate-off experiment, not an old-commit execution.
- **New punctuation handling:** there is no `link_entities` implementation change between 0c441e0 and a12762b; the new sanitization is in `claims.py:277`. `Osimertinib acts on EGFR!` passes. The question `Which drugs act on ALK!` (likewise `:` or `;`) still links no entity and yields `intent=unsupported`, while `?` works (`query.py:120`). This is an unaddressed question-path limitation, not a new linker regression.
- **Dictionary-to-parser coverage:** among 2,634 stored multiword aliases, 2,566 link an intended drug ID; five of these lose that ID during claim tokenization (two parenthesized chemical aliases and three parent/salt overlap cases). Exact strings and entity traces are in `standards_probe.json`. These counts describe parser discrepancies, not five newly introduced linker regressions.
- **Successful controls:** explicit reversed active relations, all original wrong named pairs, old clinical/negation attacks, Korean/mixed text, correct basic `target of`, correct `EGFR is inhibited by osimertinib`, and simple elided-subject `and inhibits` cases were exercised. Their passes/failures are retained alongside attacks. Fixes demonstrably improved behavior; the blockers remain independently reproducible.
- **Dedup limit:** distinct-sentence contexts are fixed, but Q3 / `Osimertinib is safe and EGFR is safe.` still yields two raw `safe` findings and only one final finding because both clauses retain the same unit text (`query.py:560-562`). The result remains False; dedup cannot turn a nonempty findings list into a pass. See `root_design_probe.json`, ID `dedup_same_unit`.

Reproduce from the repository root with `powershell -NoProfile -File audit_evidence_claims/r2/reproduce_all.ps1`. New-design probes are `root_design_probe.py`, `spec_probe.py`, and `standards_probe.py`; their adjacent JSON files contain exact input, output and retrieved evidence. Final tracked/staged diffs were empty; `git status --short` listed only the pre-existing untracked `audit_evidence_claims/r2/` tree.

VERDICT: CHANGES REQUIRED
