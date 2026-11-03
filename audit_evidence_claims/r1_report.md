## BLOCKERS

Verified commit `0c441e015117fd9384fa54419ca484fb748dc70b` against the real local graph. **Unsupported claims still return `grounded=True`.** No tracked files were changed.

[Full report with exact inputs, outputs and evidence](<C:/Users/geoum/Dropbox/GY's Formal Workspace/2026 Job recruting/바이오리서치에이아이/oncokg/audit_evidence_claims/independent_verification_report.txt>) · [Reproduction script](<C:/Users/geoum/Dropbox/GY's Formal Workspace/2026 Job recruting/바이오리서치에이아이/oncokg/audit_evidence_claims/independent_reproduce.ps1>)

Question identifiers below denote these exact inputs:

| ID | Question |
|---|---|
| Q1 | `Which companies are developing osimertinib?` |
| Q2 | `What trials evaluate Tagrisso?` |
| Q3 | `What does osimertinib target?` |
| Q4 | `Which drugs act on ALK?` |
| Q5 | `What is AstraZeneca running in NSCLC?` |
| Q6 | `What is the capital of France?` |

Unless stated otherwise, reproductions call `Engine().check(question, answer)`. **Every answer in this BLOCKERS section returned `grounded=True`, `unsupported_claims=[]`.**

1. **Relations are checked without sentence direction or required endpoints.**  
   `src/claims.py:170`, `src/claims.py:183`, `src/claims.py:225` assign roles by entity type, permit empty pair loops, and exempt relation words from further checking.

   | Question | Exact answer |
   |---|---|
   | Q3 | `EGFR acts on osimertinib.` |
   | Q3 | `EGFR is an osimertinib inhibitor.` |
   | Q2 | `osimertinib evaluates NCT03909334.` |
   | Q5 | `osimertinib sponsors AstraZeneca.` |
   | Q3 | `Osimertinib sponsors EGFR.` |

   The retrieved edges support the opposite direction in the first four examples; none supports the fifth relation.

2. **Pronouns can lose their subject when the next sentence names an object.**  
   `src/claims.py:129` replaces inherited entities whenever *any* entity is found. Missing relation endpoints then pass unchecked.

   - Q3: `osimertinib acts on EGFR. It inhibits ALK.`
   - Q3: `osimertinib acts on EGFR. This drug inhibits ALK.`
   - Q2: `NCT03909334 evaluates osimertinib. It evaluates osimertinib and is phase 3.`

   The ALK claim passes both on one line and with a newline before `It`. The trial is **PHASE2**; mentioning osimertinib in the second sentence replaces the trial antecedent and admits other osimertinib trials’ phases.

   Controls: `osimertinib inhibits ALK.` fails, and `NCT03909334 evaluates osimertinib. It is phase 3.` fails.

3. **Evidence scope pools different entities, allowing phases, statuses and counts to migrate.**  
   `src/claims.py:138` selects statements mentioning **any** sentence entity; `src/claims.py:208` and `src/claims.py:218` accept a matching value anywhere in that pool.

   | Question | Exact answer | Retrieved evidence |
   |---|---|---|
   | Q2 | `NCT03909334 is phase 3 and NCT07680790 is phase 2.` | Phases are respectively **2** and **3**. |
   | Q2 | `NCT03909334 and NCT07680790 are recruiting.` | First is **ACTIVE_NOT_RECRUITING**; second is RECRUITING. |
   | Q5 | `AstraZeneca sponsors 10 NSCLC trials evaluating osimertinib.` | Osimertinib count is **14**; **10** belongs to carboplatin. |
   | Q4 | `PLB1003 acts on ALK with 13 NSCLC trials.` | PLB1003 count is **0**; **13** belongs to lorlatinib. |
   | Q4 | `PLB1003 is approved for all lung cancer and acts on ALK.` | PLB1003 has **PHASE_1**; APPROVAL comes from other ALK drugs. |

