# R5 independent semantic review

Reviewed HEAD `9fda6f8ec36e8b49d75e2d51d7f73ad3ba21e359`, diff `git diff 9fda6f8^...HEAD`, against the real graph through `Engine().check`. No tracked files changed. All new artifacts use the `spec5` prefix in `audit_evidence_claims/r5/`. Bytecode writes were disabled. The tests below judge support in the question's retrieved evidence; no external clinical truth is assumed.

## BLOCKERS

All passing attacks below return `grounded=True`, `applicable=True`, `unsupported_claims=[]`.

### B1. A heading's erased noun still carries an unsupported kind or clinical claim

Question: `What does osimertinib target?`

Exact answers and observed output:

```text
The following companies inhibit EGFR:
- Osimertinib
```

True; [].

```text
These drugs:
- EGFR
```

True; [].

```text
The following NSCLC drugs inhibit EGFR:
- Osimertinib
```

True; [].

Other exact variants `These trials:\n- Osimertinib`, `These organisations inhibit EGFR:\n- Osimertinib`, and `These NSCLC trials:\n- Osimertinib` also pass. The sole evidence is `OSIMERTINIB acts on EGFR (inhibitor)`. It does not call osimertinib a company/trial, EGFR a drug, or osimertinib an NSCLC drug.

Cause: `src/claims.py:260-264` deletes the entire determiner-plus-noun slot, including optional `NSCLC`. The first answer becomes `Osimertinib inhibit EGFR`; there is no company word left for the kind validator. A plain noun can itself assert a false type. Adjective retention does not protect it.

Controls:

- `Companies inhibiting EGFR:\n- Osimertinib` -> False; `entity: Companies`, `wording: companies`.
- `The following drugs inhibit EGFR:\n- Osimertinib` -> True, correctly.
- `The following safe drugs inhibit EGFR:\n- Osimertinib` -> False; `wording: safe`.
- `These safe companies inhibit EGFR:\n- Osimertinib` -> False; `wording: companies`, `wording: safe`.
- `Osimertinib is an NSCLC drug.` -> False; `indication: lung cancer`.

The absent kind/disease words distinguish these cases from README's one-statement word-rearrangement residue. These are ordinary list headings, not artificial encodings.

Artifacts: `spec5_extended.json` IDs `heading_wrong_kind_companies`, `heading_wrong_kind_trials`, `heading_wrong_kind_drug`, `heading_wrong_kind_org`, `heading_wrong_kind_bare`, `heading_right_kind`, `heading_nsclc_rel`, `heading_nsclc_trial`, `heading_safe`, `heading_safe_company`; `spec5_controls.json` ID `nsclc_control`.

### B2. A relative clause redirects a kind claim to the wrong owner

Question: `What does osimertinib target?`

```text
EGFR, which is inhibited by osimertinib, is a drug.
```

True; []. The shorter `EGFR, inhibited by osimertinib, is a drug.` and `EGFR that is inhibited by osimertinib is a drug.` also pass. The main subject EGFR is explicitly called a drug. The single retrieved statement `OSIMERTINIB acts on EGFR (inhibitor)` has no word `drug` and identifies EGFR as the target through its edge/linker type.

Cause: `src/claims.py:987-988` assigns a kind word to the last entity mentioned anywhere before it. Here that is the drug osimertinib inside the relative clause, not EGFR, the subject of `is a drug`. `_clauses` only splits certain conjunctions/semicolons (`:541-558`); commas and relative clauses stay together. The supported passive relation covers the named entities, leaving the wrong kind attribution accepted.

Controls:

- `EGFR is a drug.` -> False; `wording: drug`.
- R4 exact `EGFR is a drug inhibited by osimertinib.` -> False; `wording: drug`.
- `EGFR is inhibited by osimertinib and is a drug.` -> False; `wording: drug`.
- Faithful inverse `Osimertinib, which inhibits EGFR, is a drug.` -> False; `wording: drug`.

This introduces a kind word absent from the evidence, then licenses it through the wrong entity; it is outside the explicitly listed one-statement vocabulary residue. The controls show both an unsupported pass and a faithful failure from the same positional rule.

