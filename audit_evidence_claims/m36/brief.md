# Round 36 of the relation-map review

Read the round-32 brief (`audit_evidence_claims/m32/brief.md`) for scope, guarantees and the approval bar, the round-34 brief for the present name policy (`audit_evidence_claims/m34/brief.md`, as amended by round 35's brief), and the round-35 report (`audit_evidence_claims/m35/REPORT.md`). Repairs: `CODEX_MAP_M1_VERDICT.md` section "Round 35". Review the latest commit on HEAD. Tests: `python -m pytest tests -q -p no:cacheprovider` (expect 364). Page: `python src/app.py <port>` (not 8765).

## What changed since round 35

- M35-B1: `src/app.py` `_sig` now drops marks (accents) and invisible characters before reading optical-rotation descriptors. Any bracketed group with no letters or digits that contains a sign (plus, minus sign, any dash, plus-minus), in any order, becomes "+", "\u2212" or "\u00b1" (`_SIGN_GROUP`, `_sign`); then punctuation and spaces are dropped.
- M35-S1: `src/query.py` `_named_alone` decides whether a shared-key preferred name stands alone in a question: not glued to letters or signs, and after peeling brackets that wrap it, no sign group on either side.

## What to do

1. Re-run M35-B1 and S1 and every round-32 to round-34 finding; FIXED / NOT FIXED with exact inputs. Re-run the historical replays and the expanded source universe (every alias in `dictionary.drugs[*].aliases`, the index, labels, keys).
2. Attack the design as in the round-34 brief, including the composition of `_sig`'s steps (marks, invisible characters, descriptors, punctuation) with every stored name.
3. Check the question-linker change for regressions in the question boxes and demos.
4. Re-check guarantees A–G briefly.

Report data problems separately from code problems. Recorded, not blockers: question-box free-text leaks and the resolver's own lists (README defect 15); the over-refusals in `CODEX_MAP_M1_VERDICT.md`, synonyms and brands the map does not draw, two tracer drugs and preferred names written like a refused spelling; THEOPHYLLINE's upstream drug type.

Write scratch files only under `audit_evidence_claims/m36/`, the report in `audit_evidence_claims/m36/REPORT.md`. Do not edit tracked files. End with exactly one line: `VERDICT: APPROVE` or `VERDICT: CHANGES REQUIRED`.
