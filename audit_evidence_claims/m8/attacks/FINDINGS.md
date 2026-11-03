# R8 independent name attacks

HEAD: `ec4eede`. Reproduction: `python -B audit_evidence_claims/m8/attacks/probe.py`.
The script tests 174 distinct map inputs and eight QA inputs, reopens both graph connections with `mode=ro`, and writes only beside itself. It loads the exact `9bd7cb4:src/query.py` into a separate in-memory module for predecessor comparisons, retaining current shared data/rules. No HTTP result is claimed here; the root reviewer owns independent HTTP confirmation.

Evidence: [full stage results and predecessor comparisons](probe_results.json), [compact results](probe_summary.json), [dictionary entries](dictionary_evidence.json), [Unicode dash inventory](unicode_dashes.json). Full stage results include normalized input, resolver components, `_resolver_blocked`, `_link`, `_whole_name`, final linked entities and map response.

## M8-B1 — P1, new regression: stripping isotope brackets loses a refusal already returned by the resolver

Exact input: **`[89 Zr] trastuzumab`**.

- Current `Engine.resolve`: `BLOCKED_CLASS_TERM`, `rules=[extract_parenthetical, radiotracer_guard]`, `drug_id=null`, cleaned `component="trastuzumab"`.
- Current map: **TRASTUZUMAB / CHEMBL1201585**, stored trial count **13**, `matched_text="89zr-trastuzumab"`, no refusal in `also`.
- Exact predecessor: refused `[89 Zr] trastuzumab`, no centre.
- `Which trials evaluate [89 Zr] trastuzumab?` and `Which companies sponsor [89 Zr] trastuzumab?`: current QA returns **12 originator evidence rows each**. The earlier query implementation refuses both.

The stage-one adapter only recognizes a blocked tracer if `T.is_radiotracer(c['component'])` is still true (`src/query.py:187-190`). But resolver cleaning removes the bracketed isotope before returning the component (`src/normalize.py:642-644,697-700`), while its raw-part guard correctly records `radiotracer_guard` (`738-746`). The adapter discards that explicit reason and returns `{}`.

Stage two strips the `[` from `[89` and `]` from `Zr]` (`src/query.py:230-242`), giving `89 Zr trastuzumab`. `_qualified` applies `is_isotope_label` only to individual words (`112`) rather than the two-word label `89 Zr`; the wider runs only test `is_distinct_product` / `is_radiotracer` (`114-116`). The pre-existing isotope pattern explicitly supports a whitespace separator (`src/textrules.py:289`); it simply is not called on that run. The aggressive alias key subsequently maps all three words to the stored `89zr-trastuzumab` alias (`src/query.py:317-322`; `src/textrules.py:339-346`). Stage three recognizes the original tracer via `T.is_radiotracer(name)` and returns `None` at `src/query.py:211-212`, before exact-name comparison. It emits no refusal or veto, so `link_entities` returns the leaked stage-two Drug (`149-153`).

Tab, newline and NBSP isotope separators produce the same new regression: `[89\tZr] trastuzumab`, `[89\nZr] trastuzumab`, `[89\u00a0Zr] trastuzumab`. `[64 Cu] trastuzumab` and `[177 Lu] trastuzumab` also leak after returning a blocked resolver tier. All are recorded, rather than inferred from the one example.

Successful controls: `[89Zr] trastuzumab`, `[89-Zr] trastuzumab`, `89Zr trastuzumab`, and `[89 Zr]-trastuzumab` refuse. Bare `trastuzumab` still selects the originator. This is a concrete refusal regression, not a request to disallow a valid separately listed drug.

## M8-B2 — P1, inherited shared miss: internal suffix wrappers survive guard normalization but disappear in the lookup key

Exact input: **`bevacizumab-(awwb)`**; equivalent decisive input **`bevacizumab-[awwb]`**.

Both draw **BEVACIZUMAB / CHEMBL1201583**, **122** stored trials, `matched_text="Bevacizumab awwb"`, no refusal. The exact predecessor does the same. The standalone standard spelling `bevacizumab-awwb` is correctly refused. `awwb` is explicitly listed in `BIOSIMILAR_FDA_SUFFIXES` (`src/textrules.py:169-171`), so this classification uses the project's own product rule, not an external pharmacological assertion.

The resolver extracts the parenthetical suffix and returns the plain molecule as EXACT. `_resolver_blocked` has nothing to enforce. `_link` strips only edge punctuation, leaving the interior `(` / `[` before `awwb`; its anchored suffix predicate misses. `canonical_key` then erases that punctuation, matching the stored originator alias. `_whole_name` returns `None`; it does not correct the earlier positive match. Relevant sites: `src/query.py:171-177,187-190,239-242,320-322`; `src/textrules.py:156-157,339-346,358-363`.

The same result is measured for quote/brace wrappers and `trastuzumab-(dkst)` / `trastuzumab-[dkst]` (CHEMBL1201585, 13 trials). Both trial and sponsor QA for `bevacizumab-(awwb)` return 12 rows. Spaced `bevacizumab - (awwb)` is correctly refused. The defect is the internal wrapper surviving one representation and disappearing in another.

## M8-B3 — P1, inherited shared miss: the claimed universal dash fold covers only part of Unicode dash punctuation