4. **`quoted()` launders development and negation claims through matching bigrams.**  
   `src/claims.py:148`, `src/claims.py:155`, `src/claims.py:201`.

   Q1 answers:

   - `AstraZeneca is developing the drug osimertinib.`
   - `AstraZeneca has evidence of developing osimertinib.`
   - `This is not evidence that AstraZeneca sponsors osimertinib.`

   The evidence says **“a sponsorship, not evidence of developing the drug.”** Matching `developing the`, `of developing`, or `not evidence` exempts the changed claim without checking its meaning or negation scope.

5. **Hyphenated `non-` negation disappears.**  
   `non` is in `FUNCTION` at `src/claims.py:70`; tokenization at `src/claims.py:102` separates it from the following word.

   - Q3: `Osimertinib is a non-inhibitor of EGFR.`
   - Q2: `NCT07680790 is non-recruiting.`

   Evidence states EGFR inhibition and **RECRUITING**, respectively.

6. **Markdown brackets and non-English text can bypass claim checking entirely.**  
   `src/claims.py:87` removes arbitrary bracket contents; `src/claims.py:102` and `src/claims.py:111` only recognize ASCII words.

   All with Q3:

   - `Osimertinib [is safe and discontinued] acts on EGFR.`
   - `[osimertinib is safe](osimertinib) acts on EGFR.`
   - `오시머티닙은 안전하며 부작용이 없다.`
   - `osimertinib 은 EGFR 을 억제하지 않는다.`

   These are skipped claims, not merely difficult semantic paraphrases.

7. **Allowed words and relation synonyms still permit unsupported clinical claims.**

   - Q3: `Osimertinib is a treatment for all cancer.` passes because the clinical assertion consists of `FUNCTION` words (`src/claims.py:65`, `src/claims.py:225`). The evidence only states EGFR inhibition.
   - Question: `What does omaveloxolone target?`  
     Answer: `Omaveloxolone inhibits NFE2L2.`  
     Evidence: `OMAVELOXOLONE acts on NFE2L2 (activator)`.

   The second example exposes loss of action type: inhibition and other relation words map to generic `ACTS_ON` at `src/claims.py:35`; `src/claims.py:185` does not verify the stated action.

8. **Numeric regexes accept partial phases and miss ordinary count layouts.**

   | Question | Exact answer | Failure |
   |---|---|---|
   | Q4 | `PLB1003 is phase 13.` | Phase regex reads only **phase 1**; global number check finds 13 elsewhere. |
   | Q2 | `NCT07680790 is phase 3b.` | Regex validates **phase 3**; one-letter suffix is ignored. |
   | Q4 | `PLB1003 has 13 non small cell lung cancer trials.` | Count regex allows at most two intervening words. |
   | Q4 | `"- PLB1003: NSCLC trials: 13\n- lorlatinib: NSCLC trials: 0"` | Number-after-label layout bypasses count checking. |

   References: `src/claims.py:89`, `src/claims.py:206`, `src/claims.py:213`; global numeric handling at `src/query.py:496`. Actual PLB1003 and lorlatinib counts are **0** and **13**.

## SHOULD FIX

**Faithful paraphrases are rejected frequently.** Six hand-authored answers per demo question produced:

| Question | Faithful answers flagged |
|---|---:|
| Q1 | 2/6 |
| Q2 | 2/6 |
| Q3 | 1/6 |
| Q4 | 3/6 |
| Q5 | 2/6 |
| Q6: appropriate refusals | 6/6 |

That is **10/30 (33.3%)** for evidence-based answers, with refusals reported separately. This diagnostic corpus does **not** establish that most realistic answers fail, nor estimate a production LLM error rate.

Representative exact reproductions:

