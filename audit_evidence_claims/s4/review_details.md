# Structured answers: independent round 4 review

Reviewed HEAD `8adf2dd4e3cb9e2559dcabd67670300dbba6503c`, including the repair described in `CODEX_STRUCTURED_S3_VERDICT.md`. Baseline: `aa5655ae89c47631fefb9c868989ba2c1befa82e`; repair commits: `60b9c61`, `6bcde72`, `8adf2dd`.

**316 tests passed in 9.12s. All prior BLOCKER / SHOULD FIX reproductions are FIXED. No new approval-bar failure was found.** Faithful supported demo/profile claims pass **73/73 with copied labels and 73/73 with IDs**. Remaining historical NOTES are explicitly retained below; approval does not mean every robustness or completeness issue has disappeared.

All scratch writes are under `audit_evidence_claims/s4/`. Production graph connections used by audit probes were query-only; graph mutations used in-memory copies. Bytecode generation and pytest cache were disabled; test temporary files were routed under s4. Existing s4 brief/log were preserved. Tests and tracked files were not edited. See [root_manifest.json](root_manifest.json), [root_results.json](root_results.json), [pytest_stdout.txt](pytest_stdout.txt), and [final_verification.json](final_verification.json).

## BLOCKERS

None. Replays did not demonstrate an unsupported accepted graph fact, model-authored answer prose, or executable HTML injection in the reviewed path. The earlier whole-name identity bypass rejects. Retired-edge, foreign-question evidence, wrong endpoint/relation/value, PROFILE-as-relation, malformed-type, and unknown-key attacks retain their rejection behavior.

## SHOULD FIX

None under the supplied approval bar. In particular, **s3 I1 / repair S1 is FIXED**: a whole alias returning multiple candidate node IDs is refused before endpoint membership can select one. The module docstring and both READMEs now describe that behavior.

## NOTES

### Reproduction coverage and methodology

Every executable reproduction from the s1–s3 findings was replayed on current code. Repeated rounds' copies were included where they existed. Paths were adapted only to keep imports and outputs correct; original inputs were compared with saved historical inputs. The old assertion that a bug must still occur was recorded as data rather than used to abort a repaired replay. Old hardcoded commit fields inside copied probes are historical metadata, not the execution revision; current manifests record HEAD above.

| Source reproduction | Current execution and result |
| --- | --- |
| s1 and s2 root probes | 117 cases each; identical inputs; zero exceptions. [root_results.json](root_results.json), [s1 results](replay_s1/root_probe_results.json), [s2 results](replay_s2/root_probe_results.json). |
| s1 and s2 identity probes | 128 cases + 2 fixtures each; all 142 retired edges reject in each sweep, including a stale evidence allowlist. |
| s2 identity attack and root contract | 34 live-input cases + 10 fixtures, plus the independent duplicate-label fixture; original inputs retained. |
| s3 identity attack and root confirmation | 35 identity cases and all 8 constructor-based confirmation cases. [constructor outputs](replay_s3/root_confirmation.json). |
| Independent s4 alias controls | 15 cases: two/three candidates, exact IDs, wrong-edge ID, retired duplicate, unique alias, and BeiGene/BeOne rename controls; every expected result met. [boundary_results.json](identity/boundary_results.json). |
| s1/s2 faithful probes and their s3 copies | Four executions of seven questions, all 73 label and 73 ID claims accepted per execution; exact phase/schema inputs preserved. |
| Supplemental faithful replays | Both original and s3 action/PROFILE/empty-phase/dictionary scripts rerun; original inputs and prior corrected outputs agree. |
| s1 and s2 model/UI probes | 29 model calls per round, 10 HTTP and 10 actual-JavaScript-handler cases per round. Original service-failure mock returns successfully now, so captured separately rather than lost from the legacy exception-only recorder. |
| s2 additional model/UI probes | 22 recorded rows including 55 depth subcases; 7 HTTP and 7 page-handler cases. |
| s3 additional model/UI probes | 68 rows; 27 HTTP and 27 page-handler cases. Exact inputs and all recorded s3 outputs match. |

Detailed evidence: [identity findings](identity/findings.md), [identity replay manifest](identity/replay_manifest.json), [faithful/docs findings](faithful/findings.md), [faithful replay manifest](faithful/replay_manifest.json), [historical faithful input comparison](faithful/historical_input_comparison.json), [model/UI findings](modelui/findings.md), [model/UI comparison](modelui/comparison.json).

