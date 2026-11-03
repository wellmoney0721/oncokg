# Independent relation-map review — round 6

Reviewed HEAD **`b7a00f9`**, including repairs `595f5f9` and `c43f911`; baseline feature commit `bfcb83d`. Date: 2026-11-03 KST. **Three reproducible originator-leak mechanisms block approval.** All exact named m1–m4 blockers remain fixed. M5's reported spaced-separator examples are fixed, but its earlier internal-separator attack still fails. M5-B2 and M5-S1 are fixed for their reported inputs; M5-S3's reproduced cost defect is fixed. M5-S2 remains the explicitly accepted over-refusal.

No application or tracked file was edited. The intentional refusal of all drugs in one qualified item is accepted throughout this report. A product's originator being accepted is a different outcome and is not covered by that exception.

## Verification and evidence boundaries

- Required command: `python -m pytest tests -q -p no:cacheprovider` — **329 passed in 30.72 s**, exit 0. Bytecode disabled; all test temporary files confined to m6. [Output](root_checks/pytest.txt), [environment and hashes](root_checks/pytest_summary.json).
- Original CLI server `python -B -u src/app.py <port>` exercised over HTTP on owned ports **8896, 8897 and 8899**, sequentially when reusing a port. No use of 8765. Six inherited HTTP runners exited 0; all owned servers were closed. [Replay execution](root_checks/execution_http.json), [copy provenance](root_checks/reuse_manifest.json).
- **6,469 live centres**, **22 relation/direction/type/role combinations**, **0 stored-row oracle mismatches**. **19/19 DB assertions** and **24/24 UI assertions** pass. [DB/UI report and exact fixtures](db_ui/REPORT.md), [oracle](db_ui/db_validate.json), [DB assertions](db_ui/db_assertions.json), [UI assertions](db_ui/ui_assertions.json).
- **36/36 complete page-demo payloads equal m5**; all 36 demo callbacks plus 6 map callbacks succeed. [Comparison](db_ui/ui_demo_compare.json), [callbacks](db_ui/ui_m3_checks.json). No demo regression was found.
- Thirteen inherited name scripts were reused with output plumbing adapted, including m1 reproductions, m2b/m3 boundaries, m4 attacks, and the m5 **113 boundary cases / 7,511 unique alias-key sweep**. [Execution](names/replay_execution.json), [provenance](names/replay_manifest.json), [name disposition report](names/REPORT.md). Fresh independent attacks add **106 inputs / 8 QA responses**, plus **11 reversed-qualifier cases**. [Fresh results](attacks/fresh_results.json), [reversed cases](attacks/reversed_results.json).
- Page JavaScript was executed in a Node VM with controlled DOM/fetch stubs. This establishes generated markup, callbacks, error handling and request ordering; it does **not** establish browser paint/layout or browser-executed exploit behavior. Actual served HTML equals the worktree. No browser-executed XSS claim is made.
- Root-owned HTTP/test/cost evidence is under `root_checks/`; worker evidence is under `names/`, `db_ui/`, and `attacks/`. Unattributed files that appeared directly in m6 during the review are not used as evidence. The final integrity check compares against the root review's own initial tracked-file hashes.

## Blocking findings

### M6-B1 — P1: a separator glued on both sides still hides a refused suffix

Exact request:

```json
{"text":"bevacizumab - awwb/osimertinib"}
```

`POST /api/explore` returns HTTP 200 with **BEVACIZUMAB / CHEMBL1201583**, **122 trials**, and **no refused span**. The identical `/api/resolve` input returns `bevacizumab - awwb: BLOCKED_DISTINCT_PRODUCT`, no accepted first drug, and `osimertinib: EXACT / CHEMBL3353410`. Thus the refused-product premise is demonstrated using the repository's own resolver. [Actual HTTP](root_checks/confirm_http.json), [independent replay](db_ui/interior_separator_probe.json).

