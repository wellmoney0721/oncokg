# Independent verification — relation map, bfcb83d

Reviewed HEAD: `bfcb83d4320877ffad47083c102ba1c38f691bba`, on 2026-11-03.

**Approval is blocked.** With the supplied database, the page can draw a refused distinct product/tracer as its originator, and can describe a stored trial collaborator as the lead sponsor. These are independently reproducible without changing any application or database file. Retirement fixtures expose two additional inconsistencies. Passing tests do not cover these cases.

## Scope, method, and limitations

- Reviewed the commit's five changed files and the relevant linker/graph-building code. The user brief is the specification; its local copy is [brief.md](brief.md).
- Ran the requested command, `python -m pytest tests -q -p no:cacheprovider`, with bytecode writing disabled: **317 passed, 1 warning, 8.97 s**. The warning is a `cp949` decoding failure in a subprocess reader thread during `test_correction_check_fails_when_a_correction_is_pending`; it is not a failing assertion. Full output: [pytest.txt](pytest.txt).
- Started the unchanged application with `python -u src/app.py 8876`; exercised `GET /` and `POST /api/explore` over HTTP. The served page is byte-for-byte equal to `web/try.html`. The audit server was stopped afterward, and port 8876 was verified closed. Results and exact inputs: [http_results.json](http_results.json), [http_audit.py](http_audit.py).
- Compared `Engine.explore(id, per_group=100000)` against independently assembled database adjacency for **all 6,469 live nodes**, covering **18 centre/relation/direction/neighbour-type combinations**. This found **zero raw retrieval/value mismatches** in the current snapshot. It verifies stored relationships and values, not the correctness of the Korean wording or the claimed evidence ranking. Evidence: [db_validate.py](db_validate.py), [db_validate.json](db_validate.json).
- Retirement and malformed-property mutations occurred only in isolated in-memory databases. The real database was not changed. Source review, HTTP requests and fixture work called no model.
- Executed the actual page script in a Node VM with minimal DOM stubs and controlled HTTP response completion. Normal map payloads were also compared with actual HTTP results. This reproduces rendering strings, allocation, event handlers and asynchronous state; **it is not a real-browser rendering or exploit test**. Both available browser/native automation paths failed: `The browser access host is unavailable` and native pipe `os error 2`. No screenshot, browser-executed XSS, or browser layout claim is made. Dark mode was out of scope.
- No tracked file was edited. All review-created files are under `audit_evidence_claims/m1/`. An unrelated untracked `audit_evidence_claims/resume1/` directory appeared during review and was not touched. Git and database integrity results are recorded in [integrity.json](integrity.json).

## Standards review

No tracked `AGENTS.md`, `CONTRIBUTING`, or coding-standards document was found. The user-supplied instructions to ground conclusions in evidence and avoid tracked-file edits were followed. No separate coding-standard violation is asserted. The KOA/KhOpenApi code-change comparison instruction does not apply: this audit changes no application code.

## Specification blockers

### B1 — P1: refused products and tracers become originator maps

Exact live-server reproductions:

| POST `/api/explore` JSON | Actual HTTP 200 result | Independent existing resolver result |
|---|---|---|
| `{"text":"bevacizumab - awwb"}` | `BEVACIZUMAB`, `CHEMBL1201583`, 122 trials | `Engine.resolve`: `BLOCKED_DISTINCT_PRODUCT`; full-string `is_distinct_product` is true |
| `{"text":"89Zr - trastuzumab"}` | `TRASTUZUMAB`, `CHEMBL1201585`, 13 trials | `BLOCKED_CLASS_TERM`; full-string `is_radiotracer` is true |
| `{"text":"[89Zr] trastuzumab"}` | Same trastuzumab originator | Same tracer refusal |

Controls `bevacizumab-awwb` and `[89Zr]trastuzumab` are refused. Thus merely separating punctuation/qualifiers changes a refused product into the originator's relationship map.