HTTP tests exercise the actual local handler. Page checks execute the current `web/try.html` handler in a Node VM and inspect escaped output; they are **not full-browser execution tests**. LLM behavior is tested with controlled SDK mocks, not a live service. The auxiliary free-prose checker is outside this review; no independent revalidation of its historical 22/38 result is claimed.

### FIXED / NOT FIXED per historical finding

The common question `Q` below is `What does osimertinib target?`. Its exact valid claim `GOOD` is:

```json
{"kind":"relation","relation":"ACTS_ON","subject":"osimertinib","object":"EGFR","evidence":"CHEMBL3353410|ACTS_ON|ENSG00000146648|CHEMBL3353410","action":"INHIBITOR"}
```

`GOOD[field := value]` denotes changing only that field, inside `{"claims":[...]}`. Full raw payloads, including oversized strings, are retained in the linked JSON artifacts.

| Prior finding | Status at HEAD | Exact reproduction / observed output; current code |
| --- | --- | --- |
| s1 B1: partial name hidden by removing non-ASCII letters | **FIXED** | `Q`, `GOOD[subject := "osimertinib가 아닌"]` → `verified=false`, `accepted=[]`, `text=""`, reason `'osimertinib가 아닌' is not written the way the graph writes names (use the id or the name as it appears in the evidence)`. Chinese, zero-width, emoji and other original variants replayed. `src/structured.py:128–138`. |
| s1 S1: salt and long sponsor labels copied from evidence reject | **FIXED** | Original `ALECTINIB HYDROCHLORIDE` relation/drug claims, `Second Affiliated Hospital Of Nanchang University` and `Tianjin Medical University Cancer Institute And Hospital` sponsorship claims all accept. Each long sponsor claim has `trial_count=2`; exact individual inputs and graph-rendered outputs are in [historical_input_comparison.json](faithful/historical_input_comparison.json). `src/structured.py:117–126`. |
| s1 faithful follow-up: exact PRKCA target name rejects | **FIXED** | `APRINOCARSEN` → `PRKCA`, action `ANTISENSE INHIBITOR`, edge `CHEMBL2108287|ACTS_ON|ENSG00000154229|CHEMBL2108287` accepts. Changing only action to `INHIBITOR` still rejects. `src/structured.py:117–126,192–198`. |
| s1 S2: array/dictionary kind or relation raises | **FIXED** | `{"claims":[{"kind":[]}]}` → rejection `unknown kind []; use relation, trial or drug`, no exception. Original dictionary-kind and array/dictionary-relation cases also reject. `src/structured.py:150–155,174–177,283–289`. |
| s1 S3: raw NaN breaks HTTP JSON/page | **FIXED** | Raw JSON with `GOOD.action=NaN` rejects before acceptance; HTTP response is valid JSON and page handler completes. Literal Infinity and -Infinity also reject. `src/structured.py:72–81,263–271`; `src/app.py:135–140`. |
| s1 S4: empty/missing-text/null-text content and excessive JSON nesting | **FIXED** | SDK `content=[]`, `[SimpleNamespace(type='tool_use')]`, `[SimpleNamespace(text=None)]` return normal rejected results. `'{"claims":' + '['*5000 + 'null' + ']'*5000 + '}'` rejects without raising; original 1100/20000-depth and raw giant-number cases rerun. `src/query.py:475–478`; `src/structured.py:263–271`. Invalid SDK numeric/missing-message shapes remain separate NOTES below. |
| s1 empty-claims answer note | **FIXED** | `{"claims":[]}` → `empty=true`, `rejected=[]`; `answer(use_llm=True)` says `The model found nothing in the evidence that answers this question.` without a removed-claim suffix. `src/structured.py:273–276`; `src/query.py:395–401`. |
| s1 PROFILE live-edge wording | **FIXED** | Original profile stage/count claim still accepts with zero matching SQL edge rows; exception is now explicit in `src/structured.py:26–28`, `README.md:453–454`, `README.ko.md:318`. |
| s1 obsolete query/dashboard prose-check description | **FIXED** | `src/query.py:12–18`, `web/template.html:261–267` describe model JSON claims, exact verification and program rendering; generated dashboard/index agree. |
| s1 English/Korean 22/38 contradiction | **FIXED** | Both now say only 22 of 38 passed: `README.md:537`, `README.ko.md:370`. This is wording agreement, not a new auxiliary-checker evaluation. |
| s1/s2 reader-wide no-model-text wording | **FIXED** | `README.md:460–462` limits the promise to the answer and explicitly separates rejected-claim diagnostics. |
| s2 shared exact-label uniqueness SHOULD FIX | **FIXED** | In-memory `UPDATE node SET label='OSIMERTINIB' WHERE id='CHEMBL3707320'`; original OSIMERTINIB/EGFR claim → no resolved IDs, no accepted claims, reason `'OSIMERTINIB' is the label of 2 drug nodes; use the id`. `src/structured.py:117–126`. |
| s2 nonfinite diagnostic serialization SHOULD FIX | **FIXED** | Raw action `1e309` / `-1e309` reject during parsing. Parsed Python NaN/Infinity reject with diagnostic values converted to strings; `json.dumps(result, allow_nan=False)` succeeds. `src/structured.py:76–96,263–271,289`. |
| s1/s2 SDK failure and missing SDK operational notes | **FIXED** | Original `messages.create` raising `RuntimeError('simulated SDK failure')` returns `The language model could not be used (RuntimeError); no answer was generated.`; missing package reports that cause. Checks: `grounded=null`, `applicable=false`, `accepted=0`, `rejected=[]`. Exception-message markers do not leak. `src/query.py:388–394,448–451,468–474`. |
| s2 ambiguous alias note / s3 I1 unique-node documentation failure | **FIXED** | Original `azalias` multi-ID fixture and real-constructor `AstraZeneca!`, `astra-zeneca`, `ASTRAZENECA?` collision fixtures all reject with `names 2 company nodes; use the id`. See exact s3 reproduction below. `src/structured.py:140–145`. |
| s1/s2/s3 retired PROFILE through a cached drug alias | **NOT FIXED — NOTE** | Retire `CHEMBL3353410` only in an in-memory DB while retaining the dictionary. For `What is osimertinib?`, `{"claims":[{"kind":"drug","drug":"osimertinib","evidence":"profile:CHEMBL3353410","max_stage":"APPROVAL"}]}` still accepts the retained property. Direct retired ID rejects. `src/structured.py:133–145,236–249`; no retired Drug in the persisted graph. This remains the prior graph-property/liveness NOTE, not a newly demonstrated unsupported fact. |
| s2/s3 alias shadowing | **NOT FIXED — NOTE** | Drug claim name `met` resolves as Target and rejects; `METFORMIN` and `CHEMBL1431` accept the same supported fact. `src/structured.py:117–127`. Completeness only. |
| s2/s3 Unicode case and long-label restrictions | **NOT FIXED — NOTE** | Fixture literal `ÄRZT` accepts; `ärzt` rejects. A 121-character graph label rejects at the length guard. No current graph labels exceed 120 characters. `src/structured.py:106–107,117–128`. |
| s2/s3 nonfinite parse-error wording | **NOT FIXED — NOTE** | Raw `NaN` / `1e309` are safely rejected but reason remains `not valid JSON: nested too deeply`. `src/structured.py:268–271`. |
| s2/s3 empty-claims page wording | **NOT FIXED — NOTE** | `{"claims":[]}` shows `버린 주장 0개` and zero accepted claims; page does not explain `empty`. Answer path itself is fixed. `web/try.html:174–180`. |
| s2/s3 invalid SDK object shapes | **NOT FIXED — NOTE** | `content=[SimpleNamespace(text=42)]` raises `AttributeError: 'int' object has no attribute 'strip'`; missing `.content` and a `None` message also raise. These mocks violate the SDK response shape and do not allow an unsupported JSON claim into the answer. `src/query.py:475–476`. |
| s2/s3 first whitespace SDK block masks later valid JSON | **NOT FIXED — NOTE** | `[text=' ', text=validJSON]` selects the first truthy text, strips it to empty, then rejects. `src/query.py:475–478`. Completeness only. |
| s2/s3 lone-surrogate response encoding | **NOT FIXED — NOTE** | `GOOD[subject := '\ud800']` rejects; API returns valid HTTP 400 JSON with UTF-8 codec error, page displays the escaped error. `src/app.py:135–140`. |
| s3 parsed 5001-digit integer serialization | **NOT FIXED — NOTE** | Python `{"claims":[dict(GOOD,note=10**5000)]}` rejects with no answer text, but serializing diagnostics raises the 4300-digit-limit `ValueError`. Equivalent raw JSON rejects safely before claim checking. This requires a preconstructed Python integer beyond the JSON parser's ordinary limit. `src/structured.py:94–95,289`. |
| s1–s3 closed-schema omissions | **NOT FIXED — NOTE; deliberate limit** | Adding `drug_type` or `aliases_known` to a valid profile claim rejects as unknown keys. Parent ownership, enrollment/title, confidence and arbitrary mechanism prose remain inexpressible. Completeness is explicitly excluded from the guarantee. `src/structured.py:48–55,159–160`; `README.ko.md:320–322`; `web/template.html:266`. |

