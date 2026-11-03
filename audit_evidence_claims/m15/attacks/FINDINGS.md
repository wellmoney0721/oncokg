# Round 15 independent refusal attack assessment

Current HEAD: `1b3896669387cbc142c12b726909231cca8658db`. One new P1 refusal bypass is reproduced. The lower-case member of M14-B1 also remains unresolved; it is an already reported originator leak, not a known accepted over-refusal. No application code was changed. The repaired upper-case cases work, and no new current-patch regression was demonstrated.

## M15-B1 — splitting an isotope in a neighbouring chelator token defeats the check that recognizes its raw form

**Exact request:** `POST /api/explore`, JSON `{"text":"89-ZrDFO trastuzumab"}`.

**Observed:** HTTP 200, **TRASTUZUMAB / CHEMBL1201585**, **13 live trials**, no refusal. `Which trials evaluate 89-ZrDFO trastuzumab?` and `Who sponsors trials of 89-ZrDFO trastuzumab?` each return **12 originator evidence rows** (the QA result cap). The reverse **`trastuzumab DFO89-Zr`** does the same. The split-symbol alternatives **`89Z.rDFO trastuzumab`** and **`trastuzumab DFO89Z.r`** also leak. Adding `, osimertinib` still selects TRASTUZUMAB for the split-symbol input. [Full stages](targeted_results.json), [HTTP](targeted_http.json), [compact matrix](targeted_summary.json).

**Controls:** `89ZrDFO trastuzumab` and `trastuzumab DFO89Zr` refuse and have zero qualified trial/sponsor evidence. Each failing/control pair has the same canonical key; adding a hyphen inside `89Zr` is sufficient to change refusal into originator selection. No full DFO/trastuzumab key is present in the dictionary, so this is a neighbour-check failure rather than a consumed-whole-alias failure. Bare `trastuzumab` remains available. [Dictionary and helper evidence](dictionary_helper_evidence.json).

**Precise cause:** `_isotope_edge('89-ZrDFO')` and `_isotope_edge('DFO89-Zr')` both return **True** (`src/query.py:138-147`). However, `_marked` first uses `_alnum_words` to turn the preceding/following token into `['89', 'ZrDFO']` or `['DFO89', 'Zr']` (`src/query.py:293-294,316-317`). Its fused-label helper is then called on each fragment, which is false for all of them (`src/query.py:330-333`). Its separate gluing loops check only *whole* isotope labels, so `89zrDFO`/`DFO89zr` is not accepted by those checks (`src/query.py:318-329`). The later name-key fallback sees only `trastuzumab`, not the adjacent marker (`src/query.py:345-363`). `_marked` returns `None` in the captured actual `_link` call. This is a precise normalization inconsistency: the raw token is already recognizable by the existing helper, but that recognizable form is discarded before it is used.

Neither the raw resolver's guard (`src/normalize.py:738-746`; `src/textrules.py:303-314`) nor `_qualified` recognizes these forms. `Engine.explore` then draws the surviving first positive hit (`src/app.py:88-95`). Both current and HEAD^ query modules leak against the same current app/data: **inherited**, not introduced by the latest patch. This comparison changes only the query module in memory, not an entire historical deployment.

**Required outcome:** preserve the refusal of a case-marked isotope fused to a neighbouring chelator when punctuation is inserted inside its label, before or after the named drug. Validate actual linker/map/QA paths in addition to the standalone helper. No repair was implemented.

## Residual M14-B1 — lower-case stored tracer alias still maps VINBLASTINE

**Exact request:** `POST /api/explore`, JSON `{"text":"3hvinblastine"}`. HTTP 200 draws **VINBLASTINE / CHEMBL159**, with **5 live trials** and **5/5 qualified trial/sponsor evidence rows**. No stage records a refusal. `3hvinblastine, osimertinib` still draws VINBLASTINE first. This exact lower-case spelling was explicitly in the M14 report and attack matrix. [Original matrix rerun](edge_results.json), [new targeted HTTP](targeted_http.json).

The dictionary has one hit for key `3hvinblastine`: stored ChEMBL synonym **`[3h]-vinblastine`**. That original synonym and the separated `3h vinblastine` refuse. Thus the remaining failure is demonstrated by the known stored tracer identity and its refusing control, without assuming that every lower-case chemical expression is an isotope. Removing only brackets and a hyphen from a refused stored tracer draws its originator. [Identity evidence](dictionary_helper_evidence.json).

The latest patch fixes `3HVINBLASTINE`, `3HVinblastine`, and `3Hvinblastine`, but `_marked` explicitly skips a one-letter isotope when the corresponding input letter is lower-case (`src/query.py:353-355`). No earlier stage or later fallback recovers the stored alias's refusal. The user describes an upper-case repair but retains the original approval bar and does not list this originator leak among the accepted exceptions. Therefore **M14-B1 is FIXED for its three upper-case spellings, NOT FIXED as an entire reported finding family**. This should not be conflated with the accepted over-refusals or development-code dictionary limitation.

