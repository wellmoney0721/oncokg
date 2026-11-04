# Relation-map confirmation — round 38

Reviewed HEAD **`e821094d1544da4a133c53af24fedc569337d283`** against the approved **`2b1aca18faeef72a5e090dbc3af4ba6151b4ae80`**, using `git diff 2b1aca1...HEAD`, on 2026-11-04. Scope: section 0 of `web/try.html`, `POST /api/explore`, and `Engine.explore`, under the [round-32 approval bar](../m32/brief.md), [round-34 name policy](../m34/brief.md), and [round-37 amendment](../m37/brief.md).

**APPROVE within the specified relation-map scope.** M37-S1 and M37-S3 are fixed, M37-S2 remains the recorded recall tradeoff, and the exact prior map blocker reproductions remain fixed. No new blocker or should-fix was established. The four historical changes described below are changes between two undrawn rejection states, not new map admissions.

## Change boundary and method

The only production behavior change is `_DESCRIPTOR_RUN` in `src/query.py:120`: `[()\[\]{}+\-/_\s−±]*` becomes `(?:[^\w]|_)*`. The adjacent run now includes punctuation, symbols and invisible characters; the existing sign test rejects a shared-key preferred-name reading when that run contains a sign. The immediately adjacent word/sign check and `_SIGNS` are unchanged. Regression cases accompany the change in `tests/test_app.py`.

Both the complete `src/app.py` AST with docstrings removed and the inline page JavaScript are identical to the approved commit. The root lane separately compared `Engine.explore` without its docstring. Thus unchanged map logic is confirmed from source, while its indirect use of the changed linker is still exercised by the map sweeps. All **1,114,112 Unicode code points** agree between the new run predicate and an independent non-alphanumeric predicate: **975,555 run characters / 138,557 boundaries**, zero mismatches. [Source comparison and predicate evidence](source/static_provenance.json), [root confirmation](root_confirmation.json).

## M37-S1 — FIXED

The exact four headline questions now return **no linked entity and zero evidence** in `/api/ask`, `/api/structured`, and `/api/check`; their `/api/explore` requests remain undrawn. The freshly executed approved parent reads CHEMBL3 and retrieves two evidence rows for each.

| Exact question | Current question result | Current map |
|---|---|---|
| `What trials evaluate (+/-.)NICOTINE?` | No entity; zero evidence | `not_found` |
| `What trials evaluate (+/-☢)NICOTINE?` | No entity; zero evidence | `not_found` |
| `What trials evaluate (+/-$)NICOTINE?` | No entity; zero evidence | `not_found` |
| `What trials evaluate NICOTINE(.+/-)?` | No entity; zero evidence | `not_found` |

All **28 exact punctuation/mirrored questions** from the M37 evidence were rerun: none links an entity, none retrieves evidence, and none draws a map center. Twelve of these question readings change from the approved parent, all closing the reported leak. The three inherited examples also close: `What trials evaluate 〔+/-〕NICOTINE?`, `What trials evaluate NICOTINE«+/-»?`, and `"What trials evaluate (+/-)\u200bNICOTINE?"` (actual U+200B). [Full root HTTP evidence](exact_question_http.json), [compact results](exact_question_summary.json), [independent 28-case comparison](contract/supplement_classification.json).

Root exercised **41 questions × four endpoints = 164 HTTP calls**, plus ten documentation map controls. The 41 include M36-S1, the retained M37-S2 cases, and positive controls. There are zero question assertion failures. `NICOTINE`, `(NICOTINE)`, comma-separated, slash-separated and `and` controls retain their expected reading. Counts overlap with the independent contract lane and are not summed as unique test inputs.

## M37-S3 — FIXED; M37-S2 — retained as specified

The actual served page is byte-identical to `web/try.html`. Its section 0 description now explicitly states the punctuation-preserving exception for a bracketed group without letters/digits. `Engine.explore` documents the same exception at `src/app.py:110–116`. The exact M37 documentation inputs behave as follows:

| Exact input | Current result |
|---|---|
| `(+/-)NICOTINE` | CHEMBL440464 |
| `(+/-)NICO/TINE` | `not_found` |
| `(+/-)NICOTINE!` | `not_one_name` |
| `[+/-]NICOTINE` | `not_found` |
| `()osimertinib` | `not_one_name` |

