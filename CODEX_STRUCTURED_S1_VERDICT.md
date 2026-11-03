# Structured answers — Codex review 1, finding by finding (2026-11-03 KST)

Report: `audit_evidence_claims/s1/report.md`, `REPORT.md`. Verdict: CHANGES REQUIRED (one blocker). All findings reproduced and right.
Probes re-run from copies in `audit_evidence_claims/s1_recheck/`.

| # | Finding | Repair |
| --- | --- | --- |
| B1 | "osimertinib가 아닌" accepted as osimertinib: the whole-name comparison dropped non-ASCII letters | names are an id, an exact graph label (any script), or plain printable ASCII; the linker drops characters it cannot read, so other names are refused. Also closes "osimertinib是安全的", "非osimertinib", emoji and zero-width-space variants found in the review's probes |
| S1 | labels copied from the evidence ("ALECTINIB HYDROCHLORIDE", long sponsor names) rejected | exact label lookup (case-insensitive, live nodes) before alias linking |
| S2 | list/dict `kind` or `relation` raised TypeError | type checks, and any exception while checking one claim rejects that claim |
| S3 | NaN accepted by the parser, then the page got invalid JSON | NaN/Infinity refused at parse; the API serialises with allow_nan=False |
| S4 | empty SDK content (IndexError), deep nesting (RecursionError) | first text block or empty; RecursionError caught as invalid JSON |
| note | `{"claims": []}` reported as one removed claim | an empty list means "the evidence does not answer", reported as such |
| note | PROFILE records described as live edges | docstring and README say a drug claim may cite the drug's profile record |
| note | obsolete prose-check text in query.py docstring and dashboard 06; English/Korean 22/38 wording | rewritten |

Tests 312.