Artifacts: `spec5_probe.json` IDs `kind_intervening`, `kind_intervening2`; `spec5_extended.json` IDs `kind_relative`, `kind_relative_that`, `kind_relative_drug_faithful`; `spec5_controls.json` IDs `kind_original_r4`, `kind_control_drug`.

### B3. A named subject group shares only the first member's trial context

Question: `Which drugs act on ALK?`

```text
LORLATINIB and PLB1003 have clinical trials in this graph.
```

True; []. Also:

```text
LORLATINIB and PLB1003 inhibit ALK in clinical trials.
```

True; []. The retrieved rows explicitly state:

```text
LORLATINIB acts on ALK (inhibitor; max stage APPROVAL; 13 NSCLC trial(s) in this graph)
PLB1003 acts on ALK (inhibitor; max stage PHASE_1; 0 NSCLC trial(s) in this graph)
```

The first row supports lorlatinib's trial context, while PLB1003 has zero in this graph. No retrieved row contains `clinical`. These are unsupported group assertions rather than harmless statements that both drugs inhibit ALK.

Cause: `_check_attributes` chooses `subject = subjects[0]` (`src/claims.py:771`), and its new `wide` pool selects only rows mentioning that first subject (`:802`). `about_trials` is then shared by all kind/clinical words (`:808-811`, `:1013-1018`). Explicit named groups are not expanded once per member in `_check_unit`; the per-member paths at `:383-398` handle pronouns and elided subjects only.

Controls:

- `PLB1003 and LORLATINIB have clinical trials in this graph.` -> False; `wording: clinical`, `wording: trials`.
- `PLB1003 and LORLATINIB inhibit ALK in clinical trials.` -> False; same findings.
- `LORLATINIB and PLB1003 inhibit ALK. They are in clinical trials.` -> False; same findings.
- `LORLATINIB and PLB1003 inhibit ALK and have clinical trials.` -> False; same findings.
- `LORLATINIB and CRIZOTINIB inhibit ALK in clinical trials.` -> True; evidence-consistent control.
- R4 exact `PLB1003 inhibits ALK in clinical trials in this graph.` -> False; both wording findings.

The group can also borrow NSCLC context: `LORLATINIB and PLB1003 have NSCLC trials.` -> True; reversed order -> False (`indication: lung cancer`, `wording: trials`). The clinical-plus-graph case is the strongest reproduction because the new word is absent from all evidence and the graph counts explicitly disprove the group assertion. It requires two drug rows, outside the one-statement residue.

Artifacts: `spec5_probe.json` IDs `group_clinical`, `group_clinical_reverse`, `group_clinical_pron`, `group_both_clinical`; `spec5_extended.json` IDs `group_shared_clinical`, `group_shared_trials`, `group_shared_nsclc`, `group_shared_nsclc_reverse`, `group_shared_clinical_pron_survive`, `group_shared_clinical_elided`; `spec5_controls.json` IDs `clinical_group_graph`, `clinical_group_graph_reverse`, `clinical_original_r4`.

### B4. The documented `it` repair does not cover a passive list

Question: `Which drugs act on ALK?`

```text
ALK is targeted by LORLATINIB and PLB1003. It is approved.
```

True; []. Changing `It` to `They` returns False; `wording: approved`.

`ALK is targeted by LORLATINIB and PLB1003. It has clinical trials.` also passes. With `They have clinical trials`, the checker rejects clinical/trials for PLB1003. `ALK is targeted by LORLATINIB and PLB1003 and is approved.` passes too.

Cause: `st.group` is the grammatical subject group `[ALK]`. At `src/claims.py:368-369`, selection of the biggest type group in `st.last` only occurs when `p['label'] in PLURAL`; `it` is not in `PLURAL` (`:155`). It therefore resolves to ALK (`:377-379`). ALK then pulls in all ALK rows, including other drugs' APPROVAL and positive trial counts. This differs from `CODEX_CLAIMS_R4_VERDICT.md` B2, which explicitly says `they`/`it` after `targeted by A and B` stands for A and B, and from the docstring's per-member `it` claim at `src/claims.py:32-33`.

