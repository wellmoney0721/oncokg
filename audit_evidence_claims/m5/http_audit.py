"""Read-only HTTP probes for 514929c. Writes only next to this script."""
import concurrent.futures
import hashlib
import json
import time
import urllib.request
import urllib.error
from pathlib import Path

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[1]
BASE = "http://127.0.0.1:8880"
DB = ROOT / "data/processed/oncokg.sqlite"


def request(payload=None, raw=None, path="/api/explore"):
    data = raw if raw is not None else json.dumps(payload, ensure_ascii=False).encode()
    req = urllib.request.Request(BASE + path, data=data,
                                 headers={"Content-Type": "application/json"})
    start = time.perf_counter()
    try:
        response = urllib.request.urlopen(req, timeout=30)
    except urllib.error.HTTPError as err:
        response = err
    content = response.read()
    try:
        body = json.loads(content)
    except ValueError:
        body = content.decode(errors="replace")
    return {"status": response.status, "bytes": len(content),
            "ms": round((time.perf_counter() - start) * 1000, 3), "body": body}


def digest():
    return hashlib.sha256(DB.read_bytes()).hexdigest()


before = digest()
get = urllib.request.urlopen(BASE, timeout=10)
html = get.read()
(OUT / "served_try.html").write_bytes(html)
results = {"get": {"status": get.status, "bytes": len(html),
                    "matches_worktree": html == (ROOT / "web/try.html").read_bytes()},
           "cases": {}}
cases = {
    "empty_object": {}, "empty_text": {"text": ""}, "spaces": {"text": " \t\n "},
    "null_text": {"text": None}, "numeric_text": {"text": 123},
    "json_list": [], "json_null": None,
    "wrong_route": {"text": "EGFR"},
    "known": {"text": "osimertinib"}, "unknown": {"text": "no such thing zz"},
    "refused": {"text": "Mvasi"},
    "trim_case": {"text": "  OsImErTiNiB\n"},
    "long_prefix": {"text": "osimertinib " + "x" * 600},
    "long_hidden_suffix": {"text": "x" * 500 + " osimertinib"},
    "oversized_body": {"text": "x" * 21000},
    "drug_then_target": {"text": "osimertinib EGFR"},
    "refused_and_real": {"text": "Mvasi bevacizumab"},
    "company_alias_collision": {"text": "Roche"},
    "company_id": {"text": "ORG:roche"},
    "disease": {"text": "MONDO_0005233"},
}
for name, payload in cases.items():
    result = request(payload, path="/api/no-such-route" if name == "wrong_route" else "/api/explore")
    result["input"] = payload
    results["cases"][name] = result
results["cases"]["malformed_json"] = request(raw=b'{"text":')
jobs = ["osimertinib", "EGFR", "AstraZeneca", "Mvasi", "MONDO_0005233", "NCT00200395"] * 4
start = time.perf_counter()
with concurrent.futures.ThreadPoolExecutor(max_workers=12) as pool:
    responses = list(pool.map(lambda x: request({"text": x}), jobs))
results["concurrency"] = {"requests": len(jobs), "workers": 12,
    "wall_ms": round((time.perf_counter() - start) * 1000, 3),
    "all_200": all(r["status"] == 200 for r in responses),
    "responses": [{"input": x, "status": r["status"], "ms": r["ms"],
                   "center": r["body"].get("center", {}).get("id"),
                   "refused": r["body"].get("refused")} for x, r in zip(jobs, responses)]}
results["db_sha256_before"] = before
results["db_sha256_after"] = digest()
results["db_unchanged"] = before == results["db_sha256_after"]
(OUT / "http_results.json").write_text(json.dumps(results, ensure_ascii=False, indent=2), encoding="utf-8")
for name, result in results["cases"].items():
    body = result["body"]
    print(name, result["status"], result["bytes"], result["ms"],
          body.get("center", {}).get("id") if isinstance(body, dict) and "center" in body else body)
print(json.dumps({k: v for k, v in results.items() if k not in ("cases", "concurrency")}, ensure_ascii=False))
print("concurrency", results["concurrency"]["all_200"], results["concurrency"]["wall_ms"])
