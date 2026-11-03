# Round 2 model/API/UI evidence

Reviewed HEAD `60b9c61`. No tracked files changed. Both source graph connections used `PRAGMA query_only=ON`. All LLM replies were mocked; HTTP used a temporary loopback server that was shut down. Page checks execute the actual `web/try.html` script in Node VM with a minimal DOM, not a full browser.

## s1 reproduction status

`modelui_probe.py` and `modelui_page_probe.js` are exact copies of s1 and now write beside themselves in s2. All 29 model cases, 10 API cases, and 10 page cases were rerun; inputs and outputs are in `modelui_results.json`, `modelui_api_fixtures.json`, and `modelui_page_results.json`.

- **S2 FIXED**: `{"claims":[{"kind":[]}]}`, dictionary kind, list relation, and valid claim followed by malformed kind now return rejections. The mixed payload retains the valid graph sentence and rejects only the malformed claim. No exceptions.
- **S3 FIXED for the exact reported reproduction**: action token `NaN` now returns HTTP 200 with valid JSON, `verified=false`, `accepted=[]`, and a rejection. Node `JSON.parse` succeeds. Literal `Infinity` and `-Infinity` also reject.
- **S4 FIXED**: empty SDK `content=[]`, non-text block, null text, and nesting at 1100/20000 return failure results without exceptions. A simulated SDK service failure still raises its original RuntimeError; that is an operational failure, not a model-claim acceptance.
- **Empty-claims NOTE FIXED in answer**: `{"claims":[]}` produces `The model found nothing in the evidence that answers this question.` with no removed-claim suffix. Checks are `grounded=false`, `accepted=0`, `rejected=[]`, `unsupported_claims=[]`.
- **Leakage regression passes**: the exact HTML injection from s1 is escaped in every diagnostic and never appears in the graph-rendered answer. No raw injected element is present in rendered HTML.
- Duplicate-key, 50/51 claims, fenced JSON, prose-wrapped JSON, concatenated JSON, malformed JSON, and oversized unknown-field behavior reproduced consistently with s1, apart from the repaired exceptions above.

## BLOCKERS

None found within this assigned model/API/UI scope.

## SHOULD FIX

### SF-M1: nonfinite parse coverage remains incomplete

Question: `What does osimertinib target?`

Exact JSON input:

```json
{"claims":[{"kind":"relation","relation":"ACTS_ON","subject":"osimertinib","object":"EGFR","evidence":"CHEMBL3353410|ACTS_ON|ENSG00000146648|CHEMBL3353410","action":1e309}]}
```

`Verifier.verify` returns `verified=false`, `accepted=[]`, and a rejected claim whose `action` is Python infinity. `json.dumps(result, allow_nan=False)` then raises `ValueError: Out of range float values are not JSON compliant: inf`. The mocked `answer(use_llm=True).to_dict()` has the same strict serialization failure in `checks.rejected`; default Python serialization emits `Infinity`. Parsed input using `float('nan')`, `float('inf')`, or `-float('inf')` behaves similarly. Raw `-1e309` does too.

Cause: `src/structured.py:230-238` promises parsed input support but applies `parse_constant` only to raw literal constants; exponent overflow uses the default float decoder. Rejected input is retained at `src/structured.py:255-256`, then copied into checks at `src/query.py:395-400`.

The API protection **does work**: `src/app.py:135-140` returns valid HTTP 400 JSON `{"error":"Out of range float values are not JSON compliant: inf"}`. The page displays this error normally. No unsupported fact is accepted and no unsafe HTML reaches the page. This is a serialization/diagnostic robustness gap, not a false-acceptance blocker.

## NOTES

- Literal `NaN`, `Infinity`, and `-Infinity` now report `not valid JSON: nested too deeply`, though their failure is nonfinite numeric syntax. `src/structured.py:235-238` discards the custom ValueError message. This does not affect rejection.
- The empty-claims page still labels the result `버린 주장 0개` (zero discarded claims) and gives no abstention explanation because `web/try.html:174-180` does not inspect `empty`; the requested `answer(use_llm=True)` path itself is repaired.
- Missing SDK is still represented by an empty claim list (`src/query.py:442-444`), so the displayed answer misleadingly says the model found nothing even though `generated_by` states the missing package. This is operational messaging, not evidence acceptance.
- Additional exception-catch attacks used a lone surrogate in a subject, mixed Python dictionary keys, and a deliberately injected RuntimeError on the middle of three claims. Each rejected only the bad middle claim and rendered the two valid facts. RuntimeError message text was not included. See `per_claim:*` in `modelui_attack_results.json` and `src/structured.py:250-262`.
- Near-parser-limit nesting at every depth 950 through 1004 yielded no unhandled exception. A mock SDK block with `text=42` raises at `src/query.py:466`; this violates the SDK's string-text contract and is not an achievable JSON claim attack. A leading whitespace-only text block prevents selection of a later valid block, which affects completeness only.
- A raw lone-surrogate subject is correctly rejected per claim; UTF-8 response serialization then returns valid HTTP 400 JSON. No page JSON break occurs.

Additional exact inputs and outputs: `modelui_attack.py`, `modelui_attack_results.json`, `modelui_attack_api_fixtures.json`, `modelui_attack_page_probe.js`, and `modelui_attack_page_results.json`. Nonfinite Python values are explicitly encoded as `<Python inf>` / `<Python nan>` in the saved diagnostic artifact so the artifact itself remains standard JSON; the original input strings and strict-serialization exceptions preserve the distinction.
