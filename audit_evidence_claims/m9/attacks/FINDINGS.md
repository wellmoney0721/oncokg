# Round 9 independent normalization/refusal attacks

Reviewed `3a362eb`, without changing tracked files. These are **newly reported inherited failures**, not new regressions introduced by this HEAD: a bounded comparison loads the exact `ec4eede:src/query.py` in memory and observes the same eight unsafe outputs. It also verifies the two control repairs, `bevacizumab-(awwb)` and `[89 Zr] trastuzumab`. [Predecessor evidence](predecessor_results.json).

The fresh matrix covers **146 distinct inputs and 16 QA questions**. Full records include raw and normalized resolver responses, `_resolver_blocked`, `_link`, `_whole_name`, final entities, map identity, and dictionary entries. Direct probes reopen SQLite using `mode=ro`. An independent original CLI server on owned port **8895** confirms **50 HTTP requests, all 200**; its served page matches `web/try.html` byte for byte, its process was stopped, and its port is closed. [Stages](probe_results.json), [compact matrix](probe_summary.json), [HTTP](http_results.json), [predicate details](predicate_details.json).

The first HTTP attempt used the wrong `question` key for QA; the application expects `text`. Those 12 controlled 400 responses are a **harness error**, retained in [http_wrong_payload.json](http_wrong_payload.json). The corrected rerun changes only that key and repeats the complete 50-request set. [Adaptation record](adaptation.json).

## M9-B1 — P1: the positive alias key removes distinctions the refusal guards retain

### Underscore punctuation

`POST /api/explore` with `{"text":"bevacizumab_awwb"}` returns **BEVACIZUMAB / CHEMBL1201583, 122 trials**, `also: []`. `/api/resolve` returns ALIAS of the same originator. `_resolver_blocked` is `{}`, `_link` emits the Drug, `_whole_name` is `None`, and no stage emits a refusal.

U+005F LOW LINE is Unicode category **Pc**, so it is punctuation, but the new punctuation fold at `src/query.py:115-118` uses `[^\w\s]+`. Python's `\w` includes underscore. Therefore the declared punctuation-to-hyphen view leaves `bevacizumab_awwb` unchanged. The anchored suffix guard requires a hyphen (`src/textrules.py:156-157`), whereas `canonical_key` drops the underscore (`src/textrules.py:339-346`) and finds the stored `Bevacizumab awwb` alias. Positive lookup is at `src/query.py:339-354`.

Controls `bevacizumab-awwb` and `bevacizumab-(awwb)` refuse. The suffix `awwb` is explicitly present in `BIOSIMILAR_FDA_SUFFIXES` at `src/textrules.py:169-171`; the identity conclusion is grounded in that repository rule and the stored alias, without an external pharmacology assumption. Measured variants `bevacizumab__awwb`, `bevacizumab-_awwb`, `bevacizumab_-awwb`, `bevacizumab_._awwb`, `bevacizumab _ awwb` and `trastuzumab_dkst` also leak. `rituximab_abbs` does not resolve, so that analogue is not counted as a leak.

### Accents and punctuated suffix letters

`bevácizumab-awwb` (U+00E1 in the molecule name), its decomposed equivalent `beva\u0301cizumab-awwb`, and `bevacizumab-áwwb` all draw the same originator with no refusal. The first two were confirmed over HTTP. NFKC folding at `src/query.py:105-106` preserves the composed accented letter. The suffix regex is ASCII-only, but the positive key uses NFKD and removes combining marks (`src/textrules.py:341-345`), so the accepted key becomes the canonical key of the forbidden suffix form. The raw resolver returns ALIAS rather than refusing. This is a shared guard/identity mismatch, not a lost existing resolver refusal.

The inherited m8-script cases `bevacizumab-a.w.w.b` and `bevacizumab-(a.w.w.b)` still draw BEVACIZUMAB. Punctuation folding produces internal hyphens in the suffix, which the anchored `[A-Za-z]{2,12}` guard does not accept; the lookup key then removes them. These are supplementary reproductions of the same broader positive-key mismatch, not a claim that m8's exact simple-wrapper blocker remains unfixed.

For both `bevacizumab_awwb` and `bevácizumab-awwb`, HTTP trial QA and sponsor QA each return **12 originator evidence rows**. The first trial edge is `NCT00955305|EVALUATES|CHEMBL1201583|NCT00955305`; the first sponsor edge is `ORG:roche|SPONSORS_TRIAL_OF|CHEMBL1201583|`. The ordinary hyphen control yields zero for both QA forms.

Required outcome: a representation accepted as the known suffix-bearing alias must not acquire originator identity merely because its punctuation or accent is dropped only on the positive-lookup path. Apply the stated punctuation treatment consistently and check the equivalences the positive key actually accepts.

## M9-B2 — P1: the punctuation-folded view does not reach the isotope-label guards

`POST /api/explore` with `{"text":"[89.Zr] trastuzumab"}` returns **TRASTUZUMAB / CHEMBL1201585, 13 trials**, with no refusal. The raw resolver extracts the parenthetical and returns EXACT trastuzumab; `_resolver_blocked` is `{}`; the item linker returns the Drug via the `89zr-trastuzumab` alias; `_whole_name` is `None`.

