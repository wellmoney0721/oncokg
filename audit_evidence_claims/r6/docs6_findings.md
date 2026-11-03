# R6 independent documentation and fresh faithful review

HEAD `80da81b`. No tracked edits. Probes call `Engine().check` and preserve full actual retrievals, not just the eight-row UI preview. Sources: [docs6_probe.py](docs6_probe.py), [docs6_probe_results.json](docs6_probe_results.json), [docs6_controls.py](docs6_controls.py), [docs6_controls_results.json](docs6_controls_results.json). Reproduce with `python -B audit_evidence_claims/r6/docs6_probe.py` and `python -B audit_evidence_claims/r6/docs6_controls.py` with `PYTHONIOENCODING=utf-8`. These scripts write only within r6 and disable bytecode. No tests or historical corpora duplicated; those belong to the replay reviewer.

## BLOCKERS

### D-B1. Record/list prose calls a drug a clinical trial and passes

Question: `What trials evaluate Tagrisso?`

Exact answer: `Osimertinib is listed as a clinical trial.`

Observed: `grounded=True`, `applicable=True`, `unsupported_claims=[]`. Also pass: `Osimertinib is recorded as a clinical trial.`, `The graph includes osimertinib as a clinical trial.`, `The graph lists osimertinib as a clinical trial.`, `The graph records osimertinib as a clinical trial.`, and `Osimertinib is listed as a trial.`

Evidence records named trials, e.g. `NCT07680790 (PHASE3, RECRUITING) evaluates OSIMERTINIB`; osimertinib links as Drug. None contains `clinical` or asserts drug/trial identity. This adds an unsupported ordinary kind word, outside README13's explicit one-statement word-rearrangement residue.

Controls: `Osimertinib is a clinical trial.` -> False, `wording: clinical`, `wording: trial`; `NCT07680790 is listed as a clinical trial.` -> True; `Osimertinib is listed as a drug in clinical trials.` -> True. Same unsupported listed sentence under Q3, which lacks any trial context, -> False. Adding `safe` under Q2 rejects safe only.

Cause: `src/claims.py:1091-1101` checks the trial identity only when the backward scan reaches a BE word. `as` is FUNCTION and stops the scan, so `is listed as a` does not count as a copula. All trial-kind words then skip owner checking. `:1134-1140` licenses them through `about_trials`, which Q2 legitimately supplies for the drug. Record verbs do not preserve identity ownership. This extends the R5 B6 identity fix, whose exact original form now rejects.

### D-B2. As-an-inhibitor roles are reversed across multiple evidence records

Question: `Which drugs act on ALK?`

Exact answer: `ALK is listed as an inhibitor of lorlatinib and crizotinib.`

Observed: `grounded=True`, `applicable=True`, `unsupported_claims=[]` (`docs6_controls_results.json`, `inverse_as_target`; independently confirmed in `root6_confirmation.json`, root B8 cases). The evidence has separate rows `LORLATINIB acts on ALK (inhibitor; max stage APPROVAL; 13 NSCLC trial(s) in this graph)` and `CRIZOTINIB acts on ALK (inhibitor; max stage APPROVAL; 15 NSCLC trial(s) in this graph)`. Neither records ALK inhibiting a drug, and no single evidence statement names ALK and both drugs.

Controls: `Lorlatinib and crizotinib are listed as inhibitors of ALK.` passes; root's paired bare inverse without `listed as` rejects with `relation_direction`. The explicit inverse clause is normal coordinated prose, not an artificial encoding.

Cause: `src/claims.py:680-685` takes every Drug in the clause as the acting subject and every Target as its object after `as an inhibitor`, independent of the written roles. The later edge loop validates the two real forward edges instead of the two asserted inverse edges. This is outside README13's literal one-statement residue: the clause's entities span two distinct evidence statements. The Q3 one-drug variant remains conservatively a NOTE (D-N1); its classification does not extend to this cross-record clause. Integrated report cross-reference: root B8.

## SHOULD FIX

### D-S1. Fresh faithful prose still has ordinary, evidence-supported parsing failures

These are hand-authored challenge cases, not an estimate of production LLM acceptance. All evidence content was rechecked; see [docs6_faithful_evidence_review.json](docs6_faithful_evidence_review.json). Trial stages/statuses are current retrieval values: NCT07680790 and NCT07738172 PHASE3/RECRUITING; NCT03909334 PHASE2/ACTIVE_NOT_RECRUITING; NCT02411448 PHASE3/ACTIVE_NOT_RECRUITING; NCT03535363 PHASE1/COMPLETED. PLB1003 and ASP-3026 both have max stage PHASE_1. Drug counts were checked against their exact rows.

