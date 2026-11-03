# Round 4 independent claim-check review

## BLOCKERS

Reviewed HEAD `2de10d95295e94c24060648ee01a195496df7acb` against parent `8d4a6060c6d48e6d1d20a2d1470238539bb8fcf9`, using the real local graph. **Every exact previously reported blocker is now rejected, but new unsupported claims still pass outside README item 13's explicit residues.** Regression tests pass: **213/213**. No tracked files were edited; all review-created files are under `audit_evidence_claims/r4/`.

Question keys below are exact inputs:

| Key | Question |
|---|---|
| Q1 | `Which companies are developing osimertinib?` |
| Q2 | `What trials evaluate Tagrisso?` |
| Q3 | `What does osimertinib target?` |
| Q4 | `Which drugs act on ALK?` |
| Q5 | `What is AstraZeneca running in NSCLC?` |
| Q6 | `What is the capital of France?` |

All blocker answers below were run through `Engine().check(question, answer)` with unmodified retrieved evidence. **Each returns `grounded=True`, `applicable=True`, `unsupported_claims=[]`.** The standard is support in this retrieval, not external clinical truth. Exact full outputs and evidence are preserved in [root4_confirmation.json](root4_confirmation.json), [root4_probe.json](root4_probe.json), and the linked specialist artifacts. Twenty-five selected outcomes were independently rerun by the root reviewer after the parallel reviews.

### B1. Heading substitution deletes the unsupported clinical assertion

Q3, exact answers (`\n` denotes a newline):

| Answer | Observed |
|---|---|
| `The following safe drugs:\n- OSIMERTINIB acts on EGFR (inhibitor).` | True; [] |
| `The following discontinued drugs:\n- OSIMERTINIB acts on EGFR (inhibitor).` | True; [] |
| `The following safe drugs:\n- Osimertinib` | True; [] |
| Control: `These drugs are safe:\n- OSIMERTINIB acts on EGFR (inhibitor).` | False; `wording: safe` |

The only evidence is `OSIMERTINIB acts on EGFR (inhibitor)`. Neither safety nor discontinuation is supported. At `src/claims.py:253-255`, `_join` substitutes `these|the following|following` **plus any optional alphabetic word**. It removes `safe` or `discontinued` before the checker sees the heading. Both ordinary units (`:296`) and copied-line headings (`:319-321`) use this function. Removing lenient mode cannot recover an erased word.

The same defect drops `terminated` from Q2 / `The following terminated trials:\n- NCT07680790 (PHASE3, RECRUITING) evaluates OSIMERTINIB.` The retrieved status is RECRUITING. Wrong-entity joined headings are otherwise rejected, isolating this to substitution rather than the dash exemption. These assertions introduce content absent from the evidence, so the one-statement rearrangement residue does not cover them.

Artifacts: `root4_confirmation.json` IDs `heading_safe`, `heading_discontinued`, `heading_safe_bare`, `heading_safe_control`; [docs_findings.md](docs_findings.md), D-B1 and its exact controls.

### B2. Plural handling still loses members after expansion, in objects, and in elided subjects

| Q | Exact answer | Observed |
|---|---|---|
| Q4 | `PLB1003 and LORLATINIB act on ALK and they act on ALK and they are approved.` | True; [] |
| Q4 | `LORLATINIB and PLB1003 act on ALK and are approved.` | True; [] |
| Q5 | `AstraZeneca sponsors osimertinib and carboplatin. It sponsors them in 10 trials.` | True; [] |
| Q4 control | `LORLATINIB and PLB1003 act on ALK and they are approved.` | False; `wording: approved` |

PLB1003 has `max stage PHASE_1`, whereas LORLATINIB has `max stage APPROVAL`. Q5 separately gives AstraZeneca 14 osimertinib trials and 10 carboplatin trials; it does not support the ten-trial assertion about both drugs.

Three related causes:

- Each plural member is checked at `src/claims.py:352-356`, but each check updates shared state at `:425-426`. `_State.note` (`:271-277`) replaces the group with the current singleton. A later `they` sees only the last drug. Reversing the initial drugs in the three-clause example rejects approval. The lowercase multi-sentence equivalent also passes.
- Object-position `them` receives `want='Drug'` at `:340-344`, bypassing the plural branch's `want is None` condition (`:345`). `:349-350` then uses the last drug stored in `by_type`, CARBOPLATIN. This loses OSIMERTINIB before both relation and count checking.
- An elided subject uses only `st.subject` (`:388-391`), so `and are approved` checks the first drug, not the coordinated group.

