# Independent identity and value review

Commit: `aa5655ae89c47631fefb9c868989ba2c1befa82e`.

Reproduce in PowerShell:

```powershell
$env:PYTHONDONTWRITEBYTECODE='1'
python audit_evidence_claims\s1\identity_probe.py
```

This writes only `identity_probe_results.json` beside the script. The live SQLite connection is query-only. Two explicitly labelled regression fixtures use isolated in-memory database copies and do not describe current persisted graph contents.

## BLOCKERS

### Whole-name guarantee is bypassed by non-ASCII text

Question: `What does osimertinib target?`

Exact payload:

```json
{"claims":[{"kind":"relation","relation":"ACTS_ON","subject":"osimertinib가 아닌","object":"EGFR","evidence":"CHEMBL3353410|ACTS_ON|ENSG00000146648|CHEMBL3353410","action":"INHIBITOR"}]}
```

Observed: `verified=true`, `rejected=[]`, one accepted relation. `link_entities` reports `matched_text="osimertinib가"`, omitting the final word `아닌`. The full subject means "not osimertinib" rather than naming that drug alone. The rendered text is:

```text
- OSIMERTINIB acts on EGFR (inhibitor) [CHEMBL3353410|ACTS_ON|ENSG00000146648|CHEMBL3353410]
```

`src/structured.py:64-65` removes all non-ASCII letters before `resolve` compares the matched text and full subject at `src/structured.py:85-92`. This violates the documented whole-name identity condition (`src/structured.py:29`). It does **not** make the canonical rendered graph fact unsupported or leak the discarded subject text. `非osimertinib` and `osimertinib是安全的` also pass. Full evidence: `identity_probe_results.json:297`.

## SHOULD FIX

### Malformed value types raise exceptions instead of a rejected claim

Question: `What does osimertinib target?`

Exact minimal input: `{"claims":[{"kind":[]}]}`. `kind not in KEYS` at `src/structured.py:100` raises `TypeError: unhashable type: 'list'`. Replacing `relation` with `[]` in a complete valid relation claim similarly raises at `src/structured.py:122`. Dictionaries in either field behave the same way. The probe uses complete claims for these tests. Output evidence starts at `identity_probe_results.json:1635`.

Exact raw string construction `'{"claims":' + '[' * 5000 + 'null' + ']' * 5000 + '}'` raises `RecursionError: maximum recursion depth exceeded while decoding a JSON array from a unicode string`. `'{"claims":[' + '9' * 5000 + ']}'` raises `ValueError` for the 4,300-digit integer conversion limit. `verify` catches only `JSONDecodeError` (`src/structured.py:210-215`). Output evidence: `identity_probe_results.json:7908` and `:7920`.

### An exact canonical salt name in the ALK demo evidence is rejected

Question: `Which drugs act on ALK?`

Exact payload:

```json
{"claims":[{"kind":"relation","relation":"ACTS_ON","subject":"ALECTINIB HYDROCHLORIDE","object":"ALK","evidence":"CHEMBL3707320|ACTS_ON|ENSG00000171094|CHEMBL3707320","action":"INHIBITOR"}]}
```

Observed: `verified=false`, `accepted=[]`, rejection `"'ALECTINIB HYDROCHLORIDE' does not name exactly one drug on its own"`. The linker accumulates both the salt and parent drug (`src/query.py:147-170`), so `len(ents)==1` fails (`src/structured.py:86`). Changing only subject to `CHEMBL3707320` succeeds and renders the salt label. This is an expressible graph fact but the names-as-written prompt (`src/query.py:456`) leads to a false rejection. Evidence: `identity_probe_results.json:7932` and `:7979`. Treat as usefulness issue rather than unsupported acceptance.

## NOTES

- The live graph has no multi-id company key and no live edge whose endpoint is absent or retired. All 142 currently retired edges reject even when explicitly added to the retrieved-id allowlist. Normal aliases and exact IDs work; salt-to-parent substitution, foreign-question evidence, wrong relation, unsupported action, wrong counts, and mixed phase types reject.
- Stored code inventories have no `_norm` collision for action types, phases, statuses, or maximum stages. In particular, `ANTISENSE INHIBITOR` does not equal `INHIBITOR`. Optional separator/case variants pass and render the original DB value. Dictionaries and counts are in `identity_probe_results.json:8021` onward.
- `True`, floats, numeric strings, null, arrays, NaN and Infinity reject for integer fields. Duplicate JSON object keys take their final value: a final supported action passes, a final unsupported action rejects. No unchecked earlier value reaches rendered text.
- Fifty-one valid claims yield 50 accepted claims plus a rejection saying the rest were not read; overall `verified=false`. Twenty-thousand-character invalid action rejects; a 1,100-deep list is rejected as a non-object claim on this interpreter, while 5,000 nesting raises as above.
- A PROFILE pseudo-id is not an SQL edge, yet legitimate node-backed profile claims pass. This is evidence-consistent but the literal "live edge" docstring guarantee needs an exception (`src/structured.py:113-115`).
- Synthetic-only fixture: giving `companies['astrazeneca']` both AstraZeneca and Genentech IDs makes `resolve` return two IDs but the AstraZeneca claim passes. `src/structured.py:92,133` tests membership instead of singleton equality. This is a latent mismatch with the exact-one-node guarantee, not a currently reachable multi-company example. Evidence: `identity_probe_results.json:11363`.
- Synthetic-only fixture: marking osimertinib retired in an in-memory DB leaves the resolved dictionary intact; its name-based PROFILE claim still passes. Alias resolution does not recheck live node status and `_drug` fetches props without a live filter (`src/structured.py:85-92,188`). The current graph contains no retired Drug node. Evidence: `identity_probe_results.json:11413`.
