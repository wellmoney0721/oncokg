# Independent relation-map review — round 37

Reviewed **HEAD `2b1aca18faeef72a5e090dbc3af4ba6151b4ae80`**, parent `c3040c184ad4da0fc638d61ab94d46501c61a11a`, on 2026-11-04. Comparison: `git diff HEAD^...HEAD`. The subject is section 0 of `web/try.html`, `POST /api/explore`, and `Engine.explore`, under the [round-32 approval bar](../m32/brief.md), [round-34 name policy](../m34/brief.md), and [round-37 amendment](brief.md).

**APPROVE within the specified relation-map scope. The exact M36-B1, M36-B2 and M36-S1 reproductions are FIXED.** Two question-only changes and incomplete user-facing documentation are recorded separately below. FIXED closes the exact reproduction under the current policy; it does not mean alias recall or upstream source curation has been restored. This is an independent review, with no production repair.

## Verification

- **`python -m pytest tests -q -p no:cacheprovider`: 365 passed in 194.37 seconds**, exit 0; wrapper elapsed 198.185 seconds. `PYTHONUTF8=1` and bytecode suppression were enabled, with temporary files confined to m37. The full run has no warnings. [Output](pytest.txt), [command and timing](pytest_meta.json).
- Started the actual CLI **`python src/app.py 8937`**. Root retained **327 HTTP response records**: 124 baseline, 85 exact/supplementary cases, 36 question/data follow-ups, 70 round-37 repair/mode cases, seven underscore confirmations and five documentation controls. These are retained records, not a count of all requests in every lane. The expected empty-input and 501-character baseline requests return HTTP 400. The served page equals `web/try.html` byte for byte. [Baseline](root_confirmation.json), [responses](root_http.json), [exact cases](root_exact_http.json), [follow-ups](root_supplement_http.json), [round-37 cases](root_round37_http.json), [seven underscores](underscore_http.json), [documentation controls](documentation_http.json).
- The independent historical/current corpus contains **4,703 distinct inputs**: 300 centers, 1,434 refusals, 2,555 `alias_only`, 337 `not_one_name`, 73 `not_found`, four choices. There are zero exceptions, independent admitted-name membership failures, silent ambiguous draws or wrong choice sets. Against all 4,689 inherited inputs, the only semantic change is `(±)-nicotine`: CHEMBL440464 → `not_found`, the explicitly accepted descriptor-spelling exclusion. [Summary](replay/corpus_summary.json), [responses](replay/corpus_results.json), [parent changes](replay/parent_corpus_changes.json).

## Round-36 repairs

Parent comparisons load **both parent `app.py` and parent `query.py`**, and current outcomes are separately confirmed through the CLI HTTP server. Unicode escapes below denote actual characters. [Reproducer](root_round37.py), [parent/current/HTTP evidence](root_round37_http.json), [compact results](root_round37_summary.json).

| Finding | Disposition | Exact inputs and current result |
|---|---|---|
| M36-B1 | **FIXED** | `(-_)-ARTEMISININ`, `(_-)-ARTEMISININ`, `[-_]-ARTEMISININ`, `"(-\u200b_\u0301)-ARTEMISININ"`, `"(-\uff3f)-ARTEMISININ"`, `"(-\ufe4d)-ARTEMISININ"`, `(-())-ARTEMISININ`, `〔-〕-ARTEMISININ`, `«-»-ARTEMISININ` all return `not_one_name`; parent draws CHEMBL269671. Each of the seven underscore characters U+005F, U+FE33, U+FE34, U+FE4D, U+FE4E, U+FE4F and U+FF3F inside `(-<character>)-ARTEMISININ` is separately confirmed undrawn over HTTP. |
| M36-B2 | **FIXED** | `(+/-☢)NICOTINE`, `(±☢)NICOTINE`, `(+/-$)NICOTINE`, `(+/-×)NICOTINE` return `not_one_name`; `(+/☢-)NICOTINE`, `(+/×-)NICOTINE` return `not_found`. All six previously drew CHEMBL440464. Significant symbols remain in the signature. |
| M36-S1 | **FIXED exact questions** | `What trials evaluate ((+/-))NICOTINE?` and `What does NICOTINE((+/-)) target?`: no linked entity and zero evidence in `/api/ask`, `/api/structured`, and `/api/check`; map `not_found`. Parent reads CHEMBL3 and retrieves two rows. |

Positive controls remain valid: `ARTEMISININ` and `CHEMBL269671` draw CHEMBL269671; `(+/-)NICOTINE`, `( + / - )NICOTINE`, `(+/–)NICOTINE`, `(+/-)nicotine`, fullwidth `（＋/－）NICOTINE`, and accented `(+/-)NÍCOTINE` draw CHEMBL440464. `(±)-nicotine`, `(+-)NICOTINE`, `(-+)-NICOTINE` and `()osimertinib` remain undrawn under the revised policy. [Controls](root_round37_summary.json).

## Independent attack on the two comparison modes

