# Round 3 independent claim-check review

## BLOCKERS

Audited HEAD `8d4a6060c6d48e6d1d20a2d1470238539bb8fcf9`, with repairs in `a12762b` and `9a80fcb`, against the real local graph. **All exact previously reported blocker inputs are now rejected, but new unsupported claims still return `grounded=True`.** No tracked file was edited. Scratch artifacts are confined to `audit_evidence_claims/r3/`; pre-existing `brief.md` and `log.txt` were not edited.

Question shorthand below always denotes these exact strings:

| ID | Question |
|---|---|
| Q1 | `Which companies are developing osimertinib?` |
| Q2 | `What trials evaluate Tagrisso?` |
| Q3 | `What does osimertinib target?` |
| Q4 | `Which drugs act on ALK?` |
| Q5 | `What is AstraZeneca running in NSCLC?` |
| Q6 | `What is the capital of France?` |

All new blockers use `Engine().check(question, answer)`, without fabricated evidence or a union of questions. `True; []` means `checks.grounded=True`, `checks.unsupported_claims=[]`. Evidence support means support in the **retrieved evidence for that question**, not whether a claim might be true elsewhere. The README's explicitly listed single-statement rearrangement and unknown-name residues are considered separately below.

### B1. Plural pronouns shrink a coordinated subject to one drug

Q4:

| Exact answer | Observed |
|---|---|
| `LORLATINIB and PLB1003 act on ALK and they are approved.` | **True; []** |
| `PLB1003 and LORLATINIB act on ALK and they are approved.` | False; `wording: approved` |
| `LORLATINIB and PLB1003 act on ALK and PLB1003 is approved.` | False; `wording: approved` |

Retrieved evidence gives LORLATINIB `max stage APPROVAL`, but PLB1003 `max stage PHASE_1`. Both have supported ALK edges. The first answer extends approval to **both** drugs; reversing their order preserves that claim but changes the result.

`_State.note` stores only `real[0]` as subject (`src/claims.py:243-248`). `they` is an untyped pronoun (`:134`) and resolves to that single subject (`:298-302`). The second clause is therefore checked only against LORLATINIB's approval. The same error occurs across sentences when the second sentence starts with lowercase `they`; capitalized `They` happens to be rejected by the global capitalized-name check, not by correct plural resolution.

This is outside README 13's listed residue: approval is transferred across **two drugs and separate evidence statements**, rather than rearranging one statement about the same entities. Reproductions: [root3_probe.json](root3_probe.json), IDs `pronoun_same_clause`, `pronoun_same_clause_swap`, `pronoun_explicit_control`, `pronoun_two_sentences`.

### B2. Covering every entity in a relation does not prevent cross-drug count borrowing

Q5:

| Exact answer | Observed |
|---|---|
| `AstraZeneca sponsors osimertinib in 10 trials evaluating carboplatin.` | **True; []** |
| `AstraZeneca sponsors osimertinib in 14 trials evaluating carboplatin.` | False; `number: 14` |
| `AstraZeneca sponsors 10 trials evaluating carboplatin and osimertinib.` | **True; []** |
| `AstraZeneca sponsors 10 trials evaluating osimertinib and carboplatin.` | False; `number: 10` |
| `AstraZeneca sponsors osimertinib and carboplatin in 10 trials.` | **True; []** |

The evidence separately states **14** AstraZeneca trials evaluating OSIMERTINIB and **10** evaluating CARBOPLATIN. It establishes neither ten osimertinib trials nor ten trials evaluating both drugs. The reordered coordinated answers have the same ten-trial assertion but different results. The 14-trial combination is a diagnostic control, not a claim that the combination is supported.

`_owner` picks one nearest entity (`src/claims.py:594-604`); numeric `scoped` requires only that entity plus the first clause entity (`:610-618`), and the count check uses that scope (`:672-684`). Both drugs can independently satisfy relation checks (`:540-565`, `:580-586`), so `unrelated_entity` (`:345-350`) has nothing to reject. The R2 example with `with carboplatin` is fixed only because carboplatin is uncovered; adding a checked evaluation predicate restores the original numerical problem.

