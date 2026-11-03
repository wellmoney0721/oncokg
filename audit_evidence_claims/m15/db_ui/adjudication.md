# Independent round-15 tracer adjudication

Reviewed HEAD `1b3896669387cbc142c12b726909231cca8658db`. This assessment reuses the prior independent staged adjudicator, changing its candidate set; the current and HEAD^ query modules run against the same current app, rules and database. It does not reconstruct an older deployment. [Fresh evidence](adjudication_tracer.json), [script](adjudicate_tracer.py).

## P1: punctuation inside an adjacent chelator-label word defeats every refusal stage

`89-ZrDFO trastuzumab`, `89Z.rDFO trastuzumab`, and `trastuzumab DFO89-Zr` all draw **TRASTUZUMAB / CHEMBL1201585**, with 13 live trials, no refused entity, and **12/12** qualified trial/sponsor QA evidence rows. Appending `, osimertinib` still selects TRASTUZUMAB. Both current and HEAD^ have the leak.

Controls `89ZrDFO trastuzumab` and `trastuzumab DFO89Zr` refuse and yield **0/0** QA rows. The corresponding canonical keys are unchanged by the added punctuation. Thus this differs from the earlier descriptive-distance cases: a single hyphen is inserted inside an immediately adjacent, recognized label/chelator word, without adding a descriptive word, changing the drug, or moving the label farther away. `89Zr labelled trastuzumab` and `trastuzumab labelled with 89Zr` were also rerun and remain inherited supplementary failures, not new discoveries.

| Stage | All three new candidate spellings |
|---|---|
| Raw intervention resolver | CONTAINED_ALIAS, CHEMBL1201585; leftover chelator text UNRESOLVED |
| Raw tracer predicate / `_qualified` | false / false |
| Resolver veto | `{}` |
| `_marked` | `None` |
| Item/public linker | Drug CHEMBL1201585; no Refused |
| Whole-name shortcut | `None` |
| Map | TRASTUZUMAB, 13 live trials |
| Qualified trial/sponsor QA | 12 / 12 evidence rows |

The causal trace is especially direct for the hyphen cases: `_isotope_edge('89-ZrDFO')` and `_isotope_edge('DFO89-Zr')` already return **true**. `_marked` does not pass those original words to the helper. Instead `_alnum_words` splits them (`src/query.py:111-113,316-317`) into `['89','ZrDFO']` or `['DFO89','Zr']`. The glued-neighbour loops test only whether the entire glued string is an isotope, which it is not because it also includes DFO (`src/query.py:318-329`). The subsequent fused-label helper receives only individual fragments (`src/query.py:330-333`), all of which return false. The raw tracer regex also misses these forms (`src/textrules.py:303-314`), so the resolver cannot provide a veto (`src/normalize.py:738-746`; `src/query.py:249-265`). The final own-name key scan examines only `trastuzumab`, not the neighboring word (`src/query.py:345-363`). The accepted hit becomes the map centre (`src/app.py:88-95`).

Required outcome: preserve the refusal of a recognized adjacent isotope/chelator label under the same punctuation normalization that lookup uses. No application repair was made in this audit.

## Exact historical residuals: case-sensitive stored tracer keys

| Exact input | Current | HEAD^ | Classification |
|---|---|---|---|
| `3HVINBLASTINE`, `3Hvinblastine` | refused, 0/0 QA | VINBLASTINE, 5/5 QA | **FIXED** exact uppercase cases |
| `3hvinblastine` | VINBLASTINE / CHEMBL159, 5/5 QA | same | **NOT FIXED**, historical M14 variant |
| `[3h]-vinblastine`, `3H-vinblastine` | refused, 0/0 QA | same | Refused controls |
| `A33124I` | refused, 0/0 QA | ADAKITUG | **FIXED** exact M13/M14 uppercase residual |
| `A33124i` | ADAKITUG / CHEMBL5314551, 0/0 QA | same | **NOT FIXED**, lowercase closing-label variant |
| `A33 124i` | refused, 0/0 QA | same | Refused control |

The dictionary itself links canonical `3hvinblastine` to `[3h]-vinblastine`, and `a33124i` to `A33 124i`; controls establish refused identity without external pharmacology assumptions. For the two lowercase inputs every refusal stage misses, and the case condition explicitly skips the one-letter label (`src/query.py:353-355`). `_medical_isotope('124i')` is reachable only after that case condition, so the medical-mass exception does not help the lowercase closing label.

The user explicitly described the repair as uppercase-sensitive. These results document that repair's exact boundary rather than mislabeling uppercase fixes as failed. The original no-originator-leak approval guarantee still has these residuals, and the user did not list these tracer under-refusals among accepted over-refusals or the separate ChEMBL biosimilar-code limitation. They should not be counted as new independent families merely to inflate the finding count. The new neighboring-chelator punctuation finding is sufficient for CHANGES REQUIRED by itself.
