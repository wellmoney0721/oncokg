Reviewed `aa5655a`. **300 tests passed. No tracked files changed.** Full reproductions, outputs, and A–F coverage are in [REPORT.md](<C:/Users/geoum/Dropbox/GY's Formal Workspace/2026 Job recruting/바이오리서치에이아이/oncokg/audit_evidence_claims/s1/REPORT.md>).

**BLOCKERS**

**B1 — The whole-name identity guarantee fails.**

Question: `What does osimertinib target?`

Exact input:

```json
{"claims":[{"kind":"relation","relation":"ACTS_ON","subject":"osimertinib가 아닌","object":"EGFR","evidence":"CHEMBL3353410|ACTS_ON|ENSG00000146648|CHEMBL3353410","action":"INHIBITOR"}]}
```

Observed: `verified=true`, one accepted claim, `rejected=[]`.

```text
- OSIMERTINIB acts on EGFR (inhibitor) [CHEMBL3353410|ACTS_ON|ENSG00000146648|CHEMBL3353410]
```

The subject means “not osimertinib.” The linker matches only `"osimertinib가"`, omitting `"아닌"`. Nevertheless, `_flat` deletes the Korean letters from both strings, making the partial match appear complete.

Cause: `src/structured.py:64–65,85–92`; violated guarantees: `src/structured.py:29`, `README.md:454`, `README.ko.md:318`.

**This is an accepted-input identity failure. The rendered graph fact remains supported; this does not demonstrate unsupported medical prose or HTML leakage.** Approval fails against the explicitly promised whole-name condition.

**SHOULD FIX**

1. **Faithful names copied from evidence reject.** For `Which drugs act on ALK?`:

   ```json
   {"claims":[{"kind":"relation","relation":"ACTS_ON","subject":"ALECTINIB HYDROCHLORIDE","object":"ALK","evidence":"CHEMBL3707320|ACTS_ON|ENSG00000171094|CHEMBL3707320","action":"INHIBITOR"}]}
   ```

   Output: `verified=false`, `accepted=[]`, reason:
   `'ALECTINIB HYDROCHLORIDE' does not name exactly one drug on its own`.

   Changing only the subject to `CHEMBL3707320` accepts. The linker collects salt and parent together (`src/query.py:147–170`; `src/structured.py:86`). Two long sponsor labels also reject because linking stops at five tokens. Exact sponsor inputs are in the report.

2. **Malformed types throw instead of returning rejection.** For the osimertinib question, input `{"claims":[{"kind":[]}]}` raises `TypeError: unhashable type: 'list'` through `answer(use_llm=True)`. Array/dictionary `relation` values behave similarly (`src/structured.py:100,122`). HTTP catches this as 400, but direct/model callers receive no result.

3. **Rejected NaN breaks the page’s JSON response.** Use B1’s payload with ordinary subject `"osimertinib"` and replace action with the unquoted token `NaN`. The verifier correctly rejects it, but `/api/structured` returns HTTP 200 containing `"action": NaN`. The page displays `Unexpected token 'N' ... is not valid JSON`. See `src/structured.py:212`, `src/app.py:135`, `web/try.html:173`.

4. **Response-shape and parsing failures escape.** Mocked SDK response `content=[]` raises `IndexError` at `src/query.py:464`. Exact input expression `'{"claims":' + '['*5000 + 'null' + ']'*5000 + '}'` raises `RecursionError`; only `JSONDecodeError` is caught (`src/structured.py:210–215`). These fail closed.

**NOTES**

- **Usefulness:** All **73** supported demo/profile claims accept using exact IDs. Copied labels accept 69/73. Trial phase/status, sponsor counts, drug stages/counts, and supported relations are expressible. France correctly receives a refusal.
- **Rendering and HTML:** Adding `note:"<img src=x onerror=alert(1)>"` to an otherwise valid claim rejects as an unknown key; answer text is empty and diagnostic HTML contains `&lt;img`. No tested model text entered the rendered answer. Page verification executed the actual JavaScript handler in a Node VM, not a full browser (`web/try.html:176–181`).
- **Values and edges:** No current stored-code `_norm` collisions were found. `ANTISENSE INHIBITOR` accepts for aprinocarsen; substituting `INHIBITOR` rejects. All **142 retired edges** reject, including with stale allowlist entries.
- **Parsing:** Fifty-one valid claims produce 50 accepted plus an excess-count rejection. Duplicate action keys use the final value, which is checked. Fenced JSON accepts; concatenated JSON objects reject.
- **Empty replies:** `{"claims":[]}` produces one rejection and says one claim was removed, although the prompt explicitly requests this empty response (`src/query.py:457–458`; `src/structured.py:217–220`).
- **PROFILE documentation:** For `What is osimertinib?`, a drug claim citing `profile:CHEMBL3353410`, stage `APPROVAL`, and count `79` accepts. SQL finds zero corresponding live edges. Its facts remain graph-supported, but the “live edge” wording needs a PROFILE exception (`src/structured.py:113–115`).
- **Other documentation:** `src/query.py:12–18` and `web/template.html:261` retain obsolete prose-check descriptions. English README says 22/38 faithful answers were rejected; Korean README says 22/38 passed. Schema omissions and relevance/completeness limitations remain NOTES.

VERDICT: CHANGES REQUIRED