This mixes distinct evidence statements and is outside the explicit single-statement residue. Reproductions: [numeric3_probe.json](numeric3_probe.json), IDs `count_swap_tail`, `count_swap_tail_control`, `count_coordinated`, `count_coordinated_reverse`; [root3_probe.json](root3_probe.json), `count_shared_group`.

### B3. Verbatim list items still weaken heading validation

Q3, sole evidence: `OSIMERTINIB acts on EGFR (inhibitor)`.

| Exact answer (`\n` is a newline) | Observed |
|---|---|
| `these drugs are sponsors of trials:\n- OSIMERTINIB acts on EGFR (inhibitor)` | **True; []** |
| `these drugs are activators:\n- OSIMERTINIB acts on EGFR (inhibitor)` | **True; []** |
| `these drugs inhibit EGFR with ALK:\n- OSIMERTINIB acts on EGFR (inhibitor)` | **True; []** |
| `Osimertinib is a sponsor of trials.` | False; `relation_incomplete: sponsor` |
| `Osimertinib is an activator.` | False; `relation_incomplete: activator` |
| `Osimertinib inhibits EGFR with ALK.` | False; `unrelated_entity: ALK` |

The first heading attributes trial sponsorship to the drug; the second calls an inhibitor an activator. Neither assertion is supported by Q3 evidence. The `with ALK` sentence is a secondary attachment diagnostic; the clear sponsorship assertion alone is sufficient.

The copied item fills the heading's subject, then calls `_check_unit(..., lenient=True)` (`src/claims.py:271-287`). Lenient mode disables missing-endpoint findings (`:567-572`), the fragment rule (`:338`), and uncovered-entity findings (`:345`). Without endpoints, action-type validation at `:587-590` is never reached. Thus headings are visited, but do not satisfy the same constraints as ordinary prose. The exact R2 unsafe/negated/reversed headings are fixed; these are new cases.

The new heading contributes `sponsors`, `trials`, or `activators`, absent from the sole evidence statement. This is neither the intentional copied-line exception nor the one-statement rearrangement residue. Reproductions: [root3_probe.json](root3_probe.json), `heading_sponsors_full`, `heading_activators_full`, `heading_with_alk` and corresponding `plain_*` controls.

### B4. Grammar and disease-context exemptions allow ordinary clinical claims without evidence

| Question | Exact answer | Observed |
|---|---|---|
| Q3 | `Osimertinib is in clinical trials.` | **True; []** |
| Q3 | `Osimertinib is in NSCLC trials.` | **True; []** |
| Q3 | `Osimertinib is an NSCLC drug.` | **True; []** |
| Q3 | `EGFR is a drug.` | **True; []** |
| Q6 | `There are clinical trials.` | **True; []; evidence_count=0** |

Q3's sole evidence contains only osimertinib's EGFR inhibition; it contains no clinical-trial or disease assertion. Q6 retrieves nothing. These are substantive claims, not graph refusals.

`clinical`, `trial(s)`, `drug(s)` and entity-type nouns are in `FUNCTION` (`src/claims.py:104-116`). With an entity they bypass wording validation (`:721-722`); without an entity, the no-subject branch reports nothing when all words are grammar (`:329-334`). The `nsclc` rule permits adjacency to `trials`/`drug(s)` or a preceding `in`, then removes the token without requiring disease evidence (`:690-699`). `Osimertinib is for lung cancer.` correctly fails, but changing the construction to `is an NSCLC drug` passes.

Related unchecked copulas show the fragment rule's limit: Q4 / `PLB1003 is LORLATINIB.` and Q2 / `NCT03909334 is NCT07680790.` both pass. `is` counts as a predicate, so the fragment guard (`:338-344`) does not apply, while it is not a checked relation. No retrieved statement equates these separate entities.

The core clinical examples add words absent from Q3 evidence, and Q6 has no statement to rearrange. They fall outside README 13's two explicit known-pass residues. Reproductions: [root3_probe.json](root3_probe.json), `clinical_trial_unsupported`, `nsclc_trial_unsupported`, `indication_drug`, `zero_evidence_clinical`, `fragment_drug_identity`, `fragment_trial_identity`; [docs3_focused_results.json](docs3_focused_results.json), `focused_07` for `EGFR is a drug.`.

## SHOULD FIX

### S1. Faithful evidence answers mostly pass, with natural forms still rejected

