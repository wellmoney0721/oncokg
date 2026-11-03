# Independent relation-map review — round 10

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

### M1

| Finding / reproduction | Current result |
|---|---|
| B1 `bevacizumab - awwb`, `89Zr - trastuzumab`, `[89Zr] trastuzumab` | **FIXED** — refusal, no centre. [Original script replay](names/m1_exact/names_product_bypass.json), [HTTP](root_checks/regression_http.json). |
| B2 collaborator called lead: `NCT00200395`, reverse `ORG:genentech` | **FIXED** — Genentech collaborator / Montefiore lead, both directions. `src/app.py:137,160-169`; `web/try.html:142-149`. [DB](db_ui/db_assertions.json), [rendered UI](db_ui/ui_harness_results.json). |
| B3 Investigator called institution: `NCT00754364`, `ORG:armandosantoromd` | **FIXED** — person-specific heading. `web/try.html:143,148`. [DB](db_ui/db_assertions.json), [rendered UI](db_ui/ui_harness_results.json). |
| B4 retire CHEMBL3353410 in memory; query name, ID, EGFR | **FIXED** — name/ID not_found; retired neighbour excluded. `src/app.py:115-118`. [Original HTTP fixture](names/m1_exact/names_retired_http_results.json). |
| Retired Trial included in live Drug count | **FIXED** — centre count and neighbour count/weight 0. `src/app.py:129-132,139,174`. [Fixtures](db_ui/db_fixtures.json). |
| S1 misleading most-evidence wording/order, Disease | **FIXED** — actual start-date/score/count/A–Z sort disclosed and verified. `src/app.py:141-170`; `web/try.html:148-158,231-235`. [Oracle](db_ui/db_validate.json). |
| S2 silent ring cuts: ALDESLEUKIN, Disease, AstraZeneca | **FIXED** — 22/25, 39/3,074, 41/145 drawn disclosed; cut lists say 30. [UI](db_ui/ui_harness_results.json). |
| S3 stale trail after refusal/not-found/server/network error | **FIXED** — state/buttons clear, obsolete back harmless. `web/try.html:213-216,243-244`. [UI](db_ui/ui_harness_results.json). |
| S4 reverse-completed EGFR/KRAS requests and concurrent duplicate EGFR | **FIXED** — latest KRAS stays, duplicate gives one trail entry. `web/try.html:211-214`. [UI](db_ui/ui_harness_results.json). |
| S5 silent ambiguity: Roche, MET, osimertinib EGFR/reversal, Mvasi and bevacizumab | **FIXED for disclosure** — selected reading/alternatives/refusal visible. `src/app.py:95-114`; `web/try.html:222-226`. [Names](names/names_reproduction_results.json). |
| S6 action/class specificity | **FIXED** — specific gloss and original AGONIST/BINDING AGENT/class codes. `web/try.html:162-176`. [UI](db_ui/ui_harness_results.json). |
| S7 start date, sponsor-to-Drug global count/phase, zero-trial Drug | **FIXED** — NCT00200395 start 2003-07-02; osimertinib sponsor 14/global 79/APPROVAL; CHEMBL925 count 0. [DB](db_ui/db_assertions.json), [rendered UI](db_ui/ui_harness_results.json). |
| S8 node/edge props null, list, broken JSON | **FIXED** — 12 original requests and restorations return 200. `src/app.py:211-217`. [Fixtures](db_ui/db_fixtures.json). |
| Hostile labels/titles/IDs/URLs; scheme/host/credential/backslash probes | **FIXED for exercised markup paths** — escaping and HTTPS registry allowlist; browser limitation above. `web/try.html:104,180,199,221-235`. [Assertions](db_ui/ui_assertions.json). |
| Unknown type Other / relation NEWREL | **FIXED** — raw fallback, no undefined tooltip. [UI](db_ui/ui_regressions.json). |
| All three / everything documentation overclaims | **FIXED** — All of them / a capped list per relation. `src/app.py:5-11`. |
| Silent 500-character cut: `"x"*500 + " osimertinib"`, `"osimertinib " + "x"*600` | **FIXED** — explicit HTTP 400, no partial map. `src/app.py:239-243`. [HTTP](root_checks/http_results.json). |
| Lowercase IDs / Investigator names: nct00200395, chembl3353410, Armando Santoro Md | **NOT FIXED**, unchanged usability limit. [Controls](names/names_unsupported_forms.json). |
| Raw list/null/malformed JSON/oversized-body errors | **NOT FIXED**, unchanged controlled 400 exposing parse/attribute details; subsequent valid requests succeed. `src/app.py:237-239,267-269`. [HTTP](root_checks/http_results.json). |

### M2b