Exact input: **`bevacizumab⸺awwb`**, where the separator is **U+2E3A TWO-EM DASH**, category **Pd**.

Current and previous maps draw **BEVACIZUMAB / CHEMBL1201583**, 122 trials. Current trial and sponsor QA each return 12 originator rows. Stage one returns `{}`, stage two returns the Drug, stage three returns `None`. NFKC preserves this dash. The explicit `_DASHES` range at `src/query.py:100-101` does not fold it; the positive alias key erases it at `src/textrules.py:345`. ASCII `-` and U+2011 controls refuse correctly.

An exhaustive scan of the current Python Unicode database's **26 Pd code points** produced **14 leaked originator maps**. This inventory is bounded and reproducible; no claim is made that every dash-like Unicode symbol is in Pd. The complete code/name/normalized spelling/result table is in `unicode_dashes.json`. U+2E3B THREE-EM DASH, U+2E40 DOUBLE HYPHEN and U+301C WAVE DASH are additional measured misses. Because the user and source comment claim all dashes are folded, U+2E3A is a direct contradiction; the blocker does not rely on invisible format characters or misspelled qualifiers.

## M8-S1 — P2, inherited valid-item loss: qualifier carry ignores explicit punctuation boundaries

`biosimilar, and osimertinib` and `biosimilar and, osimertinib` both return only Refused `biosimilar ... osimertinib`, losing a valid drug alone in its explicit comma item. `biosimilar; and osimertinib`, slash/pipe equivalents and fullwidth punctuation reproduce it. Current and predecessor agree. These inputs were present in the m7 supplemental attack script; this is **NOT FIXED**, not a new regression.

`biosimilar, osimertinib`, `biosimilar; osimertinib`, `biosimilar / osimertinib` and `biosimilar | osimertinib` retain **OSIMERTINIB / CHEMBL3353410**, 79 trials. `_resolver_blocked` is `{}` in all these map cases, so the loss is confined to `_link`: `joined` checks that intervening `seg` entries are joiners but never checks `clause` equality (`src/query.py:282-283`), then carries the qualifier at `298-304`. The lost valid item falls within the user's stated exception to intended over-refusal. It is separate from the decisive originator blockers.

## Other controls and limits

The scan verifies current successful handling of the earlier canonical-key false positives (`is a`, `Erlotinib, hydrochloride`, `osimertinib,mesylate`), whole stored names (`CP-358,774`, `(E/Z)-AFATINIB`, `RO 09-1978/000`), legitimate originator suffixes and separately accepted aliases. `Pegylated interferon alfa-2a` remains refused as the explicitly accepted M5-S2 limitation. Root/sibling workers own exhaustive historical replay, demos, DB/UI, HTTP and cost validation.

Inspection additionally identified a potential resolver-cache rollover exception at `src/query.py:180-182` and sent it to the root/cost reviewer for an independent natural reproduction. It is not counted here without that worker's executable evidence.

The observed originator leaks fail the approval bar even if all ordinary demos pass. No tracked code was changed.

## Focused follow-up — valid lone stored aliases lost in this commit

The historical sweep worker identified four additional lost aliases. They were independently reproduced with `python -B audit_evidence_claims/m8/attacks/lone_alias_probe.py`, with full exact dictionary rows and the previous implementation's responses saved in [lone_alias_results.json](lone_alias_results.json).

### M8-S2 — P2: isotope-shaped development names become refused

| Exact input | Unique exact stored alias target | Previous map | Current map |
|---|---|---|---|
| `566C` | ATOVAQUONE / CHEMBL1450; ChEMBL synonym | 2 trials | Refused |
| `9-ac` | 9-AMINOCAMPTOTHECIN / CHEMBL274070; AACT synonym | 1 trial | Refused |
| `5ac` | AZACITIDINE / CHEMBL1489; AACT synonym | 6 trials | Refused |

The new single-word `is_isotope_label` branch at `src/query.py:112` treats these stored development names as isotope labels because the syntactic pattern accepts one to three digits followed by an element-like string (`src/textrules.py:289-300`). The intervention resolver also refuses them as `radiotracer_guard`; this is a shared false positive, **not** a resolver/linker inconsistency. The report does not assert new chemistry from the regex: the evidence is each exact unique stored synonym, its existing live Drug record, the immediately preceding map behavior, and the absence of any separate product qualifier. Preferred-name controls still draw the same IDs. These are new valid-lone-name losses outside the specifically accepted M5-S2 example; report as should-fix, separate from originator blockers.

### M8-S3 — P2: punctuation stripping defeats a letter-for-letter stored name

Exact input: **`5.BETA.,20-EPOXY-1,2.ALPHA.,4,7.BETA.`**. It is a unique literal ChEMBL synonym of **PACLITAXEL / CHEMBL428647**. The previous map draws that drug with **234** trials; current map says **not_found**. Neither current refusal stage reports a refusal, and the resolver returns only UNRESOLVED components.

`_whole_name` strips the final literal period before exact alias comparison (`src/query.py:210,214-216`), so the input that really is letter-for-letter one stored name stops matching. This is distinct from M7-S1's repair of arbitrary canonical-key equality: no invented punctuation or newly composed alias is used here. The source data and prior result establish the valid-single-name regression, without proposing a broad canonical-key fallback.
