# Structured answers — Codex review 2 (2026-11-03 KST)

Report: `audit_evidence_claims/s2/report.md`, `REPORT.md`. Verdict: CHANGES REQUIRED, no blocker: no unsupported
rendered fact and no answer-text or HTML leakage found; all s1 findings FIXED; faithful claims 73/73 by label and by id.

| # | Finding | Repair |
| --- | --- | --- |
| S1 | the docstring promised one node per name, but a label shared by two nodes would resolve to both (none in today's graph) | a label shared by two nodes of the wanted type is refused ("use the id"); docstring and READMEs state the exact name rule |
| S2 | `1e309` and NaN/Infinity reached rejected diagnostics and broke strict JSON | non-finite floats refused at parse; rejected claims echoed through a sanitiser |
| note | README said nothing the model typed "reaches the reader" while diagnostics show rejected claims | now "reaches the answer"; rejected claims are diagnostics |
| note | a missing SDK looked like an empty model answer; an SDK outage raised | both reported as "the language model could not be used", applicable=false |

Tests 315.