| Exact `/api/ask` text | Actual result |
|---|---|
| `Which trials evaluate bevacizumab - awwb/osimertinib?` | 12 originator rows; first `NCT00955305\|EVALUATES\|CHEMBL1201583\|NCT00955305` |
| `Which companies sponsor bevacizumab - awwb/osimertinib?` | 12 originator rows; first `ORG:roche\|SPONSORS_TRIAL_OF\|CHEMBL1201583\|` |

**Cause:** `src/query.py:143-154` splits comma/semicolon and whitespace, strips `/` and `|` only from the edges of a token, and creates boundaries only for `startswith`/`endswith`. Interior `awwb/osimertinib` remains one token. `_qualified` (`99-110`) never checks a run ending at `awwb`, so the anchored suffix guard (`src/textrules.py:156-157,213-223`) misses it. The separate bare `bevacizumab` token is then accepted at `src/query.py:212-237`, and `Engine.explore` trusts it at `src/app.py:88-95`.

`bevacizumab - awwb|osimertinib` also leaks. The pipe resolver itself misses that split, so the slash case is the strongest exact resolver comparison. Controls `bevacizumab - awwb/ osimertinib` and `bevacizumab - awwb / osimertinib` correctly select only OSIMERTINIB and disclose the refused product; bare `bevacizumab - awwb` refuses. These controls isolate the missing **interior** boundary.

Related consequences of the same mechanism are `Erlotinib/hydrochloride` and `Erlotinib|hydrochloride` assembling **CHEMBL1079742**, a salt across a declared item boundary; `biosimilar anastrozole/Arimidex` losing the separate Arimidex; and `osimertinib/EGFR` returning not_found. [HTTP](root_checks/alias_http.json). They are not counted as separate blockers.

**Status:** inherited under the exact `514929c` linker comparison; the slash input was already in m5's reused attack. M5-B1 is therefore **FIXED for the reported spaced examples, NOT FIXED as a mechanism**. [Previous/current comparison](attacks/fresh_results.json), [m5 replay](names/names_m5_attack.json).

**Required outcome:** all declared glued/free separators must form real item boundaries before guards and matching. Never select CHEMBL1201583 from this refused component; preserving the separately named osimertinib or refusing an ambiguous input is safe.

### M6-B2 — P1: edge punctuation is removed for alias matching after defeating refusal

Exact input **`bevacizumab-awwb。`**, with final **U+3002 IDEOGRAPHIC FULL STOP**, returns HTTP 200 and **BEVACIZUMAB / CHEMBL1201583**, **122 trials**, matched alias `Bevacizumab awwb`, and no refusal. The same `/api/resolve` input yields a single `bevacizumab-awwb: BLOCKED_DISTINCT_PRODUCT` component with no accepted drug. [HTTP](root_checks/confirm_http.json).

`Which trials evaluate bevacizumab-awwb。?` and `Which companies sponsor bevacizumab-awwb。?` each return **12 originator evidence rows**, with the same first trial/sponsor edges as B1. ASCII-period `bevacizumab-awwb.` and bare `bevacizumab-awwb` are refused; their trial/sponsor questions have **0 evidence**. Trailing U+2014, trailing ASCII hyphen and leading ASCII hyphen also produce the resolver/linker disagreement over HTTP.

**Cause:** the strip set at `src/query.py:147` differs from the resolver's edge-punctuation normalization (`src/textrules.py:283,382-383`). The suffix regex is anchored at both ends (`156-157`), so the retained punctuation defeats it. The later `canonical_key` call (`src/query.py:221`; `src/textrules.py:339-346`) removes that punctuation and recovers an alias for the originator. Whole-item and eight-word checks preserve the same offending character, so increasing their coverage cannot fix this mismatch.

**Status:** inherited under `514929c`, still a blocker. Quoted/bracketed suffix variants and some Unicode hyphens also fail both resolver and linker; those are explicitly distinguished from the exact U+3002 resolver disagreement in [independent findings](attacks/FINDINGS.md). No external pharmacology assumption is needed for the primary reproduction.

**Required outcome:** normalization that enables a positive alias must not remove evidence that prevented its refusal guard from matching. The U+3002 and hyphen-edge controls must refuse the product before mapping or retrieving originator evidence.

