# Round 34 of the relation-map review

## Before you start

- Read the round-32 brief, `audit_evidence_claims/m32/brief.md`, for the scope, guarantees and approval bar. Read the round-33 report at `audit_evidence_claims/m33/REPORT.md`.
- Repairs are in `CODEX_MAP_M1_VERDICT.md`, section "Round 33".
- Review the latest commit on HEAD.
- Run the tests with `python -m pytest tests -q -p no:cacheprovider`; expect 362.
- Start the page with `python src/app.py <port>`, on any port except 8765.

## What changed since round 33

The changes are in `src/app.py` `Engine.__init__` and `Engine.explore`, and in `src/query.py`.

- **Drugs are read only by their ChEMBL preferred name.** The map still compares names by `_sig`, as in round 33.
  - Every other stored name of a drug goes into `alias_only`: trade names, ChEMBL synonyms and registry (AACT) synonyms. Typing one returns the reply `alias_only`, and the page asks for the preferred name.
  - This replaces round 33's partial source exclusions, which had the replies `registry_name` and `biologic_synonym`.
  - Why: the round-33 data findings showed that trade names, like synonyms, file combination products, formulations and biosimilars under one molecule.
- **The map also reads:** every node's own label, target symbols, and company and disease keys. The company and disease keys only match input whose `_sig` equals the dictionary key.
- **A refused stored name stays refused, however it is spelt.** The question linker checks every stored name that matches the input's `_sig`, whether that name is read or `alias_only`. If any is refused, the input is refused. This repairs M33-B1: `Myocet™`, `My/o/cet`, `Inf/lectra` and `Megace/ES` are now refused.
- **More names in `_OTHER_PRODUCT_NAMES` (`src/query.py`).** The question boxes now also refuse the round-33 combination products, plus PRED-G, NEO-DELTA-CORTEF and LEP-ETU.
- **The preferred-name rule for a shared key in a question** now needs the name to be written as a word of its own. This repairs M33-S1, "(+/-)NICOTINE".
- **Docs:** README defects 9 and 15 in both languages, and section 0 of `web/try.html`.

## What to do

1. Re-run every round-33 finding (M33-B1, D1–D6, S1, S2) and the round-32 findings. Mark each FIXED or NOT FIXED, with exact inputs. Re-run the historical replays against the map.
2. Attack the design. Look for:
   - any input drawn for a node of which it is not, as a whole, one read name under `_sig`;
   - a read name (a ChEMBL preferred name, a node label, a target symbol, a company or disease key) that denotes a different product from the node drawn;
   - a stored name the question linker refuses that the map still draws under some spelling;
   - Unicode problems, the `choose` and `alias_only` replies and their markup, retired nodes, and the id path.
3. Check the question-linker changes for regressions in the question boxes and the demos.
4. Briefly re-check guarantees A–G.

Report data problems separately from code problems. For each data problem give the exact input, the source record and an independent identity reference.

## Not blockers (recorded)

- Free-text leaks in the question boxes (README defect 15).
- The resolver's own brand lists in graph construction (README defect 15).
- Known over-refusals:
  - the list in `CODEX_MAP_M1_VERDICT.md`;
  - brands and development codes that are only synonyms, which the map does not draw;
  - two tracer drugs, refused by their own labels.

## Output

- Write scratch files only under `audit_evidence_claims/m34/`.
- Put the report in `audit_evidence_claims/m34/REPORT.md`.
- Do not edit tracked files.
- End with exactly one line: `VERDICT: APPROVE` or `VERDICT: CHANGES REQUIRED`.
