# Independent claim-check audit, round 5

Reviewed HEAD **9fda6f8ec36e8b49d75e2d51d7f73ad3ba21e359**, diff `git diff 9fda6f8^...HEAD`, on the real local graph. **The exact earlier attacks are repaired, but new unsupported claims still pass outside README item 13's explicit residue.** No tracked files were edited. All new scratch artifacts are under `audit_evidence_claims/r5/`; pre-existing `brief.md` and `log.txt` were not edited by the review.

Support means support in the question's actual retrieved evidence, not an external medical judgment. New blockers below use `Engine().check(question, answer)` with unmodified retrievals, not synthetic evidence. A passing evidence-consistent answer is a NOTE. The disclosed one-statement rearrangement residue and artificial encodings are treated separately.

Question keys denote these exact inputs:

| Key | Question |
|---|---|
| Q1 | `Which companies are developing osimertinib?` |
| Q2 | `What trials evaluate Tagrisso?` |
| Q3 | `What does osimertinib target?` |
| Q4 | `Which drugs act on ALK?` |
| Q5 | `What is AstraZeneca running in NSCLC?` |
| Q6 | `What is the capital of France?` |

Primary independent confirmations: [root5_confirmation.py](root5_confirmation.py), [root5_confirmation.json](root5_confirmation.json). Exploratory numeric cases: [root5_numeric.py](root5_numeric.py), [root5_numeric.json](root5_numeric.json). Each result preserves the exact input, full check output and complete retrieved evidence, beyond the app's eight-row preview.

## BLOCKERS

Unless a row is explicitly a control, **every answer below returns `grounded=True`, `applicable=True`, `unsupported_claims=[]`**.

### B1. Heading substitution still deletes kind and disease claims

All with Q3:

| Exact answer (`\n` is a newline) | Observed |
|---|---|
| `The following companies inhibit EGFR:\n- Osimertinib` | True; [] |
| `These drugs:\n- EGFR` | True; [] |
| `These NSCLC drugs:\n- Osimertinib` | True; [] |
| Control: `The following safe drugs:\n- Osimertinib` | False; `wording: safe` |
| Control: `Osimertinib is an NSCLC drug.` | False; `indication: lung cancer` |
| Faithful control: `The following drugs inhibit EGFR:\n- Osimertinib` | True; [] |

The only Q3 evidence is `OSIMERTINIB acts on EGFR (inhibitor)`. It does not call osimertinib a company, EGFR a drug, or osimertinib an NSCLC drug. These ordinary headings add kind/disease words absent from that statement, so they are outside the accepted one-statement word-rearrangement residue.

**Cause:** `src/claims.py:260-264` replaces the entire determiner-plus-plain-noun slot, including optional `NSCLC`. Adjectives now survive, but a plain noun can itself be false. The first attack becomes `Osimertinib inhibit EGFR`; the kind validator never receives `companies`. Without the slot, `Companies inhibiting EGFR:\n- Osimertinib` rejects both `entity: Companies` and `wording: companies`.

Artifacts: `root5_confirmation.json` IDs `B1_*`; [spec5_extended.json](spec5_extended.json), `heading_wrong_kind_drug` and other `heading_*` cases. The exact R4 safe/discontinued heading repairs remain FIXED.

### B2. Named groups borrow the first member's clinical-trial context

Q4:

```text
LORLATINIB and PLB1003 are in clinical trials.
```

True; []. The more explicit `LORLATINIB and PLB1003 have clinical trials in this graph.` also passes, as does `LORLATINIB and PLB1003 inhibit ALK in clinical trials.`

Retrieved evidence:

```text
LORLATINIB acts on ALK (inhibitor; max stage APPROVAL; 13 NSCLC trial(s) in this graph)
PLB1003 acts on ALK (inhibitor; max stage PHASE_1; 0 NSCLC trial(s) in this graph)
```

No Q4 statement contains `clinical`. PLB1003's row explicitly gives zero trials in this graph. The shared clinical-trial assertion therefore borrows another drug's positive context; it is not merely the supported assertion that both inhibit ALK.

**Cause:** `_check_attributes` picks `subjects[0]` at `src/claims.py:771`; `wide` is now scoped only to that first subject at `:802`. `about_trials` then licenses all clinical/trial words at `:808-811,1013-1018`. Explicit named subject groups are not expanded by the per-member paths at `:383-398`, which handle pronouns and elision.

