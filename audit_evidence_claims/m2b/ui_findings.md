# UI and standards re-review — c64f433

Compared `git diff bfcb83d...HEAD -- web/try.html src/app.py src/query.py tests/test_app.py`; repair commits `9db058c` and `c64f433`. Re-ran the current page script, not the archived m2 page.

## Standards axis

No tracked AGENTS.md, CONTRIBUTING, CODING_STANDARDS, or `docs/agents/*` rules were found. No separate documented coding-standard violation is asserted. The user instruction forbidding tracked-file edits overrides any skill setup workflow; all artifacts from this sub-review are under `audit_evidence_claims/m2b/`. No application code was edited, so the KOA/KhOpenApi code-change comparison instruction is not applicable.

## Specification axis summary

The original role/type wording failures B2/B3 and the original UI should-fix reproductions are repaired: collaborator and lead groups are separate, Investigator headings say researcher, cuts and sort rules are disclosed, latest-request sequencing prevents stale results, failure states clear the trail, alternative readings are visible, action/class codes survive, omitted details appear, and map URLs are restricted to the registry. All 36 examples from sections 1–4 executed and rendered without exceptions. A new malformed-props path fabricates a zero sponsor count where the stored count is unavailable; this violates the value guarantee. The module introduction still says “everything” although output is capped. New association-score rendering rounds stored numbers without a precision notice; boolean scores accepted by Python's numeric check cause the page script to reject and stay in the loading state. Both malformed-property findings are in-memory fixtures, not current-database failures. See detailed evidence below.

## Original finding outcomes