Space, dash-style, case, fullwidth and accented controls—`( + / - )NICOTINE`, `(+/–)NICOTINE`, `(+/-)nicotine`, `（＋/－）NICOTINE`, `(+/-)NÍCOTINE`—still draw CHEMBL440464. [Exact HTTP controls](documentation_http.json), [served wording and docstring](root_confirmation.json), [served page](served_try.html).

`What trials evaluate NICOTINE + osimertinib?`, `What trials evaluate osimertinib + NICOTINE?`, and `What trials evaluate NICOTINE - osimertinib?` continue to link only CHEMBL3353410. The `/` and `and` controls retain both drugs. These match the approved parent and the explicitly retained adjacent-sign rule; they are not a new regression. The 360-case expanded question supplement changes 118 descriptor cases, introduces no new IDs, and leaves the ordinary control/list cohorts unchanged. [Supplement classification](contract/supplement_classification.json), [paired results](contract/question_supplement.json).

## Earlier blocker confirmation

**M36-B1, M36-B2, M36-S1 and earlier map blocker reproductions remain FIXED under the current name policy.** FIXED describes exposure through the map, not upstream alias curation or restoration of excluded recall.

| Finding | Exact current evidence |
|---|---|
| M36-B1 | `(-_)-ARTEMISININ`, `(_-)-ARTEMISININ`, `[-_]-ARTEMISININ`, `"(-\u200b_\u0301)-ARTEMISININ"`, `"(-\uff3f)-ARTEMISININ"`, `"(-\ufe4d)-ARTEMISININ"`, `(-())-ARTEMISININ`, `〔-〕-ARTEMISININ`, `«-»-ARTEMISININ` all remain undrawn. All seven underscores U+005F, U+FE33, U+FE34, U+FE4D, U+FE4E, U+FE4F, U+FF3F are individually confirmed over HTTP. |
| M36-B2 | `(+/-☢)NICOTINE`, `(±☢)NICOTINE`, `(+/-$)NICOTINE`, `(+/-×)NICOTINE`, `(+/☢-)NICOTINE`, `(+/×-)NICOTINE` all return `not_found`; no wrong CHEMBL440464 center. |
| M36-S1 | `What trials evaluate ((+/-))NICOTINE?` and `What does NICOTINE((+/-)) target?` have no linked entity and zero evidence across all three question endpoints; no map center. |
| M32–M35 | 124 exact map cases, their question follow-ups and 456 brand refusal variants were rerun. All map results match the saved approved M37 responses; 456/456 variants remain refused. Exact per-finding inputs and results are retained in the linked ledger. |

[M36 77-request HTTP evidence](replay/m36_exact_http.json), [M36 assertions](replay/m36_exact_summary.json), [M32–M36 exact finding ledger](replay/recent_findings.md), [brand variants](replay/m33_brand_variants_http.json), [replay validation](replay/exact_validation.json).

The fresh **4,703-input historical map corpus** returns **300 centers, 1,434 refusals, 2,555 `alias_only`, 333 `not_one_name`, 77 `not_found`, four choices**. Independent membership, ambiguity, choice-set and execution checks have zero failures. The only four response changes from saved M37 are `(+/-$)NICOTINE`, `(+/-×)NICOTINE`, `(+/-☢)NICOTINE`, `(±☢)NICOTINE`: **`not_one_name` → `not_found`** because the erroneous fallback entity is gone. None becomes drawable. [Corpus summary](replay/corpus_summary.json), [fresh results](replay/corpus_results.json), [all changes](replay/parent_corpus_changes.json).

All 275 inherited naming finding rows have fresh case dispositions: **260 FIXED / 15 NOT FIXED for the map**. The residuals are nine recorded over-refusals and six deliberately excluded alias-recall cohorts. Including three old question-only residuals gives 257 FIXED / 18 NOT FIXED overall. The private M1 retired-node fixture passes. This round replays the consolidated exact-input corpus and targeted fixtures; it does not claim to rerun all 123 historical leaf scripts from M37. [Historical ledger](replay/historical_table.md), [counts](replay/matrix_summary.json), [method and limitations](replay/FINDINGS.md).

