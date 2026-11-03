# Round 3 — names and QA review

HEAD: `574097f67e0719c32bfdc0526133e649b1864993`. No tracked file was edited. All scripts/results created here; real DB read only. Old-method comparisons replace only `link_entities` on an isolated Engine, leaving current application/data unchanged. Fixtures touching company aliases alter only that Engine's Python index. The retired-Drug fixture is covered by the parallel DB review.

## Replayed findings

| Prior finding | Disposition | Evidence at current HEAD |
|---|---|---|
| m1 B1 spaced biosimilar/tracer | **FIXED** for every exact original reproduction | `bevacizumab - awwb`, `89Zr - trastuzumab`, `[89Zr] trastuzumab` return refusal, no centre. Unspaced controls refuse too. `names_reproduction_results.json`; `src/query.py:170-178`. The broader guarantee is blocked by the new case below. |
| m1 silent identity ambiguity | **FIXED** | `Roche` still selects FOLIC ACID but also exposes Roche; `MET` selects METFORMIN and exposes the MET Target. `osimertinib EGFR` / `EGFR osimertinib` select the first named hit and disclose the other. `names_reproduction_results.json`; `src/app.py:95-114`. |
| m1 omitted refused span beside valid entity | **FIXED** | `Mvasi and bevacizumab` selects the separately named bevacizumab and exposes `also=[{"refused":"Mvasi and"}]`. The span includes the conjunction, but the refused token is disclosed. |
| m1/m2b silent >500-character truncation | **FIXED** | Exact `"x"*500 + " osimertinib"` and `"osimertinib " + "x"*600` now return HTTP 400 `input is longer than 500 characters`, rather than silently mapping a prefix. `names_reproduction_results.json`; `src/app.py:239-241`. |
| m2b R1 mixed generic-product selection and QA subject switch | **FIXED** for the reported exact cases | `osimertinib and generic version of bevacizumab` selects OSIMERTINIB and discloses only the generic product as refused. Both trial and sponsor questions retrieve osimertinib evidence. `[89Zr] trastuzumab and osimertinib`, reverse order, and `osimertinib and oral azacitidine` retain osimertinib. `names_regressions.json`, `names_boundary_details.json`. |
| m2b embedded company multi-ID ambiguity | **FIXED** | With isolated `companies['sharedbrand']=['ORG:astrazeneca','ORG:roche']`, both `Sharedbrand` and `Sharedbrand company` expose Roche as alternative to AstraZeneca. `src/app.py:97-101`; `names_boundary_details.json`. No current multi-ID company alias exists. |
| m2b explicitly noted inherited `What is the generic version of bevacizumab?` bypass | **NOT FIXED** | Still maps BEVACIZUMAB / CHEMBL1201583; resolver says BLOCKED_DISTINCT_PRODUCT. Refused prefix `What is the generic version` consumes the five-token maximum and leaves `of bevacizumab` to link. Reproduced with original `bfcb83d`, previous `c64f433` and current linker; not newly attributed to this repair. `names_regressions.json`, `names_new_boundaries.json`; `src/query.py:157-178`. |

All 62 distinct old name-boundary inputs and the 14 extra probes in the inherited reproduction script were rerun, plus the 13 m2b regression comparisons and all 14 boundary-detail controls. The reported original scripts were copied into m3 with their output paths changed, not executed in place. Seven current retired IDs/labels were also replayed; retired IDs return not_found. A retired historical label can resolve to a different live merged company (e.g. Merck/BeOne), which is not a retired centre leaking back.

## New blocker: `with` inside a refused product description bypasses the guard

Exact input:

```text
paclitaxel with albumin bound nanoparticles
```

Current `Engine.explore` returns:

```json
{
  "center": {"id":"CHEMBL428647","label":"PACLITAXEL","trials":234},
  "also": [{"refused":"albumin bound nanoparticles"}]
}
```

The unchanged `Engine.resolve` returns **BLOCKED_DISTINCT_PRODUCT**, no drug ID, for that complete component. The immediately preceding `c64f433` linker refuses the whole phrase, yielding no map and no QA evidence. Current QA produces 7 originator-profile evidence rows. Exact question `What trials evaluate paclitaxel with albumin bound nanoparticles?` changes from 0 evidence to **12 PACLITAXEL trial edges**. The variants `paclitaxel with albumin bound formulation` and `paclitaxel with nanoparticle albumin bound formulation` reproduce the same map regression.

