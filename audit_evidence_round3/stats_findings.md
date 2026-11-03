# Independent statistical and numerical audit

Evidence generation: `python audit_evidence_round3/stats_numbers_audit.py` (exit 0). The script imports neither `evaluate.py` nor its Wilson/bootstrap functions. It reads byte-preserved originals, computes Wilson with z=1.959963984540054, and draws 50,000 stratified bootstrap replicates with independent seed 93012026. Full arithmetic is in `stats_numbers_results.json`; the bilingual numerical claim matrix is `numbers_claim_inventory.json`.

## Findings

1. **The current-pipeline estimate and bootstrap cannot describe all current resolutions even under the repository's own labels.** `src/evaluate.py:79-84` selects only unchanged labelled rows, then `:125-134` weights those survivor rates by all current unique resolutions. All 12 incorrect accepted held-out rows are among the 16 accepted rows removed as stale: the remaining 99/99 is selection, not measured repair accuracy. Six independently distinct, still-current accepted triples in dev/postfix are already labelled incorrect: dev ids 10,30,93,139,142 and postfix id22. Therefore at most 2,159/2,165 = **99.7229%** of the current accepted distinct population can be correct under those same labels. Yet `evaluation_frozen_test.json.accepted_precision.estimate` is **99.9076%**, and the independent bootstrap interval **99.7691–100%** excludes even that maximum. The README correctly disclaims a new held-out measurement; that disclaimer does not turn extrapolated survivor statistics into population precision. Exact source: README.md:55-59 / README.ko.md:42-46; evaluate.py:79-93,125-134,155-165. This is not a criticism of using distinct-count weights by themselves.

2. **The dashboard's alias count includes removed contamination.** `web/template.html:303` describes `headline.aliases=9750` as “reference vocabulary after curation.” `src/make_dashboard_data.py:121` counts `dictionary.drugs[*].aliases`, whereas curation modifies `dictionary.index` (`src/normalize.py:231-269`). There are **670 stored alias→drug associations absent from the curated index**, including `tobramycin` under DEXAMETHASONE. The curated index has **7,693 normalized keys / 7,791 key→drug entries**; these are different units, not interchangeable corrected alias totals. The main precision headline is correct; this is a different tile.

3. **The historical re-score denominator is overstated.** README.md:436-439 says “round 2 re-scored 58 held-out rows and disagreed on three.” README.ko.md:306-307 says the same. The saved row-level artifact `audit_evidence_20261103/labels_rescore.json.summary.disagreement_ids` contains only ids **13,141**; its `postfix_additional_disagreement` is `gold_postfix.csv` id8. There are two disagreements among the 58 held-out rows plus one elsewhere. This agrees with the independently reproduced headline change 105/115→103/115.

4. **The corporate-map count is stale.** README.md:457 / README.ko.md:327 says 59 keys; AST evaluation of the current `src/normalize.py.CURATED_PARENTS` finds **57**. This is a count mismatch, independent of whether the individual ownership mappings are valid.

## What survived

* As-labelled raw counts: dev **126/137**, test **103/115**, postfix **36/38**. Independent test Wilson **82.6431–93.9295%**, matching rounded artifact values. Samples are disjoint on the sampling key `(raw,component,drug_id)`.
* Current surviving raw counts: **113/118**, **99/99**, **35/36**; current sample rows **183/147/54**, stale rows **31/25/4**. Their arithmetic is reproducible; interpretation is the issue above.
* Independent stratified estimates: **97.8912%,99.9076%,99.2671%**. Wilson endpoint propagation: **86.5566–99.4519%,89.4655–99.9740%,70.6116–99.8600%**. Independent bootstraps: **95.3747–99.9076%,99.7691–100%,97.9400–100%**. All agree with current README rounding. The brief's 71.5–99.8 postfix interval is obsolete; current documents say 70.6–99.9.
* Distinct-population weights match the sampling unit in `make_gold_sample.py:75-97`; they do not inherently inflate precision. Using occurrence weights instead yields still-higher **98.8242%,99.9595%,99.6655%**, but targets a different population and is not substituted as a preferred result.
* Four tiers are carried into test, but FUZZY_REVIEW has zero accepted-precision weight. CLEANED/SALT_STRIPPED/FUZZY_AUTO contribute **1+5+13=19/2165=0.8776%**; excluding them gives **100%**. The narrow dev-only strata therefore do not drive the large reported improvement.
* Wilson-bound propagation is not calibrated 95% coverage, as now disclosed. The bootstrap is materially narrower because 100%-correct tiers never produce an error in resampling. Neither repairs survivor selection. The postfix interval is a wide sensitivity range, not an independent validation of repaired performance.
* Current headline, coverage **4942/6355=77.7655%**, snapshot counts **3000/2742/2175**, dictionary defect counts, curation report counts, live graph counts **6474/17576**, all seven relation counts, **1313/3181=41.2763%** industry sponsorship, and source-record/tier null counts all match artifacts/SQL.

## New pharmaceutical disagreement sensitivity

The independent pharmaceutical reviewer identifies `gold_test.csv` id139 (`DN-101 (calcitriol) - Drug`) as another incorrect product collapse. It is still current, unlike the three additional dev/postfix disagreement rows. If adopted, test as-labelled raw becomes **102/115**, and current survivor raw becomes **98/99**. Original labelled statistics above remain separately preserved. See `pharma_rescore.json` for external pharmacology evidence and exact verdicts.

## Exact overclaim sentences to soften

* README.md:89-90: “The spread between them is the honest statement of what this sample size supports.” The intervals do not account for selecting only unchanged labels; the bootstrap excludes a label-implied upper bound.
* README.md:436-439: “Round 1 re-scored 62 rows and disagreed on five; round 2 re-scored 58 held-out rows and disagreed on three.” The second count mixes held-out and postfix samples.
* README.md:414-417: “One earlier item is gone because it no longer reproduces: `adenovirus` inside `dendritic cell-adenovirus CCL21 vaccine` used to resolve to an oncolytic product and now falls to the class guard on `vaccine`.” The current labelled postfix row with an `autologous` prefix still resolves its adenovirus component to TASADENOTUREV. The exact unprefixed probe may pass; the stated defect family remains.
