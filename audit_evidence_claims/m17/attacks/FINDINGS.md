# Round 17 refusal-stage attack evidence

HEAD: `4df54ae7f8bd16babc4ccb2dd0e8d4ce0314098b`. All new files are confined to `audit_evidence_claims/m17/attacks/`; no tracked file was edited. No model was called. Counterfactuals substitute only HEAD^ `query.py` against the current app/data; they are not full historical deployments.

## M17-B1 — P1: punctuation before an element-first one-letter isotope is lost before its boundary check

**Exact input:** `trastuzumab labelled-I-124`.

`POST /api/explore` returns HTTP 200 and draws **TRASTUZUMAB / CHEMBL1201585**, with **13 live clinical trials**, without any refusal. `Which trials evaluate trastuzumab labelled-I-124?` and `Who sponsors trials of trastuzumab labelled-I-124?` each return **12 originator evidence rows**. The same occurs for `trastuzumab labelled-with-I-124`, `iodine-I-124 trastuzumab`, and `trastuzumab (iodine-I-124)`.

The paired inputs `trastuzumab labelled-124I`, `I-124-labelled trastuzumab`, and `trastuzumab labelled with I-124` all refuse, and both QA questions have zero evidence. Bare `trastuzumab` remains available. These are one-product descriptions: the explicit word "labelled" and the I-124 isotope identify radiolabelled trastuzumab. This is not the explicitly excluded cross-word one-letter case: the isotope is wholly inside the original token `labelled-I-124`, and its preceding boundary is a visible hyphen.