These claims transfer attributes across different drugs and evidence statements; they are not the listed one-statement residue. Artifacts: `root4_confirmation.json` IDs `plural_chain`, `plural_implicit`, `object_count`, `plural_original_fixed`; [spec_findings.md](spec_findings.md), B1/B2.

### B3. `trials: N` bypasses the new count ambiguity check

Q5:

| Exact answer | Observed |
|---|---|
| `AstraZeneca sponsors osimertinib and carboplatin in trials: 10.` | True; [] |
| Control: `AstraZeneca sponsors osimertinib and carboplatin in 10 trials.` | False; `count_ambiguous: OSIMERTINIB / CARBOPLATIN` |

The evidence gives separate 14/10 counts, with no ten-trial count for both drugs. The ordinary number checker recognizes a preceding trial label at `src/claims.py:798-802`, but `count_ambiguous` only looks for a trial word **after** the number (`:819-820`). The count is therefore validated against the final drug alone. Correct separate `14 trials of osimertinib and 10 trials of carboplatin` passes.

Artifacts: `root4_confirmation.json` IDs `colon_count`, `prefix_count_control`; [spec_probe2.json](spec_probe2.json), `count_label_shared_same`; [spec_controls.json](spec_controls.json). This is another cross-statement count transfer, outside the explicit residue.

### B4. A shared phase or status validates only one trial

Q2, each answer returns True; []:

```text
NCT03909334 and NCT07680790 are recruiting trials of osimertinib.
```

```text
NCT03909334 and NCT07680790 are phase 3 trials of osimertinib.
```

```text
Recruiting trials evaluating osimertinib include NCT07680790 and NCT03909334.
```

The evidence is explicit:

```text
NCT03909334 (PHASE2, ACTIVE_NOT_RECRUITING) evaluates OSIMERTINIB
NCT07680790 (PHASE3, RECRUITING) evaluates OSIMERTINIB
```

The new trial-noun/list relation checks cover both endpoints (`src/claims.py:559-575`, `:651-665`), but phase checking selects one nearest trial (`:779-785`) and status checking likewise selects one (`:848-851`). A trailing attribute selects the last trial; a prefix modifier selects the first listed trial. The assertion applies to both. Swapping the IDs in the recruiting-list example changes the result to False (`status: recruiting`). Elided `... evaluate osimertinib and are recruiting` also loses the group.

The original exact R1 group-status input is now rejected by `identity`, not by checking both statuses. Adding the faithful `trials of osimertinib` relation removes that incidental rejection and reveals the same ownership limitation. FIXED in the replay table is consequently an exact-input result, not a claim that the mechanism is safe.

Artifacts: `root4_confirmation.json` IDs `trial_group_status`, `trial_group_phase`, `trial_status_prefix`, `trial_status_swap`; [spec_findings.md](spec_findings.md), B4, including phase-prefix and elided controls. This requires multiple trial statements and is outside the listed residue.

### B5. Kind and clinical words borrow support from the wrong entity

| Q | Exact answer | Observed |
|---|---|---|
| Q3 | `EGFR is a drug inhibited by osimertinib.` | True; [] |
| Q3 control | `EGFR is a drug.` | False; `wording: drug` |
| Q4 | `PLB1003 inhibits ALK in clinical trials in this graph.` | True; [] |
| Q4 control | `PLB1003 has clinical trials.` | False; `wording: clinical`, `wording: trials` |

Q3 has only the osimertinib–EGFR inhibitor statement; it never calls EGFR a drug. `present` includes every entity kind anywhere in the clause (`src/claims.py:719-720`), and `:901-907` accepts `drug` whenever any Drug is present. The valid passive relation provides osimertinib and thus licenses a false kind claim about EGFR. The identity rule does not help because the clause contains a relation.

PLB1003's exact evidence is `PLB1003 acts on ALK (inhibitor; max stage PHASE_1; 0 NSCLC trial(s) in this graph)`. No Q4 statement contains `clinical`. The `wide` pool (`:745-759`) includes statements mentioning **any** clause entity, so ALK pulls in other drugs' positive trial counts. `about_trials` then accepts the new clinical-trials claim for PLB1003. A causal diagnostic checks the identical answer against only the unchanged PLB1003 row: it fails both `clinical` and `trials`; the full retrieval passes. The blocker itself uses the full normal retrieval.