If `It` is read as the grammatical subject ALK, approval is unsupported; if read as one of the drugs, PLB1003 does not have APPROVAL. The conservative rule documented by this repair promises checking all candidate group members, but does not do so here. This is at least a confirmed code/documentation repair discrepancy. The verdict does not depend on treating this case as outside the broad rearrangement residue: B1-B3 are stronger, unambiguous outside-residue failures.

Artifacts: `spec5_probe.json` IDs `passive_it_approval`, `passive_they_approval`; `spec5_extended.json` IDs `passive_it_clinical`, `passive_it_clinical_reverse`, `passive_they_clinical`, `group_shared_clinical_subjectless_after_passive`, `object_them_then_it`.

## SHOULD FIX

Faithful ordinary kind phrases are rejected by the same nearest-entity rule:

Question `What does osimertinib target?`:

- `EGFR is inhibited by the drug osimertinib.` -> False; `wording: drug`. The kind word occurs before its named noun but after EGFR, so it binds to EGFR.
- `Osimertinib, which inhibits EGFR, is a drug.` -> False; `wording: drug`. The kind word binds to EGFR in the relative clause.
- Control `The drug osimertinib inhibits EGFR.` -> True.

These are focused false-positive controls, not a sampled corpus and not a claim about most answers. The parent's full faithful corpus review determines that part of the approval bar. Source: `src/claims.py:981-991`; artifacts `spec5_probe.json` ID `kind_faithful`, `spec5_extended.json` IDs `kind_relative_drug_faithful`, `kind_before_noun_faithful`.

## NOTES

### Requested semantic-path checks

| Path | Fresh result |
|---|---|
| Heading adjective retention | `The following safe drugs inhibit EGFR:\n- Osimertinib` rejects safe; true repair. Erased kind/NSCLC nouns still fail B1. |
| Group survival through per-member checks | R4 `PLB1003 and LORLATINIB act on ALK and they act on ALK and they are approved.` rejects approved. Replacing PLB1003 with CRIZOTINIB passes consistently. |
| Object `them` | Q5 `AstraZeneca sponsors osimertinib and carboplatin. It sponsors them in 10 trials.` rejects number 10; R4 exact fix. Q4 `LORLATINIB and CRIZOTINIB inhibit ALK. ALK is targeted by them.` passes consistently. Replacing second ALK with EGFR rejects both drug-EGFR edges. |
| Elided subject after group | Q4 `LORLATINIB and PLB1003 act on ALK and are approved.` rejects approved; clinical-trial elision also rejects. |
| Passive list `they` | Rejects shared approval/trials for LORLATINIB + PLB1003; faithful `They are drugs` passes. |
| Passive list `it` | Fails B4; not actually expanded to biggest drug group. |
| Kind owner | R4 exact `EGFR is a drug inhibited by osimertinib.` rejects; new relative-clause owner fails B2. |
| Subject trial/NSCLC context | R4 single PLB1003 clinical claim rejects; named group borrows first member's context, B3. |
| Identity across explicit verb | `PLB1003 is LORLATINIB.` rejects identity. |
| Identity with elided subject | `Osimertinib inhibits EGFR and is EGFR.` rejects identity. |
| Alias identity | `Osimertinib is Tagrisso.` passes consistently. |

Phase/status runs, numeric ownership, citation stripping, historical replay, full regressions and documentation corpus review are handled by the root/other reviewer. This report deliberately does not claim independent coverage of those paths.

Reproduce from repository root with bytecode disabled:

```powershell
$env:PYTHONDONTWRITEBYTECODE = '1'
$env:PYTHONIOENCODING = 'utf-8'
python -B audit_evidence_claims/r5/spec5_probe.py
python -B audit_evidence_claims/r5/spec5_extended.py
python -B audit_evidence_claims/r5/spec5_controls.py
```

Each script writes only its own corresponding JSON under `r5/`. All exact inputs and complete `Engine.check` outputs are preserved there; `spec5_controls.json` additionally records all retrieved evidence rather than the Engine's first-eight preview.

VERDICT: CHANGES REQUIRED
