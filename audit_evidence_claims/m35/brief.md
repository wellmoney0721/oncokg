# Round 35 of the relation-map review

Read the round-32 brief for the scope, guarantees and approval bar: `audit_evidence_claims/m32/brief.md`. Read the round-34 brief and report: `audit_evidence_claims/m34/brief.md` and `audit_evidence_claims/m34/REPORT.md`. The repairs are in `CODEX_MAP_M1_VERDICT.md`, section "Round 34".

Review the latest commit on HEAD. Run the tests with `python -m pytest tests -q -p no:cacheprovider`; expect 363 passing. Start the page with `python src/app.py <port>`, using any port other than 8765.

## What changed since round 34

- **M34-B1.** In `src/app.py` `Engine.__init__`, both name tables now take every stored spelling of a drug: each drug's preferred name and every entry in its alias list, plus the lookup index. The refusal check in `explore` therefore sees spellings the index dropped. One consequence: a preferred name with the same `_sig` as a refused spelling is refused too. `CABOZANTINIB S-MALATE` is refused because the resolver blocks `Cabozantinib (s)-malate`. This is recorded as an over-refusal.
- **M34-S2.** `_sig` keeps optical-rotation descriptors. `(+/-)` and `(±)` become `±`, `(-)` becomes `−` (U+2212), and `(+)` keeps its `+`.
- **M34-S1.** In `src/query.py`, the preferred-name rule for a shared key is blocked only by a closing bracket before the name or an opening bracket after it. Brackets around the name no longer block it.

## What to do

1. Re-run M34-B1, S1 and S2, and the round-33 and round-32 findings. Mark each FIXED or NOT FIXED, with exact inputs.
2. Re-run the historical replays against the map, including the expanded source universe: every alias in `dictionary.drugs[*].aliases`, the index, labels and keys.
3. Attack the design as in the round-34 brief.
4. Check the question-linker change for regressions.
5. Briefly re-check guarantees A to G.
6. Report data problems separately from code problems.

Not blockers, already recorded:
- Leaks in the question boxes' free text, and the resolver's own lists (README defect 15).
- The over-refusals listed in `CODEX_MAP_M1_VERDICT.md`.
- Synonyms and brands the map does not draw.
- Two tracer drugs, and preferred names whose letters equal a refused spelling.
- THEOPHYLLINE's upstream drug type.

Write scratch files only under `audit_evidence_claims/m35/`. Put the report in `audit_evidence_claims/m35/REPORT.md`. Do not edit tracked files. End with exactly one line: `VERDICT: APPROVE` or `VERDICT: CHANGES REQUIRED`.
