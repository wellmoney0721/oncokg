# Structured answers — Codex review 3 (2026-11-03 KST)

Report: `audit_evidence_claims/s3/report.md`, `REPORT.md`. Verdict: CHANGES REQUIRED, no blocker: no unsupported output and
no model-text leakage; every s1/s2 reproduction FIXED.

| # | Finding | Repair |
| --- | --- | --- |
| S1 | an organisation alias the linker maps to several ids was accepted and documented as "merged ids count as one" (none in today's graph) | an alias that could mean several nodes is refused ("use the id"); docstring and READMEs say so |

Tests 316.

Round 4: VERDICT: APPROVE (audit_evidence_claims/s4/report.md). No blockers or should-fix items; faithful claims 73/73 by label and by id.
