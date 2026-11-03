# Round 7 name-resolution replay report

HEAD `9bd7cb4b5d9270bbe99cb5dfec3993502f6b5377`. Every exact named m1-m6 originator-leak finding is FIXED, including M6-B1/B2/B3, but the inherited bracketed suffix cases still pass both guards, and the new whole-name fast path introduces an additional punctuation regression. The six bare-input M6-S1 wrong-identity examples are FIXED; their prefixed-QA forms remain NOT FIXED under the whole-input-only policy. Nineteen other lone stored aliases remain lost, separate from the explicitly accepted M5-S2.

Only scratch files below `audit_evidence_claims/m7/names/` were written. No application source was edited. These are direct Engine results except the explicitly identified HTTP artifacts.

## Reproduction completeness

- All **13 inherited m5/m6 name scripts** exited 0: [execution](replay_execution.json), [provenance](replay_manifest.json). Their algorithm/input logic was left unchanged; only output destinations moved. This includes **62 original inputs + 14 extra probes**, **30 m3 boundary cases + 21 joiner aliases**, **45 m4 attacks + 37 QA controls + 2,584 multi-token aliases**, and **113 m5 attacks + 7,511 unique alias keys**, 49 confirmation cases, and 13 cross-item controls.
- To avoid relying only on extracted input corpora, all five original m1 name scripts were also rerun: `names_probe.py`, `names_extra_probe.py`, `names_product_probe.py`, `names_retired_probe.py`, `names_retired_http.py`. Only their output paths and original fixed port changed. The unchanged CLI served actual HTTP on owned port **8903**, including the extra-script HTTP list. The retired-node fixture remained in memory; every stored retired node was queried by ID and label. All five exited 0; the server was terminated. [Original-script provenance](m1_exact/reuse_manifest.json), [execution](m1_exact/execution.json), [extra results](m1_exact/names_extra_results.json), [retired fixture HTTP](m1_exact/names_retired_http_results.json), [all retired rows](m1_exact/names_retired_probe_stdout.txt).
- All six m6 supplements exited 0, including the exact **106-case/8-QA fresh probe** and **11-case reversed-qualifier probe**: [execution](supplement_execution.json), [fresh cases](fresh_results.json), [reversed cases](reversed_results.json). The two m6 attack scripts were reused without source changes because the relative directory depth is identical.
- The old no-relink scripts patch `link_entities`, but the guarded matcher has moved to `_link`; their path-only replay now has an inert counterfactual. Those runs are retained but **not interpreted as no-relink evidence**. A separately logged mechanical adaptation patches `_link`, leaving the outer resolver and whole-name wrapper intact, and replays the exact frozen 1,648-string prior input list. It yields **64 identical / 1,560 entity-metadata-only / 24 semantic differences / 0 errors**. The inputs, order and duplicates exactly equal the m5 corpus. [Adaptation](counterfactual_adaptation.json), [adapted result](adapted_frozen_qa_relink_sweep.json), [corpus verification](corpus_verification.json).
- [39-case prior-finding matrix](focused_matrix.json) and [23-case M6/guard-stage matrix](m7_focus.json) isolate current identities and refusal stages. The only unexpected result in the 39-case matrix is the already accepted M5-S2.

## Earlier findings: exact dispositions

