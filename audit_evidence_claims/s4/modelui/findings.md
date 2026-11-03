# Round 4 model/API/UI recheck

Reviewed current HEAD `8adf2dd`. No tracked files edited. All new scripts, copies, outputs and temporary paths are inside `audit_evidence_claims/s4/modelui/`. All live graph connections used `PRAGMA query_only=ON`. Model replies were controlled SDK mocks; temporary HTTP servers used loopback and were shut down. Page checks execute the actual `web/try.html` script in a Node VM with minimal DOM objects, not a full browser.

## BLOCKERS

None in this scope. No tested unsupported claim entered the answer. No model injection became raw HTML; diagnostic model strings remain escaped and separate from the answer.

## SHOULD FIX

None affecting the approval bar in this scope. All historical model/API SHOULD FIX reproductions are fixed. Remaining cases below are the existing robustness/completeness NOTES and do not show unsupported acceptance, answer leakage, or a documentation overclaim about evidence support.

## Every historical reproduction

Reproduce from repository root:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
$env:PYTHONUTF8='1'
$env:PYTHONIOENCODING='utf-8'
python -B audit_evidence_claims/s4/modelui/run_replays.py
python -B audit_evidence_claims/s4/modelui/compare_replays.py
```

`replay_manifest.json` records all original paths, relocated copies, path-only changes, and successful exit codes. `comparison.json` proves original case inputs and HTTP requests match. s1 and s2 each execute 29 model cases, 10 HTTP requests, and 10 page cases. Each old probe records only 28 model rows because its `sdk_failure` branch records only escaping exceptions; `modelui_sdk_exact_replay.py` profiles the unchanged original call and saves its returned answer in `modelui_legacy_sdk_failure_results.json`. s2 also executes 22 attack rows including all 55 nesting depths 950–1004, plus 7 HTTP and 7 page cases. s3 executes all 68 attack rows, 27 HTTP and 27 page cases. Every s3 output is identical to its s3 counterpart as parsed JSON, including every HTTP output.

Question `Q` throughout is exactly `What does osimertinib target?`. `GOOD` is exactly:

```json
{"kind":"relation","relation":"ACTS_ON","subject":"osimertinib","object":"EGFR","evidence":"CHEMBL3353410|ACTS_ON|ENSG00000146648|CHEMBL3353410","action":"INHIBITOR"}
```

| Historical finding | Status | Exact input / observed current output | Current code |
| --- | --- | --- | --- |
| s1 S2: list/dict kind, list relation throws | **FIXED** | `{"claims":[{"kind":[]}]}` returns accepted 0, rejected `unknown kind []; use relation, trial or drug`. `{}` kind similarly rejects. `GOOD` with `relation=[]` rejects `unknown relation []`. `[GOOD,{"kind":[]}]` retains 1 accepted fact and rejects only the malformed claim. | `src/structured.py:153`, `175`, `284–289` |
| s1 S3: NaN API response invalid JSON | **FIXED** | `{"claims":[GOOD]}` with action replaced by raw `NaN` / `Infinity` / `-Infinity` returns accepted 0, one parse rejection; HTTP 200 is standard JSON and the actual page handler parses it. | `src/structured.py:73`, `266–271`; `src/app.py:135–138` |
| s1 S4: empty/non-text/null SDK content | **FIXED** | `content=[]`, `[SimpleNamespace(type='tool_use')]`, `[SimpleNamespace(text=None)]` now return `accepted=0`, rejection `not valid JSON: Expecting value`, no exception. | `src/query.py:475–478` |
| s1 S4: deep nesting escapes | **FIXED** | `'{"claims":'+'['*20000+'0'+']'*20000+'}'` and depth 1100 reject without exception. All s2 depths 950–1004 also return without exception. | `src/structured.py:268–271`, `284–289` |
| s1/s2 SDK failure escapes | **FIXED** | `messages.create` raises exact `RuntimeError('simulated SDK failure')`: output `The language model could not be used (RuntimeError); no answer was generated.`; checks `grounded=null, applicable=false, accepted=0, rejected=[]`. Both old calls captured separately. | `src/query.py:388–394`, `468–474` |
| s1 empty-claims answer | **FIXED** | `{"claims":[]}` yields `The model found nothing in the evidence that answers this question.`, `accepted=0`, `rejected=[]`, no removed-claim suffix. | `src/structured.py:274–276`; `src/query.py:395–398` |
| s2 SF-M1: overflow/parsed nonfinite diagnostics | **FIXED** | Raw action `1e309` and `-1e309` return parse rejection and strict-serializable result. Already-parsed action `float('inf')` becomes diagnostic string `"inf"`, rejects as non-string action, and strict serialization succeeds. Parsed NaN and negative infinity do likewise. | `src/structured.py:77–81`, `84–98`, `266–271`, `289` |
| s2 missing SDK described as abstention | **FIXED** | `sys.modules['anthropic']=None`; `answer(Q,use_llm=True)` now says `The language model could not be used (the anthropic package is not installed); no answer was generated.` with `grounded=null, applicable=false, accepted=0`. | `src/query.py:388–394`, `448–451` |
| s2/s3 parse-reason wording | **NOT FIXED — NOTE** | Raw NaN and `1e309` both say `not valid JSON: nested too deeply`. Correct rejection; imprecise reason. | `src/structured.py:268–271` |
| s2/s3 empty-claims page wording | **NOT FIXED — NOTE** | `{"claims":[]}` yields the badge `버린 주장 0개` and accepted 0, without abstention explanation. Correct model-answer behavior is separately fixed. | `web/try.html:174–180` |
| s2/s3 invalid SDK shape | **NOT FIXED — NOTE** | `content=[SimpleNamespace(text=42)]` throws `AttributeError: 'int' object has no attribute 'strip'`. s3 `msg=SimpleNamespace()` throws missing `.content`; `msg=None` throws missing `.content`. These violate the SDK response contract; no JSON claim is accepted. | `src/query.py:475–476` |
| s2/s3 whitespace-first SDK response | **NOT FIXED — NOTE** | `content=[SimpleNamespace(text=' '),SimpleNamespace(text=json.dumps({'claims':[GOOD]}))]` chooses first block, accepts 0 with `not valid JSON: Expecting value`; later valid text is omitted. Completeness only. | `src/query.py:475–477` |
| s2/s3 lone surrogate | **NOT FIXED — NOTE** | `GOOD` with subject `"\ud800"` rejects per claim; the API safely returns valid HTTP 400 JSON containing the UTF-8 codec error. The page displays escaped error text. | `src/structured.py:126–130`; `src/app.py:135–140` |
| s3 N1 parsed giant integer | **NOT FIXED — NOTE** | Python input `{'claims':[dict(GOOD,note=10**5000)]}` yields verified false, empty text, one unknown-key rejection; `json.dumps(result,allow_nan=False)` raises the 4300-digit conversion-limit ValueError. The corresponding raw JSON integer is rejected during parsing and serializes correctly. Not attainable through the reviewed model JSON decoder on this interpreter. | `src/structured.py:94–95`, `266–271`, `289` |

Regression controls all pass: HTML injections in every claim field/key; per-claim injected exception; cyclic/deep/broad parsed input; valid finite/underflow numeric action values rejecting by type; duplicate keys; fences; prose around JSON; concatenated JSON objects; empty/malformed replies; 50/51 claims; oversized requests. These were notes/controls, not unfixed findings.

## Leakage, rendering boundary, and model checks

Exact injection marker:

```text
<img src=x onerror="globalThis.MODEL_INJECTED=1"><script>globalThis.MODEL_INJECTED=2</script>&"'
```

The marker in `kind`, `relation`, `subject`, `object`, `action`, `evidence`, an unknown `note`, or an unknown key rejects. `[GOOD,GOOD+note=MARK,GOOD]` yields exactly two graph sentences and one rejection. All 54 HTTP/page scenarios (10+10+7+27) have no raw injected elements and no executed marker. Error, answer, rejection reason, rejected-claim JSON, and evidence display all go through `esc` at `web/try.html:93,176–182`; the evidence is escaped generated HTML strings, not full browser execution.

`{"claims":[GOOD]}`, fenced JSON, and prose around JSON produce exactly:

```text
- OSIMERTINIB acts on EGFR (inhibitor) [CHEMBL3353410|ACTS_ON|ENSG00000146648|CHEMBL3353410]
```

Greedy extraction `re.search(r"\{.*\}",raw,re.S)` at `src/query.py:477` may discard surrounding model prose or collect too much, but all retained JSON still passes through `verify_structured` (`src/query.py:395`). Concatenated JSON objects reject `not valid JSON: Extra data`; no surrounding model prose is rendered. `claims=[GOOD]*51` retains 50, adds `more than 50 claims; the rest were not read`, and reports grounded false. Duplicate action keys remain last-wins: `ACTIVATOR` then `INHIBITOR` accepts the graph inhibitor; reverse order rejects.

The real prompt (`src/query.py:453–467`; captured `replay_s1/modelui_prompt.txt`) requests fixed claim kinds, exact evidence names/ids, no extra keys/prose, and an empty claims list for abstention. Claim selection is not checked for completeness/relevance. Accepted fields are graph values. Mixed accepted/rejected answers explicitly set `grounded=false`, retain the valid graph sentences, and report rejections; errors before a model reply set `applicable=false` with no groundedness assertion. Mock constructor/request failures with RuntimeError, ValueError, ConnectionError, and TimeoutError include sensitive/HTML markers in exception messages: only the exception type reaches the failure answer, not its message (`src/query.py:474`).

## Box 3/4 documentation

`web/try.html:68–71` describes fixed structured claims, exact graph checking, graph-only answer text, and unknown-key rejection; these behaviors match the replay evidence. `web/try.html:79–83` explicitly calls the prose screen auxiliary and fallible. `web/try.html:90` accurately says the page does not call a model and box 3 accepts manually supplied claim JSON. No approval-bar documentation mismatch found in this assigned page/model surface.

## Artifact map

- `run_replays.py`, `replay_manifest.json`: every source probe and path-only relocation.
- `replay_s1/` and `replay_s2/`: exact legacy model replies, API requests/responses, prompts, page HTML, copied scripts, stdout.
- `replay_s3/`: exact s3 attack definitions, 68 result rows, 27 API requests/responses and page outputs.
- `modelui_sdk_exact_replay.py`, `modelui_legacy_sdk_failure_results.json`: original outage call observations.
- `compare_replays.py`, `comparison.json`: input equality, counts, persistent notes, and s3 output equality.