**Causal evidence:** new `_JOINERS` includes `with` (`src/query.py:92`), and `src/query.py:170-172` now disallows refusal of every window containing it. `src/textrules.py:144-145` explicitly treats albumin-bound descriptions as a distinct product. The remaining suffix window is refused, leaving the preceding paclitaxel token free for alias acceptance at `src/query.py:181-194`; `src/app.py:95` selects it. The code assumes every `with` separates independent things, which does not hold for this repository-refused product description. No external pharmacology assumption is needed.

The direct previous/current comparisons, current resolver output, complete QA evidence and stored-name controls are in [names_new_boundaries.json](names_new_boundaries.json), reproduced by [names_new_boundaries.py](names_new_boundaries.py). This is a current-data failure, not a DB mutation fixture. It independently fails the no-refused-product-as-originator approval criterion.

## Residual should-fix: the token refusal prepass still crosses commas

`osimertinib, liposomal doxorubicin`, `osimertinib, biosimilar bevacizumab`, `Mvasi, osimertinib` and `osimertinib, Mvasi` all refuse the separately named osimertinib. The comma is removed from the refusal label. `liposomal doxorubicin, osimertinib` and `biosimilar bevacizumab, osimertinib` retain it; the result depends on order. `Which trials evaluate osimertinib, biosimilar bevacizumab?` returns no evidence, while the resolver preserves osimertinib as an exact component.

This is **inherited / NOT FIXED**, not introduced by the latest patch. `src/query.py:139-143` still expands a refused single token to its adjacent tokens without checking `clause`; the new comma guard runs only later at `170`. The repair note's claim that refused product spans never cross commas is therefore too broad. Evidence: [names_new_boundaries.json](names_new_boundaries.json).

## Additional boundary qualifications

- `bevacizumab, - awwb` and `[89Zr], trastuzumab` now concatenate across commas into alias hits (`Bevacizumab awwb` / `89zr-trastuzumab`); the previous linker refused. The new comma guard gates only refusal, not subsequent alias lookup. However, the unchanged resolver splits these strings into an ordinary drug plus an unrecognized/isotope piece, so these punctuation-only examples are recorded as consistency evidence, not an independent claim that the whole input is a refused product.
- The stored legitimate name **`Paclitaxel conjugate with poly-l-glutamic acid`** correctly selects PACLITAXEL POLIGLUMEX / CHEMBL2108628, not PACLITAXEL as its centre, at both versions. All **21 stored alias records** containing joiner-like words were exercised; full QA outputs have **zero differences** against the immediately preceding linker. This includes `daratumumab and hyaluronidase-fihj`. Thus the new blocker concerns refusal interpretation, not a demonstrated failure to recognize that exact legitimate alias.
- Salt/parent controls remain distinct: Tarceva / erlotinib hydrochloride → CHEMBL1079742; erlotinib → CHEMBL553; osimertinib mesylate → CHEMBL3545063. Case, surrounding whitespace and fullwidth ordinary-name controls behave as in m2b. Unsupported lowercase IDs and investigator-name lookup remain inherited limitations. `names_reproduction_results.json`, `names_label_scan.json`.
- ABP-215, unhyphenated `bevacizumab awwb`, some Unicode hyphen variants, and `89Zr trastuzumab` continue to be accepted by the current resolver and linker. Those are not misclassified here as latest-repair regressions or as names the current resolver itself refuses.

## Demo QA regression check

All **7 page/CLI demo questions** have complete current response objects identical to the original `bfcb83d` linker, including entity identities and evidence IDs rather than just counts. Counts: Tagrisso trials 12; osimertinib companies 12; ALK drugs 11; osimertinib targets 1; AstraZeneca NSCLC portfolio 12; Mvasi 0; capital-of-France unsupported 0. All use deterministic answering/no language model. Evidence: [names_demo_results.json](names_demo_results.json), [names_demo_compare.py](names_demo_compare.py).

Names/QA recommendation: **CHANGES REQUIRED** for the introduced `with` product-refusal regression. R1's exact old reproduction passes; that narrow success does not establish the broader claimed boundary behavior.