| Earlier finding and exact input | Status | Current evidence |
|---|---|---|
| M1-B1: `bevacizumab - awwb`, `89Zr - trastuzumab`, `[89Zr] trastuzumab`, compact controls | **FIXED** | Refused, no originator. [Original HTTP](m1_exact/names_product_bypass.json), [matrix](focused_matrix.json). |
| M1-B4: retire CHEMBL3353410 in memory; `osimertinib`, ID, `EGFR` | **FIXED** | Name/ID not_found; EGFR excludes retired neighbour. [Real handler](m1_exact/names_retired_http_results.json). |
| M1 silent identity ambiguity: `Roche`, `MET`, `osimertinib EGFR`, reverse; `Mvasi and bevacizumab` | **FIXED for disclosure** | Stored selected identity, alternatives and refusal exposed. [Original replay](names_reproduction_results.json), `src/app.py:88-114`. |
| M1 lowercase IDs / Investigator name: `nct00200395`, `chembl3353410`, `Armando Santoro Md` | **NOT FIXED - unchanged usability qualification** | Unsupported forms remain not_found; canonical IDs work. [Controls](names_unsupported_forms.json). |
| M2b-R1: `osimertinib and generic version of bevacizumab`, reverse and comma forms | **FIXED** | Only separately accepted osimertinib survives; trial/sponsor QA returns its evidence. [Replay](names_regressions.json). |
| M2b-R1 separate tracer/oral product: `[89Zr] trastuzumab and osimertinib`, reverse; `osimertinib and oral azacitidine` | **FIXED** | Separately named osimertinib retained. [Replay](names_regressions.json). |
| M2b inherited / M3-B2: `What is the generic version of bevacizumab?` | **FIXED** | Full qualified drug refusal, no centre. [Replay](names_regressions.json). |
| M2b embedded company ambiguity fixture: `Sharedbrand company` | **FIXED** | `also_matching_ids=['ORG:roche']` is disclosed; selected AstraZeneca explicit. [Fixture](names_boundary_details.json), `src/app.py:97-102`. |
| M3-B1: `paclitaxel with albumin bound nanoparticles`, formulation variants; `generic version with bevacizumab` | **FIXED** | No parent centre or parent QA evidence. [Replay](names_new_boundaries.json). |
| M3 comma collateral refusal: `osimertinib, liposomal doxorubicin`, `osimertinib, biosimilar bevacizumab`, reversals/QA | **FIXED** | Separate osimertinib survives; QA retains its evidence. [Replay](names_new_boundaries.json). |
| M3 full-name/nested-relink controls: `erlotinib hydrochloride`, `Paclitaxel conjugate with poly-l-glutamic acid` | **FIXED / retained** | CHEMBL1079742 / CHEMBL2108628; no nested parent re-link. Explicit separately named parent remains linkable. [Replay](names_attack.json). |
| M3 supplemental / M4-B1: `osimertinib with generic version of bevacizumab`, reversed and added-a variants | **FIXED under current design** | Same-item drugs both refuse; zero originator QA evidence. Intentional fail-closed behavior. [Replay](names_attack.json), [QA](names_final_checks.json). |
| M4-B1 semicolon/fullwidth comma: `osimertinib; generic version of bevacizumab`, `osimertinib` + U+FF0C FULLWIDTH COMMA + ` generic version of bevacizumab` | **FIXED** | Separate osimertinib retained, product refused. [Replay](names_separator_checks.json). |
| M4-B2: `generic version of Paclitaxel conjugate with poly-l-glutamic acid`, distant monoclonal-antibody qualifier | **FIXED** | Full qualified product refused, no drug QA evidence. [Replay](names_attack.json), [QA](names_final_checks.json). |
| M4-B3: `biosimilar version of bevacizumab`, `liposomal formulation of doxorubicin`, `paclitaxel with albumin-bound nanoparticles`, two-product form | **FIXED** | No parent drug hit or originator evidence. [Replay](names_attack.json). |
| M4 target/company collateral refusal: `EGFR biosimilar bevacizumab`, `AstraZeneca biosimilar bevacizumab`, reverse/with forms | **FIXED** | Target/company survives; qualified Drug refused. [Replay](names_attack.json). |
| M4 no-relink assessment | **FIXED / retained** | 1,648 frozen questions; same 24 nested-company interpretation changes, 0 exceptions. [Meaningful adapted comparison](adapted_frozen_qa_relink_sweep.json). |
| M5-B1 reported and internal-separator examples: `bevacizumab-awwb/ osimertinib`, `bevacizumab - awwb/osimertinib`, pipe counterparts | **FIXED** | OSIMERTINIB / CHEMBL3353410 selected; refused bevacizumab product exposed. Trial/sponsor QA yields 12 osimertinib rows. [Replay](names_m5_confirm.json), [M6 matrix](m7_focus.json). |
| M5-B2: `liposomal and nanoparticle formulation of doxorubicin`, plural and sustained-release variants | **FIXED** | No centre, no originator QA evidence. [Replay](names_m5_confirm.json), [matrix](focused_matrix.json). |
| M5-S1: `biosimilar anastrozole, Arimidex`; `biosimilar Prolia, xgeva` | **FIXED** | Separate Arimidex/CHEMBL1399 and Xgeva/CHEMBL1237023 retained. [Replay](names_cross_item_refusal.json). |
| M5-S1 salt assembly: `Erlotinib, hydrochloride biosimilar bevacizumab`, semicolon | **FIXED** | Parent ERLOTINIB / CHEMBL553, no cross-item salt assembly. [Replay](names_m5_confirm.json). |
| M5-S2: `Pegylated interferon alfa-2a` | **NOT FIXED - explicitly accepted known over-refusal** | Refuses; canonical name and CHEMBL1201560 still work. [Matrix](focused_matrix.json). |
| M6-B1: `bevacizumab - awwb/osimertinib`, pipe | **FIXED** | Same as M5 internal-separator row. `src/query.py:208-230,293-294`. [Matrix](m7_focus.json). |
| M6-B2 exact reported punctuation: `bevacizumab-awwb` + U+3002 IDEOGRAPHIC FULL STOP, trailing em dash/hyphen and leading hyphen | **FIXED** | No centre; trial/sponsor QA 0 rows. `src/query.py:138-154,218-220`. [Matrix](m7_focus.json). |
| M6-B3: `doxorubicin (nanoparticle and liposomal formulation)`, `bevacizumab (investigational and biosimilar)` | **FIXED** | No centre; trial/sponsor QA 0 rows. `src/query.py:228-229,243-246`. [Matrix](m7_focus.json). |
| M6-S1 six complete stored names selecting wrong drugs | **FIXED for all six exact bare-input wrong-ID examples** | Stored IDs restored, table below. [Matrix](m7_focus.json). |
| M6-S1 prefixed-QA forms: `Which trials evaluate ENDOSTATIN, N-TERMINAL-MGGSHHHHH?`; `Which trials evaluate Rapamycin, 42-o-(2-hydroxyethyl)-?` | **NOT FIXED - current whole-input-only design consequence** | ENDOSTATIN question still selects CHEMBL4297747 with 2 evidence rows; Rapamycin question still selects CHEMBL413 with 5 rows. The matching sponsor questions do likewise. The whole-name fast path does not apply to these prefixed inputs. [Actual HTTP](../root_checks/alias_http.json). |
| M6 associated lone-alias losses | **NOT FIXED for 19 beyond accepted M5-S2** | Exact stored slash/joiner aliases still disappear; should-fix below. [Alias sweep](names_m5_summary.json). |