|Question|Raw passed|Definitive faithful denominator|
|---|---:|---:|
|Q1 sponsors|5/8|5/8|
|Q2 trials|6/8|6/8|
|Q3 target|4/8|4/8|
|Q4 ALK drugs|3/8|3/7|
|Q5 AZ portfolio|4/8|4/7|
|Evidence answers|22/40 (55%)|22/38 (57.9%)|
|Q6 refusal, separate|5/6|5/6|

Q4 case7 (`ALK is inhibited by lorlatinib. Its maximum stage is approval.`) is retained only as an ambiguity diagnostic: the intended drug antecedent has APPROVAL, but `Its` could refer to ALK. Q5 case1 pairs three counts by position without `respectively`. Both are excluded from the definitive denominator; excluding only Q4 case7 would give22/39 (56.4%). A majority passes; this review does not claim most faithful answers fail. The stable, unambiguous failures below suffice to demonstrate usability gaps:

- Q1 `Osimertinib trial sponsors include AstraZeneca, Bristol Myers Squibb and Eli Lilly.` -> False, `relation_direction: OSIMERTINIB sponsors Astrazeneca/Bristol Myers Squibb/Eli Lilly`. All three sponsor rows exist.
- Q3 `EGFR inhibitors include the drug osimertinib.` -> False, `relation_incomplete: inhibitors`, `unrelated_entity: OSIMERTINIB`. The record says OSIMERTINIB acts on EGFR (inhibitor).
- Q3 `Inhibition of EGFR by Tagrisso is recorded in the graph.` -> False, `entity: Inhibition`. The new noun relation parser handles lower-case placement, but `src/query.py:543-551` mistakes the sentence-initial supported relation noun for an entity. Paired control `The recorded mechanism is inhibition of EGFR by osimertinib.` passes.
- Q4 `Lorlatinib, crizotinib and alectinib are approved ALK inhibitors.` -> False, `wording: approved`. Each retrieved drug row says APPROVAL. Splitting into `Lorlatinib, crizotinib and alectinib inhibit ALK. They are approved.` passes. A flat group sentence has no single row naming all drugs, so `src/claims.py:445-446,1143-1146` rejects wording even though the shared attribute holds per member.
- Q5 `AstraZeneca: 14 NSCLC trials of Tagrisso; 10 NSCLC trials of carboplatin.` -> False, `number: 10`. Both counts are the exact AZ pair counts; the second entry loses sponsor context after the semicolon.
- Q5 `AstraZeneca sponsors 6 NSCLC trials of cisplatin, 6 of pemetrexed and 6 of paclitaxel.` -> False, `unrelated_entity: PEMETREXED`, `unrelated_entity: PACLITAXEL`. Each pair has6; the new single elided-count repair does not generalize to a three-item comma list.

### D-S2. The high-level query docstring still promises more than the implementation

`src/query.py:12-18` says “The facts are identical either way, so the model can only change the prose” and “anything unsupported is reported rather than shipped.” These are unconditional output properties, not merely the prompt's intention. D-B1 shows generated text can pass with a new unsupported identity. Even the explicit README13 residue contradicts an unconditional statement that the model cannot change the facts. This is inherited wording, not a newly introduced overstatement.

The narrower `check_groundedness` docstring at `src/query.py:461-468` correctly qualifies the parser and points to the residue. `src/claims.py:10-11,52-55` similarly calls its bullets rules, not a guarantee. README.md:508-532 and README.ko.md:354-366 disclose pattern limitations; their residue list does not cover the new kind/record defect above. Web template/dashboard section06 (lines258-267), index section06 (lines268-277), and try box3 (`web/try.html:68-72`) carry a rule-shape caveat and explicit final human judgment; `web/try.html:145` says no findings is not proof of correctness. These caveats are useful and should remain.

However, `web/template.html:265`, `web/dashboard.html:265`, and `web/index.html:275` explicitly say every escape shape found in five adversarial rounds is blocked by regression tests. The historical R4 input `Osimertinib and EGFR are drugs.` is in `audit_evidence_claims/r4/docs_controls.py:20` (`kind_target_nonrelation`), and the R6 replay/root confirmation shows it now passes Q3 with `grounded=True`, `unsupported_claims=[]`. This is a previous exact input, not merely an unseen shape admitted by the caveat. The historical regression contradicts the blanket statement. The root replay owns its full reproduction and FIXED/NOT FIXED accounting.

The source's role description (`src/claims.py:13-19`) is also not what the new `as an inhibitor` branch actually does (`:680-685`): that branch assigns roles by entity type anywhere in the clause. The one-record reproduction is conservatively D-N1; its multi-record extension is D-B2 and falls outside the explicit residue.