The item token after edge-wrapper removal is `89.Zr`. The new punctuation fold converts it to `89-Zr`, and **`T.is_isotope_label('89-Zr')` is true**. But `hit` at `src/query.py:114-118` applies only `is_distinct_product` and `is_radiotracer` to the folded view. The one- and two-word isotope-label tests at `src/query.py:122-126` see only the original tokens. `is_radiotracer('89-Zr trastuzumab')` is false: its anchored grammar expects an additional hyphen between isotope and carrier or a bracketed isotope (`src/textrules.py:303-314`). This leaves the declared folded-word isotope check unperformed before aggressive alias matching.

`89:Zr trastuzumab`, `89.Zr trastuzumab`, `[89:Zr] trastuzumab` and `89::Zr trastuzumab` reproduce the same mechanism. `89-Zr trastuzumab`, `89 Zr trastuzumab`, `[89 Zr] trastuzumab` and `[89Zr] trastuzumab` correctly refuse. `89.Zr-trastuzumab` also refuses because its folded complete string satisfies the separate tracer grammar. These controls isolate the missing application of the isotope-label predicate; the report does not assert that any arbitrary unfamiliar isotope spelling is a valid medical name.

HTTP trial and sponsor QA for `[89.Zr] trastuzumab` each return **12 originator evidence rows**. The first trial edge is `NCT00016367|EVALUATES|CHEMBL1201585|NCT00016367`; the first sponsor edge is `ORG:nationalcancerinstitute|SPONSORS_TRIAL_OF|CHEMBL1201585|`. Both QA forms for the hyphenated-token control `89-Zr trastuzumab` return zero.

Required outcome: run the one- and two-word isotope-label tests on the punctuation-folded item representation as well, preserving the specified lone-stored-name exception.

## M9-B3 — P1: a known biosimilar suffix separated by whitespace is accepted as an exact originator alias

`bevacizumab awwb`, `bevacizumab (awwb)` and `bevacizumab [awwb]` all draw **BEVACIZUMAB / CHEMBL1201583, 122 trials**, without refusal. The first two are independently confirmed over HTTP. The repository itself records `awwb` as a biosimilar suffix (`src/textrules.py:169-171`), while the dictionary also lists `Bevacizumab awwb` under the originator. The whole-name exception is not permission to erase that product distinction: the user grants that exception only to the tracer rule for a lone stored name, and the code's whole-name docstring explicitly says product refusals must win (`src/query.py:221-226`).

The guard requires a hyphen at `src/textrules.py:156-157`; whitespace alone is not accepted. The raw resolver returns ALIAS for `bevacizumab awwb`, or EXACT plain bevacizumab after extracting `(awwb)` / `[awwb]` (`src/textrules.py:358-363`). Stage one thus has no recorded refusal. Stage two strips the separate word's edge wrappers at `src/query.py:257-260`, leaving `bevacizumab awwb`; neither raw nor punctuation-folded guard view supplies a hyphen. It resolves the complete alias. Stage three returns the originator for the literal stored alias, or `None` for the wrapped forms, leaving the unsafe positive result intact (`src/query.py:229-239`).

`trastuzumab dkst` and `trastuzumab (dkst)` likewise draw TRASTUZUMAB. Controls with the explicit hyphen refuse. This is distinct from M9-B1's punctuation mismatch: even the literal stored alias has the problem. Both HTTP QA forms for `bevacizumab (awwb)` return 12 originator rows.

Required outcome: recognize the repository's known biosimilar suffix when whitespace or a separate wrapper separates it from the named originator, before accepting the alias. A separately named legitimate drug should continue to survive according to the stated item policy.

## Passing boundaries and limits

All **16 fresh comma/semicolon/slash/pipe and parenthesis carry-boundary cases** retained the separately listed osimertinib. This includes `biosimilar (and), osimertinib`, `biosimilar (and)/osimertinib`, `biosimilar, (and osimertinib)`, and `biosimilar and (/ osimertinib)`. The repaired `biosimilar, and osimertinib`, `biosimilar; and osimertinib`, and `biosimilar and, osimertinib` controls also pass.

The direct controls `566C`, `9-ac`, `5ac` and their explicitly delimited combinations retain their stored identities; no new lone-name loss is claimed from this subset. The historical sweep worker owns the full alias audit. `Pegylated interferon alfa-2a` remains the explicitly accepted M5-S2 refusal. Basic valid molecules and legitimate originator FDA suffixes retain their identities.

All implicated positive maps use real live graph rows; the defect is the selected identity, not fabricated graph edges. These are sufficient originator blockers even though existing demos may pass. Root/sibling workers own historical disposition matrices, exhaustive DB/UI checks, demos and costs.

Reproduction, from the repository root, with bytecode disabled:

```text
python -B audit_evidence_claims/m9/attacks/probe.py
python -B audit_evidence_claims/m9/attacks/http_probe.py
python -B audit_evidence_claims/m9/attacks/predecessor.py
```

All scripts write only beside themselves under `audit_evidence_claims/m9/attacks/`. No application code or earlier audit artifact was changed.