| Finding / reproduction | Current result |
|---|---|
| R1 `osimertinib and generic version of bevacizumab`, reverse/comma, trial/sponsor QA | **FIXED** — only separate osimertinib; correct evidence. [HTTP](root_checks/regression_http.json), [supplement](root_checks/supplemental_http.json). |
| R1 tracer/oral-product collateral refusal, both orders | **FIXED** — `[89Zr] trastuzumab and osimertinib` and `osimertinib and oral azacitidine` retain osimertinib. [Names](names/names_regressions.json). |
| Inherited `What is the generic version of bevacizumab?` | **FIXED** — refusal, no centre; also M3-B2. [HTTP](root_checks/supplemental_http.json). |
| R2 missing sponsor count, Alaunos–ALDESLEUKIN edge, both endpoints and null/list/broken/empty props | **FIXED** — null/zero sort weight; UI unknown, numeric 0 stays 0. `src/app.py:141-146`; `web/try.html:173`. [Fixture](db_ui/db_missing_sponsor_count.json). |
| Bool association score and hidden precision rounding | **FIXED** — bool null/weight 0; exact EGFR/KRAS decimal values retained. [DB](db_ui/db_score_fixture.json), [UI](db_ui/ui_regressions.json). |
| Embedded multi-ID `Sharedbrand company` fixture | **FIXED** — Roche disclosed alongside selected AstraZeneca. `src/app.py:97-102`. [Fixture](names/names_boundary_details.json). |
| Missing/unknown SPONSORS role and equal-weight A–Z | **FIXED** — neutral role wording, both directions/types; ordering verified. [DB/UI](db_ui/db_assertions.json). |
| Trial phases='PHASE2' render exception, four entry routes | **FIXED** — caught error, cleared trail, recovery/stale suppression. [Callbacks](db_ui/ui_m3_checks.json). |
| Residual module wording / successful-input truncation | **FIXED** — individual M1 rows above. |

### M3 and M4

| Finding / reproduction | Current result |
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
| M4 no-relink QA assessment | **FIXED / retained** — exact frozen 1,648-input counterfactual, 64 identical / 1,560 metadata-only / 24 semantic differences / 0 errors; adapted matcher target is `_link`. [Result](names/adapted_frozen_qa_relink_sweep.json). |
| M3/M4 blank/whitespace form | **NOT FIXED**, unchanged usability limit: no request, previous view stays. `web/try.html:241`. [UI](db_ui/ui_m3_checks.json). |
| M3/M4 positive/negative Infinity fixture | **NOT FIXED**, unchanged failure closed: controlled HTTP 400, no invalid value drawn, none in snapshot. `src/app.py:207-208,264-269`. [Fixture](db_ui/db_numeric_fixture.json). |
| Repeated lowercase-ID/name and raw request qualifications | **NOT FIXED**, same individual M1 rows above. |

### M5 and M6

