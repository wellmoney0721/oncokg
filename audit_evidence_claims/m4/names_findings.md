# M4 independent name/linker and QA audit

HEAD `bf436c6`; immediately preceding linker `574097f`. All application code and real data unchanged. New scripts/results live only in m4; old scripts were inspected, copied and their output directory changed before execution. All QA uses `Engine.ask`, hence `use_llm=False`. New isolation engines reopen SQLite with `mode=ro`.

## Disposition of the earlier name findings

“FIXED” is limited to each named reproduction, not a certification of every product description.

| Earlier reproduction | Status | Current evidence |
|---|---|---|
| M1 B1: `bevacizumab - awwb`, `89Zr - trastuzumab`, `[89Zr] trastuzumab`, unspaced controls | FIXED | No centre; refusal returned. `names_reproduction_results.json` includes 62 original boundary inputs. |
| M1 S5: `Roche`, `MET`, `osimertinib EGFR`, `EGFR osimertinib`, `Mvasi and bevacizumab` | FIXED | Stored-alias reading still selects FOLIC ACID/METFORMIN/first hit but alternatives and refused spans are disclosed. |
| M1 salt/parent controls: Tarceva, erlotinib hydrochloride, erlotinib, osimertinib mesylate | FIXED / preserved | CHEMBL1079742, CHEMBL1079742, CHEMBL553, CHEMBL3545063 respectively. Parent no longer appears as a second entity solely from the salt phrase. |
| M2b R1: `osimertinib and generic version of bevacizumab`, reversed and comma forms; trial/sponsor QA variants | FIXED | Separately named osimertinib retained; generic bevacizumab refused. `names_regressions.json`, `names_boundary_details.json`. |
| M2b R1 related: `[89Zr] trastuzumab and osimertinib`, reverse; `osimertinib and oral azacitidine`, reverse | FIXED | OSIMERTINIB retained. |
| M2b inherited `What is the generic version of bevacizumab?`, also M3-B2 | FIXED | Refuses `generic version of bevacizumab`; no centre/evidence. |
| M2b multi-company alias fixture, `Sharedbrand company` | FIXED | Index-only fixture preserves Roche in `also`; `names_boundary_details.json`. Production multi-ID company alias count remains zero. |
| M3-B1: `paclitaxel with albumin bound nanoparticles`, formulation variants; `generic version with bevacizumab`; trial QA | FIXED | Parent refused, no map centre or QA evidence. `names_new_boundaries.json`. |
| M3 comma over-refusal: `osimertinib, liposomal doxorubicin`, `osimertinib, biosimilar bevacizumab`, reverse and trial QA | FIXED | OSIMERTINIB retained. |
| M3 supplementary control: `osimertinib with generic version of bevacizumab` | NOT FIXED — new regression | 574097f retains osimertinib; HEAD draws bevacizumab. See N1. This input was already in m3's supplementary script, though not a report blocker. |
| M3 supplementary control: `generic version of Paclitaxel conjugate with poly-l-glutamic acid` | NOT FIXED — new regression | 574097f refuses; HEAD draws PACLITAXEL POLIGLUMEX. See N2. |
| Unsupported lowercase IDs and Investigator names | NOT FIXED — unchanged qualification | `chembl3353410`, `nct00200395`, `Armando Santoro Md` still not found. `CHEMBL3353410`, `NCT00200395`, `ORG:armandosantoromd` work. All six exact prior controls freshly rerun in `names_unsupported_forms.json`. Not an invented relationship. |

The retained replay entry points are `names_reproduction.py`, `names_regressions.py`, `names_boundary_details.py`, `names_new_boundaries.py` and `names_label_scan.py`; all exited 0. The first three retain their old bfcb83d comparison for historical continuity. `names_new_boundaries.py` retains its c64f433 comparison. **Latest-repair causation is established separately by `names_attack.py`, using the exact 574097f method and its exact `_JOINERS` global**, not by conflating the older comparisons with HEAD's parent.

## N1 — P1 new regression: shortest span can bind the qualifier to the other drug

Exact input: `osimertinib with generic version of bevacizumab`.

HEAD returns centre BEVACIZUMAB / CHEMBL1201583, 122 trials, and `also=[{"refused":"osimertinib with generic version"}]`. The immediately previous linker returns OSIMERTINIB / CHEMBL3353410 and refuses `generic version of bevacizumab`. Reversing the drug names gives the symmetric failure: `bevacizumab with generic version of osimertinib` selects OSIMERTINIB and refuses the bevacizumab prefix. The existing resolver refuses the complete product-containing input; there is no external pharmacological assumption.