DB/UI/cost findings are owned by the parent review, not reclassified here.

M6-S1 now preserves these exact bare-input identities:

| Exact input | Current correct stored ID |
|---|---|
| `Usp mab 003, monoclonal igg1` | CHEMBL1743008 |
| `Usp mab 002, monoclonal igg1` | CHEMBL1201583 |
| `CP-358,774` | CHEMBL553 |
| `Rapamycin, 42-o-(2-hydroxyethyl)-` | CHEMBL1908360 |
| `12,13-desoxyepothilone b, cis` | CHEMBL96172 |
| `ENDOSTATIN, N-TERMINAL-MGGSHHHHH` | CHEMBL4297946 |

The corresponding prefixed QA behavior is not repaired by a whole-input-only shortcut. The parent's unchanged-server reproduction shows `Which trials evaluate ENDOSTATIN, N-TERMINAL-MGGSHHHHH?` still links CHEMBL4297747 (2 rows), and `Which trials evaluate Rapamycin, 42-o-(2-hydroxyethyl)-?` still links CHEMBL413 (5 rows). Sponsor questions select the same shorter names. These remain **NOT FIXED** historical reproductions, reported as consequences of the explicit current policy, not promoted into a new blocker against that policy. [Parent HTTP evidence](../root_checks/alias_http.json).

