# S4 identity/spec review

Reviewed `8adf2dd` against baseline `aa5655a`. All persisted SQLite connections were query-only; every fixture mutated a separate in-memory copy. Writes were confined to this directory. No tracked file was changed by this reviewer.

## Spec summary

No BLOCKER or SHOULD FIX found in the identity scope. The s3 alias repair now rejects every reproduced multi-node alias, including the production-constructor fixture rather than only the new mocked-linker unit test. `src/structured.py:140-145` checks the complete distinct-ID set, so two or three candidate organisations produce no accepted facts. Canonical IDs remain usable; both original organisations' IDs accept on their respective edges. Real same-entity rename aliases `BeiGene` and `BeOne` both resolve to the single `ORG:beonemedicines` node and accept its own sponsorship fact. Exact-label precedence remains intentional: a unique exact label is accepted before alias lookup, whereas a nonexact spelling exposing several alias candidates is refused. This matches the three alternatives in the module contract (`src/structured.py:29-32`).

The original non-ASCII whole-name bypass, salt-label false rejection, malformed type crashes, deep/huge JSON crashes, duplicate-label ambiguity, and multi-ID company alias ambiguity all return the repaired results. Previously evidence-consistent limitations remain NOTES: cached Drug aliases can resolve an in-memory retired node's retained PROFILE properties; `met` is a Target label and therefore cannot name METFORMIN; exact Unicode case variants and labels over 120 characters may reject. These do not demonstrate unsupported output on the persisted graph. That graph has zero multi-ID company keys or duplicate same-type live labels, and all 142 retired edges reject even if explicitly included in stale retrieved evidence.

## Replay inventory