| Finding / reproduction | Current result |
|---|---|
| M5-B1 reported attached slash/pipe and internal both-sides-glued attack | **FIXED** — `bevacizumab-awwb/ osimertinib` and `bevacizumab - awwb/osimertinib` select only OSIMERTINIB and expose refusal; pipe counterparts too. [HTTP](root_checks/m5_http.json), [m6 replay](root_checks/confirm_http.json). |
| M5-B2 `liposomal and nanoparticle formulation of doxorubicin`, plural/sustained-release | **FIXED** — forward qualifier carry refuses product; QA 0. [HTTP](root_checks/m5_http.json). |
| M5-S1 `biosimilar anastrozole, Arimidex`; `biosimilar Prolia, xgeva` | **FIXED** — separate aliases survive; 2/3 trial rows. [HTTP](root_checks/cross_item_http.json). |
| M5-S1 `Erlotinib, hydrochloride biosimilar bevacizumab`, semicolon | **FIXED** — original qualified comma/semicolon inputs preserve CHEMBL553; the simplified comma-list M7 regression is also repaired. [Exact HTTP](root_checks/m5_http.json), [M7 controls](names/historical_focus.json). |
| M5-S2 Pegylated interferon alfa-2a | **NOT FIXED — accepted known over-refusal**, not a new blocker. Canonical name/ID work. [HTTP](root_checks/m5_http.json). |
| M5-S3 all-substring cubic work / 999-character plain-answer timeout | **FIXED for exact previous cost cases** — bounded predicate work and original plain-answer requests complete. Repeated-piece overhead also repaired; the cache-boundary failure is now also repaired (M8-S1 below). [Original HTTP](root_checks/perf_check_http.json), [current instrumentation](cost/perf_current.json). |
| M6-B1 interior slash/pipe | **FIXED** — separate osimertinib retained; forbidden originator absent from QA. [Exact HTTP](root_checks/confirm_http.json), [39-case matrix](names/focused_matrix.json). |
| M6-B2 U+3002 suffix punctuation, trailing em dash/hyphen, leading hyphen | **FIXED** — all four original edge-punctuation inputs refuse, as do trial/sponsor QA. [Exact HTTP](root_checks/confirm_http.json), [current focused stages](names/historical_focus.json). |
| M6-B2 supplementary bracketed/Unicode variants | **FIXED** — whole-product wrappers `(bevacizumab-awwb)` / `[bevacizumab-awwb]` and the previously reported Unicode hyphens now refuse; question-mark and quoted shortcut cases also refuse. [Historical matrix](names/historical_focus.json), [m7 attack HTTP](names/m7_attacks/http_results.json). |
| M6-B3 `doxorubicin (nanoparticle and liposomal formulation)` / `bevacizumab (investigational and biosimilar)` | **FIXED** — both parenthesized reversed qualifiers produce no centre or QA evidence. [Exact HTTP](root_checks/carry_http.json), [stages](names/historical_focus.json). |
| M6 non-parenthetical reversed-qualifier supplement | **NOT FIXED as original expectation; accepted current item-policy consequence** — `doxorubicin in nanoparticle and liposomal formulations` still selects doxorubicin after listing-word separation. [Exact HTTP](root_checks/reverse_http.json). |
| M6-S1 six complete stored aliases returning another Drug ID | **FIXED for all six bare inputs** — intended stored IDs retained. [Current stages](names/historical_focus.json), [HTTP](root_checks/alias_http.json). |
| M6-S1 prefixed QA using those comma-containing names | **NOT FIXED — current whole-input-only design consequence**. ENDOSTATIN prefixed QA still selects CHEMBL4297747 with 2 rows; Rapamycin prefixed QA CHEMBL413 with 5 rows. [Exact HTTP](root_checks/alias_http.json), [direct QA](names/historical_focus.json). |
| M6 associated lone stored-alias losses | **FIXED for all 19 non-M5-S2 historical lost aliases** — slash/joiner names restored; known M5-S2 still refuses. M9-S1 is individually classified below; its three accepted over-refusals remain. [Exact previous/current alias comparison](names/alias_regressions.json), [complete current sweep](names/adapted_names_m5_summary.json). |
| M6 split_2000 / many-piece cost control | **FIXED for exact repeated-piece cost control** — current resolver skips no-drug pieces and deduplicates; the previous per-piece delay is gone. [Exact stress replay](cost/cost_stress.json), [old/current samples](cost/fresh_cost_comparison.json). |

### M7

| Finding / reproduction | Current result |
|---|---|
| M7-B1 Whole-name refusal bypass: `bevacizumab-awwb?`, `bevacizumab-awwb!`, quoted form | **FIXED** — All return refusal/no centre; trial and sponsor QA zero. [Current stages](names/historical_focus.json), [original m7 HTTP replay](names/m7_attacks/http_results.json). |
| M7-B2 Wrappers and Unicode hyphens: `(bevacizumab-awwb)`, `[bevacizumab-awwb]`, U+2011 suffix and bio-similar | **FIXED** — All named inputs refuse after shared normalization and edge stripping; no originator QA. [Stages](names/historical_focus.json), [HTTP](names/m7_attacks/http_results.json). |
| M7-B3 Whitespace isotope: `89Zr trastuzumab` | **FIXED** — No centre; both QA forms have zero evidence. [Stages](names/historical_focus.json), [HTTP](names/m7_attacks/http_results.json). |
| M7-S1 Canonical equality too broad: `Erlotinib, hydrochloride`, `osimertinib,mesylate`, `is a` | **FIXED** — Respectively CHEMBL553, CHEMBL3353410 and not_found; actual exact aliases retain intended IDs. [Current controls](names/historical_focus.json), [HTTP](names/m7_attacks/http_results.json). |
| M7-S2 Lone exact stored names: `(E/Z)-AFATINIB`, `RO 09-1978/000`, `Anusol plus hc` and 19-alias set | **FIXED** — All 19 old non-M5-S2 losses restored; three named controls select CHEMBL1173655 / CHEMBL1773 / CHEMBL389621. [Exact previous/current comparison](names/alias_regressions.json), [HTTP](names/alias_http.json). |
| M7-S3 Repeated identical-piece full resolver cost / queued ordinary map | **FIXED** — Exact old repeated-x controls and corresponding requests complete with materially reduced work. The cache failure is now repaired (M8-S1 below); unique-piece cost is reported below. [Cost replay](cost/cost_stress.json), [comparison](cost/fresh_cost_comparison.json), [HTTP](cost/fresh_cost_http.json). |


### M8

