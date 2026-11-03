# Round 6 independent boundary attack

Current HEAD: `b7a00f9`. Reproducer: `python -B audit_evidence_claims/m6/attacks/fresh_probe.py`.
Evidence: [106 exact inputs, full linker/resolver/map metadata and eight QA responses](fresh_results.json),
[compact per-input comparison](fresh_summary.json). The predecessor column transplants the exact
`link_entities` and `_drug_spans` methods from `514929c` into a separate Engine, with unchanged current
dictionary and helper functions. Both database connections are replaced with SQLite `mode=ro` connections.

## M6-B1: interior glued separator hides the refused suffix (blocker)

Exact input: `bevacizumab - awwb/osimertinib`.

* Current map: `BEVACIZUMAB`, `CHEMBL1201583`, **122 trials**, no refusal.
* Current full resolver: `bevacizumab - awwb` is `BLOCKED_DISTINCT_PRODUCT`, while `osimertinib` is
  `EXACT / CHEMBL3353410`.
* Exact QA `Which trials evaluate bevacizumab - awwb/osimertinib?` returns **12** originator rows;
  first edge `NCT00955305|EVALUATES|CHEMBL1201583|NCT00955305`.
* Exact QA `Which companies sponsor bevacizumab - awwb/osimertinib?` returns **12** originator rows;
  first edge `ORG:roche|SPONSORS_TRIAL_OF|CHEMBL1201583|`.
* `bevacizumab - awwb|osimertinib` also draws BEVACIZUMAB. The pipe resolver does not split that form,
  so the slash form is the strongest exact resolver-versus-linker reproduction.
* Free separator control `bevacizumab - awwb / osimertinib` correctly retains only OSIMERTINIB and
  discloses refusal. The bare suffix is also refused.

**Cause:** `src/query.py:143-154` splits commas, semicolons and whitespace, strips slash/pipe only from
token edges, and tests only `startswith`/`endswith`. A slash inside `awwb/osimertinib` is left inside
one token. The anchored suffix check at `src/textrules.py:156-157,213` therefore misses the product;
the standalone `bevacizumab` token then links at `src/query.py:221-236`. No whole-item guard can
refuse a suffix that it never recognizes. `Engine.explore` selects that positive hit at `src/app.py:88-95`.

This contradicts the explicit glued-separator design and the refusal approval bar. **Inherited:** the
same exact input also maps to CHEMBL1201583 with the `514929c` predecessor; the latest repair did not
cover a separator glued on both sides.

Related consequences of the same splitting gap:

| Exact input | Current result | Boundary contract consequence |
|---|---|---|
| `osimertinib/EGFR` | `not_found` | Neither separate named entity is found. |
| `biosimilar anastrozole/Arimidex` | Entire string refused, no centre | Valid Arimidex alone after the declared separator is lost; full resolver accepts Arimidex. |
| `Erlotinib/hydrochloride` | `CHEMBL1079742`, **31 trials** | A salt is assembled across the declared separator; full resolver keeps first-item parent `CHEMBL553`. |
| `Erlotinib|hydrochloride` | `CHEMBL1079742`, **31 trials** | Same identity construction across pipe. |

These related observations are not separate blockers and do not allege that any listed stored trial count
is itself wrong. The wrong identity is selected. All are inherited in the exact predecessor comparison.

## M6-B2: punctuation normalization defeats the anchored guard (blocker)

Exact input: `bevacizumab-awwb。` (final character U+3002 IDEOGRAPHIC FULL STOP).

* Full resolver: component `bevacizumab-awwb`, `BLOCKED_DISTINCT_PRODUCT`, no accepted drug.
* Map: `BEVACIZUMAB / CHEMBL1201583`, **122 trials**, no refusal, matched alias `Bevacizumab awwb`.
* `Which trials evaluate bevacizumab-awwb。?` returns **12** originator rows, first
  `NCT00955305|EVALUATES|CHEMBL1201583|NCT00955305`.
* `Which companies sponsor bevacizumab-awwb。?` returns **12** originator rows, first
  `ORG:roche|SPONSORS_TRIAL_OF|CHEMBL1201583|`.
* `bevacizumab-awwb.` (ASCII full stop) and bare `bevacizumab-awwb` refuse correctly.
* The same resolver/linker disagreement occurs for `bevacizumab-awwb—` (trailing U+2014),
  `—bevacizumab-awwb`, `bevacizumab-awwb-`, and `-bevacizumab-awwb`.

