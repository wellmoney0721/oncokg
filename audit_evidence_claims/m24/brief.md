# Round 24 of the relation-map review. Previous: audit_evidence_claims/m1 to m23 REPORT.md. Repairs: CODEX_MAP_M1_VERDICT.md (all rounds), latest commit on HEAD. Tests: 351.
This round: symbol-first isotope at any position in a word (DOTACe134); conjugat-/covalently/linked to/with refuse a drug unless the joining word is in the matched name or the drug name carries a payload; negation covers bare radio + next word and a label after its adverb.
Known, recorded over-refusals (not blockers): M5-S2; 40-o-/42-o-(2-hydroxyethyl)rapamycin; Trastuzumab--vcmmae conjugate; 9-amino-20(s)-camptothecin; il-6ra; TAK-659F; GS-11CAL-101; 3en3hg4wsw; same-list-item over-refusal. Known data limitations (recorded, awaiting the owner's curation decision): ChEMBL lists bevacizumab biosimilar development codes as bevacizumab synonyms; an AACT synonym maps 13-cis-retinoic acid/isotretinoin to CHEMBL38 TRETINOIN (M23-D1).
1. Re-run every earlier reproduction (m1 to m23); FIXED / NOT FIXED per finding. Reuse earlier scripts.
2. Attack for originator leaks where every stage misses a refusal, demo regressions, and cost.
Same approval bar as below. Write scratch files only under audit_evidence_claims/m24/, report in audit_evidence_claims/m24/REPORT.md. Do not edit tracked files.
End with exactly one line: VERDICT: APPROVE or VERDICT: CHANGES REQUIRED.

--- original brief ---
# Codex verification brief — relation map on the try-it page (commit bfcb83d)

You are an independent reviewer. Do NOT edit any tracked file. Write scratch files only under
`audit_evidence_claims/m1/`. Put your report in `audit_evidence_claims/m1/REPORT.md`.
End with exactly one line: `VERDICT: APPROVE` or `VERDICT: CHANGES REQUIRED`.

## What was added

`src/app.py` `Engine.explore(text, per_group=30)` and `POST /api/explore`; `web/try.html` section "0. 관계 지도"
(`drawMap`, `explore`, `itemDetail`, the GKO/TKO/ACT/PH tables, click-through and the "따라온 길" trail);
`tests/test_app.py::test_explore_draws_a_drug_and_refuses_a_biosimilar`. Run tests with
`python -m pytest tests -q -p no:cacheprovider` (317). Start the page with `python src/app.py [port]` (use a port
other than 8765, which may already be in use) and exercise it over HTTP.

The page is for a domain reviewer to look at one node (drug, target, company, investigator, trial, disease) and
everything a live edge ties it to, grouped by relation, and to click through. It is read-only.

## The guarantees claimed (page text in section 0 and the `explore` docstring)

1. Every neighbour shown is joined to the centre by a live (not retired) edge to a live node, and the group label
   states the relation and its direction correctly (e.g. "이 약의 임상을 주관한 곳 (주관 ≠ 개발)" for
   Company -SPONSORS_TRIAL_OF-> Drug seen from the drug).
2. Details shown for a neighbour are the stored values: trial phases/status/start/title/url, sponsor trial count
   (`evidence_trials`) and sponsor class, drug trial count in the graph (EVALUATES), max phase, action type.
3. A name the question linker refuses (biosimilar, distinct product, tracer) is reported as refused, never drawn
   as the originator molecule; an unknown name says "not found".
4. Groups are ordered by size and each list keeps the `per_group` neighbours with most evidence; the page says
   when a list is cut and shows the true total.
5. Nothing is written; no model is called.

## What to verify (reproduce; cite file:line and exact inputs)

A. **Wrong relations or directions.** Any centre where an edge is grouped under the wrong label or direction,
   self-loops (src == dst), edges with both ends equal to the centre, PARENT_OF/SPONSORS/STUDIES/ASSOCIATED_WITH
   direction wording, Investigator vs Company handling, nodes whose type the tables do not cover.
B. **Name resolution.** `explore` takes the first non-refused hit of `link_entities`. Inputs with several entities
   ("osimertinib EGFR"), a refused token next to a real one ("Mvasi bevacizumab"), salts vs parents, company aliases
   with `also_matching_ids` (only the first id is drawn — is that misleading?), node ids vs names that collide,
   case/whitespace/Unicode, long inputs. Is anything drawn that the input does not name, or a refused product drawn
   as the originator?
C. **Wrong values.** Trial counts, sponsor counts, max phase and action shown versus the database
   (`data/processed/oncokg.sqlite`); retired edges/nodes leaking in; counts computed over retired edges;
   the `trials` count chunking; JSON props that are null or malformed.
D. **Cutting and ordering.** Is the "most evidence" ordering what the page says (trials are ordered by start date
   string — is that what the text implies)? Does the map's subset (`drawMap` allocation) ever hide a whole group
   or misstate totals? The Disease node (thousands of neighbours) — performance and output size.
E. **Page safety and correctness.** HTML/SVG injection from labels, titles, ids, URLs (`href` with `javascript:`?),
   edge ids in `data-id` attributes, the trail/back buttons after errors, double clicks, refused/not-found states,
   dark mode legibility is not in scope.
F. **Server.** Error handling for empty/oversized input, concurrency with the lock, behaviour when the DB has
   retired rows.
G. **Docs and wording.** Section 0 text, README/README.ko lines for `app.py`, the module docstring: do they claim
   more than the code does? Korean labels in GKO/ACT/PH that misstate the stored code.

## Approval bar

No known way for the map to show a relation that is not a live edge, a wrong direction or relation wording, a
value that differs from the stored one, a refused product drawn as the originator, or script injection. Report
should-fix items (misleading wording, cut lists without notice) separately from blockers.
