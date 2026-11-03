# Round 14 independent originator attacks

Reviewed HEAD `73ee310` against the current database. **Two P1 blockers:** a newly introduced one-letter-isotope regression, and an inherited two-letter-isotope alias whose trailing imaging suffix defeats the revised key check. Every refusal stage misses both. The exact M13 DARATUMUMAB reproduction is fixed.

## M14-B1 — a consumed one-letter-isotope alias bypasses the case-marked check (regression)

**Exact HTTP:** `POST /api/explore`, JSON `{"text":"3HVINBLASTINE"}`. HTTP 200 draws **VINBLASTINE / CHEMBL159**, matched alias **`[3h]-vinblastine`**, with **5 live trials**, and no refusal. `Which trials evaluate 3HVINBLASTINE?` and `Who sponsors trials of 3HVINBLASTINE?` each return **5 originator evidence rows**. `3HVinblastine`, `3Hvinblastine`, and `3hvinblastine` do the same. With `3Hvinblastine, osimertinib`, the wrong first centre is still VINBLASTINE. [Full stages and previous comparison](edge_results.json), [HTTP](edge_http.json).

**Control and identity:** `[3h]-vinblastine` and `[3H]vinblastine` are refused, with zero trial/sponsor evidence. Their canonical key is the same **`3hvinblastine`** as the accepted input, uniquely naming the stored tracer alias of VINBLASTINE. Bare `vinblastine` remains available. For the deliberately case-marked input **`3HVINBLASTINE`**, `_isotope_edge` returns **true**. Thus this finding does not depend on reading lower-case chemistry as an isotope. [Dictionary, helper result, key checks](dictionary_evidence.json).

The HEAD^ query module refuses all four glued spellings and selects the separate OSIMERTINIB in the comma control. This is a **current-patch regression**, established with the same current app, normalization/rules, and database and only `query.py` replaced in memory. It is not a reconstructed old deployment. [Version-labelled direct results](edge_results.json).

**Cause:** positive matching consumes the complete alias (`src/query.py:450-470`). The new helper is called only on **outside neighbouring words** (`src/query.py:317-320`), never on the consumed name's `own` words. The inside scan (`src/query.py:282-297,321-323`) recognizes whole isotope labels but cannot split `3HVINBLASTINE`. The revised key fallback excludes one-letter elements and starts its prefix-length loop at 3 (`src/query.py:327-337`), although `3H` has length 2. The previous key fallback refused this canonical alias. The comment saying that one-letter elements are left to the case-marked check is ineffective for a consumed alias.

**Required outcome:** preserve refusal for a known tracer alias when its isotope separator is removed, including the case-marked form the new helper already recognizes, without broadening lower-case dose/chemistry interpretation.

## M14-B2 — a two-letter-isotope alias with a trailing PET/CT marker still maps its originator (inherited)

**Exact HTTP:** `POST /api/explore`, JSON `{"text":"89Zrpanitumumab-PET-CT"}`. HTTP 200 draws **PANITUMUMAB / CHEMBL1201827**, matched alias **`89zr-panitumumab-pet/ct`**, with **8 live trials**. Trial and sponsor QA return **8 / 7 originator evidence rows**. There is no Refused entity or refusal notice. [HTTP](edge_http.json), [stages](edge_results.json).

**Minimal control:** **`89Zr-panitumumab-PET-CT`** refuses and yields zero QA evidence. Removing only the hyphen between the isotope and the drug causes the leak. Both strings have canonical key **`89zrpanitumumabpetct`**, uniquely pointing to the same stored AACT alias. `89Zr panitumumab PET CT` also refuses; bare `panitumumab` still works. Fully glued `89ZrpanitumumabPETCT`, lower-case `89zrpanitumumabpetct`, and `89Zrpanitumumab PET CT` leak too. Appending `, osimertinib` does not prevent the wrong PANITUMUMAB centre. [Dictionary evidence](dictionary_evidence.json), [compact matrix](edge_summary.json).

**Cause:** the isotope is fused inside a consumed alias, so it is neither a whole isotope word nor an outside neighbour (`src/query.py:282-323`). `_isotope_edge('89Zrpanitumumab')` is true, but this helper is never applied to that own word. The final fallback isolates `89zr` but requires the remaining key **to end with** a same-drug key of at least five characters (`src/query.py:329-334`). `panitumumabpetct` does not end in any such key: the stored imaging marker follows the drug name. Allowing arbitrary text only **between** the isotope and a terminal same-drug name does not protect this actual stored tracer alias. The HEAD^ query module has the same leak, so this is inherited, not a newly introduced regression.

**Required outcome:** normalization of a stored refused tracer alias must preserve its refused identity even when the alias includes a trailing imaging marker.

## Every stage for both blockers

