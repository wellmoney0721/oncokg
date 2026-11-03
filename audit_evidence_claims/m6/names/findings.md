# M6 names and QA evidence

Reviewed `b7a00f9c14e5ee0447601795d0c0f4535c2f0376`; `src/query.py` SHA-256 `dbebe9981200a453368426872d0c253d3aa0fd72cf420a78c712f3fb4058e3b6`. Scratch writes stay in this directory. Python bytecode is disabled. New fixtures open the real database read-only; older probes retain their existing read-only behavior. No application code was edited and no model was called. These are direct Engine results, not HTTP results; the root reviewer independently confirms HTTP.

## Reused evidence and coverage

`replay.py` copies 13 existing M5 name scripts with **only scratch path substitutions**, preserving their prior inputs and counterfactual comparisons. `replay_manifest.json` records original source hashes, exit codes and times. All 13 exit codes are zero. Earlier M1/M2b/M3/M4 inputs are carried by those scripts; none of their earlier outputs is overwritten.

- 62 original M1/name cases plus 14 additional probes: `names_reproduction_results.json`.
- 13 previous mixed-input/QA regressions and boundary/multi-company fixtures: `names_regressions.json`, `names_boundary_details.json`.
- All 30 M3 supplemental cases and 21 stored joiner-containing aliases: `names_new_boundaries.json`.
- All 45 M4 attacks, 37 QA questions and 2,584 multi-token alias keys: `names_attack.json`; final and separator controls: `names_final_checks.json`, `names_separator_checks.json`.
- Old no-relink isolation sweep regenerated **1,612** questions from current entities: 28 identical, 1,560 entity-metadata-only changes, 24 semantic changes, zero errors. `names_qa_relink_sweep.json`.
- To retain every historical reproduction despite that dynamic inventory shrinking, `historical_qa_replay.py` reuses the same comparison code with the ordered union of the literal M4 and M5 saved input inventories. Both contained 1,648 questions and their union is **1,648**, including 36 absent from the regenerated list. Exact historical replay: **64 identical, 1,560 entity-metadata-only changes, 24 semantic changes, zero errors**; exit 0. `historical_qa_replay.json`, `historical_qa_replay_stdout.txt`, `historical_adaptation.json`. The regenerated 1,612-case artifact remains intact.
- All seven unique page/CLI demo questions: six complete responses identical to `bfcb83d`; Mvasi remains refused with zero evidence, with a refusal-label change. Evidence counts remain 12/12/11/1/12/0/0. `names_demo_results.json`.
- Repeated M5's 113 input scan, 7,511 unique unambiguous alias keys, 49 focused comparisons and additional cross-item controls: `names_m5_attack.json`, `names_m5_confirm.json`, `names_cross_item_refusal.json`.
- New focused **74** cases, with exact immediate-M5 (`514929c`) linker, `_drug_spans`, and `_JOINERS` comparisons: `focused_new.py`, `focused_new.json`. Remaining source/data are held current in the counterfactual.

## Earlier name findings: explicit dispositions