**Same-mechanism corroboration:** **`A33124i`** and **`a33124i`** still draw ADAKITUG / CHEMBL5314551 (zero trials), while **`A33 124i`** refuses and repaired **`A33124I`** now refuses. Both share the stored key `a33124i`. `_medical_isotope('124i')` is true, but the lower-case check skips the iteration before the medical-mass closing-label branch (`src/query.py:354-362`). The original upper-case M13/M14 reproduction is **FIXED**; the lower-case equivalent remains an originator leak. This is corroboration of the remaining case-sensitive stored-alias gap, not a separately inflated new finding.

## Every stage for representative failures

| Stage | `89-ZrDFO trastuzumab` | `3hvinblastine` | `A33124i` |
|---|---|---|---|
| Raw intervention resolver | CONTAINED_ALIAS + UNRESOLVED; no BLOCKED component | ALIAS / CHEMBL159 | ALIAS / CHEMBL5314551 |
| `_qualified` on the single item | false | false | false |
| Resolver veto | `{}` | `{}` | `{}` |
| `_marked` during actual `_link` | `None` | `None` | `None` |
| Item linker | Drug, no Refused | Drug, no Refused | Drug, no Refused |
| Whole-name shortcut | `None` | `None` | `None` |
| Public linker | TRASTUZUMAB, no Refused | VINBLASTINE, no Refused | ADAKITUG, no Refused |
| Map / live trial count | CHEMBL1201585 / 13 | CHEMBL159 / 5 | CHEMBL5314551 / 0 |
| Qualified trial / sponsor QA rows | 12 / 12 | 5 / 5 | 0 / 0 |

All entries come from [captured current and HEAD^ stages](targeted_results.json), not inference from the map alone. The ordinary relationships may be correct for the originator, but the wrong selected centre fails the approval bar.

## Replays, controls and exploratory limits

- **97 original direct attack cases rerun**: 29 in [edge](edge_results.json), 27 in [fresh](fresh_results.json), 41 in [focused](focused_results.json). Case lists are unchanged from m14; scripts are copied under m15, with provenance in [reuse manifest](reuse_manifest.json). The naming worker separately covers m14 extra-neighbour and broader historical name reproductions.
- **29 additional targeted direct cases**, compared current/HEAD^, and **116 unmodified CLI HTTP requests**, all 200. The owned port **8945** is closed; database SHA-256 is unchanged; the served page equals the worktree page. [Lifecycle](targeted_lifecycle.json). The root independently repeated the new split-neighbour failures and controls.
- **M14-B2 FIXED for originator leakage**: `89Zrpanitumumab-PET-CT`, `89ZrpanitumumabPETCT`, `89zrpanitumumabpetct`, and `89Zrpanitumumab PET CT` explicitly refuse, with zero qualified originator QA. The slash-bearing forms `89zr-panitumumab-pet/ct` and `89Zrpanitumumabpet/ct` return `not_found`, rather than an explicit refusal; neither draws PANITUMUMAB. The comma-separated `89ZrpanitumumabPETCT, osimertinib` selects the valid OSIMERTINIB. These response states are distinct. **M13/M14 `A33124I` FIXED**. Main M13 joined-chelator reproductions remain fixed.
- `13-cis retinoic acid`, `BKM-120NX`, `NSC-118218H`, `DX-8951F`, `GW572016F`, bare VINBLASTINE, ADAKITUG and TRASTUZUMAB preserve their expected current identities. [Targeted results](targeted_results.json).
- An exploratory **428-variant / 104-key** scan transforms isotope-shaped stored aliases by removing separators and changing case. **178 variants** draw a centre where the source spelling refuses. This count is **not 178 defects**: it includes already isotope-labelled molecules, chemical locants and known over-refusals. The clear unlabelled-tracer cases are the residual VINBLASTINE and A33 cases above. [Full scan](alias_variants.json), [script](alias_variants.py).
- `89Zr DFO trastuzumab`, `89 Z r DFO trastuzumab`, and `89Zr D-F-O trastuzumab` also draw TRASTUZUMAB. They are retained as corroborating spacing boundaries; the promoted new finding uses the stronger punctuation-only change for which the existing raw helper already returns true.
- Previously recorded distant isotope / split lexical qualifier gaps are retained in the original focused replay, not re-labelled as newly discovered findings. Native radiolabelled drug entries and accepted over-refusals are not used to inflate blocker counts. No external medical claim is required by these findings.

## Specification-axis summary

The changed upper-case, trailing-marker and upper-case medical-mass reproductions work. The original no-originator-leak guarantee still fails in two ways: a new reproduced punctuation boundary in the neighbouring chelator check, and the explicitly recorded lower-case member of M14-B1. For `89-ZrDFO trastuzumab`, the existing helper recognizes the raw isotope-bearing word, but normalization splits it before the helper is called; all stages then accept the originator. For `3hvinblastine`, the dictionary already identifies the consumed alias as the same stored tracer that the control refuses, but the new case rule skips it. Both yield ordinary originator evidence through HTTP. No source repair was made.
