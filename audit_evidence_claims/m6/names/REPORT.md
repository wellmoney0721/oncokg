# M6 name-resolution replay subreport

Only files below `audit_evidence_claims/m6/names/` were created by this worker. The 13 m5 replay scripts were copied with their output-directory strings changed; the manifest records SHA-256 provenance. The m5 scripts already replace old HTTP helpers with direct Engine calls, so this evidence is **direct Engine**, not an HTTP claim. All 13 exited 0; none was allowed to write a tracked file. The former-revision comparisons replace exactly the functions named in each artifact and keep the current data and remaining code.

- [Execution ledger](replay_execution.json), [source/adaptation manifest](replay_manifest.json), [runner](run_replays.py).
- [Focused 39-case matrix](focused_matrix.json) and [reproducer](focused_matrix.py).
- Original m1 inputs: 62 reproductions + 14 regression probes ([replay](names_reproduction_results.json)).
- m4 replay: 45 focused map/name cases, 37 QA cases and 2,584 multi-token alias records ([replay](names_attack.json)); all m3 boundary cases and joiner aliases also replayed ([replay](names_new_boundaries.json)).
- m5 replay: 113 boundary attacks and 7,511 unique alias keys ([attack](names_m5_attack.json)), 49 confirmation cases ([confirmation](names_m5_confirm.json)), 13 cross-item controls ([controls](names_cross_item_refusal.json)).

## Earlier finding matrix

These are dispositions of exact reported inputs. Broad refusal coverage remains blocked by the residual separator mechanism below. Parent review owns DB, HTTP, UI and cost findings.

