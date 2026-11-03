# Round 13 independent refusal attacks

Reviewed HEAD `481100c584ec772cc2332960ba5d3b28ba36ae6f`. **One P1 blocker, M13-B1:** removing an isotope/chelator boundary in a stored tracer alias still draws its originator. Every refusal stage misses it. This is inherited from HEAD^, not a newly introduced regression. The exact M12-B1 inputs are fixed.

## M13-B1 ? isotope/chelator boundary erased inside a matched alias

**Exact HTTP request:** `POST /api/explore`, JSON `{"text":"89ZrDFO-daratumumab"}`.

**Actual:** HTTP 200, centre **DARATUMUMAB / CHEMBL1743007**, matched alias **`89zr-dfo-daratumumab`**, **2 live trials**, and no Refused entity or refusal notice. `Which trials evaluate 89ZrDFO-daratumumab?` and `Who sponsors trials of 89ZrDFO-daratumumab?` each return **2 originator evidence rows**. The fully glued `89zrdfodaratumumab`, `[89ZrDFO]-daratumumab`, `89Z.rDFO-daratumumab`, `89ZrDFO daratumumab`, and `89-ZrDFO-daratumumab` do likewise. Adding `, osimertinib` still selects DARATUMUMAB. [Full stages](fresh_results.json), [compact matrix](fresh_summary.json), [actual CLI HTTP](fresh_http.json).

**Identity/control evidence:** the candidate and refused `[89Zr]-DFO-daratumumab` have the identical canonical key **`89zrdfodaratumumab`**, which the dictionary maps uniquely to the AACT synonym `89zr-dfo-daratumumab` for DARATUMUMAB. The refused controls `89Zr-dfo-daratumumab`, `[89Zr]-DFO-daratumumab`, and `89Zr-DFOdaratumumab` produce no centre and zero qualified trial/sponsor rows. Bare `daratumumab` remains available. These are alternative spellings accepted as the same stored alias by the application's own key; no external pharmacology assumption is necessary. [Dictionary and predicates](dictionary_evidence.json).

| Stage for `89ZrDFO-daratumumab` | Result |
|---|---|
| Raw resolver | `ALIAS` / CHEMBL1743007, no blocked component |
| Resolver veto | `{}` |
| Item linker | Drug DARATUMUMAB, no Refused |
| Whole-name shortcut | `None`; no previously recorded refusal is overridden |
| Public linker | Drug DARATUMUMAB, no Refused |
| Map | DARATUMUMAB / CHEMBL1743007, 2 trials |
| Trial / sponsor QA | 2 / 2 originator evidence rows |

The source explains this result:

1. Positive lookup removes every non-letter/digit through `canonical_key` (`src/textrules.py:339-346`) and consumes the complete stored alias (`src/query.py:413-426`).
2. `_alnum_words` splits only at separators (`src/query.py:111-113`). The candidate therefore has `['89ZrDFO', 'daratumumab']`, not an `89Zr` word. The new inside-name scan glues whole words but cannot split an alphanumeric word (`src/query.py:258-268`); its six-character limit also stops the first word, whose length is seven. Fully glued input similarly contains no word equal to an isotope.
3. No outside neighbour contains the isotope (`src/query.py:274-290`), because the whole alias was consumed.
4. The isotope-plus-same-drug fallback can isolate `89zr`, but requires remainder `dfodaratumumab` to be a separate dictionary alias of the same drug (`src/query.py:292-296`). That key is absent. `daratumumab` is present.
5. The raw tracer predicate expects a separator or bracket after the isotope and does not recognize the alphanumeric `89ZrDFO` (`src/textrules.py:303-314`, `src/normalize.py:740-745`). `_qualified` likewise returns false (`src/query.py:119-142`). `Engine.explore` selects the surviving positive hit (`src/app.py:87-95`).

**Required outcome:** positive alias normalization must not erase the refused tracer identity when the isotope becomes glued to a chelator or another part of a known tracer alias. Checking only whole alphanumeric words is insufficient; preserving identity must not depend on a nonexistent isotope-stripped remainder alias. No application changes were made.

**Version attribution:** both current and the exact HEAD^ query module (`d9260a1ea544cf7bb80415383667784e0aba146a`) leak these new spellings. The comparison uses the current app, normalization/rules and database with only query.py swapped. It is a same-data module counterfactual, not a reconstruction of an old deployment. [Version-labelled stages](fresh_results.json).