Controls: reverse the names to `PLB1003 and LORLATINIB are in clinical trials.` -> False, `wording: clinical`, `wording: trials`; singular PLB1003 -> the same findings. `LORLATINIB and PLB1003 inhibit ALK. They are in clinical trials.` also rejects. Supported LORLATINIB + CRIZOTINIB clinical context passes. This order dependence isolates the first-member leak, outside the one-statement residue.

Artifacts: `root5_confirmation.json`, `B2_*`; [spec5_controls.json](spec5_controls.json), `clinical_group_graph` and reverse; [spec5_findings.md](spec5_findings.md).

### B3. `It` after a passive list still misses the documented group check

Q4:

```text
ALK is targeted by LORLATINIB and PLB1003. It is approved.
```

True; []. Changing `It` to `They` rejects `wording: approved`. Using the active first sentence, `LORLATINIB and PLB1003 target ALK. It is approved.`, also rejects. The faithful passive LORLATINIB + CRIZOTINIB list followed by `They are approved.` passes.

**Cause:** the passive sentence leaves `st.group` as `[ALK]`. The largest same-type group from `st.last` is selected at `src/claims.py:368-369` only when the pronoun belongs to `PLURAL`; `it` does not (`:155`). It resolves to ALK at `:377-379`, whose evidence pool contains other drugs' approval. This is the opposite of the explicit B2 repair claim in `CODEX_CLAIMS_R4_VERDICT.md:10` and the per-member `it` description in `claims.py:32-33`.

Approval of the target ALK is unsupported, and the documented conservative interpretation of the two-drug list must also reject because PLB1003 has only PHASE_1. Because the pronoun can be semantically ambiguous and the later clause can resemble the broad single-row residue, this is principally a **confirmed repair/code/documentation discrepancy**, not the sole basis for the verdict. B1, B2, B4, B5 and B6 independently fail the outside-residue bar.

Artifacts: `root5_confirmation.json`, `B3_*`; `spec5_probe.json`, `passive_it_approval` / `passive_they_approval`.

### B4. Parenthetical metadata breaks shared trial phase/status ownership

Q2, both pass:

```text
NCT03909334 (phase 2) and NCT07680790 (phase 3) are recruiting.
```

```text
NCT03909334 (active, not recruiting) and NCT07680790 are phase 3.
```

Evidence:

```text
NCT03909334 (PHASE2, ACTIVE_NOT_RECRUITING) evaluates OSIMERTINIB
NCT07680790 (PHASE3, RECRUITING) evaluates OSIMERTINIB
```

The first answer incorrectly calls NCT03909334 recruiting; the second assigns it phase 3. Each uses a natural parenthetical descriptor that is itself correct.

**Cause:** `trial_run` at `src/claims.py:814-826` asks `_group` for a contiguous run around the nearest trial. The intervening phase/status tokens stop the run before the earlier trial (`_group`, `:561-580`). Shared phase validation at `:849-860` or shared status validation at `:935-947` therefore checks only the last trial. The named subjects still include both trials; no general rule requires their shared attributes to cover the full subject list.

Controls: removing the parentheticals makes both claims fail (`status: recruiting` / `phase: phase 3`). Reversing the first answer's trial order makes it fail `status: recruiting`. The faithful `NCT07680790 and NCT02411448 are phase 3.` passes. This transfers values across two records, outside the explicit one-statement residue.

Artifacts: `root5_confirmation.json`, `B4_*`; `root5_numeric.json`, `status_phase_parentheses`, `status_phase_one`, `phase_context_parentheses`, and controls.

### B5. Counts escape through longer labels and cross-sentence references

Q5:

```text
AstraZeneca sponsors osimertinib and carboplatin in trials in this graph: 10.
```

True; []. The evidence has **14** trials for OSIMERTINIB and **10** for CARBOPLATIN; it does not establish a shared ten-trial count. The exact R4 immediate label `... in trials: 10.` now rejects `count_ambiguous`, but ordinary inserted words bypass it.

