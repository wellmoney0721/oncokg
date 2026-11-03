# Round 19 attacks and specification review

HEAD `c476d9d559ce5e723c6f5d91fad5e6c3599cfe93`; query-only counterfactual `4bed79c1f170ebe1efa3d452ce4398cce17b2113`.

**Two P1 originator leaks remain after the Round 18 repair.** Both pass every refusal stage and the actual HTTP endpoint. Both also occur with the previous query module; they are inherited holes rather than demonstrated regressions introduced by this commit. Exact M18-B1 inputs now refuse (the historical-name reviewer supplies the exhaustive prior-finding matrix).

## M19-B1 — P1: hyphenated radio-labelling words still draw the originator

Exact input: **`radio-labelled trastuzumab`**. `POST /api/explore` returns HTTP 200 with **TRASTUZUMAB / CHEMBL1201585**, **13 trials**, and no refusal. `Which trials evaluate radio-labelled trastuzumab?` and `Who sponsors trials of radio-labelled trastuzumab?` each return **12 originator evidence rows**. Removing only the hyphen, producing `radiolabelled trastuzumab`, returns a refusal and zero QA evidence.

This is an ordinary spelling of a tracer description, not a contrived isotope spelling: a primary experimental article develops and evaluates isotope-labelled trastuzumab and uses the exact phrase “radio-labelled trastuzumab” in its Discussion. [Lub-de Hooge et al., Preclinical characterisation of 111In-DTPA-trastuzumab](https://pmc.ncbi.nlm.nih.gov/articles/PMC1575276/). The article supports the terminology and tracer/originator distinction; it does not supply graph evidence or a clinical recommendation.

| Stage | `radio-labelled trastuzumab` | `radiolabelled trastuzumab` |
|---|---|---|
| Intervention resolver | CONTAINED_ALIAS + UNRESOLVED, no BLOCKED | CONTAINED_ALIAS + UNRESOLVED, no BLOCKED |
| `_resolver_blocked` | `{}` | `{}` |
| `_qualified` | false | false |
| `_item_has_isotope` | false | true |
| Actual `_marked` call | `None`; both tokens in segment 0 | refusal |
| `_whole_name` | `None` | `None` |
| Public linker | Drug TRASTUZUMAB, no Refused | Refused only |
| HTTP map | CHEMBL1201585, 13 trials | refused, no centre |
| Trial / sponsor QA | 12 / 12 | 0 / 0 |

**Cause:** `src/query.py:177-179` splits the phrase into alphanumeric words and tests each word independently for membership in `_LABEL_WORDS` or a `radiolabel`/`radioiod` prefix. The hyphenated word becomes `radio`, `labelled`; neither passes. The earlier patterns in `src/textrules.py:306-318` recognise isotope-symbol syntax, not this word. The resolver records no BLOCKED component (`src/query.py:303-343`), `_qualified` misses it (`src/query.py:232-256`), and the item-wide check in `_marked` is false (`src/query.py:423-425`). `Engine.explore` selects the surviving positive hit (`src/app.py:88-95`). The new test only checks joined `radiolabelled` (`tests/test_app.py:428-440`).

**Corroborating exact inputs:** `radio-labeled trastuzumab`, `radio labelled trastuzumab`, `radio‑labelled trastuzumab` (U+2011), `radio_labelled trastuzumab`, `RADIO-LABELLED TRASTUZUMAB`, `trastuzumab (radio-labelled)`, `trastuzumab radio-iodinated`, `trastuzumab radio-tracer`. These all draw the originator, while their joined control spellings refuse. `radio-labelled Herceptin`, `radio-labelled vinblastine`, and `radio-labelled erlotinib` show the same guard failure across aliases/drugs. They are common-cause software probes; no claim is made that every synthetic descriptor denotes a marketed product.

The same new lexical check is incomplete for ordinary morphology: `trastuzumab radioactively labelled`, `radioconjugated trastuzumab`, `trastuzumab radioimmunoconjugates`, and `trastuzumab radiopharmaceuticals` survive, while `trastuzumab radioactive label` and `trastuzumab radiopharmaceutical` refuse. These are corroborations of incomplete labelling-word recognition, not separate counted blockers.

## M19-B2 — P1: mass-first metastable full element name bypasses the reverse-order rule

Exact input: **`trastuzumab labelled with 99m-technetium`**. The HTTP map again selects CHEMBL1201585 with 13 trials and no refusal; trial and sponsor QA each return 12 originator evidence rows. Change only the isotope spelling to `technetium-99m` or `99mTc`: the map refuses and both QA evidence arrays are empty. `99m-technetium trastuzumab`, `99m technetium trastuzumab`, and the fused `technetium99m trastuzumab` also survive. The direct paired case is the explicit labelled product, not a drug merely mentioned alongside a separate isotope.

Tc-99m-labelled trastuzumab is an actual radiopharmaceutical research product: the original RP-39 abstract reports its preparation via DTPA for imaging. [Bhusari et al., Radiopharmacy RP-39](https://pmc.ncbi.nlm.nih.gov/articles/PMC3868035/). The equivalence of the tested isotope notations is the reviewer's inference from that identity and the application's own accepted/refused controls.

**Cause:** the general two-order element-name loop requires `num.isdigit()` (`src/query.py:181-185`), so `99m` is rejected as a mass. Its special exception checks only `a == "technetium" and b in ("99m", "99")` (`src/query.py:186-187`); the reversed order is never tested. The symbol guards do not convert the full element name. `_qualified == false`, `_resolver_blocked == {}`, `_item_has_isotope == false`, actual `_marked == None`, `_whole_name == None`, and the public linker has a positive Drug and no Refused. Thus this is a second concrete failure mechanism within the new helper.

**Required behaviour for both blockers:** recognise equivalent explicit labelling descriptions consistently with their refused controls; no unlabelled TRASTUZUMAB map or originator QA evidence may survive. No application repair was made.

## Should-fix and additional observations

- **M19-S1, new over-refusal:** `non-radiolabelled trastuzumab` now refuses, whereas HEAD^ and current `unlabelled trastuzumab` draw TRASTUZUMAB. Splitting the `non-` prefix leaves a matching label word, without negation handling. This is a new recall regression, not an originator-leak blocker, and is distinct from the user's previously accepted over-refusals.
- Full element names fused to mass remain unrecognised in several ordinary compact renderings: `iodine124 trastuzumab`, `trastuzumab iodine124`, `zirconium89 trastuzumab`, `89zirconium trastuzumab`. Their hyphenated controls refuse. Recorded as supplements; B1/B2 suffice for rejection.
- `tritiated FDG` and `FDG labelled with carbon-14` select the already-labelled F18 preferred product despite `_item_has_isotope == true`. This extends the previous isotope-compatibility concern in m18; no independent product-identity proof is supplied here, so it is not promoted to another blocker.
- Ordinary controls `trastuzumab`, `osimertinib 80 mg`, `paclitaxel 2 cycles`, and `lead compound osimertinib` remain available. The intended labelled-product control `fluorine-18 fluorodeoxyglucose` still selects FLUDEOXYGLUCOSE F 18. Broader demo and cost checks belong to the other reviewers.

## Specification review (under 400 words)

Specification source: the user's Round 19 brief and original guarantee 3 / approval bar: “a refused product drawn as the originator” is a blocker. Diff reviewed: `git diff 4bed79c1f170ebe1efa3d452ce4398cce17b2113...HEAD -- src tests`.

**Two P1 failures.** (1) `radio-labelled trastuzumab` is a published ordinary tracer description, but every guard misses the separated label word (`src/query.py:177-179`); actual HTTP draws CHEMBL1201585 with 13 trials, and trial/sponsor questions each return 12 originator evidence rows. The joined `radiolabelled` spelling refuses. (2) `trastuzumab labelled with 99m-technetium` produces the same wrong map and evidence; reversing the isotope to `technetium-99m` refuses. The full-element loop rejects `99m` as nonnumeric and handles the special metastable form in only one order (`src/query.py:181-187`).

The exact repair examples are fixed. Both new holes reproduce on HEAD^ with current data/app modules; neither is claimed as a newly introduced originator regression. New `non-radiolabelled trastuzumab` refusal is a separate should-fix recall regression. No scope-creep finding is identified. Known over-refusals and bevacizumab biosimilar-code curation do not determine these findings.

Specification: **2 P1 findings; CHANGES REQUIRED.**

## Evidence and reproducibility

- [82 exact inputs](new_cases.json), [initial 57-case scan](initial_scan.json).
- [Full current/HEAD^ stage pairs](new_results.json), [compact summary](new_summary.json), [key-stage extraction](key_evidence.json).
- [328 actual HTTP requests and responses](new_http.json), [server lifecycle](new_lifecycle.json), [final assertions and hashes](final_checks.json).
- [Reuse manifest](reuse_manifest.json), [primary sources](sources.json).

`new_probe.py` and `new_http.py` reuse the m18 attack harnesses. Adaptations: new exact input list, counterfactual module label, and owned port 19193. Output paths follow each script's location. Run `python -B audit_evidence_claims/m19/attacks/new_probe.py` then `python -B audit_evidence_claims/m19/attacks/new_http.py`. All 82 current/HEAD^ pairs complete; all 328 HTTP responses are 200; the server's owned port closes, the served page equals the worktree, and the database SHA-256 remains unchanged. Direct probes use SQLite read-only connections. Query-only comparisons are not full historical deployments. QA uses the application's no-model path. Timings overlap other work and are not cost benchmarks. All writes are under m19/attacks; no tracked file was modified.
