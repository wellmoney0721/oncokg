# Independent audit

Needs revision. Audited commit `e79049b`; no source or label edits. Detailed evidence is indexed in [evidence_index.json](evidence_index.json).

## BLOCKERS

- **The relation rename broke consumers.** `src/query.py:206,286` and `src/make_dashboard_data.py:57,82,86` still query `DEVELOPS`. Osimertinib/company queries return no evidence despite 54 live sponsorship edges; `web/data.json.top_companies=[]`.
- **Corporate identities remain wrong.** `normalize_company("Merck & Co., Inc.")` returns parent **Merck KGaA**, a [separate company](https://www.emdgroup.com/en/company/our-name-and-brands.html) (`src/normalize.py:926-933`). Actual SQLite also asserts `ORG:beonemedicines|PARENT_OF|ORG:beigene|hand-curated corporate map`: a [name change](https://ir.beonemedicines.com/news/beone-medicines-launches-following-redomiciliation-to-switzerland-marking-a-new-chapter-in-global-oncology/3bf1505f-9411-4a38-b445-54544ad4c88e) became ownership. GSK/GlaxoSmithKline has the same [rename-as-ownership error](https://www.gsk.com/media/ryjnw2s3/annual-report-2022.pdf). The full corporate audit also records Schering and Juno false mappings.
- **Removed evidence remains live.** Derivation precedes retirement (`src/graph.py:308,333`). Removing sole trial NCT00200395 leaves its derived sponsorship until another rebuild. Removed trial nodes persist; node updates never change `type` (`:121,335`).
- **Groundedness accepts inventions.** `xyzabumab cures cancer.` and spelled-out fabricated percentages pass (`src/query.py:437-451`). Evidence containing `47.5` accepts invented `47` but rejects exact `47.5`; `1,234` also fails. These are direct checker tests; no API key was available.
- **Correction verification falsely succeeds.** A pending correction makes `--check` print both "PENDING" and "all corrections are already in the labels", exit 0 (`src/apply_label_corrections.py:83-85,99-101`). Its guard checks ID/verdict, not surface/target (`:69-82`).

## LABEL DISAGREEMENTS

Independently reviewed **58 held-out rows**: 30 CONTAINED_ALIAS, 15 PARENTHETICAL, eight placebo and five difficult ALIAS. No FUZZY_AUTO/SALT_STRIPPED rows exist in this test sample.

Under the repository's declared **product-preserving** criterion, these author-`correct` labels are `incorrect`:

| Exact location | Surface -> assigned target | Evidence |
|---|---|---|
| `reports/gold_test.csv:14` | CC-486 -> AZACITIDINE | Oral product; [FDA prohibits IV/SC substitution](https://www.accessdata.fda.gov/drugsatfda_docs/label/2020/214120s000lbl.pdf). |
| `reports/gold_test.csv:142` | NanoPac -> PACLITAXEL | Distinct nanoparticle formulation: [trial protocol](https://cdn.clinicaltrials.gov/large-docs/85/NCT03029585/Prot_000.pdf). |
| `reports/gold_postfix.csv:9` | Nab-paclitaxel -> PACLITAXEL | Same error already corrected in test ID22; [NCI](https://www.cancer.gov/about-cancer/treatment/drugs/nanoparticlepaclitaxel). |

Test becomes **103/115=89.57%**, weighted **96.01%**. Postfix becomes **36/38=94.74%**, weighted **96.75%**. These are product-identity disagreements, not different-active-molecule claims.

The previous five verdict corrections survive that criterion. However, correction ID22's claimed trial purpose is wrong (`apply_label_corrections.py:38-41`): NCT07318883 compares HLX07/placebo, not the two paclitaxel formulations.

## DOMAIN ERRORS

- Curated lookup still maps **tobramycin -> DEXAMETHASONE** (`data/raw/drugs.json:40259`; curation `src/normalize.py:187-202`). These are [separate ingredients](https://www.accessdata.fda.gov/drugsatfda_docs/label/2026/050818s010lbl.pdf). `corticosteroid` -> HYDROCORTISONE also auto-accepts (`drugs.json:77781`).
- `Mvasi`, `Alymsys`, `Zirabev` collapse to bevacizumab. Adding `and cisplatin` makes otherwise-blocked **liposomal doxorubicin** acceptable because cleaning removes its qualifier (`normalize.py:467,509,525`). Conversely, [originator cemiplimab-rwlc](https://www.fda.gov/drugs/drug-approvals-and-databases/fda-approves-cemiplimab-rwlc-metastatic-or-locally-advanced-cutaneous-squamous-cell-carcinoma) and `amivantamab-vmjw` are falsely blocked (`textrules.py:138-139`).
- `prednisolone phosphate` loses a [covalent ester](https://www.accessdata.fda.gov/drugsatfda_docs/nda/pre96/019157_PEDIAPRED_ORIGINAL_AP.pdf) as though it were a salt (`textrules.py:41-49`); leucovorin/calcium nevertheless remain separate nodes. `pembrolizumab antibody` is blocked, while `mab inhibitor` escapes the class guard (`:97-117`).
- `No pembrolizumab` becomes an accepted exposure (`normalize.py:424-458`). Shared parentheses overwrite unknown combination components (`:561`); `DB-1303/BNT323`, two names for one agent, is split (`textrules.py:158-164`).

## STATISTICAL OBJECTIONS

Independent calculation confirms **105/115=91.3043%, Wilson 84.7303-95.2082%** before rescoring.

`population_unique` weighting matches distinct-resolution sampling (`make_gold_sample.py:79-97`); it does not estimate precision over trial occurrences or graph edges. More seriously, `evaluate.py:65-71` combines current tier populations with historical labels: **20/172 rows changed**, including 12 accepted rows and every originally incorrect accepted match.

Carried accepting tiers contribute **22/2,185=1.0069%**; FUZZY_REVIEW contributes zero. Excluding carried tiers yields **97.0766%**, versus 96.8772%.

Weighted marginal Wilson endpoints (`evaluate.py:116-120`) are not calibrated 95% intervals. A 200,000-resample stratified bootstrap gives **94.23-98.95%**, materially narrower than 85.66-98.97%; it cannot discover errors in empirically perfect tiers, so it is no replacement. Postfix **71.49-99.78%** reproduces but does not establish repair success.

## OVERCLAIMS

- "Every edge carries its **source**, the **source record**, the **fetch timestamp**, the **resolution tier** that produced it and a **confidence**." (`README.md:248-249`; Korean `:195`). **3,187** live edges have null source_record; **10,368** have null tier. Derived edges retain only sampled trial IDs, up to ten.
- "The facts are identical either way; only the prose changes." (`README.md:293-294`). Checker counterexamples disprove this guarantee.
- "Rebuilding from unchanged sources records zero changes." (`README.md:260-261`; Korean `:204`). False after the demonstrated source-removal build.
- **MISMATCH:** "four other molecules" (`README.md:210-212`; Korean `:160-162`) names three: MEDI4736 is durvalumab. "other 62 re-scored rows agreed" (`README.md:316`; Korean `:219`) conflicts with 62 total/five disagreements (`apply_label_corrections.py:8`).
- **UNVERIFIABLE:** "most recent 3,000" (`README.md:398-399`; Korean `:260`): ingestion specifies no sort (`ingest.py:185-190`). Full bilingual quotations/counterexamples are in `readme_overclaims.json`.

## WHAT SURVIVED

Original and fresh Git archive: **24 tests pass**, two offline builds each exit **0**, Python stderr empty. Git reports a global-ignore permission warning. Both second builds report **added/changed/retired=0/0/0**. No missing rebuild files or original-directory import dependency. Diffs were only build IDs and expected `added:17591->0`; tracked artifacts were restored afterward.

**VERIFIED against exact fields and independent SQL** (`statistics_results.json.number_audit`):

| Claim | Reproduced value |
|---|---|
| Dev/test/postfix raw; accepted denominators | 92.0/91.3/97.4%; 137/115/38 |
| Original weighted estimates | 97.7/96.9/99.1% |
| Coverage; distinct drugs/conditions; trials | 4,969/6,351=78.2%; 2,742/2,175; 3,000 |
| Review proposals; placebo sample | 37.5%; 8/8 |
| Curation ambiguity; exact | 2,193->69; 1,997->4,056 |
| Dictionary defect counts, README order | 134/124/80/78/47/7/6 |
| Nodes; live edges | 6,476; 17,591 |
| SPONSORS/EVALUATES/SPONSORS_TRIAL_OF/STUDIES/ACTS_ON/ASSOCIATED_WITH/PARENT_OF | 4,652/4,449/3,187/2,774/2,186/300/43 |
| Industry/non-industry | 1,313/3,187=41.2%; 58.8% |

Live template `applicable:false` survives, but `reports/query_examples.json[0].checks` still records the old `grounded:true` template check. France refusal, academic-name preservation and sorted dashboard output survive. Repairs **1/2/3/5/6/9/11/13** hold; **4/7/8/10/12/14** remain incomplete. All 59 corporate keys were inspected; continued legal existence of every subsidiary remains unverified.
