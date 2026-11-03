# Claim check — Codex round 4, finding by finding (2026-11-03 KST)

Report: `audit_evidence_claims/r4/report.md`, `r4_report.md`. Verdict: CHANGES REQUIRED. All 438 earlier exact
reproductions were rejected; faithful corpora 29/30 and 29/30. Every new finding was reproduced here and was right.
Codex's probes were re-run from copies in `audit_evidence_claims/r4_recheck/`.

| # | Finding | Verdict | Repair |
| --- | --- | --- | --- |
| B1 | "The following safe drugs:" — the heading join deleted "safe" | right | the slot is a determiner plus a plain noun only (optionally "NSCLC"); adjectives stay in the sentence and are checked |
| B2 | plural members lost after a per-member check, in object "them", in an elided subject | right | the group survives per-member checks; "them" after a verb stands for every entity of that kind in the clause before; an elided subject after a group is checked once per member; "they"/"it" after "targeted by A and B" stands for A and B |
| B3 | "trials: 10" skipped the shared-count check | right | a count after a trial word counts too; a repeated alias is one drug |
| B4 | a phase or status shared by two trials checked against one | right | a value belongs to the run of trials joined by "and" just before it (or the first run after it), and each must have it |
| B5 | "EGFR is a drug inhibited by …", "PLB1003 … in clinical trials" borrowed support | right | a kind word belongs to the entity just before it; trial/NSCLC context comes from the clause subject's own statements |
| B6 | "N O T" spelled out | right | two or more single letters in a row are reported as unreadable |
| S1 | faithful forms rejected (shared phase, alias in a count, "They", ENSG citation, "Trials of X include …") | right | identity only across a verb; aliases de-duplicated; pronouns in the stop list; the global name check drops citations whose ids are evidence records; trial lists after "include" |
| S2 | docs incomplete; dashboard said two rounds | right | docstring states the new ownership rules; README lists four rounds and the new shapes; dashboard text updated |

Found while re-checking: "Osimertinib inhibits EGFR and is EGFR" (identity through an elided subject), percentages read as plain
counts, and "1 phase" matching the digit of PHASE_1. All fixed and tested.

Tests 240 (R1 33 + R2 39 + R3 22 + R4 21 attacks; 46 faithful forms). Inputs from Codex's R4 probes that still pass are
consistent with the evidence ("ALK is targeted by them" after naming both ALK drugs, "Osimertinib inhibits it and targets it",
coordinated phases that are both PHASE3).