## NOTES

### D-N1. As-an-inhibitor reversals pass; conservatively assigned to disclosed residue

Question Q3 `What does osimertinib target?`; answer `EGFR is listed as an inhibitor of osimertinib.` -> True, []. The bare `EGFR is an inhibitor of osimertinib.` rejects with `relation_direction: EGFR inhibitor OSIMERTINIB`. `The graph records EGFR as an inhibitor of osimertinib.` also passes; the corresponding correct-role sentence passes. `as an activator` rejects action type. The new branch at `src/claims.py:680-685` chooses Drug entities as subjects and Target entities as objects regardless of their written positions. The Q4 two-drug extension is separately D-B2, because it cannot be constructed from one evidence statement.

This is a natural, unsupported inverse relation and contradicts the described role-reading algorithm. Still, the Q3 claim's entities and action word occur in its one evidence statement; to avoid silently narrowing the accepted README13 residue, it is a NOTE rather than an independent verdict driver. The Q2 clinical-trial-kind blocker does not depend on this interpretation.

### D-N2. Other passing controls do not create blockers

Supported prefix/by/noun relations, valid NCT status lists, correct trial identity, correct `as an inhibitor` roles and approved/drug controls pass. `EGFR includes osimertinib.` and `EGFR records osimertinib.` pass, but they use grammar and same-record entities with vague/odd meaning; these remain residue notes rather than invented independent blockers. No artificial encodings were needed for D-B1.

## Exact fresh corpus and observed output

Q1 `Which companies are developing osimertinib?`; Q2 `What trials evaluate Tagrisso?`; Q3 `What does osimertinib target?`; Q4 `Which drugs act on ALK?`; Q5 `What is AstraZeneca running in NSCLC?`; Q6 `What is the capital of France?`. `\n` below denotes a newline. Each JSON result preserves full output, including evidence and reasons.