Previously passing observations remain regression passes rather than bugs requiring a repair: duplicate JSON keys use the final parsed value and validate it; 51/1000 claims retain only the first 50 plus an excess-count rejection; fenced model JSON accepts while concatenated objects reject; wrong-question citations and every retired edge reject; no current stored-code `_norm` collision was found; sponsorship wording, multi-phase/empty-phase rendering, and HTML escaping remain faithful. Exact probes and outputs are included in the artifacts linked above.

### Exact s3 repair reproduction and controls

The fixture changes only the in-memory copy:

```sql
UPDATE node SET label='Astrazeneca' WHERE id='ORG:genentech';
```

Instantiate `OncoKG` against that copied connection, using its real constructor and linker. It builds:

```json
{"astrazeneca":["ORG:astrazeneca","ORG:genentech"]}
```

Question: `What is AstraZeneca running in NSCLC?`

Original s3 exact claim:

```json
{"claims":[{"kind":"relation","relation":"SPONSORS_TRIAL_OF","subject":"AstraZeneca!","object":"osimertinib","evidence":"ORG:astrazeneca|SPONSORS_TRIAL_OF|CHEMBL3353410|","trial_count":14}]}
```

Observed now:

```json
{"verified":false,"accepted":[],"text":"","rejected":[{"claim":{"kind":"relation","relation":"SPONSORS_TRIAL_OF","subject":"AstraZeneca!","object":"osimertinib","evidence":"ORG:astrazeneca|SPONSORS_TRIAL_OF|CHEMBL3353410|","trial_count":14},"why":"'AstraZeneca!' names 2 company nodes; use the id"}]}
```