**Cause:** trial-count detection only examines three surrounding tokens (`src/claims.py:878-881`), while shared-count detection examines three after/two before (`:905-907`). `in this graph:` pushes `trials` out of both windows. The number is treated as an untyped figure and validated against the nearest drug, CARBOPLATIN, using `scoped(..., "after")` (`:777-789,882-889`). `... in trials recorded: 10.` also passes. Correct separate `14 trials of osimertinib and 10 trials of carboplatin` passes; swapped counts reject both numbers.

A more natural cross-sentence variant also passes:

```text
AstraZeneca sponsors trials of Tagrisso. There are 10 such trials in this graph.
```

The faithful 14 version passes too. Replacing the second sentence with `This drug has 10 such trials in this graph.` rejects number 10. `AstraZeneca sponsors trials of Tagrisso and has 10 such trials.` also passes. `such` refers back to osimertinib trials, but the state retains AstraZeneca as the subject (`:470-471,281-288`), the elided-subject rule reuses it (`:427-433`), and numeric scope then needs only the sponsor, allowing CARBOPLATIN's row. There is no retained sponsor-drug pair for `such trials`. This is value transfer across two statements, not a harmless rewording of one record.

Artifacts: `root5_confirmation.json`, `B5_*`; `root5_numeric.json`, `count_label_*`, `count_such_*`, `count_separate_*`; independent confirmation in [spec5_anaphora.json](spec5_anaphora.json) and [spec5_anaphora_findings.md](spec5_anaphora_findings.md).

### B6. Kind words still accept the wrong owner or confuse participation with identity

| Q | Exact answer | Observed |
|---|---|---|
| Q3 | `EGFR, which is inhibited by osimertinib, is a drug.` | True; [] |
| Q3 | `The drug EGFR is inhibited by osimertinib.` | True; [] |
| Q2 | `Osimertinib is a clinical trial.` | True; [] |

The first two call the target EGFR a drug; the third calls a drug a trial. The Q3 evidence is only `OSIMERTINIB acts on EGFR (inhibitor)`. Q2 evidence consists of named NCT trials evaluating OSIMERTINIB. None supports these identities. `drug` in the Q3 assertion and `clinical trial` in Q2 are absent from the respective evidence statements, so these are outside the explicit one-statement vocabulary residue.

Three concrete paths:

- At `src/claims.py:987-988`, a kind word binds to the last entity mentioned anywhere before it. A relative clause can put OSIMERTINIB nearer than the main subject EGFR.
- With no preceding entity, the same line accepts `kind in present`, letting the Drug at the other end of the supported relation license `The drug EGFR`.
- `trial`, `trials`, and `clinical` skip that owner test (`:983-985`) and use `about_trials` (`:808-811,1013-1018`). The checker treats `is a trial` like `is in trials`; identity validation requires a named entity on each side (`:443-449`), so it does not intervene.

Controls: R4 `EGFR is a drug inhibited by osimertinib.` rejects `wording: drug`; Q3 `Osimertinib is a clinical trial.` rejects `clinical` and `trial`; faithful Q2 `Osimertinib is in clinical trials.` and `NCT07680790 is a clinical trial.` pass. The same owner rule also rejects faithful `EGFR is inhibited by the drug osimertinib.` and `Osimertinib, which inhibits EGFR, is a drug.` with `wording: drug`.

Artifacts: `root5_confirmation.json`, `B6_*`, `S1_*`; [docs5_controls_results.json](docs5_controls_results.json), `kind_prefix_*`, `trial_identity*`; [docs5_findings.md](docs5_findings.md).

## SHOULD FIX

### S1. Historical faithful answers mostly pass; fresh prose still has material gaps

These are diagnostic hand-authored corpora, not estimates of production LLM failure rates. Do not pool them as independent samples.

| Question | Original R1 corpus passed | R3 added corpus passed | Fresh R5 corpus passed |
|---|---:|---:|---:|
| Q1 | 6/6 | 5/6 | 4/8 |
| Q2 | 6/6 | 6/6 | 7/8 |
| Q3 | 6/6 | 6/6 | 5/8 |
| Q4 | 6/6 | 6/6 | 7/8 |
| Q5 | 5/6 | 6/6 | 5/8 |
| Evidence answers | **29/30 (96.7%)** | **29/30 (96.7%)** | **28/40 (70%)** |
| Q6 refusals, separate | 4/6 | 5/6 | 5/6 |

