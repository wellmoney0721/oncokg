# Independent relation-map review — round 34

Reviewed **HEAD `1f6017e8ae7923d21cfafca64b1285331e0d2c18`**, parent `db1580d758062e6a4948056dc87fa42b2a04bc21`, on 2026-11-04. **CHANGES REQUIRED: one code blocker.** The original round-33 and round-32 blocker reproductions are closed, but the new refusal check omits stored aliases removed from the lookup index. `Cabozantinib (s)-malate` is refused, while `cabozantinibsmalate` and even `Cabozantinib (s)-malate?` draw its node under the same `_sig`. This violates the explicit requirement that every matching refused stored name remains refused. Separate nonblocking findings concern question recall, chemical punctuation equivalence and source metadata.

The scope is section 0, `POST /api/explore`, and `Engine.explore`, using the round-34 preferred-name policy and [round-32 approval bar](../m32/brief.md). The prior report and repair notes were reviewed. A FIXED disposition closes the exact reproduction under this policy; it does not mean that upstream records were curated or excluded aliases regained recall. No tracked file was edited.

## Verification and evidence

- Ran **`python -m pytest tests -q -p no:cacheprovider`**: **362 passed in 94.65 seconds**, exit 0. Bytecode was disabled; pytest/process temporary paths were under m34. [Output](pytest.txt), [command and timing](pytest_meta.json).
- Started **`python src/app.py 8934`** and exercised the actual HTTP routes. Root independently captured **124 baseline requests plus 36 supplementary requests**. Empty and 501-character map inputs returned the expected HTTP 400; the remaining baseline requests succeeded. Served HTML equals `web/try.html` byte for byte. [Raw baseline](root_http.json), [summary](root_confirmation.json), [supplement](root_supplement_http.json). Other lanes have additional HTTP captures.
- Replayed **4,660 distinct historical/current inputs**: 295 centers, 1,425 refusals, 2,556 `alias_only`, 321 `not_one_name`, 59 `not_found`, four choices. Independent read-name/id membership, ambiguity and choice-set checks found **zero violations and zero exceptions**. [Summary](replay/corpus_summary.json), [all results](replay/corpus_results.json).
- Independently rebuilt the source universe and exercised **14,639 distinct names/keys**: 8,061 centers, 6,407 `alias_only`, 164 refusals, four choices, three not-found replies, **zero membership/ambiguity/refusal invariant failures**. All 1,066 drug node labels and indexed preferred names agree with the dictionary's preferred names. This checks recorded membership, not the scientific identity of every possible spelling. [Summary](attacks/source_summary.json), [results](attacks/source_sweep.json), [records](attacks/all_source_records.json).
- Tested **164 refused stored names × 13 forms = 2,132 inputs**: all refused. Tested **1,066 drug preferred names × six significant suffixes = 6,396 inputs**: none drew. The original M33 matrix independently passed **456/456 HTTP refusals**. [Refusal sweep](attacks/refusal_variants_summary.json), [significant suffixes](attacks/significant_suffixes_summary.json), [original matrix](replay/m33_brand_variants_http.json).
- Fullwidth letters, U+200B/U+FEFF, combining accents and trademark forms were exercised. U+034F/U+FE0F remain significant and fail closed. Private ambiguity-retirement fixtures cover **54 exact cases / 10 assertion groups**: both live → choose, one retired → the remaining live node, all retired → not-found, including lower-case retired IDs and no retired-Roche fallback to folic acid. [Unicode HTTP](attacks/http_attack_reproductions.json), [private fixture](attacks/retired_private_fixture.json).
- Checked **all 6,469 live centers**, covering **22 relation/direction/type/role combinations**, against an independent SQLite oracle: **zero errors**. **19/19 DB assertions** and **26/26 UI assertions** pass. [DB oracle](contract/db_validate.json), [DB assertions](contract/db_assertions.json), [UI assertions](contract/ui_assertions.json).
- Executed the actual served JavaScript in a Node VM DOM/fetch harness, including real HTTP choice clicks, demos, `alias_only`, escaping and history. **No browser rendering result is claimed:** Opera reported no connected browser; two CUA inventory attempts timed out. [Availability record](browser_availability.json), [UI execution](contract/ui_harness_results.json).

