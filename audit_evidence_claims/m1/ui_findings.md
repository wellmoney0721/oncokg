# Independent standards and UI review of bfcb83d

## Standards

No tracked AGENTS.md, CODING_STANDARDS, CONTRIBUTING or issue-tracker instructions were found outside the audit archives. No documented coding-standard violation is asserted. The user's no-tracked-edits rule was followed; all outputs here have the `ui_` prefix and live under `audit_evidence_claims/m1/`.

## Blocking specification finding: sponsor-role wording

**Input `NCT00200395`** (`POST /api/explore` on port 8876, HTTP 200) includes `Genentech` under `SPONSORS|in`. The rendered label is **`이 임상의 주관 기관`** (`web/try.html:144,194`). The live edge `ORG:genentech|SPONSORS|NCT00200395|NCT00200395` actually stores `props.role="collaborator"`, not `lead_sponsor`. `src/graph.py:255-256,282-286` deliberately stores both roles as SPONSORS; `src/app.py:105-120` discards that role before rendering. Thus direction is correct, but the page promotes collaboration to trial leadership. There are 1,652 live collaborator SPONSORS edges and 3,000 lead-sponsor edges. Evidence: `ui_db_excerpt.txt`, `ui_real_maps.json`, `ui_http.json`, `ui_harness_results.json` (real.NCT00200395.groupLabels). This is a relation-wording blocker under the user's approval bar.

**Related exact input `NCT00754364`:** the same `SPONSORS|in` label calls `Armando Santoro Md`, whose live node type is `Investigator`, a `주관 기관`. `TKO` itself correctly translates Investigator as 연구자 (`web/try.html:140`), but `GKO` ignores the group node type. Evidence in the same JSON files.

## Should fix

1. **Unannounced circular-map cuts:** `CHEMBL1201438` (ALDESLEUKIN) returns groups of 11 trials, 11 companies and 3 targets, all below `per_group=30`. `drawMap` draws only 22 of those 25 neighbors (`web/try.html:162-164`), and the only cut notice checks `g.total > g.items.length` (`:194`), so no cut notice appears. Section 0 says `모두 그립니다` (`:54`). With default positive per_group no nonempty group is hidden completely: the map gives each at least three slots or all available items. `MAX=40` is also not a hard cap (AstraZeneca draws 41). These are presentation/wording issues, not fabricated edges.
2. **Ordering overclaim:** `src/app.py:74` says evidence ordering and `web/try.html:194` says `근거가 많은`, but Trial weights are their start-date strings (`src/app.py:110-112`), and other unweighted types use zero (`:116-117`) followed by reverse label order (`:124`). Call date ordering recent-start ordering, and do not describe unweighted target/company lists as evidence-ranked.
3. **Broken trail after refusal/not-found/error:** `osimertinib` -> `EGFR` establishes two trail buttons. Submit `Mvasi`: form handler clears the trail array (`web/try.html:199`), refusal returns early (`:184`) without clearing old trail HTML. Clicking the old first trail button throws `TypeError: Cannot read properties of undefined (reading '0')` at `:202`. The same error was reproduced with `unknown-m1-entity` returning not_found and a synthetic HTTP error (`:183,185`). Exact-source Node VM reproduction is in `ui_harness.js/results.json`. Two overlapping `explore("EGFR")` calls also append duplicate EGFR trail entries; this is redundant history, not corrupted graph data.
4. **Overlapping request race:** start `explore("EGFR")`, then `explore("KRAS")`; complete KRAS first and EGFR second. The old EGFR response overwrites the newer map and appends a misleading `KRAS -> EGFR` trail (`web/try.html:181-197`). There is no cancellation/request-generation guard. The harness controls completion order and uses actual HTTP map data.
5. **Stored-code specificity lost:** actual `CHEMBL1201438` has three ACTS_ON edges storing `AGONIST`; `ACT.AGONIST="작용"` produces `작용: 작용` (`web/try.html:149,155`). This loses the action subtype. `BINDING_AGENT` is not the stored `BINDING AGENT`, so the latter falls back safely to its raw code. Sponsor classes FED/NIH/NETWORK/OTHER/OTHER_GOV are collapsed into one non-industry phrase (`:153`); display the stored class alongside any translation. PH and phase fallbacks preserve unrecognized stored codes.

## Safety checks and limits

The actual page script was executed in a Node VM with stubbed DOM elements and fetch; this verifies produced markup and handlers, not browser execution. Labels, titles, IDs, and edge IDs containing `<`, `>`, `&`, and double quotes were escaped in the tested generated strings (`web/try.html:104,171-178,190-196`). `edge_id` is shown as escaped text, not used as a data-id attribute; data-id uses the escaped node ID.

**Conditional URL hazard:** stored `url="javascript:alert(document.domain)"` survives as an `<a href="javascript:alert(document.domain)" target="_blank" rel="noopener">` in both center and neighbor links (`web/try.html:193,196`). HTML escaping does not restrict URL schemes. Native browser availability was absent, so no claim is made that this executes in the installed browser; `target=_blank`/noopener behavior may block it. Scheme allowlisting should be added, but this evidence is only unsafe-href preservation, not demonstrated XSS. All injection data in this check was a synthetic response in the harness; production DB was unchanged.

README app.py lines (`README.md:566,596`; `README.ko.md:387`) accurately identify the local page and command. Module text `src/app.py:10` says “All three” after describing four boxes; minor stale wording. Its “everything” (`:5,70`) needs the same truncation qualification as section 0.

## Reproduction

With root's app server on 8876: `python -B audit_evidence_claims/m1/ui_collect.py`, then `node audit_evidence_claims/m1/ui_harness.js`. `ui_http.json` confirms HTTP 200 and byte-for-byte semantic equality to direct Engine results for all eight named inputs. For DB role/action excerpts run `python -B audit_evidence_claims/m1/ui_inspect.py`. No browser-rendered visual or executed-XSS assertion is supported by these scripts.