| m1 finding / exact input or sequence | Outcome at HEAD | Current code / evidence |
|---|---|---|
| B2: `NCT00200395`; reverse `ORG:genentech` | **FIXED.** Genentech is in `이 임상의 협력 기관 (collaborator)`; Montefiore is in `이 임상의 책임 주관 기관 (lead sponsor)`. Genentech's outgoing trial groups distinguish leadership and collaboration. | `web/try.html:142-149`; `ui_harness_results.json` → `real.NCT00200395`, `real.ORG:genentech` |
| B3: `NCT00754364` | **FIXED.** Armando Santoro Md appears under `이 임상의 책임 주관 연구자 (lead sponsor)`. | `web/try.html:143,148`; same JSON → `real.NCT00754364` |
| Unrecorded sponsor role found in interrupted m2 | **FIXED.** `null`, empty string and unrecognized roles produce `역할 기록 없음`, without guessing collaborator. | `web/try.html:147-149`; `ui_regressions.json` → `missingRoleChecks` |
| “Most evidence” overclaim: `MONDO_0005233`, ALDESLEUKIN and ordinary groups | **FIXED for UI/explore docstring.** Trial headings state recent-start order; disease-target groups state association-score order; unweighted groups state name order. The generic evidence wording is gone. Actual sort validation is in the DB sub-review. | `web/try.html:148-157,231-235`; `src/app.py:70-78`; `ui_harness_results.json` → `real` |
| Silent ring cut: `CHEMBL1201438` | **FIXED.** 25 total / 22 drawn is explicitly shown even though all three lists are below 30. Disease shows 3,074 total / 39 drawn plus the 30-item list notices. AstraZeneca still draws 41, but there is no claimed hard 40 cap in the UI. | `web/try.html:54,191-204,233`; `ui_harness_results.json` → `real` |
| Stale trail after `osimertinib → EGFR → Mvasi`, `unknown-m1-entity`, HTTP/network error | **FIXED.** Trail array and markup become empty; invoking the old button handler does not throw. During a pending new-root lookup the old buttons can remain visible briefly, but the guard ignores them and terminal states remove them. | `web/try.html:213-216,240-241`; `ui_harness_results.json` → `failureVariants`, `pendingNewLookup` |
| Start EGFR then KRAS, complete KRAS before EGFR; two concurrent EGFR requests | **FIXED.** Final map/trail remains KRAS; stale success and stale rejection cannot overwrite it. Concurrent duplicate EGFR requests leave one trail entry. Successful back navigation also works. | `web/try.html:211-214`; `ui_harness_results.json` → `reverseResponses`, `staleError`, `doubleClick`, `backAfterSuccess` |
| Silent ambiguity: `Roche`, `MET`, `osimertinib EGFR`, `EGFR osimertinib` | **FIXED for these exact reproductions.** Current centre remains the linker's first choice, but the reading and other hit are exposed. Roche offers the Company, MET offers the Target, and multi-entity inputs offer the other entity. `Mvasi and bevacizumab` exposes the refused span. | `web/try.html:222-226`; same JSON → `real` |
| AGONIST / BINDING AGENT and collapsed sponsor classes | **FIXED.** ALDESLEUKIN's actions display `작용: 작용제 (AGONIST)`; BINDING AGENT displays its code and gloss. INDUSTRY, NIH, FED, OTHER_GOV, NETWORK, OTHER and unknown class codes remain visible. | `web/try.html:162-176`; `ui_harness_results.json` → `details`, `real.CHEMBL1201438` |
| Missing Trial centre start date; sponsor→Drug global count/max phase; zero-trial centre | **FIXED.** NCT00200395 displays `시작 2003-07-02`; AstraZeneca→osimertinib displays sponsor count 14, global count 79 and approval; CHEMBL925 displays graph trial count 0. | `web/try.html:173-174,228-229`; same JSON → `real.NCT00200395`, `real.AstraZeneca`, `real.CHEMBL925` |
| Unsafe map URL schemes (`javascript:`, `data:`) | **FIXED for map anchors.** Both centre and neighbour paths apply the registry URL allowlist. Host-prefix, credential and backslash spoof fixtures are rejected. Valid `https://clinicaltrials.gov/study/...` and the `www.` form remain clickable. | `web/try.html:180,221,230,234-235`; `ui_harness_results.json` → `urlChecks`, `injectionHTML` |
| Unknown node-type SVG tooltip showed `undefined` | **FIXED.** `Other` and raw relation `NEWREL|in` are retained in the fixture; no undefined tooltip. | `web/try.html:158,199,227`; `ui_regressions.json` → `markupChecks` |
| Module “All three” after four boxes | **FIXED.** Now “All of them”. | `src/app.py:10` |
| Module intro “everything” despite capped output | **NOT FIXED.** The module introduction at line 5 retains this overclaim; page section 0 and explore's detailed docstring now disclose cuts. This is documentation, not fabricated graph data. | `src/app.py:5`; compare `web/try.html:54`, `src/app.py:74-78` |

## New observations

### P2: missing/unparseable sponsor count is displayed as a measured zero

In a read-only backup of the real database into memory, change only `props` of edge `ORG:alaunos|SPONSORS_TRIAL_OF|CHEMBL1201438|` to the stored JSON text `null`, `[]`, or `{broken`. Exact requests are `POST /api/explore {"text":"CHEMBL1201438"}` and `{"text":"ORG:alaunos"}`. Before corruption its stored count is 1; **after corruption the count is absent/unparseable, not still 1**. For all six requests bfcb83d fails closed with HTTP 400. HEAD returns HTTP 200 with `weight:0`, and the actual current page script renders **`책임 주관한 임상 0건`**. The reverse view additionally renders the unrelated true global count 11 and approval phase.

The repair's `_obj` fallback converts malformed props to an empty dictionary (`src/app.py:129,198-204`), after which `ep.get("evidence_trials") or 0` (`src/app.py:136`) supplies a numeric zero. `web/try.html:173` presents the ranking fallback as a factual trial count. This is a new reachable wrong-value display for exactly the null/list/broken classes the brief asks to test. The `{}` case already defaulted to zero before the repair and is explicitly retained as a control, not called newly introduced. Preserve unknown/count-unavailable separately from a ranking weight, or fail with a data error; a missing value must not be stated as 0.