**Cause:** `src/query.py:127-132` checks refusal on individual tokens. `src/query.py:146-168` subsequently joins matching windows and accepts aliases without applying the refusal checks to those windows. `src/app.py:81-88` trusts the first accepted hit. This is an inherited linker weakness exposed by the new map, not a claim that the tokenization bug originated in this commit. The map's promised product separation is nevertheless false (`src/app.py:72-74`, `web/try.html:184`).

**Required outcome:** accepted names must satisfy the same product/tracer boundaries as the existing resolver, including spaced and Unicode punctuation variants, before choosing a centre. Do not return an originator map for these exact inputs.

Evidence: [names_product_probe.py](names_product_probe.py), [names_product_bypass.json](names_product_bypass.json). No external pharmacology assumption is needed: the repository's own refusal predicates and resolver identify the prohibited product/tracer.

### B2 — P1: collaborator is described as the trial lead

POST `{"text":"NCT00200395"}`. The returned `SPONSORS|in|Company` group includes Genentech. The page labels that group **“이 임상의 주관 기관”**.

The exact live database edge is:

```text
ORG:genentech|SPONSORS|NCT00200395|NCT00200395
src = ORG:genentech
dst = NCT00200395
props.role = collaborator
retired_at = NULL
```

Montefiore Medical Center is stored as this trial's `lead_sponsor`. The page erases this distinction. In the reverse view it also calls a collaborator's trial **“이곳이 주관한 임상”**.

**Cause and evidence for the distinction:** `src/graph.py:255-256` processes both lead sponsors and collaborators; `src/graph.py:282-286` stores their role. `src/graph.py:336-344` deliberately restricts the derived `SPONSORS_TRIAL_OF` relation to `lead_sponsor`. But `src/app.py:105-120` omits `SPONSORS.role`, and `web/try.html:144,194` applies the same lead-sponsor wording to all such edges. The supplied graph contains **1,652 live collaborator SPONSORS edges**, alongside 3,000 lead-sponsor edges.

**Required outcome:** preserve and display the role, using accurate incoming/outgoing wording or a neutral combined heading. A collaborator must not be asserted to be the lead.

Evidence: [db_fixture.json](db_fixture.json), [ui_real_maps.json](ui_real_maps.json), [ui_harness_results.json](ui_harness_results.json).

### B3 — P2: investigator is described as an institution

POST `{"text":"NCT00754364"}`. The group `SPONSORS|in|Investigator` contains `ORG:armandosantoromd`, **Armando Santoro Md**, but its heading is again **“이 임상의 주관 기관”**. This is a person, not a stored Company/institution. There are 43 live Investigator → SPONSORS → Trial edges.

`src/graph.py:260-269` deliberately distinguishes people from institutions. `web/try.html:140` has the correct Investigator translation, but `web/try.html:144,194` selects the heading using only relation and direction. This is a concrete type/relationship wording failure within the requested Investigator-vs-Company check.

**Required outcome:** use person-appropriate or neutral wording for this group. Evidence: [db_fixture.json](db_fixture.json), [ui_harness_results.json](ui_harness_results.json).

### B4 — P2, isolated retirement state: a retired centre returns through name lookup

The supplied snapshot has no retired Drugs. To test the requested retirement behavior, [names_retired_http.py](names_retired_http.py) backs up the real database into memory and applies only:

```sql
UPDATE node SET retired_at='AUDIT_FIXTURE' WHERE id='CHEMBL3353410';
```

Through the real HTTP handler:

- POST `{"text":"osimertinib"}` returns HTTP 200 with that **retired** centre and four groups with totals **79, 53, 1, 1**.
- POST `{"text":"CHEMBL3353410"}` returns `not_found`.
- An `EGFR` query excludes the retired drug as a neighbour.

`src/app.py:76-77` checks retirement only for the exact-ID path. Dictionary-based name resolution bypasses that check, and the final node query at `src/app.py:89` has no retirement predicate. Thus a retired node can still be explored by name, despite being excluded by ID and from its neighbours' maps.

**Required outcome:** apply a live-node check to the resolved centre regardless of resolution path. This is a reproduced lifecycle defect, **not current-snapshot retired-drug leakage**. Evidence: [names_retired_http_results.json](names_retired_http_results.json).