These introduce `drug`/`clinical` absent from the relevant evidence and therefore are outside the one-statement vocabulary residue. Artifacts: `root4_confirmation.json` IDs `kind_drug`, `kind_drug_control`, `clinical_trial`, `clinical_trial_control`; [docs_diagnostics_results.json](docs_diagnostics_results.json), `trial_graph`, `trial_scope_full`, `trial_scope_plb_only`; [docs_findings.md](docs_findings.md), D-B2/D-B3.

### B6. Spelling out negation as letters is silently ignored

Q3 / `Osimertinib does N O T inhibit EGFR.` returns True; []. The lower-case `n o t` equivalent also passes. `src/claims.py:484-492` tokenizes the spelling as three single-letter words, and `:908` exempts all words shorter than two characters. This is a deliberately adversarial spelling, less natural than B1–B5; the verdict does not depend on it. It is nevertheless a reproduced unsupported negation, with additional text absent from the evidence and no matching explicit README residue. Ordinary `not`, `non-`, underscore and backtick controls remain rejected.

Artifacts: `root4_confirmation.json`, `split_negation`; `root4_probe.json`, `negation_split`, `non_ascii_hyphen`, `negation_underscore`, `negation_backtick`.

## SHOULD FIX

### S1. Faithful answers mostly pass, but new false positives remain

The two historical hand-authored corpora were replayed unchanged. They are diagnostic samples, not a production LLM distribution and not independent statistical samples to pool.

| Question | Original R1 corpus passed | R3 added corpus passed |
|---|---:|---:|
| Q1 | 6/6 | 5/6 |
| Q2 | 6/6 | 6/6 |
| Q3 | 6/6 | 6/6 |
| Q4 | 6/6 | 6/6 |
| Q5 | 5/6 | 6/6 |
| Evidence answers | **29/30 (96.7%)** | **29/30 (96.7%)** |
| Q6 refusals, separate | 4/6 | 5/6 |

These satisfy the tested **mostly-pass** part of the bar. New focused failures do not establish that most faithful answers fail:

| Q | Exact faithful answer | Observed |
|---|---|---|
| Q2 | `NCT07680790 and NCT02411448 are phase 3.` | False; `identity: NCT07680790 = NCT02411448` |
| Q5 | `AstraZeneca sponsors 14 trials of osimertinib (Tagrisso).` | False; `count_ambiguous: OSIMERTINIB / OSIMERTINIB` |
| Q4 | `LORLATINIB and CRIZOTINIB act on ALK. They are approved.` | False; `entity: They` |
| Q3 | `Osimertinib acts on EGFR [CHEMBL3353410, ENSG00000146648].` | False; `entity: ENSG00000146648` |
| Q2 | `Trials of osimertinib include NCT03909334 and NCT07680790.` | False; `fragment: OSIMERTINIB NCT03909334 NCT07680790` |

Causes and controls:

- `identity` (`src/claims.py:401-405`) treats coordinated subjects plus a shared copula as an equality. Both trials are PHASE3; spelling the statements separately passes.
- `count_ambiguous` (`:818-829`) counts mention positions, so a repeated alias is treated as another drug. Removing `(Tagrisso)` passes.
- The global capitalized-name test (`src/query.py:533-542`) has no `They` stop word. Lowercase `they` passes the same supported approval claim.
- Claim-level citation stripping accepts the comma-separated graph IDs, but the older global haystack (`query.py:482-487`) omits edge IDs and rejects ENSG. A single `[CHEMBL3353410]` citation passes. Space-separated valid IDs additionally mismatch `_strip_citations`' comma/semicolon split (`claims.py:211-218`).
- The trial-noun rule reads a trial before `of` (`claims.py:563-566`), whereas the faithful noun-list form puts the trials after `include`. The equivalent `Trials evaluating osimertinib include ...` passes.

The original `supports trials` wording and refusals naming France still fail as documented. The six specific R3 S1 repairs all pass. Exact inputs/outputs are in [replay4_report.md](replay4_report.md), [spec_findings.md](spec_findings.md), [docs_findings.md](docs_findings.md), and `root4_confirmation.json` / `root4_probe.json`.

### S2. Documentation improved, but the explicit known-residue list is incomplete

