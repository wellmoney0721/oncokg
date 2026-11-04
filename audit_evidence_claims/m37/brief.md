# Round 37 of the relation-map review

Read the round-32 brief (`audit_evidence_claims/m32/brief.md`) for scope, guarantees and the approval bar, the round-34 brief for the name policy (`audit_evidence_claims/m34/brief.md`), and the round-36 report (`audit_evidence_claims/m36/REPORT.md`). Repairs: `CODEX_MAP_M1_VERDICT.md` section "Round 36". Review the latest commit on HEAD. Tests: `python -m pytest tests -q -p no:cacheprovider` (expect 365). Page: `python src/app.py <port>` (not 8765).

## What changed since round 36

- `src/app.py` `_sig` no longer interprets optical-rotation descriptors. After trademark signs, compatibility folding, case, marks (accents) and invisible characters are removed, a name that contains a bracketed group (any Unicode opening/closing or initial/final quotation punctuation) holding no letter or digit is compared character for character: only spaces are dropped and every dash (category Pd, U+2212) is read as "-". Every other name keeps the round-32 rule (spaces and punctuation dropped). Stored names go through the same function, so a descriptor name matches only its own spelling (spaces, case, accents, invisible characters and dash style aside).
- `src/query.py` `_named_alone`: any sign (+, -, minus, plus-minus) in the run of brackets, signs, dashes, slashes, underscores and spaces next to a shared-key name in a question blocks the preferred-name reading.

## What to do

1. Re-run M36-B1, B2, S1 and every round-32 to round-35 finding; FIXED / NOT FIXED with exact inputs. Re-run the historical replays and the expanded source universe.
2. Attack the design as in the round-34 brief, including the two comparison modes and which mode a name falls into.
3. Check the question-linker change for regressions in the question boxes and demos.
4. Re-check guarantees A–G briefly.

Report data problems separately from code problems. Recorded, not blockers: question-box free-text leaks and the resolver's own lists (README defect 15); the over-refusals in `CODEX_MAP_M1_VERDICT.md`, synonyms and brands the map does not draw, descriptor spellings other than the stored one, two tracer drugs and preferred names written like a refused spelling; THEOPHYLLINE's upstream drug type.

Write scratch files only under `audit_evidence_claims/m37/`, the report in `audit_evidence_claims/m37/REPORT.md`. Do not edit tracked files. End with exactly one line: `VERDICT: APPROVE` or `VERDICT: CHANGES REQUIRED`.