The first source oracle intentionally covered `dictionary.index` plus node labels/keys. Its zero failures are valid for that universe but do not cover every spelling in `dictionary.drugs[...].aliases`. An independent final review challenged that assumption. The expanded omitted-alias scan found the blocker below; nine additional root HTTP requests corroborated it. Structural membership passes must not be read as proof of full stored-refusal consistency.

## Code blocker

### M34-B1 — a refused stored alias omitted from the index escapes the refusal closure

The exact stored alias **`Cabozantinib (s)-malate`** is present in `data/processed/resolved.json:1` at **`dictionary.drugs.CHEMBL2103868.aliases[2]`**, with `type: "synonym"`, `source: "ChEMBL"`. Its raw provenance is `data/raw/drugs.json:1`, **`data[563].drug.synonyms[1].label`**. The canonical index keeps only the preferred spelling **`CABOZANTINIB S-MALATE`** for this drug/key. `src/normalize.py:165-171` retains the synonym in the drug's alias list but admits only the first same-drug entry into the index.

`Engine.__init__` at **`src/app.py:61-65`** builds both name tables only from that index. Consequently the stored-spelling check at **`src/app.py:149-154`** never asks the linker about the omitted alias. The ordinary input check still refuses its exact spelling, but other spellings reach the preferred-name admission path.

| Exact HTTP input | Current result |
|---|---|
| `Cabozantinib (s)-malate` | `refused`, label `Cabozantinib -malate`, reason `names a distinct product or tracer, not the originator molecule` |
| `cabozantinibsmalate` | **center CHEMBL2103868 — CABOZANTINIB S-MALATE** |
| `CABOZANTINIB S-MALATE` | **same center** |
| `Cabozantinib (s)-malate?` | **same center** |
| `C a b o z a n t i n i b   ( s ) - m a l a t e` | **same center** |
| `Cabozantinib/(s)-malate` | **same center** |
| `Cabozantinib\u200b(s)-malate` (actual U+200B, not literal backslash text) | **same center** |

Every name in the table has `_sig == "cabozantinibsmalate"`. The correct literal trademark control `Cabozantinib (s)-malate™` remains refused, and direct ID `CHEMBL2103868` draws the requested ID as allowed. [Independent full HTTP/source confirmation, exact code points](root_blocker_confirmation.json), [initial independent discovery](contract/omitted_raw_refusals.json), [full omitted-alias scan](attacks/omitted_alias_refusal_summary.json), [all follow-up probes](attacks/omitted_alias_refusal_probes.json).

The full supplement examines **1,652 omitted alias occurrences / 1,376 unique spellings**. Eighteen omitted spellings are linker-refused; six have an indexed equivalent. Of 48 targeted variants, five draw, all in this one Cabozantinib failure family; the root's additional question-mark variant also draws. These counts are not separate blockers. The initial discovery's question-mark input is recorded literally; no converted trademark is misreported as a trademark bypass.

This is a **code/spec consistency failure**, not a claim that the salt name is a different chemical product or that this linker refusal is scientifically correct. The brief's rule is unconditional for stored refused names, and no Cabozantinib exception appears in the recorded exclusions. Repair the refusal-equivalence source so it includes all stored alias spellings, including canonical duplicates omitted from the lookup index, while preserving preferred-name-only admission. No production repair was made.

## Round-33 dispositions

Every row below has fresh exact-input HTTP evidence, Unicode code points and source records in [m33_exact_http.json](replay/m33_exact_http.json). Root independently corroborated the principal cases.

