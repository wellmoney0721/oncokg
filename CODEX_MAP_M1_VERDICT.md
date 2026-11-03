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

Round 2 (audit_evidence_claims/m2) stopped at Codex's usage limit before a report (log.txt ends with the limit error).
Its partial fixtures showed a SPONSORS edge without a role would be labelled collaborator; the page now says
"역할 기록 없음" for any role other than lead_sponsor/collaborator. Groups shown as "이름 순" were sorted Z to A; now A to Z
within equal weight. Round 2 to be re-run when the limit resets (2026-11-04 15:37).

## Round 2 re-run (audit_evidence_claims/m2b) — CHANGES REQUIRED

All m1 reproductions FIXED. New:

| # | Finding | Repair |
| --- | --- | --- |
| R1 | "osimertinib and generic version of bevacizumab": the refusal window swallowed osimertinib and left bevacizumab to link (map and QA switched subject) | a refused product span never crosses a comma or a joining word (and, or, plus, with, vs, …); separately named drugs survive in either order |
| R2 | malformed sponsor props displayed as "0건" | an unrecorded count is `evidence_trials: null`, shown as "기록 없음"; 0 is only a sort weight |
| should-fix | bool scores accepted and crashing render; rounded score; embedded multi-id alias alternatives dropped; "everything" docstring; silent 500-char cut | numbers exclude bool/NaN; score shown as stored; the hit's `also_matching_ids` disclosed; docstring; >500 chars is a 400 error; render errors shown |

Tests 323.

## Round 3 (audit_evidence_claims/m3) — CHANGES REQUIRED

| # | Finding | Repair |
| --- | --- | --- |
| M3-B1 | "with" as a joiner let "paclitaxel with albumin bound nanoparticles" draw PACLITAXEL (and QA answer with it) | refusal is now bound to the drug it qualifies: the shortest span holding that drug and no other drug, inside one list item; "with" is no longer a joiner |
| M3-B2 | "What is the generic version of bevacizumab?" drew BEVACIZUMAB (inherited) | same repair: the span must contain the drug, so the question prefix no longer absorbs the qualifier |
| should-fix | the single-token qualifier pass crossed commas ("osimertinib, liposomal doxorubicin" refused osimertinib) | neighbours are taken only within the same list item and never a joining word |
| found while fixing | words of a longer name were read again ("erlotinib hydrochloride" also listed ERLOTINIB) | a matched span is not re-linked |

Tests 325.