| Finding / exact reproduction | Round 10 disposition |
|---|---|
| M8-B1 `[89 Zr] trastuzumab`, tab/newline/NBSP between mass and element | **FIXED** - no centre; trial/sponsor QA zero. Recorded `radiotracer_guard` honored at `src/query.py:214-219`; adjacent alnum labels checked at `248-255`. [Replayed stages](names/attacks/probe_results.json), [HTTP](root_checks/new_http.json). |
| M8-B2 `bevacizumab-(awwb)`, `bevacizumab-[awwb]`, separate-osimertinib variant | **FIXED** - product refused; separate OSIMERTINIB survives; qualified-product QA zero. `src/query.py:125-138`. [Stages](names/attacks/probe_results.json), [HTTP](root_checks/new_http.json). |
| M8-B3 U+2E3A `bevacizumab⸺awwb`; all 26 Unicode Pd characters | **FIXED** - all 26 fold to hyphen and refuse; no originator centre. `src/query.py:100-117`. [All Pd results](names/attacks/unicode_dashes.json), [HTTP](root_checks/new_http.json). |
| M8-S1 4,097th cache entry; original 7,511-key alias sweep | **FIXED** - 82 successful requests fill 4,096 distinct pieces; first `osimertinib` and retry both HTTP 200 / CHEMBL3353410 / 79 trials. Original and adapted alias sweeps finish without cache errors. `src/query.py:197-205`. [Natural HTTP](cost/cache_boundary_http.json), [name runs](names/round9_execution.json). |
| M8-S2 `biosimilar, and osimertinib`, `biosimilar; and osimertinib`, `biosimilar and, osimertinib` | **FIXED** - all preserve CHEMBL3353410; the first comma-and form has 12 trial and 12 sponsor QA rows. Carry now requires equal comma/semicolon clause IDs at `src/query.py:337-339`. [HTTP](root_checks/new_http.json), [replayed stages](names/attacks/probe_results.json). |
| M8-S3 `566C`, `9-ac`, `5ac` | **FIXED** - correct CHEMBL1450 / CHEMBL274070 / CHEMBL1489, HTTP 200. `src/query.py:206-219,248-252`. [Alias HTTP](names/alias_checks/new_http.json). |
| M8-S4 `5.BETA.,20-EPOXY-1,2.ALPHA.,4,7.BETA.` | **FIXED** - PACLITAXEL / CHEMBL428647, HTTP 200. Stored/input punctuation stripped symmetrically at `src/query.py:266-271`. [Alias HTTP](names/alias_checks/new_http.json). |

### M9

| Finding / exact reproduction | Round 10 disposition |
|---|---|
| M9-B1 `bevacizumab_awwb`, `bevacizumab__awwb`, accented/decomposed `bevácizumab-awwb`, dotted suffix | **FIXED** — exact reported forms refuse; separate osimertinib survives; trial/sponsor QA has no forbidden originator evidence. Guards now use accent/punctuation folding and same-drug suffix keys at `src/query.py:125-138,238-247`. [Exact M9 matrix](names/m9_attacks/probe_results.json), [HTTP](names/m9_attacks/http_results.json), [root confirmation](root_checks/independent_http.json). |
| M9-B2 `[89.Zr] trastuzumab`, `89:Zr trastuzumab`, `89::Zr` variants | **FIXED** — no centre and no trial/sponsor evidence for the exact inputs. `src/query.py:248-255`. M10-B3 is a different whitespace/punctuation-token hole. [M9 stages](names/m9_attacks/probe_results.json), [HTTP](root_checks/independent_http.json). |
| M9-B3 `bevacizumab awwb`, `bevacizumab (awwb)` / `[awwb]`, `trastuzumab dkst` | **FIXED** — known suffix forms refuse, with zero originator QA. `src/query.py:238-247`. [M9 stages](names/m9_attacks/probe_results.json), [HTTP](root_checks/independent_http.json). |
| M9-S1 `Theophylline in dextrose 5% in plastic container` | **FIXED** — correct THEOPHYLLINE / CHEMBL1355736 over HTTP 200. [Alias confirmation](names/new_alias_confirmation.json), [root HTTP](root_checks/independent_http.json). |
| M9-S1 `40-o-(2-hydroxyethyl)-rapamycin` | **NOT FIXED — accepted known over-refusal**, not a blocker. EVEROLIMUS/name ID controls work. [Alias confirmation](names/new_alias_confirmation.json). |
| M9-S1 `42-o-(2-hydroxyethyl)rapamycin` | **NOT FIXED — accepted known over-refusal**, not a blocker. [Alias confirmation](names/new_alias_confirmation.json). |
| M9-S1 `Trastuzumab--vcmmae conjugate` | **NOT FIXED — accepted known over-refusal**, not a blocker. TRASTUZUMAB VEDOTIN and its ID work. [Alias confirmation](names/new_alias_confirmation.json), [root HTTP](root_checks/independent_http.json). |

## Cost, nonblocking qualifications and demos

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