The second original s3 claim, subject `AstraZeneca!`, object `CHEMBL1201583`, edge `ORG:genentech|SPONSORS_TRIAL_OF|CHEMBL1201583|`, `trial_count=5`, also rejects with that reason. Citing either candidate's genuine retrieved edge cannot disambiguate the alias for acceptance. Exact outputs: [s3 identity replay](identity/replay_s3/identity_attack_results.json), [independent constructor replay](replay_s3/root_confirmation.json).

The relevant before/after is the existing committed repair; this audit made no code edits:

```python
# Before, 6bcde72:
return {e["id"], *e.get("also_matching_ids", [])}, None

# Current, src/structured.py:140–145:
ids = {e["id"], *e.get("also_matching_ids", [])}
if len(ids) > 1:
    return set(), f"'{name}' names {len(ids)} {want.lower()} nodes; use the id"
return ids, None
```

Positive controls matter: exact `ORG:astrazeneca` and `ORG:genentech` accept their own retrieved edges; Genentech's ID on the AstraZeneca edge rejects. Three-candidate aliases reject. Retiring the conflicting company before constructing a fresh index restores singleton-alias acceptance. Persisted `BeiGene`, `BeOne`, and `ORG:beonemedicines` all resolve to the same one node and accept their own edge.

One boundary must be stated accurately: with the second fixture label `Astra-Zeneca`, the literal `AstraZeneca` remains a unique exact graph label and can accept only the AstraZeneca edge; `AstraZeneca!` enters the ambiguous alias branch and rejects both candidates. This matches the documented alternatives (ID, unique literal label, or whole singleton alias); it is not evidence that a multi-ID alias passed the new check.

Current source graph has zero multi-ID company keys and zero duplicate live same-type labels. Both persisted and fixture SQLite integrity checks return `ok`. Collision findings are constructor-valid synthetic boundary checks, not claims that the current graph contains those collisions.

### Usefulness, rendering, model path, and documentation

