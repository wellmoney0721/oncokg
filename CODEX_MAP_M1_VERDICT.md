# Relation map — Codex review 1 (2026-11-03 KST)

Report: `audit_evidence_claims/m1/REPORT.md`. Verdict: CHANGES REQUIRED. Every finding reproduced before fixing.

| # | Finding | Repair |
| --- | --- | --- |
| B1 | "bevacizumab - awwb", "[89Zr] trastuzumab" drew the originator (linker joined tokens without the refusal checks) | `link_entities` refuses a multi-token window that names a distinct product or tracer, and none of its tokens link (fixes questions too) |
| B2 | a collaborator was labelled the trial's lead sponsor | SPONSORS groups keep `role`; headings say lead sponsor or collaborator |
| B3 | an investigator was labelled an institution | heading uses 연구자 for Investigator groups |
| B4 | a retired node could be explored by name | the centre must be live whatever path resolved it |
| count | drug trial counts included retired trials | counts join live Trial nodes |
| should-fix | ordering wording, ring cut silently, stale trail after errors, out-of-order replies, ambiguous names silent, action/class labels, omitted details, malformed props, `javascript:` URLs, "All three" | each group states its actual sort; ring says drawn/total; trail cleared on refusal/not-found/error; replies older than the latest request are dropped; the reading and other matches (company, target, refused span) are shown; stored action codes shown with a Korean gloss; sponsor class code shown; centre start date, drug count and phase always shown; props that are not objects read as empty; only clinicaltrials.gov links are clickable; docstring fixed |

Tests 321.
