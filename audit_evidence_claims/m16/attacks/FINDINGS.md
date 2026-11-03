# M16 independent isotope attack findings

HEAD `8ebd6629b51a474f216457c8c00f20152304bd1d`; previous query module `1b3896669387cbc142c12b726909231cca8658db`. Application and dictionary files were not modified. All new artifacts are in this directory. No model was called.

## P1: element-first one-letter isotope spelling passes every refusal stage

**Exact request:** `POST /api/explore`, `{"text":"I-124-labelled trastuzumab"}`. HTTP 200 draws **TRASTUZUMAB / CHEMBL1201585**, with **13 live trials** and no refusal. `Which trials evaluate I-124-labelled trastuzumab?` and `Who sponsors trials of I-124-labelled trastuzumab?` each return **12 originator evidence rows**. The natural phrase **`trastuzumab labelled with I-124`** does exactly the same. The explicit word `labelled` makes these one product description, not a coincidental list of two names.

The mass-first controls **`124I-labelled trastuzumab`** and **`trastuzumab labelled with 124I`** refuse; both QA queries then have zero evidence. Bare `trastuzumab` remains available. Shorter `I-124 trastuzumab`, `trastuzumab I-124`, no-hyphen `I124`, lowercase `i-124`, and bracketed `[I-124]` also leak. `I-124-labelled trastuzumab, osimertinib` still selects the wrong TRASTUZUMAB centre; the separately tested `osimertinib, trastuzumab I-124` selects OSIMERTINIB but leaves the tracer accepted as another drug.

[All current/previous stage captures](new_results.json), [compact summary](new_summary.json), [168 actual CLI HTTP responses](new_http.json), [server lifecycle](new_lifecycle.json), [helper and identity evidence](helper_identity_evidence.json).

| Stage | `I-124-labelled trastuzumab` | `124I-labelled trastuzumab` |
|---|---|---|
| Raw resolver | CONTAINED_ALIAS + UNRESOLVED; no BLOCKED component | BLOCKED_CLASS_TERM, radiotracer_guard |
| `_qualified` | false | true |
| `_resolver_blocked` | `{}` | CHEMBL1201585 veto |
| `_marked` actual call | `None`, both tokens in segment 0 | not reached, already refused |
| `_whole_name` | `None` | `None` |
| Public linker | TRASTUZUMAB, no Refused | Refused only |
| Map | CHEMBL1201585 / 13 trials | refused |
| Trial QA / sponsor QA | 12 / 12 | 0 / 0 |

**Cause:** `_medical_isotope_in` accepts mass-first isotopes at `src/query.py:139-145`, but its element-first regex requires **exactly two letters** at `src/query.py:146-148`. `I-124` becomes `i124` within a single original token, but `_medical_isotope_in('i124')` is false. This is not the expressly excluded cross-word one-letter case: the input isotope is wholly within `I-124-labelled` or `I-124`. `_marked` therefore misses both the whole-item and same-word checks at `src/query.py:375-379`. Earlier isotope/tracer regexes also require mass first (`src/textrules.py:289,303-314`; used by `src/normalize.py:740-743`). `_qualified` has no independent guard for this spelling (`src/query.py:184-205`), so no layer recovers the refusal. `Engine.explore` selects the surviving positive hit (`src/app.py:88-95`).

The asymmetry is visible even in the newly added helpers: `_labelled('I-124')` is **true** because the preferred-name path accepts one-letter element-first labels (`src/query.py:152-162`), whereas `_medical_isotope_in('i124')` is **false**. The medical table already contains iodine 124 (`src/query.py:126`); this is an orientation gap, not a missing mass or an inference about an unlisted isotope.

