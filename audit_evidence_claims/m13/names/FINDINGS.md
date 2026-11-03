# Round 13 historical name-resolution verification

Reviewed HEAD `481100c584ec772cc2332960ba5d3b28ba36ae6f`. **Every originally reported blocking name reproduction M1–M12 is FIXED for its exact input.** Retained over-refusals and previously recorded policy limitations are individually classified below. This does not imply the overall map is safe: a new joined-chelator originator leak was independently found and handed to the root/attack workers.

## Execution and evidence

- **52 reused scripts** copied with current-run outputs relocated to m13/names and owned HTTP port **19300**; historical read paths and exact input inventories retained. **44 reused leaf reproduction scripts executed**, excluding wrapper/comparison utilities, all exit 0. [Manifest](reuse_manifest.json), [core](replay_execution.json), [supplement](supplement_execution.json), [cumulative runner](round9_execution.json), [original M1](m1_exact/execution.json), [additional](additional_execution.json), [final HTTP](final_replay_execution.json), [completion](completion_execution.json).
- Original **113-case / 7,511-key** sweep: **319** changes against its declared old-method counterfactual, **70** formerly linked aliases without a current Drug. Counts and loss set equal M12: **zero newly lost aliases**. These are diagnostic counts, not 70 defects. [Sweep](names_m5_attack.json), [summary](names_m5_summary.json), [current/M12 loss sets](new_alias_losses.json), [cache-safe sweep](adapted_names_m5_summary.json).
- Frozen no-relink counterfactual: **1,648 exact questions; 68 identical / 1,556 metadata-only / 24 semantic / zero errors**, identical to M12. The adapted script changes current `_link`; public-wrapper-only historical counterfactuals are retained as provenance. [Evidence](adapted_frozen_qa_relink_sweep.json).
- **39-case earlier matrix:** only the explicitly accepted M5-S2 over-refusal differs from its old expectation. **26 M6/M7 literal controls pass**; all **19 non-M5-S2 old alias losses remain restored**. [Matrix](focused_matrix.json), [literal controls](historical_focus.json), [restored set](historical_alias_set_check.json).
- Reused exact M9 matrix: **146 inputs / 16 QA**; M10 probe: **1,224 inputs**, plus **35-case focus**; M11 original probe: **26 inputs**, plus **12 literal/preserved-osimertinib cases**. M12 original focused attack: **41 inputs**, comparing current with the actual HEAD^ query module on the same current app/rules/database. [M9](m9_attacks/probe_results.json), [M10](m10_attacks/probe_results.json), [M10 focus](m10_attacks/focus_results.json), [M11](m11_attacks/key_equivalence_results.json), [M11 exact](m11_exact.json), [M12](m12_attacks/focused_results.json).
- Historical name HTTP scripts use the unmodified CLI server and closed owned port 19300 after completion. M7 44 / M9 50 / M9-S1 10 responses remain HTTP200. [M7](m7_attacks/http_results.json), [M9](m9_attacks/http_results.json), [M9-S1](new_alias_confirmation.json), [final checks](worker_final_checks.json).
- Every evidence file referenced by the 59 inherited name-finding rows is semantically equal to M12 after ignoring declared counterfactual outputs, refusal wording, timing and process metadata. Positive centres, graph/evidence values and refusal existence are retained in this comparison. This validates carrying the dispositions forward; it is not an exhaustive safety proof. [Comparison and ignored fields](replay_comparison.json).

## Individual historical dispositions

M2 has no completed report; its partial name cases are represented in M2b's cumulative scripts. DB, UI, cost and full HTTP confirmation are covered by other workers.

