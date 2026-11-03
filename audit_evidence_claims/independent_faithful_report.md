# Independent faithful-answer and regression audit

Commit: `0c441e015117fd9384fa54419ca484fb748dc70b`.

Reproduce with `$env:PYTHONDONTWRITEBYTECODE='1'; python audit_evidence_claims/independent_faithful_probe.py`.

Required regression command: `python -m pytest tests -q -p no:cacheprovider` -> **79 passed in 5.96s** with TEMP/TMP set to `audit_evidence_claims/independent_faithful_temp`. Exact log: `independent_faithful_pytest_scoped.txt`. The first run also passed (79 in 5.68s), but inherited Windows TEMP/TMP. Six test sites use `tempfile.TemporaryDirectory()`; those contexts created then automatically removed temporary directories outside the permitted scratch folder, and their exact generated names were not logged. This was an execution-scope mistake; no manual outside cleanup was attempted. The scoped rerun retained the exact required pytest command and redirected all Python tempfile writes into the allowed directory. Bytecode writes and pytest cache were disabled for both runs.

## Corpus and scope

Six hand-authored, plausible phrasings for each demo question in src/query.py:579-584. This is a diagnostic corpus, not a population error-rate estimate. The sixth question has no evidence and its faithful refusal variants are reported separately. One draft added the word protein beyond the literal evidence; that draft was excluded and replaced with a direct inhibition paraphrase before freezing this corpus. No corpus answer was tuned after the freeze.

| Demo question | Flagged / total |
|---|---|
| Which companies are developing osimertinib? | 2 / 6 |
| What trials evaluate Tagrisso? | 2 / 6 |
| What does osimertinib target? | 1 / 6 |
| Which drugs act on ALK? | 3 / 6 |
| What is AstraZeneca running in NSCLC? | 2 / 6 |
| What is the capital of France? | 6 / 6 |

**Evidence paraphrases: 10/30 flagged (33.3%); refusals: 6/6 flagged separately.** Basic inhibitor-of, inhibited-by, and being-tested-in phrasings pass, as do 3/4 multi-entry list examples; the ALK-colon heading is rejected.

## Exact inputs and observed outputs

Each call is `Engine().check(question, answer)`. A listed `true` has `unsupported_claims=[]`. For false results, pairs show `(kind,value)`; full dictionaries and evidence are in `independent_faithful_results.json`.

| Case | Exact answer (JSON string) | grounded | Findings |
|---|---|---|---|
| Q1P1 | `"AstraZeneca is a sponsor of trials evaluating osimertinib."` | true | `[]` |
| Q1P2 | `"Osimertinib is being tested in trials sponsored by AstraZeneca."` | true | `[]` |
| Q1P3 | `"AstraZeneca leads 14 trials investigating osimertinib."` | false | `[["wording", "leads"]]` |
| Q1P4 | `"For osimertinib, the graph lists AstraZeneca as a trial sponsor."` | false | `[["wording", "lists"]]` |
| Q1P5 | `"Sponsors of osimertinib trials:\n- AstraZeneca\n- Eli Lilly"` | true | `[]` |
| Q1P6 | `"AstraZeneca sponsors 14 trials evaluating osimertinib, and Eli Lilly sponsors 2 trials evaluating osimertinib."` | true | `[]` |
| Q2P1 | `"NCT03909334 evaluates osimertinib."` | true | `[]` |
| Q2P2 | `"Osimertinib is being tested in NCT03909334."` | true | `[]` |
| Q2P3 | `"NCT03909334 is a phase 2 trial evaluating osimertinib and is active, not recruiting."` | false | `[["wording", "active"], ["wording", "recruiting"]]` |
| Q2P4 | `"NCT07680790 is a phase 3 trial evaluating Tagrisso."` | false | `[["drug_name", "Tagrisso"]]` |
| Q2P5 | `"Trials evaluating osimertinib include:\n- NCT03909334\n- NCT07680790"` | true | `[]` |
| Q2P6 | `"NCT03535363 was a phase 1 trial of osimertinib and has completed."` | true | `[]` |
| Q3P1 | `"Osimertinib acts on EGFR."` | true | `[]` |
| Q3P2 | `"Osimertinib is an inhibitor of EGFR."` | true | `[]` |
| Q3P3 | `"EGFR is inhibited by osimertinib."` | true | `[]` |
| Q3P4 | `"The target of osimertinib is EGFR."` | true | `[]` |
| Q3P5 | `"Osimertinib inhibits EGFR, according to the retrieved evidence."` | true | `[]` |
| Q3P6 | `"Reported mechanism:\n- Osimertinib: inhibition of EGFR."` | false | `[["wording", "inhibition"]]` |
| Q4P1 | `"Lorlatinib and crizotinib act on ALK."` | true | `[]` |
| Q4P2 | `"ALK is targeted by alectinib, brigatinib and ceritinib."` | true | `[]` |
| Q4P3 | `"Agents acting on ALK:\n- LORLATINIB\n- CRIZOTINIB\n- ALECTINIB"` | false | `[["wording", "alk"]]` |
| Q4P4 | `"Crizotinib acts on ALK and has 15 NSCLC trials in this graph."` | true | `[]` |
| Q4P5 | `"CONTELTINIB acts on ALK with a maximum stage of phase 1/2."` | false | `[["number", "2"], ["phase", "phase 1/2"]]` |
| Q4P6 | `"The graph lists lorlatinib, crizotinib and alectinib as drugs that act on ALK."` | false | `[["wording", "lists"]]` |
| Q5P1 | `"AstraZeneca sponsors NSCLC trials evaluating osimertinib and carboplatin."` | true | `[]` |
| Q5P2 | `"Osimertinib is being tested in NSCLC trials sponsored by AstraZeneca."` | true | `[]` |
| Q5P3 | `"AstraZeneca is the sponsor of 14 NSCLC trials of osimertinib and 10 NSCLC trials of carboplatin."` | true | `[]` |
| Q5P4 | `"AstraZeneca supports trials studying osimertinib in NSCLC."` | false | `[["wording", "supports"]]` |
| Q5P5 | `"AstraZeneca sponsors trials of these NSCLC drugs:\n- OSIMERTINIB\n- CARBOPLATIN\n- GEFITINIB"` | true | `[]` |
| Q5P6 | `"The graph lists AstraZeneca as a sponsor of NSCLC trials evaluating durvalumab."` | false | `[["wording", "lists"]]` |
| Q6P1 | `"This graph cannot answer that question."` | false | `[["wording", "answer"], ["negation", "cannot"], ["wording", "question"]]` |
| Q6P2 | `"No evidence was retrieved for that question."` | false | `[["negation", "no"], ["wording", "question"]]` |
| Q6P3 | `"The graph covers NSCLC drugs and trials, so it cannot answer this question."` | false | `[["wording", "answer"], ["negation", "cannot"], ["wording", "covers"], ["wording", "question"], ["wording", "so"]]` |
| Q6P4 | `"There is no supporting evidence in this graph."` | false | `[["entity", "There"], ["negation", "no"], ["wording", "supporting"]]` |
| Q6P5 | `"The question is outside the scope of this graph."` | false | `[["wording", "outside"], ["wording", "question"]]` |
| Q6P6 | `"I cannot determine the capital of France from the retrieved evidence."` | false | `[["entity", "France"], ["negation", "cannot"], ["wording", "capital"], ["wording", "determine"], ["wording", "france"]]` |

