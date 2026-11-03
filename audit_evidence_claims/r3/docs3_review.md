# Round 3 independent documentation, faithful-prose and passive review

Audited HEAD `8d4a606`; baseline `0c441e0`; source changes in `a12762b` and `9a80fcb`. No tracked files edited. Scratch files use `docs3_` under `audit_evidence_claims/r3/`. Python bytecode disabled. All results use the real local graph through `Engine().check(question, answer)`, with full retrieved evidence additionally saved from the same Engine KG. The JSON artifacts contain exact inputs, outputs, evidence and IDs.

## BLOCKERS

### D-B1. Clinical-trial claims made only from FUNCTION words are not checked

Question: `What does osimertinib target?`. Sole evidence: `OSIMERTINIB acts on EGFR (inhibitor)`.

Each returns `grounded=True`, `unsupported_claims=[]`:

- `Osimertinib is in clinical trials.` (`docs3_focused_results.json`, focused_01)
- `This drug is in clinical trials.` (focused_02)
- `Osimertinib has clinical trials.` (focused_03)
- `Osimertinib is a clinical trial.` (focused_04)
- `EGFR is a drug.` (focused_07)
- `EGFR is an organisation.` (focused_08)

Question: `What is the capital of France?`, evidence count **0**:

- `There are clinical trials.` -> `grounded=True`, `unsupported_claims=[]` (focused_10).
- Control `The trial is clinical.` -> False, `no_antecedent: the trial` (focused_11).

This is an unsupported clinical-trial existence/status assertion, not a factual assertion that trial evidence could never exist elsewhere. The audit checks the retrieved evidence for this question. It also accepts objectively incorrect entity classifications. `trial`, `clinical`, `drug`, `organisation` and `company` are unconditional FUNCTION words (`src/claims.py:104-116`). A clause with a subject reaches the exempt-word skip (`:721-722`); an entity-free clause containing only these words falls through the no-subject branch without a finding (`:329-334`). The fragment rule does not apply when `is`/`are` is a predicate (`:338`). This needs no obscure syntax, source-like markup or newly invented clinical adjective.

This is **outside README item 13's explicit known residue** (`README.md:517-519`, `README.ko.md:359-360`): the Q3 evidence contains no `clinical`, `trials`, `drug` or `organisation`; Q6 has no evidence statement at all. The broad warning that new sentence shapes may be misread is not the same as listing this known mechanism, under the user's approval bar.

### D-B2. Record-ID-shaped text can still hide a claim (secondary)

Same Q3 and evidence:

- `Osimertinib [ORG:is-safe] acts on EGFR.` -> True, [] (focused_18).
- `Osimertinib [ORG:inhibits-ALK] acts on EGFR.` -> True, [] (focused_19).
- `Osimertinib [ORG:does-not-inhibit] acts on EGFR.` -> True, [] (focused_20).

`RE_CITE` (`src/claims.py:153-155`) accepts arbitrary letters, dots, underscores and hyphens after `ORG:` and `_units` strips them (`:197`). It checks identifier shape, not whether the identifier exists in the retrieved evidence. These exact content strings are not in evidence. This is weaker than D-B1 as a normal-prose example because it resembles a citation; preserve it as an explicit residual ambiguity. Ordinary visible `Osimertinib is safe [ORG:safe].` correctly fails `wording: safe` (focused_17). The exact R2 whitespace example is repaired; this is a new no-whitespace variant, not a claim that the old reproduction still passes.

## SHOULD FIX

### D-S1. Mostly-pass faithful corpus, with ordinary failures

A fresh hand-authored corpus contains six plausible answers per demo question, selected from the actual evidence before execution. It includes ordinary active/passive prose, lists, aliases, paired clauses, scope disclaimers, and refusals. This is a diagnostic sample, not a production LLM error-rate estimate.

| Question | Faithful pass | Flagged |
|---|---:|---:|
| Q1: companies for osimertinib | 5/6 | 1/6 |
| Q2: trials evaluating Tagrisso | 4/6 | 2/6 |
| Q3: osimertinib target | 4/6 | 2/6 |
| Q4: ALK drugs | 6/6 | 0/6 |
| Q5: AstraZeneca portfolio | 5/6 | 1/6 |
| Evidence answers total | **24/30 (80%)** | **6/30 (20%)** |
| Q6: appropriate refusals, separate | 2/6 | 4/6 |

The evidence answers **mostly pass** this sample. Refusals remain over-strict and the code's normal query path has a separate refusal route. Do not describe the six rejected evidence answers as mostly failing.

Notable natural forms:

