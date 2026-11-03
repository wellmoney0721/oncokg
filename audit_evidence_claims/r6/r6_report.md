# Independent claim-check audit, round 6

Reviewed **80da81b** against `9fda6f8`, using the real local graph and unchanged retrievals. **The principal R1–R5 attack reproductions are repaired, but one older diagnostic regresses and new ordinary unsupported claims pass outside README item 13's explicit residues.** No tracked files were edited. All new scratch files are under `audit_evidence_claims/r6/`; pre-existing `brief.md` and `log.txt` were preserved.

Support here means support in the question's retrieved evidence, not an external clinical judgment. All new blockers below use `Engine().check(question, answer)`, not synthetic evidence. Evidence-consistent passes and the disclosed one-statement rearrangement residue are treated as NOTES. No artificial encoding is needed for this verdict.

| Key | Exact question |
|---|---|
| Q1 | `Which companies are developing osimertinib?` |
| Q2 | `What trials evaluate Tagrisso?` |
| Q3 | `What does osimertinib target?` |
| Q4 | `Which drugs act on ALK?` |
| Q5 | `What is AstraZeneca running in NSCLC?` |
| Q6 | `What is the capital of France?` |

Independent confirmations: [root6_confirmation.py](root6_confirmation.py), [root6_confirmation.json](root6_confirmation.json). Each JSON row preserves the exact question and answer, full check output, and **all** retrieved evidence, beyond the application's eight-row preview. Additional probes: [root6_numeric.json](root6_numeric.json), [spec6_controls.json](spec6_controls.json), [docs6_probe_results.json](docs6_probe_results.json).

## BLOCKERS

Unless a row is explicitly a control, every attack below returns **`grounded=True`, `applicable=True`, `unsupported_claims=[]`**. FIXED elsewhere means an exact old input is corrected; it does not certify the whole language mechanism.

### B1. A predicate in a relative clause removes the first trial from a shared assertion

Q2, both pass:

```text
NCT03909334 (which is phase 2) and NCT07680790 are recruiting.
```

```text
NCT03909334, which evaluates osimertinib, and NCT07680790 are phase 3.
```

The relevant evidence is:

```text
NCT03909334 (PHASE2, ACTIVE_NOT_RECRUITING) evaluates OSIMERTINIB
NCT07680790 (PHASE3, RECRUITING) evaluates OSIMERTINIB
```

The parenthetical/relative description is faithful, but the final shared predicate incorrectly gives the first trial recruiting status or phase 3. Removing `which is` from the first answer and using the exact R5 parenthetical form rejects `status: recruiting`. Faithful controls replacing the first trial with NCT07738172 for recruiting, or NCT02411448 for phase 3, pass.

**Cause:** `src/claims.py:560-577` splits at `and` whenever both sides contain any predicate, including a subordinate `is` or `evaluates`. It separates the first trial from the coordinated main subject. The new all-subject-trials rule at `:913-918` sees only the second trial in the final clause. Parentheses were already removed at `:499`.

Artifacts: `root6_confirmation.json`, `B1_relative_status`, `B1_relative_phase`, and their controls. This transfers a value between two records and is outside the one-record rearrangement residue.

### B2. Groups after a record verb still borrow the last trial's status

Q2:

```text
The graph records NCT03909334 (phase 2) and NCT07680790 (phase 3) as recruiting trials.
```

Passes, despite NCT03909334 being ACTIVE_NOT_RECRUITING. Removing the parenthetical phases or reversing the two trials rejects `status: recruiting`. Substituting NCT07738172 for NCT03909334 passes correctly.

**Cause:** `records` is now a predicate (`src/claims.py:157-159`), before both trials. `trial_run` therefore has no subject trials before the predicate (`:915-918`); it falls back to the nearest trial run (`:919-926`). The intervening parenthetical tokens terminate `_group` (`:580-604`), leaving only the last trial for status validation (`:1033-1046`). Unlike B1, this example is one clause throughout.

Artifacts: `root6_confirmation.json`, `B2_record_status*`. This is another cross-record status transfer, not a vocabulary-only rearrangement of one statement.

### B3. A trial-count label after the drug names escapes shared-count checking