**Documentation/standards axis:** No separate repository coding-standard violation is asserted. The new `claims.py:10-11` explicitly calls its rules a description rather than a guarantee. `README.md:508-529`, `README.ko.md:354-365`, `src/query.py:448-466`, `web/template.html:263-267`, and `web/try.html:69-72,142-145` acknowledge pattern limitations and distinguish no findings from proof of truth. The original blanket documentation criticism should not be repeated unchanged.

However, the explicit known-pass list covers one-statement rearrangement, unknown non-INN drug names and odd evidence-consistent wording. It does not cover erased safety headings, cross-statement plural/count/status transfer, new kind/clinical words admitted through another entity, or ignored spelled-out negation. The broad unseen-shapes caveat is not the explicit known-residue disclosure required by this audit's approval bar. The heading claim is also materially incomplete: `claims.py:37-39` and README say headings are checked, but `_join` has already deleted the critical word in B1. These paths must be repaired or specifically disclosed.

Smaller precision issues: the docstring's nearest-entity phase summary (`claims.py:22-24`) does not reflect the new preference for the nearest **trial** (`:779-781`); `web/template.html:265` still says two adversarial rounds, while README describes three. The documentation-axis assessment is preserved separately in [docs_findings.md](docs_findings.md); the specification-axis assessment is in [spec_findings.md](spec_findings.md).

## NOTES

### Every prior finding: FIXED / NOT FIXED

Fourteen historical scripts were rerun through copies that write only under `r4/`: six R1, three R2, and five R3 scripts. **438 answer cases were checked for identical case IDs, questions and answers: 142 R1 + 104 R2 + 192 R3.** Dictionary probes, templates and punctuation experiments are additional. Original source hashes, adaptation diffs, return codes and new outputs are in [replay4_manifest.json](replay4_manifest.json). [replay4_report.md](replay4_report.md) gives every historical blocker's exact input and fresh output; [replay4_all_cases.json](replay4_all_cases.json) preserves all cases.

**FIXED means the exact reported reproductions are corrected. It does not mean all variants of the mechanism are safe.**

| Prior finding | Disposition | Exact prior blocker inputs still passing |
|---|---|---:|
| R1 B1 direction/endpoints | FIXED | 0/5 |
| R1 B2 pronoun subject loss | FIXED | 0/4 |
| R1 B3 phase/status/count pooling | FIXED | 0/5 |
| R1 B4 bigram laundering | FIXED | 0/3 |
| R1 B5 non- negation | FIXED | 0/2 |
| R1 B6 brackets/non-English | FIXED | 0/4 |
| R1 B7 clinical grammar/action | FIXED | 0/2 |
| R1 B8 numeric layouts | FIXED | 0/4 |
| R2 B1 reversed noun/cleft | FIXED | 0/4 |
| R2 B2 hidden endpoints | FIXED | 0/4 |
| R2 B3 pronoun timing/verbatim trial | FIXED | 0/3 |
| R2 B4 count ownership/slots | FIXED | 0/2 |
| R2 B5 action substring | FIXED | 0/2 |
| R2 B6 headings | FIXED | 0/5 |
| R2 B7 META clinical claims | FIXED | 0/4 |
| R2 B8 refused products | FIXED | 0/4 |
| R2 B9 ORG citation content | FIXED | 0/2 |
| R3 B1 plural pronouns | FIXED | 0/2 |
| R3 B2 count borrowing | FIXED | 0/3 |
| R3 B3 headings | FIXED | 0/3 |
| R3 B4 clinical/kind/identity | FIXED | 0/7 |
| R3 weaker count-after-label | FIXED | 0/1 |
| R3 weaker approval-in-NSCLC | FIXED | 0/1 |
| R3 weaker id-shaped citations | FIXED | 0/3 |
| R1 faithful/refusal handling | NOT FIXED overall; improved | 1/30 evidence answers and 2/6 refusals flagged |
| R1 Cartesian-product pair checks | FIXED | All three faithful pairs pass; swapped pairs fail |
| R1 distinct-sentence dedup | FIXED | Both separate `safe` contexts retained |
| R2 S1 faithful/refusal handling | NOT FIXED overall | Original supports/refusal failures remain |
| R2 S1 inline pronoun/repeated alias/spaced code | FIXED | All three exact inputs pass |
| R3 S1 six specifically cited faithful failures | FIXED | All six exact inputs pass |
| R3 S1 faithful/refusal handling overall | NOT FIXED overall; improved | 1/30 evidence answers and 1/6 refusals flagged |
| R1 documentation / R2 S2 / R3 S2 | NOT FIXED overall; improved | Old wording repaired; newly known residues still absent |