### M6-B3 — P1: forward-only qualifier carry loses a trailing qualifier inside one product description

Two exact parenthetical descriptions independently fail:

| Exact input | `/api/resolve` | `/api/explore` |
|---|---|---|
| `doxorubicin (nanoparticle and liposomal formulation)` | One `doxorubicin` component, `BLOCKED_DISTINCT_PRODUCT`, no accepted drug; rules `extract_parenthetical`, `distinct_product_guard` | DOXORUBICIN / CHEMBL53463, 3 trials, no refusal |
| `bevacizumab (investigational and biosimilar)` | One `bevacizumab` component, `BLOCKED_DISTINCT_PRODUCT`, no accepted drug; same rules | BEVACIZUMAB / CHEMBL1201583, 122 trials, no refusal |

These are qualified descriptions of the preceding drug, not two separately named drugs. [Actual HTTP](root_checks/carry_http.json), [independent current/predecessor comparison](attacks/reversed_results.json).

`Which trials evaluate doxorubicin (nanoparticle and liposomal formulation)?` returns **3** originator rows, first `NCT01970540|EVALUATES|CHEMBL53463|NCT01970540`. Its sponsor question returns 3 rows, first `ORG:imunon|SPONSORS_TRIAL_OF|CHEMBL53463|`. The corresponding two bevacizumab questions return **12** originator rows each, beginning with B1's trial/sponsor edges.

**Cause:** `src/query.py:167-174` splits on `and` even inside the parenthetical qualifier. The drug is in the earlier, unqualified item. The later `liposomal formulation)` or `biosimilar)` item has no drug, so `192-197` stores it as `dangling` and continues. Carry is applied only to a **subsequent** drug (`183-184,199-201`); it never marks the earlier drug refused before final positive matching. The final qualifier can therefore disappear without even an output Refused entry. The full resolver preserves the original product context for its guard (`src/normalize.py:707,729-735`).

Controls `doxorubicin (liposomal formulation)` and the original M5-B2 `liposomal and nanoparticle formulation of doxorubicin` both refuse and produce **0 QA evidence**. Separate-drug controls `osimertinib and liposomal doxorubicin` and `doxorubicin and liposomal paclitaxel` retain the independently named first drug. [HTTP controls](root_checks/carry_http.json).

**Status:** inherited under `514929c`; the latest forward-carry repair does not solve this design failure. The stated carry direction explains the implementation but does not waive the approval bar against a refused product becoming its originator. This is an **under-refusal**, not the accepted same-item over-refusal or M5-S2.

**Required outcome:** preserve the qualifier's scope within an unambiguously single product description, or refuse that ambiguous product as a whole. Do not propagate every trailing qualifier backwards indiscriminately across genuinely separate named products.

## Earlier findings — exact reproduction dispositions

The following tables include prior should-fix items and qualifications, not only blockers. FIXED refers to the cited reproduction; it does not certify the broader guarantee contradicted above. Detailed raw cases and source references are also in the [names matrix](names/REPORT.md) and [DB/UI matrix](db_ui/REPORT.md).

### M1