Q5, both pass:

```text
AstraZeneca sponsors trials of osimertinib and carboplatin: 10.
```

```text
AstraZeneca sponsors trials of carboplatin and osimertinib: 14.
```

The evidence gives AstraZeneca **14** trials of OSIMERTINIB and **10** of CARBOPLATIN in separate rows. It does not establish either shared or combined count. The first answer in particular cannot describe a ten-trial total containing the fourteen recorded osimertinib trials.

Adding `trials` after the final `10` rejects `count_ambiguous`. The exact repaired R5 `... osimertinib and carboplatin in trials in this graph: 10.` also rejects. The faithful `AstraZeneca sponsors 14 trials of osimertinib and 10 trials of carboplatin.` passes.

**Cause:** `is_count` scans backward only until an entity (`src/claims.py:883-889`). Here the last drug prevents it reaching `trials`. The value is accepted as an untyped figure belonging to the nearest drug (`:816-825,976-987`); the shared-count check only processes figures already recognized by `is_count` (`:1003-1018`).

Artifacts: `root6_confirmation.json`, `B3_*`. Both drugs are named, so no single evidence statement contains this claim's entities and count.

### B4. A neutral intervening company sentence loses the drug behind “such trials”

Q5:

```text
AstraZeneca sponsors trials of Tagrisso. It is a company. There are 10 such trials in this graph.
```

Passes. The fully named middle sentence, `AstraZeneca is a company.`, also passes. The only trials introduced are osimertinib trials, whose AstraZeneca count is 14; 10 belongs to carboplatin. Omitting the middle sentence makes the wrong 10 reject `number: 10`. Changing 10 to 14 passes correctly with the middle sentence.

**Cause:** `_State.note` replaces `last` with the current clause's entities (`src/claims.py:286-293`). The company sentence drops the drug from `last`. The new `such trials` restriction derives `prev_drugs` only from that one clause (`:486-487`) and requires exactly one previous drug to restrict the sponsor's count (`:857-859`). With none retained, the number can match any AstraZeneca row.

Artifacts: `root6_confirmation.json`, `B4_*`. The problem is cross-statement reference loss, not a new factual claim in the neutral middle sentence.

### B5. Groups after “records” or “includes” borrow the first drug's trial context

Q4:

```text
The graph records lorlatinib and PLB1003 in clinical trials.
```

Also passing: `The graph includes lorlatinib and PLB1003 in clinical trials.` and `The graph records NSCLC trials of lorlatinib and PLB1003.`

Relevant evidence:

```text
LORLATINIB acts on ALK (inhibitor; max stage APPROVAL; 13 NSCLC trial(s) in this graph)
PLB1003 acts on ALK (inhibitor; max stage PHASE_1; 0 NSCLC trial(s) in this graph)
```

Reversing the drug order rejects `wording: clinical` and `wording: trials`; the NSCLC form also rejects the indication claim. PLB1003 alone rejects. Replacing PLB1003 with CRIZOTINIB, which has 15 trials, passes correctly.

**Cause:** the new group-context rule collects entities only before the first predicate (`src/claims.py:831-837`). Both drugs follow the newly recognized record verb, so the group becomes only its first drug. `trials_for` then licenses the entire clause's trial context from that drug (`:897-908,1134-1140`).

Artifacts: `root6_confirmation.json`, `B5_*`; `spec6_controls.json`, `record_group_*`, `include_group_*`. PLB1003 borrows another row's positive trial context; this is outside the disclosed residue.

### B6. Kind assertions still have the wrong owner; an older rejected diagnostic regresses

| Q | Exact unsupported answer | Result |
|---|---|---|
| Q3 | `Osimertinib inhibits EGFR, which is a drug.` | True; [] |
| Q3 | `Osimertinib and EGFR are drugs.` | True; [] |
| Q2 | `NCT07680790 and osimertinib are clinical trials.` | True; [] |
| Q2 | `The graph records osimertinib as a clinical trial.` | True; [] |

The Q3 evidence is only `OSIMERTINIB acts on EGFR (inhibitor)`. It does not make EGFR a drug. Q2 records named trials evaluating OSIMERTINIB; it does not make OSIMERTINIB a trial. The kind words introduce unsupported content absent from those statements.

