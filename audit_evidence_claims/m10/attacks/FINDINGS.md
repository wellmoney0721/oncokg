# Round 10 independent originator and tracer attacks

Reviewed `c364c84` against the supplied round-10 brief. No application or earlier audit file was edited. Both scripts run against the live snapshot through a read-only SQLite connection after Engine construction; bytecode generation is disabled. All files from this worker are under this directory.

## Reproducible evidence

- `python -B audit_evidence_claims/m10/attacks/probe.py`: **1,224 inputs**, recording raw resolver, resolver veto, list linker, whole-name shortcut, public linker, map, and full dictionary hit. [Full output](probe_results.json), [candidate positives](positive_summary.json). **396 Drug maps are a triage population, not 396 findings**: controls, chemical locants, genuinely labelled stored drugs, and explicit list-policy boundary cases are included.
- `python -B audit_evidence_claims/m10/attacks/focus.py`: **35 exact inputs** against current and exact parent-commit query modules (`3a362eb4f156ea252301d18507ff0a733d0b601e`), each with map, trial QA and sponsor QA. [Output](focus_results.json), [HTTP-ready input list](http_inputs.json). All other application code/data are held current; these are query-module counterfactuals, not a reconstructed old deployment.
- Root performs actual original-CLI HTTP confirmation independently. This worker's evidence above is direct Engine execution, not HTTP.

## Blocking candidates, exact inputs

### A. New regression: a stored name absorbs its trailing isotope before `_marked` checks adjacent words

`A33 124i` draws the **ADAKITUG / CHEMBL5314551 centre**, with antibody props and one outgoing ACTS_ON group for **CXCL8 / INHIBITOR**, instead of refusal. The dictionary explicitly contains `A33 124i` as a ChEMBL synonym of ADAKITUG. `T.is_isotope_label("124i")` is true (`src/textrules.py:289-298`), and exact parent query code refuses this exact input. Current `A33 124 i`, `A33 [124i]`, and `A33 124I` also draw the ADAKITUG centre; `124i A33` returns not_found with no centre, rather than a refusal. The preferred-name control `ADAKITUG` remains available. ADAKITUG has **zero live trials**, so both QA forms have zero evidence; this finding does not claim invented trial evidence. Its existing ACTS_ON edge is displayed under the wrongly accepted tracer name.

Every current stage misses the tracer distinction: raw resolver ALIAS to CHEMBL5314551; resolver veto `{}`; list linker Drug; whole-name shortcut Drug for the exact `A33 124i`; final map ADAKITUG. At `src/query.py:248-252`, `own` is `["A33", "124i"]`, but only `own[:1]` and `own[:2]` are tested. Neither finds the trailing label. The match has already consumed that label, so it is absent from `nxt`. The exact-name shortcut (`258-275`) consequently receives no refusal and returns the same wrong identity. This is the tracer-alias exception risk expressly cited by the round-9 repair note; the new adjacent-name implementation does not cover the end of an accepted name itself.

### B. New regression: the lone isotope-shaped alias allowance is applied inside longer inputs

`18F fluorothymidine` and `18-F fluorothymidine` draw **FLUDEOXYGLUCOSE F 18 / CHEMBL2030434 / 1 live trial**, even though the supplied name is not fludeoxyglucose. Trial QA and sponsor QA each return **one fludeoxyglucose evidence row**. The stronger vocabulary-only control `18F nonexistingdrug` does the same. The dictionary has a standalone `18f` synonym for this drug; `fluorothymidine` itself is absent. Exact parent query code refused all three longer inputs; both versions accept the permitted lone `18f` control.

For the unbracketed forms, raw resolver is UNRESOLVED, resolver veto `{}`, list/public linker accepts only the `18F`/`18-F` token, whole-name shortcut is `None`, and final map is FLUDEOXYGLUCOSE F 18. No refusal stage fires. `_marked` explicitly excludes `ws == own` (`src/query.py:252`) without requiring this token to be the entire item. Therefore an isotope token's presence in the alias index can turn a different or unknown labelled substance into that alias's therapeutic graph. `src/query.py:384-402` then records that token as a complete Drug hit. This is separate from valid lone `566C`/`9-ac`/`5ac` exceptions and from the recorded over-refusals.

### C. Inherited hole: two-token slicing happens before punctuation-only tokens are removed

`trastuzumab 89 - Zr`, `trastuzumab [89 - Zr]`, and `trastuzumab 89 _ Zr` draw **TRASTUZUMAB / CHEMBL1201585 / 13 live trials**, with **12 trial and 12 sponsor QA rows**. Controls `trastuzumab 89 Zr`, `trastuzumab 89-Zr`, and `trastuzumab [89.Zr]` refuse, as does current prefix `89 - Zr trastuzumab`. This is inside one list item; no comma/slash/list-word policy ambiguity is involved.

Raw resolver accepts the unlabelled drug; veto is `{}`; list/public linker emits Drug without Refused; whole-name is `None`. At `src/query.py:245`, `after` is limited to two original whitespace tokens (`89`, `-`) **before** `_alnum_words` at `250` discards `-`. `Zr` is never examined. The user specified one or two **alnum words, any separator**; this code instead budgets punctuation as a word. Exact parent query code also leaks, so this is a newly reported inherited hole, not a claim that the latest commit introduced it.

### D. Inherited multiword qualifier normalization holes

`generic-version of bevacizumab` and `generic_version of bevacizumab` draw **BEVACIZUMAB / CHEMBL1201583 / 122 live trials**, and each QA form has **12 rows**. `albumin - bound paclitaxel` draws **PACLITAXEL / CHEMBL428647 / 234 trials**, also **12/12 QA rows**. `follow-on-biologic bevacizumab` leaks likewise. Controls `generic version of bevacizumab`, `albumin-bound paclitaxel`, and `follow-on biologic bevacizumab` refuse.

All three guard stages miss; no Refused hit occurs. `_qualified` only preserves whitespace or folds punctuation to hyphen (`src/query.py:127-134`), whereas the existing patterns require whitespace between `generic`/`version` and `on`/`biologic`, or at most one whitespace-or-hyphen between `albumin`/`bound` (`src/textrules.py:142-149`). For example the underscore form becomes `generic-version`, which still fails `generic\s+version`. All are inherited in the parent-module comparison. These are clear product qualifiers, rather than isotope or alias classification guesses.

## Cases deliberately not promoted to blockers

Slash/comma/semicolon/pipe separators can detach suffix or isotope words, but these conflict with the expressly adopted list-item boundary policy, so their maps are retained as observations only. `89Zr labelled trastuzumab` and element-first notation are outside the narrow just-adjacent label design; no separate blocker is asserted for those. The known M5-S2/rapamycin/ADC over-refusals are not reclassified as blockers. Stored names whose chemical locants resemble isotopes and true isotope-bearing drugs require individual identity assessment; the broad alias-scan positives do not establish wrongdoing by themselves.

## Spec axis (under 400 words)

The brief requires that a refused product never draw its originator and asks whether the map draws anything the input does not name. Current code still violates that outcome for `A33 124i` (new suffix-isotope regression), `18F fluorothymidine` (new isotope-token substitution), `trastuzumab 89 - Zr` (inherited separation hole), and explicit product descriptions such as `albumin - bound paclitaxel` (inherited pattern hole). The current design specifically promises isotope inspection in one or two alnum words with any separator; inspecting only two raw tokens and only the beginning of a matched alias is partial implementation. Existing names and metadata controls continue to distinguish accepted bare molecules from qualified products. Evidence and counterfactuals above support changes required; no unrelated feature or scope change is requested.