## Regression checks

- **`python -m pytest tests -q -p no:cacheprovider`: 366 passed in 114.35 seconds**, exit 0, no warnings; wrapper elapsed 116.286 seconds. Bytecode suppression and temporary directories under m38 were used. [Output](pytest.txt), [command/timing](pytest_meta.json).
- **36 shipped demos:** fresh HTTP responses match direct current Engine results and freshly executed parent-query results, zero changes. Inputs were extracted from the current page's JavaScript. [Demo comparison](contract/demo_previous_comparison.json).
- **99 shared keys / 708 question cases:** zero parent/current changes. [Shared-key comparison](contract/shared_key_question_comparison.json).
- **1,648 historical questions:** freshly loaded parent `app.py` and `query.py` versus HEAD, 1,648 complete responses identical, zero errors, 55.629 seconds. This is actual parent execution, not same-HEAD relinking. [Summary and parent hashes](replay/parent_qa_summary.json), [responses](replay/parent_qa_results.json).
- **Current intervention inventory:** 10,520 processed intervention/other-name occurrences, 4,604 distinct strings, zero parent/current entity changes. This explicitly inventoried set is not claimed to be the old 9,746-case headline corpus. [Source pointers and paired results](contract/intervention_comparison.json), [summary](contract/intervention_summary.json).
- **Expanded questions:** 312 boundary cases unchanged; 540 composition cases have 120 tightened readings and no new IDs; the 360-case supplement has 118 descriptor-only changes. No map centers occur in any of these matrices. The overlapping counts are not summed as independent defects. [Contract summary](contract/summary.json).

## Map source sweep

The fresh independent sweep covers **22,956 distinct inputs from 34,429 records**, including **all 9,581 drug alias entries**, preferred names, index spellings and keys, SQL node labels, target symbols, company keys and disease keys. It includes **16,015 literal source spellings/read keys and 6,941 additional canonical-only index strings**, plus all **1,696 alias occurrences omitted from the lookup index**. The independent oracle reconstructs admissions from source records and SQL and implements normalization with its own character scanner; it does not use `Engine.names` or `app._sig`.

| Current map result | Count |
|---|---:|
| Center | 10,088 |
| `alias_only` | 12,486 |
| Refused | 354 |
| `choose` | 8 |
| `not_found` | 5 |
| `not_one_name` | 15 |

The sweep completed in **483.628 seconds**, with **zero membership, stored-refusal, silent-ambiguity or live-choice failures and zero exceptions**. There are **zero changed, added or removed inputs versus saved M37 results**. This compares fresh HEAD execution against saved prior compact responses, not a freshly executed parent Engine sweep. Compact responses retain state/center/choice details and omit relation groups; the separate SQL oracle below verifies relation groups. [Source inventory](source/all_source_records.json), [fresh responses](source/source_sweep.json), [assertions/counts](source/source_summary.json), [prior comparison](source/source_parent_changes.json), [source classes](source/source_classified_summary.json).

All **182 literal refused spellings × 13 variants = 2,366 cases** remain refused. All **1,066 preferred names × six significant suffixes = 6,396 cases** remain undrawn. A separate 84 synthetic canonical-only keys × 13 = 1,092 cases yield 1,074 refusals, 12 `alias_only`, six `not_found`, and no centers. The latter 18 raw assertion rows are inherited nonliteral-key cases, not hidden failures of the literal-source refusal contract. All these responses match saved M37. [Classified refusal variants](source/refusal_variants_classified.json), [suffix results](source/significant_suffixes_summary.json), [validation](source/validation.json).

## Guarantees A–G

