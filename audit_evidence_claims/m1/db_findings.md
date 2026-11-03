# Independent DB/spec review: A/C/D

Reviewed commit `bfcb83d4320877ffad47083c102ba1c38f691bba`. Production SQLite opened with `mode=ro`; all mutations below used isolated in-memory fixtures. Reproduce scripts with `python -B audit_evidence_claims/m1/db_probe.py`, `db_validate.py`, `db_fixture.py`, and `db_http_fixtures.py`. Corresponding JSON files contain exact results.

## Approval blockers

### P1: `SPONSORS` collaborators are presented as trial leads

HTTP input `POST http://127.0.0.1:8876/api/explore` with `{"text":"NCT00200395"}` returns `Genentech` in `SPONSORS|in|Company`. `web/try.html:144` labels this group **이 임상의 주관 기관**, and the reverse direction **이곳이 주관한 임상**. However, the exact live DB edge `ORG:genentech|SPONSORS|NCT00200395|NCT00200395` stores `props.role = "collaborator"`. Montefiore Medical Center is the lead sponsor for this trial. `src/app.py:105-120` reads edge props but drops `role`; UI cannot distinguish them.

This is not merely inferred terminology: `src/graph.py:255-256` iterates both lead sponsor and collaborator, `src/graph.py:282-286` preserves the role on SPONSORS, while `src/graph.py:336-344` explicitly restricts the derived SPONSORS_TRIAL_OF relation to `role='lead_sponsor'`. The current live DB contains **1,652 collaborator SPONSORS edges and 3,000 lead_sponsor edges**. Display the stored role and use direction/type/role-specific wording (or a neutral combined heading) rather than asserting all are leads. Exact DB rows and HTTP responses: `db_fixture.json`.

### P2: Investigator is labelled as an institution

HTTP input `{"text":"NCT00754364"}` returns `ORG:armandosantoromd`, label `Armando Santoro Md`, type `Investigator`, in `SPONSORS|in|Investigator`. The same fixed GKO string at `web/try.html:144` calls the person **이 임상의 주관 기관**. The correct node type appears in TKO (`web/try.html:140`) but group headings use only `rel|dir` (`web/try.html:194`). Current DB has **43 live Investigator → SPONSORS → Trial** edges. `src/graph.py:260-269` explicitly documents and prevents treating named physicians as institutions. Use a person-appropriate or neutral heading. Evidence: `db_fixture.json` / `db_validate.json`.

### P2, isolated state robustness: retired Trial inflates a displayed drug count

Fixture has live Drug `D`, retired Trial `T`, and still-live `T -EVALUATES-> D`. `POST /api/explore {"text":"D"}` through the real `make_handler` returns 200 and `center.trials=1`, while no Trial neighbour is returned. For live Target `X` with `D -ACTS_ON-> X`, `explore('X')` gives D a trial weight of 1 as well. The neighbour query filters `n.retired_at` (`src/app.py:90-95`), but trial counting only filters edge retirement (`src/app.py:100-102`). The two displayed views therefore disagree about the live graph. Join live Trial nodes when counting.

This state is **not present in the supplied snapshot**: there are zero live edges with retired endpoints, including EVALUATES; current counts correctly exclude 18 retired EVALUATES edges. The fixture is relevant to the brief's requested retired-row/server guarantee, not evidence of current data corruption. Exact fixture and HTTP output: `db_fixture.py`, `db_fixture.json`, `db_http_fixtures.py`, `db_http_fixtures.json`.

## Should-fix wording and resilience

- **Evidence ordering claim is not accurate for all groups.** `src/app.py:74` says neighbours are ordered by evidence; `web/try.html:194` says “근거가 많은 30개만”. Trial weights are start-date strings (`src/app.py:110-112`), not evidence counts, while Target/Disease/Company ordinary edges have weight 0 (`src/app.py:116-117`) and reverse-label ties (`src/app.py:124`). For `MONDO_0005233`, 2,774 trials are headed by future start date `2027-12-01` (`NCT05745740`), and 300 associated targets are headed by `ZFHX3`, `XPC`, `VEGFA`, `USP8`, `UBR5`, all weight 0. `ASSOCIATED_WITH` even stores an association_score (EGFR 0.8883707400322897), but this is ignored. State the actual ordering per group; do not imply the selected 30 have the most evidence.
- **Malformed JSON fails closed but poorly.** Fixture neighbour/ACTS_ON edge `props='null'`, `props='[]'`, or `props='{broken'` yields HTTP 400 with AttributeError/JSONDecodeError text at `src/app.py:105`, caught by `src/app.py:208-210`. Restoring `{}` gives 200 after every failure; lock/server recover. There is no malformed/JSON-null props value in the supplied DB. This is a resilience improvement, not an observed wrong-value result.
- `ACT` key `BINDING_AGENT` (`web/try.html:149`) does not match the stored `BINDING AGENT` code; fallback preserves the raw code, so this is incomplete translation rather than false stored data. `AGONIST:"작용"` is less specific than agonist/효능제. Current non-INDUSTRY sponsor codes are FED, NETWORK, NIH, OTHER, OTHER_GOV; no UNKNOWN/null counterexample was found, although exact classes are collapsed into one Korean description.

## Positive results / scope

- Exhaustive direct `Engine.explore(id, per_group=100000)` comparison against independently assembled SQL adjacency for **all 6,469 live nodes** completed in **100.988 seconds**, with **zero** mismatches for edge/endpoint liveness, stored labels, group directions/counts, descending group size, implemented item ordering, phases/status/title/start_date/url, sponsor evidence_trials/class, non-sponsor Drug trial counts/max_phase, and ACTS_ON action. This checks retrieval/value identity, not the correctness of the Korean headings above. `db_validate.json` retains 18 centre/relation/direction/neighbor-type combinations.
- Six current node types are all covered by TKO/TCOL. No current self-loops; all observed relationship type signatures are the expected ones. PARENT_OF, STUDIES, ASSOCIATED_WITH, EVALUATES and ACTS_ON directions match stored endpoints.
- DB contains 7 retired Company nodes and 142 retired edges. They did not leak into live-neighbour output in the exhaustive checks. No live edge has a retired endpoint in the current snapshot.
- More than two count chunks tested: isolated Target `X` with **1,001 Drug neighbours**, each evaluated by its own trial. `per_group=2000` returned 1,001 items, every weight exactly 1. Chunking at 500 works (`src/app.py:98-102`).
- Direct Disease input `MONDO_0005233` takes **47.2 ms** in one measured call, returns **17,158 UTF-8 JSON bytes**, and reports totals 2,774 Trial + 300 Target while retaining 30 items per list. This is a single local measurement, not a performance benchmark.
- `drawMap` allocation takes at least 3 available items per nonempty group (`web/try.html:164`), so no nonempty group can be entirely hidden by that allocation. It can show fewer items than the lists, and the global “all” wording does not disclose that extra cut; defer visual wording details to the UI reviewer. Defaults preserve true list totals.

No tracked files were edited by this reviewer. Scripts and outputs exist only under `audit_evidence_claims/m1/`.