## Refusal gaps found in the replay

`(bevacizumab-awwb)` and `[bevacizumab-awwb]` genuinely pass **both** refusal layers: resolver accepts ALIAS / CHEMBL1201583, `_resolver_blocked` returns `{}`, `_link` returns BEVACIZUMAB, and `explore` draws that originator. Trial and sponsor questions each return **12** originator evidence rows. Bare `bevacizumab-awwb` refuses. The punctuation wraps the same refused suffix; no external pharmacology premise is required. These were already present in the m6 fresh attack and remain **NOT FIXED**, although the narrower named M6-B2 examples are fixed. Current guards preserve brackets (`src/query.py:218-220`), the suffix pattern is anchored (`src/textrules.py:156-157,213-223`), and later canonical alias matching removes the wrapper. [Stage-isolated result](m7_focus.json), [exact reused m6 attack](fresh_results.json).

`bevacizumab-awwb?` is an additional **new fast-path regression**: the prior 514929c linker refuses, current map draws BEVACIZUMAB. The resolver accepts it; `_whole_name` obtains the positive key using `text.strip(" ?.!")` (`src/query.py:191`), but tests the raw punctuated input for refusal (`195-196`), then returns before `_link` (`138-142`). `_link` alone correctly refuses this input. Quoted suffix/tracer forms have the same fast-path-versus-list-linker disagreement. Do not incorrectly classify these latter cases as both guards missing. [Comparison](fresh_results.json), [stages](m7_focus.json). Parent review supplies independent CLI HTTP confirmation.

The non-parenthetical `doxorubicin in nanoparticle and liposomal formulations` still maps doxorubicin in the reused reversed probe. Under the explicit current listing-word policy this has separated items, so this report does not promote it beyond the demonstrated bracketed suffix blockers.

## Should-fix: full-name shortcut excludes stored slash and listing-word names

Of **7,511** unique alias keys, the inherited before/after sweep finds **20** formerly linked aliases with no current Drug: the accepted M5-S2 plus **19** slash/joiner-containing aliases. No alias in this sweep now returns a *different* drug ID from the unique stored ID. The complete lost-alias list and stored records are in [names_m5_summary.json](names_m5_summary.json).

Actual unchanged-server HTTP on owned port 8903 confirms:

| Exact input | Stored unique Drug | Resolver | Map |
|---|---|---|---|
| `(E/Z)-AFATINIB` | CHEMBL1173655 | EXACT / same ID | HTTP 200 not_found |
| `RO 09-1978/000` | CHEMBL1773 | ALIAS / same ID | HTTP 200 not_found |
| `Anusol plus hc` | CHEMBL389621 | UNRESOLVED + BLOCKED_TARGET_TERM; neither a distinct-product nor tracer refusal | HTTP 200 not_found |

The corresponding exact IDs draw live nodes. [HTTP, stored-index proof, and ID controls](alias_http.json), [server lifecycle](alias_lifecycle.json). `_whole_name` rejects any slash/pipe or standalone joiner **before** checking whether the whole input uniquely names a stored drug (`src/query.py:189-194`). This contradicts the stated whole-name precedence for a single stored, non-refused input. It is a lone-valid-name should-fix, separate from originator leakage and from M5-S2.

## Demo and integrity limits

All seven QA demos retain evidence counts **12, 12, 11, 1, 12, 0, 0**. Six complete outputs equal original bfcb83d; Mvasi differs only in refusal metadata. [Demo comparison](names_demo_results.json). The parent DB/UI worker verifies the remaining page demonstrations and callbacks.

No browser-executed claim is made by this name subreport. Direct Engine calls are not asserted to apply the HTTP size cap. Old-revision comparisons restore only the exact methods/globals specified by each reused script and keep current data and other source; they are isolation experiments, not full old-application runs. Inert historical counterfactuals are explicitly segregated above. No tracked file was edited, and both owned HTTP server lifecycles ended.