Controls isolate three failures:

- The relative-clause answer split into `Osimertinib inhibits EGFR. EGFR is a drug.` rejects `wording: drug`. The faithful relative sentence `EGFR is inhibited by osimertinib, which is a drug.` incorrectly rejects the same word.
- Reversing either mixed group rejects `wording: drugs` or `wording: clinical`; faithful homogeneous drug and trial groups pass.
- `Osimertinib is a clinical trial.` rejects `clinical` and `trial`, while the record form passes. `The graph records NCT07680790 as a clinical trial.` passes correctly.

**Cause:** `first_e` is chosen once for the whole clause (`src/claims.py:1085`). Copular kind words bind to this first entity (`:1096-1105`), so relative clauses and heterogeneous groups do not get their own correct owners. The trial-identity branch is additionally limited to a detected copula (`:1097-1101`), letting `records ... as a clinical trial` fall through to the general trial-context permission.

**Confirmed regression:** `Osimertinib and EGFR are drugs.` is the unchanged R4 `docs_controls_results/kind_target_nonrelation` diagnostic, cited in `r4/docs_findings.md:70`. It rejected in R4 and R5 but now passes. This is **NOT FIXED (REGRESSED)**, even though every primary numbered R1–R5 blocker reproduction is fixed. The replay report explicitly distinguishes this case.

Artifacts: `root6_confirmation.json`, `B6_*`; `spec6_controls.json`; `replay6_r4_docs_controls_results.json`.

### B7. A heading's retained noun attaches to the wrong entity inside a sentence item

Q3:

```text
These drugs:
- EGFR is inhibited by osimertinib.
```

Passes, classifying the listed subject EGFR as a drug. The simpler `These drugs:\n- EGFR` correctly rejects. The faithful inverse list, `These drugs:\n- Osimertinib inhibits EGFR.`, incorrectly rejects `wording: drugs`.

Q2 also passes `These clinical trials:\n- Osimertinib is evaluated in NCT07680790.`, although its standalone assertion that osimertinib is a clinical trial rejects.

**Cause:** `_join` substitutes the **entire item sentence** for the determiner (`src/claims.py:262-270`). The Q3 attack becomes `EGFR is inhibited by osimertinib drugs`; kind ownership attaches `drugs` to the last entity (`:1107-1109`). The faithful inverse becomes `Osimertinib inhibits EGFR drugs` and fails for the opposite reason. The natural user input has not malformed the sentence; the checker creates this attachment internally.

Artifacts: `root6_confirmation.json`, `B7_*`; `spec6_controls.json`, `heading_clinical_wrong`. The unsupported kind word is absent from the one evidence statement, so this is outside its vocabulary-rearrangement residue.

### B8. “As an inhibitor” reverses an expressed relation across multiple evidence records

Q4:

```text
ALK is listed as an inhibitor of lorlatinib and crizotinib.
```

Passes. This says the target ALK inhibits the two drugs. The retrieved evidence instead has separate `LORLATINIB acts on ALK (inhibitor; ...)` and `CRIZOTINIB acts on ALK (inhibitor; ...)` rows. No single retrieved statement contains ALK and both drugs.

The bare `ALK is an inhibitor of lorlatinib and crizotinib.` rejects `relation_direction: ALK inhibitor LORLATINIB/CRIZOTINIB`. The faithful `Lorlatinib and crizotinib are listed as inhibitors of ALK.` passes.

**Cause:** the new `as an inhibitor` branch at `src/claims.py:680-685` selects every Drug entity as a subject and every Target as an object, ignoring their expressed grammatical roles. Subsequent checks verify the two supported Drug-to-ALK edges, not the inverse assertion that was written. This is a natural relation error, not an encoding trick.

Unlike the Q3 two-entity variant retained as a NOTE below, this answer requires multiple evidence statements and therefore falls outside README13's explicit **one-statement** rearrangement residue. Artifacts: `root6_confirmation.json`, `B8_*`.

## SHOULD FIX

### S1. Historical faithful forms improve substantially; fresh natural forms still expose gaps