| Stage | `3HVINBLASTINE` | `89Zrpanitumumab-PET-CT` |
|---|---|---|
| Raw intervention resolver | ALIAS / CHEMBL159 | ALIAS / CHEMBL1201827 |
| `_qualified` | false | false |
| Resolver veto | `{}` | `{}` |
| Item linker | Drug; no Refused | Drug; no Refused |
| Whole-name shortcut | `None` | `None` |
| Public linker | VINBLASTINE; no Refused | PANITUMUMAB; no Refused |
| Map centre / live trial count | CHEMBL159 / 5 | CHEMBL1201827 / 8 |
| Qualified trial / sponsor QA rows | 5 / 5 | 8 / 7 |

The raw tracer predicate expects a boundary after the element (`src/textrules.py:303-314`), so the normalized raw resolver also misses the guard (`src/normalize.py:738-746`). `Engine.explore` selects the surviving first positive hit (`src/app.py:88-95`). These are not cases where the map ignores an already-recorded refusal; **all refusal paths miss**. The relationships shown may be valid for the originator but are attached to a wrongly selected centre.

## Reused earlier attacks and controls

The m13 `focused.py`, `fresh.py`, `http_probe.py`, and `fresh_http.py` case lists were reused unchanged. Only round labels and owned HTTP ports were adapted. [Reuse manifest](reuse_manifest.json), [execution](execution.json).

| Earlier reproduction | Current disposition |
|---|---|
| M12-B1 `[89Z.r]-DFO-daratumumab` and punctuation variants | **FIXED**; refused, zero originator trial/sponsor rows. Separate OSIMERTINIB remains available. [Replayed stages](focused_results.json), [replayed HTTP](new_leaks_http.json). |
| M13-B1 `89ZrDFO-daratumumab`, `89zrdfodaratumumab`, `[89ZrDFO]-daratumumab`, `89Z.rDFO-daratumumab`, `89ZrDFO daratumumab`, `89-ZrDFO-daratumumab` | **FIXED for these reported main reproductions**; no DARATUMUMAB centre or qualified originator QA. Separate OSIMERTINIB survives. [Original M13 matrix replay](fresh_results.json), [HTTP](fresh_http.json). |
| M13 supplementary `A33124I` | **NOT FIXED**; still maps ADAKITUG / CHEMBL5314551 with no refusal, whereas `A33 124i` refuses. The alias key is identical. This is a residual recorded example, with zero QA rows, not a third new blocker. [Direct evidence](edge_results.json), [HTTP](edge_http.json), [dictionary](dictionary_evidence.json). |
| M12/M13 over-refusal `rad001c` | **FIXED**; EVEROLIMUS / CHEMBL1908360, 9 trial / 7 sponsor QA rows. [Current/previous stages](edge_results.json). |
| M11/M12/M13 descriptive isotope-distance and unusual punctuated lexical qualifiers | **NOT FIXED** where earlier recorded; bounded observations remain supplementary. Examples `trastuzumab labelled with [89Zr]`, `b.i.o.similar bevacizumab`, `lip.osomal doxorubicin` retain originator maps. [Unchanged historical case list](focused_results.json). |
| Dose/chemistry controls `13-cis retinoic acid`, `BKM-120NX`, `osimertinib 80 mg`, `paclitaxel 2 cycles`, `cisplatin 75 mg/m2 day 1` | Expected current drug selections remain available; no new over-refusal for these controls. [HTTP](edge_http.json), [stages](edge_results.json). |

**Additional casing observation, not a third blocker:** `89ZRDFO trastuzumab` and `89zrDFO trastuzumab` draw TRASTUZUMAB, while `89ZrDFO trastuzumab` refuses. `_isotope_edge` requires exact upper/lower element casing even for two-letter elements (`src/query.py:133-134`). This also passes the raw resolver veto and item predicate. It is retained as a supplementary boundary observation; the two stored-alias blockers above independently decide the approval bar. [Direct neighbouring-word probes](extra_neighbors.json).

## Execution and integrity

- Six scripts exit 0. The final direct matrices contain 41 reused M12 cases, 27 reused M13 cases, and 29 new/control cases, each with current and HEAD^ query-module stages.
- The final HTTP evidence contains **308 requests**: 76 reused M12, 108 reused M13, and 124 new/control requests. All return HTTP 200; refusal correctness is checked from response bodies.
- Owned ports **8950, 8951, 8952** are closed. All CLI servers ran unmodified `src/app.py`; served page bytes match `web/try.html`; the database SHA-256 was unchanged. [M12 lifecycle](new_leaks_lifecycle.json), [M13 lifecycle](fresh_lifecycle.json), [new lifecycle](edge_lifecycle.json).
- Comparison probes reopen SQLite with `mode=ro`. No mutation fixtures, application edits, or model calls were used. Bytecode is disabled; HTTP temporary directories and all new scripts/results remain inside m14/attacks.
- Timings overlap other review work and are not benchmarks. The parent review owns historical-name completeness, demo/UI/DB checks, cost testing, pytest, and whole-worktree integrity.

Reproduce from repository root: `python -B audit_evidence_claims/m14/attacks/run.py`. Servers check their own ports and terminate only the processes they start.

**Spec assessment: CHANGES REQUIRED.** Two directly reproduced refused-tracer identity failures violate the originator approval bar. M14-B1 is also a regression from HEAD^.
