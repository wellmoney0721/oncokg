# Names / question-answering review at c64f433

## Scope and status

Freshly reran all literal name cases in m1 `names_probe.py`, `names_extra_probe.py`, and `names_product_probe.py`, plus the m1 report's `MET`, mixed-case whitespace and 500-character HTTP cases: **62 distinct current HTTP reproductions**. `names_reproduction_results.json` includes current/old linker output, resolver tiers and current map output. `names_regressions.json` contains 13 additional current/baseline HTTP comparisons. The baseline comparison replaces only `link_entities` with the exact AST-extracted bfcb83d method; all other code and data remain current, isolating the ten-line repair's effect. Baseline code is never written into tracked files. All answers use `Engine.ask`, which explicitly disables models.

## M1 outcomes

| M1 finding / exact input | Status | Current evidence |
|---|---|---|
| B1 `bevacizumab - awwb`, `89Zr - trastuzumab`, `[89Zr] trastuzumab` | **FIXED for the exact m1 reproductions** | All return a `refused` response, without a centre. `bevacizumab-awwb`, `[89Zr]trastuzumab` and en-dash `bevacizumab – awwb` also refuse. Broader guarantee still fails at R1 below. |
| Identity ambiguity: `Roche`, `MET` | **FIXED for the m1 reproductions** | Primary centres remain FOLIC ACID / METFORMIN, but `also` now names Company `ORG:roche` / Target `ENSG00000105976`; selected alias is in `center.matched_text`. |
| Multi-entity selection: `osimertinib EGFR`, reversed order | **FIXED disclosure** | The first hit remains selected and the second is now disclosed in `also`. |
| `Mvasi and bevacizumab` silently discarded refused span | **FIXED** | BEVACIZUMAB is explicitly named and selected; `also=[{"refused":"Mvasi and"}]` now discloses refusal. `Mvasi bevacizumab` still refuses. |
| Long HTTP input silently truncates | **NOT FIXED** (existing qualification) | `"x"*500 + " osimertinib"` returns not_found for the 500-character prefix; `"osimertinib " + "x"*600` maps OSIMERTINIB. Handler still slices to 500 characters. |

Salt controls remain distinct: Tarceva / erlotinib hydrochloride -> CHEMBL1079742; erlotinib -> CHEMBL553; osimertinib mesylate -> CHEMBL3545063. ASCII case, fullwidth OSIMERTINIB and AVASTIN, and HTTP surrounding whitespace still work. Lowercase NCT/CHEMBL IDs and investigator names remain unsupported. All seven stored retired IDs return not_found; former company names may resolve to their live curated successors (`names_boundary_details.json`). B4's mutated drug fixture is assigned to the DB reviewer.

## R1 — P1 blocker: added refusal windows can select the refused product and suppress the valid drug

Exact `POST /api/explore` text:

`osimertinib and generic version of bevacizumab`

Current result: centre BEVACIZUMAB / CHEMBL1201583, 122 trials; `also` says `osimertinib and generic version of` was refused. The bfcb83d linker selected OSIMERTINIB first. The unchanged resolver independently identifies `osimertinib` as EXACT and `generic version of bevacizumab` as BLOCKED_DISTINCT_PRODUCT. Thus this is not an outside pharmacology judgement: the new window logic suppresses the accepted component and draws the component the same application refuses.

Cause: `src/query.py:146-162` checks largest windows first. The first five words contain the distinct-product phrase `generic version`, so all five tokens are marked refused. The overlapping window containing the actual qualified drug is then skipped at lines 148-149; `bevacizumab` remains available and is accepted at lines 171-178. `src/app.py:87-95` selects that remaining hit. The new ten-line hunk is `src/query.py:153-162`.

This also changes QA, which shares the linker:

| Exact question | bfcb83d-linker first evidence | Current first evidence |
|---|---|---|
| `Which trials evaluate osimertinib and generic version of bevacizumab?` | `NCT03909334\|EVALUATES\|CHEMBL3353410\|NCT03909334` | `NCT00955305\|EVALUATES\|CHEMBL1201583\|NCT00955305` |
| `Which companies sponsor osimertinib and generic version of bevacizumab?` | `ORG:astrazeneca\|SPONSORS_TRIAL_OF\|CHEMBL3353410\|` | `ORG:roche\|SPONSORS_TRIAL_OF\|CHEMBL1201583\|` |

Both answers have 12 evidence rows, so checking count/success alone misses the switched subject. Exact responses and source-controlled baseline comparisons are in `names_regressions.json` and `names_boundary_details.json`.

Controls distinguish repaired and inherited behavior:

- `generic version of bevacizumab` now correctly refuses; it mapped BEVACIZUMAB before.
- `generic version of bevacizumab and osimertinib` now selects OSIMERTINIB and refuses the qualified product.
- `What is the generic version of bevacizumab?` still maps BEVACIZUMAB; this exact full-question bypass is inherited (both old/current), not a new regression. It remains a counterexample to blanket refusal guarantees.
- `osimertinib and oral azacitidine` now refuses the whole input, including the valid osimertinib that the old linker retained. `[89Zr] trastuzumab and osimertinib` likewise refuses the valid trailing osimertinib; reversed order preserves it. These are new over-refusal regressions from the same overly broad window rule, not separate wrong-edge claims.

Required outcome: identify the refusal span belonging to the actual distinct product/tracer, exclude its molecule consistently, and retain separately named valid entities regardless of word order. The generic-version mixed input must not select BEVACIZUMAB.

## Residual ambiguity qualification

The live company index still contains zero multi-ID aliases. An index-only fixture (no DB write) sets `companies['sharedbrand']=['ORG:astrazeneca','ORG:roche']`. `Sharedbrand` discloses both; `Sharedbrand company` silently drops `also_matching_ids=['ORG:roche']` and returns `also=[]`. `src/app.py:95-107` only restores company alternatives by the entire input key and ignores the hit's `also_matching_ids` from `src/query.py:189-197`. This is a should-fix limitation of the ambiguity repair, not a current-snapshot multi-ID defect. Evidence: `names_boundary_details.json`.

Unicode suffix variants (`bevacizumab—awwb`, `bevacizumab－awwb`), `bevacizumab awwb`, `ABP 215`, and `89Zr trastuzumab` still map their stored aliases, but the current whole-string resolver also accepts them. They are unchanged shared-boundary limitations; this review does not mislabel them as new linker regressions or use unverified pharmacology to manufacture a blocker.

## Demo questions

All **7 unique page/CLI demo questions** are exactly identical between current and bfcb83d-linker responses, including entities, evidence, answer and checks: Tagrisso trials (12 evidence rows), osimertinib companies (12), ALK drugs (11), osimertinib target (1), AstraZeneca portfolio (12), Mvasi refusal (0), and France refusal (0). `names_demo_compare.py` / `names_demo_results.json` preserve the extraction and complete comparisons. The parent reviewer runs the requested full suite and actual CLI server HTTP demos separately.

## Reproduce

Use `python -B audit_evidence_claims/m2b/names_reproduction.py`, `names_regressions.py`, `names_boundary_details.py`, `names_demo_compare.py` and `names_label_scan.py`. Each script writes only under m2b; temporary HTTP servers are stopped in finally blocks. No application file, database content, tracked file or model service was changed or called.