|ID|Exact answer|grounded|Findings (kind:value)|
|---|---|---|---|
|fresh_q1_1|`AstraZeneca sponsors trials evaluating osimertinib; the graph records 14 trials for this company and this drug.`|True|[]|
|fresh_q1_2|`Osimertinib trial sponsors include AstraZeneca, Bristol Myers Squibb and Eli Lilly.`|False|relation_direction: OSIMERTINIB sponsors Astrazeneca/Bristol Myers Squibb/Eli Lilly|
|fresh_q1_3|`AstraZeneca: 14 trials of Tagrisso. Bristol Myers Squibb: 2 trials of Tagrisso. Eli Lilly: 2 trials of Tagrisso.`|True|[]|
|fresh_q1_4|`AstraZeneca is a sponsor of osimertinib trials, as are Bristol Myers Squibb and Eli Lilly.`|False|unrelated_entity: Bristol Myers Squibb; unrelated_entity: Eli Lilly|
|fresh_q1_5|`Osimertinib is evaluated in trials sponsored by AstraZeneca and by Eli Lilly.`|True|[]|
|fresh_q1_6|`The graph includes AstraZeneca as a sponsor of 14 trials evaluating osimertinib.`|True|[]|
|fresh_q1_7|`Trials evaluating osimertinib are sponsored by Bristol Myers Squibb. It sponsors 2 trials of this drug.`|False|number: 2; relation: Bristol Myers Squibb — evaluates — OSIMERTINIB; relation_direction: OSIMERTINIB sponsors OSIMERTINIB|
|fresh_q1_8|`AstraZeneca leads trials evaluating osimertinib. Eli Lilly also sponsors trials of it.`|True|[]|
|fresh_q2_1|`Osimertinib trials include NCT07680790, which is recruiting in phase 3, and NCT03535363, which is completed in phase 1.`|True|[]|
|fresh_q2_2|`NCT07680790 evaluates osimertinib in phase 3 and is recruiting.`|True|[]|
|fresh_q2_3|`NCT03909334 evaluates Tagrisso; its phase is 2 and its status is active, not recruiting.`|False|number: 2; wording: status|
|fresh_q2_4|`The phase 3 trials NCT07680790 and NCT07738172 evaluate osimertinib and are recruiting.`|True|[]|
|fresh_q2_5|`NCT03909334 and NCT02411448 are active but not recruiting trials evaluating osimertinib.`|True|[]|
|fresh_q2_6|`The graph lists NCT03535363 as a completed phase 1 trial of osimertinib.`|True|[]|
|fresh_q2_7|`Osimertinib is tested by NCT03909334, a phase 2 trial, and by NCT07680790, a phase 3 trial.`|False|unrelated_entity: NCT07680790|
|fresh_q2_8|`Trials evaluating Tagrisso:\n- NCT07680790: phase 3; recruiting.\n- NCT03535363: phase 1; completed.`|True|[]|
|fresh_q3_1|`Inhibition of EGFR by Tagrisso is recorded in the graph.`|False|entity: Inhibition|
|fresh_q3_2|`The drug osimertinib is listed as an inhibitor of EGFR.`|True|[]|
|fresh_q3_3|`EGFR inhibitors include the drug osimertinib.`|False|unrelated_entity: OSIMERTINIB; relation_incomplete: inhibitors|
|fresh_q3_4|`The graph records EGFR as the target of Tagrisso.`|True|[]|
|fresh_q3_5|`Tagrisso acts on EGFR. Its mechanism is inhibition of this target.`|True|[]|
|fresh_q3_6|`Osimertinib acts on EGFR as an inhibitor; EGFR is its target.`|False|unrelated_entity: EGFR; relation_incomplete: target|
|fresh_q3_7|`Osimertinib inhibits EGFR, and this target is inhibited by the drug.`|True|[]|
|fresh_q3_8|`EGFR is the reported target. Osimertinib inhibits it.`|False|relation_incomplete: target|
|fresh_q4_1|`The graph lists lorlatinib and crizotinib as inhibitors of ALK.`|True|[]|
|fresh_q4_2|`ALK inhibitors include lorlatinib, crizotinib and brigatinib.`|False|unrelated_entity: BRIGATINIB; unrelated_entity: CRIZOTINIB; unrelated_entity: LORLATINIB; relation_incomplete: inhibitors|
|fresh_q4_3|`Lorlatinib is approved and has 13 NSCLC trials in this graph; crizotinib is approved and has 15.`|True|[]|
|fresh_q4_4|`PLB1003 and ASP-3026 inhibit ALK and have a maximum stage of phase 1.`|True|[]|
|fresh_q4_5|`Lorlatinib, crizotinib and alectinib are approved ALK inhibitors.`|False|wording: approved|
|fresh_q4_6|`For lorlatinib, the graph records 13 NSCLC trials. For crizotinib, it records 15 NSCLC trials.`|False|number: 15; count_ambiguous: CRIZOTINIB / LORLATINIB|
|fresh_q4_7|`ALK is inhibited by lorlatinib. Its maximum stage is approval.`|False|wording: approval|
|fresh_q4_8|`Lorlatinib targets ALK, as does crizotinib.`|False|unrelated_entity: CRIZOTINIB|
|fresh_q5_1|`AstraZeneca sponsors trials of osimertinib, carboplatin and gefitinib, with 14, 10 and 8 trials in this graph.`|False|number: 10; number: 14; count_ambiguous: OSIMERTINIB / CARBOPLATIN / GEFITINIB|
|fresh_q5_2|`AstraZeneca: 14 NSCLC trials of Tagrisso; 10 NSCLC trials of carboplatin.`|False|number: 10|
|fresh_q5_3|`AstraZeneca runs trials evaluating osimertinib and trials evaluating durvalumab in NSCLC.`|True|[]|
|fresh_q5_4|`The graph records AstraZeneca as a sponsor of 7 NSCLC trials of durvalumab and 8 NSCLC trials of gefitinib.`|True|[]|
|fresh_q5_5|`Osimertinib is evaluated in 14 NSCLC trials sponsored by AstraZeneca.`|True|[]|
|fresh_q5_6|`AstraZeneca sponsors 6 NSCLC trials of cisplatin, 6 of pemetrexed and 6 of paclitaxel.`|False|unrelated_entity: PACLITAXEL; unrelated_entity: PEMETREXED|
|fresh_q5_7|`AstraZeneca sponsors trials of durvalumab. It sponsors 7 such trials in this graph.`|False|relation_incomplete: sponsors|
|fresh_q5_8|`Trials of osimertinib and carboplatin are sponsored by AstraZeneca in NSCLC.`|True|[]|
|fresh_q6_1|`There are no records in this graph that answer this question.`|True|[]|
|fresh_q6_2|`The available evidence cannot answer the question.`|True|[]|
|fresh_q6_3|`This question is outside the scope of the graph.`|True|[]|
|fresh_q6_4|`I found no relevant information in the retrieved evidence.`|True|[]|
|fresh_q6_5|`The graph does not contain the information needed for an answer.`|True|[]|
|fresh_q6_6|`The capital of France is not covered by this graph.`|False|entity: France; no_subject: capital france not covered|

Recommendation from this workstream: CHANGES REQUIRED (D-B1 and D-B2).
