"""Independent live-server verification of name-linking regression candidates."""
import hashlib
import json
from pathlib import Path
import time
import urllib.error
import urllib.request

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[1]
BASE = "http://127.0.0.1:8878"

def post(path, text):
    data = json.dumps({"text": text}, ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(BASE + path, data=data,
        headers={"Content-Type": "application/json"})
    start = time.perf_counter()
    try:
        response = urllib.request.urlopen(request, timeout=30)
    except urllib.error.HTTPError as error:
        response = error
    return {"path": path, "input": {"text": text}, "status": response.status,
            "elapsed_ms": round((time.perf_counter() - start) * 1000, 3),
            "body": json.loads(response.read())}

inputs = ["bevacizumab - awwb", "89Zr - trastuzumab", "[89Zr] trastuzumab",
          "osimertinib and generic version of bevacizumab",
          "generic version of bevacizumab", "osimertinib and bevacizumab",
          "[89Zr] trastuzumab and osimertinib",
          "osimertinib and [89Zr] trastuzumab",
          "Mvasi and bevacizumab", "osimertinib EGFR", "EGFR osimertinib"]
before = hashlib.sha256((ROOT / "data/processed/oncokg.sqlite").read_bytes()).hexdigest()
cases = []
for value in inputs:
    cases.extend([post("/api/explore", value), post("/api/resolve", value)])
for value in ["Which trials evaluate osimertinib and generic version of bevacizumab?",
              "Which trials evaluate [89Zr] trastuzumab and osimertinib?",
              "Which trials evaluate osimertinib and [89Zr] trastuzumab?"]:
    cases.append(post("/api/ask", value))
after = hashlib.sha256((ROOT / "data/processed/oncokg.sqlite").read_bytes()).hexdigest()
result = {"base": BASE, "cases": cases, "db_sha256_before": before,
          "db_sha256_after": after, "database_unchanged": before == after}
(OUT / "regression_http.json").write_text(json.dumps(result, indent=2, ensure_ascii=False), encoding="utf-8")
for case in cases:
    body = case["body"]
    print(json.dumps({"path": case["path"], "text": case["input"]["text"],
        "status": case["status"], "center": body.get("center", {}).get("id"),
        "refused": body.get("refused"), "also": body.get("also"),
        "components": [{k: c.get(k) for k in ("raw", "status", "drug_id", "verdict")} for c in body.get("components", [])],
        "entities": body.get("entities"), "answer": body.get("answer")}, ensure_ascii=False))
