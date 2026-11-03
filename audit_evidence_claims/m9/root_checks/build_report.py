"""Assemble the review, retaining every historical finding as an individual row."""
from pathlib import Path

OUT = Path(__file__).resolve().parent.parent
header = r'''# Independent relation-map review - round 9

Reviewed **`3a362eb4f156ea252301d18507ff0a733d0b601e`**, 2026-11-03 KST, against the supplied round-9 design and original approval bar. **Approval is blocked by reproducible originator leaks that every refusal stage misses.** All seven named M8 findings are fixed for their exact inputs. Four different standalone stored aliases now lose their correct drug maps.

No tracked file was edited. All new scripts, fixtures, logs and this report are under `audit_evidence_claims/m9/`; the pre-existing `brief.md` was preserved. Known **M5-S2** and the stated same-item over-refusal policy are accepted. A correct graph around the wrong selected molecule still fails the approval bar.

## Verification and limits

- **336 passed in 23.63 s**, exit 0: `python -m pytest tests -q -p no:cacheprovider`, with bytecode disabled and temporary files under m9. [Output](root_checks/pytest.txt), [environment/hashes](root_checks/pytest_summary.json).
- Reused all earlier finding reproducers, relocating outputs and owned ports. Root's six inherited HTTP runners and four M6 runners all exit 0; the original M1 HTTP cases, seven original QA demos and M8's 57-request confirmation are included. [Reuse manifest](root_checks/reuse_manifest.json), [six runners](root_checks/execution_http.json), [four runners](root_checks/execution_m6_http.json), [M8 HTTP](root_checks/new_http.json).
- Historical naming coverage includes **13 core scripts, six supplements, all five original M1 name scripts, 113 attack cases and 7,511 unique alias keys**, plus the frozen **1,648-question** no-relink counterfactual. The literal old alias sweep now finishes without the old cache crash. Known obsolete harness calls use the documented M8 adaptations; inert old monkey-patches are not used as evidence for current no-relink behavior. [Name report](names/FINDINGS.md), [manifest](names/reuse_manifest.json), [execution](names/round9_execution.json).
- Reused the distinct M7 attack script: **93 inputs / 10 QA / 44 HTTP requests**. Reused the M8 attack script: **174 inputs / 8 QA**, all **26 Unicode Pd** characters, plus **16 alias/control HTTP requests**. [M7](names/m7_attacks/fresh_results.json), [M8](names/attacks/probe_results.json), [aliases](names/alias_checks/new_http.json).
- Independent graph oracle: **6,469 live centres, 22 relation/direction/type/role combinations, zero errors**. **19/19 DB assertions** pass, including live trial counts, retired endpoints, malformed props, unknown counts, exact score precision and the 1,001-drug chunking fixture. [Oracle](db_ui_cost/db_validate.json), [assertions](db_ui_cost/db_assertions.json).
- **24/24 UI assertions**, all **36 demo callbacks plus six map callbacks** pass. All **36 complete demo responses equal M7 and M8**; all **36 original-CLI HTTP demo responses return 200 and equal direct Engine output**. [DB/UI/demo/cost report](db_ui_cost/FINDINGS.md).
- Fresh attacks cover **146 inputs / 16 QA**, **50 corrected actual HTTP requests**, and ten exact predecessor-query comparisons. Records include resolver output, normalized input, resolver veto, item linker, whole-name result, public linking and map output. An initial wrong QA payload key was a harness error, preserved and corrected before the full rerun; it is not an application finding. Root independently confirmed **54 additional actual HTTP responses** with the original CLI server. [Fresh attacks](attacks/FINDINGS.md), [adaptation](attacks/adaptation.json), [independent HTTP](root_checks/independent_http.json), [lifecycle](root_checks/independent_lifecycle.json).
- UI checks execute actual page JavaScript in a Node VM with controlled DOM/fetch stubs. They verify generated markup, callbacks and stale-response behavior, not browser paint or real-browser exploitation. Served HTML was byte-identical to the worktree. Port 8765 was not used. No clinical interpretation or external pharmacology assumption is needed for the findings below: the repository's own suffix/isotope rules and stored identities supply the controls.

## Blocking findings

### M9-B1 - P1: positive name normalization remains broader than every refusal stage

Exact request: `POST /api/explore` with `{"text":"bevacizumab_awwb"}`.

Actual HTTP 200 draws **BEVACIZUMAB / CHEMBL1201583 / 122 trials**, with no refusal. `bevacizumab__awwb` does the same. The ASCII-hyphen control `bevacizumab-awwb` is correctly refused. `bevacizumab_awwb, osimertinib` still selects the forbidden BEVACIZUMAB centre; the separate valid drug does not authorize that identity.

| Stage | `bevacizumab_awwb` |
|---|---|
| Raw resolver | ALIAS to CHEMBL1201583, no refusal |
| `_resolver_blocked(_fold(text))` | `{}` |
| `_link(_fold(text))` | Drug CHEMBL1201583, no Refused entry |
| `_whole_name(...)` | `None`, supplying no veto |
| Public map / trial QA | Originator map / 12 originator evidence rows |

`Which trials evaluate bevacizumab_awwb?` returns 12 originator rows over HTTP. The hyphen control returns zero. [Independent responses](root_checks/independent_http.json), [stage matrix](attacks/probe_results.json), [additional HTTP](attacks/http_results.json).

**Cause:** the new punctuation fold at **`src/query.py:114-118`** uses `[^\w\s]+`; underscore is a word character in this regex, although Unicode classifies it as connector punctuation. It therefore remains unchanged. The suffix predicate is narrower (`src/textrules.py:156-157`), while the positive key **removes underscore** (`src/textrules.py:339-346`). The key retrieves the stored alias `Bevacizumab awwb`, and `_link` accepts it (`src/query.py:339-354`). Returning no whole-name match is not a refusal (`src/query.py:160-165`). `awwb` is explicitly a known biosimilar suffix in `src/textrules.py:169-173`.

The same representation mismatch also admits **`bevácizumab-awwb`** (U+00E1, and its decomposed equivalent): the guard sees an accented letter outside its ASCII stem pattern, but `canonical_key` removes the accent and accepts the blocked name. Exact predecessor comparisons show these are **newly reported inherited holes**, not a claim that M8's exact repaired input regressed. Additional dotted-suffix variants are retained in the attack evidence, without claiming an exhaustive Unicode proof. [Predicate details](attacks/predicate_details.json), [predecessor comparison](attacks/predecessor_results.json).

**Required outcome:** punctuation/character equivalences that recover a known refused product must not recover its originator through a more permissive positive key. Preserve the bare originator and separately listed valid-drug controls.

### M9-B2 - P1: the punctuation-folded isotope is never checked as an isotope label

**`[89.Zr] trastuzumab`** and **`89:Zr trastuzumab`** each return HTTP 200, **TRASTUZUMAB / CHEMBL1201585 / 13 trials**, no refusal. Both trial questions return **12 originator evidence rows**. Controls `89-Zr trastuzumab`, `[89 Zr] trastuzumab` and `[89Zr] trastuzumab` refuse; bare `trastuzumab` works. [Independent HTTP](root_checks/independent_http.json), [all stages](attacks/probe_results.json).

After edge stripping (`src/query.py:257-260`), the item begins `89.Zr` or `89:Zr`. Its punctuation-folded form is `89-Zr trastuzumab`. `is_isotope_label("89-Zr")` is true under **`src/textrules.py:289-298`**, and the literal folded control is refused. But the folded variant at **`src/query.py:117-118`** reaches only `is_distinct_product` / `is_radiotracer`; **the one- and two-word isotope tests at `123-126` see only the original words**. The narrower full-tracer predicate does not recognize this unbracketed, space-separated form. Positive alias matching erases the punctuation and recovers the stored `89zr-trastuzumab` alias as the unlabelled molecule (`src/textrules.py:339-346`, `src/query.py:339-354`).

The raw resolver, resolver veto and item linker all miss the refusal; whole-name fallback supplies no veto. This is an inherited input hole still present after M8, and violates the added requirement to run the item guards on the punctuation-folded item. [Predicate evidence](attacks/predicate_details.json), [predecessor evidence](attacks/predecessor_results.json).

**Required outcome:** apply the complete item refusal policy, including isotope-label checks, to the permitted folded representation before accepting an originator identity.

### M9-B3 - P1: a known suffix without a hyphen is accepted as the originator alias

**`bevacizumab awwb`** and **`bevacizumab (awwb)`** return HTTP 200, **BEVACIZUMAB / CHEMBL1201583 / 122 trials**, with no refusal. Both trial questions return **12** originator rows. The exact repaired `bevacizumab-(awwb)` and ordinary `bevacizumab-awwb` controls refuse. [Independent HTTP](root_checks/independent_http.json).

The stored alias `Bevacizumab awwb` itself points to the originator ID. The suffix policy recognizes `awwb` but only when the pattern includes a hyphen (`src/textrules.py:156-157,169-173`). Spaces are deliberately preserved by the new punctuation fold (`src/query.py:118`), while edge wrappers are stripped (`257-260`). Thus all refusal stages miss the product distinction; the whole-name shortcut can also return Drug for the exact spaced stored alias (`229-239`). A dictionary hit does not establish product identity when the same suffix is expressly rejected in the control spelling.

This is a **newly reported inherited hole**, distinct from M8-B2's now-fixed interior-wrapper-with-hyphen reproduction. The current design's stored-name tracer exception does not authorize treating this known biosimilar suffix as the original molecule. [Stage and predecessor evidence](attacks/FINDINGS.md).

**Required outcome:** known suffix product names must not draw originator edges merely because they are stored without a hyphen or surrounded by whitespace-separated wrappers.

## Earlier findings - individual FIXED / NOT FIXED dispositions

The **62 carried-forward rows remain 54 FIXED / 8 NOT FIXED** for their exact reproductions. Adding the seven M8 findings below yields **69 rows: 61 FIXED / 8 NOT FIXED**. These counts include repeated qualifications, not 69 independent defects. M2 stopped without a REPORT; its partial role/order fixtures and completed M2b report are covered. Current re-execution, not the previous report's verdict, supplies the dispositions. [Machine-readable matrix](names/historical_findings_matrix.json).

'''