Fresh primary scientific identity evidence: the original study constructed iodine-124-labelled trastuzumab for PET imaging, so the radioligand is not interchangeable with unlabelled trastuzumab. [Guo et al., original study, PMID 31919745](https://pubmed.ncbi.nlm.nih.gov/31919745/). The NCI also uses element-first I-124 notation for an iodine radioconjugate. [NCI Drug Dictionary](https://www.cancer.gov/publications/dictionaries/cancer-drug/def/iodine-i-124-labeled-hsp90-inhibitor-puh71). These establish the isotope/product distinction and notation; no medical recommendation is made.

| Stage | `trastuzumab labelled-I-124` | `trastuzumab labelled-124I` |
|---|---|---|
| Raw resolver | CONTAINED_ALIAS + UNRESOLVED; no BLOCKED component | CONTAINED_ALIAS + UNRESOLVED |
| `_qualified` | false | false |
| `_resolver_blocked` | `{}` | `{}` |
| Actual `_marked` call | `None`; both tokens in segment 0 | `trastuzumab` refusal |
| `_item_has_isotope` | false | true |
| `_whole_name` | `None` | `None` |
| Public linker | Drug TRASTUZUMAB, no Refused | Refused only |
| Map | CHEMBL1201585, 13 trials | refused |
| Trial/sponsor QA | 12 / 12 | 0 / 0 |

**Cause:** `src/query.py:164` first converts every original token to its letters-and-digits key. At `src/query.py:167`, the new `(?<![a-z])([a-z])(\d{1,3})(?!\d)` guard then sees `labelledi124`. The preceding hyphen no longer exists, so `i` is incorrectly treated as internal to a letter run. `_medical_isotope_in` still recognizes only two-letter element-first forms (`src/query.py:147-149`); no earlier helper catches this spelling. `_qualified` (`src/query.py:204-226`) and `_resolver_blocked` (`src/query.py:275-317`) also miss. The earlier `_marked` neighbour loops start at `labelled` and cannot recover the trailing element-first label (`src/query.py:358-385`). The item guard at `src/query.py:395-397` therefore returns false, and `Engine.explore` selects the surviving positive hit (`src/app.py:88-95`). [Helper evidence](helper_evidence.json).

**Introduction:** both current and HEAD^ link/map/QA results reproduce this leak. The latest change repairs the earlier spelling but leaves this inherited boundary gap. The original approval bar still forbids the originator map.

**Corroborations, not extra findings:** uppercase/lowercase, underscore, colon, attached parentheses/brackets, and reversed comma/and list orders have the same result. `vinblastine labelled-H3`, `erlotinib labelled-F18`, `paclitaxel labelled-C14`, and `cetuximab labelled-Y-90` also draw their unlabelled drugs; mass-first and bare element-first controls refuse. Their token shapes support the common code cause; only the primary iodine-124/trastuzumab scientific identity was independently sourced. No claim that each synthetic spelling is a real marketed product is needed.

**Required result:** retain genuine within-token punctuation boundaries when checking element-first one-letter isotope labels, while preserving BKM120/AZD9291 and dose/schedule controls. Check all public resolver/linker/map/QA paths with these paired inputs. No repair was implemented.

## Historical reproductions and controls

| Earlier finding / reproduction | Status | Fresh evidence |
|---|---|---|
| M16-B1 original `I-124-labelled trastuzumab`, `trastuzumab labelled with I-124`, `I-124`/`I124`/lowercase/bracket variants; H3/H-3 vinblastine corroboration | **FIXED** | Original 42-case script reused without changing inputs. [Stages](previous_results.json), [168 HTTP calls](previous_http.json). |
| M15-B1 `89-ZrDFO trastuzumab` and M15-B2 `3hvinblastine`, residual `A33124i` | **FIXED** | Reused 29 original m15 targeted cases plus explicit new-suite controls. [Targeted](targeted_results.json), [new](new_results.json). |
| M14/M15 earlier 97 isotope/case/chelator/formulation attack cases | **FIXED for prior promoted blocker cases**, with previously recorded supplemental qualifications retained by the cumulative finding table | Reused focused 41 + fresh 27 + edge 29 original inputs. [Focused](focused_results.json), [fresh](fresh_results.json), [edge](edge_results.json). |
| M16 transformed SIROLIMUS collapsed systematic-alias over-refusal (lowercase and uppercase) | **NOT FIXED**, availability-only supplemental, not an originator-map blocker | 428 transformed variants / 104 keys match m16 exactly: zero centre/refusal changes. Literal stored SIROLIMUS alias still resolves. [Sweep](alias_variants.json), [comparison](alias_variants_comparison.json). |
| Ordinary BKM120 / AZD9291, osimertinib 80 mg, paclitaxel 2 cycles, cisplatin 75 mg/m2 day 1; 13-cis retinoic acid; bare trastuzumab/vinblastine/erlotinib/paclitaxel/cetuximab | **PASS / no regression reproduced** | [63 paired cases](new_results.json), [252 actual HTTP responses](new_http.json). |

The m16 suite includes deliberately excluded cross-word one-letter exploratory inputs; their acceptance is not promoted as a blocker. All accepted user-listed over-refusals and the ChEMBL bevacizumab-code data limitation remain nonblocking. This worker does not replace the root's full per-finding historical table.

## Execution and limits

Original reused stages: **41 + 27 + 29 + 29 + 42 = 168 cases**. New staged/current-versus-HEAD^ cases: **63**. Actual HTTP: **168 old + 252 new = 420 requests**, all 200. Both owned CLI servers served the exact `web/try.html`, closed their ports, and preserved database bytes. These request latencies were gathered during parallel audit work and are not performance benchmarks.

Original and adapted script SHA-256 provenance: [primary reuse](reuse_manifest.json), [additional reuse](reuse_additional_manifest.json). All four primary runner scripts and all five additional runners exit 0. [Execution](execution_summary.json), [additional execution](reuse_additional_execution.json), [final assertions](final_checks.json). New script cases and supplemental scan are inspectable in [new_cases.json](new_cases.json) and [initial_scan.json](initial_scan.json).

Reproduce from repository root with Python bytecode disabled. `build_and_run.py` generates only m17 attack scripts and runs the original m16 suite plus the paired new suite; `reuse_additional.py` replays the additional original scripts; `finalize.py` verifies the evidence and builds the compact summary.

```text
python -B audit_evidence_claims/m17/attacks/prepare.py
python -B audit_evidence_claims/m17/attacks/build_and_run.py
python -B audit_evidence_claims/m17/attacks/reuse_additional.py
python -B audit_evidence_claims/m17/attacks/finalize.py
```

Specification axis: [SPEC_REVIEW.md](SPEC_REVIEW.md). **One new P1 family; CHANGES REQUIRED.**