Evidence: `db_missing_sponsor_count.py/json` (real handler, baseline vs HEAD, isolated memory DB) and `ui_missing_sponsor_count.js/json` (actual page script and full generated markup). The current production database is unmodified and contains valid props, so this blocker is qualified as fixture-only lifecycle/data-corruption behavior.

### Association-score precision is silently changed in the displayed value

Exact production inputs `EGFR` and `KRAS` produce stored/API association scores `0.8883707400322897` and `0.8337881598550857`. The current script renders `연관 점수 0.888` and `연관 점수 0.834` in both list details and SVG tooltips. `web/try.html:176` newly calls `it.score.toFixed(3)`. The field was not shown at bfcb83d. The display does not mark this as rounding or expose the original precision elsewhere in the page.

Evidence: `ui_real_maps.json`, `ui_regressions.json` → `precision`, `ui_http_check.json` (HTTP results equal the direct fixtures). This is a presentation precision issue: the API preserves the original value, no wrong relationship is implied, and there is no claim of a changed stored value. Under a literal reading of the supplied approval bar (“a value that differs from the stored one”), exact display or an explicit approximation plus exact-value access is required; otherwise it is a should-fix precision disclosure.

### New malformed-property fixture leaves the page stuck loading

With a live `X:Target -ASSOCIATED_WITH-> Y:Disease` edge whose props are `{"association_score": true}` (also false), the actual handler returns HTTP 200 and `score:true`/`score:false`. Python accepts bool as int at `src/app.py:145`. The new `it.score.toFixed(3)` at `web/try.html:176` then throws `TypeError: it.score.toFixed is not a function`. Since only the fetch is in the try/catch (`web/try.html:213`), `explore` rejects and leaves `<p class='note'>그리는 중…</p>` on screen after already pushing a trail entry. At bfcb83d the API did not expose a score and no such renderer call existed.

Evidence: DB sub-review `db_score_fixture.py/json` runs the real handler against an isolated in-memory DB and compares bfcb83d/HEAD; `ui_regressions.js/json` reproduces the current script failure. All 300 current live association-score props are JSON real, so this is a should-fix robustness regression, not an observed current-data UI failure.

## Execution and safety evidence

- `python -B audit_evidence_claims/m2b/ui_collect.py`: 16 current map payloads, source DB opened read-only for queries.
- `node audit_evidence_claims/m2b/ui_harness.js`: entire current script parses and initializes; actual payloads and controlled response ordering drive handlers.
- `node .../ui_demos.js export`, `python -B .../ui_demos_collect.py`, `node .../ui_demos.js`: **36** actual page demos (**13** resolver, **7** questions, **9** prose checks, **7** structured checks), no Engine errors and no UI rendering errors. This verifies execution; QA semantic/baseline comparison belongs to the names sub-review.
- `python -B .../ui_http_check.py`: actual unchanged server on port 8878, **10/10** HTTP map responses equal direct fixtures; served page bytes equal `web/try.html`, SHA-256 `f91f11d7dcb2f245391ad798e0ae8f5ba3e3d92bc07f054edbb87c78d2f1c86b`.
- Markup payloads containing `<script>`, `<img onerror>`, SVG payloads, quotes and hostile ids remain escaped; edge ids remain text, not data-id values. Injected origin and alternative-match fields were included. Map URL allowlisting removes javascript/data schemes. `ui_regressions.json` records boolean assertions for these generated strings.
- README command descriptions remain accurate at `README.md:566,596`, `README.ko.md:387`.
- Browser automation was unavailable to root (`The browser access host is unavailable`; native Chrome use was not approved). This sub-review therefore proves produced strings, callback behavior, and HTTP payloads, **not browser layout or browser-executed XSS**. No browser exploit claim is made.