The original R1 corpus was replayed unchanged. A separate fresh corpus contains six hand-authored faithful answers per demo question. These are diagnostic samples, not a production LLM error-rate estimate; they should not be pooled as independent statistical samples.

| Question | Original corpus passed | Fresh corpus passed |
|---|---:|---:|
| Q1 | 6/6 | 5/6 |
| Q2 | 6/6 | 4/6 |
| Q3 | 6/6 | 4/6 |
| Q4 | 6/6 | 6/6 |
| Q5 | 5/6 | 5/6 |
| Evidence answers | **29/30 (96.7%)** | **24/30 (80%)** |
| Q6 refusals, separate | 4/6 | 2/6 |

Thus the tested evidence answers satisfy the **mostly-pass** part of the bar. The verdict is driven by B1–B4 and the incomplete documented residue, not by a claim that most faithful answers fail.

Representative exact failures:

| Q | Exact faithful answer | Observed |
|---|---|---|
| Q3 | `Osimertinib targets EGFR and inhibits it.` | False; `relation_direction: OSIMERTINIB inhibits OSIMERTINIB` |
| Q2 | `NCT03909334 evaluates osimertinib in phase 2.` | False; `phase: phase 2` |
| Q2 | `NCT03909334 is a phase II trial evaluating osimertinib.` | False; `wording: ii` |
| Q5 | `AstraZeneca sponsors 14 NSCLC trials evaluating osimertinib and 10 NSCLC trials evaluating carboplatin.` | False; `number: 10` |
| Q3 | `AZD9291 (AZD-9291) acts on EGFR.` | False; global `number: 9291` |
| Q3 | `Osimertinib (Tagrisso, AZD 9291, AZD9291) acts on EGFR.` | False; clause `number: 9291`, `wording: azd` |

Object pronouns are assigned the prior subject (`claims.py:298-302`). A phase after the drug selects drug max-stage evidence even when the sentence's named trial has the stated phase (`:657-664`). Roman phases are parsed (`:647-648`) but remain in the later wording list (`:701-726`). Repeated evaluation clauses split away the company owner (`:420-439`, `:614-617`). The global numeric-name exemption calls the deduplicating linker once (`query.py:508-513`), while claim tokenization permits only three alias-linking rounds (`claims.py:375`), producing separate repeated-alias failures.

`AZD-9291 acts on EGFR.` and `Osimertinib (Tagrisso, AZD 9291) acts on EGFR.` pass. The correct count-elision form `AstraZeneca sponsors 14 trials of osimertinib and 10 trials of carboplatin.` passes. Exact evidence, full findings, all corpus answers and more controls are in [docs3_review.md](docs3_review.md), [docs3_probe_results.json](docs3_probe_results.json), and [numeric3_findings.md](numeric3_findings.md).

### S2. Documentation is substantially more candid, but still does not cover known passes

`README.md:508-524` and `README.ko.md:354-362` now explicitly describe a word-order pattern checker with unseen-shape limitations. `src/query.py:448-466` no longer promises semantic verification. `web/template.html:263-265` and `web/try.html:69-72` include the caveat; `web/try.html:142-145` says nothing was flagged and expressly disclaims proof of correctness. Those are improvements, and the old blanket documentation criticism should not be repeated unchanged.

Nevertheless, the **explicit known-pass list** in `README.md:517-519` covers rearranging one evidence statement and an unknown non-INN drug name. B1–B4 involve multiple statements, skipped heading obligations, new clinical vocabulary, or no evidence. A generic warning that unseen shapes can fail does not specifically list these residues under the requested approval bar.

The `claims.py:10-27` docstring frames its rules as what a clause **must satisfy to pass**: all relation entities covered, both endpoints identified, values scoped, and content supported. B1–B4 show additional exceptions beyond the two named at `:29-33`. Revise the universal phrasing and explicit residue or repair these behaviors before approval. The R2 repair table correctly retracts the old reversed-noun repair claim (`CODEX_CLAIMS_R2_VERDICT.md:6-7`); the exact prior direction cases now fail.

No separate repository coding-standard document was found, and no standalone style violation is asserted. This is a behavioral/specification and documentation review, not a source-code change; the instruction to compare changed source against KOA reference folders is therefore not triggered. Separate documentation/standards reasoning is in [docs3_review.md](docs3_review.md).

## NOTES

