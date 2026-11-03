"""Assemble current evidence and individually reverified historical dispositions."""
from pathlib import Path
import re

OUT = Path(__file__).resolve().parent.parent
ROOT = OUT.parents[1]
previous = (ROOT/'audit_evidence_claims/m9/REPORT.md').read_text(encoding='utf8')
tables = previous[previous.index('### M1\n'):previous.index('## Should-fix')]
tables = tables.replace('db_ui_cost/', 'db_ui/')
for name in ['perf_current.json', 'cost_stress.json', 'cache_boundary_http.json']:
    tables = tables.replace('db_ui/'+name, 'cost/'+name)
tables = tables.replace('db_ui/isolated_fresh_cost_comparison.json', 'cost/fresh_cost_comparison.json')
tables = tables.replace('db_ui/isolated_fresh_cost_http.json', 'cost/fresh_cost_http.json')
tables = tables.replace('names/round9_execution.json', 'names/round9_execution.json')
tables = tables.replace('Round 9 disposition', 'Round 10 disposition')
tables = tables.replace('Four additional standalone stored-alias regressions are reported below.',
                        'M9-S1 is individually classified below; its three accepted over-refusals remain.')
tables = tables.replace('`src/query.py:204-207`; two-word labels checked at `125-126`',
                        '`src/query.py:214-219`; adjacent alnum labels checked at `248-255`')
tables = tables.replace('`src/query.py:114-118`', '`src/query.py:125-138`')
tables = tables.replace('`src/query.py:101-106`', '`src/query.py:100-117`')
tables = tables.replace('`src/query.py:187-195`', '`src/query.py:197-205`')
tables = tables.replace('`src/query.py:300-302`', '`src/query.py:337-339`')
tables = tables.replace('`src/query.py:122,196-209`', '`src/query.py:206-219,248-252`')
tables = tables.replace('`src/query.py:229-235`', '`src/query.py:266-271`')