| Earlier finding / exact inputs | M6 disposition | Fresh evidence |
|---|---|---|
| M1-B1: `bevacizumab - awwb`, `89Zr - trastuzumab`, `[89Zr] trastuzumab`, compact controls | **FIXED** for the named inputs: no originator | `names_reproduction_results.json` |
| M1-S5 identity ambiguity: Roche, MET, `osimertinib EGFR`, reverse, `Mvasi and bevacizumab` | **FIXED**: selected reading and alternatives/refusal retained | Same file |
| M1 salt/parent, case/whitespace/fullwidth ordinary-name controls | **FIXED / retained**: salt and parent IDs remain distinct for these inputs | Same file |
| M1 lowercase IDs / Investigator names | **NOT FIXED**, unchanged usability qualification | `names_unsupported_forms.json` |
| M2b-R1: `osimertinib and generic version of bevacizumab`, reverse/comma and exact trial/sponsor QA | **FIXED**: only separately listed osimertinib contributes drug evidence | `names_regressions.json`, `names_boundary_details.json` |
| M2b-R1 tracer/oral-azacitidine controls beside osimertinib | **FIXED**: separately listed osimertinib retained | `names_reproduction_results.json`, `names_regressions.json` |
| M2b embedded multi-ID company fixture `Sharedbrand company` | **FIXED**: Roche disclosed; zero live multi-ID company keys | `names_boundary_details.json` |
| M3-B1: `paclitaxel with albumin bound nanoparticles`, formulation variant, `generic version with bevacizumab` | **FIXED**: no originator | `names_new_boundaries.json` |
| M3-B2: `What is the generic version of bevacizumab?` | **FIXED**: refused, zero drug evidence | Same file |
| M3 comma over-refusal: osimertinib beside `liposomal doxorubicin` / `biosimilar bevacizumab`, reverse and QA | **FIXED** for exact cases | Same file |
| M3 full-name/no-relink controls: erlotinib hydrochloride and poliglumex full alias | **FIXED / retained**: correct full drug, no embedded parent | `names_attack.json` |
| M4-B1: `osimertinib with generic version of bevacizumab`, reverse and QA | **FIXED under accepted policy**: both same-item drugs refuse | `names_attack.json`, `names_final_checks.json` |
| M4-B1 punctuation: semicolon/fullwidth comma | **FIXED**: separately listed osimertinib survives | `names_separator_checks.json` |
| M4-B2: qualified poliglumex alias; long generic-version bevacizumab descriptions; exact QA | **FIXED**: no qualified originator; bare poliglumex retained | `names_attack.json`, `names_final_checks.json` |
| M4-B3: `biosimilar version of bevacizumab`, `liposomal formulation of doxorubicin`, hyphenated albumin-bound paclitaxel, two qualified products | **FIXED** | `names_attack.json`, `names_new_boundaries.json` |
| M4 target/company collateral refusal: EGFR/AstraZeneca plus qualified bevacizumab | **FIXED**: target/company retained | `names_attack.json` |
| M5-B1 primary slash/bar inputs: `bevacizumab-awwb/ osimertinib`, spaced suffix variant, `bevacizumab-awwb\| osimertinib`, exact slash QA | **FIXED**: osimertinib selected, bevacizumab refused | `names_m5_confirm.json`, `focused_new.json` |
| M5-B1 already reproduced variants: `bevacizumab-awwb+ osimertinib`, `bevacizumab - awwb& osimertinib`, `bevacizumab - awwb&osimertinib` | **NOT FIXED**; therefore the finding as a whole is not closed | Same files; these inputs occur in M5 `names_m5_confirm.py` and M5 name findings N1 |
| M5-B2: liposomal and nanoparticle formulation(s), investigational formulation, sustained-release variants, biosimilar-and-investigational bevacizumab | **FIXED for earlier exact inputs**: forward dangling qualifier reaches drug | `names_m5_confirm.json`, `focused_new.json` |
| M5-S1: `biosimilar anastrozole, Arimidex`, `biosimilar Prolia, xgeva`; `Erlotinib, hydrochloride biosimilar bevacizumab`, semicolon and QA | **FIXED**: second-item real drugs survive; erlotinib parent retained | `names_m5_confirm.json`, `names_cross_item_refusal.json` |
| M5-S2: `Pegylated interferon alfa-2a` | **NOT FIXED — recorded accepted over-refusal**; canonical name and ID still work | `names_m5_confirm.json`, `focused_new.json` |
| M5-S3 input cost | Root reviewer owns current timing evidence | Root `perf_current.json` and HTTP results |

## Blocking mechanism 1: internal slash/bar and existing +/& variants still hide suffixes

`bevacizumab - awwb/osimertinib` returns **BEVACIZUMAB / CHEMBL1201583**, 122 trials, `also:[]`, and no refusal. The same input's unchanged resolver gives `bevacizumab - awwb: BLOCKED_DISTINCT_PRODUCT` and `osimertinib: EXACT / CHEMBL3353410`. Thus the counterexample uses the repository's own refusal boundary, with no external pharmacology premise.

`Which trials evaluate bevacizumab - awwb/osimertinib?` returns 12 BEVACIZUMAB rows, first `NCT00955305|EVALUATES|CHEMBL1201583|NCT00955305`. Sponsor QA starts `ORG:roche|SPONSORS_TRIAL_OF|CHEMBL1201583|`. The pipe input `bevacizumab - awwb|osimertinib` repeats the wrong map. `bevacizumab - awwb/EGFR` also selects the refused originator.

The tokenizer at `src/query.py:143-154` strips `/|` only at token edges and increments clause IDs only for `startswith`/`endswith`. An interior `awwb/osimertinib` token survives. The anchored suffix check (`src/textrules.py:156-157,213-223`) therefore never sees `bevacizumab - awwb`; positive alias acceptance at `src/query.py:221-237` can still link the independent `bevacizumab` token. This directly contradicts the stated glued-slash list boundary. `Erlotinib/hydrochloride` likewise links the salt whereas `Erlotinib / hydrochloride` links the parent, showing that interior slash has not become a boundary in positive matching either.

The previously recorded `+`/`&` variants above remain additional routes to the same forbidden originator. `_JOINERS` (`src/query.py:94-95,168-171`) only recognizes a complete token, and stripping at line 147 does not remove these symbols. Both the interior-slash cases and surviving +/& cases already leak in exact M5; they are inherited holes, not newly introduced in M6. Fixed edge-attached-slash controls must not be used to classify the whole M5 finding as FIXED.

## Blocking mechanism 2: postpositive qualified descriptions still leak