| Finding / exact input or fixture | Status | Current evidence |
|---|---|---|
| B1 `bevacizumab - awwb`, `89Zr - trastuzumab`, `[89Zr] trastuzumab`, compact controls | **FIXED** | Refused, no centre. [HTTP](root_checks/regression_http.json), [all original name inputs](names/names_reproduction_results.json). |
| B2 collaborator labelled lead: `NCT00200395`, reverse `ORG:genentech` | **FIXED** | Genentech collaborator, Montefiore lead; role-specific reverse groups. `src/app.py:137,160-169`; [DB/UI](db_ui/REPORT.md). |
| B3 Investigator called institution: `NCT00754364`, `ORG:armandosantoromd` | **FIXED** | Investigator heading uses researcher. `web/try.html:143,148`; [render](db_ui/ui_harness_results.json). |
| B4 retired centre by name; retire CHEMBL3353410 in memory, request name/ID/EGFR | **FIXED** | Name/ID not_found; EGFR omits it. `src/app.py:115-118`; [handler fixture](db_ui/db_retired_center.json). |
| Retired-Trial count, live T-EVALUATES-D edge with retired T | **FIXED** | D centre and neighbour count/weight 0; retired T excluded. `src/app.py:129-132,139,174`; [fixture](db_ui/db_fixtures.json). |
| S1 evidence-order wording, Disease and equal-weight names | **FIXED** | Each sort stated; start dates, scores, counts and A–Z match oracle. `src/app.py:166-170`; `web/try.html:148-158`; [oracle](db_ui/db_validate.json). |
| S2 silent ring/list cuts: ALDESLEUKIN, Disease, AstraZeneca | **FIXED** | 22/25, 39/3,074 and 41/145 drawn are disclosed; 30-item list cuts disclosed. [render](db_ui/ui_harness_results.json). |
| S3 stale trail after refusal/not-found/server/network failure and old back callback | **FIXED** | Trail cleared; obsolete callback harmless; normal back works. [callbacks](db_ui/ui_harness_results.json). |
| S4 EGFR/KRAS reverse completion and duplicate EGFR requests | **FIXED** | Latest result survives, stale errors ignored, duplicate requests leave one trail entry. [callbacks](db_ui/ui_harness_results.json). |
| S5 `Roche`, `MET`, `osimertinib EGFR`, reversed; mixed refusal disclosure | **FIXED for exact inputs** | Selected stored alias and alternatives/refused item disclosed. `src/app.py:95-114`; [names](names/names_reproduction_results.json), [UI](db_ui/ui_harness_results.json). |
| S6 AGONIST/BINDING AGENT and sponsor-class detail | **FIXED** | Specific gloss plus original action/class codes. `web/try.html:162-176`; [UI](db_ui/ui_harness_results.json). |
| S7 centre start date, sponsor-to-Drug global count/phase, zero-trial Drug | **FIXED** | `2003-07-02`; AstraZeneca→osimertinib sponsor 14/global 79/APPROVAL; CHEMBL925 count 0. [DB/UI](db_ui/REPORT.md). |
| S8 props `null`, `[]`, `{broken`, node and edge | **FIXED** | 12 original requests and restored controls return 200. `src/app.py:211-217`; [fixture](db_ui/db_fixtures.json). |
| Hostile labels/titles/IDs/URLs; javascript/data/host/credential/backslash variants | **FIXED for exercised map paths** | Escaped markup and registry HTTPS allowlist; browser limitation above. `web/try.html:104,180,199,221-235`; [assertions](db_ui/ui_assertions.json). |
| Unknown type `Other` / relation `NEWREL` tooltip | **FIXED** | Raw fallback, no undefined. [UI](db_ui/ui_regressions.json). |
| “All three” / later “everything” doc overclaims | **FIXED** | “All of them”, “a capped list per relation”. `src/app.py:5-11`. |
| Silent 500-character cut: `"x"*500 + " osimertinib"`; `"osimertinib " + "x"*600` | **FIXED** | HTTP 400 explicit length error, no partial map. `src/app.py:239-243`; [HTTP](root_checks/http_results.json). |
| Lowercase IDs / Investigator names: `nct00200395`, `chembl3353410`, `Armando Santoro Md` | **NOT FIXED — unchanged usability limit** | These remain not_found; canonical IDs work. [replay](names/names_unsupported_forms.json). |
| Raw request-shape errors: list/null/malformed JSON/oversized body | **NOT FIXED — unchanged server qualification** | Controlled 400 exposes parse/attribute detail; subsequent valid calls work. [HTTP](root_checks/http_results.json). |

### M2b