| Round / finding | Status | Current evidence |
|---|---|---|
| M1 B1 `bevacizumab - awwb`, `89Zr - trastuzumab`, `[89Zr] trastuzumab` | **FIXED** | Original three suffix/tracer inputs all refuse, no centre. [Evidence](m1_exact/names_product_bypass.json). |
| M1 B4 retire CHEMBL3353410 in memory; query name, ID, EGFR | **FIXED** | Retired OSIMERTINIB by name and ID is not_found; retired neighbour excluded. [Evidence](m1_exact/names_retired_http_results.json). |
| M1 S5 silent ambiguity: Roche, MET, osimertinib EGFR/reversal, Mvasi and bevacizumab | **FIXED** | Roche/MET/multiple entities retain the selected identity and disclose alternatives/refusal. [Evidence](names_reproduction_results.json). |
| M1 Lowercase IDs / Investigator names: nct00200395, chembl3353410, Armando Santoro Md | **NOT FIXED** | Lowercase NCT/CHEMBL IDs and investigator label remain not_found; exact IDs work. [Evidence](names_unsupported_forms.json). |
| M2b R1 `osimertinib and generic version of bevacizumab`, reverse/comma, trial/sponsor QA | **FIXED** | Explicit separate osimertinib survives beside generic bevacizumab in both orders. [Evidence](names_regressions.json). |
| M2b R1 tracer/oral-product collateral refusal, both orders | **FIXED** | Separate osimertinib survives tracer/oral-product refusals in both orders. [Evidence](names_regressions.json). |
| M2b Inherited `What is the generic version of bevacizumab?` | **FIXED** | Leading question text no longer detaches the generic qualifier. [Evidence](names_new_boundaries.json). |
| M2b Embedded multi-ID `Sharedbrand company` fixture | **FIXED** | Sharedbrand company fixture discloses the other matching company ID. [Evidence](names_boundary_details.json). |
| M3 and M4 M3-B1 `paclitaxel with albumin bound nanoparticles`, formulation variant, `generic version with bevacizumab` | **FIXED** | Albumin-bound nanoparticle/generic-with original cases refuse, no parent map. [Evidence](names_new_boundaries.json). |
| M3 and M4 M3-B2 leading generic-version question | **FIXED** | What is the generic version of bevacizumab? refuses. [Evidence](names_new_boundaries.json). |
| M3 and M4 M3 comma collateral refusal: osimertinib with separately listed liposomal/biosimilar drug; reversals/QA | **FIXED** | Comma-separated ordinary osimertinib survives qualified-product refusal. [Evidence](names_new_boundaries.json). |
| M3 and M4 M3 bare erlotinib hydrochloride / long paclitaxel-poliglumex name; nested-parent re-link | **FIXED** | Complete erlotinib salt/paclitaxel-poliglumex names retain their own IDs without re-linking nested parents. [Evidence](names_attack.json). |
| M3 and M4 M4-B1 wrong shortest-span tie: `osimertinib with generic version of bevacizumab`, reversal/added a | **FIXED** | Both drugs in the original same-item generic-description tie are refused under revised design. [Evidence](names_attack.json). |
| M3 and M4 M4-B1 semicolon and fullwidth-comma variants | **FIXED** | Semicolon and fullwidth comma separate the valid osimertinib item. [Evidence](names_separator_checks.json). |
| M3 and M4 M4-B2 long qualified poliglumex / `generic version of the monoclonal antibody bevacizumab` | **FIXED** | Long qualified poliglumex and distant generic qualifier refuse; bare long-name control survives. [Evidence](names_attack.json). |
| M3 and M4 M4-B3 consumed qualifier: biosimilar version / liposomal formulation / albumin-bound / two-product combination | **FIXED** | Consumed qualifier cases for biosimilar/liposomal/albumin/two products refuse parent identity. [Evidence](names_attack.json). |
| M3 and M4 M4 target/company collateral refusal: EGFR or AstraZeneca beside biosimilar bevacizumab, reverse/with controls | **FIXED** | EGFR/AstraZeneca survive beside refused bevacizumab; refusal remains disclosed. [Evidence](names_m5_attack.json). |
| M3 and M4 M4 no-relink QA assessment | **FIXED** | Frozen 1,648 cases: 68 identical, 1,556 entity-metadata-only, 24 semantic changes, 0 errors. [Evidence](adapted_frozen_qa_relink_sweep.json). |
| M5 and M6 M5-B1 reported attached slash/pipe and internal both-sides-glued attack | **FIXED** | Attached slash/pipe cases select separate OSIMERTINIB and disclose refused bevacizumab. [Evidence](names_m5_confirm.json). |
| M5 and M6 M5-B2 `liposomal and nanoparticle formulation of doxorubicin`, plural/sustained-release | **FIXED** | Forward bare-qualifier carry refuses original liposomal/nanoparticle product descriptions. [Evidence](names_m5_confirm.json). |
| M5 and M6 M5-S1 `biosimilar anastrozole, Arimidex`; `biosimilar Prolia, xgeva` | **FIXED** | Separate Arimidex/xgeva aliases survive prior-item refusal. [Evidence](names_cross_item_refusal.json). |
| M5 and M6 M5-S1 `Erlotinib, hydrochloride biosimilar bevacizumab`, semicolon | **FIXED** | Qualified comma/semicolon Erlotinib lists preserve CHEMBL553. [Evidence](names_m5_attack.json). |
| M5 and M6 M5-S2 Pegylated interferon alfa-2a | **NOT FIXED** | NOT FIXED; explicitly accepted M5-S2 over-refusal. Preferred name and ID remain available. [Evidence](names_m5_summary.json). |
| M5 and M6 M6-B1 interior slash/pipe | **FIXED** | Interior slash/pipe variants retain separate osimertinib; no refused-product originator. [Evidence](focused_matrix.json). |
| M5 and M6 M6-B2 U+3002 suffix punctuation, trailing em dash/hyphen, leading hyphen | **FIXED** | Original U+3002/trailing em dash/trailing hyphen/leading hyphen suffix inputs all refuse. [Evidence](historical_focus.json). |
| M5 and M6 M6-B2 supplementary bracketed/Unicode variants | **FIXED** | Bracketed, quoted, question-mark and Unicode-hyphen suffix variants all refuse. [Evidence](historical_focus.json). |
| M5 and M6 M6-B3 `doxorubicin (nanoparticle and liposomal formulation)` / `bevacizumab (investigational and biosimilar)` | **FIXED** | Both original parenthesized trailing qualifier descriptions refuse; QA evidence 0. [Evidence](historical_focus.json). |
| M5 and M6 M6 non-parenthetical reversed-qualifier supplement | **NOT FIXED** | NOT FIXED as original expectation: doxorubicin in nanoparticle and liposomal formulations selects CHEMBL53463, unchanged listing-word policy consequence. [Evidence](reversed_results.json). |
| M5 and M6 M6-S1 six complete stored aliases returning another Drug ID | **FIXED** | All six exact complete stored aliases select their intended Drug IDs. [Evidence](historical_focus.json). |
| M5 and M6 M6-S1 prefixed QA using those comma-containing names | **NOT FIXED** | NOT FIXED: prefixed ENDOSTATIN comma-name QA selects CHEMBL4297747 with 2 rows; prefixed Rapamycin comma-name QA selects CHEMBL413 with 5 rows. [Evidence](historical_focus.json). |
| M5 and M6 M6 associated lone stored-alias losses | **FIXED** | All 19 old non-M5-S2 losses retain the stored Drug ID; only accepted M5-S2 remains refused. [Evidence](alias_regressions.json). |
| M7 M7-B1 Whole-name refusal bypass: `bevacizumab-awwb?`, `bevacizumab-awwb!`, quoted form | **FIXED** | All original whole-name question-mark/exclamation/quote bypasses refuse; QA evidence 0. [Evidence](historical_focus.json). |
| M7 M7-B2 Wrappers and Unicode hyphens: `(bevacizumab-awwb)`, `[bevacizumab-awwb]`, U+2011 suffix and bio-similar | **FIXED** | Parentheses, brackets, U+2011 suffix and bio-similar qualifier originals refuse. [Evidence](historical_focus.json). |
| M7 M7-B3 Whitespace isotope: `89Zr trastuzumab` | **FIXED** | 89Zr trastuzumab refuses; both trial and sponsor QA evidence 0. [Evidence](historical_focus.json). |
| M7 M7-S1 Canonical equality too broad: `Erlotinib, hydrochloride`, `osimertinib,mesylate`, `is a` | **FIXED** | Erlotinib, hydrochloride -> CHEMBL553; osimertinib,mesylate -> CHEMBL3353410; is a -> not_found. [Evidence](historical_focus.json). |
| M7 M7-S2 Lone exact stored names: `(E/Z)-AFATINIB`, `RO 09-1978/000`, `Anusol plus hc` and 19-alias set | **FIXED** | All 19 historical non-M5-S2 lone names are restored, including (E/Z)-AFATINIB, RO 09-1978/000, Anusol plus hc. [Evidence](alias_regressions.json). |
| M8 M8-B1 [89 Zr] trastuzumab; tab/newline/NBSP mass-element variants | **FIXED** | [89 Zr] and tab/newline/NBSP variants refuse; trial/sponsor QA evidence 0. [Evidence](attacks/probe_results.json). |
| M8 M8-B2 bevacizumab-(awwb), bevacizumab-[awwb]; separate osimertinib | **FIXED** | Internal wrappers bevacizumab-(awwb)/-[awwb] refuse; separate osimertinib survives. [Evidence](attacks/probe_results.json). |
| M8 M8-B3 bevacizumab⸺awwb and all 26 Unicode Pd characters | **FIXED** | All 26 Unicode Pd characters normalize and refuse the suffix product. [Evidence](attacks/unicode_dashes.json). |
| M8 M8-S1 Natural cache rollover in exact 7,511-key sweep | **FIXED** | Original 7,511-key scan completes; adapted scan cache_errors=[]; natural HTTP rollover verified by cost worker. [Evidence](adapted_names_m5_summary.json). |
| M8 M8-S2 biosimilar, and osimertinib; semicolon; biosimilar and, osimertinib | **FIXED** | biosimilar, and osimertinib / semicolon / and-comma forms retain CHEMBL3353410. [Evidence](m9_attacks/probe_results.json). |
| M8 M8-S3 566C, 9-ac, 5ac | **FIXED** | 566C/9-ac/5ac retain CHEMBL1450/CHEMBL274070/CHEMBL1489. [Evidence](attacks/lone_alias_results.json). |
| M8 M8-S4 5.BETA.,20-EPOXY-1,2.ALPHA.,4,7.BETA. | **FIXED** | 5.BETA.,20-EPOXY-1,2.ALPHA.,4,7.BETA. retains CHEMBL428647. [Evidence](attacks/lone_alias_results.json). |
| M9 M9-B1 bevacizumab_awwb; bevacizumab-a.w.w.b; bevacizumab-(a.w.w.b); accented/decomposed forms | **FIXED** | All named original positive-key mismatch forms refuse; independent actual HTTP confirms underscore/accent examples and QA evidence 0. [Evidence](m9_attacks/probe_results.json). |
| M9 M9-B2 [89.Zr] trastuzumab; 89:Zr trastuzumab; 89.Zr and 89::Zr variants | **FIXED** | Original folded isotope inputs refuse; actual HTTP and trial/sponsor QA evidence 0. [Evidence](m9_attacks/probe_results.json). |
| M9 M9-B3 bevacizumab awwb; bevacizumab (awwb)/[awwb]; trastuzumab dkst/(dkst) | **FIXED** | All original whitespace/wrapper suffix forms refuse; HTTP QA evidence 0. [Evidence](m9_attacks/probe_results.json). |
| M9 M9-S1 Theophylline in dextrose 5% in plastic container | **FIXED** | Exact lone alias now maps THEOPHYLLINE / CHEMBL1355736 over HTTP200. [Evidence](new_alias_confirmation.json). |
| M9 M9-S1 40-o-(2-hydroxyethyl)-rapamycin | **NOT FIXED** | Accepted known over-refusal; EVEROLIMUS and its ID work. [Evidence](new_alias_confirmation.json). |
| M9 M9-S1 42-o-(2-hydroxyethyl)rapamycin | **NOT FIXED** | Accepted known over-refusal; EVEROLIMUS and its ID work. [Evidence](new_alias_confirmation.json). |
| M9 M9-S1 Trastuzumab--vcmmae conjugate | **NOT FIXED** | Accepted known over-refusal; TRASTUZUMAB VEDOTIN and its ID work. [Evidence](new_alias_confirmation.json). |
| M10 M10-B1 isotope inside stored name | **FIXED** | Exact inputs now refuse with no centre and zero trial/sponsor QA evidence: A33 124i; A33 124 i; A33 [124i]; A33 124I; A33-124i [Evidence](m10_attacks/focus_results.json). |
| M10 M10-B2 isotope token substituted for substance | **FIXED** | Exact inputs now refuse with no centre and zero trial/sponsor QA evidence: 18F fluorothymidine; 18-F fluorothymidine; [18F] fluorothymidine; 18F nonexistingdrug; 18-F trastuzumab; 90y somatostatin [Evidence](m10_attacks/focus_results.json). |
| M10 M10-B3 punctuation consumed neighbor-word budget | **FIXED** | Exact inputs now refuse with no centre and zero trial/sponsor QA evidence: trastuzumab 89 - Zr; trastuzumab [89 - Zr]; trastuzumab 89 _ Zr [Evidence](m10_attacks/focus_results.json). |
| M10 M10-B4 separator variants of product qualifiers | **FIXED** | Exact inputs now refuse with no centre and zero trial/sponsor QA evidence: generic-version of bevacizumab; generic_version of bevacizumab; albumin - bound paclitaxel; follow-on-biologic bevacizumab [Evidence](m10_attacks/focus_results.json). |
| M11 M11-B1 split isotope element symbol | **FIXED** | All literal reported forms refuse with no centre and zero trial/sponsor evidence; each comma-osimertinib form retains CHEMBL3353410. Inputs: [89Z.r] trastuzumab; 89Z_r trastuzumab; trastuzumab [89Z.r] [Evidence](m11_exact.json). |
| M11 M11-B2 fragmented biosimilar suffix | **FIXED** | All literal reported forms refuse with no centre and zero trial/sponsor evidence; each comma-osimertinib form retains CHEMBL3353410. Inputs: bevacizumab a - w w b; bevacizumab - a - w - w - b; bevacizumab a_w_w_b [Evidence](m11_exact.json). |
| M11 M11-S1 9-amino-20(s)-camptothecin | **NOT FIXED** | Explicitly accepted known over-refusal; preferred name and exact node ID still select CHEMBL274070. [Evidence](alias_loss_controls.json). |
| M11 M11-S1 il-6ra | **NOT FIXED** | Explicitly accepted known over-refusal; preferred name and exact node ID still select CHEMBL1237022. [Evidence](alias_loss_controls.json). |
| M11 M11-S1 TAK-659F | **NOT FIXED** | Explicitly accepted known over-refusal; preferred name and exact node ID still select CHEMBL3979920. [Evidence](alias_loss_controls.json). |
| M12 M12-B1 split symbol inside chelator-bearing stored alias | **FIXED** | Exact reported [89Z.r]-DFO-daratumumab and 89Z_r-dfo-daratumumab, plus three alternate old cases, refuse with zero qualified trial/sponsor QA evidence. Separate osimertinib survives; bare daratumumab maps correctly. [Evidence](m12_attacks/focused_results.json). |
| M12 M12-S1 rad001c / RAD001C stored-alias over-refusal | **NOT FIXED** | Still refuses with no centre, as in M12. Current and HEAD^ agree. rad, RAD001, EVEROLIMUS and exact ID remain available. This is inherited and nonblocking. [Evidence](new_alias_regression.json). |
| M12 M12 supplementary previously unpromoted descriptive label-distance inputs | **NOT FIXED** | The old labelled/labeled-distance forms still draw TRASTUZUMAB and match the HEAD^ result. Retained separately from the new joined-chelator blocker, consistent with prior classification. [Evidence](m12_attacks/focused_results.json). |