## Additional retirement-count defect

An isolated fixture has live Drug `D`, retired Trial `T`, live `T -EVALUATES-> D`, and live `D -ACTS_ON-> X`. Real-handler POST `{"text":"D"}` returns `center.trials=1` while excluding T from the groups; POST `{"text":"X"}` gives D a trial weight of 1.

`src/app.py:100-102` counts live EVALUATES edges without checking their source Trial, whereas `src/app.py:90-95` excludes retired neighbour nodes. If “이 그래프 안 임상” means the displayed live graph, this is an incorrect live-trial count and should be fixed by using live Trial endpoints. If the intended definition is explicitly *all non-retired EVALUATES rows even when their trials are retired*, the count matches that narrower SQL definition, but the page needs to state that distinction. This finding does not depend on any retired edge being counted: retired edges themselves are correctly excluded.

**Current-snapshot qualification:** there are zero live edges with retired endpoints, so this inconsistency is not present in the supplied database. Evidence: [db_fixture.json](db_fixture.json), [db_http_fixtures.json](db_http_fixtures.json). The verdict already fails on B1–B3 independently of this counting-contract interpretation.

## Should-fix findings

| Finding and exact reproduction | Evidence / code |
|---|---|
| **“Most evidence” is not the implemented ordering.** `MONDO_0005233` selects trials by descending start-date string, led by `NCT05745740` / `2027-12-01`. Its 300 associated Targets have weight 0 and are selected by reverse label order (`ZFHX3`, `XPC`, …), ignoring stored association scores. Sponsor-derived groups do use `evidence_trials`; ordinary Drug groups use EVALUATES counts. Describe each actual sort instead of implying every retained item has the most evidence. | `src/app.py:74,108-124`; `web/try.html:194`; [db_validate.json](db_validate.json) |
| **The ring silently cuts further than the lists.** `CHEMBL1201438` / ALDESLEUKIN returns 25 items (11 trials, 11 sponsors, 3 targets), all lists below 30, but `drawMap` draws only 22 neighbours. No list truncation notice appears, while the introduction says “모두 그립니다”. Show ring drawn/total separately. No whole nonempty group is lost: the allocation takes at least 3 available items from each. `MAX=40` is not a hard cap; AstraZeneca draws 41. | `web/try.html:54,160-165,194`; [ui_harness_results.json](ui_harness_results.json) |
| **Stale trail buttons fail after refusal/not-found/error.** Navigate osimertinib → EGFR, then submit Mvasi, `unknown-m1-entity`, or a request returning an error in the VM harness. Submission clears the trail array, but the early return leaves old buttons. Clicking old back index 0 throws `TypeError: Cannot read properties of undefined (reading '0')`. | `web/try.html:183-188,199-202`; [ui_harness.js](ui_harness.js), [ui_harness_results.json](ui_harness_results.json) |
| **Overlapping responses can replace the latest selection with an older one.** Start EGFR then KRAS; complete KRAS before EGFR. The final map becomes EGFR and the trail follows completion order. Two overlapping EGFR calls append duplicate entries. This is a deterministic controlled-response reproduction, not a claim that network reordering was observed in the browser. | `web/try.html:181-197,200`; [ui_harness_results.json](ui_harness_results.json) |
| **Identity ambiguity is silent.** `Roche` draws FOLIC ACID (`CHEMBL1622`), whereas `ORG:roche` draws the company. `MET` selects METFORMIN. `osimertinib EGFR` selects osimertinib; reversing the order selects EGFR. These reflect stored aliases/linker priority, so they are not fabricated edges, but show the selected match and alternatives or require an explicit choice. | `src/query.py:155-187`; `src/app.py:82-88`; [names_results.json](names_results.json), [names_label_scan.json](names_label_scan.json) |
| **Action/class rendering loses specificity.** ALDESLEUKIN has three `AGONIST` target edges, rendered as “작용: 작용”. Preserve `AGONIST` or a specific Korean label. `BINDING_AGENT` does not match stored `BINDING AGENT`; raw-code fallback is accurate but untranslated. Sponsor classes are collapsed into INDUSTRY/non-industry wording; actual codes FED, NETWORK, NIH, OTHER, OTHER_GOV are not visible. No current UNKNOWN-class counterexample was found. | `web/try.html:149-155`; [ui_harness_results.json](ui_harness_results.json), [db_probe.json](db_probe.json) |
| **Some stored details are omitted.** A centre Trial's `start_date` is returned but not displayed. A Drug under a sponsor's `SPONSORS_TRIAL_OF` group shows sponsor-specific trial count/class, omitting that Drug's global count/max phase because the sponsor branch wins. These are omissions, not altered stored values. Zero-trial Drug centres return `trials:null`, omitting the count rather than showing 0. | `src/app.py:107-115,130-133`; `web/try.html:151-155,191-192` |
| **Malformed props fail closed, but with raw implementation errors.** In isolated real-handler fixtures, node/edge props `null`, `[]`, and `{broken` return 400 with AttributeError/JSONDecodeError text. Each restored request returns 200, so the lock recovers. Validate object shape or provide a clearer data-error response. None of these invalid props occur in the supplied snapshot. | `src/app.py:105,128,208-210`; [db_http_fixtures.json](db_http_fixtures.json) |

