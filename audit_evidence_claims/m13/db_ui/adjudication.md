# Independent adjudication: fully joined isotope and chelator

**A blocker is confirmed.** `89ZrDFO-daratumumab` and `89zrdfodaratumumab` name the same canonical stored tracer alias as `[89Zr]-DFO-daratumumab`, yet return DARATUMUMAB (`CHEMBL1743007`) without any refusal. This is an **inherited unclosed boundary**, not a regression introduced by HEAD: the exact HEAD^ query module produces the same leak on current app/rules/data. [Independent stages and comparison](adjudication_tracer.json), [root HTTP](../root_checks/independent_m13_http.json).

The evidence is repository-internal: the dictionary key `89zrdfodaratumumab` has the single AACT synonym `89zr-dfo-daratumumab` for DARATUMUMAB; `is_isotope_label('89Zr')` is true; the normally separated stored alias and `[89Zr]-DFO-daratumumab` are refused. No external assumption about a drug or isotope is needed.

| Exact input | Current map | Trial/sponsor QA rows | Exact HEAD^ query |
|---|---|---|---|
| `89ZrDFO-daratumumab` | DARATUMUMAB, no Refused | 2 / 2 | Same leak |
| `89zrdfodaratumumab` | DARATUMUMAB, no Refused | 2 / 2 | Same leak |
| `89ZrDFO-daratumumab, osimertinib` | DARATUMUMAB first, no Refused | 2 / 2 | Same leak |
| `[89Zr]-DFO-daratumumab` | Refused, no centre | 0 / 0 | Refused |
| `89zr-dfo-daratumumab` | Refused, no centre | 0 / 0 | Refused |
| `[89Z.r]-DFO-daratumumab` | Refused, no centre | 0 / 0 | DARATUMUMAB |
| `89Z_r-dfo-daratumumab` | Refused, no centre | 0 / 0 | DARATUMUMAB |
| `daratumumab` | DARATUMUMAB | 2 / 2 | Same accepted control |

Raw resolver, resolver veto, item linker, whole-name shortcut and public linker were each inspected. The leaking candidates resolve by ALIAS, veto `{}`, item/public Drug, and whole-name `None`. Therefore this is not a later override of an earlier refusal.

Causal chain:

1. Positive canonical lookup drops punctuation (`src/textrules.py:339-346`), so joining isotope and chelator keeps the same alias identity.
2. `_alnum_words` retains contiguous letters/digits as a single word (`src/query.py:111-113`). `89ZrDFO-daratumumab` gives `['89ZrDFO','daratumumab']`; `89zrdfodaratumumab` gives one long word.
3. HEAD's new inside-name loop joins whole words and stops above six characters (`src/query.py:258-269`). It never splits `89ZrDFO` into isotope `89Zr` and chelator `DFO`.
4. The remaining key-prefix check recognizes `89zr` but requires its remainder `dfodaratumumab` to be a separate same-drug alias (`src/query.py:290-295`). That remainder has no dictionary entry.
5. Raw tracer patterns require their own delimiters (`src/textrules.py:303-314`), so the resolver at `src/normalize.py:740-745` also misses the fully joined isotope. No veto remains before `Engine.explore` chooses the first surviving Drug (`src/app.py:88-95`).

The exact M12 blockers are **FIXED**. The broader guarantee remains violated because a spelling accepted as the same stored tracer identity can lose its refusal. A repair must preserve that identity across lookup-equivalent spellings; existing accepted controls and explicitly known over-refusals should remain separately recorded.