**Cause:** the token-edge strip set at `src/query.py:147` differs from the resolver's `RE_PUNCT_EDGE`
at `src/textrules.py:283`, applied by `clean_surface` at `382-383`. The suffix guard is anchored to
both ends (`156-157`), so extra punctuation hides the suffix. Positive alias matching then calls
`canonical_key` (`339-346`), which removes the very punctuation that caused refusal to fail, recovering
the stored originator alias. The whole-item/eight-word scans at `src/query.py:99-110` cannot repair
this because every scanned run preserves the offending punctuation.

**Inherited:** the exact `514929c` linker also draws CHEMBL1201583 for U+3002. This remains a blocker
despite not being newly introduced.

Additional variants `(bevacizumab-awwb)`, `[bevacizumab-awwb]`, quoted `"bevacizumab-awwb"`, U+2010
or U+2014 internal hyphens, and quoted `"[89Zr] trastuzumab"` also draw their originators. For these
the full resolver itself also accepts the originator, so they are recorded as shared guard/normalization
limitations, not presented as exact resolver/linker disagreements. The U+3002 reproduction is sufficient
without an external pharmacology assumption.

## M6-B3: a trailing bare qualifier is detached from its own drug (blocker)

Exact input: `doxorubicin (nanoparticle and liposomal formulation)`.

The parenthetical describes one product. The full resolver returns **one** component, `doxorubicin`,
`BLOCKED_DISTINCT_PRODUCT`, no accepted drug. The current map instead draws **DOXORUBICIN / CHEMBL53463**,
**3 trials**, with no refused item. The exact question
`Which trials evaluate doxorubicin (nanoparticle and liposomal formulation)?` returns all **3** originator
trial rows, beginning `NCT01970540|EVALUATES|CHEMBL53463|NCT01970540`.

Independent natural counterpart: `bevacizumab (investigational and biosimilar)` also has only a blocked
component in the full resolver, but the map draws **BEVACIZUMAB / CHEMBL1201583**, **122 trials**, without
refusal. `Which trials evaluate bevacizumab (investigational and biosimilar)?` returns **12** originator
rows, beginning `NCT00955305|EVALUATES|CHEMBL1201583|NCT00955305`.

Remove the conjunction and both controls fail closed: `doxorubicin (nanoparticle liposomal formulation)`
and `bevacizumab (investigational biosimilar)` have no map centre and no QA evidence. The repaired forward
case, `liposomal and nanoparticle formulation of doxorubicin`, also refuses correctly.

**Cause:** the unconditional listing-word split at `src/query.py:167-174` separates the drug from the
right-hand qualifier, even inside one parenthetical product description. The drug's item is not qualified;
the later qualifier's item has no drug, so `192-197` sets `dangling` and immediately continues. That state
can affect only a later item at `183-184,199-201`; it never revisits the drug that precedes the qualifier.
It is also not emitted as a refusal when the input ends. Positive matching at `211-236` therefore accepts
the originator with no refusal disclosure. In contrast, the full resolver sees one cleaned component and
checks the original complete input via `src/normalize.py:707,729-735`.

This exposes the **forward-only carry design itself**. The user's allowance for excessive refusal inside
an item does not allow acceptance of this distinct product as its originator. No second drug is named;
the failure is a conjunction inside the description, with the qualifier to the right of its drug.

**Inherited:** both exact parenthetical failures also draw the same originator under the `514929c`
linker. The forward repair fixes the original M5 input but leaves this reverse ordering vulnerable.
Reproducer: `python -B audit_evidence_claims/m6/attacks/reversed_probe.py`.
[Eleven inputs with full current/prior map results, resolver components and QA evidence](reversed_results.json).
The earlier non-parenthetical `doxorubicin in nanoparticle and liposomal formulations` also leaks but its
resolver accepts the first component; the parenthetical cases above establish the stronger exact mismatch.

## Controls and limits

* All **16** suffix/tracer/liposomal/generic-version tests with 0, 4, 8 or 16 filler words on each side
  refuse. No new eight-word-window escape was demonstrated.
* `liposomal and nanoparticle formulation of doxorubicin`, `liposomal and sustained release doxorubicin`,
  and intervening `EGFR`/extra conjunction controls refuse the qualified drug.
* `Mvasi and bevacizumab`, `(Mvasi) and bevacizumab`, `Mvasi® and bevacizumab`, and `Abraxane and paclitaxel`
  retain the separately named originator and disclose the product refusal.
* Same-item fail-closed over-refusals and the known pegylated alias limitation are not new findings.
* Actual HTTP reproductions are owned by the primary reviewer; this file reports independent in-process
  results. No application code or tracked file was edited.
