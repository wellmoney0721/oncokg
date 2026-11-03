# Independent adjudication of round-12 tracer candidates

**`[89Z.r]-DFO-daratumumab` is an approval blocker.** Independent current-HEAD execution returns DARATUMUMAB / CHEMBL1743007, two graph trials, and two originator evidence rows for each trial/sponsor question. The raw resolver, resolver veto, item linker and public linker make no refusal; the whole-name shortcut is `None`. [Independent stages and controls](adjudication_tracer.json), [reproducer](adjudicate_tracer.py).

This conclusion needs no external pharmacological assumption:

- The stored synonym is exactly `89zr-dfo-daratumumab`, mapped to CHEMBL1743007.
- The attack and clean `[89Zr]-DFO-daratumumab` have the identical lookup key `89zrdfodaratumumab`.
- Both the clean form and stored synonym refuse, with zero trial/sponsor QA evidence. The repository itself identifies them as tracer forms.
- The attacked map explicitly reports the matched synonym `89zr-dfo-daratumumab` while drawing the parent DARATUMUMAB node. This is not an already isotope-labelled centre such as a lutetium product, an unrelated unknown name, or a separate-item boundary.

The same attack also leaks using the exact HEAD^ query module against current app/rules/data. It is an inherited remaining hole, not a new regression caused by d9260a1. The comparison is a query-module counterfactual, not a reconstructed previous deployment.

The mechanism is directly supported by current source and the dictionary:

1. `_alnum_words` splits the consumed alias into `89Z`, `r`, `DFO`, `daratumumab` (`src/query.py:111-113`). The internal-label test considers runs of one or two words joined with a space (`src/query.py:252-260,278-280`). `89Z r` fails the isotope parser, which permits a separator between mass and element but not inside the element symbol (`src/textrules.py:289-298`).
2. The latest glued-neighbour scan (`src/query.py:264-277`) sees no neighbours because the entire tracer alias is consumed as one name.
3. The new key-splitting guard (`src/query.py:281-286`) recognizes `89zr` but requires the remainder `dfodaratumumab` to be another dictionary key for the same drug. That key is absent. The accepted full tracer alias therefore escapes this final guard.
4. Positive matching keeps the stored synonym (`src/query.py:409-432`), and `Engine.explore` selects the surviving first Drug (`src/app.py:87-95`). All resulting edges can be live and correctly stored while the selected centre is wrong for the input.

**Required behavioral outcome:** retain the tracer refusal for this accepted stored synonym and the punctuated spellings already treated as the same positive key. Merely requiring the isotope-stripped remainder to be a second dictionary key does not cover intervening text such as `DFO` in the accepted stored synonym.

## Labelled-distance supplement

`trastuzumab labelled with [89Zr]` and `[89Z.r]-labelled trastuzumab` also independently draw TRASTUZUMAB / CHEMBL1201585, with no public-linker refusal and 12/12 originator QA rows. Clean `[89Zr]-labelled trastuzumab`, `[89Zr] trastuzumab` and `trastuzumab [89Zr]` refuse as maps. Both leaked descriptions also leak with HEAD^ query code. [Results](adjudication_tracer.json).

These are explicit descriptions of the named drug being labelled with the repository-recognized isotope, not a deliberate comma/semicolon/list-item split. The code explicitly leaves `with` inside product descriptions (`src/query.py:92-95`) and documents item-level refusal of tracer descriptions (`src/query.py:339-346`). They therefore support a genuine remaining refusal gap. The new neighbour gluing stops at a word such as `labelled` once its concatenated length exceeds six, rather than reaching the isotope (`src/query.py:266-280`).

However, m11 already recorded label-separated lexical observations without promoting them as blockers ([m11 observation](../../m11/attacks/FINDINGS.md), line 27). They must be described as previously observed and newly adjudicated, not newly introduced. The stored-synonym daratumumab contrast above independently determines the approval result and is the cleaner primary finding.

The `[89Zr] labelled trastuzumab` standalone map refuses but its prefixed QA variants can still yield originator evidence; this is retained in the raw independent evidence and is not needed to establish the primary map blocker. No inference is made that every isotope-bearing stored node should be refused.
