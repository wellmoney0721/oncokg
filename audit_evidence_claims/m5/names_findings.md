# M5 independent names and QA review

HEAD `514929c`. All scripts and outputs here are scratch; source/database files are read only. No model was called. Existing name scripts were copied from m4 (demo comparator from m2b), with output paths redirected to m5. The two original HTTP-post helpers were adapted to direct Engine calls; these files are **not new HTTP evidence**. Root owns the unchanged CLI-server HTTP confirmation.

## Replay coverage

`names_prepare.py` documents the exact copy/adaptation and executes ten previous scripts. Every exit code is 0: `names_replay_execution.json`.

- 62 original m1 name cases, 14 additional original probes: `names_reproduction_results.json`.
- 13 earlier explicit mixed-name/QA regressions: `names_regressions.json`.
- Earlier boundary/multi-company/retired-name controls: `names_boundary_details.json`.
- All current non-Drug/Trial node-label probes: `names_label_scan.json`.
- All 45 m4 focused attacks, 37 varied QA inputs, 2,584 unique multi-token alias keys: `names_attack.json`.
- All 30 m3 supplementary controls and joiner-bearing stored aliases: `names_new_boundaries.json`.
- Exact m4 final QA, unsupported forms, and nine separator/hyphenation checks: `names_final_checks.json`, `names_unsupported_forms.json`, `names_separator_checks.json`.
- The old no-relink isolation sweep rerun against HEAD: 1,648 questions; 28 identical, 1,596 entity-metadata-only changes, 24 semantic changes, 0 exceptions. As in m4, the semantic differences concern the deliberately removed duplicate/nested entity matches; they do not show a new M5 adverse no-relink regression. `names_qa_relink_sweep.json`.
- All seven unique page/CLI demo questions: six full responses identical to bfcb83d; Mvasi still refuses with zero evidence, with only the refused entity's span expanded to the whole item. Expected evidence counts remain 12/12/11/1/12/0/0. No demo was blocked. `names_demo_results.json`.

New coverage: 113 boundary/qualifier attacks, **7,511 unambiguous stored alias keys**, then 49 focused exact-before/after confirmations. `names_m5_attack.json`, `names_m5_summary.json`, `names_m5_confirm.json`. The exact immediate-predecessor comparator restores **all three** old linker methods (`link_entities`, `_drug_spans`, `_qualified_drug_spans`) and its `_JOINERS` from `bf436c6`; other code and database stay current.

## Prior finding dispositions

| Prior finding | Current status and evidence |
|---|---|
| M1 B1 spaced suffix / tracers: `bevacizumab - awwb`, `89Zr - trastuzumab`, `[89Zr] trastuzumab` | **FIXED** for every exact input. All refuse; compact forms remain refused. `names_reproduction_results.json`. |
| M1 ambiguity disclosure: Roche/MET, `osimertinib EGFR`, reversed, `Mvasi and bevacizumab` | **FIXED**. Selected identity and other entity/refusal disclosed. `names_reproduction_results.json`. |
| M1 salt/parent distinction and Unicode/case/whitespace controls | **FIXED / retained** for original inputs: erlotinib hydrochloride CHEMBL1079742 versus erlotinib CHEMBL553; osimertinib mesylate CHEMBL3545063; fullwidth and mixed case accepted. |
| M1 unsupported lowercase IDs and Investigator names | **NOT FIXED**, unchanged usability limitation. `names_unsupported_forms.json`. |
| M2b R1 `osimertinib and generic version of bevacizumab`, reverse/comma; exact trial/sponsor questions | **FIXED**. OSIMERTINIB kept, BEVACIZUMAB refused; evidence names osimertinib. `names_regressions.json`, `names_boundary_details.json`. |
| M2b `[89Zr] trastuzumab and osimertinib` / reverse; `osimertinib and oral azacitidine` / reverse | **FIXED**. Separately listed osimertinib survives. |
| M2b embedded multi-ID company `Sharedbrand company` fixture | **FIXED**. Roche alternative disclosed. No live multi-ID company key. `names_boundary_details.json`. |
| M3 B1 `paclitaxel with albumin bound nanoparticles`, formulation variant, `generic version with bevacizumab` | **FIXED**. No originator centre/evidence. `names_new_boundaries.json`. |
| M3 B2 `What is the generic version of bevacizumab?` | **FIXED**. Refused; no centre. |
| M3 comma over-refusal `osimertinib, liposomal doxorubicin`, `osimertinib, biosimilar bevacizumab`, reverses and QA | **FIXED** for these exact cases. Osimertinib and its evidence retained. |
| M3 longer alias `Paclitaxel conjugate with poly-l-glutamic acid`, `erlotinib hydrochloride` | **FIXED / retained** for bare aliases. No nested parent relink. |
| M4 B1 `osimertinib with generic version of bevacizumab`, reverse and exact trial/sponsor QA | **FIXED** under the new accepted design. Both drugs in this one item refuse; no qualified originator appears. This intentional refusal is not reported as should-fix. |
| M4 B1 semicolon/fullwidth comma: `osimertinib; generic version of bevacizumab`, `osimertinib， generic version of bevacizumab` | **FIXED**. OSIMERTINIB retained, BEVACIZUMAB refused. |
| M4 B2 `generic version of Paclitaxel conjugate with poly-l-glutamic acid`, `generic version of the monoclonal antibody bevacizumab`, exact QA | **FIXED**. No originator centre/evidence, no six-token reach limit. |
| M4 B3 `paclitaxel with albumin-bound nanoparticles`, `biosimilar version of bevacizumab`, `liposomal formulation of doxorubicin` | **FIXED**. No originator centre/evidence. |
| M4 target/company collateral refusal: `EGFR biosimilar bevacizumab`, `AstraZeneca biosimilar bevacizumab`, reverse/generic-version controls | **FIXED**. EGFR/AstraZeneca survive and refusal is disclosed. `names_attack.json`, `names_m5_attack.json`. |