These are hand-authored diagnostic corpora, not production LLM pass-rate estimates. They overlap in purpose and must not be pooled as independent samples.

| Question | Original R1 | Added R3 | Fresh R5 replay | Fresh R6, raw |
|---|---:|---:|---:|---:|
| Q1 | 6/6 | 5/6 | 7/8 | 5/8 |
| Q2 | 6/6 | 6/6 | 8/8 | 6/8 |
| Q3 | 6/6 | 6/6 | 8/8 | 4/8 |
| Q4 | 6/6 | 6/6 | 8/8 | 3/8 |
| Q5 | 5/6 | 6/6 | 8/8 | 4/8 |
| Evidence answers | **29/30** | **29/30** | **39/40** | **22/40** |
| Q6 refusals, separately | 4/6 | 5/6 | 5/6 | 5/6 |

The R6 raw corpus contains two ambiguous presentation diagnostics: Q4's passive sentence followed by `Its maximum stage...` and Q5's ordered counts without an explicit mapping word. Excluding both gives **22/38 (57.9%)**, with Q4 3/7 and Q5 4/7. Their raw inputs/results remain preserved. A majority passes, so this audit does not claim that most faithful answers fail; the blocker verdict rests on unsupported passes above.

Clear faithful failures include:

| Q | Exact faithful answer | Observed, grounded=False |
|---|---|---|
| Q3 | `EGFR is inhibited by osimertinib, which is a drug.` | `wording: drug` |
| Q3 | `Inhibitors of EGFR include osimertinib.` | `entity: Inhibitors` |
| Q3 | `Inhibition of EGFR by osimertinib is recorded.` | `entity: Inhibition` |
| Q4 | `Lorlatinib, crizotinib and alectinib are approved ALK inhibitors.` | `wording: approved` |
| Q5 | `AstraZeneca: 14 NSCLC trials of Tagrisso; 10 NSCLC trials of carboplatin.` | `number: 10` |

The noun relations are correctly parsed when prefixed with `The`; the upstream capitalized-name heuristic (`src/query.py:543-551`) otherwise mistakes `Inhibitors`/`Inhibition` for new entities. The heading and relative-kind false positives share the causes of B6/B7. The approval group has separate supporting rows for all three drugs, but no single row containing all three names for ordinary-word support (`claims.py:447-448,867-871`). In the semicolon entry list, the second fragment does not retain the sponsor when scoping a sponsor–drug count (`:434-440,843-864`).

Evidence and all remaining failures: [docs6_findings.md](docs6_findings.md), [docs6_probe_results.json](docs6_probe_results.json), [replay6_report.md](replay6_report.md). Root-confirmed minimal cases are also in `root6_confirmation.json`, `S_*`, `B6_kind_relative_faithful`, `B7_heading_faithful`.

### S2. Documentation must distinguish exact repairs from broader rules

The README and UI now acknowledge pattern limitations and distinguish no findings from proof of truth. That improvement should be retained. `README.md:508-535` / `README.ko.md` item 13 explicitly disclose one-record rearrangements, unknown non-INN names and strict faithful/refusal handling. Those caveats do **not** explicitly cover the cross-record values, context transfer, or kind-word errors above.

Concrete remaining discrepancies:

- `src/claims.py:13-19,28-38` describes positional relations, group-wide attributes, kind ownership, referenced counts and heading preservation. B1–B8 demonstrate natural shapes where these descriptions do not hold. The introductory “not a guarantee” caveat does not list these now-known residues under the user's approval bar.
- `CODEX_CLAIMS_R5_VERDICT.md:7-13` accurately describes the exact old repairs but overgeneralizes to every member, shared values, kind owners and trial references. The boundary is narrower than that wording.
- `web/template.html:265` and the corresponding dashboard/index text say all escape shapes found in five rounds are blocked by regression tests. The historical mixed-kind diagnostic now passes again (B6). The numbered old blocker repairs should not be generalized to every prior diagnostic.
- The inherited module introduction `src/query.py:12-18` says the model can only change prose and unsupported content is reported rather than shipped. The actual checker allows the new unsupported answers above. Its narrower method docstring and the UI's caution are more accurate than this introduction.
- `CODEX_CLAIMS_R5_VERDICT.md:17-19` reports **38/40** for the fresh R5 corpus and includes a France refusal among two remaining cases. The current unmodified evidence-answer corpus is **39/40**, with that refusal in a separate Q6 group. This is a conservative denominator error, a NOTE rather than a blocker.