The tested evidence answers pass a majority, so this audit does not claim that most faithful answers fail. All five specifically cited R4 false positives now pass. Fresh examples still rejected:

| Q | Exact faithful answer | Observed (`grounded=False`) |
|---|---|---|
| Q3 | `EGFR is inhibited by the drug osimertinib.` | `wording: drug` |
| Q1 | `AstraZeneca sponsors 14 trials of osimertinib. Bristol Myers Squibb sponsors 2 trials of it.` | `number: 2`; `relation_direction: Bristol Myers Squibb sponsors Astrazeneca` |
| Q2 | `NCT07680790 is recruiting. NCT03909334 is active but not recruiting.` | `wording: active`, `wording: but`, `negation: not`, `status: recruiting` |
| Q4 | `The graph records 13 NSCLC trials of lorlatinib and 15 NSCLC trials of crizotinib.` | `number: 15` |
| Q5 | `AstraZeneca runs 6 NSCLC trials of pemetrexed and 6 of cisplatin.` | `count_ambiguous: PEMETREXED / CISPLATIN` |

Naming osimertinib instead of `it` in the Q1 example passes; splitting the Q4 counts into two sentences passes; `active, not recruiting` passes in place of `active but not recruiting`. These isolate parser limitations, rather than lack of supporting evidence. Full failures and source-based validation of all 40 new answers are in [docs5_findings.md](docs5_findings.md), [docs5_faithful_evidence_review.json](docs5_faithful_evidence_review.json), and [docs5_faithful_summary.json](docs5_faithful_summary.json).

Unchanged historical failures include `supports trials`, sponsorship-not-development commentary and refusals naming France, which README already discloses. Two additional old R4 diagnostics still reject: Q4 `LORLATINIB and CRIZOTINIB are approved.` (`wording: approved`) and Q2 `NCT03909334 and NCT07680790 evaluate osimertinib. The former is phase 2 and the latter is phase 3.` (`former`/`latter` and phases). These are not new R5 regressions.

### S2. Documentation axis: better caveats, but incomplete explicit residues and repair claims

No separate repository coding-standard violation is asserted. The specification-axis findings are B1-B6; this documentation assessment is separate.

The earlier blanket criticism should not be repeated: `README.md:508-531`, `README.ko.md:354-366`, `claims.py:10-11,48-51`, `query.py:450-468`, `web/template.html:263-267`, and `web/try.html:69-72,142-145` acknowledge pattern limitations and distinguish no findings from proof of truth. The page now correctly says four rounds. Evidence-validated citation stripping in the global name check behaved as documented in the new controls.

However, the explicit known-pass list (`README.md:520-524`, `README.ko.md:361-363`) does not disclose the heading kind/disease erasure, named-group clinical borrowing, cross-record trial/status/count transfer, or new false kind assertions above. A general unseen-shapes caveat is not disclosure of these now-known residues under this audit's bar.

Concrete precision issues:

- `CODEX_CLAIMS_R4_VERDICT.md:10` says `they`/`it` after a passive list stand for both drugs; B3 shows the `it` path does not.
- `claims.py:33-35` broadly describes spelled-out letter rejection and heading preservation. Comma-separated spelling still passes, and the heading's noun/NSCLC modifier can be removed (B1).
- `claims.py:25` and `CODEX_CLAIMS_R4_VERDICT.md:18-19` describe percentage checking/fixing; a space before `%` still defeats it (N2). The guarantee needs this qualification even though this audit conservatively treats the one-row numeric variant as a residue note.
- `claims.py:22-26` describes prior-trial ownership less precisely than `trial_run`, which also handles a following run.
- `CODEX_CLAIMS_R4_VERDICT.md:3` says all 438 earlier exact reproductions were rejected, but that denominator included faithful/control cases. It should identify the rejected **attack** cases rather than all 438.

The original exact repairs are genuine; the documentation's problem is the scope claimed for them and omission of newly demonstrated residues.

## NOTES

### Every earlier finding: FIXED / NOT FIXED

**606 exact answer inputs were replayed** through 23 original scripts copied/adapted only under `r5/`: R1 **142**, R2 **104**, R3 **192**, R4 **168**. Case IDs, questions and answers were checked for identity. Dictionary/template experiments and four citation transformations are additional. Some historical result files had been overwritten during repairs; historical dispositions use the actual prior reports, not overwritten result Booleans. Source hashes, adaptation diffs and exit codes are in [replay5_manifest.json](replay5_manifest.json).