| Finding / exact reproduction | Status | Current evidence |
|---|---|---|
| R1 `osimertinib and generic version of bevacizumab`, reverse/comma variants, trial/sponsor questions | **FIXED** | Only separate osimertinib retained; its trial/sponsor evidence returned. [HTTP](root_checks/regression_http.json), [supplement](root_checks/supplemental_http.json). |
| R1 tracer/oral-product collateral refusal, both orders | **FIXED** | `[89Zr] trastuzumab and osimertinib`, reversal, `osimertinib and oral azacitidine` retain separate osimertinib. [names](names/names_regressions.json). |
| Inherited `What is the generic version of bevacizumab?` | **FIXED** | No centre; also M3-B2. [HTTP](root_checks/supplemental_http.json). |
| R2 missing sponsor count on `ORG:alaunos\|SPONSORS_TRIAL_OF\|CHEMBL1201438\|`, both endpoints, null/list/broken/empty props | **FIXED** | API null, sorting weight 0; UI says unknown. Stored numeric 0 remains 0. [fixture](db_ui/db_missing_sponsor_count.json), [render](db_ui/ui_missing_sponsor_count.json). |
| Bool association scores and hidden precision rounding | **FIXED** | Bool→null/weight 0; no renderer crash; EGFR/KRAS exact scores preserved. [DB](db_ui/db_score_fixture.json), [UI](db_ui/ui_regressions.json). |
| Embedded multi-ID company alias `Sharedbrand company` fixture | **FIXED** | AstraZeneca selected, Roche disclosed in also. `src/app.py:97-102`; [fixture](names/names_boundary_details.json). |
| Missing/unknown SPONSORS role and equal-weight A–Z follow-up | **FIXED** | Neutral unknown-role wording, both directions/types; order passes. [DB](db_ui/db_role_fallback.json), [UI](db_ui/ui_regressions.json). |
| Render exception escape: Trial `props.phases='PHASE2'`, four entry routes | **FIXED** | Caught error, cleared trail, recovery and stale-reply suppression. [callbacks](db_ui/ui_m3_checks.json). |
| Residual module wording and successful-input truncation | **FIXED** | M1 wording/length rows above. |

### M3

| Finding / exact reproduction | Status | Current evidence |
|---|---|---|
| B1 `paclitaxel with albumin bound nanoparticles`, formulation variant, `generic version with bevacizumab` | **FIXED** | No originator centre; paclitaxel QA 0 evidence. [HTTP](root_checks/supplemental_http.json), [boundary replay](names/names_new_boundaries.json). |
| B2 `What is the generic version of bevacizumab?` | **FIXED** | Refused, no centre. [HTTP](root_checks/supplemental_http.json). |
| Comma collateral refusal: `osimertinib, liposomal doxorubicin`, biosimilar variant, reversals and QA | **FIXED** | Separate osimertinib survives, with 12 trial rows. [HTTP](root_checks/supplemental_http.json). |
| Bare long-name/nested-parent controls `erlotinib hydrochloride`, `Paclitaxel conjugate with poly-l-glutamic acid` | **FIXED / retained** | Correct full identities, no nested parent; explicitly separate parent still links. [controls](names/names_attack.json). |
| Supplementary wrong-binding, long qualified poliglumex, hyphenated albumin-bound, semicolon/fullwidth comma | **FIXED** | Covered individually in M4 below and [separator replay](names/names_separator_checks.json). |
| Empty/whitespace map form | **NOT FIXED — unchanged usability qualification** | No request; previous view remains. `web/try.html:241`; [UI](db_ui/ui_m3_checks.json). |
| Positive/negative Infinity fixture | **NOT FIXED — unchanged, failure closed** | Numeric helper accepts Infinity, JSON encoding gives controlled HTTP 400; no invalid value drawn, none in snapshot. `src/app.py:207-208,264-269`; [fixture](db_ui/db_numeric_fixture.json). |

### M4