| Earlier finding | Disposition | Current evidence |
|---|---|---|
| M1-B1 `bevacizumab - awwb`, `89Zr - trastuzumab`, `[89Zr] trastuzumab` and compact controls | **FIXED** | No centre; full refusal. [M1 replay](names_reproduction_results.json), [matrix](focused_matrix.json). |
| M1 identity ambiguity `Roche`, `MET`, `osimertinib EGFR`, reverse order | **FIXED for disclosure** | Stored alias-selected FOLIC ACID/METFORMIN and first selected entity remain, with alternative entities disclosed; not an invented-edge finding. [M1 replay](names_reproduction_results.json). `src/app.py:88-114`. |
| M1 lowercase IDs / Investigator names: `nct00200395`, `chembl3353410`, `Armando Santoro Md` | **NOT FIXED ? unchanged usability limit** | These remain not_found; uppercase IDs and `ORG:armandosantoromd` work. [Controls](names_unsupported_forms.json). |
| M2b-R1 `osimertinib and generic version of bevacizumab`, reverse and comma variants | **FIXED** | OSIMERTINIB/CHEMBL3353410 retained; qualified bevacizumab refused. QA trials starts `NCT03909334|EVALUATES|CHEMBL3353410|NCT03909334`, sponsor QA starts `ORG:astrazeneca|SPONSORS_TRIAL_OF|CHEMBL3353410|`. [Replay](names_regressions.json). |
| M2b-R1 separate tracer/oral product: `[89Zr] trastuzumab and osimertinib`, reverse; `osimertinib and oral azacitidine` | **FIXED** | Separately listed osimertinib survives. [Replay](names_regressions.json). |
| M2b inherited `What is the generic version of bevacizumab?` (also M3-B2) | **FIXED** | Whole input refused, no centre. [Replay](names_regressions.json). |
| M2b embedded company alias fixture `Sharedbrand company` | **FIXED** | `also_matching_ids=['ORG:roche']` produces Roche in map `also`; selected AstraZeneca remains explicit. [Fixture](names_boundary_details.json). `src/app.py:97-102`. |
| M3-B1 `paclitaxel with albumin bound nanoparticles`, nanoparticle formulation variants; `generic version with bevacizumab` | **FIXED** | No originator centre; corresponding QA has no supporting drug evidence. [Replay](names_new_boundaries.json). |
| M3 comma collateral refusal `osimertinib, liposomal doxorubicin`, `osimertinib, biosimilar bevacizumab`, reversals | **FIXED** | Only separately listed osimertinib survives; trial QA retains its 12 rows. [Replay](names_new_boundaries.json). |
| M3 longer-name/nested-relink controls `erlotinib hydrochloride`, `Paclitaxel conjugate with poly-l-glutamic acid` | **FIXED / retained** | CHEMBL1079742 / CHEMBL2108628 respectively; no nested parent relink. Explicit separately named parent remains linkable. [Attack/control replay](names_attack.json), [matrix](focused_matrix.json). |
| M3 supplementary / M4-B1 `osimertinib with generic version of bevacizumab`, reversed and added-a variants | **FIXED under current design** | Same-item drugs both refused, with no centre; trial/sponsor QA has 0 evidence. Intended over-refusal is accepted. [QA](names_final_checks.json), [replay](names_attack.json). |
| M3 supplementary / M4-B1 semicolon and fullwidth comma | **FIXED** | `osimertinib; generic version of bevacizumab` and fullwidth-comma control retain only osimertinib. [Replay](names_separator_checks.json). |
| M4-B2 `generic version of Paclitaxel conjugate with poly-l-glutamic acid`; distant generic version of monoclonal antibody bevacizumab | **FIXED** | Entire qualified drug refused; no centre / drug QA evidence. [Replay](names_attack.json), [QA](names_final_checks.json). |
| M4-B3 `biosimilar version of bevacizumab`, `liposomal formulation of doxorubicin`, `paclitaxel with albumin-bound nanoparticles`; two-product combination | **FIXED** | No parent drug hit / originator QA evidence. [Replay](names_attack.json), [separator controls](names_separator_checks.json). |
| M4 Target/company collateral refusal `EGFR biosimilar bevacizumab`, `AstraZeneca biosimilar bevacizumab`, reversals/with forms | **FIXED** | Target/Company survives while drug is refused. [Replay](names_attack.json). |
| M4 no-relink assessment | **FIXED / retained behavior** | 1,612 current questions: 28 identical, 1,560 entity-metadata-only, 24 semantic differences, 0 errors against the same HEAD linker with matched-token exclusion disabled. Semantic differences remain removal of nested company hits from full drug aliases. [Sweep](names_qa_relink_sweep.json). |
| M5-B1 exact reported examples `bevacizumab-awwb/ osimertinib`, `bevacizumab - awwb/ osimertinib`, `bevacizumab-awwb| osimertinib` | **FIXED for these inputs** | Selects OSIMERTINIB/CHEMBL3353410 and discloses refused bevacizumab product. Their trial/sponsor QA now returns 12 osimertinib rows. [Confirmation](names_m5_confirm.json). |
| M5-B1 mechanism / earlier attack `bevacizumab - awwb/osimertinib` and pipe counterpart | **NOT FIXED** | Originator BEVACIZUMAB/CHEMBL1201583, 122 trials, no refusal. Exact slash case was already in the reused m5 attack. See residual blocker below. [Attack](names_m5_attack.json), [matrix](focused_matrix.json). |
| M5-B2 `liposomal and nanoparticle formulation of doxorubicin`, plural and sustained-release variants | **FIXED** | No centre; propagated refusal spans first qualifier plus next item. Exact singular/plural QA controls contain 0 evidence. [Confirmation](names_m5_confirm.json), [matrix](focused_matrix.json). |
| M5-S1 `biosimilar anastrozole, Arimidex`; `biosimilar Prolia, xgeva` | **FIXED** | Separate Arimidex/CHEMBL1399 and Xgeva/CHEMBL1237023 survive. Arimidex trial QA yields 2 rows. [Confirmation](names_m5_confirm.json), [controls](names_cross_item_refusal.json). |
| M5-S1 `Erlotinib, hydrochloride biosimilar bevacizumab`, semicolon variant | **FIXED** | ERLOTINIB/CHEMBL553, 118 trials; no cross-item salt assembly. QA yields parent evidence. [Confirmation](names_m5_confirm.json). |
| M5-S2 `Pegylated interferon alfa-2a` | **NOT FIXED ? explicitly known/accepted over-refusal** | No centre. Canonical `PEGINTERFERON ALFA-2A` and ID select CHEMBL1201560. Do not count this as a new blocker. [Confirmation](names_m5_confirm.json). |

## Residual blocker: internal slash/pipe is never separated

`bevacizumab - awwb/osimertinib` selects **BEVACIZUMAB / CHEMBL1201583**, with 122 trials and no refused item. The same string passed to the existing resolver produces `bevacizumab - awwb: BLOCKED_DISTINCT_PRODUCT` and `osimertinib: EXACT / CHEMBL3353410`. This is an internally established refused product, without any external pharmacology inference. The precise input already exists in the m5 attack and is still failing in the fresh replay. `bevacizumab - awwb|osimertinib` similarly leaks. [Current exact input/results](new_focused.json), [reused m5 script and results](names_m5_attack.json).