## Blocker N1: missed attached separator defeats the product guard (inherited)

Exact input **`bevacizumab-awwb/ osimertinib`** returns centre **BEVACIZUMAB / CHEMBL1201583**, 122 trials, with OSIMERTINIB merely in `also`, and no refusal. `Engine.resolve` on the same exact input gives two components: `bevacizumab-awwb` **BLOCKED_DISTINCT_PRODUCT**, `osimertinib` **EXACT / CHEMBL3353410**. The bare `bevacizumab-awwb` refuses in both current and preceding linker. This is a repository-internal counterexample to the refused-product guarantee, not an external interpretation of a drug name.

`Which trials evaluate bevacizumab-awwb/ osimertinib?` returns 12 evidence rows beginning `NCT00955305|EVALUATES|CHEMBL1201583|NCT00955305`. `Which companies sponsor bevacizumab-awwb/ osimertinib?` starts `ORG:roche|SPONSORS_TRIAL_OF|CHEMBL1201583|` (12 rows). These are the refused originator's evidence.

Variants `bevacizumab - awwb/ osimertinib`, `bevacizumab - awwb&osimertinib`, `bevacizumab - awwb& osimertinib` and `bevacizumab-awwb+ osimertinib` also expose BEVACIZUMAB. The resolver splits and refuses the product in each plain-string variant. A space on **both** sides of `/` instead triggers intended whole-item refusal in HEAD, because `/` is not a listed separator but the unadorned suffix becomes visible to the guard. A separated `&` is a recognized listing token and retains only osimertinib. The mismatch is tokenization-sensitive, and is also present in bf436c6.

Cause: `src/query.py:128-130` splits only five comma/semicolon characters and whitespace; `145-149` recognizes listing symbols only when they are the complete token. `/`, `+`, or `&` attached after the suffix stays in the guard's word. The anchored suffix predicate `src/textrules.py:156-157,213-223` then fails. Matching subsequently uses `canonical_key` (`src/query.py:182,184`; `src/textrules.py:339-346`) that discards that punctuation, recovering the stored originator alias after the refusal check has missed it. Exact current/predecessor/resolver/QA results: `names_m5_confirm.json`.

## Blocker N2: a listing word can split adjectives of one qualified product (inherited)

**`liposomal and investigational formulation of doxorubicin`** names one qualified formulation; HEAD refuses only `liposomal` and maps **DOXORUBICIN / CHEMBL53463**, 3 trials. The full-string product predicate is true. The unchanged full-string resolver returns `BLOCKED_DISTINCT_PRODUCT`, no drug. `Which trials evaluate a liposomal and investigational formulation of doxorubicin?` returns all 3 doxorubicin trial rows, beginning `NCT01970540|EVALUATES|CHEMBL53463|NCT01970540`.

Additional exact cases `liposomal and nanoparticle formulations of doxorubicin` and `Which companies sponsor biosimilar and investigational versions of bevacizumab?` likewise recover the originator; the latter supplies 12 BEVACIZUMAB sponsor evidence rows. The singular-formulation example is the clearest: `and` coordinates descriptors, with no second named substance.

`_JOINERS` at `src/query.py:94-95` and the unconditional boundary `145-149` detach the qualifier before examining the drug. Item-local product scanning (`156-164`) cannot reconnect them. This follows the newly described implementation rule but still violates the unchanged product/QA approval guarantee. No claim is made that ordinary separate names such as `liposomal doxorubicin and osimertinib` should share qualifiers; that intended isolation succeeds. This bypass was also present in bf436c6. Evidence: `names_m5_confirm.json`.

## New cross-item alias regression: identities are stitched across the separators

