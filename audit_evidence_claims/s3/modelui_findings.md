# Round 3: model, parser, diagnostics, and page

Reviewed `6bcde7295e7b2292636119cd3e1b2a604324693d`. All writes from these probes are under `audit_evidence_claims/s3/`. Source graph connections use `PRAGMA query_only=ON`; SDK responses are mocked, and temporary loopback HTTP servers are shut down. The page probes execute the actual script from `web/try.html` with a Node VM and minimal DOM, not a full browser.

## Reproduction inventory and status

`modelui_replay_runner.py` copies the original s1 and s2 probes into `replay_s1/` and `replay_s2/`; only root-directory lookup changes. `modelui_comparison.json` confirms identical recorded input strings and identical HTTP requests. Both old model scripts execute all 29 model scenarios, 10 HTTP requests, and 10 page scenarios. They record only 28 model rows now: their `sdk_failure` branch appends a result only when an exception escapes. That old exception no longer escapes. `modelui_sdk_exact_replay.py` runs the same copied scripts with a Python profiler observing the original call's returned answer; `modelui_legacy_sdk_failure_results.json` captures the exact original outage input and result from each round. It is also recorded as `legacy_exact:sdk_failure` in `modelui_new_results.json`.

The s2 attack script adds 22 top-level rows, including 55 depths (950 through 1004) inside `near_limit_nesting`, plus 7 HTTP and 7 page cases. All its input/template fields and HTTP requests compare equal. New s3 attacks add 68 recorded rows, 27 HTTP cases and 27 page cases. Commands:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
$env:PYTHONUTF8='1'
$env:PYTHONIOENCODING='utf-8'
python -B audit_evidence_claims/s3/modelui_replay_runner.py
python -B audit_evidence_claims/s3/modelui_new_attacks.py
node audit_evidence_claims/s3/modelui_new_page_probe.js
python -B audit_evidence_claims/s3/modelui_sdk_exact_replay.py
python -B audit_evidence_claims/s3/modelui_compare.py
```

| Prior finding | Status | Current observation |
| --- | --- | --- |
| s1 S2 / model SF1: list/dictionary kind, list relation | **FIXED** | `{"claims":[{"kind":[]}]}` and dictionary-kind variants reject without throwing; mixed valid/invalid payload preserves its valid graph sentence. |
| s1 S3 / model SF2: raw `NaN` API response is not JSON | **FIXED** | Raw `NaN`, `Infinity`, `-Infinity` reject; HTTP 200 response parses in the actual page handler. |
| s1 S4 / model SF3: empty/no-text/null-text SDK content | **FIXED** | `content=[]`, `content=[SimpleNamespace(type='tool_use')]`, and `content=[SimpleNamespace(text=None)]` return rejection results without exception. |
| s1 S4 / model SF3: deeply nested JSON | **FIXED** | Original 1100- and 20000-deep arrays reject; every s2 depth 950–1004 returns without an unhandled exception. |
| s1 model SF3 / s2 operational note: SDK service failure escapes | **FIXED** | Exact `messages.create` mock raising `RuntimeError('simulated SDK failure')` returns a model-unavailable answer and `applicable=false`. |
| s1 empty-claims note | **FIXED in `answer`** | `{"claims":[]}` produces the abstention text and `rejected=[]`; no removed-claim suffix. |
| s2 SF-M1: `1e309`, `-1e309`, pre-parsed NaN/Infinity break strict serialization | **FIXED** | All reject and `json.dumps(result, allow_nan=False)` succeeds. Raw overflow is stopped at parsing; parsed nonfinite values become strings in rejected diagnostics. |
| s2 note: missing SDK falsely described as a model abstention | **FIXED** | Missing import now says the language model could not be used; `grounded=null`, `applicable=false`, `accepted=0`. |
| s2 note: nonfinite parser errors say `nested too deeply` | **NOT FIXED (NOTE)** | Raw `1e309` and `NaN` still report `not valid JSON: nested too deeply`; rejection is correct. |
| s2 note: empty-claims page only says zero discarded claims | **NOT FIXED (NOTE)** | `{"claims":[]}` displays `버린 주장 0개`, accepted 0; the page does not inspect `empty`. |
| s2 note: mocked SDK block `text=42` throws | **NOT FIXED (NOTE)** | `AttributeError: 'int' object has no attribute 'strip'`; this violates the SDK text-block contract, not a JSON claim path. |
| s2 note: first whitespace block masks later valid text | **NOT FIXED (NOTE)** | `content=[text=' ', text=validJSON]` selects the first block and rejects; completeness only. |
| s2 note: lone-surrogate subject causes UTF-8 response failure | **NOT FIXED (NOTE)** | Per-claim rejection succeeds; HTTP safely returns valid 400 JSON and the page shows the codec error. |
| s1/s2 HTML injection, duplicate keys, fences, multiple JSON objects, 50/51 claims | **REGRESSION PASS** | Same supported facts accepted; unknown-field HTML rejects and is escaped; last duplicate-key value is checked; concatenated JSON objects reject; 51 claims retain only the first 50 and add excess-count rejection. |

## BLOCKERS

None in this assigned scope. No tested unsupported claim was accepted; no injected model text entered an answer sentence or became raw HTML in the page. Mixed valid/rejected cases retain only the graph-rendered valid facts.

## SHOULD FIX

No additional approval-bar failure in this scope. The original nonfinite-number repair is effective. The remaining sanitizer and SDK edge cases below are robustness notes and do not demonstrate false acceptance or text leakage.

## NOTES

### N1 — Already-parsed giant integers can still break diagnostic serialization

This is a new edge case outside ordinary Python JSON decoding. `src/structured.py:94–95` preserves arbitrary integers; `src/structured.py:284` then puts one into diagnostics. Exact construction (the `GOOD` claim is given below):

```python
payload = {"claims": [dict(GOOD, note=10**5000)]}
result = kg.verify_structured(payload, evidence)
json.dumps(result, allow_nan=False)
```

Observed verifier result: `verified=false`, `accepted=[]`, `text=""`, one unknown-key rejection. Strict JSON serialization raises:

```text
ValueError: Exceeds the limit (4300 digits) for integer string conversion; use sys.set_int_max_str_digits() to increase the limit
```

The corresponding raw JSON (`note` equal to `1` followed by 5000 zeros) is rejected during parsing, and its result serializes normally. Thus this needs an already-constructed Python integer that bypasses the default JSON decoder's integer-string limit. It cannot be generated through the reviewed model JSON path on this interpreter. See `sanitiser:parsed_5001_digit_int` and `sanitiser:raw_5001_digit_int` in `modelui_new_results.json`.

The sanitizer otherwise survived parsed nonfinite values in action/kind/subject/evidence/unknown fields, nesting 100 levels deep, a cyclic Python list, 100-key dictionaries, and long strings. All these results serialize with `allow_nan=False`. Cyclic and oversized pre-parsed structures are diagnostic stress tests, not JSON-native values. Depth truncation and per-container/string limits behaved as implemented (`src/structured.py:84–96`).

### N2 — Error path repair correctly excludes exception text

The missing SDK reproduction is `sys.modules['anthropic']=None` followed by `kg.answer(Q,use_llm=True)`. Exact output:

```text
The language model could not be used (the anthropic package is not installed); no answer was generated.
```

The original service outage produces:

```text
The language model could not be used (RuntimeError); no answer was generated.
```

Both checks dictionaries are:

```json
{"grounded":null,"applicable":false,"accepted":0,"rejected":[],"unsupported_claims":[],"method":"no model reply to check"}
```

Constructor and `messages.create` exceptions were separately tested with `RuntimeError`, `ValueError`, `ConnectionError`, and `TimeoutError`; all returned this shape. Their exception messages contained `SENSITIVE_MODEL_OR_CREDENTIAL_TEXT` plus the HTML marker, and neither string reached the answer or checks. The code retains only the exception class (`src/query.py:468–474`) and renders the model-unavailable branch (`src/query.py:388–394`).

Malformed SDK objects are a separate limitation: missing `.content`, a `None` message, and numeric block text still throw at `src/query.py:475–476`, after the request try/except. These are invalid SDK response shapes. Empty and non-text content—the original reproductions—do not throw. No outage-recovery or actual SDK/network availability claim is made; the review uses controlled mocks.

### N3 — Parse diagnostics and empty-page wording remain imprecise

The parser rejects both literal nonfinite constants and exponent overflow, but its ValueError handler replaces the reason with `nested too deeply` (`src/structured.py:263–266`). Tested finite values at and below `1.7976931348623157e308`, underflow (`1e-400`), negative zero, and integral-looking floats remain float-typed and reject in the tested action field. Nonfinite values one step above the finite limit reject before claim validation. These are strict-JSON serializable failures.

`web/try.html:174–180` still gives an empty claim array a zero-discarded badge instead of explaining abstention. The model-answer path separately handles `empty` at `src/query.py:395–398` and reports it correctly.

### N4 — HTML and answer-boundary probes

Question for all attacks:

```text
What does osimertinib target?
```

Exact baseline claim:

```json
{"kind":"relation","relation":"ACTS_ON","subject":"osimertinib","object":"EGFR","evidence":"CHEMBL3353410|ACTS_ON|ENSG00000146648|CHEMBL3353410","action":"INHIBITOR"}
```

Exact marker:

```text
<img src=x onerror="globalThis.MODEL_INJECTED=1"><script>globalThis.MODEL_INJECTED=2</script>&"'
```

The marker was placed in each of kind, relation, subject, object, evidence, action, an unknown `note`, and an unknown key. Each rejects; the page contains escaped `&lt;img`/`&lt;script`, no raw injected element. `[GOOD, GOOD+note=MARK, GOOD]` yields two accepted claims, one rejection, and exactly two copies of the graph sentence:

```text
- OSIMERTINIB acts on EGFR (inhibitor) [CHEMBL3353410|ACTS_ON|ENSG00000146648|CHEMBL3353410]
```

All 27 new HTTP bodies parse strictly and all 27 page cases have `has_raw_injected_element=false`. Original 10+10 and s2's additional 7 page cases pass as well. The real handler escapes all reflected fields with `esc` (`web/try.html:93,176–181`). The Node VM is not an HTML parser; its evidence is the escaped generated string and absence of raw injected elements, not browser execution coverage.

## Artifacts

- `modelui_replay_runner.py`, `modelui_replay_manifest.json`: replay scripts and path-only adaptations.
- `replay_s1/modelui_*`, `replay_s2/modelui_*`: legacy copies, exact requests/replies, outputs, prompts and JS handler results.
- `modelui_new_attacks.py`, `modelui_new_results.json`: all 68 new/supplementary exact inputs and observations.
- `modelui_new_api_fixtures.json`, `modelui_new_page_probe.js`, `modelui_new_page_results.json`: all 27 HTTP and page checks.
- `modelui_compare.py`, `modelui_comparison.json`: input equality, counts, and remaining exceptions.
- `modelui_sdk_exact_replay.py`, `modelui_legacy_sdk_failure_results.json`: profiler captures proving the original s1 and s2 outage calls return the repaired model-unavailable answer.