| Question | Answer | Observed output |
|---|---|---|
| Q1 | `AstraZeneca leads 14 trials investigating osimertinib.` | `grounded=False`; `wording: leads` |
| Q2 | `NCT03909334 is a phase 2 trial evaluating osimertinib and is active, not recruiting.` | False; `wording: active, recruiting` |
| Q2 | `NCT07680790 is a phase 3 trial evaluating Tagrisso.` | False; `drug_name: Tagrisso` |
| Q3 | `"Reported mechanism:\n- Osimertinib: inhibition of EGFR."` | False; `wording: inhibition` |
| Q4 | `CONTELTINIB acts on ALK with a maximum stage of phase 1/2.` | False; `number: 2`, `phase: phase 1/2` |
| Q4 | `"Agents acting on ALK:\n- LORLATINIB\n- CRIZOTINIB\n- ALECTINIB"` | False; `wording: alk` |
| Q6 | `This graph cannot answer that question.` | False; `negation: cannot`, `wording: answer, question` |

Causes include underscore-preserving status tokens (`src/claims.py:102`), missing lexical equivalents (`src/claims.py:227`), literal alias comparison (`src/query.py:529`), compound-phase normalization (`src/claims.py:208`), and colon-sensitive target linking (`src/query.py:120`, `src/query.py:171`). The Tagrisso rejection is inherited from the existing overlap check.

**Correct paired clauses are rejected by the Cartesian-product relation check.**  
Using the union of unmodified evidence retrieved for `What does osimertinib target?` and `What does crizotinib target?`:

- Answer: `osimertinib acts on EGFR and crizotinib acts on ALK.`
- Output: `grounded=False`, with invented obligations `CRIZOTINIB — acts on — EGFR` and `OSIMERTINIB — acts on — ALK`.
- Splitting the same clauses into two sentences returns `grounded=True`.

The same behavior was reproduced for correct trial–drug and company–drug pairs. Cause: `src/claims.py:183`.

**Dedup hides subsequent claim contexts.**  
Q3, answer `Osimertinib is safe. EGFR is safe.` produces two raw `safe` findings, but `src/query.py:545` retains only the first sentence’s finding. Final output remains `grounded=False`; dedup alone cannot turn a nonempty finding list into a pass.

**Documentation promises exceed the implementation.**

- `README.md:508`, `README.ko.md:354`: categorical relation/content-word guarantees omit the demonstrated bypasses.
- `src/claims.py:27`: “negation words are always reported” directly contradicts the quotation exception and observed results.
- `src/query.py:444`, `src/query.py:458`: verification guarantees are stronger than the actual checks.
- `web/template.html:263`, `web/try.html:69`: claims about catching unsupported relations and clinical statements need qualification.
- `web/try.html:140`: the success message says every sentence’s relations and wording match the evidence—even for the passing counterexamples above.

The existing “words, not meaning” caveat does not adequately describe discarded text, unchecked endpoints, or transferred values.

## NOTES

- **Regression suite:** `python -m pytest tests -q -p no:cacheprovider` → **79 passed in 5.96s**.
- **Templates:** all **5/5 evidence template bodies** pass when explicitly checked as generated prose, after removing `Scope:` exactly as `src/query.py:389` does. Full templates including Scope fail on metadata counts and `only`. The France refusal fails generated-prose checking; normal `ask()` accepts it through a separate refusal path.
- **Linker change:** compared **2,634 unique stored multiword aliases**, from **7,610 dictionary keys / 1,066 drugs**, against the previous behavior. **No intended links were lost.** `is a` changes from ISATUXIMAB to no match. `AZD 9291`, `osimertinib mesylate`, `trastuzumab deruxtecan`, and `pemetrexed disodium` retain their links.
- **Successful controls:** ordinary `safe`, `discontinued`, `not`, `isn't`, `isn’t`, `no longer`, and tested `un-` forms are flagged. `Osimertinib is an inhibitor of EGFR.` and `Osimertinib is being tested in NCT03909334.` pass. Explicit wrong named drug–target, trial–drug and company–drug pairs are rejected. `AstraZeneca's osimertinib.` is flagged as wording.
- **Execution-scope exception:** the first pytest run inherited system TEMP/TMP; test `TemporaryDirectory()` contexts created and automatically removed files outside the permitted scratch directory. I reran the exact command with TEMP/TMP confined to `audit_evidence_claims/`; all 79 tests passed. Bytecode and pytest cache writes were disabled. Final tracked-file diff is empty.

VERDICT: CHANGES REQUIRED