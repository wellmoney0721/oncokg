# Round 38 — confirmation after the round-37 approval

Round 37 approved the relation map at commit 2b1aca1 (`audit_evidence_claims/m37/REPORT.md`). Since then one commit on HEAD addresses its nonblocking items (`CODEX_MAP_M1_VERDICT.md`, section "Round 37"):

- `src/query.py` `_DESCRIPTOR_RUN`: the run beside a shared-key preferred name in a question is now every non-letter, non-digit character, so any sign in it blocks the reading (M37-S1).
- `web/try.html` section 0 and the `Engine.explore` docstring state that a name with a bracketed group holding no letter or digit is compared with its punctuation (M37-S3).
- M37-S2 is kept as a recorded recall tradeoff.

Scope and approval bar are unchanged: `audit_evidence_claims/m32/brief.md`, the name policy in `audit_evidence_claims/m34/brief.md`, and the round-37 amendment `audit_evidence_claims/m37/brief.md`.

Do:
1. Confirm M37-S1 and S3 with the exact inputs from the round-37 report, and that the M36 and earlier blocker reproductions stay fixed.
2. Check that the change introduced no regression: run `python -m pytest tests -q -p no:cacheprovider` (expect 366), the shipped demos, the shared-key question comparison, and the map's source sweep. `Engine.explore` code is unchanged apart from its docstring.
3. Anything new you find in scope: blocker or should-fix as before.

Write scratch files only under `audit_evidence_claims/m38/`, the report in `audit_evidence_claims/m38/REPORT.md`. Do not edit tracked files. End with exactly one line: `VERDICT: APPROVE` or `VERDICT: CHANGES REQUIRED`.