The oracle reconstructs names and candidate IDs from the dictionary and SQL records; it does not use `Engine.names`. Its normalization classifier is a separate character scanner rather than the implementation's `_GROUP` regular expression. [Oracle and source sweep](source/source_audit.py), [composition probes](source/modes.py), [boundary probes](source/mode_boundaries.py).

The critical separation is structural: a strict-mode signature retains at least one opening/initial-quotation and one closing/final-quotation punctuation character. An ordinary-mode signature removes all punctuation. Those signature spaces cannot collide. This argument depends on the promised preprocessing order: trademark removal, compatibility/case folding and mark/invisible removal precede classification; space removal and dash normalization cannot erase those retained delimiters. It supports mode separation, not universal chemical equivalence of ordinary punctuation-normalized names.

- **22,956 source/key inputs × 14 transforms = 321,384 comparisons.** Fourteen literal source spellings use strict mode; 22,942 use ordinary mode. No implementation-versus-independent-oracle mismatch was found. There are 42 mode-dependent punctuation-transform differences, which are expected under the new policy. Two additional generic `swapcase()` invariance probes differ for Turkish dotless `ı`; both agree with the prescribed casefold oracle. Those probe assumptions are not silently counted as passing or as new map defects. [Summary](source/source_mode_summary.json), [differences](source/source_mode_differences.json), [follow-up outcomes](source/mode_followup.json).
- **11,086 assigned punctuation/mark/symbol/space characters × four contexts = 44,344 cases**, plus all **91 opening × 87 closing delimiters = 7,917 pairs**: zero oracle failures or unsafe plain-ARTEMISININ collisions. [Unicode summary](source/unicode_mode_summary.json).
- **138,557 assigned Unicode letter/number characters** inserted into a candidate group: zero classifier disagreements. Sixteen lose their letter/number category during the specified compatibility/mark preprocessing and correctly change mode afterwards. [Classification results](source/letter_number_classification.json).
- Nested and mismatched brackets, Unicode quotations, empty groups, fullwidth forms, signs, unrelated symbols, letters/digits inside a group and preprocessing-created empty groups were exercised. **28 HTTP boundary controls** supplement root's confirmations. `(-ARTEMISININ)` and `(-A)RTEMISININ` have letters inside their only group and therefore use ordinary mode, drawing ARTEMISININ; ASCII apostrophes are category Po, not the designated Pi/Pf quotation delimiters. These results follow the explicit new classifier and inherited ordinary punctuation rule. They are disclosed design boundaries, not evidence that the code interprets arbitrary strings as optical descriptors. [Boundary evidence](source/mode_boundary_http.json).
- **182 literal refused spellings × 13 variants = 2,366, all refused.** A separate 84 synthetic canonical-only keys × 13 = 1,092 cases yield 1,074 refusals, 12 `alias_only`, six `not_found`, no centers. All **1,066 preferred names × six significant suffixes = 6,396** remain undrawn. **54 private retirement cases / ten assertion groups** pass. [Classified refusal results](source/refusal_variants_classified.json), [raw summary](source/refusal_variants_summary.json), [suffixes](source/significant_suffixes_summary.json), [retirement fixture](source/retired_private_fixture.json).

## New nonblocking findings

### M37-S1 — punctuation or a symbol can end the question descriptor scan before its sign

**Question-linker regression**, `src/query.py:118` and `src/query.py:133–135`. The parent accepted arbitrary nonword characters inside a sign group. The new adjacent run excludes punctuation such as `.` and symbols such as `☢` and `$`. Looking left from NICOTINE, the scan stops on that character before reaching the sign.

| Exact input | Parent question result | HEAD question result | HEAD map |
|---|---|---|---|
| `What trials evaluate (+/-.)NICOTINE?` | no entity/evidence | CHEMBL3; two evidence rows | `not_one_name` |
| `What trials evaluate (+/-☢)NICOTINE?` | no entity/evidence | CHEMBL3; two evidence rows | `not_one_name` |
| `What trials evaluate (+/-$)NICOTINE?` | no entity/evidence | CHEMBL3; two evidence rows | `not_one_name` |
| `What trials evaluate NICOTINE(.+/-)?` | no entity/evidence | CHEMBL3; two evidence rows | `not_one_name` |

The same new reading occurs with `×`, `:` and `,`, including mirrored suffix forms. The combined **28-question / 112-HTTP** probe has **12 newly admitted question readings** and no map centers. `/api/ask` and `/api/check` expose the entity; `/api/structured` retrieves the same two evidence rows. The opposite-side punctuation controls remain blocked because the scan meets a sign first. This is a loss of question refusal coverage, not a map admission failure; it is nonblocking under README defect 15 and the explicit review scope. [Prefix/suffix evidence](contract/question_punctuation_regression.json), [mirrored suffix evidence](contract/question_punctuation_mirror.json).

### M37-S2 — ordinary sign-separated lists lose a shared preferred name