header = r'''# Independent relation-map review — round 10

Reviewed **`c364c84a289cfc3da5981708db3547ff6c752bde`**, 2026-11-03 KST. **Changes required:** every previously reported originator-blocking reproduction is now fixed, but four independently reproduced name-resolution defect families remain: **two regressions introduced by the latest query change and two inherited holes**. A map can contain entirely genuine graph edges and still be wrong because it selected a molecule the qualified input does not name.

No tracked file was edited. All new scripts, fixtures, logs and this report are under `audit_evidence_claims/m10/`. The explicitly accepted M5-S2, two hydroxyethyl rapamycin forms and `Trastuzumab--vcmmae conjugate` over-refusals are **not blockers**.

## Verification and evidence limits

- **337 passed in 28.38 s**, exit 0, using `python -m pytest tests -q -p no:cacheprovider`, bytecode disabled and temporary files under m10. [Output](root_checks/pytest.txt), [environment and hashes](root_checks/pytest_summary.json).
- Reused the six historical root HTTP runners, four M6 HTTP runners, M8's 57-request confirmation, and M9's 54-request independent confirmation; all exit 0. Port-sharing runners ran sequentially. [Manifest](root_checks/reuse_manifest.json), [six runners](root_checks/execution_http.json), [M6](root_checks/execution_m6_http.json), [M8/M9](root_checks/execution_extra.json).
- Historical naming: **37 leaf scripts**, including all five exact M1 scripts, the **113-case / 7,511-key** sweep, M7's **93 inputs / 10 QA / 44 HTTP** cases, M8's **174 inputs / 8 QA** including all **26 Unicode Pd** characters, and M9's **146 inputs / 16 QA / 50 HTTP** cases. The old alias sweep finishes without cache errors. [Name report](names/FINDINGS.md), [reuse manifest](names/reuse_manifest.json), [50 name-related dispositions](names/historical_name_dispositions.json).
- The frozen **1,648-question** no-relink counterfactual has **64 identical / 1,560 entity-metadata-only / 24 semantic differences / 0 errors**. Its inherited adaptation patches current `_link`; obsolete old monkey-patches are not used as current behavioral evidence. [Result](names/adapted_frozen_qa_relink_sweep.json).
- Independent graph oracle: **6,469 live centres, 22 relation/direction/type/role combinations, zero errors**. All **19 DB assertions** and **24 UI assertions** pass, including live/retired counts, missing/malformed props, exact score values, 1,001-drug chunking, ordering, cut notices, escaping, trail clearing and stale-response suppression. [DB/UI report](db_ui/FINDINGS.md), [oracle](db_ui/db_validate.json), [DB](db_ui/db_assertions.json), [UI](db_ui/ui_assertions.json).
- All **36 page demos plus six map callbacks** pass; all **36 complete demo responses equal m7, m8 and m9**. All 36 original-CLI HTTP demo requests are 200 and equal direct Engine responses. The seven original QA demo evidence counts remain **12, 12, 11, 1, 12, 0, 0**; six full responses match original `bfcb83d`, with only Mvasi refusal metadata changed. [Demos](db_ui/demo_previous_comparison.json), [HTTP](db_ui/demo_http.json), [original comparison](root_checks/http_demo_results.json).
- Fresh attack sweep: **1,224 inputs**, recording raw resolver, resolver veto, item linker, whole-name shortcut, public linker and map. **35 focused inputs** compare exact parent `3a362eb` and current query modules against the same current app/rules/database. These are query-module counterfactuals, not a reconstructed old deployment. Root separately confirms **95 actual HTTP responses** using the original `src/app.py` CLI. [Attack report](attacks/FINDINGS.md), [sweep](attacks/probe_results.json), [parent comparison](attacks/focus_results.json), [57 HTTP responses](root_checks/candidate_http.json), [38 HTTP responses](root_checks/isotope_http.json).
- UI tests execute actual page JavaScript in a Node VM with controlled DOM/fetch stubs. They establish generated markup and callback/state behavior, not browser paint or browser-executed XSS. Original-CLI HTTP served bytes match `web/try.html`. No server used port 8765. Findings below use the repository's own isotope/product predicates, dictionary identities and controlled spellings; they do not require external clinical assumptions.

## Blocking findings

### M10-B1 — P1, new regression: a stored alias absorbs its trailing isotope

Exact request: `POST /api/explore` with `{"text":"A33 124i"}`.

**Actual:** HTTP 200, **ADAKITUG / CHEMBL5314551**, no refusal. Its map draws the stored **ACTS_ON → CXCL8 (ENSG00000169429), INHIBITOR** edge. The centre has **0 trials**; trial and sponsor QA both have zero evidence, so this is not a claim of invented trial rows. The dictionary records `A33 124i` as an alias of the unlabelled ADAKITUG antibody. The repository identifies `124i` as an isotope (`src/textrules.py:289-298`). Exact parent query code refused this input. [Independent HTTP](root_checks/candidate_http.json), [dictionary, stages and predecessor](attacks/focus_results.json).

| Current stage | `A33 124i` result |
|---|---|
| Raw resolver | ALIAS → CHEMBL5314551 |
| Resolver veto | `{}` |
| Item/public linker | Drug ADAKITUG, no Refused |
| Whole-name shortcut | Drug ADAKITUG |
| Map | ADAKITUG with its CXCL8 relation |

**Cause:** `_marked` computes `own = ["A33", "124i"]`, but checks only `own[:1]` and `own[:2]`, not the trailing isotope (`src/query.py:248-252`). The accepted match already consumed `124i`, so it is no longer in the adjacent `nxt` words. The whole-name shortcut receives no veto and accepts the same stored alias (`258-275`). This recreates the stored tracer-alias risk explicitly discussed in the round-9 repair note without adding an explicit exemption.

Controls/variants: `A33 124 i`, `A33 [124i]`, and `A33 124-I` also select ADAKITUG; preferred name `ADAKITUG` correctly remains available. `124i A33` is **not_found**, not a successful refusal control. Do not generalize this finding to every restored isotope-bearing stored name: several other names identify an explicitly labelled drug node themselves.

**Required outcome:** an isotope at the end of an accepted stored alias must not disappear from the refusal decision merely because the positive matcher consumed it.

### M10-B2 — P1, new regression: an isotope token is substituted for the named substance

Exact input **`18F fluorothymidine`** returns HTTP 200, **FLUDEOXYGLUCOSE F 18 / CHEMBL2030434 / 1 trial**, no refusal. Trial QA returns its **NCT00923273** evidence row; sponsor QA has one row. **`18F nonexistingdrug`** gives the same map and evidence, proving that recognizing the isotope token alone is sufficient to invent a positive identity for an unknown labelled substance. `18-F fluorothymidine` and `[18F] fluorothymidine` also reproduce. [Independent HTTP](root_checks/isotope_http.json), [full QA/stages](attacks/focus_results.json).

For the unbracketed inputs every refusal stage misses: raw resolver **UNRESOLVED**, veto `{}`, item/public linker matches only **`18F`**, whole-name `None`. The dictionary has a standalone `18f` synonym for fludeoxyglucose; the remainder does not name that molecule. Exact parent query code refused the longer inputs. Both versions permit the lone `18f` alias control, so preserving valid lone-name behavior does not require this regression.

**Cause:** `_marked` excludes any isotope test equal to the matched name itself via **`ws != own`** (`src/query.py:252`) without requiring that token to be alone in its item. The positive matcher then emits it as a Drug (`384-402`). The protection intended for lone isotope-shaped names is thus applied inside a longer product description. Bare `fluorothymidine` is not_found, but prefixing an isotope produces an unrelated positive map.

**Required outcome:** keep supported lone aliases while preventing an isotope word from replacing the unknown or different substance it labels. This is a wrong selected identity, not a fabricated graph edge.

### M10-B3 — P1, inherited hole: punctuation consumes the two-word isotope budget

Exact inputs **`trastuzumab 89 - Zr`** and **`trastuzumab [89 - Zr]`** return HTTP 200, **TRASTUZUMAB / CHEMBL1201585 / 13 trials**, no refusal. Trial QA returns **12** originator rows; direct sponsor QA also returns **12**. `trastuzumab 89 - Zr, osimertinib` still selects TRASTUZUMAB. [Independent HTTP](root_checks/candidate_http.json), [complete stages/QA](attacks/focus_results.json).

Raw resolver accepts the unlabelled drug; resolver veto is `{}`; item/public linker emits Drug without Refused; whole-name is `None`. Controls **`trastuzumab 89 Zr`**, **`trastuzumab 89-Zr`**, and **`trastuzumab [89.Zr]`** refuse. Current prefix **`89 - Zr trastuzumab`** also refuses. These are single-item inputs, with no comma/slash/list-word interpretation needed.

**Cause:** `after` takes only two original whitespace tokens at **`src/query.py:245`**: `89` and `-`. `_alnum_words` removes `-` only afterward (`250`), so `Zr` never reaches the isotope predicate. The promised limit is one or two **alnum words, any separator**, not two raw tokens. The underscore-separator variant also leaks. Parent query code leaks too; this is newly reported inherited incompleteness, not a claim that M9's exact repaired examples regressed.

**Required outcome:** apply the adjacency budget to the normalized alnum words rather than letting punctuation-only tokens exhaust it.

### M10-B4 — P1, inherited hole: normalized multiword product qualifiers still miss every guard

| Exact input | HTTP map | Trial QA evidence | Refusing control |
|---|---|---:|---|
| `generic-version of bevacizumab` | BEVACIZUMAB / CHEMBL1201583 / 122 trials | 12 | `generic version of bevacizumab` |
| `albumin - bound paclitaxel` | PACLITAXEL / CHEMBL428647 / 234 trials | 12 | `albumin-bound paclitaxel` |

Both are HTTP 200 without refusal. Sponsor QA also has 12 rows for each. `generic_version of bevacizumab` and `follow-on-biologic bevacizumab` are additional direct reproductions. Raw resolver, resolver veto and item linker all miss; whole-name supplies no veto. Exact parent query code leaks too. [Independent HTTP and controls](root_checks/candidate_http.json), [stages and parent comparison](attacks/focus_results.json).

**Cause:** `_qualified` retains whitespace or folds punctuation to hyphen (`src/query.py:125-138`), but the underlying patterns require whitespace in `generic\s+version` and `on\s+biologic`, or at most one whitespace/hyphen in `albumin[\s\-]?bound` (`src/textrules.py:142-149`). Thus underscore folding still produces an unrecognized `generic-version`, and spaces around a hyphen defeat `albumin-bound`. The words qualify the same product within one item; this is separate from the accepted list-boundary policy.

**Required outcome:** equivalent separator forms of an explicit product qualifier must preserve refusal before its originator is accepted. Bare molecule and separately listed valid-drug controls must remain distinguishable.

## Earlier findings — individual FIXED / NOT FIXED dispositions

These tables are backed by this round's script executions, not inherited verdicts. The earlier report's table layout is reused for traceability. All original originator-blocking inputs are **FIXED**; continued limitations and accepted over-refusals remain individually **NOT FIXED**. M2 stopped without a REPORT; its partial role/order and name fixtures are included through the completed M2b/cumulative replays. Repeated rows reflect repeated qualifications rather than independent defects.

'''