- Q3 `Osimertinib targets EGFR and inhibits it.` -> False, `relation_direction: OSIMERTINIB inhibits OSIMERTINIB`. An object pronoun is resolved to the previous clause's subject, not EGFR (`src/claims.py:298-302`, `:243-248`). This is a readable faithful answer.
- Q2 `Phase 3 trials evaluating osimertinib include NCT07680790 and NCT02411448.` -> False, unrelated_entity for both trials plus phase 3. Both trials are phase 3 in the evidence. The preposed phase selects the drug's max-stage rule; listed trials are not treated as subjects of evaluation.
- Q2 `The trials include NCT03909334 (phase 2, active not recruiting) and NCT07680790 (phase 3, recruiting).` -> False, `number: 2,`, `number: 3,`, status and phase findings. The global number regex includes a trailing comma (`src/query.py:514-519`); without a split predicate the attribute support also pools both trials.
- Q5 `AstraZeneca sponsors 14 NSCLC trials evaluating osimertinib and 10 NSCLC trials evaluating carboplatin.` -> False, number 10. The natural repeated evaluation clause loses the sponsorship owner. The nearby elided form with `of 14 trials of osimertinib and 10 trials of carboplatin` passes.
- Q3 `The mechanism recorded for osimertinib is inhibition of EGFR.` -> False, wording recorded. This is the explicitly acknowledged unknown-paraphrase strictness, not a new semantic bypass.
- Q1 sponsorship disclaimer `This is evidence of sponsorship, not evidence that it develops the drug.` is flagged for not/develops despite faithfully stating the graph's limitation. Verbatim evidence disclaimer passes by the intentional exception; paraphrase does not.

All 36 exact inputs and findings are tabulated below. Saved full results: `docs3_probe_results.json`.

### D-S2. Documentation now warns correctly, but the explicit residue list and docstring are still incomplete

- `README.md:508-524` / `README.ko.md:354-362` now explicitly call this a word-order pattern checker, acknowledge unseen sentence shapes, name two intentional exceptions, and list residual bypasses and over-strict forms. That is a real improvement; do not repeat the older blanket claim that these versions promise semantic verification.
- The **explicit** known-pass list (`README.md:517-519`) omits D-B1. Its two mechanisms are rearranging one evidence statement and an unknown non-INN drug name. An evidence-free clinical claim, and claims that introduce `clinical trials` into Q3, are neither mechanism. The user's approval bar requires new known passes to be repaired or explicitly listed.
- `src/claims.py:10-27` is headed 'What a clause must satisfy to pass' and claims every other content word has scoped evidence, relations bind every entity, unresolved pronouns are reported, and values belong to their owner. Some exceptions follow (`:29-38`), but FUNCTION words can themselves assert clinical facts (D-B1), outside the two stated narrow exceptions. The language should describe implemented checks and explicit limitations, rather than present these as universal pass invariants.
- `src/query.py:448-466` has appropriately replaced the former 'nothing absent from evidence' guarantee with a procedural description and explicit pattern-parser caveat; its pointer saying README lists known bypasses is incomplete once D-B1 is known.
- `web/template.html:263-265` and `web/try.html:69-72` now add the rule-based caveat. `web/try.html:142-145` says 'nothing flagged' and expressly says this is not proof of correctness. This success text is honest and materially better than the earlier claim that everything matches.
- `CODEX_CLAIMS_R2_VERDICT.md:6-7` explicitly corrects the R1 reversed-noun repair overstatement. Its citation claim ('ORG citation only whitespace-free identifiers') accurately describes the implemented syntax restriction, but does not establish source-ID membership validation.
- No independent repository style/standards file was found. No standalone style violation is asserted. The user requested source-code comparisons with KOA reference folders only when changing code; this audit changes no source code.

## NOTES

Passive-needs-by controls passed the intended direction tests: `EGFR is inhibited osimertinib.`, `EGFR was inhibited with osimertinib.`, cleft `EGFR is what inhibited osimertinib.`, and `Osimertinib was inhibited by EGFR.` all fail. Faithful `EGFR is inhibited by osimertinib.` and `Tagrisso is being evaluated in NCT07680790, a recruiting phase 3 trial.` pass. Nominal `The inhibition of EGFR by osimertinib.` is a faithful fragment but is still rejected, while the plainly reversed nominal is also rejected.

Known-residue distinction: Q4 `Lorlatinib is approved in NSCLC.` and `Lorlatinib is approved in lung cancer.` pass (focused_13, focused_16). These can plausibly be classified as the explicitly documented rearrangement of one evidence statement, because its source already contains APPROVAL and NSCLC. They are not counted as a new blocker here. Conversely Q3 clinical-trial claims contain clinical/trial content absent from its sole statement.

## Fresh faithful corpus: exact inputs and observed findings


