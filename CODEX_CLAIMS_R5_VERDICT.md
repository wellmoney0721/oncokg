# Claim check — Codex round 5, finding by finding (2026-11-03 KST)

Report: `audit_evidence_claims/r5/report.md`, `r5_report.md`. Verdict: CHANGES REQUIRED. All 606 earlier exact
reproductions were rejected; old faithful corpora 29/30 and 29/30; fresh faithful corpus 28/40. Every new finding was
reproduced here and was right. Codex's probes were re-run from copies in `audit_evidence_claims/r5_recheck/`.

| # | Finding | Verdict | Repair |
| --- | --- | --- | --- |
| B1 | headings: the slot still removed plain nouns ("these drugs" over EGFR, "companies", "NSCLC drugs") | right | only the determiner is replaced; every noun and adjective stays and is checked |
| B2 | a named group borrowed its first member's clinical-trial context | right | trial/NSCLC context must hold for every member of the subject group before the verb |
| B3 | "It" after "ALK is targeted by A and B" resolved to ALK | right | an untyped "it" after a clause naming several entities of one kind stands for all of them, as "they" does; an elided subject after such a passive is checked against ALK's own words, not the drugs' bracketed facts |
| B4 | parentheticals broke shared phase/status ownership | right | a phase or status after the verb is about every trial before the verb |
| B5 | counts escaped through "trials in this graph: 10" and "10 such trials" | right | any earlier trial word with no entity between makes a figure a trial count; a company-only count after a sentence naming one drug is that pair's count (several drugs = count_ambiguous) |
| B6 | kind words bound to the wrong entity; "is a clinical trial" | right | "the drug X" belongs to X; "… is a drug" to the clause's subject; "is a (clinical) trial" requires a trial |
| S1 | 12 fresh faithful forms rejected | right | object "it" after "trials of"; "active but not recruiting"; counts scoped to their own drug; elided "6 of cisplatin" and "8 evaluating gefitinib"; noun relations with the subject listed after "include" or "by"; "as an inhibitor"; "Company: N trials of X" entries; record verbs ("records", "includes") as verbs, with the X-is-Y rule kept to forms of "be" |
| S2 | docs | right | docstring rules and README item 13 updated (five rounds); dashboard text updated |

Fresh R5 faithful corpus now 38/40; the two left are already documented (a negated comment about the evidence, and a refusal
naming France). Comma-separated spelled letters and "13 %" are also closed. Tests 275.