### URL safety qualification

`esc` protects label/title/id text and quoted attributes in the tested HTML/SVG payloads. Node IDs, not edge IDs, populate `data-id`; edge IDs are escaped text (`web/try.html:171,195-196`). No markup/attribute breakout was found for the tested `<script>`, `<img onerror>`, quotes, or SVG-title payloads.

However, `web/try.html:193,196` applies HTML escaping to URLs without a scheme allowlist. Supplying fixture `props.url = "javascript:alert(document.domain)"` leaves that exact scheme in both generated anchors. **This establishes unsafe URL acceptance, not confirmed JavaScript execution**: the links have `target="_blank" rel="noopener"`, and browser navigation behavior was not tested because the browser tools were unavailable. All **3,000 current stored node URLs** use `https://clinicaltrials.gov/study/`; no current malicious stored URL was found ([url_scan.json](url_scan.json)). Restrict allowed URL schemes and test in a real browser before claiming universal injection safety. Evidence: [ui_harness_results.json](ui_harness_results.json).

## Coverage and successful checks

### A / C — graph membership, directions, values

- Current DB has **7 retired Company nodes and 142 retired edges**, including 18 retired EVALUATES edges. They did not leak into current live-neighbour results. No current self-loop or edge with both ends equal to a centre was found. The SQL's self-loop behavior is one outgoing item, not two copies (`src/app.py:93,120`); this was inspected, not a current-data reproduction.
- All six current node types are in TKO/TCOL. No current uncovered type was found. Unknown future types use raw/fallback labels in some places but yield `undefined` in the SVG tooltip; extensibility is not proved.
- PARENT_OF, STUDIES, ASSOCIATED_WITH, EVALUATES and ACTS_ON directions match their stored endpoints. Examples retained in `db_validate.json` include parent and child Company views, Trial→Disease, Disease→Trial, Target→Disease and Disease→Target. The SPONSORS wording failures are B2/B3; its raw direction is correct.
- Returned trial phases/status/start/title/url, non-sponsor Drug max phase/count, sponsor `evidence_trials`/class, and ACTS_ON action agree with stored data. Group totals and descending group sizes are correct. Raw ordering agrees with the implemented weights, with the wording qualification above.
- A **1,001-Drug** fixture spans three count chunks. `explore('X', per_group=2000)` returns all 1,001 items with weight exactly 1; no chunk boundary failure was found (`src/app.py:98-102`, [db_fixture.json](db_fixture.json)).

### B — names and boundaries

