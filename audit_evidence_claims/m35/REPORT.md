# Independent relation-map review — round 35

Reviewed **HEAD `56eb3d6297f2878d008e5edd9eb5eade62a0841c`**, parent `1f6017e8ae7923d21cfafca64b1285331e0d2c18`, on 2026-11-04. **CHANGES REQUIRED: one code blocker.** The exact M34-B1, S1 and S2 reproductions are fixed, but the optical-sign repair runs before removal of invisible characters. An invisible character inside `(-)` makes its minus disappear, admitting a negative optical isomer as an unqualified preferred-name node. A separate question-linker regression is nonblocking under the given scope. No new upstream data defect was established.

Scope: section 0 of `web/try.html`, `POST /api/explore`, and `Engine.explore`, using the [round-32 approval bar](../m32/brief.md), [round-34 brief](../m34/brief.md), [round-34 report](../m34/REPORT.md), and current repair notes. FIXED below closes an exact original reproduction under the present policy; it does not certify every related spelling, restore excluded brand recall, or imply upstream data curation. No tracked file was edited.

## Verification

- **`python -m pytest tests -q -p no:cacheprovider`: 363 passed in 79.57 seconds**, exit 0; wrapper elapsed 81.331 seconds. Bytecode was disabled and test/process temporary files redirected under m35. [Test output](pytest.txt), [command/timing](pytest_meta.json).
- Started the actual CLI with **`python src/app.py 8935`**. Root captured **254 HTTP requests**: 124 baseline, 36 supplement, 85 exact/adversarial, and nine independent optical confirmations. The two expected baseline errors are empty input and 501 characters, both HTTP 400. The served page equals `web/try.html` byte for byte. Other lanes retain additional requests. [Baseline summary](root_confirmation.json), [baseline bodies](root_http.json), [supplement](root_supplement_http.json), [exact cases](root_exact_http.json), [optical confirmation](root_optical_confirmation.json).
- **4,673 distinct historical/current inputs**: 295 centers, 1,434 refusals, 2,554 `alias_only`, 324 `not_one_name`, 62 `not_found`, four `choose`; no errors, independent admitted-name membership failures, silent ambiguous draws, or wrong choice sets in that corpus. Its comparison with all 4,660 prior inputs changes only `CABOZANTINIB S-MALATE` (center → refused), `5 FU` and `pegintron` (`alias_only` → refused). [Corpus](replay/corpus_summary.json), [all replies](replay/corpus_results.json), [parent differences](replay/parent_corpus_changes.json).
- **22,956 distinct source/key inputs from 34,429 records**, including every one of **9,581 raw drug-alias records**, completed with zero structural membership/refusal/ambiguity failures and zero exceptions. Source membership under the implementation's `_sig` is checked separately from whether that implementation respects the promised sign/invisible-character semantics; the former cannot disprove M35-B1. [Source summary](attacks/source_summary.json), [all replies](attacks/source_sweep.json).

## Code blocker

### M35-B1 — an ignored invisible character defeats optical-sign preservation

**Location:** `src/app.py:278-282`, `_sig`. The new regular expressions recognize optical descriptors before the final character filter removes invisible characters and combining marks. An inserted U+200B is not matched by `\s*`; consequently the ASCII minus remains punctuation and is deleted by that final filter. There is no later descriptor pass.

The following are fresh HTTP results. In escaped spellings, `\u200b`, `\ufeff`, `\u2060`, and `\u0301` denote **actual single Unicode characters**, not six literal backslash characters. Complete inputs, responses, source records, and code-point captures are linked below.

| Exact input / reproducible Python spelling | `_sig` | Map result |
|---|---|---|
| `ARTEMISININ` | `artemisinin` | center **CHEMBL269671** |
| `(-)-ARTEMISININ` | `−artemisinin` (U+2212) | `not_one_name` |
| `"(-\u200b)-ARTEMISININ"` | `artemisinin` | **center CHEMBL269671** |
| `"(-\ufeff)-ARTEMISININ"` | `artemisinin` | **same center** |
| `"(-\u2060)-ARTEMISININ"` | `artemisinin` | **same center** |
| `"(-\u0301)-ARTEMISININ"` | `artemisinin` | **same center** |
| `"(\u2212\u200b)-ARTEMISININ"` | `−artemisinin` | `not_one_name` |
| `(+)-ARTEMISININ` | `+artemisinin` | `alias_only` |
| `CHEMBL269671` | ID path | center CHEMBL269671, permitted ID control |