| ID | Q | Exact answer | Grounded | Findings |
|---|---|---|---|---|
| faithful_01 | Q1 | `AstraZeneca is the lead sponsor of 14 trials evaluating osimertinib.` | True | [] |
| faithful_02 | Q1 | `The evidence records AstraZeneca as a lead sponsor of 14 trials evaluating osimertinib.` | True | [] |
| faithful_03 | Q1 | `AstraZeneca sponsors trials of osimertinib; Bristol Myers Squibb also sponsors trials of osimertinib.` | True | [] |
| faithful_04 | Q1 | `Osimertinib is being studied in trials sponsored by AstraZeneca.` | True | [] |
| faithful_05 | Q1 | `AstraZeneca sponsors 14 trials of osimertinib. This is evidence of sponsorship, not evidence that it develops the drug.` | False | development_claim: develops; negation: not |
| faithful_06 | Q1 | `The graph records trial sponsorship. AstraZeneca is a lead sponsor for osimertinib trials.` | True | [] |
| faithful_07 | Q2 | `NCT03909334 is a phase 2 trial evaluating Tagrisso. It is active, not recruiting.` | True | [] |
| faithful_08 | Q2 | `Tagrisso is being evaluated in NCT07680790, a recruiting phase 3 trial.` | True | [] |
| faithful_09 | Q2 | `NCT03909334 evaluates osimertinib and is phase 2; NCT07680790 evaluates osimertinib and is phase 3.` | True | [] |
| faithful_10 | Q2 | `Phase 3 trials evaluating osimertinib include NCT07680790 and NCT02411448.` | False | unrelated_entity: NCT02411448; unrelated_entity: NCT07680790; phase: phase 3 |
| faithful_11 | Q2 | `The trials include NCT03909334 (phase 2, active not recruiting) and NCT07680790 (phase 3, recruiting).` | False | number: 2,; number: 3,; status: active not recruiting; phase: phase 3; status: recruiting |
| faithful_12 | Q2 | `NCT03535363 is a completed phase 1 trial of osimertinib.` | True | [] |
| faithful_13 | Q3 | `Osimertinib is an inhibitor of EGFR.` | True | [] |
| faithful_14 | Q3 | `EGFR is inhibited by osimertinib.` | True | [] |
| faithful_15 | Q3 | `The mechanism recorded for osimertinib is inhibition of EGFR.` | False | wording: recorded |
| faithful_16 | Q3 | `Osimertinib targets EGFR and inhibits it.` | False | relation_direction: OSIMERTINIB inhibits OSIMERTINIB |
| faithful_17 | Q3 | `According to the evidence, osimertinib inhibits EGFR.` | True | [] |
| faithful_18 | Q3 | `The target of osimertinib is EGFR.` | True | [] |
| faithful_19 | Q4 | `Lorlatinib, crizotinib and alectinib inhibit ALK.` | True | [] |
| faithful_20 | Q4 | `The graph lists lorlatinib as an ALK inhibitor, with 13 NSCLC trials.` | True | [] |
| faithful_21 | Q4 | `PLB1003 inhibits ALK; its maximum stage is phase 1, with 0 NSCLC trials in this graph.` | True | [] |
| faithful_22 | Q4 | `ALK is inhibited by lorlatinib, crizotinib and alectinib.` | True | [] |
| faithful_23 | Q4 | `CONTELTINIB is an ALK inhibitor with a maximum stage of phase 1/2.` | True | [] |
| faithful_24 | Q4 | `ALK inhibitors include:<br>- lorlatinib<br>- crizotinib<br>- alectinib` | True | [] |
| faithful_25 | Q5 | `AstraZeneca sponsors 14 NSCLC trials evaluating osimertinib and 10 NSCLC trials evaluating carboplatin.` | False | number: 10 |
| faithful_26 | Q5 | `AstraZeneca is running NSCLC trials of osimertinib, carboplatin and gefitinib.` | True | [] |
| faithful_27 | Q5 | `According to the graph, AstraZeneca sponsors 7 trials of durvalumab in NSCLC.` | True | [] |
| faithful_28 | Q5 | `The graph records AstraZeneca as the sponsor of 14 trials of osimertinib and 10 trials of carboplatin.` | True | [] |
| faithful_29 | Q5 | `Osimertinib and carboplatin are being studied in NSCLC trials sponsored by AstraZeneca.` | True | [] |
| faithful_30 | Q5 | `AstraZeneca sponsors trials of the following drugs:<br>- osimertinib<br>- carboplatin<br>- gefitinib` | True | [] |
| faithful_31 | Q6 | `The graph does not contain the information needed to answer this question.` | False | no_subject: not contain information needed answer question |
| faithful_32 | Q6 | `This question is outside the scope of the graph.` | True | [] |
| faithful_33 | Q6 | `I cannot determine the capital of France from the retrieved evidence.` | False | entity: France; no_subject: i cannot determine capital france |
| faithful_34 | Q6 | `There is no supporting evidence for an answer in this graph.` | True | [] |
| faithful_35 | Q6 | `This graph contains information about drugs and trials, so it cannot answer the question.` | False | no_antecedent: it |
| faithful_36 | Q6 | `No relevant evidence was retrieved.` | False | no_subject: no relevant |

Reproduce from repository root with `python audit_evidence_claims/r3/docs3_probe.py` and `python audit_evidence_claims/r3/docs3_focused.py` after setting `PYTHONDONTWRITEBYTECODE=1` and `PYTHONUTF8=1`. These scripts only write their adjacent r3 JSON artifacts.
