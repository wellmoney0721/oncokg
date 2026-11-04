# Independent relation-map review — round 36

Reviewed **HEAD `c3040c184ad4da0fc638d61ab94d46501c61a11a`**, parent `56eb3d6297f2878d008e5edd9eb5eade62a0841c`, on 2026-11-04. **CHANGES REQUIRED: two normalization blockers.** The exact M35-B1 and M35-S1 reproductions are fixed. A punctuation character can still hide a negative optical descriptor, and the new descriptor substitution deletes unrelated significant symbols. A separate nested-descriptor question regression is nonblocking under the specified scope. No new upstream data defect was established.

Scope is section 0 of `web/try.html`, `POST /api/explore`, and `Engine.explore`, under the [round-32 approval bar](../m32/brief.md), [round-34 name policy](../m34/brief.md), its [round-35 amendment](../m35/brief.md), and [round-35 report](../m35/REPORT.md). FIXED below closes an exact reproduction under the current preferred-name policy; it does not certify all related spellings, restore excluded aliases, or imply source-data curation. This is a review; no production repair was made.

## Verification

- **`python -m pytest tests -q -p no:cacheprovider`: 364 passed in 129.57 seconds**, exit 0; wrapper elapsed 132.828 seconds. One warning came from a subprocess reader decoding UTF-8 output as CP949 in `test_correction_check_fails_when_a_correction_is_pending`. That test was rerun with `PYTHONUTF8=1`: **1 passed in 3.94 seconds**, no warning. The full-suite warning is retained rather than described as a warning-free run. [Full output](pytest.txt), [command/timing](pytest_meta.json), [focused recheck](pytest_warning_recheck.txt).
- Started the actual CLI using **`python src/app.py 8936`**. Root retained **274 HTTP response records**: 124 baseline, 85 exact/adversarial, 36 supplement, 22 new attack cases, and seven Unicode confirmations. This counts retained records, not every request made by all lanes. Empty input and 501-character input produce the two expected baseline HTTP 400 responses. The served page is byte-identical to `web/try.html`. [Baseline](root_confirmation.json), [bodies](root_http.json), [exact cases](root_exact_http.json), [supplement](root_supplement_http.json), [new attacks](root_new_attack_http.json), [Unicode HTTP](ignored_character_http.json).
- **4,689 distinct historical/current inputs**: 301 centers, 1,434 refusals, 2,555 `alias_only`, 327 `not_one_name`, 68 `not_found`, four choices; zero exceptions, independent admitted-name membership failures, silent ambiguous draws, or wrong choice sets. Four changes against the 4,673 prior corpus inputs are intended mark-removal recall: `"trastuzumab\u034f"`, `"trastuzumab\ufe0f"`, `"trastuzumab\U000e0100"`, and `"trastu\u034fzumab"` now draw CHEMBL1201585. Actual Unicode characters are meant in these escaped spellings. [Corpus summary](replay/corpus_summary.json), [responses](replay/corpus_results.json), [parent differences](replay/parent_corpus_changes.json).

## Code blockers

### M36-B1 — underscore punctuation still erases a negative optical descriptor

**Location:** `src/app.py:282-296`, especially `_SIGN_GROUP` at line 289 and the final punctuation filter at line 284. The comment and amended contract say a group with no letters or digits is recognized. Python `\w` also includes `_`, however. `(-_)` therefore does not match; the subsequent punctuation filter deletes both the hyphen and underscore. The sign is never recovered.

| Exact input / Python spelling | Current `_sig` | Fresh HTTP result |
|---|---|---|
| `ARTEMISININ` | `artemisinin` | center **CHEMBL269671** |
| `(-)-ARTEMISININ` | `−artemisinin` | `not_one_name` |
| `"(-\u200b)-ARTEMISININ"` | `−artemisinin` | `not_one_name`; M35-B1 exact repair works |
| `(-_)-ARTEMISININ` | `artemisinin` | **center CHEMBL269671** |
| `(_-)-ARTEMISININ` | `artemisinin` | **same center** |
| `[-_]-ARTEMISININ` | `artemisinin` | **same center** |
| `"(-\u200b_\u0301)-ARTEMISININ"` | `artemisinin` | **same center** |
| `"(-\uff3f)-ARTEMISININ"` | `artemisinin` | **same center**; fullwidth underscore folds to `_` |
| `"(-\u203f)-ARTEMISININ"` | `−artemisinin` | `not_one_name`; undertie punctuation control |
| `CHEMBL269671` | permitted ID path | center CHEMBL269671 |