| Finding / exact reproduction | Status | Current evidence |
|---|---|---|
| B1 shortest-span tie: `osimertinib with generic version of bevacizumab`, reversal / added `a`, exact trial/sponsor QA | **FIXED under current design** | Both same-item drugs refused, QA 0. This over-refusal is explicitly accepted. [HTTP](root_checks/attack_http.json). |
| B1 semicolon/fullwidth-comma variants | **FIXED** | Separately listed osimertinib survives; qualified bevacizumab refused. [replay](names/names_separator_checks.json). |
| B2 six-token reach: qualified long poliglumex alias and `generic version of the monoclonal antibody bevacizumab` | **FIXED** | Refusal and 0 qualified-drug evidence; bare poliglumex links. [HTTP](root_checks/attack_http.json). |
| B3 consumed qualifier: `biosimilar version of bevacizumab`, `liposomal formulation of doxorubicin`, `paclitaxel with albumin-bound nanoparticles`, two-product combination | **FIXED** | No originator drug hit; QA empty for qualified drugs. [replay](names/names_attack.json), [HTTP](root_checks/attack_http.json). |
| Target/company collateral refusal: EGFR/AstraZeneca plus biosimilar bevacizumab, reversed/with controls | **FIXED** | Target/company retained, drug refusal disclosed. [HTTP](root_checks/m5_http.json), [names](names/names_attack.json). |
| No-relink QA assessment | **FIXED / retained behavior** | All **1,648 frozen earlier questions** replayed in exact order: 64 identical, 1,560 metadata-only, 24 semantic differences, 0 errors versus HEAD with token re-linking enabled. Differences remove nested company matches inside full drug aliases. [frozen sweep](names/frozen_qa_relink_sweep.json), [input-array equality proof](names/frozen_qa_relink_verification.json). The separately generated current 1,612-question sweep also has 0 errors. |
| Repeated lowercase-ID, raw error, blank-submit and Infinity qualifications | **NOT FIXED — unchanged** | Individual M1/M3 rows above, with fresh evidence. |

### M5

| Finding / exact reproduction | Status | Current evidence |
|---|---|---|
| B1 reported `bevacizumab-awwb/ osimertinib`, `bevacizumab - awwb/ osimertinib`, pipe equivalent | **FIXED for reported examples** | Separate OSIMERTINIB centre; refused bevacizumab span disclosed; QA switches to correct osimertinib evidence. [HTTP](root_checks/m5_http.json). |
| B1 earlier attack with internal `/` or `|`, both sides glued | **NOT FIXED** | BEVACIZUMAB centre and originator QA; M6-B1 above. [reused attack](names/names_m5_attack.json), [HTTP](root_checks/confirm_http.json). |
| B2 `liposomal and nanoparticle formulation of doxorubicin`, plural/sustained-release versions | **FIXED for reported examples** | Forward bare-qualifier carry refuses drug; QA 0. [HTTP](root_checks/m5_http.json). The new reversed-parenthetical mechanism is M6-B3. |
| S1 `biosimilar anastrozole, Arimidex`; `biosimilar Prolia, xgeva` | **FIXED** | Separate aliases survive, with 2 Arimidex / 3 Xgeva trial rows. [HTTP](root_checks/cross_item_http.json). |
| S1 `Erlotinib, hydrochloride biosimilar bevacizumab`, semicolon variant | **FIXED** | ERLOTINIB/CHEMBL553, 118 trials; no cross-item salt. [HTTP](root_checks/m5_http.json). |
| S2 `Pegylated interferon alfa-2a` | **NOT FIXED — recorded accepted over-refusal** | Still refused; canonical PEGINTERFERON ALFA-2A/ID works. Not a blocker or new finding. [HTTP](root_checks/m5_http.json). |
| S3 all-runs cubic cost, lock contention and 999-character check-answer timeout | **FIXED for reproduced defect** | Bounded predicate work, prompt completed responses; measurements below. [instrumentation](root_checks/perf_results.json), [HTTP](root_checks/perf_http.json), [answer-field replay](root_checks/perf_check_http.json). |

## Should-fix and design consequences, separate from blockers

### M6-S1 — P2: complete stored names containing list punctuation can select a different drug

The strict item policy can do more than refuse a lone alias: six complete stored aliases in the reused 7,511-key sweep now select only another drug ID. Examples confirmed over actual HTTP:

| Complete stored name / alias | Stored unique identity | Current selected identity |
|---|---|---|
| `ENDOSTATIN, N-TERMINAL-MGGSHHHHH` — preferred name | CHEMBL4297946 | ENDOSTATIN / CHEMBL4297747 |
| `Rapamycin, 42-o-(2-hydroxyethyl)-` | EVEROLIMUS / CHEMBL1908360 | SIROLIMUS / CHEMBL413 |
| `CP-358,774` | ERLOTINIB / CHEMBL553 | ERLOTINIB HYDROCHLORIDE / CHEMBL1079742 |

[HTTP and QA](root_checks/alias_http.json), [all six aliases, stored provenance and previous/current hits](names/names_m5_attack.json), [summary table](names/REPORT.md). The other examples are `Usp mab 002, monoclonal igg1`, `Usp mab 003, monoclonal igg1`, and `12,13-desoxyepothilone b, cis`. The endostatin exact-ID control selects the intended CHEMBL4297946. The complete endostatin name's trial QA instead retrieves two CHEMBL4297747 rows.

This follows the unconditional item boundaries at `src/query.py:143,216-217,277`. Because the requested design explicitly imposes those boundaries, this is reported as an identity tradeoff/should-fix, not used as an additional approval blocker or mislabeled as an over-refusal. It needs an explicit user-visible limitation or a safe disambiguation policy. Do not bypass product guards merely because a full alias exists.

The same sweep records **57** formerly recognized lone aliases with no current Drug hit against the exact bf436c6 comparison: the accepted pegylated alias plus **56** punctuation/list-word cases such as `ICI 182,780`, `CP-675,206`, `Nk cells, autologous`, and `Anusol plus hc`. These deliberate boundary losses are recorded without treating intended over-refusal as a new blocker. None appears in the page demos. [summary](names/names_m5_summary.json).

Previously recorded lowercase-ID/name handling, blank submit, raw 400 details and Infinity behavior remain as itemized above. No new misleading cut notice, graph relation/direction, stored field value, or generated-markup injection defect was established in the exercised paths.

## Cost, demo and boundary controls

The exact m5 performance script was reused; its `m4` baseline means bf436c6, not the slower m5 revision. Fresh instrumented HEAD uses **2,223 calls to each refusal predicate / 32,882 aggregate characters** for the 250-token plain case; the prior m5 report recorded 31,625 calls each / 10,479,750 characters. The bounded eight-word scan removes the former all-substring growth. [instrumentation](root_checks/perf_results.json).

| Exact fresh HTTP workload | Observed result |
|---|---|
| `/api/explore`, `" ".join(["x"] * 250)` — 499 chars | 200, **0.0302 s** |
| `/api/ask`, same 499 chars | 200, **0.0308 s** |
| `/api/explore`, 244 x tokens plus osimertinib — 499 chars | 200, **0.0796 s** |
| Four simultaneous 499-character explores | All 200, **0.1290 s** total wall time |
| Ordinary EGFR sent 0.1 s after one long lookup | 200, **0.0385 s**; not proof it waited on an occupied lock |
| 501-character explore | 400, **0.0030 s** |
| `/api/check`, question EGFR, 999-character x answer | 200, **0.1812 s**; following EGFR 200, **0.0402 s** |
| `/api/check`, question EGFR, 3,999-character x answer | 200, **0.3930 s** |

[HTTP timing/lock replay](root_checks/perf_http.json), [previous answer-timeout reproduction](root_checks/perf_check_http.json), [larger answer-field HTTP](root_checks/confirm_http.json). These are local observations, not universal latency guarantees; first replay workloads overlapped with other read-only audit work.

An additional isolated three-sample direct-linker check gives medians **0.0143, 0.0277, 0.0569, 0.1139 s** at 250/500/1,000/2,000 plain tokens. A 3,999-character semicolon-separated answer takes **0.1395 s** to link / **0.3340 s** for `Engine.check`; many matched drugs, many refused items and many joiners also complete below those check timings. [Exact inputs and measurements](root_checks/cost_stress.json), [reproducer](cost_stress.py). The overall linker still has per-segment rescans and growing set operations (`src/query.py:180-186,214`); this report does not infer global linear complexity from `_qualified` alone. No further practical cost blocker was demonstrated within the HTTP caps.