`_drug_spans` discovers each drug separately. `_qualified_drug_spans` iterates the left drug first (`src/query.py:255`). Both `osimertinib with generic version` and `generic version of bevacizumab` have length four and satisfy the product predicate. The strict `<` update (`271-272`) retains the left candidate. `out` then prevents the right drug from using the qualifier (`264`), so ordinary linking accepts it (`181-189`). Removing `with` from `_JOINERS` (`92-96`) enabled this regression. A shortest token span does not establish semantic attachment.

QA on the plain input now gives BEVACIZUMAB profile/VEGFA evidence instead of OSIMERTINIB profile/EGFR evidence. `names_final_checks.json` verifies the exact full questions against 574097f: `Which trials evaluate osimertinib with generic version of bevacizumab?` changes its first edge from `NCT03909334|EVALUATES|CHEMBL3353410|NCT03909334` to `NCT00955305|EVALUATES|CHEMBL1201583|NCT00955305`; `Which companies sponsor osimertinib with generic version of bevacizumab?` changes AstraZeneca/osimertinib to Roche/bevacizumab. Both retain 12 rows. Root's `attack_http.json` also exercises these over the unchanged CLI server. This fails the refusal/subject guarantee regardless of whether a graph edge is itself real.

Evidence: `names_attack.json` (full current/previous/counterfactual results), `names_new_boundaries.json` (rerun prior supplementary case).

## N2 — P1 new regression plus inherited remote-qualifier failures: six-token ceiling

Exact new regression: `generic version of Paclitaxel conjugate with poly-l-glutamic acid`.

The five-token suffix is a stored unambiguous alias for PACLITAXEL POLIGLUMEX / CHEMBL2108628. Unqualified, it correctly selects that entity in both versions. Qualified, HEAD still selects it, shows 4 graph trials, and reports no refused span. `Engine.ask` returns 7 profile/mechanism evidence rows; the 574097f linker refuses and returns zero. The unchanged resolver reports `BLOCKED_DISTINCT_PRODUCT` for the full input.

Before/after qualification: the plain phrase above is the new map/QA regression. The longer question `What targets does generic version of Paclitaxel conjugate with poly-l-glutamic acid act on?` already bypassed the previous linker and returns the same 12 target evidence rows in both versions. `Which trials evaluate generic version of Paclitaxel conjugate with poly-l-glutamic acid?` likewise returns 4 in both. Those longer-question failures are inherited, not newly attributed. Exact comparisons are in `names_final_checks.json`.

The helper requires a candidate to include the entire matched drug span, while `range(b-a, 7)` (`src/query.py:258`) permits only up to six tokens. The full eight-token phrase cannot be examined; `generic version` is not a single-token predicate, so nothing in the prefix is refused either. Ordinary longest-first alias matching accepts all five drug tokens (`166-189`). The no-relink counterfactual still selects the same centre: this failure is the refusal algorithm, not removing nested aliases.

Inherited remote-qualifier cases expose the same ceiling: `generic version of the anticancer drug bevacizumab` (seven tokens) and `generic version of the commercially available monoclonal antibody bevacizumab` select BEVACIZUMAB. The six-token control `generic version of the drug bevacizumab` refuses. `paclitaxel formulated with nanoparticles that are albumin bound` selects PACLITAXEL. These full strings satisfy the existing product predicate; the long generic bevacizumab case also produces 12 bevacizumab trial evidence rows when asked as a trial question. Such remote failures existed before, but HEAD now omits even the old detached qualifier refusal.

Evidence: `names_attack.json`, `names_attack.py`; server confirmation in root's `attack_http.json`.

## N3 — P1 inherited failure: pre-refused qualifier cannot extend to its drug

`biosimilar version of bevacizumab` selects BEVACIZUMAB / CHEMBL1201583 and refuses only `biosimilar version`. `liposomal formulation of doxorubicin` selects DOXORUBICIN / CHEMBL53463 and refuses only `liposomal formulation`. Both complete inputs are `BLOCKED_DISTINCT_PRODUCT` at the unchanged resolver. Trial questions return 12 bevacizumab rows and 3 doxorubicin rows respectively. Before and after results are identical in this essential failure, so it is not attributed as a new regression.

The token pass at `src/query.py:143-151` initially refuses each qualifier and its immediate neighbours. The helper rejects every candidate touching that `refused` set (`264`); it therefore cannot connect the known qualifier to the later named drug, even within four tokens. `liposomal formulation of doxorubicin and biosimilar version of bevacizumab` links both originators. In contrast, `liposomal doxorubicin and biosimilar bevacizumab` correctly refuses both products.