This is a residual composition defect, present in the parent too, not a claim that the four original M35 inputs still fail. Removing marks/invisibles first correctly repairs those inputs; it does not repair a punctuation character that the descriptor recognizer mistakenly classifies as a word character. [Exact HTTP/code points](root_new_attack_http.json), [step-by-step normalization and parent signatures](normalization_stages.json), [full parent/current comparison](root_parent_comparison.json).

An independent enumeration of **3,501 assigned punctuation/spacing/mark/control characters** whose normalized form is ignorable and contains no additional sign, letter, digit, or grouping delimiter finds **seven failures**: U+005F, U+FE33, U+FE34, U+FE4D, U+FE4E, U+FE4F, U+FF3F. All seven normalize to underscore and all seven draw CHEMBL269671 over HTTP. Unassigned code points, private-use characters, and surrogates are excluded from this count. [Predicate, failures](ignored_character_matrix.json), [HTTP confirmations](ignored_character_http.json), [reproducible checker](root_composition.py).

**Identity evidence:** `data/processed/resolved.json:1`, `dictionary.drugs.CHEMBL269671.name` is `ARTEMISININ`, with `aliases[1].alias == "(+)-artemisinin"`; raw provenance is `data/raw/drugs.json:1`, `data[768].drug`. ChEBI identifies the natural compound as the positive optical form; primary synthesis research explicitly distinguishes negative artemisinin from its natural positive antipode. These references were reopened during this review. [Source records](focused_source_records.json), [ChEBI](https://www.ebi.ac.uk/chebi/CHEBI:223316), [Krieger et al., PMID 29723442](https://pubmed.ncbi.nlm.nih.gov/29723442/).

Thus the source assignment is consistent; the wrong draw is caused by code dropping the input's negative descriptor. The same issue appears with nested empty punctuation, e.g. `(-())-ARTEMISININ`, but the blocker requires only the unambiguous underscore examples above.

### M36-B2 — descriptor substitution consumes unrelated significant symbols

**Location:** `src/app.py:289-296`. The broad pattern accepts any non-word, non-bracket character; `_sign` replaces the entire match with one sign and discards every other symbol it contained. This newly weakens the retained rule that letters, digits and symbols must match (`Engine.explore`, lines 110–115; `_sig`, lines 270–275).

| Exact input | Parent result | HEAD signature / fresh result |
|---|---|---|
| `(+/-)NICOTINE` | CHEMBL440464 | `±nicotine`; same legitimate center |
| `(+/-☢)NICOTINE` | `not_found` | `±nicotine`; **CHEMBL440464** |
| `(±☢)NICOTINE` | `not_found` | `±nicotine`; **CHEMBL440464** |
| `(+/-$)NICOTINE` | `not_found` | `±nicotine`; **CHEMBL440464** |
| `(+/-×)NICOTINE` | `not_found` | `±nicotine`; **CHEMBL440464** |
| `(+/-)NICOTINE☢` | `not_found` | `±nicotine☢`; `not_found` |

The stored preferred name is `dictionary.drugs.CHEMBL440464.name == "(+/-)NICOTINE"`. It does not contain ☢ (U+2622, `So`), $ (U+0024, `Sc`), or × (U+00D7, `Sm`). These are neither punctuation nor the ignored trademark marks nor rotation signs. The table's parent/current Engine comparison loads **both parent `app.py` and parent `query.py`**, so this is a demonstrated commit regression rather than only a theoretical regex difference. Root HTTP separately confirms `(±☢)NICOTINE`, `(+/☢-)NICOTINE`, and `(+/×-)NICOTINE`. [Parent/current responses](root_parent_comparison.json), [HTTP](root_new_attack_http.json), [normalization stages](normalization_stages.json), [source record](focused_source_records.json).

The round-36 change summary accurately describes the broad collapse of a sign-containing group with no letters/digits. It does **not** remove the retained approval bar or the explicit guarantee that other significant symbols match. This finding identifies that design conflict: broad group collapse cannot be used to justify dropping arbitrary symbols. No assertion that `☢` alone identifies a particular isotope or pharmaceutical product is needed; the input contains a significant symbol absent from the admitted name.

Across the source inventory, **14 distinct optical-descriptor spellings / 30 source occurrences × six extra-symbol mutations = 84 cases** all lose the extra symbol. Six variants of the admitted `(+/-)NICOTINE` preferred name draw CHEMBL440464. Other source spellings are aliases and stay excluded. [Descriptor source inventory](attacks/descriptor_source_records.json), [all mutations](attacks/sign_symbol_composition.json), [summary](attacks/sign_symbol_composition_summary.json).

## Question-linker regression — nonblocking

### M36-S1 — an extra pair of brackets around the descriptor hides it

**Location:** `src/query.py:118-134`, `_named_alone`. It peels brackets surrounding the name, then requires the adjacent descriptor to match immediately at the edge of the remaining text. It does not look through an extra pair of brackets around that descriptor.

| Exact question | Parent linker | HEAD / question APIs |
|---|---|---|
| `What trials evaluate ((+/-))NICOTINE?` | no entity/evidence | **CHEMBL3 NICOTINE**, two evidence rows |
| `What does NICOTINE((+/-)) target?` | no entity/evidence | **CHEMBL3 NICOTINE**, two evidence rows |
| `What trials evaluate (+/-)(NICOTINE)?` | CHEMBL3 | no entity/evidence; original M35-S1 fixed |
| `What trials evaluate (NICOTINE)?` | CHEMBL3 | CHEMBL3; ordinary bracket recall retained |

The incorrect nested-descriptor reading reaches `/api/ask`, `/api/structured`, and `/api/check`; the map returns `not_one_name`. Therefore it is **not a map blocker**, consistent with README defect 15 and the review scope. [36 HTTP records and parent controls](contract/question_regression_http.json), [540-case composition matrix](contract/question_composition.json), [summary](contract/question_composition_summary.json).

The new matrix covers six shared preferred names × 45 formats × two question wrappers: **540 cases, 130 changed readings, zero map centers**. Changes include successful M35 repair cases as well as the new regression; 130 is not a defect count. All **36 shipped demos** and the inherited **99-key / 708-case** shared-name corpus remain parent-identical. [Demos](contract/demo_previous_comparison.json), [shared-key comparison](contract/shared_key_question_comparison.json).

## Prior exact findings

| Finding | Disposition | Exact inputs and fresh result |
|---|---|---|
| M35-B1 | **FIXED exact reproduction** | `"(-\u200b)-ARTEMISININ"`, `"(-\ufeff)-ARTEMISININ"`, `"(-\u2060)-ARTEMISININ"`, `"(-\u0301)-ARTEMISININ"` (actual Unicode characters) and the ordinary negative controls are undrawn. `ARTEMISININ` and `CHEMBL269671` still draw CHEMBL269671; `(+)-ARTEMISININ` is `alias_only`. [Exact HTTP/codepoints](replay/m35_exact_http.json). |
| M35-S1 | **FIXED exact reproduction** | `What trials evaluate (+/-)(NICOTINE)?`, `What does (+/-)[NICOTINE] target?`, `What trials evaluate (NICOTINE)(+/-)?`, `What trials evaluate [NICOTINE](+/-)?`, `What trials evaluate (NICOTINE)(+)?`, and `What trials evaluate NICOTINE (+/-)?` have zero entities/evidence in all three question APIs. `What trials evaluate ( NICOTINE ) and osimertinib?` retains both drug entities. All full questions stay undrawn. [Exact HTTP](replay/m35_exact_http.json). |
| M34-B1 | **FIXED** | `Cabozantinib (s)-malate`, `cabozantinibsmalate`, `CABOZANTINIB S-MALATE`, `Cabozantinib (s)-malate?`, `C a b o z a n t i n i b   ( s ) - m a l a t e`, `Cabozantinib/(s)-malate`, `Cabozantinib\u200b(s)-malate` (actual U+200B), and `Cabozantinib (s)-malate™` all refuse. `CHEMBL2103868` still draws that exact ID. The preferred-name refusal is the recorded over-refusal. |
| M34-S1 | **FIXED** | `What trials evaluate (NICOTINE)?`, `What does (NICOTINE) target?`, `What trials evaluate [NICOTINE]?`, `What does [NICOTINE] target?` all link CHEMBL3 and return two evidence rows in each question API; the map returns `not_one_name`. Descriptor controls `What trials evaluate (+/-)NICOTINE?` and `What trials evaluate NICOTINE(+)?` abstain with zero evidence. |
| M34-S2 | **FIXED exact original reproduction** | `(+)-NICOTINE`, `(+)NICOTINE`, `(-)-nicotine` return `not_found`; `(+/-)NICOTINE` and `(±)-nicotine` draw CHEMBL440464; bare `NICOTINE` draws CHEMBL3. This closes the exact prior inputs. Normalization composition attacks are reported separately by the root/source lane. |
| M34-D1 | **NOT FIXED, recorded data nonblocker** | `THEOPHYLLINE` draws CHEMBL1355736 and still carries stored `drug_type: Protein`. No metadata repair is claimed. |
| M33-B1 | **FIXED** | `Myocet`, `Myocet™`, `My/o/cet`, `My ocet`, `Inflectra`, `Inf/lectra`, `Equidacent`, `Equi/dacent`, `Fyarro`, `Fy/arro`, `Megace ES`, `Megace/ES` refuse. All original **456/456** stored-brand variants refuse; no centers. [Full matrix](replay/m33_brand_variants_http.json). |
| M33-D1 | **FIXED for map** | `Oraqix` refuses; no LIDOCAINE center. |
| M33-D2 | **FIXED for map** | `Actikerall` refuses; no FLUOROURACIL center. |
| M33-D3 | **FIXED for map** | `Betnesol-n` refuses; no BETAMETHASONE SODIUM PHOSPHATE center. |
| M33-D4 | **FIXED for map** | `Maxitrol` refuses; no DEXAMETHASONE center. |
| M33-D5 | **FIXED for map** | `Cipro HC` refuses; no HYDROCORTISONE center. |
| M33-D6 | **FIXED for map** | `Tobradex` refuses; no DEXAMETHASONE center. |
| M33-S1 | **FIXED wrong-record reproduction** | `What trials evaluate (+/-)NICOTINE?` and `What does (+/-)NICOTINE target?` abstain in all question APIs (zero entities/evidence), with `not_found` on map. Bare `(+/-)NICOTINE` retains CHEMBL440464. Racemic-name question recall is not restored. |
| M33-S2 | **FIXED source-classification mismatch under new policy** | `Darzalex`, `Tepezza`, `Tevimbra`, `Winrevair`, `Privigen`, `Lmx 4` return `alias_only`. Brand recall is deliberately excluded. |
| M32-B1 | **FIXED** | `trastu+zumab`, `trastu$zumab`, `trastu=zumab`, `trastuzumabß`, `trastuzumabø`, `trastuzumabæ`, `trastuzumabł`, `trastuzumabð`, `trastuzumabı` all return `not_one_name`. |
| M32-B2 | **FIXED** | `AstraZeneca +`, `Pfizer$`, `Pfi+zer`, `Roche $` return `not_one_name`; `Merck + Co` is `not_found`; control `Merck & Co` draws ORG:merckco. |
| M32-B3 | **FIXED** | `ABT-510` / `ABT 510` both choose CHEMBL262489 and CHEMBL386115. `FLUDEOXYGLUCOSE F 18` / `FLUDEOXYGLUCOSE-F18` both choose CHEMBL2030434 and CHEMBL497613. `MAGE-A3` / `MAGEA3` draw ENSG00000221867; `ctla-4` / `CTLA4` draw ENSG00000163599. |
| M32-B4 | **FIXED identity mismatch** | `Tarceva`, `Tarceva®`, `Tarceva™`, `Tarceva©`, `Tarceva℠` all return `alias_only`. |
| M32-D1 | **FIXED for map** | `bupivacaine hydrochloride` returns `alias_only`. Underlying AACT curation is not claimed. |
| M32-D2 | **FIXED for map** | `irinotecan liposome`, `irinotecan liposome injection`, `nanoliposomal irinotecan`, `doxorubicin hydrochloride liposome` return `alias_only`. |
| M32-D3 | **FIXED for map** | `ropeginterferon alfa-2b` returns `alias_only`. |
| M32 inherited NICOTINE recall | **FIXED** | `What trials evaluate NICOTINE?` links CHEMBL3 with two evidence rows in ask/check/structured, and the map is `not_one_name`. |
| M32 Greek stored-alias recall | **NOT FIXED; intentional exclusion** | `thymosin α1`, `ifn-α-2b`, `interferon α-2b` return `alias_only`. |
| M32 trademark recall | **FIXED** | `trastuzumab™` draws CHEMBL1201585; `AstraZeneca™` draws ORG:astrazeneca. |


The exact request/response ledger includes all earlier name findings and original Unicode characters. The nonidentity historical findings are covered below and in the contract ledger.


## Data problems, separate from code

**M34-D1 remains NOT FIXED, recorded nonblocker.** `THEOPHYLLINE` / `Theophylline` draws CHEMBL1355736 with stored `drug_type: "Protein"`. Raw source is `data/raw/drugs.json:1`, `data[191].drug.drugType`; the resolved dictionary and node preserve it. ChEBI describes a dimethylxanthine, C7H8N4O2. This is upstream metadata, faithfully displayed by the map. [Current source records](focused_source_records.json), [HTTP](root_exact_http.json), [ChEBI](https://www.ebi.ac.uk/chebi/CHEBI:28177).

The earlier wrong-product aliases remain stored: their **map reproductions are FIXED**, while their **data assignments are NOT FIXED**. All exact source occurrence pointers and current replies are in [known_data_records.json](known_data_records.json); references were reopened in this round and logged in [reference_verification.json](reference_verification.json).

| Finding / exact input | Filed-under source record | Independent product identity |
|---|---|---|
| M33-D1 `Oraqix` | `dictionary.index.oraqix` → CHEMBL79 LIDOCAINE | Lidocaine **and prilocaine**. [DailyMed](https://dailymed.nlm.nih.gov/dailymed/lookup.cfm?setid=b501d239-923b-48b2-82ed-6c5c253a67e2). |
| M33-D2 `Actikerall` | `dictionary.index.actikerall` → CHEMBL185 FLUOROURACIL | Fluorouracil **and salicylic acid**. [Manufacturer SmPC](https://www.medicines.org.uk/emc/product/4621/smpc). |
| M33-D3 `Betnesol-n` | `dictionary.index.betnesoln` → CHEMBL1200762 BETAMETHASONE SODIUM PHOSPHATE | Also contains **neomycin sulfate**. [HPRA](https://www.hpra.ie/find-a-medicine/for-human-use/authorised-medicines/details/28877). |
| M33-D4 `Maxitrol` | `dictionary.index.maxitrol` → CHEMBL384467 DEXAMETHASONE | Also contains **neomycin and polymyxin B**. [DailyMed](https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=5776c435-ac60-49b6-8db1-23a3012b9155). |
| M33-D5 `Cipro HC` (stored `Cipro hc`) | `dictionary.index.ciprohc` → CHEMBL389621 HYDROCORTISONE | Also contains **ciprofloxacin hydrochloride**. [DailyMed](https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=6b318e8c-ce91-41ce-9f35-fc9861cd9474). |
| M33-D6 `Tobradex` | `dictionary.index.tobradex` → CHEMBL384467 DEXAMETHASONE | Also contains **tobramycin**. [DailyMed](https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=2a2259ee-05e4-4785-ba75-5946132debf3). |
| M32-D1 `bupivacaine hydrochloride` | `dictionary.index.bupivacainehydrochloride` → CHEMBL4297652 ANTIMONY | An **amide local anesthetic**. [NCI](https://www.cancer.gov/publications/dictionaries/cancer-drug/def/bupivacaine-hydrochloride). |
| M32-D2 `irinotecan liposome`, `irinotecan liposome injection`, `nanoliposomal irinotecan` | Corresponding canonical index keys → CHEMBL481 IRINOTECAN | **Liposomal irinotecan formulation**. [Onivyde label](https://dailymed.nlm.nih.gov/dailymed/fda/fdaDrugXsl.cfm?setid=c8b58efa-1820-48a4-b70d-62918fc4abfc). |
| M32-D2 `doxorubicin hydrochloride liposome` | `dictionary.index.doxorubicinhydrochlorideliposome` → CHEMBL359744 DOXORUBICIN HYDROCHLORIDE | **Liposomal formulation**. [NCI](https://www.cancer.gov/about-cancer/treatment/drugs/doxorubicin-hydrochloride-liposome). |
| M32-D3 `ropeginterferon alfa-2b` | `dictionary.index.ropeginterferonalfa2b` → CHEMBL1201558 INTERFERON ALFA-2B | **PEG-conjugated interferon**. [NCI](https://www.cancer.gov/publications/dictionaries/cancer-drug/def/ropeginterferon-alfa-2b). |

All dictionary pointers above are in `data/processed/resolved.json:1`. M33 records are trade names; M32 records are AACT synonyms. The present alias-exclusion rule closes the map exposure, not the upstream curation issue. No additional admitted name was proved to have an incorrect source identity; this is not an exhaustive scientific certification of every stored name.

## Expanded source, historical replay, and guarantees A–G

The expanded sweep covers **22,956 distinct source/key inputs from 34,429 records**, including **every one of the 9,581 entries in `dictionary.drugs[*].aliases`**, all preferred names, index aliases and keys, node labels, target symbols, and company/disease keys. There are 16,015 literal source spellings/read keys and 6,941 additional canonical drug-index key strings. Fresh results: **10,088 centers, 12,486 `alias_only`, 354 refused, eight choices, five `not_found`, 15 `not_one_name`**. Corrected independent membership/refusal/choice assertions have zero failures or exceptions; all responses equal the prior round's corresponding source responses. [Inventory](attacks/all_source_records.json), [source results](attacks/source_sweep.json), [summary](attacks/source_summary.json), [source classes](attacks/source_classified_summary.json), [parent changes](attacks/source_parent_changes.json).

The oracle rebuilds membership from dictionary and SQL records, without reading `Engine.names`. Its first generated version suffered a PowerShell-to-Python encoding error that converted three Unicode literals to question marks. The actual inputs and production replies were unaffected. The original script/results were preserved, the oracle was corrected to ASCII Unicode escapes and checked on four controls, and **all 22,956 saved fresh responses were revalidated**. Only those corrected assertions support this report. [Correction and provenance](attacks/findings.md#oracle-correction-and-limits), [revalidation code](attacks/revalidate_source.py), [revalidation log](attacks/revalidation.log).

Composition was tested on **every stored/source input**, not just the new examples: eight formatting transforms × 22,956 inputs = **183,648 signature comparisons**. Twelve fail, all involving underscore insertion into a stored optical descriptor; the other seven transform families have no differences. Fresh map follow-up shows three excluded optical aliases become drawn preferred names: `(_-_)_-_P_A_C_L_I_T_A_X_E_L` → CHEMBL428647, `(_-_)_-_g_o_s_s_y_p_o_l` → CHEMBL51483, and `(_-_)_-_s_i_r_p_i_g_l_e_n_a_s_t_a_t` → CHEMBL4650367. This demonstrates policy/signature instability; it does not assert a new scientific source misassignment. [All differences](attacks/composition_benign_differences.json), [exact follow-up replies](attacks/composition_benign_map_followup.json).

For each of the same 22,956 inputs, the independent optical invariant compares a `(-)-` prefix with `"(-_\u200b\u0301)-"`. All 22,956 lose the sign in the second form; **10,084 draw centers and eight produce choices**, while their signed controls remain undrawn. These are repeated manifestations of M36-B1, including company/target/trial names; they are **not 10,084 independently proven chemical identity errors**. [Composition summary](attacks/composition_summary.json), [signature differences](attacks/composition_sign_differences.json), [draw/control responses](attacks/composition_draws.json).

Supporting safety checks remain positive: **182 literal refused spellings × 13 forms = 2,366, all refused**; another **84 canonical-only keys × 13 = 1,092** remain undrawn (1,074 refused, 12 `alias_only`, six `not_found`). The latter 18 are synthetic-key terminal-state differences. **1,066 preferred names × six significant suffixes = 6,396** draw no center. **54 private retirement cases / ten assertion groups** pass, including both-live choices, one-live reduction, all-retired, lowercase IDs, and retired Roche. All **29 source inputs sharing the 18 omitted refused spellings' signatures refuse**. [Refusal classes](attacks/refusal_variants_classified.json), [suffixes](attacks/significant_suffixes_summary.json), [retirement](attacks/retired_private_fixture.json), [omitted-alias closure](attacks/omitted_refusal_summary.json).

All **123 historical leaf jobs exited 0**, as did all nine additional replay jobs. There are 151 reuse provenance entries, 45 lifecycle records, no lifecycle failure flags, and 27 closed replay ports. The original **7,511-key alias sweep** and both **1,648-question frozen/historical replays** completed; each question replay reports 1,648 identical and zero errors. The constructed no-relink adapter separately reports 72 identical, 1,552 entity-metadata-only, and 24 semantic differences; these are **not** HEAD-versus-parent counts. The unavailable original M22 generator is not claimed to have run: its saved-input adapter replays the recorded 58 inputs. [Execution summary](replay/execution_summary.json), [QA summary](replay/historical_qa_summary.json), [provenance and caveats](replay/FINDINGS.md).

All **275 inherited naming finding rows** have fresh exact-case dispositions: **257 FIXED / 18 NOT FIXED overall**, **260 FIXED / 15 NOT FIXED for the map**. Residual map rows are the nine recorded over-refusal rows and six deliberately excluded recall cohorts; three further overall residuals concern question-only behavior. This historical ledger does not contain or supersede the new blockers. [Per-finding cases](replay/per_finding_cases.json), [readable ledger](replay/historical_table.md), [counts](replay/matrix_summary.json).

| Guarantee | Fresh result and scope |
|---|---|
| A — relations/directions | **PASS**: independent SQL oracle across all **6,469 live centers / 22 relation combinations**, zero errors. Self-loops, unknown types/relations, sponsor/collaborator roles and Investigator labels retain correct behavior. [Oracle](contract/db_validate.json), [special cases](contract/self_loop_unknown.json). |
| B — names/IDs/live choices | **FAIL: M36-B1 and M36-B2.** Exact prior repairs, IDs, live-candidate sets and private retirement controls otherwise pass in the tested cases. [Blockers](root_new_attack_http.json), [choice clicks](contract/choose_ui.json), [retirement](attacks/retired_private_fixture.json). |
| C — stored values/live counts | **PASS, 19/19 assertions**: missing versus zero, exact scores, boolean handling, malformed props, live trial counts and 1,001-drug chunking. Synthetic Infinity fails closed with HTTP 400. THEOPHYLLINE's type is an upstream error. [Assertions](contract/db_assertions.json), [numeric fixture](contract/db_numeric_fixture.json). |
| D — ordering/cuts/totals | **PASS**: independent weight ordering, label ties, group sizes, true totals and actual page list/ring-cut behavior. [DB oracle](contract/db_validate.json), [page JS](contract/ui_harness_results.json). |
| E — page safety/state | **PASS within the executed JavaScript harness, 26/26 assertions**: escaped labels/IDs/URLs, safe `choose` and `alias_only` markup, real choice click-through, trails, stale responses, double clicks and error recovery. Painted-browser layout was not verified. [Assertions](contract/ui_assertions.json), [choices](contract/choose_ui.json), [state checks](contract/ui_regressions.json). |
| F — server | **PASS with recorded qualifications**: controlled invalid requests, recovery, 24 concurrent map calls and retired-node fixtures. Blank-submit retention and parser-detail disclosure remain inherited nonblockers. [Server](contract/server_checks.json), [callbacks](contract/ui_m3_checks.json). |
| G — docs/read-only/no model | **FAIL for universal normalization wording**, as demonstrated by both blockers. The preferred-name/alias policy otherwise matches the exercised literal-source behavior; inspected paths remain read-only and call no model. See final integrity below. |

The **23 inherited nonidentity rows** were rerun: **20 FIXED / three NOT FIXED**. Residual exact cases are: submit empty/whitespace after a valid map (old view remains, no request); private `+Infinity`/`-Infinity` stored numeric values (controlled HTTP 400 rather than a rendered value; absent in the snapshot); malformed JSON/list/null/oversized bodies (controlled errors expose parser or attribute details, followed by successful valid requests). These are separately recorded nonblockers, not new normalization findings. [Exact inputs, fixtures and dispositions](contract/HISTORY.md).

All **15 cost suites exited 0**. Their 11 historical dispositions remain **six FIXED / five NOT FIXED**. Residual cold/queued-map times are 9.539/9.519 s for 400 distinct `isa` pieces, 12.425/12.425 s for 4,000 U+FDFA characters, 17.681/17.670 s for 1,000 `isa` matches, and 8.725/8.697 s for joined-item rescans; the 1,000 punctuation-separated `x` test has a 1.364 s direct median. These completed under concurrent audit load and do not establish a commit-caused latency regression. All seven cost-suite lifecycles preserve the DB and close their ports. [Cost ledger](contract/cost/FINDINGS.md), [summary](contract/cost/summary.json).

The first full DB oracle hit its copied 600-second **audit harness** limit. The child was terminated and verified absent before one rerun with a 1,800-second allowance. The rerun completed the oracle in 326.865 seconds and all seven DB suites successfully; all nine UI/question suites also completed. The original timeout and retry are retained, not concealed or reported as an application timeout. [Retry record](contract/retry_note.json), [DB execution](contract/execution.json), [final contract summary](contract/summary.json).

## Standards axis

**Zero hard documented-standard violations identified.** The scoped diff is `git diff HEAD^...HEAD`, commit `c3040c184ad4da0fc638d61ab94d46501c61a11a`, parent `56eb3d6297f2878d008e5edd9eb5eade62a0841c`. No filesystem AGENTS.md or separate coding-style standard was found. The user's supplied evidence-backed review instructions and the round36 brief's no-tracked-edit/scratch-only requirements govern this audit. No unrelated tracker setup or invented style rule was imposed.

The diff preserves parameterized SQL, live-node filtering and page escaping. The new helpers operate on existing strings and introduce no source-data writes, network access or model calls. The map's read-only/no-model statement is `src/app.py:14`; inspected paths retain that behavior. Focused regression cases and comments accompany the changes. Normalization and boundary-condition defects belong to the independently reported Spec axis; passing this Standards check does not establish their correctness.

This audit changes no production code. The user's conditional KOA Studio/KhOpenApi comparison instruction for code repairs is therefore not triggered. Review artifacts, private fixture inputs and temporary files remain under `audit_evidence_claims/m36/`; production integrity is checked separately by hashes. README.md:595 and README.ko.md:404 both state364 tests, matching the requested suite count.

## Spec axis

The exact M35 sign/mark/invisible examples close, but the specified composition is incomplete. The round-36 brief requires a group “with no letters or digits” containing a sign to retain its rotation value. `_SIGN_GROUP` excludes underscore through `\w`; the later punctuation filter therefore erases the negative descriptor in `(-_)-ARTEMISININ`, drawing CHEMBL269671. That is the positive source identity, as supported by its source alias and independent references above. This violates the round-32 approval bar for the whole input naming the drawn node.

The retained `Engine.explore` contract says “every other letter, digit and symbol must match.” `_sign` instead replaces the entire group, including unrelated significant symbols. `(+/☢-)NICOTINE` draws CHEMBL440464 exactly as `(+/-)NICOTINE`. The broadly worded new descriptor prose is in tension with this inherited guarantee; the code follows that broad reduction but fails the retained symbol-preservation requirement. Treat this as a separate significant-symbol loss, not another spelling of the underscore defect.

No unrelated scope expansion or new data misassignment was established in this lane. Passing source membership and refusal sweeps establish behavior for their enumerated inputs; they cannot establish that `_sig` implements the independent composition contract.

Axes remain separate: **Standards: zero hard violations. Spec: two map blockers; a question-only regression is recorded separately.**

## Integrity and limits

All **7,837 checked files**, comprising the tracked-file baseline plus the processed database and resolved dictionary, retain their pre-test SHA-256 values: **zero changed, zero added to the tracked baseline**, tracked git status empty, HEAD unchanged. All scratch files, temporary files and this report are confined to m36. No production repair, source curation, model invocation or external publication occurred. [Initial hashes](integrity_before.json), [final integrity](integrity_final.json).

Root stopped its owned CLI on port 8936 after the replay and question lanes finished using it. All **33 owned/tested ports** are closed: root 8936, contract 9600/9601/9602/9610/9611, and the 27 replay ports. [Root process lifecycle](server_lifecycle.json), [contract lifecycle](contract/summary.json), [replay lifecycle](replay/execution_summary.json), [final link/port validation](report_validation.json).

Opera's connector reported that no browser was connected. Page evidence therefore executes the actual served JavaScript in Node VM DOM/fetch harnesses, including forms, demo callbacks, generated markup and real HTTP click-through. It proves those application behaviors, **not browser painting or layout**. [Browser availability](browser_availability.json), [page assertions](contract/ui_assertions.json).

The source-oracle encoding correction, initial DB audit timeout/retry, and full-suite subprocess-decoding warning are disclosed above with their retained evidence. None is counted as a production defect or silently omitted from the validation account. Passing checks are bounded to the tested inputs and fixtures; no universal free-text refusal, resolver-list correctness, or scientific identity certification is claimed.

The positive checks do not negate M36-B1 or M36-B2. Membership measured only with the implementation's own `_sig` can accept its erroneous equivalence classes. This review separately checks descriptor/punctuation composition and preservation of significant symbols, then confirms the resulting counterexamples through the actual HTTP server.

VERDICT: CHANGES REQUIRED