| Finding | Disposition | Exact inputs and current result |
|---|---|---|
| M33-B1 | **FIXED** | `Myocet`, `Myocet™`, `My/o/cet`, `My ocet`, `Inflectra`, `Inf/lectra`, `Equidacent`, `Equi/dacent`, `Fyarro`, `Fy/arro`, `Megace ES`, `Megace/ES` all return `refused`. All 456 original forms refuse. |
| M33-D1 | **FIXED for the map** | `Oraqix` → `refused`; no LIDOCAINE center. |
| M33-D2 | **FIXED for the map** | `Actikerall` → `refused`; no FLUOROURACIL center. |
| M33-D3 | **FIXED for the map** | `Betnesol-n` → `refused`; no BETAMETHASONE SODIUM PHOSPHATE center. |
| M33-D4 | **FIXED for the map** | `Maxitrol` → `refused`; no DEXAMETHASONE center. |
| M33-D5 | **FIXED for the map** | `Cipro HC` → `refused`; no HYDROCORTISONE center. |
| M33-D6 | **FIXED for the map** | `Tobradex` → `refused`; no DEXAMETHASONE center. |
| M33-S1 | **FIXED wrong-record reproduction** | `What trials evaluate (+/-)NICOTINE?` and `What does (+/-)NICOTINE target?` now have no linked entity/evidence in the question APIs; the map returns `not_found`. Bare `(+/-)NICOTINE` still draws CHEMBL440464. This is repaired by abstention, not restored sentence recall. |
| M33-S2 | **FIXED classification under the revised policy** | `Darzalex`, `Tepezza`, `Tevimbra`, `Winrevair`, `Privigen`, `Lmx 4` all return `alias_only`. Trade-name recall intentionally remains unavailable; the former distinction between permitted trade names and excluded synonyms no longer applies. |

The implementation now constructs admitted/alias indexes at `src/app.py:59-69`, filters live candidates at `src/app.py:134-146`, and checks indexed equivalent spellings before admission at `src/app.py:147-154`. The old source-specific replies have been replaced by `alias_only`. The six combination products and `PRED-G`, `NEO-DELTA-CORTEF`, `LEP-ETU` also refuse in the question controls. **M33-B1's original variants are FIXED, but M34-B1 demonstrates that its broader refusal-consistency family is not fully closed.**

## Round-32 dispositions

[All exact requests and matching source records](replay/m32_exact_http.json); [expanded current table](replay/recent_findings.md).

| Finding | Disposition | Exact inputs and current result |
|---|---|---|
| M32-B1 | **FIXED** | `trastu+zumab`, `trastu$zumab`, `trastu=zumab`, `trastuzumabß`, `trastuzumabø`, `trastuzumabæ`, `trastuzumabł`, `trastuzumabð`, `trastuzumabı` → `not_one_name`. |
| M32-B2 | **FIXED** | `AstraZeneca +`, `Pfizer$`, `Pfi+zer`, `Roche $` → `not_one_name`; `Merck + Co` → `not_found`. `Merck & Co` draws ORG:merckco. |
| M32-B3 | **FIXED** | `ABT-510` / `ABT 510` both choose CHEMBL262489 and CHEMBL386115. `FLUDEOXYGLUCOSE F 18` / `FLUDEOXYGLUCOSE-F18` both choose CHEMBL2030434 and CHEMBL497613. `MAGE-A3` / `MAGEA3` draw ENSG00000221867; `ctla-4` / `CTLA4` draw ENSG00000163599. |
| M32-B4 | **FIXED identity mismatch** | `Tarceva`, `Tarceva®`, `Tarceva™`, `Tarceva©`, `Tarceva℠` all return `alias_only`; no spelling chooses a different drug. |
| M32-D1 | **FIXED for the map** | `bupivacaine hydrochloride` → `alias_only`. |
| M32-D2 | **FIXED for the map** | `irinotecan liposome`, `irinotecan liposome injection`, `nanoliposomal irinotecan`, `doxorubicin hydrochloride liposome` → `alias_only`. |
| M32-D3 | **FIXED for the map** | `ropeginterferon alfa-2b` → `alias_only`. |
| Inherited NICOTINE question recall | **FIXED** | `What trials evaluate NICOTINE?` links CHEMBL3 and returns two evidence rows through each question API; the whole question remains undrawn by the map. |
| Greek stored-name recall | **NOT FIXED; intentional exclusion** | `thymosin α1`, `ifn-α-2b`, `interferon α-2b` → `alias_only`. |
| Trademark recall | **FIXED** | `trastuzumab™` → CHEMBL1201585; `AstraZeneca™` → ORG:astrazeneca. |
| Blank-input view retention | **NOT FIXED; inherited nonblocker** | Submit `""` or whitespace after a valid map: no request, previous map retained. [Callbacks](contract/ui_m3_checks.json). |
| Nonfinite numeric fixture | **NOT FIXED; fail-closed qualification** | Private stored `+Infinity` / `-Infinity` produce controlled HTTP 400, never an invalid numeric map value; absent from the snapshot. [Fixture](contract/db_numeric_fixture.json). |
| Malformed-body disclosure | **NOT FIXED; inherited nonblocker** | Malformed JSON, list/null bodies and oversized bodies return 400 with parser/attribute error details; subsequent valid input recovers. [Exact bodies and replies](contract/server_checks.json). |
| Historical cost findings | **Mixed; individually marked** | Retained workloads and exact repeat counts are listed in [cost/FINDINGS.md](contract/cost/FINDINGS.md); successful completion is distinguished from remaining lock delay. |

