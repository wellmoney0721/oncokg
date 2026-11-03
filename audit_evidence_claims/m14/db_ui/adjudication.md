# Independent isotope-boundary adjudication, round 14

Two originator leaks are independently reproduced against HEAD `73ee310d970c8c3b4886bbbdfd6d88026d403c28`. The first is a regression from the exact HEAD^ query module. The second is inherited. Both are blockers under guarantee 3; the explicitly accepted over-refusals do not apply.

The reused [adjudicator](adjudicate_tracer.py) loads HEAD^ `src/query.py` into a separate module and runs both engines against the same read-only database, current app and text rules. It records raw resolver, resolver block map, item qualifier, `_marked` calls/returns, item linker, whole-name fallback, public linker, map and trial/sponsor QA. No live data is mutated. [Full staged evidence](adjudication_tracer.json).

| Exact input | Current map / QA trial,sponsor rows | HEAD^ query | Refusal control |
|---|---|---|---|
| `3Hvinblastine` | VINBLASTINE / **CHEMBL159**, **5,5** | Refused, **0,0** | `[3h]-vinblastine` and `3H-vinblastine`: refused, **0,0** |
| `3hvinblastine` | VINBLASTINE / CHEMBL159, **5,5** | Refused, **0,0** | Same stored-alias control |
| `89Zrpanitumumab-PET-CT` | PANITUMUMAB / **CHEMBL1201827**, **8,7** | Same leak, **8,7** | `89Zr-panitumumab-PET-CT`: refused, **0,0** |

Both bare originator names retain their expected IDs and evidence. `3Hvinblastine, osimertinib` regresses from selecting OSIMERTINIB under HEAD^ to selecting VINBLASTINE now. The panitumumab mixed input also wrongly selects PANITUMUMAB.

## One-letter prefix regression

Evidence chain: `3Hvinblastine` and stored ChEMBL synonym `[3h]-vinblastine` share canonical key `3hvinblastine`; the resolver accepts the input as ALIAS to CHEMBL159 without a refusal rule. `_resolver_blocked` is `{}`, `_qualified` is false and `_marked` returns null. Item/public linker emits Drug; whole-name shortcut returns null, so this is an ordinary linker leak rather than an exact-name fallback. The separated stored alias receives `radiotracer_guard` and is refused.

`src/query.py:329-337` replaced the prior one-or-two-letter key-edge guard with a two-letter-only condition and starts at length three. `3h` therefore cannot match. The replacement case-marked helper is applied only to neighboring words (`src/query.py:317-320`), not the consumed name's own fused word. Whole-word inside checks at `src/query.py:282-297,321-323` cannot isolate `3H` from `3Hvinblastine`. The HEAD^ `_marked` instead returns the refusal label for exactly the same canonical dictionary entry. The original guard and replacement are preserved in [latest diff](review_diff_latest.txt).

## Two-letter isotope with trailing modality

Evidence chain: the AACT synonym `89zr-panitumumab-pet/ct` and attacked spelling share `89zrpanitumumabpetct`. The input is accepted as ALIAS; `_resolver_blocked` is `{}`, `_qualified` false, `_marked` null, item/public linker Drug and whole-name shortcut null. Canonical synonym with slash is safely not_found in the map because list splitting prevents a hit, while its raw resolver explicitly records `radiotracer_guard`; the equivalent fully hyphenated control is explicitly refused by map and QA.

The consumed name's alphanumeric words are `89Zrpanitumumab`, `PET`, `CT`. No inside word run equals an isotope label, and the fused-prefix helper never examines own words. The new canonical-key guard recognizes `89zr` but the remaining `panitumumabpetct` does not end in any same-drug key of length at least five (`src/query.py:329-334`). Saved diagnostics enumerate all eleven PANITUMUMAB keys and establish zero matching suffix keys. Thus the new boundary rule closes the chelator-prefix case only when the drug key is at the remainder's end. The original HEAD^ code also leaks this input; this is not labeled a newly introduced regression.

No external chemical inference is needed for either finding: the repository's own stored synonym, canonical-key equality and radiotracer refusal controls establish the intended product distinction. [Primary reviewer's real HTTP confirmation](../root_checks/independent_m14_http.json) exercises the same application routes independently.