**Question recall/design cost**, `src/query.py:133–135`. `What trials evaluate NICOTINE + osimertinib?` previously linked CHEMBL3 and CHEMBL3353410; now only CHEMBL3353410 remains. The selected evidence consequently changes from two NICOTINE rows to 12 osimertinib rows. `What trials evaluate osimertinib + NICOTINE?` and `What trials evaluate NICOTINE - osimertinib?` also drop NICOTINE. The `/` and `and` controls retain both entities.

This follows the requested rule that **any adjacent sign** blocks a shared-key preferred-name reading. It should be understood as a recall tradeoff, rather than claimed to violate that new rule. All such complete questions remain undrawn by the map. The expanded supplement tests **six names × 30 patterns × two wrappers = 360 cases**, with 74 parent-query changes and zero map centers; not all 74 changes are defects. [Supplement and parent comparison](contract/question_supplement.json), [summary](contract/question_supplement_summary.json), [embedded HTTP records](contract/question_supplement.json).

Previously existing free-text leaks are separate: `What trials evaluate 〔+/-〕NICOTINE?`, `What trials evaluate NICOTINE«+/-»?` and `"What trials evaluate (+/-)\u200bNICOTINE?"` still read CHEMBL3 with two evidence rows, identically to the parent. These remain recorded question-box limitations. Ordinary `(NICOTINE)` recall and the exact M36 nested-descriptor repair pass.

### M37-S3 — page and explore documentation omit the new punctuation exception

**Documentation should-fix**, `web/try.html:54` and `src/app.py:110–115`. Their unqualified claim that punctuation is ignored no longer describes every name. The new `_sig` docstring explains the exception, but the visible page does not. For example, `(+/-)NICOTINE` draws while `(+/-)NICO/TINE`, `(+/-)NICOTINE!`, or bracket changes do not; `()osimertinib` is also undrawn. Explain that a bracketed group without letters/digits switches the whole name to literal-punctuation comparison. These are accepted recall exclusions, so the wording issue does not negate the map safety result. [Exact HTTP controls](documentation_http.json).

## Data problems, separate from code