The waived historical `13-cis retinoic acid`, `BAT1706`, `BI 695502`, `FKB238`, `HLX-04`, `HLX04-O`, and development-code/brand synonyms now remain undrawn. `Roche` draws only ORG:roche because its folic-acid trade-name record is excluded. `Kadcyla` is now `alias_only`; `trastuzumab emtansine` and its ID still draw the corresponding drug.

## New code/design should-fix findings

### M34-S1 — ordinary parentheses or brackets suppress a valid question name

**New, nonblocking question recall regression.** `src/query.py:896-898` excludes parentheses and brackets on either side of a shared-key preferred name. Parent/current comparison and real HTTP show:

| Exact input | Parent | HEAD |
|---|---|---|
| `What trials evaluate (NICOTINE)?` | CHEMBL3, two evidence rows | No entity, zero evidence |
| `What does (NICOTINE) target?` | CHEMBL3, two evidence rows | No entity, zero evidence |
| `What trials evaluate [NICOTINE]?` | CHEMBL3, two evidence rows | No entity, zero evidence |

All three question APIs show the loss. Unwrapped `What trials evaluate NICOTINE?` still returns two rows; `What trials evaluate (osimertinib)?` still returns 12. A stereochemical prefix attached to a name and punctuation enclosing a name need different treatment. The map correctly leaves these full questions undrawn, so this does not fail the map approval bar. [Parent/current evidence and 45 HTTP calls](contract/boundary_question_comparison.json), [root HTTP corroboration](root_supplement_http.json).

### M34-S2 — the agreed punctuation equivalence can erase stereochemistry

**Nonblocking limitation of the specified `_sig` design, not a newly misfiled alias.** Exact `(+)-NICOTINE` and `(+)NICOTINE` draw **CHEMBL440464, `(+/-)NICOTINE`**. The stored preferred-name record and node label are `(+/-)NICOTINE`; the input is admitted because `_sig` at `src/app.py:261-272` drops the slash and hyphen while retaining `+`, giving `+nicotine` for all three strings. The linker itself returns no entity for the positive-enantiomer forms. [Source record, signatures and HTTP](attacks/stereochemical_punctuation_http.json), [independent root HTTP](root_supplement_http.json).