**Identity evidence:** the original clinical study constructed iodine-124-labelled trastuzumab as a PET radioligand, distinct from unlabelled trastuzumab ([Guo et al., primary study](https://pubmed.ncbi.nlm.nih.gov/31919745/)). NCI explicitly uses `[I-124]` in a radioconjugate abbreviation ([NCI Drug Dictionary](https://www.cancer.gov/publications/dictionaries/cancer-drug/def/iodine-i-124-cpd-1028)); FDA names the isotope IODINE I-124 ([FDA GSRS](https://precision.fda.gov/ginas/app/ui/substances/6432f496-edbb-4482-b6a0-00f18498bf8a)). These sources support tracer identity and spelling; no efficacy or clinical-use recommendation is inferred.

**Corroboration:** `vinblastine H3`, `vinblastine H-3` and `[H-3] vinblastine` draw VINBLASTINE / CHEMBL159 with 5 live trials and 5/5 trial/sponsor QA rows. The stored `[3h]-vinblastine` identity, `vinblastine 3h` and repaired `3hvinblastine` refuse. This is the same element-first failure, not a second inflated finding.

**Introduction:** both current and HEAD^ query modules leak the representative cases when run against the same current app/data. It is an inherited gap newly reproduced in this round. This comparison does not reconstruct the complete old deployment. The original approval bar still forbids the resulting originator map.

**Required result:** preserve refusal when an unambiguously radiolabelled product uses the element-first form of a one-letter isotope within a word. Check actual resolver/linker/map/QA responses with paired mass-first controls. No fix was implemented.

## Prior exact reproductions

The source input lists of `focused.py` (41 cases), `fresh.py` (27), `edge_probe.py` (29) and `targeted_probe.py` (29) were reused, preserving **97 original m14 cases and 29 m15 cases**. Every process exited 0. Only output location and in-memory previous-module name changed. See [reuse manifest](reuse_manifest.json), [execution summary](execution_summary.json).

| Historical family | Status | Evidence |
|---|---|---|
| M12 consumed split-symbol `[89Z.r]-DFO-daratumumab` family | FIXED | [focused results](focused_results.json) |
| M13 `89ZrDFO-daratumumab` and punctuation/case family | FIXED | [fresh results](fresh_results.json) |
| M13/M14 `A33124I` and M15 lowercase `A33124i` / `a33124i` residual | FIXED | [targeted results](targeted_results.json) |
| M14 upper-case and lower-case 3H-vinblastine / M15-B2 | FIXED | `3hvinblastine` now refuses; comma-separated osimertinib survives. [targeted results](targeted_results.json) |
| M14 PANITUMUMAB PET/CT suffix family | FIXED | [edge results](edge_results.json) |
| M15-B1 `89-ZrDFO trastuzumab`, reverse `trastuzumab DFO89-Zr`, split-symbol variants | FIXED | All original cases refuse; separately listed osimertinib survives. [targeted results](targeted_results.json) |

The original bare-drug, dose and development-code controls remain available, including `13-cis retinoic acid`, `BKM-120NX`, `NSC-118218H`, `DX-8951F`, `GW572016F`, `osimertinib 80 mg`, `paclitaxel 2 cycles` and `cisplatin 75 mg/m2 day 1`.

## Supplemental exploration, not extra blockers

The 428-variant / 104-stored-key transformed-alias scan was rerun. Its 175 accepted variants of originally refused strings are **not** a defect count: the pool includes labelled drugs, isotope-shaped development codes and chemical locants. Compared with the m15 artifact, only five cases changed: `A33124i`, `a33124i` and `3hvinblastine` now refuse; two completely run-together systematic SIROLIMUS aliases now refuse because their chemical text includes `3h`. This is a **new conservative transformed-alias availability loss**, not a demo regression or originator leak. The exact stored SIROLIMUS alias remains accepted. Full exact strings: [comparison](alias_variants_comparison.json); [all variants](alias_variants.json).

`18 FDFO trastuzumab` and `18 F DFO trastuzumab` draw TRASTUZUMAB while their joined controls refuse. These are recorded in the 42-case matrix but are **not promoted**: the current brief expressly limits the new one-letter check to within a word. The promoted I-124 inputs meet that within-word constraint.

The `_labelled` preferred-name sweep identified 14 labelled names (see [list](labelled_names.json)); it did not find an ordinary preferred name spuriously exempted by a chemical locant. A separate DB/UI reviewer investigates isotope mismatch on an already labelled preferred name.

## Execution

The new 42-case matrix captures each current and HEAD^ stage and runs all four HTTP paths per case: **168/168 HTTP 200** from unmodified `src/app.py` on owned port **8970**. Served page bytes equal `web/try.html`; the database SHA check is unchanged; the spawned server is stopped and the port closed. [Lifecycle](new_lifecycle.json).

Commands from repository root (bytecode disabled; no application writes):

```text
python -B audit_evidence_claims/m16/attacks/reuse.py
python -B audit_evidence_claims/m16/attacks/new_probe.py
python -B audit_evidence_claims/m16/attacks/new_http.py
python -B audit_evidence_claims/m16/attacks/compare_alias_variants.py
python -B audit_evidence_claims/m16/attacks/finalize.py
```

Recommended spec verdict: CHANGES REQUIRED.