## M12 repair and retained loss

The newly added loop joins every letters-and-digits word run inside a consumed name up to six characters (`src/query.py:259-267`), then feeds the result to the isotope predicate (`287-289`). `[89Z.r]-DFO-daratumumab` now contains the glued run `89Zr`, so the matched drug is refused at `426-435`; `_whole_name` cannot override it (`304-305`). The exact reported M12 variants have no centre or qualified QA evidence. [Stage evidence](m12_attacks/focused_results.json).

`rad001c` remains a nonblocking inherited stored-alias loss: both current and HEAD^ refuse. The key-splitting rule sees same-drug alias `rad` plus isotope-shaped `001c` (`src/query.py:291-295`); `rad`, `RAD001`, EVEROLIMUS and its ID still work. No newly lost unambiguous stored alias was observed in the 7,511-key replay. [Stages and controls](new_alias_regression.json).

## Independently discovered new candidate

`89ZrDFO-daratumumab` and `89zrdfodaratumumab` have the same canonical key as the stored/refused `89zr-dfo-daratumumab`, yet map to **DARATUMUMAB / CHEMBL1743007**, with **2 trial + 2 sponsor QA rows**. The raw resolver is ALIAS, resolver veto `{}`, item/public linkers emit Drug without Refused, and whole-name shortcut is `None`. The isotope is now inside one longer alnum word (`89ZrDFO`), so joining whole words does not extract it; the separate key-prefix check still requires missing same-drug remainder `dfodaratumumab`. `[89ZrDFO]-daratumumab`, `89zrdfo daratumumab`, and a separate-osimertinib variant also leak. Refused controls and bare daratumumab behave as expected. This candidate was independently communicated to the root/attack workers for actual HTTP confirmation. [Nine-case independent stage/QA evidence](joined_label_probe.json).

## Demos, integrity and reproduction

All seven original QA demos retain counts **12, 12, 11, 1, 12, 0, 0**. Six full responses still equal bfcb83d; Mvasi differs only in refusal metadata. [Demo comparison](names_demo_results.json). Full page demos are in the separate DB/UI worker's evidence.

No tracked file or application code was changed. Historical source hashes are unchanged; owned port 19300 is closed. Outputs and TMP/TEMP/TMPDIR stay under m13/names, bytecode is disabled. No model was called. Counterfactuals replace only their stated query methods/module and retain current app/rules/data; they are not historical deployment reconstructions. The KOA/KhOpenApi original-versus-modified-code requirement is conditional on application edits; this audit makes none.

```text
python -B audit_evidence_claims/m13/names/run_round9.py
python -B audit_evidence_claims/m13/names/run_completion.py
python -B audit_evidence_claims/m13/names/joined_label_probe.py
python -B audit_evidence_claims/m13/names/build_summary.py
```

Run port-sharing wrappers sequentially. The root report decides the overall verdict using independent HTTP and DB/UI evidence.