**FIXED means the exact reported reproductions are corrected, not that the mechanism has no new variants.** The full per-input questions, answers and fresh findings are in [replay5_report.md](replay5_report.md); machine-readable mapping: [replay5_dispositions.json](replay5_dispositions.json).

| Prior finding | Disposition | Exact prior attacks still passing |
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
| R2 B2 hidden extra endpoint | FIXED | 0/4 |
| R2 B3 pronoun timing/verbatim trial | FIXED | 0/3 |
| R2 B4 numeric ownership/count slots | FIXED | 0/2 |
| R2 B5 action substring | FIXED | 0/2 |
| R2 B6 headings | FIXED | 0/5 |
| R2 B7 META clinical claims | FIXED | 0/4 |
| R2 B8 refused spans | FIXED | 0/4 |
| R2 B9 ORG citation content | FIXED | 0/2 |
| R3 B1 plural pronouns | FIXED | 0/2 |
| R3 B2 count borrowing | FIXED | 0/3 |
| R3 B3 headings | FIXED | 0/3 |
| R3 B4 clinical/kind/identity | FIXED | 0/7 |
| R3 weaker count-after-colon | FIXED | 0/1 |
| R3 weaker approval-in-NSCLC | FIXED | 0/1 |
| R3 weaker id-shaped citations | FIXED | 0/3 |
| R4 B1 heading adjective erasure | FIXED | 0/4 |
| R4 B2 plural chaining/object/elision | FIXED | 0/3 |
| R4 B3 count after trial label | FIXED | 0/1 |
| R4 B4 shared trial phase/status | FIXED | 0/3 |
| R4 B5 kind/clinical ownership | FIXED | 0/2 |
| R4 B6 spelled-out letters | FIXED | 0/2 |
| R4 weaker NSCLC/identity/attached-percent residues | FIXED | 0/3 |
| R4 additional phase-as-figure diagnostic | FIXED | 0/1 |

| Prior SHOULD FIX finding | Disposition and fresh evidence |
|---|---|
| R1 faithful/refusal handling | NOT FIXED overall; 29/30 evidence answers and 4/6 refusals pass |
| R1 Cartesian-product pair checks | FIXED; all three faithful joined/split relation pairs pass; all swapped pairs fail |
| R1 distinct-sentence dedup | FIXED; both separate `safe` contexts survive |
| R2 S1 faithful/refusal handling overall | NOT FIXED; documented supports/refusal failures remain |
| R2 S1 inline pronoun/repeated alias/spaced code | FIXED; all three exact cases pass |
| R3 S1 six specifically cited faithful failures | FIXED; all six pass |
| R3 S1 faithful/refusal handling overall | NOT FIXED; 29/30 evidence answers and 5/6 refusals pass |
| R4 S1 five specifically cited faithful failures | FIXED; shared phase, count alias, capitalized They, ENSG citation and Trials-of list all pass |
| R4 S1 overall faithful handling | NOT FIXED; historical remaining forms above still reject |
| R1 docs / R2 S2 / R3 S2 / R4 S2 overall | NOT FIXED overall; earlier wording improved, but R5 discrepancies and residues remain (S2) |

### Requested R5 areas and residue boundary

