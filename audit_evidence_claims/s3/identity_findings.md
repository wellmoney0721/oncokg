# S3 identity, alias and edge review

Reviewed HEAD `6bcde7295e7b2292636119cd3e1b2a604324693d`. Persisted SQLite was query-only. Fixtures used isolated in-memory copies. No tracked file was edited.

## Replay inventory

Run `python -B audit_evidence_claims/s3/identity_replay_runner.py` with `PYTHONDONTWRITEBYTECODE=1` and `PYTHONUTF8=1`.

| Original probe | Current artifact | Cases | Result |
| --- | --- | ---: | --- |
| s1/identity_probe.py | replay_s1/identity_probe_results.json | 128 + 2 synthetic + 142 retired edges | Original input tuples exactly match; zero exceptions; all retired edges reject |
| s2/identity_probe.py | replay_s2/identity_probe_results.json | 128 + 2 synthetic + 142 retired edges | Original input tuples exactly match; zero exceptions; all retired edges reject |
| s2/identity_attack.py | replay_s2/identity_attack_results.json | 34 live-input cases + 10 fixtures | All original inputs and fixture descriptions exactly match |
| s2/root_contract_probe.py | replay_s2/root_contract_results.json | 1 duplicate-label fixture | Original input/SQL retained; old bug assertion recorded as false instead of aborting |

The replay runner changes only root/output paths and converts the old contract assertion to recorded data. `identity_replay_summary.json` holds input equality, counts, old/new observations and source hashes. The new `identity_attack.py` runs another **35** cases; exact outputs are in `identity_attack_results.json`.

## FIXED / NOT FIXED per prior identity finding

| Prior finding | Status | Current observation |
| --- | --- | --- |
| s1 B1 whole-name non-ASCII negation/extra text | **FIXED** | The exact subject `osimertinib가 아닌` now rejects; accepted `[]`, text `""`; same for Chinese additions, zero-width and emoji additions |
| s1 S1 canonical salt label | **FIXED** | Exact `ALECTINIB HYDROCHLORIDE` claim on `CHEMBL3707320|ACTS_ON|ENSG00000171094|CHEMBL3707320` accepts |
| s1 S2 list/dict kind or relation crashes | **FIXED** | All original bad types return rejection without exceptions |
| s1 S4 nesting and huge integer crash | **FIXED** | 5,000 nested arrays and 5,000-digit integer raw JSON return rejected results |
| s1 multi-ID exact-company fixture | **FIXED for that exact reproduction** | Exact graph label `AstraZeneca` resolves only to `ORG:astrazeneca` even when another ID is manually added to its alias map |
| s1/s2 retired Drug PROFILE NOTE | **NOT FIXED; remains NOTE** | Retire `CHEMBL3353410` in memory while retaining its resolved dictionary: `osimertinib` and `Tagrisso` still resolve to that ID and its PROFILE claim accepts; direct retired ID rejects |
| s2 duplicate same-type exact-label SHOULD FIX | **FIXED for exact label reproduction** | `OSIMERTINIB` resolves to no IDs; reason `"'OSIMERTINIB' is the label of 2 drug nodes; use the id"`; accepted `[]`, text `""` |
| s2 ambiguous nonexact organisation alias NOTE / name-contract issue | **NOT FIXED** | The original `azalias` fixture still resolves AstraZeneca and Genentech and accepts; the new constructor-only fixture below demonstrates the same issue without alias-map injection |
| s2 alias-shadowing NOTE (`met`) | **NOT FIXED; remains NOTE** | `met` rejects as Target rather than Drug; `METFORMIN` and `CHEMBL1431` accept |
| s2 Unicode case/long-label NOTES | **NOT FIXED; remain NOTES** | Synthetic exact `ÄRZT` accepts, `ärzt` rejects; 121-character label rejects; no current labels exceed 120 characters |

For the exact s1 whole-name reproduction, question `What does osimertinib target?`, input is:

```json
{"claims":[{"kind":"relation","relation":"ACTS_ON","subject":"osimertinib가 아닌","object":"EGFR","evidence":"CHEMBL3353410|ACTS_ON|ENSG00000146648|CHEMBL3353410","action":"INHIBITOR"}]}
```

Observed `verified=false`, `accepted=[]`, `text=""`, reason `"'osimertinib가 아닌' is not written the way the graph writes names (use the id or the name as it appears in the evidence)"`.

## BLOCKERS

No unsupported graph-rendered fact was demonstrated. This includes the organisation ambiguity below: the accepted edge continues to support the output fact. It is a false identity guarantee/documentation issue, not fabricated sponsorship prose.

## SHOULD FIX

### I1. Organisation alias candidates are still described as a single entity's merged IDs

The s2 repair enforces uniqueness only in the exact-label branch (`src/structured.py:117–126`). The alias branch returns all `also_matching_ids` (`src/structured.py:133–140`), and relation verification tests only membership (`src/structured.py:181`). The constructor explicitly indexes several distinct organisations under one name (`src/query.py:102–113`), while linking wraps the whole candidate set in one entity object (`src/query.py:179–187`). Nothing checks a same-entity merge before accepting the candidate set.