`bevacizumab in an investigational and biosimilar formulation` maps **CHEMBL1201583**, no refusal. `Which companies sponsor bevacizumab in an investigational and biosimilar formulation?` returns its 12 sponsor rows. `doxorubicin in a novel and liposomal formulation` maps **CHEMBL53463**; its trial question returns the three doxorubicin rows, starting `NCT01970540|EVALUATES|CHEMBL53463|NCT01970540`.

These singular descriptions contain one named drug. The exact full-string `is_distinct_product` predicate is true. The clause containing the drug precedes `and`, while the qualifier is only in the next clause. At `src/query.py:192-197` it becomes a dangling qualifier with no later drug, so no refusal is emitted. The forward-only propagation at `183-204` repairs M5's prefix cases but leaves this direction exposed. Exact M5 comparison reproduces the same originator map; what changed is the refusal metadata, which now disappears. Unlike the suffix reproduction, the full resolver itself splits this phrase into multiple components and accepts the first one; do not claim a whole-input resolver disagreement for this case.

Ordinary same-item over-refusal remains accepted and is not a finding. This case is positive acceptance of a qualified originator, not over-refusal.

## Should-fix: named-product punctuation turns the carry rule into cross-item refusal

Bare `Mvasi and bevacizumab` correctly retains BEVACIZUMAB and discloses Mvasi refusal. **`(Mvasi) and bevacizumab`** now refuses `'(Mvasi) ... bevacizumab'` and returns no map/evidence, whereas the exact M5 predecessor retains BEVACIZUMAB. `[Mvasi] and bevacizumab` and `"Mvasi" and bevacizumab` repeat it. A separate valid second-item drug is being refused, outside the accepted same-item over-refusal policy.

`T.is_distinct_product` recognizes the brand using extracted words, but `src/query.py:188-191` tests raw token `.lower()` membership in the brand set. Parentheses/brackets/quotes make that test false; there is no dictionary Mvasi alias to rescue it. Lines 192-197 therefore treat a named product as a bare qualifier, and lines 199-205 refuse the next drug. `"Mvasi" and bevacizumab` also provides an unchanged resolver control: refused Mvasi plus exact BEVACIZUMAB.

There is a related hard-boundary issue: `liposomal, and doxorubicin`, `liposomal and; doxorubicin`, and `liposomal and / doxorubicin` all carry the qualifier across the hard punctuation. `joined` at lines 183-184 examines intervening joiner token markers but not clause IDs; omitted separator tokens do not stop carry. These synthetic boundary controls are secondary to the ordinary parenthesized-brand case.

`check_carry_assertions.py` independently validates the complete recorded current/predecessor outputs for three quoted/bracketed-brand failures, four hard-boundary failures, and two bare-brand controls: **9/9 assertions pass**, exit 0. Evidence: `carry_assertions.json`.

## Measured accepted-design consequences and inherited limitations

- Commas inside stored aliases are hard boundaries under the stated design. The 7,511-key scan reports 156 anomaly/difference rows versus the older M4 comparator; 57 previously linked aliases now have no Drug (including known M5-S2), and six now link a different component drug. Immediate-M5 confirmation: `CP-358,774` changes ERLOTINIB CHEMBL553 to the CP-358 alias's ERLOTINIB HYDROCHLORIDE CHEMBL1079742; `ENDOSTATIN, N-TERMINAL-MGGSHHHHH` changes CHEMBL4297946 to ENDOSTATIN CHEMBL4297747. These are measured consequences of the explicit no-name-across-items rule, **not additional blockers or demo regressions**. None of the seven demo questions regresses.
- Unicode guard normalization is still weaker than alias-key normalization. Fullwidth `ｂｅｖａｃｉｚｕｍａｂ－ａｗｗｂ`, em-dash `bevacizumab—awwb`, nonbreaking-hyphen `bevacizumab‑awwb`, `[８９Ｚｒ] trastuzumab`, `［89Zr］ trastuzumab`, and `[89Zr]—trastuzumab` map originators in current and exact M5; local guard predicates are false and the resolver also accepts. En-dash `bevacizumab–awwb` and ASCII tracer controls refuse. This is an inherited shared guard/normalization gap, not a new map-versus-resolver regression. Exact Unicode strings and outputs are in `focused_new.json`.
- `[89Zr] and copper labelled trastuzumab` / `[89Zr] - and trastuzumab` still map TRASTUZUMAB; a bare isotope is not recognized by `_qualified` as a tracer until joined to following letters. These are inherited, ambiguous conjunction controls; the suffix leak is sufficient to reject approval without relying on their interpretation.

Names/spec assessment: approval remains blocked by reproduced originator leakage. All earlier named M1-M4 failures and exact M5-B2/S1 cases are repaired; M5-B1 is only partially repaired, and M5-S2 remains the explicitly accepted known over-refusal.
