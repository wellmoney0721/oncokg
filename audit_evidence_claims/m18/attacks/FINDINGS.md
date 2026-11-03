# Round 18 attack and specification review

HEAD **4bed79c1f170ebe1efa3d452ce4398cce17b2113**; query-only counterfactual **4df54ae7f8bd16babc4ccb2dd0e8d4ce0314098b**. **One newly promoted P1 family: full element-name isotope notation passes every refusal stage and maps the unlabelled originator.** This is an inherited hole reproduced on both versions, not a demonstrated regression introduced by the latest patch. Original M17-B1 is FIXED.

## M18-B1 — P1: iodine-124 wording draws unlabelled trastuzumab

**Exact input:** `trastuzumab radiolabelled with iodine-124`.

The actual CLI server returns HTTP 200 for `/api/explore` and draws **TRASTUZUMAB / CHEMBL1201585**, with **13 live trials**, without a refusal. `Which trials evaluate trastuzumab radiolabelled with iodine-124?` and `Who sponsors trials of trastuzumab radiolabelled with iodine-124?` each return **12 originator evidence rows**. Changing only `iodine-124` to `I-124` or `124I` produces a refusal and zero trial/sponsor evidence. Bare trastuzumab remains available.

The input explicitly describes a radiolabelled product; it does not merely list iodine separately from trastuzumab. The original study constructed a PET radioligand by labelling trastuzumab with iodine-124, and PubMed indexes Iodine-124 as a substance for that study. This establishes the tracer/originator distinction for the primary example. [Guo et al., original study, PMID 31919745](https://pubmed.ncbi.nlm.nih.gov/31919745/). The notation and clinical product distinction were freshly checked, not inferred solely from a spelling pattern. No medical recommendation is made.

The original approval bar says there must be no known way to draw a refused product as the originator. The paired symbol spelling of this same tracer is refused, whereas the ordinary full element name bypasses every stage. [Full stage records](new_results.json), [summary](new_summary.json), [actual HTTP requests/responses](new_http.json).

| Stage | `trastuzumab radiolabelled with iodine-124` | `trastuzumab radiolabelled with I-124` |
|---|---|---|
| Raw intervention resolver | CONTAINED_ALIAS + UNRESOLVED; no BLOCKED component | CONTAINED_ALIAS + UNRESOLVED |
| `_qualified` | false | false |
| `_resolver_blocked` | `{}` | `{}` |
| `_item_has_isotope` | false | true |
| Actual `_marked` call | `None`; four tokens, all segment 0 | returns refusal |
| `_whole_name` | `None` | `None` |
| Public linker | Drug TRASTUZUMAB; no Refused | Refused only |
| Map | CHEMBL1201585, 13 trials | refused, no centre |
| Trial / sponsor QA | 12 / 12 | 0 / 0 |

**Code cause:** the medical-mass table keys are element **symbols** (`src/query.py:124-128`). `_medical_isotope_in` only reads one/two-letter symbols (`src/query.py:136-150`); `_item_has_isotope` tries the canonical token, punctuation-separated pieces, and each adjacent concatenation, but never converts a full element name to its symbol (`src/query.py:154-173`). For `iodine-124`, the checked keys include `iodine124`, `iodine`, `124`, and `iodine124`; none becomes `i124`. The inverse regex may see `ne124`, and the one-letter inverse regex cannot treat the final `e` as a standalone element. [Exact helper inputs](helper_evidence.json).

Earlier layers also have no full element-name radiolabel rule: `_qualified` delegates to product/tracer patterns (`src/query.py:207-229`), whose isotope expressions accept only one/two-letter symbols (`src/textrules.py:289-314`). `_resolver_blocked` cannot block this input because its recorded components are CONTAINED_ALIAS and UNRESOLVED (`src/query.py:301-319`). `_marked` sees no recognised neighbouring/own isotope and the item check is false (`src/query.py:370-400`). `Engine.explore` therefore selects the surviving positive Drug (`src/app.py:88-95`). This is not a whole-name override, database alias corruption, or loss of a previously recorded refusal.

**Corroborations:** `iodine-124 trastuzumab`, `trastuzumab iodine-124`, `trastuzumab labelled-iodine-124`, `trastuzumab iodinated with iodine-124`, `trastuzumab (iodine-124)`, and `trastuzumab [iodine-124]` have the same wrong centre and 12/12 QA evidence. Uppercase, underscore and colon variants also bypass. Comma/and reversals keep the tracer as an accepted Drug even when OSIMERTINIB is selected first. Full-name zirconium-89/copper-64 forms behave the same, while their symbol controls refuse. Other synthetic element/drug pairs are common-cause probes, not claims that each is a marketed product or independent blockers.

**Required behaviour:** recognise this explicit iodine-124-labelled product consistently with its I-124/124I spellings; it must not draw unlabelled TRASTUZUMAB. Retain ordinary drugs, code/salt aliases and dose/schedule controls. No application repair was made.

## Earlier attack reproductions

All reused scripts retain their original case literals. Changes are limited to output names, module labels, owned ports, and the separate new input list. [Reuse manifest](reuse_manifest.json), [literal comparison](literal_preservation.json), [execution results](execution.json).

| Earlier reproduction | Status | Fresh evidence |
|---|---|---|
| M12 split-symbol stored alias and neighbour spellings | FIXED for promoted blocker forms | 41 focused cases in [focused_results.json](focused_results.json); accepted spelling supplements are not silently relabelled as fixed |
| M13 chelator/isotope prefix forms | FIXED for promoted blocker forms | 27 cases in [fresh_results.json](fresh_results.json) |
| M14 uppercase one-letter isotope / PET-CT suffix forms | FIXED for promoted blocker forms | 29 cases in [edge_results.json](edge_results.json) |
| M15 lowercase mass-first / isotope-chelator forms | FIXED for promoted blocker forms | 29 cases in [targeted_results.json](targeted_results.json) |
| M16 element-first one-letter isotope | FIXED | 42 cases in [previous_results.json](previous_results.json); [168 HTTP responses](previous_http.json) |
| M17 punctuation boundary before one-letter isotope | FIXED | All 63 original cases rerun. `trastuzumab labelled-I-124`, `iodine-I-124 trastuzumab`, and family now refuse; 24 prior leaked-centre cases improve. [Stages](m17_results.json), [252 HTTP responses](m17_http.json) |
| Transformed stored isotope aliases | No newly changed outcome | 428 variants / 104 keys; zero centre/refusal changes versus m17. [Comparison](alias_variants_comparison.json) |

The separate historical-name reviewer supplies the exhaustive m1–m17 per-finding dispositions, including accepted over-refusals and old nonblocking supplements. These grouped attack counts are not substituted for that table.

## Additional observations not separately promoted

- `trastuzumab labelled-I-1-24` still bypasses while `trastuzumab labelled-I-124` refuses: a reverse isotope spread across three punctuation pieces can escape the adjacent-pair budget. The split mass is an artificial spelling; it is not needed to establish M18-B1. The same applies to `labelled-C-1-4`. [Stage records](new_results.json).
- `trastuzumab labelled-I 124` bypasses. The documented item rule intentionally excludes one-letter symbols across whitespace to protect text such as `13 NSCLC`. This is recorded without calling that deliberate scope choice a new patch regression.
- A preferred-name `_labelled` inventory contains 14 visibly isotope-labelled drug names; no accidental exemption for a clearly unlabelled preferred name was observed. A synthetic `FDG labelled-C-14` selects the stored F18 product while `FDG 14C` refuses, because an already-labelled preferred name bypasses the item-wide guard. This is an unpromoted isotope-compatibility concern, not the originator blocker; product identity for that synthetic input was not independently established. [Inventory](labelled_preferred_names.json), [probe](labelled_exception_probe.json).

## Specification review

Spec source: the user's Round 18 brief and original map guarantees. The latest patch implements its stated punctuation-piece/adjacent-pair rule, and exact M17-B1 reproductions are fixed. No scope-creep finding is identified.

**One P1 specification failure:** the original approval bar forbids drawing a refused tracer as its originator. `trastuzumab radiolabelled with iodine-124` is the same labelled product whose `I-124`/`124I` spellings are refused, but all resolver/linker guards miss it, the live HTTP map draws CHEMBL1201585 with 13 trials, and trial/sponsor QA each supplies 12 originator rows. Full element names never become the symbol-keyed isotope labels in `src/query.py:124-173`; the positive hit survives at `src/app.py:88-95`. Fresh primary identity evidence and paired stages/HTTP are above.

Both current and HEAD^ query code exhibit the miss against the same current data/app modules. Thus the latest repair succeeds on its exact target while an inherited tracer-identity hole remains. Known over-refusals and ChEMBL bevacizumab-code curation do not determine this finding. **Specification: one newly promoted P1 family; CHANGES REQUIRED.**

## Execution and limits

Eleven probe/replay scripts exit zero: **231 historical staged cases + 64 fresh current/HEAD^ pairs**, **676 actual CLI HTTP requests**, all 200. Three owned ports (9130–9132) close; served page bytes equal the worktree; DB SHA-256 is unchanged in each server lifecycle. [Final assertions](final_checks.json), [new server lifecycle](new_lifecycle.json), [M17 lifecycle](m17_lifecycle.json), [M16 lifecycle](previous_lifecycle.json).

Direct paired probes use SQLite read-only connections. Counterfactuals change only the query module; they are not full old deployments. QA calls use the application's no-LLM path. No tracked file was edited; all attack artifacts are under m18/attacks. The scripts' timings overlapped other reviewers and are not isolated cost estimates.