`src/structured.py:30–32` promises one entity and calls the exception that entity's "merged ids". `README.md:455–456` and `README.ko.md:318` still promise that the whole alias points to the single node. Those descriptions do not cover distinct organisations that merely share a name/key. The real rename aliases `BeiGene` and `BeOne` both resolve to the **single** current node `ORG:beonemedicines`; the multiple-ID path has different semantics.

**Minimal constructor-based reproduction, fixture only:**

1. Copy the current graph to `sqlite3.connect(':memory:')`.
2. Run `UPDATE node SET label='Astrazeneca' WHERE id='ORG:genentech'` in that copy.
3. Construct a new `OncoKG` using the copied connection (the script mocks only connection creation, not entity linking or the company index).
4. Production constructor now produces `companies['astrazeneca'] == ['ORG:astrazeneca','ORG:genentech']`. Genentech still has `raw_names=["Genentech, Inc."]`, parent `Roche`, and its existing graph edges; there has been no identity merge. `PRAGMA integrity_check` remains `ok`.

Question: `What is AstraZeneca running in NSCLC?`

Exact input:

```json
{"claims":[{"kind":"relation","relation":"SPONSORS_TRIAL_OF","subject":"AstraZeneca!","object":"osimertinib","evidence":"ORG:astrazeneca|SPONSORS_TRIAL_OF|CHEMBL3353410|","trial_count":14}]}
```

Observed resolver IDs: `["ORG:astrazeneca","ORG:genentech"]`; `verified=true`, one accepted claim, `rejected=[]`.

```text
- Astrazeneca is lead sponsor of 14 trial(s) evaluating OSIMERTINIB - a sponsorship, not evidence of developing the drug [ORG:astrazeneca|SPONSORS_TRIAL_OF|CHEMBL3353410|]
```

Removing only `!` makes the exact-label repair refuse: `"'AstraZeneca' is the label of 2 company nodes; use the id"`. `astra-zeneca` and `ASTRAZENECA?` also take the multi-ID alias path and accept.

The same question retrieves the distinct Genentech candidate's edges. Exact second input:

```json
{"claims":[{"kind":"relation","relation":"SPONSORS_TRIAL_OF","subject":"AstraZeneca!","object":"CHEMBL1201583","evidence":"ORG:genentech|SPONSORS_TRIAL_OF|CHEMBL1201583|","trial_count":5}]}
```

Observed `verified=true` and:

```text
- Astrazeneca is lead sponsor of 5 trial(s) evaluating BEVACIZUMAB - a sponsorship, not evidence of developing the drug [ORG:genentech|SPONSORS_TRIAL_OF|CHEMBL1201583|]
```

Both output lines are supported by their cited graph edges and current fixture labels. The problem is the unconditional single-entity/merged-ID guarantee. Current persisted graph has **zero** multi-ID company keys and **zero** duplicate live labels of the same type; this is a valid synthetic boundary test, not a claim of current graph contamination. To meet the documentation bar, either reject multiple candidate IDs unless equivalence is established, or describe evidence-based candidate selection accurately in all three documents.

## NOTES

- Exact duplicate Drug labels now reject across ASCII case and surrounding whitespace. A direct valid ID accepts. Retiring only the duplicate restores singleton-label acceptance. A punctuation alias for the unique drug dictionary entry can still accept, but it resolves to one ID and is consistent with the declared alias alternative.
- On the persisted graph, `MedImmune`, `Genentech`, and `Roche` cannot stand for `ORG:astrazeneca` on the AZ sponsorship edge; all reject. This protects the current parent/subsidiary cases.
- Current graph code-value dictionaries still contain no `_norm` collisions. All 142 retired edges reject, including with explicit stale retrieval allowlists. Foreign-question edges, PROFILE-as-relation, wrong relation/action/count, salt-to-parent substitutions and mixed phase types continue to reject.
- For the previously reported retired PROFILE note, exact input after in-memory node retirement is `{"claims":[{"kind":"drug","drug":"osimertinib","evidence":"profile:CHEMBL3353410","max_stage":"APPROVAL"}]}` for `What is osimertinib?`. It accepts the retained graph property `APPROVAL`; name aliases do not recheck retirement (`src/structured.py:133–140`), and `_drug` fetches the node without a retirement filter (`src/structured.py:236`). No retired Drug exists in the current persisted graph.
- Replays preserve legacy duplicate-key semantics: the final JSON value is checked; an earlier overwritten value does not appear in output. Fifty-one claims retain 50 valid facts plus an excess-count rejection. These remain evidence-consistent NOTES.

Identity-scope conclusion: shared-label exact rejection is repaired; the organisation alias documentation guarantee remains inaccurate. Recommend CHANGES REQUIRED on the stated docs approval bar, with no new unsupported rendered fact demonstrated.
