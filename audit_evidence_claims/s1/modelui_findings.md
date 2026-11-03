# Model path and page review (aa5655a)

Reproduce from repo root:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
python -B audit_evidence_claims/s1/modelui_probe.py
node audit_evidence_claims/s1/modelui_page_probe.js
```

The Python harness invokes the actual `_llm_claims` and `answer(use_llm=True)` with an injected `anthropic` module, then sends real HTTP requests to `make_handler(Engine())` on an ephemeral localhost server. It puts both graph connections in SQLite `query_only` mode. It does not call the paid/network model service. The JS harness executes the actual script from `web/try.html` in a Node VM, supplies the captured HTTP JSON and minimal form/DOM objects, and observes assigned HTML. This is a JS-handler/escaping test, not full browser rendering.

## BLOCKERS

None found in the assigned model/text leakage surface. No tested unsupported model text reached the answer, and rejected HTML strings were escaped in the page.

## SHOULD FIX

1. **Malformed field types escape as exceptions rather than a rejected-claim result.** `src/structured.py:99-101` performs hash lookup before validating kind type; `src/structured.py:121-123` does the same for relation. Exact question: `What does osimertinib target?`. Exact model reply `{"claims":[{"kind":[]}]}` produces `TypeError: unhashable type: 'list'` from `answer(use_llm=True)`. `{"claims":[{"kind":{}}]}` produces `TypeError: unhashable type: 'dict'`. A valid relation claim with `relation: []` also raises the list error. HTTP `/api/structured` catches these and returns 400 `{"error":"unhashable type: 'list'"}` (`src/app.py:137-139`), but direct/model callers receive no result. `faithful_then_kind_list` shows even a previously valid claim is lost. This fails closed, not false acceptance.

2. **Non-finite JSON constants break the API response contract.** Exact inner answer is `{"claims":[{"kind":"relation","relation":"ACTS_ON","subject":"osimertinib","object":"EGFR","evidence":"CHEMBL3353410|ACTS_ON|ENSG00000146648|CHEMBL3353410","action":NaN}]}` and question is the one above. `json.loads` accepts `NaN` at `src/structured.py:212`; action validation correctly rejects it. However `src/app.py:135` serializes rejected claim with literal `NaN`. HTTP status is 200 but the body is not standard JSON. The page's real `r.json()` path (`web/try.html:173`) fails before showing a rejection. Observed handler HTML: `<p class="err">오류: Unexpected token 'N', ...&quot;&quot;action&quot;: NaN}, &quot;why&quot;... is not valid JSON</p>`. Infinity likewise rejects as an action in the model path. Parse non-finite tokens as invalid input before reflecting them. No unsupported claim is accepted.

3. **Empty SDK content, API failures, and extreme JSON nesting are not converted to structured failure.** At `src/query.py:460-464`, mocked SDK response `content=[]` produces `IndexError: list index out of range`; `content=[SimpleNamespace(type='tool_use')]` produces `AttributeError: 'types.SimpleNamespace' object has no attribute 'text'`; `content=[SimpleNamespace(text=None)]` produces `AttributeError: 'NoneType' object has no attribute 'strip'`; mocked `messages.create` raising `RuntimeError('simulated SDK failure')` escapes unchanged. `src/structured.py:212-215` catches only JSONDecodeError: exact raw string expression `'{"claims":' + '['*20000 + '0' + ']'*20000 + '}'`, produces `RecursionError: maximum recursion depth exceeded while decoding a JSON array from a unicode string`. Full bytes are in `modelui_results.json` case `nested20000`. Ordinary malformed JSON and empty text do return a closed rejection. These are robustness findings only.

## NOTES

- Baseline exact claim: `{"kind":"relation","relation":"ACTS_ON","subject":"osimertinib","object":"EGFR","evidence":"CHEMBL3353410|ACTS_ON|ENSG00000146648|CHEMBL3353410","action":"INHIBITOR"}`. Wrapped as `{"claims":[claim]}` for the question above, actual model path returns `grounded=true, accepted=1, rejected=[]` and exactly `- OSIMERTINIB acts on EGFR (inhibitor) [CHEMBL3353410|ACTS_ON|ENSG00000146648|CHEMBL3353410]`.
- The same JSON in a Markdown fence, or surrounded by arbitrary text, produces exactly the same accepted answer. The greedy brace extraction at `src/query.py:465` discards text outside the first/last braces; extra prose does not leak. Two JSON objects concatenated, or `{garbage}` followed by a valid object, reject because the extraction is not parseable JSON. This may lose otherwise useful claims but does not expand accepted claims.
- HTML probe string is exactly `<img src=x onerror="globalThis.MODEL_INJECTED=1"><script>globalThis.MODEL_INJECTED=2</script>&"'`. Supplying it as extra `note` or as `action` rejects. `web/try.html:93,176-181` escapes answer, rejection reason, rejected claim JSON, evidence, and errors. Actual handler output contained `&lt;img`/`&lt;script` and no raw `img`/`script` element. Rejected model text is intentionally visible as escaped diagnostic text, separate from the answer. `src/query.py:392-399` similarly retains rejected strings in checks, not in `Answer.text`.
- 51 copies of the baseline claim accept only 50, return `grounded=false`, and append `{"claim":null,"why":"more than 50 claims; the rest were not read"}` (`src/structured.py:223-230`). Replacing the 51st with an injected note has the same result; its content cannot reach the answer.
- Duplicate action keys are last-wins at JSON decoding: `"action":"ACTIVATOR","action":"INHIBITOR"` accepts and renders graph inhibitor; reversing the pair rejects. The discarded duplicate is not rendered. Evidence-consistent, but not strict duplicate-key rejection.
- `{"claims":[]}` is requested by the prompt (`src/query.py:457-458`) but the verifier treats it as an invalid envelope (`src/structured.py:217-220`), returns one rejection, and answer adds `(1 claim(s) were removed because the graph does not support them.)`. Nothing was actually claimed. Missing `anthropic` package follows this same route with `generated_by="error: the anthropic package is not installed"`.
- A 1,100-deep nested array rejects as a non-object claim without acceptance; a 139 KB model reply with an extra unknown field rejects. The HTTP endpoint reads at most 20,000 bytes (`src/app.py:113`), so that oversized request returns 400 truncated-JSON error rather than accepting a partial answer.
- `src/query.py:12-18` still says the model only changes prose and facts are identical; that header is stale after structured selection. `web/try.html:240` says box 3 checks an AI answer, while it now accepts claim JSON (less severe wording drift).

Artifacts: `modelui_probe.py`, `modelui_results.json` (all exact raw replies, outputs and SDK request), `modelui_prompt.txt`, `modelui_api_fixtures.json` (exact requests and raw responses), `modelui_page_probe.js`, `modelui_page_results.json` (full generated HTML), `modelui_stdout.txt`, `modelui_page_stdout.txt`. Parsed non-finite values in the portable results file are explicitly labeled strings; original raw reply/request/response strings retain exact `NaN`/`Infinity` tokens.