This is a real chemical distinction: ChEBI identifies `(+)-nicotine` as the R enantiomer, whereas its racemate record contains equal R and S amounts. [ChEBI R-nicotine](https://www.ebi.ac.uk/chebi/CHEBI:39162), [ChEBI racemate](https://www.ebi.ac.uk/chebi/CHEBI:18723). The review does **not** interpret signature equality as chemical equivalence. This review classifies it as nonblocking under the literal `_sig` admission criterion: these inputs satisfy the stated punctuation equivalence and are not linker-refused names. That is a scope judgment, **not an explicitly recorded stereochemistry exception**. A stronger medicinal-identity guarantee would require changing that comparison policy, preserving stereochemical notation or refusing such normalized matches.

## Data findings, separate from code

### M34-D1 — THEOPHYLLINE is incorrectly typed as Protein upstream

**Nonblocking source metadata error.** Exact input `THEOPHYLLINE` / `Theophylline` draws CHEMBL1355736 with `props.drug_type: "Protein"`. Its raw source is **`data/raw/drugs.json:1`, `data[191].drug`**, containing `id: "CHEMBL1355736"`, `name: "THEOPHYLLINE"`, `drugType: "Protein"`. `data/processed/resolved.json:1`, `dictionary.drugs["CHEMBL1355736"].drug_type`, and the node properties preserve that value. ChEBI independently identifies theophylline as dimethylxanthine, formula C7H8N4O2. [ChEBI identity](https://www.ebi.ac.uk/chebi/CHEBI:28177).

The map reproduces the stored value faithfully, and no contrary molecular identity of the named node was established. Therefore this is a curation issue, not a stored-value transcription failure or a wrong-product identity blocker. [Complete source record and response](attacks/theophylline_metadata.json), [HTTP confirmation](attacks/http_attack_reproductions.json).

### Previously proven data errors remain stored, but no longer draw

The following references were reopened during this review. Exact current records, JSON pointers and responses are preserved in [known_data_records.json](known_data_records.json). M33 rows are `trade_name` records with normalized `source: null` in `dictionary.index[<key>]`; raw trade-name provenance is documented in the [prior raw-source capture](../m33/attacks/trade_name_raw_provenance.json). M32 rows are AACT synonyms. Blocking map reproductions are FIXED; upstream data curation is **not** claimed.

| Finding / exact input | Source key → filed-under record | Independent identity reference |
|---|---|---|
| M33-D1 `Oraqix` | `oraqix` → CHEMBL79 LIDOCAINE | Lidocaine **and prilocaine**. [DailyMed](https://dailymed.nlm.nih.gov/dailymed/lookup.cfm?setid=b501d239-923b-48b2-82ed-6c5c253a67e2). |
| M33-D2 `Actikerall` | `actikerall` → CHEMBL185 FLUOROURACIL | Fluorouracil **and salicylic acid**. [Manufacturer SmPC](https://www.medicines.org.uk/emc/product/4621/smpc). |
| M33-D3 `Betnesol-n` | `betnesoln` → CHEMBL1200762 BETAMETHASONE SODIUM PHOSPHATE | Betamethasone sodium phosphate **and neomycin sulfate**. [HPRA](https://www.hpra.ie/find-a-medicine/for-human-use/authorised-medicines/details/28877). |
| M33-D4 `Maxitrol` | `maxitrol` → CHEMBL384467 DEXAMETHASONE | Dexamethasone, **neomycin and polymyxin B**. [DailyMed](https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=5776c435-ac60-49b6-8db1-23a3012b9155). |
| M33-D5 `Cipro HC` (stored `Cipro hc`) | `ciprohc` → CHEMBL389621 HYDROCORTISONE | Hydrocortisone **and ciprofloxacin hydrochloride**. [DailyMed](https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=6b318e8c-ce91-41ce-9f35-fc9861cd9474). |
| M33-D6 `Tobradex` | `tobradex` → CHEMBL384467 DEXAMETHASONE | Dexamethasone **and tobramycin**. [DailyMed](https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=2a2259ee-05e4-4785-ba75-5946132debf3). |
| M32-D1 `bupivacaine hydrochloride` | `bupivacainehydrochloride` → CHEMBL4297652 ANTIMONY | An amide local anesthetic. [NCI](https://www.cancer.gov/publications/dictionaries/cancer-drug/def/bupivacaine-hydrochloride). |
| M32-D2 `irinotecan liposome`, `irinotecan liposome injection`, `nanoliposomal irinotecan` | Corresponding canonical keys → CHEMBL481 IRINOTECAN | Liposomal formulation. [Onivyde label](https://dailymed.nlm.nih.gov/dailymed/fda/fdaDrugXsl.cfm?setid=c8b58efa-1820-48a4-b70d-62918fc4abfc). |
| M32-D2 `doxorubicin hydrochloride liposome` | `doxorubicinhydrochlorideliposome` → CHEMBL359744 DOXORUBICIN HYDROCHLORIDE | Liposomal formulation. [NCI](https://www.cancer.gov/about-cancer/treatment/drugs/doxorubicin-hydrochloride-liposome). |
| M32-D3 `ropeginterferon alfa-2b` | `ropeginterferonalfa2b` → CHEMBL1201558 INTERFERON ALFA-2B | PEG-conjugated interferon. [NCI](https://www.cancer.gov/publications/dictionaries/cancer-drug/def/ropeginterferon-alfa-2b). |

No additional exact admitted preferred name or node label was proved to denote a different product from its node. This is a bounded search result, not a certification of all source identities. The source sweep also found **1,652 raw alias occurrences whose spelling is absent from the index**, including **427 occurrences / 247 signatures absent entirely**. These absent-signature cases produced 356 `not_found`, 59 `not_one_name`, 12 refusals and no centers. Many are intentional upstream curation; these are **not 247 proven data defects**. The implementation's indexed-only interpretation of “every stored name” is incomplete: omitted spellings sharing an admitted signature produce M34-B1. [Discrepancies](attacks/source_discrepancies.json), [absent-signature responses](attacks/absent_alias_signatures.json).

## Question boxes and demos

The **99-shared-key / 708-case** parent/current comparison contains only two changes, both intended abstentions for M33-S1. The supplementary punctuation tests expose M34-S1 outside that older corpus. **All 36 shipped demo results are unchanged** with parent/current query.py and match current HTTP: 13 resolver, seven ask, nine prose-check, seven structured-check examples. Actual form/example callbacks execute without UI errors. **47 product keys/names**, bare and in two question wrappers, all refuse; **141 question-box HTTP calls** return no evidence. This includes the nine newly listed product names. [Shared keys](contract/shared_key_question_comparison.json), [demos](contract/demo_previous_comparison.json), [callbacks](contract/ui_m3_checks.json), [products](contract/product_questions.json).

## Original guarantees A–G

| Check | Conclusion and evidence |
|---|---|
| A — relations/directions | **PASS**: 6,469-center oracle, 22 combinations; private self-loop, unknown relation/type and sponsor-role fixtures pass. [Oracle](contract/db_validate.json), [fixture](contract/self_loop_unknown.json). |
| B — names/IDs/retirement | **FAIL: M34-B1**, omitted refused stored aliases can draw under equivalent spellings. Indexed-name membership, significant-symbol checks, lowercase IDs, choice sets and retired-node filtering otherwise pass the exercised cases. M34-S2's separate chemical limitation remains. [Blocker](root_blocker_confirmation.json), [source sweep](attacks/source_sweep.json), [choice lifecycle](contract/choose_lifecycle.json), [retirement](contract/db_retired_center.json). |
| C — stored values/live counts | **PASS**: 19 assertions, exact scores, missing versus zero, malformed properties and 1,001-drug chunking. Infinity fails closed. M34-D1 is erroneous source metadata, faithfully copied. [Assertions](contract/db_assertions.json). |
| D — ordering/cuts | **PASS**: stored weights, ties, group ordering, true totals and visible list/ring cuts. [DB oracle](contract/db_validate.json), [UI](contract/ui_harness_results.json). |
| E — markup/state | **PASS in the executed JavaScript harness**: `choose` IDs/text and `alias_only` content are escaped, choice clicks work, terminal states clear trails, stale replies/errors cannot overwrite newer state, malformed-render recovery passes. Browser paint/layout unverified. [Choices](contract/choose_ui.json), [new reply](contract/new_states.json), [regressions](contract/ui_regressions.json). |
| F — server | **PASS with inherited nonblockers**: controlled errors/recovery, 24 concurrent map calls and private retirement. Parser disclosure, blank view retention and long question lock costs remain. [HTTP](contract/server_checks.json), [cost ledger](contract/cost/FINDINGS.md). |
| G — docs/no writes/no model | **The universal stored-refusal claim is false because of M34-B1.** Preferred-name policy, new reply and README test count otherwise match current behavior. Scientific meaning is limited by M34-S2. Inspected routes read state and invoke no model. [Contract review](contract/FINDINGS.md), [bounded hashes](contract/post_checks.json), final integrity below. |

## Historical coverage and independent review axes

All **275 inherited naming finding rows** have current exact-case dispositions: **257 FIXED / 18 NOT FIXED overall**, **260 FIXED / 15 NOT FIXED for the map**. The 15 map rows are nine recorded over-refusal rows and six now-intentionally-excluded recall cohorts; three additional rows are question-only failures. **1,337 previous centers now intentionally return `alias_only`.** The change in recall is not mislabeled as a new wrong-node failure. [Counts](replay/matrix_summary.json), [all per-finding inputs/results](replay/per_finding_cases.json), [readable historical table](replay/historical_table.md).

All **123 copied original leaf jobs exited 0**, with 151 source/copy entries and 45 lifecycle records retained. The original **7,511-key alias sweep** and two **1,648-question historical/frozen replays** completed; each reports 1,648 identical / zero errors in its comparison. The separate historical no-relink adapter reports 72 identical, 1,552 entity-metadata-only and 24 semantic differences against its constructed old baseline; those are not HEAD-versus-parent regression counts. All 27 owned replay ports are closed. The missing original M22 generator remains covered by its saved exact 58-input adapter; the unavailable generator is not claimed to have run. [Execution summary](replay/execution_summary.json), [QA summary](replay/historical_qa_summary.json), [reuse and limitations](replay/FINDINGS.md).

All **23 historical DB/UI/server rows** were re-exercised: **20 FIXED / three NOT FIXED**, with exact fixtures/bodies in the linked artifacts. [Historical contract ledger](contract/HISTORY.md). **15 cost suites exited 0**; their 11 dispositions are six FIXED and five inherited residual costs. The 400-distinct-`isa`, 4,000-U+FDFA, punctuation-token, 1,000-`isa`, and joined-item workloads retain overhead/lock delay. No new timeout or wrong map was established. Seven cost-server lifecycles preserve DB hashes and close their ports. Timings overlap other audit work and are not evidence of a commit-caused performance regression. [Cost ledger](contract/cost/FINDINGS.md). Counts overlap across ledgers and are not added as independent findings. Old positive-map assertions are not substituted for the current admission contract.

**Standards axis:** zero hard documented-standard violations. The review follows the user's evidence and no-tracked-edit rules; parameterized SQL, live filtering and escaping are preserved. No unrelated tracker setup or style rule was imposed. [Separate Standards review](contract/FINDINGS.md#standards-axis-separate-from-spec).

**Spec axis: not satisfied.** M34-B1 violates the explicit universal stored-refusal requirement. Indexed membership, choice, live-value and markup checks pass within their tested scope. M34-S1 is a question-only recall regression; M34-S2 exposes a limitation of the explicitly prescribed signature rule. The data metadata error is separate. [Independent identity/spec review](attacks/findings.md).

## Integrity and limits

All **7,835 tracked files plus the processed SQLite database and resolved dictionary** match their pre-test SHA-256 baseline: **7,837 files checked, zero changed or added**, tracked git status clean, HEAD unchanged. Both root-owned CLI runs on port 8934 were stopped after their requests completed; all **31 checked owned ports** are closed. [Final integrity](integrity_final.json), [initial hashes](integrity_before.json), [server lifecycles](server_lifecycle.json). Scratch artifacts and this report are confined to m34. No production repair was made, so the user's code-change requirement concerning KOA Studio/KhOpenApi references does not arise.

Changes are required to close M34-B1's omitted-alias refusal gap. Passing tests, the original repaired examples and the indexed-name oracle do not discharge the broader stored-name guarantee. This review also does not certify question free-text refusal completeness, graph-construction brand assignments, upstream source correctness, or chemical equivalence of all punctuation-normalized names.

VERDICT: CHANGES REQUIRED