### Every prior reported finding: FIXED / NOT FIXED

All **nine prior probe scripts** were rerun through copies that write only under `r3/`: six R1 scripts and the three additional R2 scripts. This covers **246 input-identity-checked answer cases (142 R1 + 104 R2)**, plus templates, dictionary experiments and punctuation probes. Historical outcomes follow the reports, since some old JSON outputs were overwritten during repairs. Source hashes, adaptation diffs and fresh outputs are preserved in [replay3_manifest.json](replay3_manifest.json) and the `replay3_*` files.

**FIXED below means every exact reported reproduction is fixed, not that all variants of its mechanism are safe.** [replay3_report.md](replay3_report.md) prints each prior blocker's exact question, answer and fresh findings; [replay3_all_cases.json](replay3_all_cases.json) contains all 246 cases.

| Prior finding | Disposition | Exact reported attacks still passing |
|---|---|---:|
| R1 B1 direction/endpoints | **FIXED** | 0/5 |
| R1 B2 pronoun subject loss | **FIXED** | 0/4 |
| R1 B3 phase/status/count pooling | **FIXED** | 0/5 |
| R1 B4 bigram quotation laundering | **FIXED** | 0/3 |
| R1 B5 `non-` negation | **FIXED** | 0/2 |
| R1 B6 brackets/non-English | **FIXED** | 0/4 |
| R1 B7 clinical grammar/action type | **FIXED** | 0/2 |
| R1 B8 numeric layouts/partial phases | **FIXED** | 0/4 |
| R2 B1 reversed noun/cleft | **FIXED** | 0/4 |
| R2 B2 extra endpoints | **FIXED** | 0/4 |
| R2 B3 clause timing/verbatim trial | **FIXED** | 0/3 |
| R2 B4 numeric ownership/count slots | **FIXED** | 0/2 |
| R2 B5 agonist/antagonist substring | **FIXED** | 0/2 |
| R2 B6 discarded/bypassed headings | **FIXED** | 0/5 |
| R2 B7 META clinical claims | **FIXED** | 0/4 |
| R2 B8 refused product spans | **FIXED** | 0/4 |
| R2 B9 whitespace ORG content | **FIXED** | 0/2 |
| R1 SF faithful paraphrases/refusals | **NOT FIXED** overall; improved | 1/30 evidence answers, 2/6 refusals still flagged |
| R1 SF Cartesian-product pairs | **FIXED** | All three faithful paired relations pass; swapped pairs fail |
| R1 SF distinct-sentence dedup | **FIXED** | Both `safe` sentence contexts retained |
| R1 SF docs / R2 S2 docs | **NOT FIXED** overall; improved | S2 above |
| R2 S1 faithful/refusal handling | **NOT FIXED** overall | Original `supports` and two refusal failures remain |
| R2 S1 specific inline pronoun, repeated alias, spaced code | **FIXED** for all three reported inputs | All three pass |

Remaining original faithful failures, exact inputs and findings:

- Q5 / `AstraZeneca supports trials studying osimertinib in NSCLC.` -> False; `unrelated_entity: Astrazeneca`, `wording: supports` (known strictness).
- Q6 / `The graph covers NSCLC drugs and trials, so it cannot answer this question.` -> False; `no_antecedent: it` (known refusal limitation).
- Q6 / `I cannot determine the capital of France from the retrieved evidence.` -> False; `entity: France`, `no_subject: i cannot determine capital france`.

The exact repaired R2 S1 forms are `Osimertinib acts on EGFR and it inhibits EGFR.`, `Osimertinib (Tagrisso) acts on EGFR.`, and `AZD 9291 acts on EGFR.`; all return True with no findings. Same-unit dedup still merges duplicate `safe` findings in `Osimertinib is safe and EGFR is safe.`; the answer remains False. This does not create a false acceptance.

### Round-3 design coverage and controls

