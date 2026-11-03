# Name-resolution review (bfcb83d)

All probes used the unchanged source. Scratch files only in this directory. Product probes hit the actual server at `http://127.0.0.1:8876/api/explore`. Retirement testing used an isolated in-memory SQLite backup and an ephemeral HTTP server.

## Blockers

1. **A refused product/tracer can still become the originator map.** POST `{"text":"bevacizumab - awwb"}` returns HTTP 200, center `CHEMBL1201583` / `BEVACIZUMAB`, trials 122. In the same environment `Engine.resolve` returns `BLOCKED_DISTINCT_PRODUCT`; `textrules.is_distinct_product` on that exact string is true. POST `{"text":"89Zr - trastuzumab"}` and `{"text":"[89Zr] trastuzumab"}` return center `CHEMBL1201585` / `TRASTUZUMAB`, trials 13, although the full-string tracer predicate and resolver reject them. `src/query.py:127-132` checks refusal per token, then `src/query.py:146-168` rejoins matching windows without rechecking; `src/app.py:81-88` trusts the accepted hit. Controls `bevacizumab-awwb` and `[89Zr]trastuzumab` refuse. Evidence: `names_product_probe.py`, `names_product_bypass.json`.

2. **Retired drug resurrected by name.** In a SQLite in-memory backup, execute `UPDATE node SET retired_at='AUDIT_FIXTURE' WHERE id='CHEMBL3353410'`. Actual HTTP POST `{"text":"osimertinib"}` returns the retired center and four relation groups (79, 53, 1, 1 neighbours); exact ID returns `not_found`. The live-ID lookup at `src/app.py:76` is bypassed through the dictionary, and `src/app.py:89` does not recheck retirement. `EGFR` correctly excludes this retired neighbour. Evidence: `names_retired_http.py`, `names_retired_http_results.json`.

## Should fix / qualifications

- Identity choice is silent: `Roche` draws FOLIC ACID while `ORG:roche` draws Roche; `MET` links METFORMIN instead of the stored target. Drug aliases precede targets/companies (`src/query.py:155-187`). Stored aliases make these ambiguity cases rather than fabricated edges.
- `Mvasi bevacizumab` correctly refuses; `Mvasi and bevacizumab` silently drops the refused span and draws the explicitly named bevacizumab. `osimertinib EGFR` chooses osimertinib; reversed order chooses EGFR.
- Salts stay distinct: Tarceva/erlotinib hydrochloride -> CHEMBL1079742 (31); erlotinib -> CHEMBL553 (118). Case/fullwidth drug names work. Lowercase NCT IDs fail; HTTP whitespace is trimmed. Inputs beyond 500 characters silently truncate (`src/app.py:182`).
- Current company index has zero multiple-ID aliases, so `also_matching_ids` truncation has no baseline example. All seven existing retired node IDs are excluded. Investigator names are absent from the linker; IDs remain usable.

Additional artifacts: `names_results.json`, `names_extra_results.json`, `names_label_scan.json`; corresponding `names_*probe.py`/`names_label_scan.py` scripts reproduce them.