Cause: `src/query.py:143-154` splits punctuation only for commas/semicolons, strips slash/pipe only from the **edges** of a whitespace token, and adds boundaries only when that raw token starts or ends with slash/pipe. An internal `awwb/osimertinib` is unchanged. `_qualified` (`99-110`) never gets a run ending in `awwb`; the anchored suffix regex (`src/textrules.py:156-157,213-223`) misses. Positive matching (`src/query.py:212-237`) then accepts the separate `bevacizumab` token. Required outcome: refuse that product and either retain the separate osimertinib or fail closed; never draw CHEMBL1201583.

Related unchanged earlier probes include `bevacizumab - awwb&osimertinib`, `bevacizumab - awwb& osimertinib`, `bevacizumab-awwb+ osimertinib`, and Arabic comma/semicolon, halfwidth comma or fullwidth slash appended to `awwb`. These all draw BEVACIZUMAB in [m5 confirmation replay](names_m5_confirm.json). The explicit ASCII slash/pipe contract alone is sufficient to block approval; these are additional normalization gaps under the same mechanism, not independent findings.

## Alias and demo consequences of current item design

All seven page QA demos retain evidence counts **12, 12, 11, 1, 12, 0, 0**. Six complete results equal bfcb83d; Mvasi differs only in refusal metadata. [Demo comparison](names_demo_results.json).

The 7,511 unique alias-key sweep shows 57 formerly linked lone aliases now have no drug hit against the exact bf436c6 functions: the recorded pegylated alias plus **56 aliases containing newly enforced list punctuation/words**. Examples include `ICI 182,780`, `CP-675,206`, `Nk cells, autologous`, `Anusol plus hc`. The list-boundary design explains these losses; no demo uses them, and this report does not relabel these deliberate boundary restrictions as originator leaks. [Summary](names_m5_summary.json).

However, six complete stored aliases now select only a *different* drug ID, which is a separate identity consequence for the parent reviewer to assess under the explicit item policy:

| Stored complete alias | Unique stored drug | Selected current drug |
|---|---|---|
| `Usp mab 003, monoclonal igg1` | DROZITUMAB / CHEMBL1743008 | PEMBROLIZUMAB / CHEMBL3137343, matched `mab` |
| `Usp mab 002, monoclonal igg1` | BEVACIZUMAB / CHEMBL1201583 | PEMBROLIZUMAB / CHEMBL3137343, matched `mab` |
| `CP-358,774` | ERLOTINIB / CHEMBL553 | ERLOTINIB HYDROCHLORIDE / CHEMBL1079742, matched `CP-358` |
| `Rapamycin, 42-o-(2-hydroxyethyl)-` | EVEROLIMUS / CHEMBL1908360 | SIROLIMUS / CHEMBL413, matched `Rapamycin` |
| `12,13-desoxyepothilone b, cis` | EPOTHILONE D / CHEMBL96172 | PRALSETINIB / CHEMBL4582651, matched `cis` |
| `ENDOSTATIN, N-TERMINAL-MGGSHHHHH` (stored preferred name) | CHEMBL4297946 | ENDOSTATIN / CHEMBL4297747 |

These are reproducible in `alias_anomalies` of [the reused attack](names_m5_attack.json); each row contains stored alias provenance, current and predecessor hits, and resolver output. No claim of new false graph edges is made. They arise because punctuation-bearing chemical aliases are interpreted as separate list items before the full stored identity can be considered (`src/query.py:143,216-217,277`).

## Frozen prior QA corpus completeness follow-up

The dynamic no-relink sweep above derives its questions from current alias behavior and therefore shrank to 1,612. To re-run **every earlier reproduction**, [the same script](frozen_qa_relink_sweep.py) was additionally run with the exact frozen `inputs` array from `audit_evidence_claims/m5/names_qa_relink_sweep.json`. This replay contains **1,648 questions: 64 identical, 1,560 entity-metadata-only differences, 24 semantic changes, 0 errors** against current HEAD with matched-token exclusion disabled. [Full output](frozen_qa_relink_sweep.json), [source hash/input equality verification](frozen_qa_relink_verification.json).

All 1,648 strings compare exactly equal to the prior array, including order and duplicates. The current 24 changed-answer rows are included verbatim in the output, and their input names are also listed in the verification artifact. They remain the same nested-company versus complete-drug interpretation effects. Dynamic artifacts were preserved.