The overall documentation findings R1 / R2 S2 / R3 S2 / R4 S2 / R5 S2 are **NOT FIXED overall**: many exact historical discrepancies are corrected, but these current omissions and overstatements remain. `web/try.html` already describes “no problem found” rather than a truth certificate; no new independent defect was found in that box's caution.

## NOTES

### Every earlier reproduction and finding

**31 historical scripts were rerun**, from copies confined to r6. **853 answer cases were checked for input identity:** R1 142, R2 104, R3 192, R4 168, R5 247. Four citation transformations, template checks and dictionary experiments are additional. Original internal-call adaptations and obsolete historical-result assertions are recorded in the adaptation diffs; questions, answers and direct/filtered evidence inputs were preserved.

Full **FIXED / NOT FIXED per finding**, exact question/answer/result tables, source hashes and script exit codes are in [replay6_report.md](replay6_report.md), [replay6_dispositions.json](replay6_dispositions.json), and [replay6_manifest.json](replay6_manifest.json). The aggregate inputs/outputs are in [replay6_all_cases.json](replay6_all_cases.json).

| Prior finding | R6 disposition | Evidence |
|---|---|---|
| R1 B1 direction/endpoints | FIXED | 0/5 exact inputs still pass |
| R1 B2 pronoun subject loss | FIXED | 0/4 exact inputs still pass |
| R1 B3 phase/status/count pooling | FIXED | 0/5 exact inputs still pass |
| R1 B4 bigram laundering | FIXED | 0/3 exact inputs still pass |
| R1 B5 non- negation | FIXED | 0/2 exact inputs still pass |
| R1 B6 brackets/non-English | FIXED | 0/4 exact inputs still pass |
| R1 B7 clinical grammar/action | FIXED | 0/2 exact inputs still pass |
| R1 B8 numeric layouts | FIXED | 0/4 exact inputs still pass |
| R2 B1 reversed noun/cleft | FIXED | 0/4 exact inputs still pass |
| R2 B2 hidden extra endpoint | FIXED | 0/4 exact inputs still pass |
| R2 B3 pronoun timing/verbatim trial | FIXED | 0/3 exact inputs still pass |
| R2 B4 numeric ownership/count slots | FIXED | 0/2 exact inputs still pass |
| R2 B5 action substring | FIXED | 0/2 exact inputs still pass |
| R2 B6 headings | FIXED | 0/5 exact inputs still pass |
| R2 B7 META clinical claims | FIXED | 0/4 exact inputs still pass |
| R2 B8 refused spans | FIXED | 0/4 exact inputs still pass |
| R2 B9 ORG citation content | FIXED | 0/2 exact inputs still pass |
| R3 B1 plural pronouns | FIXED | 0/2 exact inputs still pass |
| R3 B2 count borrowing | FIXED | 0/3 exact inputs still pass |
| R3 B3 headings | FIXED | 0/3 exact inputs still pass |
| R3 B4 clinical/kind/identity | FIXED | 0/7 exact inputs still pass |
| R3 weaker count-after-colon | FIXED | 0/1 exact inputs still pass |
| R3 weaker approval-in-NSCLC | FIXED | 0/1 exact inputs still pass |
| R3 weaker id-shaped citations | FIXED | 0/3 exact inputs still pass |
| R4 B1 heading adjective erasure | FIXED | 0/4 exact inputs still pass |
| R4 B2 plural chaining/object/elision | FIXED | 0/3 exact inputs still pass |
| R4 B3 count after trial label | FIXED | 0/1 exact inputs still pass |
| R4 B4 shared trial phase/status | FIXED | 0/3 exact inputs still pass |
| R4 B5 kind/clinical ownership | FIXED | 0/2 exact inputs still pass |
| R4 B6 spelled-out letters | FIXED | 0/2 exact inputs still pass |
| R4 weaker NSCLC/identity/percentage residues | FIXED | 0/3 exact inputs still pass |
| R4 additional phase-as-figure diagnostic | FIXED | 0/1 exact inputs still pass |
| R5 B1 heading kind/disease erasure | FIXED | 0/3 exact inputs still pass |
| R5 B2 named-group clinical context | FIXED | 0/3 exact inputs still pass |
| R5 B3 passive-list it | FIXED | 0/1 exact inputs still pass |
| R5 B4 parenthetical trial values | FIXED | 0/2 exact inputs still pass |
| R5 B5 longer trial labels/such trials | FIXED | 0/3 exact inputs still pass |
| R5 B6 kind-word owners/trial identity | FIXED | 0/3 exact inputs still pass |
| R5 N2 spaced percent/comma letters | FIXED | 0/3 exact inputs still pass |
| R4 kind-group diagnostic (REGRESSED) | NOT FIXED | 1/1 exact inputs still pass |
| R2 S1 inline pronoun/repeated alias/spaced code | FIXED | 0/3 exact faithful inputs still fail |
| R3 S1 six specifically cited faithful forms | FIXED | 0/6 exact faithful inputs still fail |
| R4 S1 five specifically cited faithful forms | FIXED | 0/5 exact faithful inputs still fail |
| R5 S1 twelve original fresh faithful failures | NOT FIXED | 1/12 exact faithful inputs still fail |
| R5 S1 two kind-owner controls | FIXED | 0/2 exact faithful inputs still fail |
| R1 SF faithful/refusal handling overall | NOT FIXED; mostly-pass bar met | 29/30 evidence answers, 4/6 refusals pass |
| R2 S1 faithful/refusal handling overall | NOT FIXED; mostly-pass bar met | same R1 residual supports/refusal forms |
| R3 S1 faithful/refusal handling overall | NOT FIXED; mostly-pass bar met | 29/30 evidence answers, 5/6 refusals pass |
| R4 S1 faithful/refusal handling overall | NOT FIXED; mostly-pass bar met | same remaining faithful/refusal failures |
| R5 S1 faithful/refusal handling overall | NOT FIXED; mostly-pass bar met | 39/40 evidence answers, 5/6 refusals pass |
| R1 SF Cartesian-product pairs | FIXED | All faithful joined/split pairs pass; swaps reject |
| R1 SF distinct-sentence dedup | FIXED | Both safe contexts retained; same-unit merging remains a NOTE |
| R1 SF documentation overall | NOT FIXED overall | Earlier caveats improved; R4 kind-group regression lies outside README item 13 explicit residues; see separate R6 documentation review |
| R2 S2 documentation overall | NOT FIXED overall | Earlier caveats improved; R4 kind-group regression lies outside README item 13 explicit residues; see separate R6 documentation review |
| R3 S2 documentation overall | NOT FIXED overall | Earlier caveats improved; R4 kind-group regression lies outside README item 13 explicit residues; see separate R6 documentation review |
| R4 S2 documentation overall | NOT FIXED overall | Earlier caveats improved; R4 kind-group regression lies outside README item 13 explicit residues; see separate R6 documentation review |
| R5 S2 documentation overall | NOT FIXED overall | Earlier caveats improved; R4 kind-group regression lies outside README item 13 explicit residues; see separate R6 documentation review |