m9 = r'''### M9

| Finding / exact reproduction | Round 10 disposition |
|---|---|
| M9-B1 `bevacizumab_awwb`, `bevacizumab__awwb`, accented/decomposed `bevácizumab-awwb`, dotted suffix | **FIXED** — exact reported forms refuse; separate osimertinib survives; trial/sponsor QA has no forbidden originator evidence. Guards now use accent/punctuation folding and same-drug suffix keys at `src/query.py:125-138,238-247`. [Exact M9 matrix](names/m9_attacks/probe_results.json), [HTTP](names/m9_attacks/http_results.json), [root confirmation](root_checks/independent_http.json). |
| M9-B2 `[89.Zr] trastuzumab`, `89:Zr trastuzumab`, `89::Zr` variants | **FIXED** — no centre and no trial/sponsor evidence for the exact inputs. `src/query.py:248-255`. M10-B3 is a different whitespace/punctuation-token hole. [M9 stages](names/m9_attacks/probe_results.json), [HTTP](root_checks/independent_http.json). |
| M9-B3 `bevacizumab awwb`, `bevacizumab (awwb)` / `[awwb]`, `trastuzumab dkst` | **FIXED** — known suffix forms refuse, with zero originator QA. `src/query.py:238-247`. [M9 stages](names/m9_attacks/probe_results.json), [HTTP](root_checks/independent_http.json). |
| M9-S1 `Theophylline in dextrose 5% in plastic container` | **FIXED** — correct THEOPHYLLINE / CHEMBL1355736 over HTTP 200. [Alias confirmation](names/new_alias_confirmation.json), [root HTTP](root_checks/independent_http.json). |
| M9-S1 `40-o-(2-hydroxyethyl)-rapamycin` | **NOT FIXED — accepted known over-refusal**, not a blocker. EVEROLIMUS/name ID controls work. [Alias confirmation](names/new_alias_confirmation.json). |
| M9-S1 `42-o-(2-hydroxyethyl)rapamycin` | **NOT FIXED — accepted known over-refusal**, not a blocker. [Alias confirmation](names/new_alias_confirmation.json). |
| M9-S1 `Trastuzumab--vcmmae conjugate` | **NOT FIXED — accepted known over-refusal**, not a blocker. TRASTUZUMAB VEDOTIN and its ID work. [Alias confirmation](names/new_alias_confirmation.json), [root HTTP](root_checks/independent_http.json). |

'''