Reproduce:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
$env:PYTHONIOENCODING='utf-8'
python -B audit_evidence_claims/s4/identity/replay.py
python -B audit_evidence_claims/s4/identity/boundary_probe.py
```

| Original script | Replayed artifact | Input coverage | Result |
| --- | --- | --- | --- |
| `s1/identity_probe.py` | `replay_s1/identity_probe_results.json` | 128 original cases, 2 fixtures, 142 retired edges | Inputs unchanged; zero exceptions; all retired edges rejected |
| `s2/identity_probe.py` | `replay_s2/identity_probe_results.json` | 128 original cases, 2 fixtures, 142 retired edges | Inputs unchanged; zero exceptions; all retired edges rejected |
| `s2/identity_attack.py` | `replay_s2/identity_attack_results.json` | 34 live cases, 10 fixtures | Inputs unchanged; zero exceptions |
| `s2/root_contract_probe.py` | `replay_s2/root_contract_results.json` | Original duplicate-label SQL and payload | Refused; old bug assertion recorded as false |
| `s3/identity_attack.py` | `replay_s3/identity_attack_results.json` | 35 original cases | Inputs unchanged; zero exceptions |
| Independent S4 boundary controls | `boundary_results.json` | 15 cases | All 15 expectations met |

`replay_manifest.json` records original source hashes, copied output paths, exact-input equality, exits, and changed outputs. The only replay modifications are path relocation and recording the obsolete root-contract bug assertion as data. Full question/payload/retrieved IDs/results are preserved in the JSON artifacts.

## FIXED / NOT FIXED per historical identity finding

| Finding | Status on S4 | Evidence / observation |
| --- | --- | --- |
| s1 B1: `osimertinib가 아닌` and Chinese/emoji/zero-width additions bypass whole-name resolution | **FIXED** | `replay_s1/identity_probe_results.json`, `name:*`: `accepted=[]`, empty answer; non-ASCII alias guard at `src/structured.py:128-132` |
| s1 S1: `ALECTINIB HYDROCHLORIDE` copied from ALK evidence rejects | **FIXED** | `alk_salt_canonical_name` accepts its exact salt edge; exact-label lookup at `src/structured.py:117-126` |
| s1 S2: list/dictionary `kind` or `relation` throws | **FIXED** | Original type cases return rejected results; guards at `src/structured.py:153-154,175-177`, catch at `:284-287` |
| s1 S4: 5,000 nested arrays / 5,000-digit integer throws | **FIXED** | Both raw inputs return `not valid JSON: nested too deeply`; catch at `src/structured.py:264-273` |
| s1 exact-company multi-ID fixture | **FIXED for exact reproduction** | `AstraZeneca` uses its unique exact graph label and resolves `ORG:astrazeneca` alone |
| s2 duplicate same-type label contract failure | **FIXED** | Original fixture returns no IDs and `OSIMERTINIB is the label of 2 drug nodes; use the id`; check at `src/structured.py:122-124` |
| s2 `azalias` mapping to two organisations | **FIXED** | Original fixture returns no IDs and `'azalias' names 2 company nodes; use the id`; no accepted facts |
| s3 constructor-built ambiguous alias / misleading merged-ID contract | **FIXED** | All three punctuation aliases and the other-org edge reject; `src/structured.py:140-145` agrees with `:29-32`, `README.md:455-457`, `README.ko.md:318` |
| s1/s2/s3 retired PROFILE cached-alias NOTE | **NOT FIXED; NOTE** | In-memory retirement preserves alias lookup and stored `APPROVAL`; `osimertinib` and `Tagrisso` accept PROFILE, direct retired ID rejects; current graph has no retired Drug node |
| s2/s3 `met` alias-shadowing NOTE | **NOT FIXED; NOTE** | `met is a target, not a drug`; METFORMIN / CHEMBL1431 controls accept |
| s2/s3 Unicode-case and long-label NOTES | **NOT FIXED; NOTES** | Exact `ÄRZT` accepts, `ärzt` rejects; 121-character exact label rejects; 47 current non-ASCII labels resolve exactly and no current label exceeds 120 |

## Exact repaired S3 input and output

Create an isolated copy with `sqlite3.connect(':memory:')`, copy the current graph, run `UPDATE node SET label='Astrazeneca' WHERE id='ORG:genentech'`, then construct a fresh `OncoKG` using that connection. All company indexing/linking is production code; only connection creation is mocked. The resulting company key contains `['ORG:astrazeneca', 'ORG:genentech']`; integrity check is `ok`.

Question: `What is AstraZeneca running in NSCLC?`

```json
{"claims":[{"kind":"relation","relation":"SPONSORS_TRIAL_OF","subject":"AstraZeneca!","object":"osimertinib","evidence":"ORG:astrazeneca|SPONSORS_TRIAL_OF|CHEMBL3353410|","trial_count":14}]}
```

Observed:

```json
{"verified":false,"accepted":[],"rejected":[{"claim":{"kind":"relation","relation":"SPONSORS_TRIAL_OF","subject":"AstraZeneca!","object":"osimertinib","evidence":"ORG:astrazeneca|SPONSORS_TRIAL_OF|CHEMBL3353410|","trial_count":14},"why":"'AstraZeneca!' names 2 company nodes; use the id"}],"text":""}
```

The original alternate Genentech claim with `object='CHEMBL1201583'`, `evidence='ORG:genentech|SPONSORS_TRIAL_OF|CHEMBL1201583|'`, `trial_count=5` also rejects with exactly the same ambiguity reason. `astra-zeneca` and `ASTRAZENECA?` do likewise. Exact IDs accept their own edges. These outputs are in `replay_s3/identity_attack_results.json` and `boundary_results.json`.

## NOTES with exact inputs

1. Retired PROFILE remains evidence-consistent. In an isolated copy run `UPDATE node SET retired_at='fixture' WHERE id='CHEMBL3353410'` while retaining the resolved dictionary. For `What is osimertinib?`, input `{"claims":[{"kind":"drug","drug":"osimertinib","evidence":"profile:CHEMBL3353410","max_stage":"APPROVAL"}]}` accepts and renders `- OSIMERTINIB: maximum clinical stage APPROVAL [profile:CHEMBL3353410]`. The retained value is in that fixture graph; this is not a fabricated claim. Alias lookup does not recheck retirement (`src/structured.py:133-145`), and node property lookup lacks the live filter (`:241`). The persisted graph has no retired Drug node.
2. Exact label and alias are distinct resolution branches. If a second organisation label becomes `Astra-Zeneca`, `AstraZeneca` remains a unique exact label and can identify AZ; `AstraZeneca!` exposes both candidates and refuses. Root separately reran these original S3 confirmation inputs. This is permitted by the ID / unique exact label / singleton alias alternatives; it is not an alias-count bypass.
3. Wrong parent/subsidiary names remain refused on the AZ edge: the exact S3 sponsorship claim above with ordinary `subject='MedImmune'`, `'Genentech'`, or `'Roche'` rejects endpoint mismatch. In contrast `BeiGene` / `BeOne` are genuine singleton rename aliases and accept the `ORG:beonemedicines` sponsorship edge in `boundary_results.json`.
4. Existing boundary semantics remain graph-consistent: final duplicate JSON value is checked; 51 valid claims yield 50 accepted and one excess-count rejection; no stored action/phase/status/stage normalization collisions were found; `ANTISENSE INHIBITOR` and `INHIBITOR` remain distinct; unsupported types/counts, wrong-question evidence, PROFILE-as-relation, and retired edges reject.

Identity-scope recommendation: APPROVE with NOTES.