The sole unsafe False-to-True change found across the 606 R1–R4 replay cases is B6's old mixed-kind diagnostic. The other three newly passing old cases are evidence-consistent noun/punctuation forms and are NOTES, not regressions to block on. Historical passing controls and documented residues must not be described as rejected attack cases.

### Requested R6 attack surfaces

| Area | Observed result |
|---|---|
| Determiner-only heading slot | Exact bare-item repairs reject; whole sentence items attach kind incorrectly (B7) |
| Subject-group trial / NSCLC context | Pre-verb exact group repairs reject; post-record-verb groups leak (B5) |
| `it` after a list | Exact passive-list R5 attack rejects; supported group controls pass |
| Values after a verb about all subject trials | Parenthetical exact repair works; embedded predicates and record-verb objects leak (B1/B2) |
| Counts after `trials ...:` | Old labels reject; inserting drug names before the colon bypasses count typing (B3) |
| `such trials` | Immediate reference repaired; neutral entity sentence resets its drug context (B4) |
| `the drug X`, `X ... is a drug`, `is a clinical trial` | Exact old repairs work; relative/mixed-group/as-trial assertions leak (B6) |
| Noun relations after `include` / `by` | Repaired supported forms pass, reversed ordinary forms reject; initial capitalized nouns cause faithful FPs (S1) |
| `as an inhibitor` | Faithful form passes; reverse-owner form passes; Q3 one-record variant is a NOTE, Q4 multi-record variant is B8 |
| Record verbs and be-only identity | Faithful record forms improved; record groups and kind assertions expose B2/B5/B6 |
| `Company: N trials of X` | Repeated-company entries and wrong-count controls behave correctly; semicolon entry with elided company rejects faithfully (S1) |
| Object pronouns | R5 `2 trials of it` passes; wrong 14 count and shared `them` count reject; exact outputs in root confirmations/probes |
| Carried targets | Q3 `Osimertinib acts on EGFR. Its recorded action is inhibition.` passes; unsupported activation rejects |
| Negation, clinical ordinary words, markdown, mixed Korean, citations | Historical repros rerun; original attacks reject; no fresh artificial encoding drives the verdict |
| Documentation | Exact repairs acknowledged; remaining known-residue and scope discrepancies in S2 |