| Question | Copied-label / ID accepted claims |
| --- | --- |
| `Which companies are developing osimertinib?` | 12/12 and 12/12; renders lead sponsorship, with the explicit warning that sponsorship is not development evidence. |
| `What trials evaluate Tagrisso?` | 24/24 and 24/24; EVALUATES plus trial phase/status. |
| `What does osimertinib target?` | 1/1 and 1/1. |
| `Which drugs act on ALK?` | 22/22 and 22/22; relation plus supported stage/count claims. |
| `What is AstraZeneca running in NSCLC?` | 12/12 and 12/12. |
| `What is the capital of France?` | No evidence; refusal before the model is called. |
| `What is osimertinib?` | 2/2 and 2/2; retrieved PROFILE plus mechanism. |

The exact live multi-phase claim for `NCT00153842` with phases `["PHASE1","PHASE2"]`, status `TERMINATED`, and edge `NCT00153842|EVALUATES|CHEMBL1023|NCT00153842` renders both phases and that status. The original in-memory `NCT03909334` empty-phase fixture renders `no phase given; status ACTIVE_NOT_RECRUITING`. Action `ANTISENSE INHIBITOR` remains distinct from `INHIBITOR`. Render uses database labels and verified graph values (`src/structured.py:298–331`); optional fields do not add unsupported claims.

The prompt gives retrieved IDs/statements and the three claim forms, forbids extra keys/prose and permits `{"claims":[]}` (`src/query.py:452–467`). Greedy JSON extraction is unchanged (`:475–478`): surrounding prose/fences are not rendered, and concatenated objects fail JSON decoding. Checks accurately distinguish verified/rejected claims, empty claims, and no model reply (`:388–407`). Invalid SDK objects are the retained NOTE above.

Exact HTML marker used by s3 replays:

```text
<img src=x onerror="globalThis.MODEL_INJECTED=1"><script>globalThis.MODEL_INJECTED=2</script>&"'
```

Putting it in each claim field or an unknown key rejects the claim. Mixed `[GOOD, GOOD+note=MARKER, GOOD]` renders exactly two graph sentences, no marker in answer text, and one escaped rejected diagnostic. Across all 54 HTTP/page replay cases (10+10+7+27), no raw injected element appeared. Relevant output sinks escape text, reason, JSON diagnostics and evidence (`web/try.html:93,176–181`).

Documentation comparison:

- Unique aliases: `src/structured.py:29–32`, `README.md:455–457`, `README.ko.md:318` agree with the singleton check at `src/structured.py:140–145`; the old description of several IDs as one merged entity is gone.
- Retrieved PROFILE exception: module `:26–28` and both README sections explicitly allow it; facts still come from the graph.
- Answer/diagnostic boundary: `README.md:460–462`, `README.ko.md:319–320`, `web/try.html:68–71` agree with the renderer and escaped diagnostic display.
- Dashboard section 06 (`web/template.html:261–267`, generated dashboard/index) describes structured claims and excludes relevance/completeness from the guarantee.
- README known defect 13 and try box 4 describe the auxiliary prose checker as fallible. No stronger structured-answer guarantee is inferred from that separate screen.

### Standards and spec review

**Standards axis:** No tracked AGENTS, CODING_STANDARDS, CONTRIBUTING or issue-tracker standard was found. No documented standards violation was identified in the repair diff. The user's evidence-based and read-only review instructions govern this audit; no implementation repair or unrelated setup was performed.

**Spec axis:** No missing or incorrect repair requirement was identified under the supplied A–F scope and approval bar. The s3 alias fix was exercised both through the original real-constructor fixture and independent controls. Faithful demo claims remain expressible, checked and accepted. Existing completeness and operational NOTES are distinguished from unsupported accepted facts and inaccurate guarantees.

### Re-run commands

Run from the repository root with UTF-8 output and bytecode disabled:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
$env:PYTHONIOENCODING='utf-8'
$env:PYTHONUTF8='1'
python -B audit_evidence_claims/s4/root_runner.py
python -B audit_evidence_claims/s4/identity/replay.py
python -B audit_evidence_claims/s4/identity/boundary_probe.py
python -B audit_evidence_claims/s4/faithful/runner.py
python -B audit_evidence_claims/s4/faithful/compare.py
python -B audit_evidence_claims/s4/modelui/run_replays.py
python -B audit_evidence_claims/s4/modelui/compare_replays.py
```

These operate on copied probes and keep new output within s4. The root runner invokes `python -B -m pytest tests -q -p no:cacheprovider --basetemp <s4/root_tmp/pytest_base>` with TEMP/TMP/TMPDIR under s4. [final_verification.json](final_verification.json) records final HEAD, file hashes, tracked status, outside-s4 scratch check, replay assertions and report-link checks.

VERDICT: APPROVE