| Requested area | Observed |
|---|---|
| `unrelated_entity` | Old stray endpoints rejected; additional checked relations restore cross-count borrowing (B2); disabled for copied-item headings (B3). |
| Fragment rule | R2 verb-less cross-entity/prepositional fragments rejected; copied-item headings bypass it (B3); copulas do not validate identity (B4). |
| Passive needs `by` | Reversed passives, missing `by`, and clefts rejected; correct `EGFR is inhibited by osimertinib.` and trial `in`/`at` forms pass. |
| Trial phase versus drug max stage | Wrong named-trial phases rejected; no new out-of-residue phase acceptance demonstrated. Natural post-object trial phase and Roman phases fail (S1). |
| Count rule | Exact old count attacks rejected; coordinated/cross-relation ownership still fails (B2). |
| Elided-repeat group extension | Correct `of 14 trials of osimertinib and 10 trials of carboplatin` passes, as does the three-drug 14/10/8 form; swapped values fail. Repeated `evaluating` form falsely fails (S1). |
| Per-clause/question-seeded pronouns | Old stale antecedents fixed. Q3 `It inhibits EGFR.` passes; `It inhibits ALK.` fails; `This trial is phase 3.` has no antecedent. Plural and object pronouns remain defective (B1/S1). |
| Headings under verbatim items | Old unsafe/negated/reversed headings fail; lenient relation omissions remain (B3). |
| `nsclc` indication rule | `is for lung cancer` fails; `is an NSCLC drug` and unsupported NSCLC-trial claims pass (B4). |
| Iterative aliases / name digits | Original aliases and spaced digits fixed; repeated numeric aliases/4th spelling still fail (S1). Standalone invented `9291 trials` remains rejected. |
| README 13 / docstrings / UI | Caveats improved; explicit residue and pass invariants remain incomplete (S2). |

### Already documented or weaker residues, not independent approval blockers

- Q4 / `PLB1003 has NSCLC trials: 1.` -> True, []; count detection looks only ahead from the number (`claims.py:674-682`), so PHASE_1 supplies 1 despite zero trials. Q4 / `LORLATINIB is approved in NSCLC.` also passes. Both plausibly fit the acknowledged one-statement rearrangement residue and are **not** used independently to reject approval.
- Q3 / `Osimertinib [ORG:is-safe] acts on EGFR.` and `[ORG:does-not-inhibit]` variants pass. `RE_CITE` accepts identifier-shaped content (`claims.py:153-155`) and removes it (`:197`) without retrieved-ID membership validation. These are weaker claim examples because they look like citations; the whitespace-containing R2 cases are fixed. Exact variants are retained in [docs3_focused_results.json](docs3_focused_results.json).
- `_flat` treats punctuation/case variants of evidence as copied lines, rather than byte-for-byte verbatim text. Tested punctuation variants did not establish an additional out-of-residue clinical claim.

### Regression, template, dictionary and filesystem verification

- `python -m pytest tests -q -p no:cacheprovider` -> **175 passed in 5.97s**, exit 0, empty stderr. The old brief's 79 and R2's 128 are previous suite sizes. UTF-8 mode and bytecode suppression were set; TEMP/TMP stayed under `r3/replay3_temp`.
- **5/5 evidence template prose bodies pass**, after the same `Scope:` removal as the normal answer path. Full Scope-inclusive templates and the France refusal template still fail generated checking as before; normal `ask()` has its separate refusal path. Exact template text/results: [replay3_faithful_results.json](replay3_faithful_results.json).
- Dictionary: **7,610 keys, 1,066 drugs, 2,634 unique multiword aliases**. The original abbreviation gate loses **zero** intended links; `is a` stays unlinked. The separate linker-to-tokenizer sweep has **2,566** aliases linking an intended ID and **five unchanged tokenizer discrepancies** (two parenthesized chemical names, three overlapping parent/salt names). These are not five new R3 linker regressions. See [numeric3_dictionary.json](numeric3_dictionary.json).
- Question punctuation limitation persists: `Which drugs act on ALK!` (also `:` / `;`) links no target; `?` works. Answer punctuation is handled separately. No new regression is claimed.
- Tracked and staged diffs are empty. Source hashes and final artifact integrity checks are recorded in [r3_verification.json](r3_verification.json). All review-created files are under `r3/`; no source repairs, commits, network calls, or model generation were performed.

Reproduce from the repository root with `powershell -NoProfile -File audit_evidence_claims/r3/reproduce_all.ps1`. This reruns the adapted previous probes, tests and new probes, writing only to `r3/`. The integrated report is an independent assessment; it does not promote passing regression examples into a general safety claim.

VERDICT: CHANGES REQUIRED