### Residues and evidence-consistent passes

Q3 `EGFR is listed as an inhibitor of osimertinib.` passes, whereas `EGFR is an inhibitor of osimertinib.` rejects `relation_direction`. The `as an inhibitor` branch (`src/claims.py:680-685`) collects entities by expected types and ignores the expressed owner. This contradicts the literal positional-relation description, but conservatively falls under README13's broad one-statement rearrangement residue. This **two-entity example is not an independent verdict driver**. The faithful inverse passes too. B8 separately demonstrates the same mechanism across multiple records, outside that explicit residue.

Q4 `ALK: 13 trials of lorlatinib.` passes and can faithfully label lorlatinib's ALK evidence; this is a NOTE, not a blocker. Correct paired counts, aliases, supported active/passive inhibition, homogeneous kind groups, valid citations and supported carried-target inhibition are likewise not blockers.

### Regressions, linker, dedup and filesystem integrity

- `python -m pytest tests -q -p no:cacheprovider` → **275 passed in 8.24s**, exit 0, empty stderr. Bytecode/cache writes were disabled and TEMP/TMP were confined to `r6/replay6_temp`.
- **5/5 evidence template prose bodies pass**, retaining headings and applying the same `Scope:` removal used by the normal path. Scope-inclusive generated-check inputs and the generated-check France refusal still reject; the normal `ask()` refusal path succeeds. Exact text/output: `replay6_faithful_results.json`.
- Dictionary: **7,610 keys / 1,066 drugs / 2,634 unique multiword aliases**. The short-word gate loses **zero** intended links versus its prior behavior; `is a` remains unlinked. `AZD 9291`, `osimertinib mesylate`, `trastuzumab deruxtecan`, and `pemetrexed disodium` retain links. The separate tokenizer audit's five previously documented discrepancies remain; no new dictionary regression was found.
- `Osimertinib is safe. EGFR is safe.` retains two sentence contexts and rejects. Same-unit duplicate `safe` wording still merges, but remains rejected; dedup does not empty the findings list. Historical bigram-laundering attacks reject.
- ALK question punctuation `!`, `:` and `;` remains an unchanged linker limitation; `?` works.
- Tracked and staged diffs are empty. [root6_verification.json](root6_verification.json) and [replay6_verification.json](replay6_verification.json) preserve HEAD and source/data hashes. No repair, commit, network request, server, external message or model-generation call was performed.

Historical replay and tests: `powershell -NoProfile -File audit_evidence_claims/r6/replay6_reproduce.ps1`. New root confirmations: `python -B audit_evidence_claims/r6/root6_confirmation.py`; exploratory numeric probes: `python -B audit_evidence_claims/r6/root6_numeric.py`. Independent spec/docs commands are in their linked reports. All output paths stay under r6.

VERDICT: CHANGES REQUIRED