**`Erlotinib, hydrochloride biosimilar bevacizumab`** should preserve first-item ERLOTINIB / CHEMBL553 and refuse the second item. Instead HEAD draws **ERLOTINIB HYDROCHLORIDE / CHEMBL1079742**, 31 trials, and simultaneously says `hydrochloride biosimilar bevacizumab` was refused. The exact preceding linker draws CHEMBL553 (118 trials). The current unchanged resolver also returns ERLOTINIB EXACT and the second item BLOCKED_DISTINCT_PRODUCT. Independent controls `Erlotinib` and `hydrochloride biosimilar bevacizumab` yield the parent and refusal, respectively. The `and` variant preserves the parent. The semicolon variant repeats the new wrong-salt map.

`Which trials evaluate Erlotinib, hydrochloride biosimilar bevacizumab?` likewise changes the subject to CHEMBL1079742, returning 12 rows beginning `NCT00445848|EVALUATES|CHEMBL1079742|NCT00445848`.

This is an adversarial constructed input, not a claim that hydrochloride bevacizumab is a real marketed product. It tests the declared list contract and explicit salt-versus-parent distinction: two list items that independently mean parent plus refusal are combined into a third identity. It does **not** require external chemistry assumptions.

Cause: `_drug_spans(tokens, skip)` at `src/query.py:155,231-248` is given only joiner-token positions, with no segment IDs. It joins `Erlotinib` and `hydrochloride` across the comma. `165` assigns the entire span to **only `seg[a]`**, the first item's segment, so the later product qualifier does not mark any of those salt-span tokens refused. The final matcher (`174-184`) also has no segment-boundary guard, so it draws the synthetic salt name. Evidence: `names_m5_confirm.json`; full counterfactual setup in `names_m5_confirm.py`.

## Should-fix S1: a real drug alone in its own item is refused (new)

**`biosimilar anastrozole, Arimidex`** returns only `refused:'biosimilar anastrozole'`; Arimidex disappears. `Arimidex` by itself resolves/maps **ANASTROZOLE / CHEMBL1399**. `biosimilar anastrozole and Arimidex` retains it. `Engine.resolve` splits the comma input into a refused first component and Arimidex **ALIAS / CHEMBL1399**. bf436c6 also retained Arimidex. Trial QA for the comma input now has 0 evidence versus the `and` variant's 2 rows.

**`biosimilar Prolia, xgeva`** similarly refuses the entire input although Xgeva alone in the second item is an accepted alias for **DENOSUMAB / CHEMBL1237023**. `biosimilar recombinant, interleukin-2` likewise suppresses second-item ALDESLEUKIN.

This is explicitly within the user's should-fix exemption: the valid drug is **alone in its own comma-separated item**, not sharing an item with a qualifier. Cause is the same cross-clause span bug, in the other direction: the dictionary contains `anastrozole (arimidex)` / `Prolia, xgeva`; `_drug_spans` merges both item tokens, then `165-168` refuses the whole span when its **first** item has a qualifier. `names_m5_confirm.json` contains exact predecessor comparisons; `names_cross_item_refusal.json` has extra direct controls.

## Should-fix S2: intrinsic pattern in a valid lone alias (new map rejection, shared resolver limitation)

Stored ChEMBL synonym **`Pegylated interferon alfa-2a`** belongs uniquely to **CHEMBL1201560 / PEGINTERFERON ALFA-2A** in the current dictionary. Used alone, HEAD refuses it and yields no map/QA evidence. The canonical name `PEGINTERFERON ALFA-2A` and exact node ID both draw that same live molecule; canonical-name profile has 3 evidence entries. bf436c6 reached the same drug through the residual `alfa-2a` alias (with an incomplete refusal), so HEAD changes that alias's map from the correct stored entity to refusal.

The full resolver already refuses the synonym via `pegylated`; this is therefore **not** asserted to be newly inconsistent with the resolver. It is a dictionary/guard inconsistency and a lone-valid-alias usability issue under the explicit request to attack intrinsic qualifier patterns. There is no originator misidentification here, and no demo uses the synonym. Of 7,511 unambiguous alias keys, this was the only newly refused previously linked lone alias. The 50 alias anomaly rows include inherited refusals and benign refusal-label changes; they are not 50 new defects. Evidence: `names_m5_summary.json`, `names_m5_confirm.json`.

## Intended refusals and limits

Newlines, tabs, pipes, slash, Arabic comma/semicolon, halfwidth ideographic comma, full stops and phrases `as well as`, `together with`, `alongside` are not all recognized separators. When the ordinary `biosimilar` token is present, these usually cause both drugs to be refused. **Those ordinary same-item refusals are not findings** under the user's fail-closed rule. The attached-suffix bypass above is different: it returns the refused originator. Semicolon/fullwidth comma/ideographic comma and all explicit `_JOINERS` controls otherwise retain separately listed osimertinib.

Likewise `osimertinib with generic version of bevacizumab`, `osimertinib with [89Zr] trastuzumab`, and both drugs with a single shared-item qualifier intentionally refuse both. No should-fix is reported for these.

The complete old direct boundary script includes a >500-character API-independent call and took 27.196 s; this is not an HTTP timing. Root separately measures bounded HTTP inputs and long direct-input costs.
