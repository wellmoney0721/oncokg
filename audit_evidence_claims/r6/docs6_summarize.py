"""Summarize independent R6 docs probes without changing the frozen corpus."""
import json
from pathlib import Path
HERE=Path(__file__).parent
rows=json.loads((HERE/'docs6_probe_results.json').read_text(encoding='utf8'))
notes={
'fresh_q1_1':'AZ OSIMERTINIB sponsorship row has 14 trials.',
'fresh_q1_2':'AZ, BMS, Eli Lilly each have SPONSORS_TRIAL_OF OSIMERTINIB rows.',
'fresh_q1_3':'AZ14, BMS2, Eli Lilly2 OSIMERTINIB rows; Tagrisso is linked alias.',
'fresh_q1_4':'AZ, BMS, Eli Lilly each sponsor OSIMERTINIB trials.',
'fresh_q1_5':'AZ and Eli Lilly each sponsor OSIMERTINIB trials.',
'fresh_q1_6':'AZ row has14 OSIMERTINIB trials.',
'fresh_q1_7':'BMS row has2 OSIMERTINIB trials. Sponsor role gives It its company antecedent.',
'fresh_q1_8':'AZ and Eli Lilly sponsor OSIMERTINIB trials; object it refers to drug.',
'fresh_q2_1':'NCT07680790 PHASE3 RECRUITING; NCT03535363 PHASE1 COMPLETED.',
'fresh_q2_2':'NCT07680790 PHASE3 RECRUITING evaluates OSIMERTINIB.',
'fresh_q2_3':'NCT03909334 PHASE2 ACTIVE_NOT_RECRUITING evaluates OSIMERTINIB.',
'fresh_q2_4':'NCT07680790 and NCT07738172 both PHASE3 RECRUITING.',
'fresh_q2_5':'NCT03909334 and NCT02411448 both ACTIVE_NOT_RECRUITING.',
'fresh_q2_6':'NCT03535363 PHASE1 COMPLETED evaluates OSIMERTINIB.',
'fresh_q2_7':'NCT03909334 PHASE2 and NCT07680790 PHASE3 both evaluate OSIMERTINIB.',
'fresh_q2_8':'NCT07680790 PHASE3 RECRUITING; NCT03535363 PHASE1 COMPLETED.',
'fresh_q3_1':'OSIMERTINIB acts on EGFR (inhibitor); Tagrisso alias.',
'fresh_q3_2':'OSIMERTINIB acts on EGFR (inhibitor).',
'fresh_q3_3':'OSIMERTINIB acts on EGFR (inhibitor).',
'fresh_q3_4':'OSIMERTINIB acts on EGFR (inhibitor); Tagrisso alias.',
'fresh_q3_5':'OSIMERTINIB acts on EGFR (inhibitor); this target points to EGFR.',
'fresh_q3_6':'OSIMERTINIB acts on EGFR (inhibitor); its target refers to drug target.',
'fresh_q3_7':'OSIMERTINIB acts on EGFR (inhibitor); typed pronouns refer to EGFR and OSIMERTINIB.',
'fresh_q3_8':'Question asks target of OSIMERTINIB, only evidence names EGFR; object it refers to EGFR.',
'fresh_q4_1':'LORLATINIB and CRIZOTINIB ACTS_ON ALK rows each inhibitor.',
'fresh_q4_2':'LORLATINIB CRIZOTINIB BRIGATINIB each inhibitor of ALK.',
'fresh_q4_3':'LORLATINIB APPROVAL13 and CRIZOTINIB APPROVAL15 NSCLC trials.',
'fresh_q4_4':'PLB1003 and ASP-3026 both PHASE_1 inhibitor of ALK; no approval/trial claim.',
'fresh_q4_5':'LORLATINIB CRIZOTINIB ALECTINIB each APPROVAL inhibitor of ALK.',
'fresh_q4_6':'LORLATINIB13 and CRIZOTINIB15 NSCLC trials; it refers to graph.',
'fresh_q4_7':'Ambiguous: intended lorlatinib stage APPROVAL, but Its could refer to main subject ALK. Excluded from definitive faithful denominator.',
'fresh_q4_8':'LORLATINIB and CRIZOTINIB each acts on ALK.',
'fresh_q5_1':'AZ trial counts OSIMERTINIB14 CARBOPLATIN10 GEFITINIB8. Positional mapping without respectively is a secondary ambiguity diagnostic.',
'fresh_q5_2':'AZ trial counts OSIMERTINIB14 CARBOPLATIN10; Tagrisso alias.',
'fresh_q5_3':'AZ sponsors OSIMERTINIB and DURVALUMAB NSCLC trials.',
'fresh_q5_4':'AZ DURVALUMAB7 GEFITINIB8 NSCLC trials.',
'fresh_q5_5':'AZ OSIMERTINIB14 NSCLC trials.',
'fresh_q5_6':'AZ CISPLATIN6 PEMETREXED6 PACLITAXEL6 NSCLC trials.',
'fresh_q5_7':'AZ DURVALUMAB7 NSCLC trials; sponsor role makes It the company.',
'fresh_q5_8':'AZ OSIMERTINIB and CARBOPLATIN NSCLC trial rows.',
}
for r in rows:
 if r['category']=='faithful':
  r['evidence_validation']=notes.get(r['id'],'No evidence is retrieved; this is a refusal, not a world fact.')
  r['ambiguity_diagnostic']=r['id'] in ('fresh_q4_7','fresh_q5_1')
(HERE/'docs6_faithful_evidence_review.json').write_text(json.dumps([r for r in rows if r['category']=='faithful'],indent=2,ensure_ascii=False),encoding='utf8')
intro='''# R6 independent documentation and fresh faithful review

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

Q1 `Which companies are developing osimertinib?`; Q2 `What trials evaluate Tagrisso?`; Q3 `What does osimertinib target?`; Q4 `Which drugs act on ALK?`; Q5 `What is AstraZeneca running in NSCLC?`; Q6 `What is the capital of France?`. `\\n` below denotes a newline. Each JSON result preserves full output, including evidence and reasons.

|ID|Exact answer|grounded|Findings (kind:value)|
|---|---|---|---|
'''
lines=[intro]
for r in rows:
 if r['category']!='faithful':continue
 c=r['result']['checks'];a=r['answer'].replace('\n','\\n').replace('|','\\|');f='; '.join(x['kind']+': '+str(x['value']) for x in c['unsupported_claims']).replace('|','\\|') or '[]'
 lines.append(f"|{r['id']}|`{a}`|{c['grounded']}|{f}|\n")
lines.append('\nRecommendation from this workstream: CHANGES REQUIRED (D-B1 and D-B2).\n')
(HERE/'docs6_findings.md').write_text(''.join(lines),encoding='utf8')
print('Wrote evidence-reviewed corpus and docs6_findings.md')