Hyphenated `paclitaxel with albumin-bound nanoparticles` is an already exercised same-mechanism control from m3: the one-token albumin-bound pass refuses its neighbours but leaves PACLITAXEL. Exact 574097f comparison in `names_separator_checks.json` confirms it is inherited (7 profile/mechanism rows in both versions; the trial question has 12 in both). The repaired unhyphenated `albumin bound` case does not establish the broader guarantee.

## Other design attacks and unchanged limitations

- Two qualified drugs: `generic version of bevacizumab and generic version of osimertinib` and the `with` variant refuse both. Mixed attached `liposomal doxorubicin and biosimilar bevacizumab` also refuses both. Remote single-token qualifier variants fail as N3.
- Qualifier between two drugs: N1 gives a clear `with ... of` attachment counterexample. `bevacizumab generic version osimertinib` picks the left span and retains osimertinib; this text is semantically ambiguous, so it is a mechanism probe rather than an additional independent blocker.
- Targets/companies near qualifiers: `EGFR generic version of bevacizumab` and `AstraZeneca generic version of bevacizumab` now preserve the target/company. `EGFR biosimilar bevacizumab` and `AstraZeneca biosimilar bevacizumab` still swallow those entities; reverse order preserves them. This is inherited over-refusal and a should-fix, distinct from originator leakage. `src/query.py:149-151` still grabs any adjacent non-joiner, including non-Drug entities.
- `Roche generic version of bevacizumab` selects bevacizumab after binding the qualifier to Roche's stored FOLIC ACID drug alias. This is a related alias-collision amplification of N1, not a claim that the dictionary's Roche alias is new.
- Semicolons/fullwidth commas are not list boundaries: `osimertinib; generic version of bevacizumab` and `osimertinib， generic version of bevacizumab` newly select bevacizumab. Exact 574097f comparisons in `names_separator_checks.json` show both plain inputs previously refused with no centre and no evidence; current plain-input QA returns two bevacizumab profile/mechanism rows. These are additional new binding regressions related to N1. Adding the prefix `Which trials evaluate` produces 12 bevacizumab trial rows in both versions, so those longer-question failures are inherited. The normal comma control retains osimertinib in both. The fullwidth comma is preserved as U+FF0C in the script and recorded codepoints.
- M1 Unicode/unknown controls and long HTTP inputs were rerun. Product spellings accepted by the resolver itself (e.g. `ABP 215`, `89Zr trastuzumab`, unsupported Unicode suffix punctuation) are recorded, not misrepresented as a new linker/resolver mismatch.

## Matched-span non-relinking isolation

This change is tested independently from the refusal changes. A separate Engine uses exactly HEAD with only `(refused | matched)` replaced by `refused` in `link_entities`; `_qualified_drug_spans`, `_drug_spans`, globals, retrieval, data and model setting remain identical.

- `names_attack.json`: 45 focused attack inputs; 37 varied QA questions including all 7 distinct page/CLI demos; **all 7 demo responses identical to 574097f**. Of the 37 ordinary QA controls, 13 differ only in entity metadata, and none has a different evidence list. Controls cover drug salts, parent+salt explicitly repeated, companies, targets, disease names, multi-entity order and multi-token aliases.
- The same artifact scans **2,584 multi-token unambiguous alias keys**. **402** change their linked entity lists, but no first accepted identity changes and no new Drug appears. Salt parents, compound-word companies and embedded targets are no longer read from an already accepted alias. This is scoped to those stored keys, not every possible sentence.
- `qa_relink_sweep.json`: four question templates for all 400 alias keys changed specifically by the no-relink toggle, plus 48 company/target/mixed controls: **1,648 questions; 28 identical responses, 1,596 entity-metadata-only changes, 24 semantic changes, zero exceptions**.
- Every semantic change is `company_portfolio` → `drug_profile` after removing a nested Company hit from an accepted Drug alias. Example: `Tell me about GSK 1120212` previously supplies 12 GlaxoSmithKline portfolio rows; HEAD supplies 3 TRAMETINIB profile/mechanism rows. `Tell me about EPOETIN BETA` previously sees Company Beta and returns no evidence; HEAD returns the named drug's two profile/mechanism rows. These observed changes support the intended repair. No adverse QA regression attributable specifically to non-relinking was found in this sweep.

`qa_relink_sweep.py` retains every generated question and full results for every semantic difference. The sweep intentionally records entity-only changes separately so a changed entity count is not mistaken for changed evidence. New refusal failures N1/N2 persist in the no-relink counterfactual and therefore cannot be assigned to this separate repair.

## Required result

Retain the exact fixed earlier cases and intended removal of nested aliases, while ensuring a qualifier belongs to the right named drug and can still reach that drug across ordinary descriptive words. The current implementation has two new prior-control regressions and inherited product bypasses. Names/specification axis recommends **CHANGES REQUIRED**.
