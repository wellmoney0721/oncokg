# Independent audit — round 3

Audited HEAD `fa7983a25fee83e54f618ce113b68fb85dade54e`. No repairs made. All tracked files were restored byte-for-byte. Detailed numerical checks, 47 row-level re-scores, corporate verification and counterexamples accompany this report in `audit_evidence_round3/`.

## BLOCKERS

1. **The supposedly repaired vaccine error remains in the live graph.** `src/textrules.py:104` limits class qualifiers to 40 characters; `src/normalize.py:761` then segments longer text. Consequently, `autologous dendritic cell-adenovirus CCL21 vaccine` becomes TASADENOTUREV. The live edge is `NCT00601094|EVALUATES|CHEMBL3990045|NCT00601094`, confidence 0.88; its derived Jonsson sponsorship has confidence 1.0. Tasadenoturev is [Ad5-DNX-2401](https://www.cancer.gov/publications/dictionaries/cancer-drug/def/tasadenoturev), not that dendritic-cell vaccine. `graph_ccl21_edges.json` records both edges.

2. **Querying bypasses ingestion safeguards.** `src/query.py:129-137` uses dictionary hits without the resolver's product guards. `Mvasi`, `Zirabev` and `bevacizumab-awwb` are blocked during ingestion but querying their trials returns 12 BEVACIZUMAB trials; liposomal doxorubicin returns three conventional-DOXORUBICIN trials. These are false product equivalences, not merely incomplete retrieval (`query_resolution_bypass.json`).

3. **False ownership survives the rename repair.** `src/normalize.py:985,1011,1129` produces live GSK→GlaxoSmithKline ownership despite a [legal name change](https://find-and-update.company-information.service.gov.uk/company/03888792/filing-history?page=12). Line 947 similarly makes Schering-Plough a Merck subsidiary, although the [SEC merger record](https://www.sec.gov/Archives/edgar/data/310158/000119312512084319/R10.htm) identifies it as the surviving company renamed Merck. The 57-key corporate review distinguishes completed acquisitions from unverified continuing legal existence.

4. **Some published counts are misleading or wrong.** `web/template.html:303` calls `web/data.json.headline.aliases=9750` a vocabulary “after curation,” but `src/make_dashboard_data.py:121` includes 670 removed alias associations. `README.md:457` / `README.ko.md:327` claim 59 corporate keys; code has 57. `README.md:436-439` / `README.ko.md:306-307` combine two held-out disagreements with one postfix disagreement and call all three held-out.

## LABEL DISAGREEMENTS

Independently re-scored **47 deliberately difficult held-out rows**. All four rows below are labelled `correct`; my verdict is `incorrect` under the repository's product-identity criterion.

| Exact row | Surface → labelled target | Evidence |
|---|---|---|
| `gold_test.csv:140`, id139 | DN-101 (calcitriol) - Drug → CALCITRIOL | [Original PK study](https://pubmed.ncbi.nlm.nih.gov/16278401/) establishes a distinct investigational formulation. This is formulation loss, not a different active molecule or separate approval. |
| `gold_dev.csv:181`, id180 | Paclitaxel loaded polymeric micelle (Genexol-PM®) → PACLITAXEL | `data/raw/trials.json.data[901].protocolSection.armsInterventionsModule` separates Genexol-PM and conventional Genexol arms. |
| `gold_dev.csv:182`, id181 | Pegylated liposomal doxorubicin (PLD) → DOXORUBICIN | Source NCT04244552 identifies Doxil; its [FDA label](https://www.accessdata.fda.gov/drugsatfda_docs/label/2016/050718s051lbl.pdf) prohibits substitution. |
| `gold_postfix.csv:2`, id1 | ABI-007 (Abraxane) and Carboplatin, component ABI-007 → PACLITAXEL | Same product already corrected in postfix id8; [FDA identifies ABI-007](https://www.accessdata.fda.gov/drugsatfda_docs/nda/2005/21660_ABRAXANE_biopharmr.PDF). |

Applying these judgments changes test to **102/115=88.7%**, Wilson **81.6–93.3%**; dev to **124/137=90.5%**; postfix to **35/38=92.1%**. This purposive re-score does not estimate a population disagreement rate.

The original five corrections, plus the later three, remain defensible. However, `src/apply_label_corrections.py:105` checks raw string and drug ID but omits component: substituting legitimate `Paclitaxel` for id22's `Nab-Paclitaxel` still passes and flips it incorrectly. Its obsolete trial-comparison rationale also remains in `gold_test.csv:23.reviewer_note`; lines 109–111 skip already-corrected rows.

## DOMAIN ERRORS

- `pembrolizumab-free regimen` becomes PEMBROLIZUMAB: `src/textrules.py:211-216` treats `free` as an FDA suffix. `[89Zr]pembrolizumab` also becomes unlabeled PEMBROLIZUMAB because cleaning removes the isotope before `src/normalize.py:684` checks it.
- `filgrastim-sndz`, `pegfilgrastim-jmdb` and Pazenir still collapse to reference molecules (`src/textrules.py:151,158`; `pharma_product_probes.json`). [FDA](https://purplebooksearch.fda.gov/index.cfm?blaNo=125553&event=productdetails) identifies the first as biosimilar; [MHRA](https://www.gov.uk/drug-safety-update/paclitaxel-formulations-conventional-and-nab-paclitaxel-caution-required-due-to-potential-for-medication-error) distinguishes Pazenir. Conversely, uppercase `Cemiplimab-RWLC` and ordinary `injection of pembrolizumab` are blocked.
- The ester guard at `src/normalize.py:752` runs after alias lookup: dexamethasone sodium phosphate and etoposide phosphate still collapse. `ICE` remains IFOSFAMIDE although [NCI defines a multidrug regimen](https://www.cancer.gov/publications/dictionaries/cancer-drug/def/ice-regimen). Disabling only registry filtering changes accepted occurrences **4,942→4,950**: ten lost, two gained, net eight; four lost genuine limertinib exposures are already disclosed.
- The groundedness checker accepts unsupported `aspirin`, `1e6 patients` and `⅔ of patients` (`src/query.py:503,511`). These are direct checker tests; no API key was available.

## STATISTICAL OBJECTIONS

Distinct-resolution weighting matches the sampling unit; it is not inherently inflationary. **Survivor selection is the defect:** `src/evaluate.py:79-84,125-134` excludes 16 accepted test rows containing all 12 errors, then extrapolates the remaining rates to the full current population. The README acknowledges loss of held-out validity, but its “current pipeline” columns still overgeneralize.

Independent 50,000-resample bootstrap: test **99.7691–100%**, versus propagated Wilson bounds **89.4655–99.9740%**. Six already-labelled current errors elsewhere imply a finite-population maximum **2159/2165=99.7229%**; that bootstrap interval excludes even this maximum. Weighted Wilson endpoints are not calibrated 95% coverage; bootstrap cannot discover errors in perfect sampled tiers.

Carried accepted tiers contribute **19/2165=0.8776%** of weight; excluding them yields **100%**. FUZZY_REVIEW contributes zero accepted weight. The actual postfix bound is **70.6–99.9**, not the brief's older 71.5–99.8; it does not validate repairs.

## OVERCLAIMS

Exact bilingual quotations and counterexamples are in `overclaims_inventory.json`. Examples requiring correction:

- “The check catches invented names and invented figures” — `README.md:405`.
- “사전 기반 최장일치 분절로 모든 성분을 추출하고, 잔여물은 명시적 미해결로 방출합니다.” — `README.ko.md:209`; short residues disappear.
- “수정을 확인할 뿐 재측정은 아닙니다.” — `README.ko.md:313`; the interval confirms no repair.

## WHAT SURVIVED

Original and fresh-archive tests each pass **44/44**, including before rebuilding the archive. Four offline builds and standalone curation exit **0**, with empty stderr. Both second builds report **0 added / 0 changed / 0 retired**. Artifact differences are timestamps only; fresh imports resolve within the extracted repository, with no missing required file.

The as-labelled **103/115**, Wilson **82.6431–93.9295%**, coverage **4942/6355**, curation **2189→65 / 1997→4054**, graph **6474/17576**, relation counts and precision headline reproduce. Retirement/re-add works; all 3,181 derived edges contain complete trial lists. Template checks correctly return `applicable:false`. These strengths do not remove the domain defects above.

The bilingual numerical inventory contains **65 grouped claims: 58 VERIFIED, 3 MISMATCH, 4 UNVERIFIABLE**. The four gaps concern historical measurements without retained pre-round-1 evidence; they are identified individually in `numbers_claim_inventory.json` and `stats_historical_evidence.json`.