## False-positive explanations

- **Status normalization** (`src/claims.py:102`, `:139-143`, `:227`): Q2P3 is supported by `NCT03909334 (PHASE2, ACTIVE_NOT_RECRUITING) evaluates OSIMERTINIB`. Evidence tokens retain `active_not_recruiting` as one token, whereas prose yields `active` and `recruiting`; both are rejected. The normalized bigram correctly exempts `not`, making this specifically a wording mismatch.
- **Known drug alias rejected** (`src/query.py:477-482`, `:529-533`): Q2P4 uses Tagrisso, the alias that already resolved the question to OSIMERTINIB. The global name-overlap check tests literal Tagrisso against the evidence rather than its linked identity; finding `(drug_name, Tagrisso)`.
- **Combined phase rejected** (`src/claims.py:93-94`, `:206-210`; `src/query.py:495-501`): Q4P5 paraphrases graph `CONTELTINIB ... max stage PHASE_1_2` as `phase 1/2`. Normalization gives phase12, so the code cannot find phase2; number handling separately rejects 2.
- **Punctuation at list heading** (`src/query.py:119`, `:169-174`; `src/claims.py:137-141`): Q4P3 token `ALK:` is not stripped to ALK; no heading entity is linked, leaving no scoped evidence, and wording `alk` is flagged.
- **Natural lexical equivalents** (`src/claims.py:31-43`, `:65-84`, `:223-230`): `leads` from lead sponsor, `lists` from graph records, `inhibition` from inhibitor, and `supports` from sponsorship are reported because missing from exact relation/function/stem vocabularies.
- **Faithful refusals** (`src/query.py:365-376`; `src/claims.py:190-203`, `:223-230`): all six refusal variants are rejected by Engine.check. Normal ask short-circuits refusal with grounded=True; generated text does not share that path.

## Template regression

Template body = `engine.ask(q)["answer"].split("\nScope:")[0]`, matching the application exclusion at src/query.py:387-392. Forced through Engine.check (generated=True), all five evidence templates pass. Normal ask returns grounded=null/applicable=false for these, as intended. The sixth no-evidence refusal passes normal ask only via the special case and fails forced prose checking.

| Question | Body grounded | Entire template grounded | Entire template findings |
|---|---|---|---|
| Which companies are developing osimertinib? | true | false | `[["number", "12"], ["comparison", "only"]]` |
| What trials evaluate Tagrisso? | true | false | `[["number", "12"], ["comparison", "only"]]` |
| What does osimertinib target? | true | false | `[["number", "1"], ["comparison", "only"]]` |
| Which drugs act on ALK? | true | false | `[["number", "11"], ["comparison", "only"]]` |
| What is AstraZeneca running in NSCLC? | true | false | `[["number", "12"], ["comparison", "only"]]` |
| What is the capital of France? | false | false | `[["wording", "about"], ["wording", "answer"], ["wording", "answers"], ["negation", "cannot"], ["wording", "covers"], ["wording", "entity"], ["wording", "matched"], ["negation", "no"], ["comparison", "only"], ["wording", "question"], ["wording", "questions"], ["wording", "relate"]]` |

The full-template failures involving Scope metadata do not contradict the five body-pass regression, since the application deliberately excludes that metadata. Exact body and full inputs are in the JSON.
