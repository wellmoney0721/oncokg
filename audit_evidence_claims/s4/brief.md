# Round 4 of the structured-answer review. Previous: audit_evidence_claims/s1, s2, s3 REPORT.md (CHANGES REQUIRED; no
blockers in s2 or s3). Repair: CODEX_STRUCTURED_S3_VERDICT.md, latest commit on HEAD. Tests: 316.
1. Re-run every s1-s3 reproduction; FIXED / NOT FIXED per finding.
2. Check the s3 repair (an alias naming several nodes is refused) and that docs and code now agree.
Same approval bar as below. Write scratch files only under audit_evidence_claims/s4/. Do not edit tracked files.
End with exactly one line: VERDICT: APPROVE or VERDICT: CHANGES REQUIRED.

--- original brief ---
# Codex verification brief — structured answers (commit aa5655a)

You are an independent reviewer. Do NOT edit any tracked file. Write scratch files only under
`audit_evidence_claims/s1/`. End with exactly one line: `VERDICT: APPROVE` or `VERDICT: CHANGES REQUIRED`.

## Context

Six rounds of review of a free-prose claim checker (`src/claims.py`; reports in `audit_evidence_claims/`)
never converged, so the design changed. With a language model, the model no longer writes the answer: it
returns `{"claims": [...]}` where each claim is a fixed-kind JSON object citing an evidence edge id.
`src/structured.py` (`Verifier`, `render`) checks each claim exactly against the SQLite graph and the
program writes the answer from accepted claims only, using graph labels and values. `src/query.py`
(`answer` with `use_llm=True`, `_llm_claims`, `verify_structured`) wires it in; `src/app.py`
(`/api/structured`) and `web/try.html` box 3 expose it. `claims.py` stays as an auxiliary screen (box 4)
and is documented as fallible (README known defect 13) — it is not under review here.
Tests: `python -m pytest tests -q -p no:cacheprovider` (300); `tests/test_structured.py` covers this.

## The guarantee claimed (module docstring, README "Asking it things", dashboard section 06)

An accepted claim is supported by the graph: correct kind and exact keys (no free-text field; unknown keys
reject), cited edge among those retrieved for the question and live, relation and both endpoints equal to
the named entities (names must resolve, whole, to exactly those node ids), and every value equal to what the
graph stores (action type, sponsor trial count, trial phase set and status, drug max stage, trials in graph).
The rendered answer contains nothing typed by the model. It does NOT claim the chosen claims answer the
question well or completely.

## What to verify (reproduce everything; cite file:line and exact inputs)

A. **False acceptance.** Any claim the graph does not support that is accepted, on the demo questions in
   `src/query.py:main` or any other question. Try: name resolution (aliases, salts vs parents, ambiguous
   names, companies with several ids via `also_matching_ids`, parent/subsidiary, case/whitespace/Unicode,
   very long names, names that link partially), id vs name mixing, evidence ids from a different question,
   PROFILE pseudo-edges, retired edges, relation/edge mismatches, value normalization in `_norm`
   (can two different stored codes normalize to the same string? e.g. phase sets, statuses, stages,
   action types like "ANTISENSE INHIBITOR" vs "INHIBITOR"), type confusion (bool/int/float/str/None/lists of
   mixed types, duplicate JSON keys, NaN/Infinity), nested or oversized payloads, more than 50 claims.
B. **Text leakage.** Any way for model-typed text to reach the rendered answer or the user-facing page
   (render uses labels from the DB; check every field and the page's display of rejected claims for HTML
   injection in `web/try.html`).
C. **Rendering faithfulness.** Does each rendered line say exactly what the accepted facts say (e.g. the
   sponsorship line, phase lists, empty phases, action wording)?
D. **The model path.** `query.answer(use_llm=True)` and `_llm_claims`: prompt, JSON extraction from the
   reply (`re.search(r"\{.*\}", raw, re.S)`), behaviour on malformed or empty replies, the checks dict.
E. **Usefulness.** Can faithful claims an LLM would produce from the evidence shown be expressed and
   accepted for each demo question (relations, trials' phase/status, sponsor counts, drug stage/count)?
   Note claim types the schema cannot express.
F. **Docs.** README "Asking it things" and item 13, README.ko, `structured.py` docstring, dashboard
   section 06 (`web/template.html`), try page box 3/4 text: do they claim more than the code does?

## Approval bar

No known way to get a claim the graph does not support accepted, or model-typed text into the answer;
faithful claims for the demo questions can be expressed and are accepted; docs do not overclaim.
Findings that are evidence-consistent or purely about completeness are NOTES.

Report: BLOCKERS, SHOULD FIX, NOTES, each with exact input and observed output. Then the verdict line.