### Requested round-4 areas and residue boundary

| Area | Result |
|---|---|
| Plural/object pronouns | Original exact plural and singular-object repairs pass; group chaining, object plurals and elision fail B2. |
| `count_ambiguous` | Original numeric-prefix attacks fail; trailing labels bypass it (B3); alias false positive S1. |
| Kind words / clinical | Plain wrong-kind claims fail; a supported relation permits wrong-kind and clinical-support borrowing (B5). |
| NSCLC / approval | Tested `approved in/for NSCLC`, including approval with trial wording, fail. Plain `Lorlatinib is approved.` is evidence-consistent. |
| Identity | Original false equalities fail; coordinated faithful attributes are over-rejected (S1). |
| Headings / joined dash | Own-entity fragments are rejected; no production lenient path found. `_join` erases arbitrary modifiers (B1). |
| Citation stripping | Old fake ORG identifiers and mixed known/fake citations fail; a valid source citation does not hide an explicit safety claim. Valid target citation formats can be over-rejected (S1). |
| `trial of X` / `trials evaluating X include NCT...` | Correct tested relation forms pass and wrong-drug controls fail; shared attributes still fail B4. |
| Status nearest trial | Faithful singular post-object status passes; a group is checked against only one trial (B4). |
| Template headings | All 5 evidence template prose bodies pass with the new headings included. |
| README 13 / docstrings | Caveats improved; explicit known residue remains incomplete (S2). |

Inputs that pass **and agree with evidence** are NOTES: `Osimertinib was inhibiting EGFR.`, `EGFR has been inhibited by osimertinib.`, `Osimertinib is an EGFR blocker.`, `Osimertinib is evaluated at NCT03909334.`, and harmless punctuation on a copied line. `Osimertinib is Tagrisso.` also passes consistently.

The following are not used as independent blockers because they plausibly fit the explicitly accepted one-statement rearrangement residue: Q4 `PLB1003 acts on ALK in NSCLC trials.`; Q3 `Osimertinib inhibits EGFR and is EGFR.`; Q4 `LORLATINIB has 13% NSCLC trials.` (the percentage mark is lost). The clinical example in B5 deliberately adds `clinical`, absent from the retrieval, and has a causal cross-row control. The report does not reinterpret every awkward passing input as a new blocker.

### Regressions, dictionary, dedup and filesystem integrity

- `python -m pytest tests -q -p no:cacheprovider` -> **213 passed in 7.78s**, exit 0, empty stderr. The original 79-test count is obsolete. TEMP/TMP were confined to `r4/replay4_temp`; bytecode and pytest cache writes were disabled.
- **5/5 evidence template bodies pass** generated-prose checking after the same `Scope:` removal used by the normal answer path. All Scope-inclusive templates and the generated-check France refusal still fail as before; normal `ask()` has a separate refusal path. Exact templates are in [replay4_faithful_results.json](replay4_faithful_results.json).
- Dictionary: **7,610 keys / 1,066 drugs / 2,634 unique multiword aliases**. Original abbreviation-gate replay loses **zero** intended links; `is a` stays unlinked. The separate dictionary-to-tokenizer probe retains five known discrepancies, not new R4 regressions. Exact examples and preserved multiword links are in [replay4_report.md](replay4_report.md).
- Same-unit dedup still merges duplicate `safe` findings in `Osimertinib is safe and EGFR is safe.`; the answer remains False. It cannot turn a nonempty finding list into acceptance. Separate sentences retain both contexts.
- `Which drugs act on ALK!` / `:` / `;` still fail question target linking; `?` works. This is unchanged and separate from answer punctuation.
- Tracked and staged diffs are empty. HEAD, source/data hashes and selected independent confirmations are in [root4_verification.json](root4_verification.json); replay identity/source hashes are in [replay4_verification.json](replay4_verification.json). Pre-existing `r4/brief.md` and `r4/log.txt` were left untouched. No source repair, commit, server, network call or model generation was performed. The instruction about comparing source changes with KOA reference folders does not apply to this read-only review.

Reproduce all historical scripts and regression tests with `powershell -NoProfile -File audit_evidence_claims/r4/replay4_reproduce.ps1`. Reproduce all new probes with `powershell -NoProfile -File audit_evidence_claims/r4/reproduce_new.ps1`. Both write only under `r4/`. Full input/output artifacts accompany each script.

VERDICT: CHANGES REQUIRED
