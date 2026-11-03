# Round 2. Your round-1 report is audit_evidence_claims/r1_report.md (VERDICT: CHANGES REQUIRED).
The checker was rewritten (commit a12762b, src/claims.py) as clause-level subject-relation-object
reading; the repair-by-finding table is CODEX_CLAIMS_R1_VERDICT.md. Your round-1 probes are in
audit_evidence_claims/independent_*.py; their attacks are now regression tests in tests/test_claims.py.

Do the same job as the brief below, with two additions:
1. Re-run every round-1 reproduction and state, per finding, FIXED or NOT FIXED.
2. Attack the new design itself: clause splitting, pronoun/elided-subject resolution, the
   "nearest entity owns the value" rule, the verbatim-statement pass, list-heading joining,
   noun-form relations ("target of", "inhibitor"), passive detection, the META refusal pass, the
   linker punctuation change, and the alias acceptance added to the old name check.
Write scratch files only under audit_evidence_claims/r2/. Do not edit tracked files.
End with exactly one line: VERDICT: APPROVE or VERDICT: CHANGES REQUIRED.

--- original brief ---
# Codex verification brief — sentence-level claim check (commit 0c441e0)

You are an independent reviewer. Do NOT edit any tracked file. You may write scratch
files only under `audit_evidence_claims/`. End with a verdict line, exactly one of:

    VERDICT: APPROVE
    VERDICT: CHANGES REQUIRED

## What changed

`OncoKG.check_groundedness` (src/query.py) checks a *generated* answer against the
evidence retrieved for the question. Before this commit it only checked that names and
numbers appeared somewhere in the evidence, so "AstraZeneca has discontinued
osimertinib", "osimertinib does not act on EGFR" and "osimertinib is safe" passed.

Now, given `linker=self.link_entities`, it also calls `claims.check_claims`
(src/claims.py), which reads the answer sentence by sentence:

1. A stated relation (acts on / evaluates / sponsors) must hold between the same
   entities in an evidence statement of that relation.
2. Negations, comparisons, hedges and "develops/owns/markets" are reported unless the
   sentence is quoting an evidence statement about the same entities.
3. "phase N" and "N trials" must be stated for that sentence's own entities (a named
   trial is the most specific subject).
4. Every other content word must be grammar (FUNCTION list) or appear in an evidence
   statement about the sentence's entities.

Also: `link_entities` no longer joins several short words into a one-word drug
abbreviation ("is a" was read as "isa" = isatuximab).

The goal set by the owner: ordinary-word claims ("safe", "discontinued") and relations
must be caught. The design is deliberately strict: a true fact the graph does not hold
is reported as unverifiable, and a human reviewer decides.

## What to verify (reproduce everything; cite file:line and exact inputs)

A. **False negatives (most important).** Find answers containing a claim the retrieved
   evidence does not support that still return `grounded=True`. Use the real graph:
   `python src/app.py` exposes `Engine().check(question, answer)`; or call
   `OncoKG().check_groundedness(answer, evidence, entities, True, vocab, linker=kg.link_entities)`.
   Try at least: reversed relations, wrong drug–target / company–drug / trial–drug
   pairing in multi-entity sentences, pronouns ("it", "this drug"), relations stated
   with nouns ("an EGFR inhibitor", "AstraZeneca's osimertinib"), status/phase of the
   wrong trial, counts, negation spelled differently ("isn't", "no longer",
   "un-", "non-"), clinical claims made only of words that happen to be in evidence
   statements, claims split across sentences, lists, Korean or mixed text, markdown.
B. **False positives.** Faithful answers an LLM would plausibly write from the evidence
   (paraphrases, "is an inhibitor of", "is being tested in", lists) that are flagged.
   Strict is intended, but a check that flags most faithful answers is not useful —
   say how often it happens on realistic paraphrases of each demo question in
   `src/query.py:main`.
C. **Correctness of the code**: regexes, sentence splitting, the subject-inheritance
   rule for fragments of one line, `quoted()` bigram rule (can it be abused to launder a
   negation?), dedup in `check_groundedness` (one finding per value — can it hide a
   finding?), the `link_entities` change (does it break any multi-word drug name the
   pipeline should still link? check against the dictionary).
D. **Regressions**: `python -m pytest tests -q -p no:cacheprovider` (79 expected), and
   that the template answers for the demo questions, read as prose, still pass.
E. **Documentation honesty**: README.md / README.ko.md item 13, the docstrings in
   claims.py and query.py, web/template.html section 06, web/try.html box 3 — do they
   claim more than the code does?

## Report format

`BLOCKERS` (claims that pass and should not, or wrong code), `SHOULD FIX`, `NOTES`,
each with a reproducible input and the observed output. Then the verdict line.