## Earlier reproductions and controls

The unchanged m12 `focused.py` case list (41 inputs) and `http_probe.py` case list (19 names, 76 requests) were reused; only labels and output/owned-port context were adapted. [Manifest](reuse_manifest.json), [execution](execution.json), [original-case stages](focused_results.json), [original-case HTTP](new_leaks_http.json).

| Historical finding / input | Current disposition |
|---|---|
| M12-B1 `[89Z.r]-DFO-daratumumab`, `89Z_r-dfo-daratumumab`, `89Z.r-dfo-daratumumab`, `89Z.r dfo daratumumab`, `89Z.r-dfo daratumumab` | **FIXED**: no centre and no trial/sponsor originator evidence. HEAD^ still leaks each. |
| M12-B1 `[89Z.r]-DFO-daratumumab, osimertinib` | **FIXED**: only OSIMERTINIB selected, tracer refusal disclosed; 12/12 QA rows concern the separately named drug. |
| M12-S1 `rad001c` | **NOT FIXED**, previously recorded nonblocking over-refusal. `RAD001` reaches EVEROLIMUS. |
| M11/M12 supplementary descriptive isotope forms, e.g. `trastuzumab labelled with [89Zr]`, `[89Z.r]-labelled trastuzumab`, `[89Z.r]-DFO trastuzumab` | **NOT FIXED** as previously recorded. Retained as supplementary observations, not additional blockers or new regressions. |
| M12 supplementary `Lutetium (177L.u) dotatate` | **FIXED**: now refuses. Its previous centre was already LUTETIUM OXODOTREOTIDE LU-177, so it was not an unlabelled-originator blocker. |
| M12 supplementary `b.i.o.similar bevacizumab` / `lip.osomal doxorubicin` | **NOT FIXED**, inherited unusual respellings, not promoted to additional blockers. |
| M11/M12 immediate isotope and suffix controls `[89Z.r] trastuzumab`, `trastuzumab [89Z.r]`, `bevacizumab a - w w b`, plus `bevacizumabawwb` / `89zrtrastuzumab` | **FIXED**: no originator map or qualified QA evidence; separate osimertinib survives. |
| Dose/schedule `osimertinib 80 mg`, `paclitaxel 2 cycles`, `cisplatin 75 mg/m2 day 1` | Expected drugs remain selected; 12/12 trial/sponsor QA rows in both versions. |

`A33124I` is a supplementary same-mechanism case: it maps to ADAKITUG / CHEMBL5314551 through stored alias `A33 124i`, while `A33 124i` and `a33[124i]` refuse. The `a33` remainder key is absent. It has zero trial/sponsor evidence and is not counted as a separate blocker. The dictionary contains no `99mtc` keys, so no additional stored-chelator metastable-isotope claim is made. [Dictionary evidence](dictionary_evidence.json), [matrix](fresh_results.json).

Historical exhaustive m1-m12 name replays and full demo/cost checks are assigned to the other review workers; this report provides the bounded independent new attack evidence.

## Execution and integrity

- Four scripts exit 0. Reused 41-case direct comparison plus fresh 27-case direct comparison; each compares current and HEAD^ query modules.
- **184 actual HTTP requests** (76 reused + 108 fresh), all HTTP 200; no request used port 8765.
- Owned ports **19360 / 19361** are closed. Both CLI servers used unmodified `src/app.py`; served page bytes match `web/try.html`; DB SHA-256 remained unchanged. [Reused lifecycle](new_leaks_lifecycle.json), [fresh lifecycle](fresh_lifecycle.json).
- Direct probes reopen SQLite with `mode=ro`. All Engine.ask calls use its no-model path. All new scripts/results are under m13/attacks. Bytecode is disabled; HTTP TMP/TEMP/TMPDIR are confined here.
- Timings in attack execution files overlap other audit work and are not performance measurements.

Reproduce from the repository root: `python -B audit_evidence_claims/m13/attacks/run.py`. The HTTP scripts check their owned port is free and shut down only the process they start.

## Spec assessment

The exact latest repair is effective, but the approval bar still fails for **M13-B1**: a normalized spelling of a stored refused tracer alias passes every guard and draws its originator. Correct live edges around that wrongly selected centre do not satisfy the refusal guarantee. Accepted over-refusals and cost concerns do not determine this conclusion.