All **16** new padded suffix/tracer/liposomal/generic-version controls with 0/4/8/16 filler words refuse. No isolated eight-word-window regression was found. Forward qualifier-carry and standalone product controls (`Mvasi and bevacizumab`, bracketed/trademark Mvasi, `Abraxane and paclitaxel`) behave as specified. [fresh attack controls](attacks/fresh_results.json).

All seven actual HTTP QA demos retain evidence counts **12, 12, 11, 1, 12, 0, 0**. Six full responses equal bfcb83d; Mvasi differs only in refusal metadata. All 36 complete demo responses equal m5. [HTTP demo comparison](root_checks/http_demo_results.json), [full demo comparison](db_ui/ui_demo_compare.json).

Ordinary Disease HTTP returns 2,774 Trials and 300 Targets, 30 each, **18,575 bytes in 80.714 ms**. The original **24 requests / 12 workers** all return expected HTTP 200 shapes in **753.288 ms**. A 1,001-Drug fixture verifies all three count chunks. [HTTP](root_checks/http_results.json), [fixtures](db_ui/db_fixtures.json).

## Standards, read-only integrity and reproduction

**Standards axis: 0 documented violations.** No tracked AGENTS/CONTRIBUTING/CODING/docs-agent standards files were found; the supplied evidence-based review and no-tracked-edit instructions govern this audit. No application code was changed, so a KOA Studio / KhOpenApi original-versus-modified code comparison is not applicable. [Separate standards review](db_ui/standards_findings.md).

**Specification axis: three blocking refusal mechanisms**, plus the separate stored-name identity tradeoff and unchanged qualifications. All graph-edge, direction and value checks remain successful for the selected centres; that does not excuse selecting a refused product's originator. The page/docstring refusal promise still fails (`src/app.py:74-76`, `web/try.html:215`). README launch wording remains accurate (`README.md:566`, `README.ko.md:387`).

Snapshot: 7 retired nodes, 142 retired edges, no live edge with a retired endpoint, no self-loop, and all six node types covered. Malformed/retired/numeric cases use isolated in-memory fixtures. No model was called by the exercised application paths; `Engine.ask` sets `use_llm=False` (`src/app.py:180-181`). Application SQLite is not globally opened read-only, so this is executed-path and hash evidence, not a database-permission claim.

Final tracked/staged diff, every tracked file's SHA-256 comparison, database hash, owned-port closure and report-link checks are recorded in [integrity_final.json](integrity_final.json). Expected unchanged database SHA-256: `7341c5a7089731f67356da5a588b269d4b69e8e6c4c054acf19aa4ef2837b529`.

Run from the repository root. The root setup copies the inspected prior scripts to m6; HTTP runners owning the same port must run sequentially. Per-worker manifests preserve the remaining reused commands.

```text
python -B audit_evidence_claims/m6/root_prepare.py
python -B audit_evidence_claims/m6/root_checks_runner.py tests
python -B audit_evidence_claims/m6/root_checks_runner.py http
python -B audit_evidence_claims/m6/root_checks_runner.py perf
python -B audit_evidence_claims/m6/confirm_http.py
python -B audit_evidence_claims/m6/carry_http.py
python -B audit_evidence_claims/m6/alias_http.py
python -B audit_evidence_claims/m6/cost_stress.py
python -B audit_evidence_claims/m6/names/run_replays.py
python -B audit_evidence_claims/m6/names/frozen_qa_relink_sweep.py
python -B audit_evidence_claims/m6/attacks/fresh_probe.py
python -B audit_evidence_claims/m6/attacks/reversed_probe.py
python -B audit_evidence_claims/m6/db_ui/db_recheck.py
python -B audit_evidence_claims/m6/db_ui/db_assertions.py
python -B audit_evidence_claims/m6/db_ui/ui_assertions.py
```

VERDICT: CHANGES REQUIRED
