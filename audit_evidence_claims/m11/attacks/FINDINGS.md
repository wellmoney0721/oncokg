# Round 11 independent refusal attacks

HEAD `2b9fc923f7b6f388f5babd2f998ed4c6e16d3439`. Two inherited blocker families remain. Both share a mismatch between the letters-and-digits lookup key and the words examined by refusal guards. No application file was edited.

## M11-B1: punctuation inside the element symbol evades isotope checks

Exact inputs: `[89Z.r] trastuzumab`, `89Z.r trastuzumab`, `89Z_r trastuzumab`, `trastuzumab [89Z.r]`. Each draws **TRASTUZUMAB / CHEMBL1201585 / 13 live trials**. `Which trials evaluate [89Z.r] trastuzumab?` and `Which companies sponsor [89Z.r] trastuzumab?` each return **12 originator evidence rows**. The same is true for the other three forms. No refusal occurs in resolver veto, item linker or public linker; the whole-name shortcut is None. [All stage outputs, map and QA](key_equivalence_results.json).

The prefix form has the same dictionary key as the stored tracer synonym `89zr-trastuzumab`: `89zrtrastuzumab`. `canonical_key` removes all non-ASCII letters/digits (`src/textrules.py:339-346`), so this spelling is accepted as that very synonym. The raw resolver reports ALIAS for `89Z.r trastuzumab`; the bracketed form strips the label and accepts bare TRASTUZUMAB. Yet `_alnum_words` splits the same label into `89Z` and `r` (`src/query.py:111-113`). `_marked` joins candidate runs with a space (`src/query.py:250-265`), and `is_isotope_label('89Z r')` is false because the regex allows a separator between mass and element, not within the element (`src/textrules.py:289-298`). Neither `89Z` nor `r` is a valid isotope. The new inside-name check therefore still accepts a normalized stored tracer alias as the originator.

Controls `[89Zr] trastuzumab`, `[89.Zr] trastuzumab`, and `89zr-trastuzumab` refuse with zero QA rows. `[8.9Zr] trastuzumab` and `[8.9.Zr] trastuzumab` also now refuse. This is not a list-boundary argument or a known over-refusal. The input and accepted tracer synonym differ only in punctuation already ignored by the positive lookup key. The reverse `trastuzumab [89Z.r]` also shows that inspecting only matched aliases would leave adjacent labels vulnerable.

## M11-B2: one punctuation token reopens a split known FDA suffix

Exact minimal contrast: `bevacizumab a w w b` **refuses**, while `bevacizumab a - w w b` draws **BEVACIZUMAB / CHEMBL1201583 / 122 live trials**, without any Refused entity. Additional reproduced forms are `bevacizumab - a - w - w - b`, `bevacizumab a - w - w - b`, and `bevacizumab a _ w _ w _ b`. Trial and sponsor questions about each leaked form return **12/12 originator rows**. [Stages and exact counterfactuals](key_equivalence_results.json).

Both sides of the minimal contrast have key `bevacizumabawwb`, matching the stored `Bevacizumab awwb` synonym. The resolver accepts ALIAS and emits no veto. The unpunctuated five-token form fits the positive match window; `_marked` then detects its key ending in `awwb`. With the single dash the form has six raw tokens, exceeding the five-token cap at `src/query.py:378-395`. The matcher falls back to bare bevacizumab. Its normalized following words are `a`, `w`; `_marked` tests only the next single word for membership in the FDA suffix set (`src/query.py:251,262-263`). `_qualified` sees `bevacizumab a w w b` but never joins the suffix's letters, so the item is not refused (`src/query.py:125-145`). No stage revisits the accepted parent with the complete known suffix. The whole-name shortcut remains None.

The same 6-token form ending in a known suffix was already accepted by HEAD^, so this is an inherited hole, not a newly introduced query regression. Merely raising a raw-token window would move this failure threshold; refusal needs to stay aligned with the accepted name/suffix normalization.

## Scope and comparison evidence

`key_equivalence.py` runs **26 inputs** against current Engine and an exact HEAD^ query module. Both M11 families leak on HEAD^. Other application modules, rules, normalization and DB remain current: this is a query-module counterfactual, not a historical deployment. The standalone qualified diagnostic is current-only; previous item_linker executes the old module's actual guards.

The reused [M10 broad probe](../names/m10_attacks/probe_results.json) covers 1,224 prior inputs. Its 202 Drug maps include controls and accepted list-policy boundaries, and are not a defect count. The [35-case focused replay](../names/m10_attacks/focus_results.json) confirms M10-B1/B2/B3/B4 are FIXED for all exact reported inputs. Parent/root independently confirms the new families through the original CLI HTTP server; this worker's stage evidence is direct Engine execution.

Other lexical observations such as `biosimilars of bevacizumab`, `doxorubicin liposome`, element-first isotope notation and a label separated from the drug by the word `labelled` are retained in raw outputs, but are not additional blocker claims here. True isotope-bearing stored nodes and deliberately adopted list boundaries require distinct semantic adjudication. The user-supplied accepted over-refusals are not used for this verdict.

## Spec axis

The requested guards fix the prior reproductions, but the map can still draw an originator for a normalized spelling of its known tracer or FDA-suffixed product. In M11-B1 the positive key merges an element symbol which the refusal path splits. In M11-B2 a punctuation token prevents the complete known suffix from reaching the guard while the bare-parent match survives. The map's normal live edges and stored counts then describe the wrongly selected molecule. All three refusal stages miss both demonstrated inputs; neither is a stale edge, rendering issue or over-refusal. These two findings fail the original approval bar. No unrelated feature change or broader medical claim is needed to reproduce them.

## Reproduction

```text
python -B audit_evidence_claims/m11/attacks/key_equivalence.py
```

Run from repository root with PYTHONDONTWRITEBYTECODE=1 and PYTHONUTF8=1. All outputs are beside the script, and the DB is reopened read-only before stage probes.
