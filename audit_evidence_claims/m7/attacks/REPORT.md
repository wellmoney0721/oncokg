# Round 7 independent originator-boundary attack

HEAD `9bd7cb4b5d9270bbe99cb5dfec3993502f6b5377`. Reproducer: `python -B audit_evidence_claims/m7/attacks/fresh_probe.py`.

**Approval blockers remain.** A new whole-name fast-path regression overrides a refusal that `_link` already gets right. Independently, parenthesized biosimilar names, Unicode hyphens, and a space-separated isotope prefix evade **both** the intervention resolver and `_link`. The same fast path also reintroduces cross-item salt identity selection.

Evidence: [93 exact cases, current resolver/block map/whole-name/item-linker/public-linker/map and predecessor maps](fresh_results.json), [compact comparison](fresh_summary.json), [44 actual HTTP requests](http_results.json), [owned server lifecycle](http_lifecycle.json), [stored aliases](dictionary_evidence.json). All 44 HTTP requests returned 200. The original `python -B -u src/app.py 8905` served worktree-identical HTML; its owned process terminated and its port closed. The ten QA inputs were exercised both in-process and over HTTP. These results do not depend on browser rendering.

The predecessor comparison replaces only `link_entities` and `_drug_spans` with their exact `b7a00f9` source, with its exact `_JOINERS`; current stored data and shared helper rules remain constant. In-process SQLite connections use `mode=ro`. No tracked/application file was edited. No network pharmacology assumptions are needed: each primary product/tracer spelling has a one-character or wrapper-only control that this repository itself refuses.

## Blocking finding A: whole-name fast path overrides an established refusal

Exact POST `/api/explore` payload:

```json
{"text":"bevacizumab-awwb?"}
```

HTTP 200 returns `center.id="CHEMBL1201583"`, `label="BEVACIZUMAB"`, `trials=122`, `matched_text="Bevacizumab awwb"`, and `also=[]`. The entire input names a qualified product, not an unqualified originator plus a separate accepted mention.

| Path / control | Observed result |
|---|---|
| `resolve_drug_string` through `/api/resolve` | `ALIAS / CHEMBL1201583`; no refusal |
| `_resolver_blocked("bevacizumab-awwb?")` | `{}` |
| `_link("bevacizumab-awwb?")` | only `Refused`, label `bevacizumab-awwb` |
| `_whole_name` / public `link_entities` | `Drug / CHEMBL1201583` |
| Exact `b7a00f9` linker map | refused `bevacizumab-awwb` |
| Current bare `bevacizumab-awwb` | refused |
| Current `bevacizumab-awwb!` | same originator leak; previous linker refused |
| Current `"bevacizumab-awwb"` including literal quotes | same originator leak even though current `_link` refuses; previous linker also leaked this quoted form |

**This is new versus `b7a00f9` for `?` and `!`.** Do not generalize that status to every wrapper variant.

Cause: `src/query.py:138-142` returns `_whole_name` before `_link`. `_whole_name` derives its lookup key from punctuation-stripped text (`191-194`) but checks `is_distinct_product` on the original punctuated text (`195-196`). The anchored suffix regex (`src/textrules.py:156-157,213`) fails on the punctuation. Aggressive canonicalization (`339-346`) nevertheless hits the stored originator alias. By contrast, `_link` removes the edge punctuation before checking its tokens (`src/query.py:217-220,252-264`) and correctly refuses this exact input; that result is never consulted. `Engine.explore` trusts the public link at `src/app.py:88-95`.

The precise QA control `Which trials evaluate bevacizumab-awwb?` has **zero evidence**, and `Which trials evaluate "bevacizumab-awwb"?` also has zero. Adding a question prefix prevents the whole-input alias hit and reaches the working item linker. This is a **map fast-path** blocker, not a claim that this exact punctuated QA sentence leaks.

Required outcome: whole-name recognition must preserve the refusal checks on the normalized text that enables the positive match. A genuine stored-name exception must not turn a correctly refused suffix into a drug merely because punctuation made the raw anchored guard miss it.

## Blocking finding B: shared refusal predicates accept equivalent distinct-product spellings

These cases fulfill the specifically requested attack: **both** the resolver and the independent list-item linker miss the refusal.

| Exact input | Resolver | `_link` and map | Control |
|---|---|---|---|
| `(bevacizumab-awwb)` | `ALIAS / CHEMBL1201583` | BEVACIZUMAB, 122 trials, no refusal | bare `bevacizumab-awwb` refuses |
| `[bevacizumab-awwb]` | same | same | bare suffix refuses |
| `bevacizumab‑awwb` with U+2011 NON-BREAKING HYPHEN | same | same | ASCII-hyphen suffix refuses |
| `bio‑similar bevacizumab` with U+2011 | `CONTAINED_ALIAS / CHEMBL1201583` plus unresolved qualifier | same | `bio-similar bevacizumab` refuses |

U+2010 and U+2014 substitutions also leak in the saved matrix. All named rows above have actual HTTP explore/resolve confirmation except the U+2010/U+2014 supplementary variants, which are in-process results.

QA impact, confirmed over HTTP:

| Exact question | Originator evidence |
|---|---|
| `Which trials evaluate (bevacizumab-awwb)?` | 12 rows, first `NCT00955305\|EVALUATES\|CHEMBL1201583\|NCT00955305` |
| `Which companies sponsor (bevacizumab-awwb)?` | 12 rows, first `ORG:roche\|SPONSORS_TRIAL_OF\|CHEMBL1201583\|` |
| `Which trials evaluate bevacizumab‑awwb?` (U+2011) | 12 originator trial rows |
| `Which trials evaluate bio‑similar bevacizumab?` (U+2011) | 12 originator trial rows |