footer = r'''## Cost, nonblocking qualifications and demos

All prior cost reproductions complete. Final timing runs were sequential after the other audit workers stopped CPU-intensive execution; unrelated host activity remains uncontrolled. These are observed timings, not latency guarantees or proof that the entire linker is linear. [Reuse manifest](cost/reuse_manifest.json), [execution](cost/execution_isolated.json), [instrumented predicates](cost/perf_current.json), [stress cases](cost/cost_stress.json).

| Workload | Current evidence |
|---|---|
| Original M5 plain 250-word / 499-character linker | Median **0.02209 s**; old cubic scan no longer present |
| Original M7 `";".join(["x"]*2000)`, three-sample same-data comparison | `9bd7cb4` **1.83084 s**, current **0.15246 s** |
| HTTP check of that 3,999-character repeated-piece answer | **0.42500 s**, 200; queued ordinary EGFR map **0.34181 s**, 200 |
| 400 distinct drug-bearing pieces, `";".join(f"isa x{i:04d}" for i in range(400))` | Cold HTTP `/api/check` **2.34826 s**, 200; queued EGFR map **2.27624 s**, 200 |
| Same unique-piece HTTP check, warm cache | **0.54082 s**, 200; ordinary map before/after about **0.036 s** |
| Resolver instrumentation | Unique 400 pieces: **400 cold / 0 warm** calls; repeated drug piece: **1 / 0**; unknown pieces: **0** |
| Natural 4,097th-entry cache rollover | **82/82 fill requests HTTP 200**, 4,096 distinct pieces; first osimertinib and retry both **200 / CHEMBL3353410 / 79 trials** |
| Disease ordinary HTTP request | **2,774 Trials + 300 Targets**, 30 per list; **18,575 bytes / 81.395 ms** |
| Historical 24-request / 12-worker HTTP workload | Expected 200 shapes, **677.505 ms** total |

The repeated-piece and cache defects are **FIXED** for their original reproductions. Distinct legal inputs still hold `engine.lock` long enough to queue ordinary maps for seconds (`src/app.py:247-263`); this remains a performance should-fix, not an asserted new regression or deadlock. The ordinary Disease/concurrency timings overlapped initial audit work. [Historical/current comparison](cost/fresh_cost_comparison.json), [repeated-piece HTTP](cost/fresh_cost_http.json), [unique-piece HTTP](cost/isolated_unique_cost_http.json), [resolver counts](cost/unique_piece_cost.json), [cache HTTP](cost/cache_boundary_http.json), [ordinary HTTP](root_checks/http_results.json).

Other unchanged nonblocking limitations are recorded individually above: unsupported lowercase IDs/investigator labels; raw request parser details in controlled 400 errors; blank submission retaining the old view; Infinity fixtures failing closed; the accepted nonparenthetical list-policy consequence; and prefixed questions containing comma-bearing complete aliases. No new demo regression was established. The specified over-refusals were not used to justify the verdict.

## Standards axis

**Zero documented-standards findings.** The separate standards review examined `git diff bfcb83d...HEAD` application changes and the latest query/tests diff. No tracked AGENTS.md, CONTRIBUTING or coding-standards source exists. The user's evidence-based, audit-only constraints govern; no tracked file was edited. The KOA Studio / KhOpenApi original-versus-modified-code requirement is conditional on code changes, so it is not applicable to this independent no-edit review. [Standards review](db_ui/FINDINGS.md#standards-axis).

## Spec axis

**Four blocking defect families:** M10-B1/B2 are new query regressions; M10-B3/B4 are inherited holes. The original name-resolution guarantee and this round's adjacent-alnum isotope design are not met for the exact inputs above. The 6,469-centre oracle establishes stored-edge/value correctness once a centre is selected; it cannot make a wrong selected molecule correct. No additional feature or implementation change was made. [Independent specification review](attacks/FINDINGS.md#spec-axis-under-400-words).

## Integrity and reproduction

The snapshot has **7 retired nodes, 142 retired edges, zero self-loops and zero live edges with retired endpoints**. All six live node types and all 22 existing relation/direction/type/role combinations were exercised. No new wrong direction, stored value, cut notice or generated-markup injection was established. Snapshot self-loop behavior is code-inspected, not an observed real-row test. [Snapshot](db_ui/db_snapshot_facts.json), [oracle](db_ui/db_validate.json).

`Engine.ask` uses `use_llm=False` (`src/app.py:180-181`); no model was called. Fixtures mutate in-memory DB copies. The application does not globally enforce a read-only SQLite handle, so no-write evidence is the executed paths and before/after hashes rather than a database-permission guarantee. Final HEAD, **2,998 tracked-file SHA-256 comparisons**, empty tracked/staged diffs, unchanged DB, report links and owned-port cleanup are recorded in [integrity_final.json](integrity_final.json). DB SHA-256: **`7341c5a7089731f67356da5a588b269d4b69e8e6c4c054acf19aa4ef2837b529`**.

Run from the repository root; output/temporary paths are confined to m10. Port-sharing scripts must remain sequential. Worker manifests record every reused source and adaptation.

```text
python -B audit_evidence_claims/m10/root_checks/run_replays.py tests
python -B audit_evidence_claims/m10/root_checks/run_replays.py http
python -B audit_evidence_claims/m10/root_checks/run_m6_http.py m6_http
python -B audit_evidence_claims/m10/root_checks/run_extra.py
python -B audit_evidence_claims/m10/names/run_round9.py
python -B audit_evidence_claims/m10/names/run_final_replays.py
python -B audit_evidence_claims/m10/db_ui/run_db.py
python -B audit_evidence_claims/m10/db_ui/run_ui.py
python -B audit_evidence_claims/m10/attacks/probe.py
python -B audit_evidence_claims/m10/attacks/focus.py
python -B audit_evidence_claims/m10/root_checks/candidate_confirm.py
python -B audit_evidence_claims/m10/root_checks/isotope_confirm.py
python -B audit_evidence_claims/m10/cost/run_cost.py cache
python -B audit_evidence_claims/m10/cost/run_cost.py isolated
```

VERDICT: CHANGES REQUIRED
'''

(OUT/'REPORT.md').write_text(header + tables + m9 + footer, encoding='utf8')
print('REPORT.md written', (OUT/'REPORT.md').stat().st_size)