- `Mvasi` and `Mvasi bevacizumab` refuse; `no such thing zz` is not found. `Mvasi and bevacizumab` selects the explicitly named bevacizumab but omits the refused span from the response. This is incomplete disclosure, distinct from B1's product-to-originator bypass.
- Salt and parent records remain distinct: Tarceva / erlotinib hydrochloride → `CHEMBL1079742` (31 trials); erlotinib → `CHEMBL553` (118).
- `  OsImErTiNiB\n` works over HTTP; fullwidth `ＡＶＡＳＴＩＮ` resolves. Lowercase NCT IDs are not recognized. Investigator IDs work, but investigator names are absent from the linker. These are usability limitations, not invented relationships.
- Current company index has **zero** multi-ID alias entries, so the loss of `also_matching_ids` has no supplied-snapshot reproduction. The code does discard it. No claim is made that this ambiguity cannot arise after a rebuild.
- HTTP input is stripped and silently truncated to 500 characters (`src/app.py:182`). Exact input `"x" * 500 + " osimertinib"` returns not_found for the 500-character prefix; `"osimertinib " + "x" * 600` draws osimertinib. This should be disclosed or rejected explicitly.

### D / F — size, errors, concurrency

- Disease `MONDO_0005233`: **2,774 Trials + 300 Targets**, 30 returned per list, **17,158 UTF-8 response bytes**, **77.319 ms** in the recorded ordinary HTTP call. The ring contains 39 neighbours; list totals remain true. This is one local timing, not a load benchmark.
- Empty object/text, whitespace and null text return **400** with `empty input`; malformed JSON returns 400. A 21,000-character text body returns 400 because only the first 20,000 bytes are parsed. JSON list/null bodies return 400 with raw `.get` errors. Valid text at an unknown route returns 404. Subsequent requests remain usable.
- **24 simultaneous requests with 12 workers**, mixing drugs, targets, a company, a refused name, Disease and Trial, all returned the expected 200 response shapes in **633.145 ms** total. `src/app.py:188-204` serializes engine work with the lock. This shows the exercised workload succeeds; it does not imply concurrent UI responses are ordered.

### E / G — read-only behavior and documentation

- The explore path issues SELECTs, and `link_entities` reads cached dictionaries/SELECTs; no model call occurs. Existing question answering explicitly sets `use_llm=False` (`src/app.py:136-137`). Database SHA-256 before and after the HTTP run was identical: `7341c5a7089731f67356da5a588b269d4b69e8e6c4c054acf19aa4ef2837b529`. The connection is opened read/write (`src/app.py:39`), so read-only behavior is observed/code-path based, not enforced by SQLite mode.
- README command descriptions at `README.md:566` and `README.ko.md:387` accurately advertise a relation-map page; no additional blanket accuracy claim was found in those lines.
- Module `src/app.py:5` and `explore`'s `src/app.py:70-74` overstate “everything” and evidence ordering when paired with capped output. `web/try.html:54` overstates the ring's completeness. Explain the two cuts and per-relation sorting. `src/app.py:10` also says “All three” after introducing four boxes, a minor pre-existing documentation inconsistency.
- PH renders stored trial phase codes without finding a false phase translation in current data; unmapped codes such as `NA` stay raw. ACT and sponsor-class qualifications are listed above.

## Reproduction artifacts

Run the unmodified server on port 8876 for live-HTTP scripts; the retirement fixture scripts start and stop their own ephemeral servers. Use `python -B` or set `PYTHONDONTWRITEBYTECODE=1` to keep bytecode out of tracked directories.

```text
python -B audit_evidence_claims/m1/http_audit.py
python -B audit_evidence_claims/m1/names_product_probe.py
python -B audit_evidence_claims/m1/names_retired_http.py
python -B audit_evidence_claims/m1/db_validate.py
python -B audit_evidence_claims/m1/db_fixture.py
python -B audit_evidence_claims/m1/db_http_fixtures.py
node audit_evidence_claims/m1/ui_harness.js
```

Supporting independent notes: [names_findings.md](names_findings.md), [db_findings.md](db_findings.md), [ui_findings.md](ui_findings.md). No remediation was applied in this review.

VERDICT: CHANGES REQUIRED
