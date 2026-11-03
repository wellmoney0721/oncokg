# S2 identity and exact-label review

HEAD `60b9c61`; comparison `git diff aa5655a...HEAD`. No tracked files changed. Persisted SQLite connection was query-only; all mutations below used isolated in-memory copies.

## S1 reproduction status

All **128** original `identity_probe.py` cases reran unchanged from its s2 copy: **zero exceptions**. All **142** retired edges still reject. Full inputs/outputs: `identity_probe_results.json`; changed outcomes: `identity_s1_comparison.json`.

- **FIXED:** Korean/Chinese/emoji/zero-width suffix identity bypasses (six accepted-to-rejected changes); canonical ALECTINIB HYDROCHLORIDE now accepts; list/dict kind/relation types, 5,000-deep JSON, and 5,000-digit integer reject without raising.
- **FIXED, original fixture only:** Injecting a second company ID into `companies['astrazeneca']` now resolves the exact label to AstraZeneca alone.
- **NOT FIXED, previous NOTE:** Retiring osimertinib only in the in-memory graph while retaining the dictionary still permits its PROFILE claim through alias linking (`structured.py:106-113,201-217`). Current graph has no retired Drug node.

## BLOCKERS

None demonstrated on the persisted graph.

## SHOULD FIX

None promoted from a previously documented evidence-consistent NOTE.

## NOTES

**Duplicate-label uniqueness is not enforced.** Fixture: `UPDATE node SET label='OSIMERTINIB' WHERE id='CHEMBL3707320'`. Exact input:

```json
{"claims":[{"kind":"relation","relation":"ACTS_ON","subject":"OSIMERTINIB","object":"EGFR","evidence":"CHEMBL3353410|ACTS_ON|ENSG00000146648|CHEMBL3353410","action":"INHIBITOR"}]}
```

`resolve` returns both Drug IDs; output is `verified=true`, one supported osimertinib–EGFR fact. `structured.py:96-99,154` accepts membership rather than uniqueness, inconsistent with literal `:30`. A nonexact company alias with two IDs has the same result (`:113`). This extends the earlier synthetic ambiguity NOTE, not a new persisted unsupported fact. SQL found **zero** duplicate live labels and **zero** ID/label collisions. Cross-type identical labels resolve by expected type.

**Alias shadowing remains fail-closed.** For `What does metformin target?`, input `{"claims":[{"kind":"relation","relation":"ACTS_ON","subject":"met","object":"ENSG00000198695","evidence":"CHEMBL1431|ACTS_ON|ENSG00000198695|CHEMBL1431"}]}` rejects: `met is a target, not a drug`. Replacing only subject with `METFORMIN` or `CHEMBL1431` accepts. Exact-label precedence (`:93-100`) narrows alias usefulness.

**Boundary results:** All 47 current non-ASCII labels resolve exactly; no current label exceeds 120 characters. Synthetic Korean label accepts; appended negation rejects. SQLite `lower()` does not Unicode-casefold: fixture `ÄRZT` accepts itself but rejects `ärzt`. Whitespace trimming and ASCII punctuation normalization preserve supported facts.

Additional reproductions and exact outputs: `identity_attack.py`, `identity_attack_results.json`.

Identity-scope recommendation: APPROVE with NOTES.

## Final adjudication

The preceding scope-only recommendation addressed supported rendered facts and is superseded for the overall approval decision. Root independently confirmed the duplicate-label fixture. A second same-type node sharing a label is valid graph data, and `resolve` returns two IDs; therefore `src/structured.py:30` overclaims when it requires a name to resolve to exactly that node ID. Absence of duplicate labels in the current snapshot limits current exposure but does not prove this unconditional contract.

The runtime observation remains a NOTE: the cited edge still supports the rendered fact. The inaccurate guarantee is a documentation SHOULD FIX (root report SF1) and fails the explicit approval bar that documentation must not overclaim. Either singleton enforcement or documentation accurately describing evidence-based disambiguation would address that discrepancy.

Overall final recommendation: CHANGES REQUIRED on the documentation bar; no unsupported rendered fact was demonstrated.
