# Database and specification review - m2b

Reviewed HEAD `c64f433648ad252b24254030196048fc17e81006` against `bfcb83d`. All fixtures mutate only in-memory databases; all outputs are here.

## Spec-axis summary

B2/B3 role and type separation, B4 retired-centre rejection, and the retired-Trial count are FIXED. The exact m1 HTTP requests now retain Genentech as collaborator and Armando Santoro Md as Investigator; retiring only `CHEMBL3353410` makes both its name and ID return `not_found`. A retired Trial contributes zero to a Drug centre and neighbour's graph-trial count.

An exhaustive independent adjacency/value/order comparison over 6,469 live centres and 22 role-aware relation/direction/type combinations reports zero errors. It checks actual edge sets, live endpoints, direction, metadata, stored trial fields, sponsor counts/classes, drug global counts/phases, action types, association scores, group sizes, and ordering. The current snapshot has 7 retired nodes, 142 retired edges, no live edge with a retired endpoint, and no self-loop. All 1,001 Drug count-chunk fixture items have count and weight 1.

The exact m1 malformed top-level node/edge props cases (`null`, `[]`, `{broken`) now return 200 and permit follow-up requests. However, the new empty-object fallback introduces a distinct value regression for malformed `SPONSORS_TRIAL_OF` props: unavailable `evidence_trials` becomes numeric zero. This is a safety problem under the requested malformed-data condition, not corruption observed in the supplied disk DB. Separately, boolean association scores pass the numeric guard and reach the page as booleans, where the new `.toFixed(3)` call throws; all 300 current scores are JSON real.

## Per-finding reproductions

| m1 item | Result | Exact evidence and current implementation |
|---|---|---|
| B2 collaborator/lead distinction | FIXED | POST `NCT00200395`: Genentech is `SPONSORS/in/Company/collaborator`; Montefiore is `lead_sponsor`. POST `ORG:genentech`: collaborator and lead Trial groups are separate (38 and 15). `src/app.py:131`, `src/app.py:151-160`; `web/try.html:145-149`. `db_validate.json` HTTP/sample payloads. |
| B3 Investigator labelled institution | FIXED for exact m1 reproduction | POST `NCT00754364`: `ORG:armandosantoromd` remains `Investigator`, role `lead_sponsor`; page incoming heading uses the researcher label (`web/try.html:143-148`). `db_validate.json`. |
| B4 retired centre by name | FIXED | Memory backup SQL `UPDATE node SET retired_at='AUDIT_FIXTURE' WHERE id='CHEMBL3353410'`; HTTP `osimertinib` and `CHEMBL3353410` both 200 `not_found`; EGFR remains live and excludes it. `src/app.py:109-112`; `db_retired_center.json`. |
| Retired-Trial count | FIXED | Memory nodes live D:Drug, retired T:Trial, live X:Target; live T-EVALUATES->D and D-ACTS_ON->X. HTTP D has `trials:0`; HTTP X's D has `trials:0, weight:0`. `src/app.py:123-126`; `db_fixtures.json`. |
| Evidence/order wording | FIXED in API and group labels | `MONDO_0005233` Trials remain latest-start-first, Targets now descending exact association score (EGFR first, 0.8883707400322897). Equal weights use ascending label; all nodes satisfy this ordering. `src/app.py:143-158`; `web/try.html:148-157`. |
| Omitted values | FIXED in API | `NCT00200395` retains start `2003-07-02`; every sponsor-linked Drug now carries global `trials` and `max_phase` independently of sponsor weight/class. Zero-trial `CHEMBL925` / TYROSINE now returns `trials:0`. `src/app.py:132-140`, `src/app.py:165-168`; current page rendering at `web/try.html:173-175,228-229`. |
| Malformed props raw errors | FIXED for exact m1 cases; see regression below | Six node/ACTS_ON-edge payload mutations x two HTTP inputs = 12 HTTP 200 responses; all restorations 200. `_obj` at `src/app.py:198-205`; `db_fixtures.json`. |
| Unknown/missing sponsor role (partial m2 finding) | FIXED at API boundary | Both directions preserve recognized roles, missing role as null, and `unknown_role` as stored; page fallback is neutral (`web/try.html:147-149`). Real HTTP eight-case baseline/HEAD matrix in `db_role_fallback.json`. |

## New malformed-property regression: an unavailable sponsor count is asserted as zero

Use `python -B audit_evidence_claims/m2b/db_missing_sponsor_count.py`.

1. Open the real DB read-only and back it up into memory.
2. Change only `edge.props` for `ORG:alaunos|SPONSORS_TRIAL_OF|CHEMBL1201438|` to each of the literal strings `null`, `[]`, `{broken`. Original props contain `evidence_trials:1` and `sponsor_class:INDUSTRY`.
3. POST `/api/explore` with `{"text":"CHEMBL1201438"}` or `{"text":"ORG:alaunos"}` to the real handler backed by that memory DB.
4. `bfcb83d` returns 400; HEAD returns 200 and the retained item has `weight:0`. `web/try.html:173` then asserts `0 lead-sponsored trials`.

`src/app.py:198-205` replaces corrupt/non-object props with `{}`; `src/app.py:136` conflates an unavailable count with zero. The stored property does not provide a count after mutation, and the repair does not recompute one. Preserve unknown/malformed metadata explicitly and omit/mark the count rather than asserting zero. The `{}` control already defaulted to zero at bfcb83d, so the new regression is the newly successful malformed-input path. Full baseline and HEAD responses: `db_missing_sponsor_count.json`. The UI reproduction is in ui_missing_sponsor_count.json.

## New boolean-score rendering hazard

`db_score_fixture.py` uses isolated X:Target -ASSOCIATED_WITH-> Y:Disease with `association_score:true` / `false` and sends both IDs through HTTP. HEAD returns `score:true` or `false`, because Python booleans satisfy `isinstance(score, (int,float))` (`src/app.py:145`). `web/try.html:176` requires a Number and throws on `.toFixed(3)`. Baseline does not emit the score. Numeric control succeeds. This is malformed-field robustness only: the live DB has 300 real-valued scores, zero booleans. Evidence: `db_score_fixture.json`.

## Artifacts and scope

- `db_recheck.py`, `db_validate.json`, `db_retired_center.json`, `db_fixtures.json`, `db_recheck_stdout.txt`: full database check and exact m1 HTTP fixtures; final pass 150.453 s, 6,469 checks, zero current-snapshot errors.
- `db_role_fallback.py/json`: actual handlers at baseline and HEAD for known, missing, unknown, malformed sponsor roles.
- `db_missing_sponsor_count.py/json`, `db_score_fixture.py/json`: introduced malformed-property paths.
- The exact m1 invalid-props fixture used a Drug node / ACTS_ON edge; it did not cover sponsor count metadata. Thus its repair pass does not establish universal fail-safe treatment of malformed metadata.