**M34-D1 remains NOT FIXED, recorded nonblocker.** `THEOPHYLLINE` / `Theophylline` draws CHEMBL1355736 with stored `drug_type: "Protein"`. Raw source: `data/raw/drugs.json:1`, `data[191].drug.drugType`; dictionary: `data/processed/resolved.json:1`, `dictionary.drugs.CHEMBL1355736.drug_type`. The map faithfully copies it. ChEBI identifies theophylline as dimethylxanthine. [Current source records](focused_source_records.json), [HTTP](root_exact_http.json), [independent identity](https://www.ebi.ac.uk/chebi/CHEBI:28177).

The previously identified wrong-product aliases also remain stored. Their **map reproductions are FIXED**, but **upstream curation is NOT FIXED**. The current source records, exact occurrence pointers and map responses are retained in [known_data_records.json](known_data_records.json). All external references below were reopened during this review. [Reference ledger](reference_verification.json).

| Exact input / finding | Source record in `dictionary.index` → filed-under node | Independent identity |
|---|---|---|
| `Oraqix` / M33-D1 | `oraqix` → CHEMBL79 LIDOCAINE | Lidocaine and prilocaine. [DailyMed](https://dailymed.nlm.nih.gov/dailymed/lookup.cfm?setid=b501d239-923b-48b2-82ed-6c5c253a67e2). |
| `Actikerall` / M33-D2 | `actikerall` → CHEMBL185 FLUOROURACIL | Fluorouracil and salicylic acid. [Manufacturer SmPC](https://www.medicines.org.uk/emc/product/4621/smpc). |
| `Betnesol-n` / M33-D3 | `betnesoln` → CHEMBL1200762 BETAMETHASONE SODIUM PHOSPHATE | Also contains neomycin sulfate. [HPRA](https://www.hpra.ie/find-a-medicine/for-human-use/authorised-medicines/details/28877). |
| `Maxitrol` / M33-D4 | `maxitrol` → CHEMBL384467 DEXAMETHASONE | Also contains neomycin and polymyxin B. [DailyMed](https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=5776c435-ac60-49b6-8db1-23a3012b9155). |
| `Cipro HC` / M33-D5 | `ciprohc` → CHEMBL389621 HYDROCORTISONE | Also contains ciprofloxacin hydrochloride. [DailyMed](https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=6b318e8c-ce91-41ce-9f35-fc9861cd9474). |
| `Tobradex` / M33-D6 | `tobradex` → CHEMBL384467 DEXAMETHASONE | Also contains tobramycin. [DailyMed](https://dailymed.nlm.nih.gov/dailymed/drugInfo.cfm?setid=2a2259ee-05e4-4785-ba75-5946132debf3). |
| `bupivacaine hydrochloride` / M32-D1 | `bupivacainehydrochloride` → CHEMBL4297652 ANTIMONY | Amide local anesthetic. [NCI](https://www.cancer.gov/publications/dictionaries/cancer-drug/def/bupivacaine-hydrochloride). |
| `irinotecan liposome`, `irinotecan liposome injection`, `nanoliposomal irinotecan` / M32-D2 | Corresponding canonical keys → CHEMBL481 IRINOTECAN | Liposomal irinotecan formulation. [Onivyde label](https://dailymed.nlm.nih.gov/dailymed/fda/fdaDrugXsl.cfm?setid=c8b58efa-1820-48a4-b70d-62918fc4abfc). |
| `doxorubicin hydrochloride liposome` / M32-D2 | `doxorubicinhydrochlorideliposome` → CHEMBL359744 DOXORUBICIN HYDROCHLORIDE | Liposomal formulation. [NCI](https://www.cancer.gov/about-cancer/treatment/drugs/doxorubicin-hydrochloride-liposome). |
| `ropeginterferon alfa-2b` / M32-D3 | `ropeginterferonalfa2b` → CHEMBL1201558 INTERFERON ALFA-2B | PEG-conjugated interferon. [NCI](https://www.cancer.gov/publications/dictionaries/cancer-drug/def/ropeginterferon-alfa-2b). |

Those pointers refer to `data/processed/resolved.json:1`; M33 entries are trade names and M32 entries are AACT synonyms. No newly admitted preferred name, node label, symbol or key was independently proved to denote a different product from the drawn node. This is a bounded review result, not scientific certification of every source identity.


## Expanded source universe

The fresh sweep covers **22,956 distinct source/key inputs from 34,429 records**, including **all 9,581 `dictionary.drugs[*].aliases` entries**, drug preferred names, index spellings and keys, SQL node labels, target symbols, and company/disease keys. It includes **16,015 literal source spellings/read keys and 6,941 additional canonical-only index strings**, against 6,469 live nodes.

Results: **10,088 centers, 12,486 `alias_only`, 354 refused, eight choices, five `not_found`, 15 `not_one_name`**. Independent membership, stored-refusal, silent-ambiguity and live-choice assertions have **zero failures and zero exceptions**. The sweep completed in **947.748 seconds**. All 1,696 dictionary alias occurrences omitted from the lookup index were included in the source inventory. [Source inventory and pointers](source/all_source_records.json), [responses](source/source_sweep.json), [assertions/counts](source/source_summary.json), [source classes](source/source_classified_summary.json), [index omissions](source/source_discrepancies.json).

There are **zero response changes against the saved M36 source results**. This is fresh HEAD execution compared with saved prior responses, not a newly rerun parent Engine sweep. The historical corpus comparison uses the same saved-prior-results distinction; the focused repair and question regression comparisons separately execute parent code. The complete source inventory and the independently specified mode oracle are both needed: matching the implementation's own signatures alone would not have detected the normalization faults in previous rounds. [Comparison](source/source_parent_changes.json), [source findings and limitations](source/findings.md).

## Exact round-32 through round-35 dispositions

Every original naming finding has fresh exact-input outcomes in the table below and its raw HTTP artifacts. **124 recent map cases**, all their question follow-ups, and the original **456/456 brand refusal variants** were rerun. FIXED refers to map exposure or the exact stated question behavior, not repair of the underlying alias data. The accepted Greek-alias recall exclusions and THEOPHYLLINE metadata remain NOT FIXED. [M32 requests](replay/m32_exact_http.json), [M33 requests](replay/m33_exact_http.json), [M34 requests](replay/m34_exact_http.json), [M35 requests](replay/m35_exact_http.json), [brand variants](replay/m33_brand_variants_http.json), [readable exact ledger](replay/recent_findings.md).


| Finding | Disposition | Exact inputs and fresh outcome |
|---|---|---|
| M32-B1 | **FIXED under current map/name policy** | `"trastu+zumab"` -> not_one_name<br>`"trastu$zumab"` -> not_one_name<br>`"trastu=zumab"` -> not_one_name<br>`"trastuzumab\u00df"` -> not_one_name<br>`"trastuzumab\u00f8"` -> not_one_name<br>`"trastuzumab\u00e6"` -> not_one_name<br>`"trastuzumab\u0142"` -> not_one_name<br>`"trastuzumab\u00f0"` -> not_one_name<br>`"trastuzumab\u0131"` -> not_one_name |
| M32-B2 | **FIXED under current map/name policy** | `"AstraZeneca +"` -> not_one_name<br>`"Merck + Co"` -> not_found<br>`"Pfizer$"` -> not_one_name<br>`"Pfi+zer"` -> not_one_name<br>`"Roche $"` -> not_one_name |
| M32-B3 | **FIXED under current map/name policy** | `"ABT-510"` -> choose CHEMBL262489,CHEMBL386115<br>`"ABT 510"` -> choose CHEMBL262489,CHEMBL386115<br>`"MAGE-A3"` -> center ENSG00000221867<br>`"MAGEA3"` -> center ENSG00000221867<br>`"ctla-4"` -> center ENSG00000163599<br>`"CTLA4"` -> center ENSG00000163599<br>`"FLUDEOXYGLUCOSE F 18"` -> choose CHEMBL2030434,CHEMBL497613<br>`"FLUDEOXYGLUCOSE-F18"` -> choose CHEMBL2030434,CHEMBL497613 |
| M32-B4 | **FIXED under current map/name policy** | `"Tarceva"` -> alias_only<br>`"Tarceva\u00ae"` -> alias_only<br>`"Tarceva\u2122"` -> alias_only<br>`"Tarceva\u2120"` -> alias_only |
| M32-D1 | **FIXED under current map/name policy** | `"bupivacaine hydrochloride"` -> alias_only |
| M32-D2 | **FIXED under current map/name policy** | `"irinotecan liposome"` -> alias_only<br>`"irinotecan liposome injection"` -> alias_only<br>`"nanoliposomal irinotecan"` -> alias_only<br>`"doxorubicin hydrochloride liposome"` -> alias_only |
| M32-D3 | **FIXED under current map/name policy** | `"ropeginterferon alfa-2b"` -> alias_only |
| M32-S1 NICOTINE question | **FIXED under current map/name policy** | `"What trials evaluate NICOTINE?"` -> not_one_name; questions ask:2 evidence, structured:2 evidence, check:2 evidence |
| M32-S2 Greek stored aliases | **NOT FIXED: intentional alias exclusion** | `"thymosin \u03b11"` -> alias_only<br>`"ifn-\u03b1-2b"` -> alias_only<br>`"interferon \u03b1-2b"` -> alias_only |
| M32-S3 trademark recall | **FIXED under current map/name policy** | `"trastuzumab\u2122"` -> center CHEMBL1201585<br>`"AstraZeneca\u2122"` -> center ORG:astrazeneca |
| controls | **Control cohort** | `"Merck & Co"` -> center ORG:merckco<br>`"trastu\u0301zumab"` -> center CHEMBL1201585<br>`"trastuzumab\u034f"` -> center CHEMBL1201585<br>`"trastuzumab\ufe0f"` -> center CHEMBL1201585<br>`"trastuzumab\udb40\udd00"` -> center CHEMBL1201585<br>`"Onivyde"` -> refused<br>`"liposomal irinotecan"` -> refused<br>`"Doxil"` -> refused<br>`"liposomal doxorubicin"` -> refused<br>`"13-cis retinoic acid"` -> alias_only<br>`"BAT1706"` -> alias_only<br>`"BI 695502"` -> alias_only<br>`"FKB238"` -> alias_only<br>`"HLX-04"` -> alias_only<br>`"HLX04-O"` -> alias_only |
| M33-B1 | **FIXED under current map/name policy** | `"Myocet"` -> refused<br>`"Myocet\u2122"` -> refused<br>`"My/o/cet"` -> refused<br>`"My ocet"` -> refused<br>`"Inflectra"` -> refused<br>`"Inf/lectra"` -> refused<br>`"Equidacent"` -> refused<br>`"Equi/dacent"` -> refused<br>`"Fyarro"` -> refused<br>`"Fy/arro"` -> refused<br>`"Megace ES"` -> refused<br>`"Megace/ES"` -> refused |
| M33-D1 | **FIXED under current map/name policy** | `"Oraqix"` -> refused; questions Oraqix:0 evidence, What trials evaluate Oraqix?:0 evidence, What does Oraqix target?:0 evidence |
| M33-D2 | **FIXED under current map/name policy** | `"Actikerall"` -> refused; questions Actikerall:0 evidence, What trials evaluate Actikerall?:0 evidence, What does Actikerall target?:0 evidence |
| M33-D3 | **FIXED under current map/name policy** | `"Betnesol-n"` -> refused; questions Betnesol-n:0 evidence, What trials evaluate Betnesol-n?:0 evidence, What does Betnesol-n target?:0 evidence |
| M33-D4 | **FIXED under current map/name policy** | `"Maxitrol"` -> refused; questions Maxitrol:0 evidence, What trials evaluate Maxitrol?:0 evidence, What does Maxitrol target?:0 evidence |
| M33-D5 | **FIXED under current map/name policy** | `"Cipro HC"` -> refused; questions Cipro HC:0 evidence, What trials evaluate Cipro HC?:0 evidence, What does Cipro HC target?:0 evidence |
| M33-D6 | **FIXED under current map/name policy** | `"Tobradex"` -> refused; questions Tobradex:0 evidence, What trials evaluate Tobradex?:0 evidence, What does Tobradex target?:0 evidence |
| M33-S1 | **FIXED under current map/name policy** | `"(+/-)NICOTINE"` -> center CHEMBL440464<br>`"What trials evaluate (+/-)NICOTINE?"` -> not_found; questions ask:0 evidence, structured:0 evidence, check:0 evidence<br>`"What does (+/-)NICOTINE target?"` -> not_found; questions ask:0 evidence, structured:0 evidence, check:0 evidence<br>`"What trials evaluate NICOTINE?"` -> not_one_name; questions ask:2 evidence, structured:2 evidence, check:2 evidence |
| M33-S2 | **FIXED under current map/name policy** | `"Darzalex"` -> alias_only<br>`"Tepezza"` -> alias_only<br>`"Tevimbra"` -> alias_only<br>`"Winrevair"` -> alias_only<br>`"Privigen"` -> alias_only<br>`"Lmx 4"` -> alias_only |
| additional new exclusions | **Control cohort** | `"PRED-G"` -> refused; questions PRED-G:0 evidence, What trials evaluate PRED-G?:0 evidence, What does PRED-G target?:0 evidence<br>`"NEO-DELTA-CORTEF"` -> refused; questions NEO-DELTA-CORTEF:0 evidence, What trials evaluate NEO-DELTA-CORTEF?:0 evidence, What does NEO-DELTA-CORTEF target?:0 evidence<br>`"LEP-ETU"` -> refused; questions LEP-ETU:0 evidence, What trials evaluate LEP-ETU?:0 evidence, What does LEP-ETU target?:0 evidence |
| M34-B1 | **FIXED under current map/name policy** | `"Cabozantinib (s)-malate"` -> refused<br>`"cabozantinibsmalate"` -> refused<br>`"CABOZANTINIB S-MALATE"` -> refused<br>`"Cabozantinib (s)-malate?"` -> refused<br>`"C a b o z a n t i n i b   ( s ) - m a l a t e"` -> refused<br>`"Cabozantinib/(s)-malate"` -> refused<br>`"Cabozantinib\u200b(s)-malate"` -> refused<br>`"Cabozantinib (s)-malate\u2122"` -> refused<br>`"CHEMBL2103868"` -> center CHEMBL2103868 |
| M34-S1 | **FIXED under current map/name policy** | `"What trials evaluate (NICOTINE)?"` -> not_one_name; questions ask:2 evidence, structured:2 evidence, check:2 evidence<br>`"What does (NICOTINE) target?"` -> not_one_name; questions ask:2 evidence, structured:2 evidence, check:2 evidence<br>`"What trials evaluate [NICOTINE]?"` -> not_one_name; questions ask:2 evidence, structured:2 evidence, check:2 evidence<br>`"What does [NICOTINE] target?"` -> not_one_name; questions ask:2 evidence, structured:2 evidence, check:2 evidence<br>`"What trials evaluate NICOTINE?"` -> not_one_name; questions ask:2 evidence, structured:2 evidence, check:2 evidence<br>`"What trials evaluate (+/-)NICOTINE?"` -> not_found; questions ask:0 evidence, structured:0 evidence, check:0 evidence<br>`"What trials evaluate NICOTINE(+)?"` -> not_found; questions ask:0 evidence, structured:0 evidence, check:0 evidence |
| M34-S2 | **FIXED under current map/name policy** | `"(+)-NICOTINE"` -> not_found<br>`"(+)NICOTINE"` -> not_found<br>`"(-)-nicotine"` -> not_found<br>`"(+/-)NICOTINE"` -> center CHEMBL440464<br>`"(\u00b1)-nicotine"` -> not_found<br>`"NICOTINE"` -> center CHEMBL3 |
| M34-D1 | **NOT FIXED: recorded upstream data nonblocker** | `"THEOPHYLLINE"` -> center CHEMBL1355736; drug_type=Protein |
| M32-B4 copyright | **FIXED under current map/name policy** | `"Tarceva\u00a9"` -> alias_only |
| M35-B1 | **FIXED under current map/name policy** | `"ARTEMISININ"` -> center CHEMBL269671<br>`"(-)-ARTEMISININ"` -> not_one_name<br>`"(-\u200b)-ARTEMISININ"` -> not_one_name<br>`"(-\ufeff)-ARTEMISININ"` -> not_one_name<br>`"(-\u2060)-ARTEMISININ"` -> not_one_name<br>`"(-\u0301)-ARTEMISININ"` -> not_one_name<br>`"(\u2212\u200b)-ARTEMISININ"` -> not_one_name<br>`"(+)-ARTEMISININ"` -> alias_only<br>`"CHEMBL269671"` -> center CHEMBL269671 |
| M35-S1 | **FIXED under current map/name policy** | `"What trials evaluate (+/-)(NICOTINE)?"` -> not_found; questions ask:0 evidence, structured:0 evidence, check:0 evidence<br>`"What does (+/-)[NICOTINE] target?"` -> not_found; questions ask:0 evidence, structured:0 evidence, check:0 evidence<br>`"What trials evaluate (NICOTINE)(+/-)?"` -> not_found; questions ask:0 evidence, structured:0 evidence, check:0 evidence<br>`"What trials evaluate [NICOTINE](+/-)?"` -> not_found; questions ask:0 evidence, structured:0 evidence, check:0 evidence<br>`"What trials evaluate (NICOTINE)(+)?"` -> not_found; questions ask:0 evidence, structured:0 evidence, check:0 evidence<br>`"What trials evaluate NICOTINE (+/-)?"` -> not_found; questions ask:0 evidence, structured:0 evidence, check:0 evidence<br>`"What trials evaluate ( NICOTINE ) and osimertinib?"` -> not_one_name; questions ask:2 evidence, structured:2 evidence, check:2 evidence |

## Historical replay coverage

All **123 historical leaf jobs and nine additional jobs exited 0**. The original **7,511-key alias sweep** and both **1,648-question frozen/historical replays** completed. Each of those two replays reports 1,648 identical and zero errors against its constructed same-HEAD relinking baseline. The separate adapted no-exclusion baseline reports **72 identical, 1,552 entity-metadata-only and 24 semantic differences**, zero errors; these are **not parent-versus-HEAD regression counts**. [Execution summary](replay/execution_summary.json), [additional jobs](replay/additional_execution37.json), [historical QA counters](replay/historical_qa_summary.json).

Separately, a fresh comparison loading **both actual parent `app.py` and parent `query.py` from Git** against HEAD produces **1,648/1,648 identical complete question API responses**, with zero entity-only changes, semantic changes or exceptions, in **45.426 seconds**. This immutable-snapshot comparison does not cover the newly constructed S1/S2 inputs. [Parent source hashes and summary](replay/parent_qa_summary.json), [paired complete results](replay/parent_qa_results.json), [reproducer](replay/parent_qa37.py).

All **275 inherited naming finding rows** have fresh exact-case dispositions: **257 FIXED / 18 NOT FIXED overall**, **260 FIXED / 15 NOT FIXED for the map**. The 15 map residual rows are nine recorded over-refusals and six deliberately excluded alias-recall cohorts; three additional overall residuals are question-only. That inherited ledger does not include the later M32–M36 findings, which are listed separately above. [Per-finding exact cases](replay/per_finding_cases.json), [readable ledger](replay/historical_table.md), [counts](replay/matrix_summary.json).

An additional **129 report-derived HTTP requests** include all 26 prior Unicode dash forms and two expected oversized-input HTTP 400 responses; 23 code/annotation spans were excluded. The original M22 standalone generator is unavailable: its saved-input adapter freshly replays the **58 recorded inputs**, and the unavailable generator is not claimed to have run. M27/M29 coverage uses their recorded attack sources. Successful legacy script exit alone is not substituted for correctness under today's map policy. [Supplementary inputs and exclusions](replay/report_input_supplement.json), [reuse details and caveats](replay/FINDINGS.md).

There are **163 copied-source provenance records**: 151 historical leaf/helper sources and 12 orchestration/checker sources. All final hashes match their prepared records. All **45 lifecycle records** have no integrity, page-equality or port-closure failure flags; all **27 private replay ports are closed**. [Provenance](replay/reuse_manifest.json), [final validation](replay/final_validation.json), [lifecycles](replay/lifecycle_records.json). Cohorts overlap and are not summed as independent findings or unique inputs.


## Question boxes and shipped demos

All **36 shipped demos** match both the parent query implementation and current HTTP responses. The **99-key / 708-case shared-name baseline** has zero changes. Expanded question matrices contain **312 cases / two parent changes**, **540 composition cases / 60 changes**, and **360 supplementary cases / 74 changes**; all map versions of those questions remain undrawn. These overlapping matrices are not added as distinct defects. The new S1/S2 cases explain why unchanged demos and the older baseline do not establish complete question refusal or recall. [Demo comparison](contract/demo_previous_comparison.json), [shared-key comparison](contract/shared_key_question_comparison.json), [contract summary](contract/summary.json).

## Guarantees A–G

| Guarantee | Fresh result and limits |
|---|---|
| A — relations and directions | **PASS:** independent SQL oracle over all **6,469 live centers / 22 relation combinations**, zero errors. Self-loops, unknown relation/type, lead/collaborator roles and Investigator wording pass their fixtures. [Oracle](contract/db_validate.json), [special cases](contract/self_loop_unknown.json). |
| B — names, IDs and live choices | **PASS within the specified two-mode name policy and exercised universe.** M36 failures close; independent membership, refusal, ambiguity, ID, retired-node and choice-click checks pass. No new wrong-node draw was established. [Source findings](source/findings.md), [choice clicks](contract/choose_ui.json), [retirement](source/retired_private_fixture.json). |
| C — stored values and live counts | **PASS, 19/19 assertions:** exact scores, missing versus zero, booleans, malformed properties, live counts and 1,001-drug chunking. Synthetic Infinity fails closed with HTTP 400; it is absent from the snapshot. THEOPHYLLINE remains a source metadata error. [Assertions](contract/db_assertions.json), [numeric fixture](contract/db_numeric_fixture.json). |
| D — ordering, cuts and totals | **PASS:** independent stored weights, label ties, group/edge totals, and actual page list/ring-cut behavior. [SQL oracle](contract/db_validate.json), [page harness](contract/ui_harness_results.json). |
| E — page safety and state | **PASS within the executed JavaScript harness, 26/26 assertions:** escaped labels/IDs/URLs, safe `choose` and `alias_only` markup, real HTTP click-through, trails, stale replies, double clicks and error recovery. Painted-browser layout was not verified. [Assertions](contract/ui_assertions.json), [state regressions](contract/ui_regressions.json). |
| F — server | **PASS with inherited qualifications:** controlled invalid-input errors and recovery; 24 concurrent map calls succeed; private retirement cases pass. Parser-detail disclosure and blank-submit retention remain recorded. [Server](contract/server_checks.json), [callbacks](contract/ui_m3_checks.json). |
| G — docs, read-only and no model | **PASS for inspected read-only/no-model behavior; documentation qualified by M37-S3.** The visible punctuation statement needs the strict-mode exception. README counts correctly say 365. Final file integrity is below. |

All **seven DB suites and nine UI/question suites exited 0**. The full DB oracle completed in **641.063 seconds**, within its 1,800-second audit allowance, with no timeout or retry. [Execution](contract/execution.json), [UI execution](contract/ui_execution.json), [summary](contract/summary.json).

All **23 inherited nonidentity rows** were re-exercised: **20 FIXED / three NOT FIXED**. Exact remaining cases are submitting empty/whitespace after a valid map (no request, previous view retained); private stored `+Infinity` / `-Infinity` (controlled HTTP 400); and malformed JSON, list/null and oversized bodies (controlled errors expose parser/attribute details, followed by successful valid requests). These remain separate nonblockers. [Per-finding fixtures and results](contract/HISTORY.md).

All **15 cost suites exited 0**; the **11 historical cost dispositions remain six FIXED / five NOT FIXED**. Residual cold/queued-map timings are **8.911/8.904 s** for 400 distinct `isa` pieces, **10.865/10.843 s** for 4,000 U+FDFA characters, **19.020/18.989 s** for 1,000 `isa` matches, and **8.474/8.433 s** for joined-item rescans; the 1,000 punctuation-separated `x` workload has a **1.396 s** direct median. These are observations under concurrent audit load, not proof of a commit-caused performance regression. All seven cost-suite lifecycles preserve the DB and close their ports. [Exact workloads and ledger](contract/cost/FINDINGS.md), [summary](contract/cost/summary.json).

## Standards axis

**Zero hard documented-standard violations identified.** The pinned review is `git diff HEAD^...HEAD`; no filesystem AGENTS.md or separate tracked coding-style standard was found. The supplied evidence-backed review and no-tracked-edit instructions govern this audit. Parameterized SQL, live-node filtering and page escaping remain intact. The changed helpers operate on strings and add no writes, external calls or model invocation. Regression cases accompany the change. No undocumented style preference or unrelated tracker setup was imposed. [Independent Standards review](contract/STANDARDS.md).

This review makes no production repair, so the user's conditional KOA Studio/KhOpenApi comparison requirement is not triggered. The review artifacts and private fixtures are confined to m37.

## Spec axis

**No blocking deviation from the revised map specification was established.** The two modes, classification after preprocessing, preservation of strict-mode punctuation/significant symbols, ordinary-mode normalization, live-only choices and stored-refusal closure were independently tested. The exact previously blocking map reproductions rerun here are fixed under the present admission policy. [Independent Spec review](source/spec_axis.md).

M37-S1 is a demonstrated question-only regression; M37-S2 is a requested-rule recall cost; M37-S3 is incomplete explanatory wording. Their evidence remains visible rather than being hidden by the passing map verdict. Source-data curation is separately outstanding. These are not promoted to map blockers contrary to the agreed scope. The conclusion does not claim universal free-text refusal, correctness of resolver-owned brand lists, arbitrary stereochemical spelling equivalence, or complete scientific validation of upstream identities.

Axes remain separate: **Standards: zero hard violations. Spec: zero established map blockers; the three nonblocking findings above remain.**


## Integrity and limits

All **7,837 checked files**, comprising the tracked baseline plus the processed SQLite database and resolved dictionary, retain their pre-test SHA-256 values: **zero changed, zero added to the tracked baseline**. Tracked git status is empty and HEAD is unchanged. All scratch files, audit scripts, temporary files and this report are under `audit_evidence_claims/m37/`. No production edit, source curation, model call or external publication was performed. [Initial hashes](integrity_before.json), [final integrity](integrity_final.json).

Root stopped its owned CLI after historical consumers released port 8937. All **33 owned/tested ports** are closed: root 8937, five contract ports 9700/9701/9702/9710/9711, and the 27 replay ports. [Root lifecycle](server_lifecycle.json), [contract closure](contract/summary.json), [replay closure](replay/execution_summary.json), [final report and port checks](report_validation.json).

The CUA browser inventory call timed out and reset its kernel. Page evidence therefore uses the actual served JavaScript in Node VM DOM/fetch harnesses, including forms, demo callbacks, generated markup and real HTTP click-through. It establishes those behaviors, **not painted-browser layout**. [Browser availability](browser_availability.json). This limitation is explicit; no screenshot-based validation is claimed.

Normalization testing retains the two dotless-i probe-assumption differences and separates synthetic canonical-key terminal states from literal-source refusal results. Historical adapted baselines, saved-prior comparisons and actual parent execution are distinguished above. The unavailable M22 generator is not represented as executed. Passing finite tests and the mode-separation argument do not establish universal semantic or scientific identity equivalence beyond the approved name policy.

The remaining questions and documentation findings are nonblocking under the agreed map scope, and known data issues remain separately recorded. No established map blocker remains in the tested HEAD.

VERDICT: APPROVE