| Guarantee | Fresh result and qualification |
|---|---|
| A — relation/direction | Independent SQL oracle covers **6,469 live centers / 22 relation combinations**, zero errors, **293.647 seconds**. Self-loops, unknown relation/type and sponsorship roles pass dedicated fixtures. [SQL oracle](contract/db_validate.json), [special cases](contract/self_loop_unknown.json). |
| B — names/IDs/choices | Historical/source oracles, exact blocker cases, live choices, ID click-through and private retired-node fixtures pass within the approved name policy. [Exact ledger](replay/recent_findings.md), [choice behavior](contract/choose_ui.json), [retirement](replay/names_retired_http_results.json). |
| C — stored values/counts | **19/19 DB assertions** pass, including stored scores, missing/zero/boolean distinctions, malformed properties, live counts and chunking. Synthetic Infinity remains a controlled HTTP 400, as previously recorded. [Assertions](contract/db_assertions.json), [numeric fixture](contract/db_numeric_fixture.json). |
| D — ordering/cuts/totals | SQL weights and totals, tie ordering, page subset allocation and cut notices pass. [SQL oracle](contract/db_validate.json), [page harness](contract/ui_harness_results.json). |
| E — page safety/state | **26/26 UI assertions** pass for escaped labels/IDs/URLs, safe choices and alias replies, click-through, trails, stale replies, duplicate clicks and error recovery. This is executed page JavaScript in a Node DOM/fetch harness, not painted-browser layout. [Assertions](contract/ui_assertions.json), [state cases](contract/ui_regressions.json). |
| F — server | Invalid/empty/oversized requests are controlled, valid requests recover, and 24 concurrent map calls pass. Parser-detail disclosure and blank-submit retention remain recorded limitations. [Server checks](contract/server_checks.json), [page callbacks](contract/ui_m3_checks.json). |
| G — docs/read-only/no model | M37-S3 is fixed; README counts correctly say 366. The inspected request path remains read-only and avoids model calls. Full tracked/data integrity is verified below. [Documentation evidence](root_confirmation.json), [contract summary](contract/summary.json). |

Previously recorded source-data issues, including THEOPHYLLINE's stored type, are not repaired or promoted to new findings. No new upstream identity claim was established; no new external identity validation is claimed.

## Standards axis

**Zero hard documented-standard violations identified.** The pinned comparison is `git diff 2b1aca1...HEAD`. No repository AGENTS.md or separate current coding-style standard was found; the supplied evidence-backed review and no-tracked-edit instructions govern. The change is a string-predicate adjustment with regression coverage and documentation updates. SQL parameterization, live-row filtering, page escaping, read-only behavior and model-free request handling remain intact. No undocumented style preference or unrelated tracker setup was imposed. [Independent standards review](contract/STANDARDS.md).

## Spec axis

**Zero established map blockers or new should-fix deviations.** The requested adjacent-run character contract passes exhaustive predicate testing; the page/docstring state the strict punctuation exception. The inherited rule that a refused stored name stays refused passes the literal-source variant probes, and the independent complete source inventory has no admission/ambiguity/refusal failures. The recorded sign-separated-list recall cost is retained as requested. No scope creep was found. [Independent specification review](source/spec_axis.md).

The axes remain separate: **Standards: zero hard violations. Spec: zero newly established blocker/should-fix findings.** Existing accepted recall and source-curation limitations remain recorded.

## Integrity and limits

All **7,837 checked files**—the tracked baseline plus the processed SQLite database and resolved dictionary—retain their initial SHA-256 values. **Zero changed, zero added to the tracked baseline; tracked git status is empty and HEAD is unchanged.** Bytecode generation was disabled and temporary files confined to m38. [Initial hashes](integrity_before.json), [final integrity](integrity_final.json).

The actual root CLI server `python src/app.py 8938` was stopped after its consumers released it; contract ports 9800/9801 are also closed. The private retirement fixture shuts down its own server. [Root lifecycle/closure](server_lifecycle.json), [contract lifecycle](contract/lifecycle.json).

No production repair is made, so the conditional KOA Studio/KhOpenApi code-change comparison instruction is not triggered. All audit writes are confined to `audit_evidence_claims/m38/`.

The verdict concerns the specified map/name contract, not universal free-text refusal or scientific certification of every upstream identity. Previously recorded source curation and recall exclusions remain separate from code defects. Source and historical comparisons against saved M37 responses are explicitly identified; focused question comparisons execute the actual parent implementation. Page JavaScript harness results do not establish painted-browser layout.

VERDICT: APPROVE
