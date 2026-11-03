# Independent relation-map review — round 7

Reviewed HEAD **`9bd7cb4b5d9270bbe99cb5dfec3993502f6b5377`**, 2026-11-03 KST. **Approval remains blocked.** The exact named m1–m6 originator-leak reproductions are repaired, but the new whole-name shortcut bypasses a correct item-linker refusal. Independently, product and tracer spellings still evade **both** refusal paths. The graph, stored-value and demo checks pass; they do not validate the identity selected from a refused product.

No tracked/application file was edited. All new audit files are under `audit_evidence_claims/m7/`. The specified whole-item fail-closed behavior and known M5-S2 are accepted. Whole-input stored-name precedence is evaluated separately from ordinary list parsing.

## Verification and evidence boundaries

- Required suite: **331 passed in 45.74 s**, exit 0, using `python -m pytest tests -q -p no:cacheprovider`. Bytecode disabled; test temporary files confined to m7. [Output](root_checks/pytest.txt), [environment/hashes](root_checks/pytest_summary.json).
- Reused earlier scripts, rather than replacing their cases with new assertions: **13 inherited name scripts**, **six m6 supplements**, **all five original m1 name scripts**, **ten inherited CLI HTTP runners**, and **16 inherited DB/UI commands** completed with exit 0. [Name provenance and coverage](names/REPORT.md), [root copy manifest](root_checks/reuse_manifest.json), [m1–m5 HTTP execution](root_checks/execution_http.json), [m6 HTTP execution](root_checks/execution_m6_http.json), [DB/UI execution](db_ui/execution.json).
- Name coverage includes the earlier **113-case boundary matrix / 7,511 unique alias-key sweep**, the exact m6 **106-input / 8-QA** and **11-input reversed-qualifier** probes, and the frozen **1,648-question** no-relink comparison. The old no-relink patch became inert after the matcher moved to `_link`; a separately recorded mechanical adaptation patches the correct method. It preserves the exact historical inputs and yields **64 identical / 1,560 metadata-only / 24 semantic differences / 0 errors**. These are counterfactual comparisons, not 24 new regressions. [Adaptation and corpus verification](names/REPORT.md#reproduction-completeness).
- **6,469 live centres**, **22 relation/direction/type/role combinations**, **0 stored-row oracle mismatches**; **19/19 DB assertions** and **24/24 UI assertions** pass. Retirement/malformed/numeric mutations use isolated in-memory fixtures. [DB/UI report](db_ui/REPORT.md), [oracle](db_ui/db_validate.json), [DB assertions](db_ui/db_assertions.json), [UI assertions](db_ui/ui_assertions.json).
- **36/36 complete page-demo responses equal m6**; all **36 demo callbacks plus six map callbacks** pass. An additional original-CLI server receives all 36 demo payloads: **36 HTTP 200 / 36 exact response matches**. [Comparison](db_ui/ui_demo_compare.json), [HTTP](db_ui/demo_http.json), [callbacks](db_ui/ui_m3_checks.json).
- Fresh attacks: **93 exact inputs**, **10 QA cases**, **44 actual HTTP requests**, with guard-stage and predecessor comparisons. [Attack report](attacks/REPORT.md), [stage results](attacks/fresh_results.json), [HTTP](attacks/http_results.json). The original CLI served worktree-identical HTML. Owned fixed ports were **8901–8905**, used sequentially where shared; no use of 8765.
- UI scripts ran in Node VM with controlled DOM/fetch stubs. This verifies generated markup, callback behavior and response ordering; it does **not** verify browser paint/layout or browser-executed exploit behavior. No browser-executed XSS certification is claimed.

## Blocking findings

### M7-B1 — P1: whole-name recognition overrides a refusal already made correctly by `_link`

Exact request:

```json
{"text":"bevacizumab-awwb?"}
```

`POST /api/explore` returns **HTTP 200**, **BEVACIZUMAB / CHEMBL1201583**, **122 trials**, `matched_text:"Bevacizumab awwb"`, and `also:[]`. There is no separate accepted originator mention.

| Stage/control | Current result |
|---|---|
| `/api/resolve` | `ALIAS / CHEMBL1201583`, no refusal |
| `_resolver_blocked` | `{}` |
| `_link` alone | only `Refused`, label `bevacizumab-awwb` |
| `_whole_name`, then public `link_entities` | Drug / CHEMBL1201583 |
| Bare `bevacizumab-awwb` | refused |
| Exact `b7a00f9` linker on `bevacizumab-awwb?` | refused |

**New versus the reviewed m6 HEAD.** `bevacizumab-awwb!` also regresses. Literal quoted `"bevacizumab-awwb"` demonstrates the same current shortcut bypass, although that quoted spelling also leaked in the predecessor. [Actual HTTP](attacks/http_results.json), [current/previous stages](attacks/fresh_results.json), [independent historical replay](names/fresh_results.json).

**Cause:** `src/query.py:138-142` returns `_whole_name` before consulting `_link`. The shortcut creates its key from punctuation-stripped text (`191-194`) but runs product/tracer guards on the original text (`195-196`). The anchored suffix pattern (`src/textrules.py:156-157,213`) misses the question mark; `canonical_key` (`339-346`) still obtains the originator alias. `_link` would remove that punctuation and refuse (`src/query.py:217-220,252-264`). `Engine.explore` trusts the shortcut's hit (`src/app.py:88-95`).

The exact prefixed QA control `Which trials evaluate bevacizumab-awwb?` returns **zero evidence**: its prefix prevents the whole-input shortcut and reaches the working item linker. This is a map-centre regression, not a claim that that precise QA sentence leaks.

**Required outcome:** a whole-name exception must preserve refusal on the representation that enables its positive match. It must not override the correct refusal merely because punctuation defeats a raw anchored predicate.

### M7-B2 — P1: product wrappers and Unicode hyphens defeat both guards

These satisfy the requested **both-paths-miss** attack:

| Exact input | Resolver | `_link` and actual map |
|---|---|---|
| `(bevacizumab-awwb)` | ALIAS / CHEMBL1201583 | BEVACIZUMAB, 122 trials; no refusal |
| `[bevacizumab-awwb]` | same | same |
| `bevacizumab‑awwb` — internal U+2011 NON-BREAKING HYPHEN | same | same |
| `bio‑similar bevacizumab` — U+2011 | CONTAINED_ALIAS / CHEMBL1201583 plus unresolved qualifier | same |

Bare ASCII `bevacizumab-awwb` and `bio-similar bevacizumab` refuse. Every row above has actual HTTP explore/resolve confirmation and direct `_link` evidence; no exception for a separately accepted molecule applies. [HTTP](attacks/http_results.json), [stages and stored aliases](attacks/fresh_results.json), [independent replay](names/m7_focus.json).

`Which trials evaluate (bevacizumab-awwb)?` returns **12 originator rows**, first `NCT00955305|EVALUATES|CHEMBL1201583|NCT00955305`. `Which companies sponsor (bevacizumab-awwb)?` returns **12**, first `ORG:roche|SPONSORS_TRIAL_OF|CHEMBL1201583|`. The U+2011 suffix and `bio‑similar` trial questions also return 12 originator rows over HTTP.

**Cause:** `_link` retains brackets (`src/query.py:217-220`), while the biosimilar suffix predicate anchors the whole input and accepts only ASCII hyphen/en dash (`src/textrules.py:156-157`). The `bio-similar` pattern permits only ASCII hyphen (`139-140`). The later canonical key removes/normalizes these distinctions (`339-346`). The resolver calls the same product predicate (`src/normalize.py:729-735`), so running it first provides no independent protection. `_qualified` simply retries these predicates (`src/query.py:99-110`).

These are **inherited**, confirmed against the exact prior linker. The parenthesized/bracketed probes already appeared in m6's supplementary attack and remain **NOT FIXED**, despite repair of m6's named U+3002 example. The repository's own refused ASCII controls establish the product premise; no external pharmacology assumption is needed.

**Required outcome:** equivalent wrappers/hyphen spellings of the refused product must not unlock its originator alias, in either map or QA.

### M7-B3 — P1: a space-separated isotope prefix passes both guards

**`89Zr trastuzumab`** returns HTTP 200, **TRASTUZUMAB / CHEMBL1201585**, **13 trials**, `also:[]`. The resolver returns **ALIAS** using stored synonym **`89zr-trastuzumab`**; `_link` returns the same originator and `_resolver_blocked` is empty. Both `89Zr-trastuzumab` and `[89Zr] trastuzumab` refuse over HTTP. [HTTP/stages](attacks/REPORT.md#blocking-finding-c-a-space-separated-isotope-prefix-passes-both-gates), [stored alias](attacks/dictionary_evidence.json).

`Which trials evaluate 89Zr trastuzumab?` returns **12 originator rows**, first `NCT00016367|EVALUATES|CHEMBL1201585|NCT00016367`, with stored intervention `Trastuzumab`. The bracketed QA control returns zero.

**Cause:** `src/textrules.py:303-305` requires a hyphen after an unbracketed isotope, or brackets around it. `is_isotope_label` recognizes the separate `89Zr` token (`289-298`), but the resolver tests the entire component (`src/normalize.py:740-741`), and `_qualified` never calls that token predicate (`src/query.py:105-110`). Canonical alias lookup then accepts the stored radiolabel synonym. This is **inherited**, not introduced by HEAD.

**Required outcome:** the isotope-bearing name must remain refused when the isotope and moiety are separated by whitespace; neither map nor QA should substitute the unlabelled originator.

## Earlier findings — FIXED / NOT FIXED per finding

These dispositions describe the exact historical reproduction, not an assertion that its broader guarantee is now proven. Repeated later-round qualifications retain their original identity. Source lines refer to current HEAD; linked subreports contain the complete fixtures and input matrices.

### M1

| Finding / exact input or fixture | Disposition and current evidence |
|---|---|
| B1 `bevacizumab - awwb`, `89Zr - trastuzumab`, `[89Zr] trastuzumab` | **FIXED** — refusal, no centre. [Original script replay](names/m1_exact/names_product_bypass.json), [HTTP](root_checks/regression_http.json). |
| B2 collaborator called lead: `NCT00200395`, reverse `ORG:genentech` | **FIXED** — Genentech collaborator / Montefiore lead, both directions. `src/app.py:137,160-169`; `web/try.html:142-149`. [DB/UI](db_ui/REPORT.md). |
| B3 Investigator called institution: `NCT00754364`, `ORG:armandosantoromd` | **FIXED** — person-specific heading. `web/try.html:143,148`. [DB/UI](db_ui/REPORT.md). |
| B4 retire CHEMBL3353410 in memory; query name, ID, EGFR | **FIXED** — name/ID not_found; retired neighbour excluded. `src/app.py:115-118`. [Original HTTP fixture](names/m1_exact/names_retired_http_results.json). |
| Retired Trial included in live Drug count | **FIXED** — centre count and neighbour count/weight 0. `src/app.py:129-132,139,174`. [Fixtures](db_ui/db_fixtures.json). |
| S1 misleading most-evidence wording/order, Disease | **FIXED** — actual start-date/score/count/A–Z sort disclosed and verified. `src/app.py:141-170`; `web/try.html:148-158,231-235`. [Oracle](db_ui/db_validate.json). |
| S2 silent ring cuts: ALDESLEUKIN, Disease, AstraZeneca | **FIXED** — 22/25, 39/3,074, 41/145 drawn disclosed; cut lists say 30. [UI](db_ui/ui_harness_results.json). |
| S3 stale trail after refusal/not-found/server/network error | **FIXED** — state/buttons clear, obsolete back harmless. `web/try.html:213-216,243-244`. [UI](db_ui/ui_harness_results.json). |
| S4 reverse-completed EGFR/KRAS requests and concurrent duplicate EGFR | **FIXED** — latest KRAS stays, duplicate gives one trail entry. `web/try.html:211-214`. [UI](db_ui/ui_harness_results.json). |
| S5 silent ambiguity: Roche, MET, osimertinib EGFR/reversal, Mvasi and bevacizumab | **FIXED for disclosure** — selected reading/alternatives/refusal visible. `src/app.py:95-114`; `web/try.html:222-226`. [Names](names/names_reproduction_results.json). |
| S6 action/class specificity | **FIXED** — specific gloss and original AGONIST/BINDING AGENT/class codes. `web/try.html:162-176`. [UI](db_ui/ui_harness_results.json). |
| S7 start date, sponsor-to-Drug global count/phase, zero-trial Drug | **FIXED** — NCT00200395 start 2003-07-02; osimertinib sponsor 14/global 79/APPROVAL; CHEMBL925 count 0. [DB/UI](db_ui/REPORT.md). |
| S8 node/edge props null, list, broken JSON | **FIXED** — 12 original requests and restorations return 200. `src/app.py:211-217`. [Fixtures](db_ui/db_fixtures.json). |
| Hostile labels/titles/IDs/URLs; scheme/host/credential/backslash probes | **FIXED for exercised markup paths** — escaping and HTTPS registry allowlist; browser limitation above. `web/try.html:104,180,199,221-235`. [Assertions](db_ui/ui_assertions.json). |
| Unknown type Other / relation NEWREL | **FIXED** — raw fallback, no undefined tooltip. [UI](db_ui/ui_regressions.json). |
| All three / everything documentation overclaims | **FIXED** — All of them / a capped list per relation. `src/app.py:5-11`. |
| Silent 500-character cut: `"x"*500 + " osimertinib"`, `"osimertinib " + "x"*600` | **FIXED** — explicit HTTP 400, no partial map. `src/app.py:239-243`. [HTTP](root_checks/http_results.json). |
| Lowercase IDs / Investigator names: nct00200395, chembl3353410, Armando Santoro Md | **NOT FIXED**, unchanged usability limit. [Controls](names/names_unsupported_forms.json). |
| Raw list/null/malformed JSON/oversized-body errors | **NOT FIXED**, unchanged controlled 400 exposing parse/attribute details; subsequent valid requests succeed. `src/app.py:237-239,267-269`. [HTTP](root_checks/http_results.json). |

### M2b

| Finding / reproduction | Disposition and current evidence |
|---|---|
| R1 `osimertinib and generic version of bevacizumab`, reverse/comma, trial/sponsor QA | **FIXED** — only separate osimertinib; correct evidence. [HTTP](root_checks/regression_http.json), [supplement](root_checks/supplemental_http.json). |
| R1 tracer/oral-product collateral refusal, both orders | **FIXED** — `[89Zr] trastuzumab and osimertinib` and `osimertinib and oral azacitidine` retain osimertinib. [Names](names/names_regressions.json). |
| Inherited `What is the generic version of bevacizumab?` | **FIXED** — refusal, no centre; also M3-B2. [HTTP](root_checks/supplemental_http.json). |
| R2 missing sponsor count, Alaunos–ALDESLEUKIN edge, both endpoints and null/list/broken/empty props | **FIXED** — null/zero sort weight; UI unknown, numeric 0 stays 0. `src/app.py:141-146`; `web/try.html:173`. [Fixture](db_ui/db_missing_sponsor_count.json). |
| Bool association score and hidden precision rounding | **FIXED** — bool null/weight 0; exact EGFR/KRAS decimal values retained. [DB](db_ui/db_score_fixture.json), [UI](db_ui/ui_regressions.json). |
| Embedded multi-ID `Sharedbrand company` fixture | **FIXED** — Roche disclosed alongside selected AstraZeneca. `src/app.py:97-102`. [Fixture](names/names_boundary_details.json). |
| Missing/unknown SPONSORS role and equal-weight A–Z | **FIXED** — neutral role wording, both directions/types; ordering verified. [DB/UI](db_ui/REPORT.md). |
| Trial phases='PHASE2' render exception, four entry routes | **FIXED** — caught error, cleared trail, recovery/stale suppression. [Callbacks](db_ui/ui_m3_checks.json). |
| Residual module wording / successful-input truncation | **FIXED** — individual M1 rows above. |

### M3 and M4

| Finding / reproduction | Disposition and current evidence |
|---|---|
| M3-B1 `paclitaxel with albumin bound nanoparticles`, formulation variant, `generic version with bevacizumab` | **FIXED** — no originator centre/evidence. [HTTP](root_checks/supplemental_http.json), [names](names/names_new_boundaries.json). |
| M3-B2 leading generic-version question | **FIXED** — full qualified drug refused. [HTTP](root_checks/supplemental_http.json). |
| M3 comma collateral refusal: osimertinib with separately listed liposomal/biosimilar drug; reversals/QA | **FIXED** — separate osimertinib retained, 12 trial rows. [HTTP](root_checks/supplemental_http.json). |
| M3 bare erlotinib hydrochloride / long paclitaxel-poliglumex name; nested-parent re-link | **FIXED / retained** — correct complete IDs; no nested parent; explicit separate parent survives. [Names](names/names_attack.json). |
| M4-B1 wrong shortest-span tie: `osimertinib with generic version of bevacizumab`, reversal/added a | **FIXED under revised design** — both same-item drugs refused; zero qualified-drug QA evidence. [HTTP](root_checks/attack_http.json). |
| M4-B1 semicolon and fullwidth-comma variants | **FIXED** — separate osimertinib retained. [Separators](names/names_separator_checks.json). |
| M4-B2 long qualified poliglumex / `generic version of the monoclonal antibody bevacizumab` | **FIXED** — refused; bare long-name control preserved. [HTTP](root_checks/attack_http.json). |
| M4-B3 consumed qualifier: biosimilar version / liposomal formulation / albumin-bound / two-product combination | **FIXED** — no parent hit/evidence. [Names](names/names_attack.json), [HTTP](root_checks/attack_http.json). |
| M4 target/company collateral refusal: EGFR or AstraZeneca beside biosimilar bevacizumab, reverse/with controls | **FIXED** — target/company retained; drug refusal disclosed. [HTTP](root_checks/m5_http.json). |
| M4 no-relink QA assessment | **FIXED / retained** — meaningful adapted 1,648-input counterfactual, 0 errors; 24 nested-company semantic differences. [Adapted result](names/adapted_frozen_qa_relink_sweep.json). |
| M3/M4 blank/whitespace form | **NOT FIXED**, unchanged usability limit: no request, previous view stays. `web/try.html:241`. [UI](db_ui/ui_m3_checks.json). |
| M3/M4 positive/negative Infinity fixture | **NOT FIXED**, unchanged failure closed: controlled HTTP 400, no invalid value drawn, none in snapshot. `src/app.py:207-208,264-269`. [Fixture](db_ui/db_numeric_fixture.json). |
| Repeated lowercase-ID/name and raw request qualifications | **NOT FIXED**, same individual M1 rows above. |

### M5 and M6

| Finding / reproduction | Disposition and current evidence |
|---|---|
| M5-B1 reported attached slash/pipe and internal both-sides-glued attack | **FIXED** — `bevacizumab-awwb/ osimertinib` and `bevacizumab - awwb/osimertinib` select only OSIMERTINIB and expose refusal; pipe counterparts too. [HTTP](root_checks/m5_http.json), [m6 replay](root_checks/confirm_http.json). |
| M5-B2 `liposomal and nanoparticle formulation of doxorubicin`, plural/sustained-release | **FIXED** — forward qualifier carry refuses product; QA 0. [HTTP](root_checks/m5_http.json). |
| M5-S1 `biosimilar anastrozole, Arimidex`; `biosimilar Prolia, xgeva` | **FIXED** — separate aliases survive; 2/3 trial rows. [HTTP](root_checks/cross_item_http.json). |
| M5-S1 `Erlotinib, hydrochloride biosimilar bevacizumab`, semicolon | **FIXED for exact inputs** — parent CHEMBL553, 118 trials. Simplified unqualified comma inputs newly fail at M7-S1 below. [HTTP](root_checks/m5_http.json). |
| M5-S2 Pegylated interferon alfa-2a | **NOT FIXED — accepted known over-refusal**, not a new blocker. Canonical name/ID work. [HTTP](root_checks/m5_http.json). |
| M5-S3 all-substring cubic work / 999-character plain-answer timeout | **FIXED for reproduced defect** — bounded predicate work and completed plain-input requests. New split-piece cost is M7-S3 below. [Instrumentation](root_checks/perf_results.json), [answer replay](root_checks/perf_check_http.json). |
| M6-B1 interior slash/pipe | **FIXED** — correct separate osimertinib, no forbidden originator QA. `src/query.py:208-230,293-294`. [HTTP](root_checks/confirm_http.json). |
| M6-B2 U+3002 suffix punctuation, trailing em dash/hyphen, leading hyphen | **FIXED for exact named inputs** — refused, no centre/evidence. `src/query.py:138-154,218-220`. [HTTP](root_checks/confirm_http.json). |
| M6-B2 supplementary bracketed/Unicode variants | **NOT FIXED** — both-path misses, now M7-B2. The previously safe question-mark control has additionally regressed, M7-B1. [Reused attack](names/fresh_results.json). |
| M6-B3 `doxorubicin (nanoparticle and liposomal formulation)` / `bevacizumab (investigational and biosimilar)` | **FIXED** — no centre; trial/sponsor QA zero. [HTTP](root_checks/carry_http.json). |
| M6 non-parenthetical reversed-qualifier supplement | **NOT FIXED as original expectation; accepted current item-policy consequence** — `doxorubicin in nanoparticle and liposomal formulations` still selects doxorubicin. Not escalated as a new blocker. [Exact replay](root_checks/reverse_http.json). |
| M6-S1 six complete stored aliases returning another Drug ID | **FIXED for all six bare inputs** — ENDOSTATIN variant→CHEMBL4297946, rapamycin derivative→CHEMBL1908360, CP-358,774→CHEMBL553, and three other alias IDs restored. [Names table](names/REPORT.md), [HTTP](root_checks/alias_http.json). |
| M6-S1 prefixed QA using those comma-containing names | **NOT FIXED; whole-input-only design consequence** — `Which trials evaluate ENDOSTATIN, N-TERMINAL-MGGSHHHHH?` still returns 2 CHEMBL4297747 rows; rapamycin derivative QA still uses CHEMBL413. Explicitly outside the whole-input exception; no demo regression claimed. [HTTP](root_checks/alias_http.json). |
| M6 associated lone stored-alias losses | **NOT FIXED** — sweep still loses 20 formerly linked aliases, including accepted M5-S2; concrete non-refused names in M7-S2. [Sweep](names/names_m5_summary.json). |
| M6 split_2000 / many-piece cost control | **NOT FIXED / regressed performance** — former fast control now causes multi-second work and queued requests, M7-S3. [Reused stress](root_checks/cost_stress.json). |

## Should-fix findings, separate from approval blockers

### M7-S1 — P2: canonical equality is broader than exactly one stored name

| Exact input | Current map | `_link` / exact prior linker |
|---|---|---|
| `Erlotinib, hydrochloride` | ERLOTINIB HYDROCHLORIDE / CHEMBL1079742, 31 trials | ERLOTINIB / CHEMBL553, 118 trials |
| `osimertinib,mesylate` | OSIMERTINIB MESYLATE / CHEMBL3545063, 7 trials | OSIMERTINIB / CHEMBL3353410, 79 trials |
| `is a` | ISATUXIMAB / CHEMBL3545131, 1 trial | no entity / not_found |

All three are actual HTTP reproductions and **new versus b7a00f9**. None exactly matches a stored alias, even case-insensitively; they only match the aggressive key. The comma inputs violate the declared list boundary. The ordinary-word input bypasses the explicit `is a` safeguard in `_link`. [HTTP](attacks/http_results.json), [dictionary proof](attacks/dictionary_evidence.json).

`_whole_name` (`src/query.py:189-195`) erases punctuation and whitespace via `canonical_key` and never checks the stored name's actual token/punctuation boundaries; `_link` correctly enforces boundaries and the single-token abbreviation safeguard (`293-307`). Genuine complete-name controls `CP-358,774` and `Rapamycin, 42-o-(2-hydroxyethyl)-` have stored full-name matches and correctly retain their intended identities. Their exception need not accept arbitrary new comma lists. Prefixed salt QA stays on the parent drug; the salt counts themselves are accurately stored values.

### M7-S2 — P2: exact stored names are rejected before whole-name lookup

**`(E/Z)-AFATINIB`** uniquely names **CHEMBL1173655**, and `/api/resolve` returns **EXACT**. **`RO 09-1978/000`** uniquely names **CHEMBL1773**, with resolver **ALIAS**. Both `/api/explore` requests return HTTP 200 **not_found**, while the exact IDs draw live nodes. [Actual HTTP, stored-index proof and ID controls](names/alias_http.json).

`src/query.py:189-190` rejects slash/pipe or a listing word before checking whether the input is exactly one stored non-refused name. Thus step (2)'s intended precedence does not cover these valid lone names. The sweep has 20 formerly recognized names with no current Drug, including known M5-S2; it has **zero remaining wrong-ID cases among the 7,511 unique stored keys**. Some lost-alias resolver statuses differ, so the two positively resolved controls above are the strongest should-fix proof. [Complete list](names/names_m5_summary.json). No demo is lost.

### M7-S3 — P2: per-piece full resolution causes new multi-second lock contention

The old cubic all-substring defect remains repaired. The new resolver call for **every list piece**, including identical repeated pieces (`src/query.py:159-164`), introduces a different cost. A same-data, three-sample comparison loads the exact **b7a00f9 query module** and current query module without changing shared rules/data. A second measurement ran after all other audit workers stopped; this isolates audit workloads, not unrelated host activity.

| Exact linker input | Characters | b7a00f9 median | Current median |
|---|---:|---:|---:|
| `" ".join(["x"]*250)` | 499 | 0.0219 s | 0.0298 s |
| `";".join(["x"]*250)` | 499 | 0.0057 s | 0.2537 s |
| `";".join(["x"]*1000)` | 1,999 | 0.0512 s | 1.3120 s |
| `";".join(["x"]*2000)` | 3,999 | 0.1779 s | 2.5561 s |

The 2,000-piece stage check spends **2.5653 s** in `_resolver_blocked`, versus **0.2734 s** in `_link`. Measurements are separate calls and need not sum to a median. [Samples/stage timings](root_checks/isolated_fresh_cost_comparison.json), [reproducer](root_checks/fresh_cost.py).

Actual unchanged CLI HTTP, within existing caps:

- 499-character semicolon text: `/api/explore` **0.3160 s**, `/api/ask` **0.3148 s**, both 200.
- `POST /api/check` with `{"text":"EGFR","answer":";".join(["x"]*2000)}`: **7.7280 s**, HTTP 200.
- Ordinary EGFR map dispatched **0.1010 s** after that check: **7.6665 s**, HTTP 200. EGFR before/after: **0.0384 / 0.0412 s**. GET `/` remains responsive.
- First independent run also reproduced the delay: check **6.0783 s**, queued EGFR **6.0118 s**. No timeout/deadlock inference is needed; these responses completed.

[Isolated HTTP](root_checks/isolated_fresh_cost_http.json), [first HTTP run](root_checks/fresh_cost_http.json), [owned-server cleanup](root_checks/isolated_fresh_cost_lifecycle.json). The inherited m6 stress script independently records split_2000 at **3.4737 s** median linking / **7.0111 s** `Engine.check`; plain 2,000-token input is far cheaper. [Exact inherited stress](root_checks/cost_stress.json).

The application holds `engine.lock` across linking/checking (`src/app.py:247-263`), and the answer cap is 4,000 characters (`260`). Avoid repeating full resolver work for identical pieces and bound total work across every caller, while preserving the refusal semantics. This is a should-fix cost regression, separate from the originator-leak approval blockers. These timings are local observations, not universal latency guarantees or a claim that the entire algorithm has one asymptotic complexity.

## Other successful controls and integrity

All seven HTTP QA demos retain evidence counts **12, 12, 11, 1, 12, 0, 0**. Six complete responses equal original bfcb83d; Mvasi differs only in refusal metadata. Ordinary Disease returns **2,774 Trials + 300 Targets**, 30 each, **18,575 bytes in 104.799 ms**. The inherited **24-request / 12-worker** workload returns expected HTTP 200 shapes in **956.657 ms**. These ordinary samples are separate from the adversarial cost measurements. [HTTP demos](root_checks/http_demo_results.json), [HTTP workload](root_checks/http_results.json).

The snapshot has **7 retired nodes, 142 retired edges, no self-loops and no live edges with retired endpoints**. All six node types and the 1,001-Drug count-chunk fixture are covered. No new wrong live edge, relation/direction wording, stored value, cut notice, or generated-markup injection was established. README launch wording remains accurate at `README.md:566` / `README.ko.md:387`. The refusal promise still fails at `src/app.py:74-76` and `web/try.html:215` for the blockers above. [DB/UI evidence](db_ui/REPORT.md).

**Standards: 0 documented violations.** No tracked standards file was found. The user-supplied evidence/no-tracked-edit instructions govern; no code modification was made, so the conditional KOA Studio / KhOpenApi original-versus-modified-code comparison is not triggered. [Standards evidence](db_ui/standards_findings.md).

No model was called by the exercised application paths; `Engine.ask` uses `use_llm=False` (`src/app.py:180-181`). SQLite is not globally opened read-only by the application, so read-only conclusions rely on executed paths, isolated fixtures and hash checks, not a connection-permission guarantee. Final HEAD, tracked/staged diffs, all **2,111 tracked-file SHA-256 comparisons**, database hash, owned-port closure and report-link checks are in [integrity_final.json](integrity_final.json). Expected database SHA-256: `7341c5a7089731f67356da5a588b269d4b69e8e6c4c054acf19aa4ef2837b529`.

## Reproduction

Run from the repository root with bytecode disabled. Copies/manifests above preserve original-script provenance; HTTP scripts sharing a port must run sequentially. Worker reports include their individual commands. The isolated benchmark is the only repeated cost run, used to remove concurrent audit workload as a confounder.

```text
python -B audit_evidence_claims/m7/root_checks/run_verification.py
python -B audit_evidence_claims/m7/root_checks/run_replays.py http
python -B audit_evidence_claims/m7/root_checks/run_m6_http.py m6_http
python -B audit_evidence_claims/m7/root_checks/run_replays.py perf
python -B audit_evidence_claims/m7/root_checks/run_perf_current.py
python -B audit_evidence_claims/m7/root_checks/cost_stress.py
python -B audit_evidence_claims/m7/root_checks/fresh_cost.py isolated
python -B audit_evidence_claims/m7/names/run_replays.py
python -B audit_evidence_claims/m7/db_ui/run_replays.py
python -B audit_evidence_claims/m7/db_ui/demo_http.py
python -B audit_evidence_claims/m7/attacks/fresh_probe.py
```

VERDICT: CHANGES REQUIRED