[Independent root HTTP/source confirmation](root_optical_confirmation.json), [separate HTTP/code-point reproduction](attacks/rotation_http.json), [70-case descriptor mutation matrix](attacks/rotation_mutations.json), [source pointers and summary](attacks/rotation_source_and_summary.json). The matrix has **56 sign-normalization invariance failures and 14 wrong-sign ARTEMISININ draws**; these are variants of one defect, not 14 independent blockers.

**Identity evidence:** `data/processed/resolved.json:1`, `dictionary.drugs.CHEMBL269671`, has preferred name `ARTEMISININ`, with `aliases[1].alias == "(+)-artemisinin"`; raw provenance is `data/raw/drugs.json:1`, `data[768].drug`, including its first ChEMBL synonym. The live node has the same preferred label. ChEBI identifies artemisinin as the positive optical form. A primary synthesis study explicitly distinguishes synthetic negative artemisinin from its natural positive antipode. [ChEBI](https://www.ebi.ac.uk/chebi/CHEBI:223316), [Krieger et al., 2018, PMID 29723442](https://pubmed.ncbi.nlm.nih.gov/29723442/). The source record is consistent with those references; this is a **code normalization defect**, not a newly misfiled synonym.

**Why this is blocking in this round:** the new repair explicitly makes the optical descriptor part of the name, while the retained comparison contract ignores invisible characters and accents. Those rules together require `(-)-ARTEMISININ` and `(-\u200b)-ARTEMISININ` to retain the same negative sign. The latter instead draws a different optical form. The exact original M34-S2 examples are fixed; that does not close this composition failure. Round 34 treated punctuation erasure as a nonblocking limitation of the then-prescribed comparison. This round explicitly changes that prescription to preserve optical descriptors. This finding therefore does not silently broaden the review to arbitrary chemical punctuation.

Under the **buggy implementation** of `_sig`, the admitted input does equal the stored signature. A purely signature-membership test consequently passes, including an independently implemented oracle that repeats the same normalization order. The counterexample rests on the two documented transformation requirements and independently established identity, rather than a claimed failure of that narrower membership test. It is not one of the recorded over-refusals, excluded brands/synonyms, tracer exceptions, or free-text question leaks.

The repair needs to make ignored-character/diacritic normalization and optical-descriptor recognition compose correctly before punctuation is discarded, or fail closed when an optical descriptor cannot be interpreted safely. Verification should preserve `−`, `+`, and `±` through invisible/combining-character variants and must not enable additional stored-name admission. No production repair was made.

## Exact prior-finding dispositions

All rows have fresh HTTP evidence in [m34_exact_http.json](replay/m34_exact_http.json), [m33_exact_http.json](replay/m33_exact_http.json), [m32_exact_http.json](replay/m32_exact_http.json), and the [complete recent-input table](replay/recent_findings.md). The root independently corroborated the principal rows.

| Finding | Disposition | Exact inputs and result |
|---|---|---|
| M34-B1 | **FIXED** | `Cabozantinib (s)-malate`, `cabozantinibsmalate`, `CABOZANTINIB S-MALATE`, `Cabozantinib (s)-malate?`, `C a b o z a n t i n i b   ( s ) - m a l a t e`, `Cabozantinib/(s)-malate`, `Cabozantinib\u200b(s)-malate` (actual U+200B), `Cabozantinib (s)-malate™`: all refused. `CHEMBL2103868` draws by ID. Preferred-name refusal is the recorded over-refusal. |
| M34-S1 | **FIXED original recall** | `What trials evaluate (NICOTINE)?`, `What does (NICOTINE) target?`, `What trials evaluate [NICOTINE]?`: CHEMBL3 and two evidence rows in each question API; no map center. New descriptor wrapping is M35-S1 below. |
| M34-S2 | **FIXED exact original reproduction** | `(+)-NICOTINE`, `(+)NICOTINE`, `(-)-nicotine`: `not_found`. `(+/-)NICOTINE`, `(±)-nicotine`: CHEMBL440464. Bare `NICOTINE`: CHEMBL3. Unicode composition remains broken as M35-B1. |
| M33-B1 | **FIXED** | `Myocet`, `Myocet™`, `My/o/cet`, `My ocet`, `Inflectra`, `Inf/lectra`, `Equidacent`, `Equi/dacent`, `Fyarro`, `Fy/arro`, `Megace ES`, `Megace/ES`: refused. Original **456/456** HTTP variants refuse. |
| M33-D1 | **FIXED for map** | `Oraqix`: refused. |
| M33-D2 | **FIXED for map** | `Actikerall`: refused. |
| M33-D3 | **FIXED for map** | `Betnesol-n`: refused. |
| M33-D4 | **FIXED for map** | `Maxitrol`: refused. |
| M33-D5 | **FIXED for map** | `Cipro HC`: refused. |
| M33-D6 | **FIXED for map** | `Tobradex`: refused. |
| M33-S1 | **FIXED wrong-record reproduction** | `What trials evaluate (+/-)NICOTINE?`, `What does (+/-)NICOTINE target?`: no entity/evidence; map `not_found`. Racemic-name question recall is not restored. |
| M33-S2 | **FIXED classification under present policy** | `Darzalex`, `Tepezza`, `Tevimbra`, `Winrevair`, `Privigen`, `Lmx 4`: `alias_only`; brand recall is intentionally excluded. |
| M32-B1 | **FIXED** | `trastu+zumab`, `trastu$zumab`, `trastu=zumab`, `trastuzumabß`, `trastuzumabø`, `trastuzumabæ`, `trastuzumabł`, `trastuzumabð`, `trastuzumabı`: `not_one_name`. |
| M32-B2 | **FIXED** | `AstraZeneca +`, `Pfizer$`, `Pfi+zer`, `Roche $`: `not_one_name`; `Merck + Co`: `not_found`. `Merck & Co` draws ORG:merckco. |
| M32-B3 | **FIXED** | `ABT-510` / `ABT 510`: same choice of CHEMBL262489 and CHEMBL386115. `FLUDEOXYGLUCOSE F 18` / `FLUDEOXYGLUCOSE-F18`: same choice of CHEMBL2030434 and CHEMBL497613. `MAGE-A3` / `MAGEA3`: ENSG00000221867; `ctla-4` / `CTLA4`: ENSG00000163599. Excluded drug synonyms no longer create admitted ambiguity. |
| M32-B4 | **FIXED identity mismatch** | `Tarceva`, `Tarceva®`, `Tarceva™`, `Tarceva©`, `Tarceva℠`: all `alias_only`. |
| M32-D1 | **FIXED for map** | `bupivacaine hydrochloride`: `alias_only`. |
| M32-D2 | **FIXED for map** | `irinotecan liposome`, `irinotecan liposome injection`, `nanoliposomal irinotecan`, `doxorubicin hydrochloride liposome`: `alias_only`. |
| M32-D3 | **FIXED for map** | `ropeginterferon alfa-2b`: `alias_only`. |
| M32 inherited NICOTINE recall | **FIXED** | `What trials evaluate NICOTINE?`: CHEMBL3/two evidence rows, map `not_one_name`. |
| M32 trademark recall | **FIXED** | `trastuzumab™`: CHEMBL1201585; `AstraZeneca™`: ORG:astrazeneca. |
| M32 Greek alias recall | **NOT FIXED; intentional exclusion** | `thymosin α1`, `ifn-α-2b`, `interferon α-2b`: `alias_only`. |
| M32 blank-input view retention | **NOT FIXED; inherited nonblocker** | Submit empty/whitespace after a valid map: no request, old view retained. [Callback reproduction](contract/ui_m3_checks.json). |
| M32 nonfinite numbers | **NOT FIXED; fail-closed qualification** | Private stored `+Infinity`/`-Infinity`: controlled HTTP 400, no invalid drawn numeric value; absent in this snapshot. [Fixture](contract/db_numeric_fixture.json). |
| M32 malformed-body disclosure | **NOT FIXED; inherited nonblocker** | Malformed JSON, list/null bodies and oversized bodies produce controlled 400 with parser/attribute details; valid requests recover. [Exact bodies/replies](contract/server_checks.json). |

## Question-linker regression, separate from the blocker

### M35-S1 — wrapping the preferred name hides an adjacent stereochemical descriptor

**Nonblocking question-only regression**, `src/query.py:898-899`. The new boundary expression permits an opening bracket immediately before the preferred-name token and a closing bracket immediately after it. It does not inspect past those brackets for a descriptor. Exact parent/current comparisons show:

| Input | Parent query.py | HEAD query.py / HTTP |
|---|---|---|
| `What trials evaluate (+/-)(NICOTINE)?` | no entity/evidence | CHEMBL3 NICOTINE, two evidence rows |
| `What does (+/-)[NICOTINE] target?` | no entity/evidence | CHEMBL3 NICOTINE, two evidence rows |
| `What trials evaluate (NICOTINE)(+/-)?` | no entity/evidence | CHEMBL3 NICOTINE, two evidence rows |
| `What trials evaluate [NICOTINE](+/-)?` | no entity/evidence | CHEMBL3 NICOTINE, two evidence rows |
| `What trials evaluate (NICOTINE)(+)?` | no entity/evidence | CHEMBL3 NICOTINE, two evidence rows |

The bare racemic control `(+/-)NICOTINE` names CHEMBL440464. All three question APIs receive the erroneous CHEMBL3 evidence for these wrapped cases. The map returns `not_one_name`, so this does **not** independently fail the map approval bar. [Expanded parent/current comparison](contract/expanded_question_comparison.json), [summary and HTTP cases](contract/expanded_question_summary.json), [root corroboration](root_exact_http.json).

The expanded comparison covers **six shared preferred names × 26 formats × two question wrappers = 312 cases**, with 110 changed readings (a mixture of intended recall recoveries and descriptor regressions), **zero map centers**. The inherited **99-key / 708-case** comparison and all **36 shipped demos** are unchanged. Therefore the repair note's corpus result is reproduced, but that older corpus misses the new bracket-descriptor composition. [Shared-key corpus](contract/shared_key_question_comparison.json), [demos](contract/demo_previous_comparison.json). The separate 47-product/141-question refusal matrix retains its expected refusals. [Product controls](contract/product_questions.json).

## Data problems, separate from code

**M34-D1: NOT FIXED, recorded nonblocker.** `THEOPHYLLINE` / `Theophylline` still draws CHEMBL1355736 with stored `drug_type: "Protein"`. Source: `data/raw/drugs.json:1`, `data[191].drug.drugType`; the resolved dictionary and node preserve it. ChEBI identifies theophylline as dimethylxanthine, formula C7H8N4O2. This is upstream metadata, faithfully copied by the map. [ChEBI](https://www.ebi.ac.uk/chebi/CHEBI:28177), [fresh raw/dictionary/node records](theophylline_metadata.json), [current HTTP](root_exact_http.json).

The prior wrong-product alias records remain stored. Their **map reproductions are fixed**, while their upstream data assignments are **not claimed fixed**. Exact current source records, filed-under IDs, and map responses are in [known_data_records.json](known_data_records.json). The independent sources below were reopened in this round; [reference ledger](reference_verification.json).

| Finding / exact input | Stored index key → filed-under record | Independent identity |
|---|---|---|
| M33-D1 `Oraqix` | `oraqix` → CHEMBL79 LIDOCAINE | Lidocaine plus prilocaine. [DailyMed](https://dailymed.nlm.nih.gov/dailymed/lookup.cfm?setid=b501d239-923b-48b2-82ed-6c5c253a67e2). |
| M33-D2 `Actikerall` | `actikerall` → CHEMBL185 FLUOROURACIL | Fluorouracil plus salicylic acid. [Manufacturer SmPC](https://www.medicines.org.uk/emc/product/4621/smpc). |
| M33-D3 `Betnesol-n` | `betnesoln` → CHEMBL1200762 BETAMETHASONE SODIUM PHOSPHATE | Also contains neomycin sulfate. [HPRA](https://www.hpra.ie/find-a-medicine/for-human-use/authorised-medicines/details/28877). |
| M33-D4 `Maxitrol` | `maxitrol` → CHEMBL384467 DEXAMETHASONE | Also contains neomycin and polymyxin B. [DailyMed](https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=5776c435-ac60-49b6-8db1-23a3012b9155). |
| M33-D5 `Cipro HC` (stored `Cipro hc`) | `ciprohc` → CHEMBL389621 HYDROCORTISONE | Also contains ciprofloxacin hydrochloride. [DailyMed](https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=6b318e8c-ce91-41ce-9f35-fc9861cd9474). |
| M33-D6 `Tobradex` | `tobradex` → CHEMBL384467 DEXAMETHASONE | Also contains tobramycin. [DailyMed](https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=2a2259ee-05e4-4785-ba75-5946132debf3). |
| M32-D1 `bupivacaine hydrochloride` | `bupivacainehydrochloride` → CHEMBL4297652 ANTIMONY | An amide local anesthetic. [NCI](https://www.cancer.gov/publications/dictionaries/cancer-drug/def/bupivacaine-hydrochloride). |
| M32-D2 `irinotecan liposome`, `irinotecan liposome injection`, `nanoliposomal irinotecan` | Corresponding canonical keys → CHEMBL481 IRINOTECAN | Liposomal irinotecan formulation. [Onivyde label](https://dailymed.nlm.nih.gov/dailymed/fda/fdaDrugXsl.cfm?setid=c8b58efa-1820-48a4-b70d-62918fc4abfc). |
| M32-D2 `doxorubicin hydrochloride liposome` | `doxorubicinhydrochlorideliposome` → CHEMBL359744 DOXORUBICIN HYDROCHLORIDE | Liposomal formulation. [NCI](https://www.cancer.gov/about-cancer/treatment/drugs/doxorubicin-hydrochloride-liposome). |
| M32-D3 `ropeginterferon alfa-2b` | `ropeginterferonalfa2b` → CHEMBL1201558 INTERFERON ALFA-2B | PEG-conjugated interferon. [NCI](https://www.cancer.gov/publications/dictionaries/cancer-drug/def/ropeginterferon-alfa-2b). |

All these keys are at `data/processed/resolved.json:1`, `dictionary.index[<key>]`; exact occurrence pointers are retained in the JSON. M33 records are trade names; M32 records are AACT synonyms. Neither the alias exclusion policy nor safe terminal replies constitute data curation. No additional admitted preferred name/node label was proved to have an erroneous source identity. That is a bounded result, not certification of all scientific identities.

## Original guarantees A–G

| Check | Conclusion |
|---|---|
| A — relations/directions | **PASS** in a fresh independent SQL oracle over all **6,469 live centers / 22 combinations**; zero errors. Self-loop, unknown-type/relation, sponsor/collaborator and fallback fixtures pass. [Oracle](contract/db_validate.json), [special cases](contract/self_loop_unknown.json). |
| B — names/IDs/live candidates | **FAIL: M35-B1.** Exact repaired cases, admitted-name membership, shared choices, lower-case IDs and private retirement tests otherwise pass in the tested universe. [Blocker](root_optical_confirmation.json), [choice/retirement fixture](attacks/retired_private_fixture.json). |
| C — stored values/live counts | **PASS:** 19/19 DB assertions, missing versus zero, exact association scores, live trial counts, malformed props and 1,001-drug chunking. Infinity remains fail-closed. THEOPHYLLINE is stored-data error, not transcription error. [Assertions](contract/db_assertions.json). |
| D — order/cuts/totals | **PASS:** independent weights/ties/group order, true totals, list and map-ring cuts. [DB oracle](contract/db_validate.json), [UI execution](contract/ui_harness_results.json). |
| E — page safety/state | **PASS in executed JavaScript:** 26/26 assertions; escaped `choose` and `alias_only` fields, real HTTP choice clicks, safe URLs, trails, stale-response/error handling and recovery. Painted-browser layout was not verified. [Assertions](contract/ui_assertions.json), [choice clicks](contract/choose_ui.json), [regressions](contract/ui_regressions.json). |
| F — server | **PASS with inherited nonblockers:** controlled errors/recovery, 24 concurrent map calls and private retired-node fixtures. Parser-detail exposure, empty-submit retention and recorded lock costs remain qualified separately. [Server checks](contract/server_checks.json). |
| G — docs/read-only/no model | Universal optical-sign/invisible comparison is **not satisfied**, M35-B1. Whole-alias refusal closure and preferred-name policy otherwise match exercised behavior. Inspected paths use reads and `use_llm=False`; final file integrity is reported below. |

Opera reported no connected browser; CUA `getState` timed out. UI evidence executes the actual served JavaScript in a Node VM DOM/fetch harness, including real HTTP callbacks. It establishes generated markup and application-state behavior, **not** browser painting or visual layout. [Availability record](browser_availability.json).

## Expanded source and attack coverage

The oracle reconstructs admitted membership from dictionary and SQL records, **not `Engine.names`**. It includes every drug preferred name and alias, every index entry, node label, target symbol, company key and disease key. It additionally probes canonical drug-index keys as inputs. The **22,956 inputs** comprise **16,015 literal stored spellings/read keys** (the prior 14,639 plus 1,376 globally omitted raw-alias spellings) and **6,941 additional canonical drug-index key strings**. All are within the HTTP length limit; maximum length is 231. The complete sweep uses direct `Engine.explore`; selected cases are separately confirmed through HTTP. [Source inventory](attacks/all_source_records.json), [independent oracle](attacks/source_audit.py), [classified counts](attacks/source_classified_summary.json).

Overall results: **10,088 centers, 12,486 `alias_only`, 354 refused, eight choices, five `not_found`, 15 `not_one_name`**, zero failures/exceptions. The literal-source subset yields 9,081 centers, 6,738 `alias_only`, 187 refused, six choices and three `not_found`. Raw-alias spelling occurrence counts and unique-string counts are kept separate. Same-drug index omissions are **1,696 records / 1,420 spellings**; the prior round's global-spelling omission definition yields **1,652 records / 1,376 spellings**. Both contain the same **18 omitted refused spellings**; all **29 source inputs sharing their signatures now refuse**. All stored preferred-name alias/index spellings and live drug labels agree with `drug['name']`; skipping redundant preferred-name entries leaves no actual alternate-spelling gap in this dataset. [Omission closure](attacks/omitted_refusal_summary.json), [source discrepancies/equality](attacks/source_discrepancies.json).

The refusal sweep exercises **182 actual refused stored spellings × 13 forms = 2,366 inputs; all refuse**. A separate **84 canonical keys × 13 = 1,092** probes all remain undrawn: 1,074 refused, 12 `alias_only`, six `not_found`. The latter 18 are terminal-state differences on three synthetic canonical keys, not failures to refuse literal stored names and not wrong-center draws. This distinction corrects the broader variable name `refused_stored_names: 266` in the unclassified summary. [Classified refusal results](attacks/refusal_variants_classified.json), [full matrix](attacks/refusal_variants.json).

**1,066 preferred names × six significant suffixes = 6,396 inputs** draw no center. **54 private retirement cases / 10 assertion groups** pass: both live → choose, one retired → remaining live candidate, all retired → not-found, including lowercase IDs and no retired-Roche fallback to a drug alias. Production DB hash remains unchanged. [Suffixes](attacks/significant_suffixes_summary.json), [retirement results](attacks/retired_private_fixture.json). These successes do not cover the separate optical-invisible mutation invariant.

## Historical replay and review axes

All **275 inherited naming finding rows** have fresh exact-case dispositions: **257 FIXED / 18 NOT FIXED overall**, **260 FIXED / 15 NOT FIXED for the map**. Map residuals are nine recorded over-refusal rows and six deliberately excluded recall cohorts; three further overall residuals concern question-only behavior. This ledger is historical; it does not contain the new M35 blocker or replace its verdict. [Counts](replay/matrix_summary.json), [per-finding inputs/results](replay/per_finding_cases.json), [readable ledger](replay/historical_table.md). All **23 inherited nonidentity rows** were rerun, **20 FIXED / three NOT FIXED**, with exact inputs/fixtures in [contract/HISTORY.md](contract/HISTORY.md). The ledgers overlap and are not added as unique-finding counts.

All **123 historical leaf jobs exited 0**, with **151 original/copy provenance entries**, **45 lifecycle records**, no lifecycle failure flags and **27 replay ports confirmed closed**. The original **7,511-key alias sweep** and two **1,648-question frozen/historical replays** completed; each of the latter reports 1,648 identical and zero errors. The separate no-relink adapter reports 72 identical, 1,552 entity-metadata-only and 24 semantic differences against its constructed old baseline; those are not HEAD-versus-parent counts. The unavailable original M22 generator is **not** claimed to have run: its byte-identical saved-input adapter reran the recorded **58 inputs**. Old assertions that expected a longer input to draw are not substituted for the current admission oracle. [Execution summary](replay/execution_summary.json), [QA summary](replay/historical_qa_summary.json), [reuse/caveats](replay/FINDINGS.md).

All **15 cost suites exited 0**. Their **11 historical dispositions are six FIXED / five NOT FIXED**. Inherited residuals remain for 400 distinct `isa` pieces, 4,000 U+FDFA characters, 1,000 punctuation-separated `x` tokens, 1,000 `isa` matches and joined-item rescans. The current cold request / queued-map times are respectively **7.032 / 6.980 s**, **8.690 / 8.632 s**, **0.526 s direct median** for punctuation tokens, **8.234 / 8.178 s**, and **7.990 / 7.952 s**. These are successful completions with residual overhead, not new timeouts or proof of a commit-caused performance regression; audit jobs ran concurrently. All seven cost-server lifecycles retain DB hashes and close their ports. [Per-finding cost ledger](contract/cost/FINDINGS.md), [summary](contract/cost/summary.json), [post-cost integrity](contract/post_cost_integrity.json).

The cost runner's initial **auxiliary** request used an incorrect oversized 2,000-osimertinib answer and returned 400 after all 15 suites had completed. The scratch request was corrected to the actual historical `EGFR` question with `';'.join(['x'] * 2000)` answer; it returned HTTP 200 in **0.719 s**. This harness error and correction are retained, not counted as a production regression or an unresolved successful test. [Runner note](contract/cost/runner_note.json), [exact corrected request](contract/cost/repeat_2000_http.json).

**Standards axis: zero hard documented-standard violations.** Parameterized SQL, live filtering and page escaping remain in place. The user's evidence and no-tracked-edit requirements govern this review; no unrelated tracker setup or invented style standard was imposed. No production code was changed, so the conditional KOA Studio/KhOpenApi code-repair comparison requirement does not arise. [Independent Standards review](contract/FINDINGS.md#standards-axis-separate-from-spec-under-400-words).

**Spec axis: not satisfied.** Whole-alias refusal closure and the exact prior repair examples pass. The new optical-sign guarantee does not compose with the existing ignored-invisible rule (M35-B1), yielding a proven wrong optical identity. The bracket-descriptor question regression (M35-S1) is separately nonblocking. No additional source data defect was established. [Independent Spec review](attacks/findings.md#spec-axis-under-400-words).

## Integrity and limits

All **7,835 tracked files plus the processed database and resolved dictionary** match the root's pre-test SHA-256 baseline: **7,837 files checked, zero changed or added**, tracked git status clean, HEAD unchanged. Root stopped its owned CLI session on port 8935 after all requests finished; all **31 owned/tested ports** are closed. [Initial hashes](integrity_before.json), [final integrity](integrity_final.json), [server/port lifecycle](server_lifecycle.json). Scratch artifacts and this report are confined to m35. No production repair, source-data curation, external publication or model invocation was performed.

This review establishes the exact counterexamples and bounded positive checks above. It does not certify exhaustive scientific identity for every source name, universal free-text refusal, graph-construction brand assignments, or rendered-browser layout. The new code blocker remains despite passing unit tests and full-source membership checks because those checks do not establish the intended composition of optical-sign and invisible-character rules.

VERDICT: CHANGES REQUIRED