footer = r'''
### M8

| Finding / exact reproduction | Round 9 disposition |
|---|---|
| M8-B1 `[89 Zr] trastuzumab`, tab/newline/NBSP between mass and element | **FIXED** - no centre; trial/sponsor QA zero. Recorded `radiotracer_guard` honored at `src/query.py:204-207`; two-word labels checked at `125-126`. [Replayed stages](names/attacks/probe_results.json), [HTTP](root_checks/new_http.json). |
| M8-B2 `bevacizumab-(awwb)`, `bevacizumab-[awwb]`, separate-osimertinib variant | **FIXED** - product refused; separate OSIMERTINIB survives; qualified-product QA zero. `src/query.py:114-118`. [Stages](names/attacks/probe_results.json), [HTTP](root_checks/new_http.json). |
| M8-B3 U+2E3A `bevacizumab⸺awwb`; all 26 Unicode Pd characters | **FIXED** - all 26 fold to hyphen and refuse; no originator centre. `src/query.py:101-106`. [All Pd results](names/attacks/unicode_dashes.json), [HTTP](root_checks/new_http.json). |
| M8-S1 4,097th cache entry; original 7,511-key alias sweep | **FIXED** - 82 successful requests fill 4,096 distinct pieces; first `osimertinib` and retry both HTTP 200 / CHEMBL3353410 / 79 trials. Original and adapted alias sweeps finish without cache errors. `src/query.py:187-195`. [Natural HTTP](db_ui_cost/cache_boundary_http.json), [name runs](names/round9_execution.json). |
| M8-S2 `biosimilar, and osimertinib`, `biosimilar; and osimertinib`, `biosimilar and, osimertinib` | **FIXED** - all preserve CHEMBL3353410; the first comma-and form has 12 trial and 12 sponsor QA rows. Carry now requires equal comma/semicolon clause IDs at `src/query.py:300-302`. [HTTP](root_checks/new_http.json), [replayed stages](names/attacks/probe_results.json). |
| M8-S3 `566C`, `9-ac`, `5ac` | **FIXED** - correct CHEMBL1450 / CHEMBL274070 / CHEMBL1489, HTTP 200. `src/query.py:122,196-209`. [Alias HTTP](names/alias_checks/new_http.json). |
| M8-S4 `5.BETA.,20-EPOXY-1,2.ALPHA.,4,7.BETA.` | **FIXED** - PACLITAXEL / CHEMBL428647, HTTP 200. Stored/input punctuation stripped symmetrically at `src/query.py:229-235`. [Alias HTTP](names/alias_checks/new_http.json). |

## Should-fix findings, separate from originator blockers

### M9-S1 - P2, new regressions: four exact standalone stored aliases are now refused

| Exact input | Correct stored drug | Current HTTP result |
|---|---|---|
| `Trastuzumab--vcmmae conjugate` | TRASTUZUMAB VEDOTIN / CHEMBL5315030 | 200, Refused, no centre |
| `Theophylline in dextrose 5% in plastic container` | THEOPHYLLINE / CHEMBL1355736 | 200, Refused, no centre |
| `40-o-(2-hydroxyethyl)-rapamycin` | EVEROLIMUS / CHEMBL1908360 | 200, Refused, no centre |
| `42-o-(2-hydroxyethyl)rapamycin` | EVEROLIMUS / CHEMBL1908360 | 200, Refused, no centre |

Each is an exact unique dictionary alias supplied alone. The exact M8 query module (`ec4eede`), loaded with the same app/rules/data, draws its correct live Drug; preferred-name/ID controls still work. The exact old set of **19 non-M5-S2 lost aliases remains repaired**; these are four other inputs. [Stored identities, old/current stages and ten HTTP requests](names/new_alias_confirmation.json), [independent confirmation of the first three](root_checks/independent_http.json), [old 19 check](names/historical_alias_set_check.json).

For the ADC, punctuation collapse turns the truncated word window into `Trastuzumab-vcmmae`, firing the generic suffix guard. For the chemical-locant names, collapse creates a tracer-like prefix. For theophylline, edge stripping removes `%` (`src/query.py:257-260`), and the new adjacent-word isotope rule reads **`5 in`** as mass/element (`125-126`). All four complete raw spellings have false raw distinct-product/radiotracer predicates; the new item checks create the refusal. The `42-o...` form additionally triggers a recorded resolver tracer veto after cleaning; the item refusal independently suffices. Whole-name recovery then exits because `found` contains Refused (`227-228`). The resolver exception at `196` covers only pieces tokenized as one word, not these complete stored names.

These losses fall outside the user's intended over-refusal allowance because the valid named drug is alone in its item. Preserve its stored ID without weakening the product/tracer controls. The larger alias sweep contains additional isotope/product-bearing names; they are retained in raw evidence but not all asserted to be defects. M5-S2 remains the accepted known exception.

## Demos and cost

All seven original QA demos retain evidence counts **12, 12, 11, 1, 12, 0, 0**. Six complete responses equal original `bfcb83d`; Mvasi differs only in refusal metadata. All 36 page-demo responses equal both M7 and M8. [Original QA comparison](root_checks/http_demo_results.json), [page comparison](db_ui_cost/demo_previous_comparison.json), [actual HTTP demos](db_ui_cost/demo_http.json).

The last timing interval ran after root/name workloads completed and the attack worker paused. Other host activity was uncontrolled; these are observations, not performance guarantees. The old comparator is exact `9bd7cb4` query code with current shared data/rules.

| Exact workload | Observed result |
|---|---|
| Link `';'.join(['x']*2000)`, 3,999 characters, three-sample median | old M7 **1.795619 s**; current **0.152050 s** |
| HTTP `/api/check`, question EGFR, same repeated-x answer | **0.395786 s**, HTTP 200 |
| Ordinary EGFR map queued behind that check | **0.313302 s**, HTTP 200; later ordinary map **0.020716 s** |
| `';'.join(f'isa x{i:04d}' for i in range(400))`, 3,999 chars, cold HTTP check | **3.110653 s**, HTTP 200 |
| Ordinary EGFR map queued behind the cold distinct-piece check | **3.051145 s**, HTTP 200 |
| Same distinct-piece check with warm cache | **0.692193 s**, HTTP 200 |

The original repeated-piece defect is repaired. Instrumentation gives **400 cold / 0 warm resolver calls** for distinct drug pieces, **1 / 0** for repeated drug pieces and **0** for non-drug pieces. Unique legal inputs still hold the shared engine lock for seconds (`src/app.py:247-263`). This is a residual cost qualification, not an established new regression, timeout or deadlock. The cache rollover exception is separately repaired. [Full cost evidence and commands](db_ui_cost/FINDINGS.md), [isolated repeated HTTP](db_ui_cost/isolated_fresh_cost_http.json), [distinct HTTP](db_ui_cost/isolated_unique_cost_http.json).

Disease returns **2,774 Trials + 300 Targets**, 30 from each group, **18,575 bytes in 74.443 ms**. The inherited **24-request / 12-worker** concurrency workload returns expected HTTP 200 shapes in **803.993 ms**. These ordinary measurements overlapped other audit work. [HTTP results](root_checks/http_results.json).

## Standards, integrity and remaining boundaries

No repository AGENTS/CONTRIBUTING/CODING_STANDARDS source was found. The supplied review and no-tracked-edit instructions govern. No application code was changed, so the conditional KOA Studio / KhOpenApi before/after-code comparison does not apply.

The DB snapshot contains **7 retired nodes, 142 retired edges, no self-loops and no live edge with a retired endpoint**. No additional wrong live-edge relationship, direction wording, stored field value, cut notice or generated-markup injection was established in the exercised paths. The refusal guarantee at `src/app.py:74-76` and the UI's product-refusal behavior at `web/try.html:215` remain unfulfilled for M9-B1-B3.

Application QA uses `use_llm=False` (`src/app.py:180-181`); no model was called. DB mutations used isolated fixtures. The application does not globally open SQLite read-only, so this review's no-write conclusion rests on executed paths and hashes rather than a database-permission guarantee.

Final HEAD, tracked/staged diffs, SHA-256 comparison of every initially present tracked file, database hash, owned-port closure and report links are recorded in [integrity_final.json](integrity_final.json). DB SHA-256: `7341c5a7089731f67356da5a588b269d4b69e8e6c4c054acf19aa4ef2837b529`.

Reproduce from the repository root with bytecode disabled. Keep runners that share a port sequential; worker manifests state path/port/instrumentation adaptations.

```text
python -B audit_evidence_claims/m9/root_checks/run_replays.py tests
python -B audit_evidence_claims/m9/root_checks/run_replays.py http
python -B audit_evidence_claims/m9/root_checks/run_m6_http.py m6_http
python -B audit_evidence_claims/m9/root_checks/new_http.py
python -B audit_evidence_claims/m9/root_checks/independent_confirm.py
python -B audit_evidence_claims/m9/names/run_round9.py
python -B audit_evidence_claims/m9/names/m7_attacks/fresh_probe.py
python -B audit_evidence_claims/m9/names/new_alias_confirmation.py
python -B audit_evidence_claims/m9/db_ui_cost/run_db.py
python -B audit_evidence_claims/m9/db_ui_cost/run_ui.py
python -B audit_evidence_claims/m9/attacks/probe.py
python -B audit_evidence_claims/m9/attacks/http_probe.py
```

VERDICT: CHANGES REQUIRED
'''

tables = (OUT / 'root_checks/historical_tables.md').read_text(encoding='utf-8')
(OUT / 'REPORT.md').write_text(header + tables + footer, encoding='utf-8')
print('Wrote', OUT / 'REPORT.md')