Cause: `_link` deliberately retains parentheses/brackets at `src/query.py:217-220`; the anchored biosimilar suffix guard (`src/textrules.py:156-157`) does not tolerate those wrappers. The suffix pattern permits ASCII hyphen and en dash only; the `bio-similar` qualifier pattern permits ASCII hyphen only (`139-140`). Meanwhile `canonical_key` drops or normalizes these distinctions (`339-346`), enabling aliases the guard did not recognize. The resolver uses the same product predicate at `src/normalize.py:729-735`, so running it first cannot repair this shared blind spot. `_qualified` at `src/query.py:99-110` merely retries the same predicates over word runs.

These are **inherited**, confirmed with `b7a00f9`; they are not evidence that the latest repair introduced every refusal defect. They remain approval blockers because wrapping a refused product name, or replacing its hyphen with a normal Unicode hyphen, does not name the originator instead. An extra accepted occurrence of the originator is absent from every primary reproduction.

## Blocking finding C: a space-separated isotope prefix passes both gates

Exact input **`89Zr trastuzumab`** returns HTTP 200 with **TRASTUZUMAB / CHEMBL1201585**, **13 trials**, `also=[]`. The resolver returns `ALIAS` on stored synonym **`89zr-trastuzumab`**, and `_link` independently returns the same originator. `_resolver_blocked` is empty. Both **`89Zr-trastuzumab`** and **`[89Zr] trastuzumab`** refuse over HTTP.

`Which trials evaluate 89Zr trastuzumab?` returns **12** originator rows; first `NCT00016367|EVALUATES|CHEMBL1201585|NCT00016367`, whose stored intervention is `Trastuzumab`. The bracketed QA control returns zero evidence. `89Zr‑trastuzumab` with U+2011 also passes both gates in-process.

Cause: `src/textrules.py:303-305` requires either a hyphen after an unbracketed isotope or brackets around the isotope. A space-only prefix satisfies neither alternative. The isotope label predicate separately recognizes `89Zr` (`289-298`) but the resolver calls it on the complete component (`src/normalize.py:740-741`), not the isotope token; `_qualified` uses `is_radiotracer`, not `is_isotope_label` (`src/query.py:105-110`). Canonical matching then reaches the already stored radiolabel synonym (`src/textrules.py:339-346`).

This is **inherited**, confirmed using `b7a00f9`. The repository's own alias and rejected one-character spelling controls establish the tracer premise; this finding does not assume an external clinical relationship.

## Separate should-fix: canonical-key equality is broader than exactly one stored name

These are current regressions versus `b7a00f9`, not extra refused-product blockers:

| Exact input | Current map | `_link` and prior map | Stored alias actually matched |
|---|---|---|---|
| `Erlotinib, hydrochloride` | ERLOTINIB HYDROCHLORIDE / CHEMBL1079742, 31 trials | ERLOTINIB / CHEMBL553, 118 trials | `ERLOTINIB HYDROCHLORIDE` |
| `osimertinib,mesylate` | OSIMERTINIB MESYLATE / CHEMBL3545063, 7 trials | OSIMERTINIB / CHEMBL3353410, 79 trials | `OSIMERTINIB MESYLATE` |
| `is a` | ISATUXIMAB / CHEMBL3545131, 1 trial | no entity / not_found | `isa` |

All three rows have actual HTTP confirmation. The comma inputs have no exact case-insensitive stored-alias match; [dictionary evidence](dictionary_evidence.json) records every index hit. Full resolver requests retain the parent as one component and leave `hydrochloride`/`mesylate` unresolved. The map's salt selection therefore comes from the whole-name exception, which erases the declared item boundary. The list linker itself stays within the boundary. Slash/pipe and `and` controls preserve the parent. Semicolon and all three declared CJK comma/semicolon variants repeat the salt regression in-process.

`_whole_name` at `src/query.py:189-195` excludes slash/pipe and listing words, but accepts every string with an equivalent aggressive key. It does not compare to the stored name's actual punctuation/token boundaries. This also bypasses the explicit `is a` safeguard at `src/query.py:302-307`. Genuine stored-punctuation controls `CP-358,774` and `Rapamycin, 42-o-(2-hydroxyethyl)-` have exact stored alias matches and retain their intended complete identities; preserving those does not require joining arbitrary new comma lists.

The corresponding prefixed QA inputs `Which trials evaluate Erlotinib, hydrochloride?` and `Which trials evaluate osimertinib,mesylate?` correctly return parent-drug evidence. The current mismatch is in selecting the map centre, not a claim that the salt's displayed count differs from its stored value.

## Controls and scope limits

* Mixed separately accepted aliases (`biosimilar anastrozole, Arimidex`, slash variant, `Mvasi and bevacizumab`, `bevacizumab-awwb, bevacizumab`) retain their independently named accepted drug. Whole-item over-refusal is not used as a failure criterion.
* `CP-358,774`, the complete rapamycin alias, and the long paclitaxel-poliglumex alias were exercised as exact-name controls. Known `Pegylated interferon alfa-2a` over-refusal is retained and not newly escalated.
* Qualifier carry with both punctuation and conjunction (`biosimilar, and osimertinib`, etc.) is recorded diagnostically. It is not promoted to a blocker because the requested carry rule could intentionally interpret the conjunction across that punctuation. The unambiguous fast-path and shared-refusal counterexamples are sufficient.
* No assertion is made that adding more calls to the existing resolver can repair findings B/C: both paths demonstrably share the failing predicates. No application changes were applied.