| Requested area | Result |
|---|---|
| Heading determiner/plain noun, adjectives retained | Safe/discontinued adjectives reject; kind and optional NSCLC are erased (B1) |
| Group survival across per-member checks | Original chained-pronoun attacks reject; faithful chains pass |
| Object `them` | Original shared 10-trial attack rejects; supported ALK object-pronoun relation passes and wrong EGFR edges reject |
| Elided subject after a group | Original shared approval/clinical claims reject |
| `it` / `they` after passive lists | `They` rejects unsupported shared attributes; `It` misses the promised expansion (B3) |
| Kind-word owner | Exact prior post-entity case rejects; prefix/relative-clause/trial-kind cases fail (B6) |
| Subject-scoped trial/NSCLC | Single PLB1003 repairs work; explicit named group still borrows first-member context (B2) |
| Trial runs for phase/status | Plain coordinated groups work; parenthetical metadata breaks coverage (B4) |
| Counts after a trial word | Immediate label works; longer labels and cross-sentence references fail (B5) |
| Alias de-duplication in counts | Correct Tagrisso/osimertinib aliases pass; wrong 10 count rejects; two separate drug/alias counts pass |
| Spelled-out letters | Whitespace N O T rejects; comma forms remain a secondary documented-rule mismatch (N2) |
| Identity across a verb / elided subject | `PLB1003 is LORLATINIB.` and `Osimertinib inhibits EGFR and is EGFR.` reject; alias identity passes |
| Percentages | Attached `13%` rejects; `13 %` and NBSP-% pass, conservatively a residue note plus documentation issue (N2) |
| Phase digits not counted as figures | `PLB1003 has 1 phase.` and phase-1-plus-one-trial controls reject; correct CONTELTINIB phase 1/2 passes |
| Evidence-validated global citation stripping | Valid comma/space/semicolon/newline IDs pass; unknown/mixed IDs and embedded safety/negation claims reject |
| Documentation | Concrete discrepancies remain (S2); old broad caveats and UI caution are present |

### N2. Secondary numeric/spelling discrepancies; not independent verdict drivers

Q4 `LORLATINIB has 13 % NSCLC trials.` and its nonbreaking-space version pass; attached `13%` rejects `number: 13%`. `RE_TOKEN` only captures a percent sign attached to digits (`src/claims.py:180-181`); a separate sign is discarded, leaving an ordinary supported count. `root5_numeric.json` records both. Because R4 already treated the one-row percentage transformation as plausibly covered by the broad residue, this review does not promote it to an independent blocker merely because R5 tried to fix it. The blanket percentage-repair statement remains inaccurate.

Q3 `Osimertinib does N, O, T inhibit EGFR.` and `Osimertinib is S, A, F, E.` pass, while whitespace-only letters reject. Commas reset the run at `claims.py:970-979`, and leftover single letters are skipped at `:1020`. These artificial forms are secondary notes about the explicitly stated letter rule, not a basis needed for rejection. Exact outputs are in `docs5_probe_results.json` / `docs5_controls_results.json`.

Evidence-consistent passes are not blockers: supported active/passive inhibition, correct group approval, alias identity, valid citations and correct paired per-drug counts. Q2 `Osimertinib is recruiting.` is conservatively assigned to the disclosed one-statement rearrangement residue, not counted as a new independent blocker.

### Regressions, linker, dedup and filesystem integrity

- `python -m pytest tests -q -p no:cacheprovider` -> **240 passed in 8.01s**, exit 0, empty stderr. TEMP/TMP were confined to `r5/replay5_temp`; bytecode and pytest cache writes were disabled.
- **5/5 evidence template prose bodies pass**, with template headings and the same `Scope:` removal used by the normal path. Scope-inclusive templates and the generated-check France refusal remain rejected; the ordinary template/refusal path is separate. Exact text is in `replay5_faithful_results.json`.
- Dictionary: **7,610 keys / 1,066 drugs / 2,634 unique multiword aliases**. Original short-word-gate replay loses **zero** intended links; `is a` stays unlinked. `AZD 9291`, `osimertinib mesylate`, `trastuzumab deruxtecan` and `pemetrexed disodium` retain their links. Five previously documented dictionary-to-tokenizer discrepancies are unchanged, not new R5 regressions.
- `Osimertinib is safe. EGFR is safe.` preserves two separate contexts. Same-unit `Osimertinib is safe and EGFR is safe.` still merges duplicate `safe` values, but remains False; dedup does not turn a nonempty finding list into a pass.
- ALK question punctuation with `!`, `:` or `;` remains an unchanged linker limitation; `?` works.
- Tracked and staged diffs are empty. HEAD, source/data SHA-256 hashes and fresh confirmation results are in [root5_verification.json](root5_verification.json) and [replay5_verification.json](replay5_verification.json). No source repair, commit, server, external message, network request or model generation was performed.

Reproduce the historical cases and regression suite with `powershell -NoProfile -File audit_evidence_claims/r5/replay5_reproduce.ps1`. Reproduce the new probes with `powershell -NoProfile -File audit_evidence_claims/r5/reproduce5_new.ps1`. Both confine outputs to `r5/`.

VERDICT: CHANGES REQUIRED
