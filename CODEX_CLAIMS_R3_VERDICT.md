# Claim check — Codex round 3, finding by finding (2026-11-03 KST)

Report: `audit_evidence_claims/r3/report.md`, `r3_report.md`. Verdict: CHANGES REQUIRED. All exact R1/R2
reproductions were already rejected (246 replayed cases). Every new finding was reproduced here and was right.
To keep Codex's outputs intact this time, its probes were re-run from copies in `audit_evidence_claims/r3_recheck/`.

| # | Finding | Verdict | Repair |
| --- | --- | --- | --- |
| B1 | "they" shrank to the first drug | right | the subject is a group; a plural pronoun is checked once per member. An untyped pronoun right after a relation verb is that relation's object ("inhibits it") |
| B2 | one trial count shared by two drugs | right | `count_ambiguous`: in a clause naming several drugs, each needs its own "N trials of/evaluating <drug>"; a company carried over from the previous clause scopes the count |
| B3 | headings over copied lines checked leniently | right | no lenient mode: the heading is checked in full with the line's subject; only the joining dash is exempt from the fragment rule, and only when the heading names no entity of its own. Template headings now name the list without stating a relation |
| B4 | "clinical trials", "drug", "NSCLC drug", "X is Y" passed as grammar | right | kind words need an entity of that kind or evidence of trials (a zero count is no trials); NSCLC only before trials the evidence calls NSCLC trials, never with approval; two different entities joined by a verb that is no relation = `identity` |
| weaker | "PLB1003 has NSCLC trials: 1", "approved in NSCLC", id-shaped `[ORG:is-safe]` | right | count read from "trials: N" too; approval + disease = `indication`; a bracket is dropped as a citation only when every id is a record of the evidence |
| S1 | faithful forms rejected (object pronoun, phase after evaluates, roman phase, repeated evaluating clauses, repeated aliases) | right | trial phase/status belong to the nearest trial; roman numerals consumed; carried-over company scopes counts; aliases and name digits linked repeatedly |
| S2 | docstring/README did not list known passes | right | docstring states rules as a description, not a guarantee; README item 13 lists what is known to pass and to be over-strict |

Found while re-checking: a crash (`dict | set`) in the object-pronoun rule that no test reached, and figures like "2," read with
the comma. Both fixed; the crash input is a test.

Tests 213 (R1 33 + R2 39 + R3 22 attacks, all `grounded=False`; 40 faithful forms, all pass). Of Codex's R3 attack list, the inputs
still passing are evidence-consistent ("Osimertinib was inhibiting EGFR", "EGFR has been inhibited by osimertinib",
"Osimertinib is an EGFR blocker", "evaluated at NCT03909334") or harmless (a copied line ending in "?").
