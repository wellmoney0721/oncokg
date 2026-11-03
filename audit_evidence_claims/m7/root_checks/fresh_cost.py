"""Bounded, same-data cost comparison and owned CLI lock-contention check."""
import concurrent.futures
import hashlib
import json
import os
from pathlib import Path
import socket
import statistics
import subprocess
import sys
import time
import types
import urllib.error
import urllib.request

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[2]
PORT = 8902
BASE = f"http://127.0.0.1:{PORT}"
PREFIX = "isolated_" if len(sys.argv) > 1 and sys.argv[1] == "isolated" else ""
sys.path.insert(0, str(ROOT / "src"))


def dump(name, obj):
    (OUT / (PREFIX + name)).write_text(json.dumps(obj, indent=2, ensure_ascii=False), encoding="utf8")


if len(sys.argv) > 1 and sys.argv[1] == "worker":
    import query
    ref, kind, size = sys.argv[2], sys.argv[3], int(sys.argv[4])
    mod = query
    if ref != "HEAD":
        mod = types.ModuleType("cost_previous")
        mod.__file__ = str(ROOT / "src/query.py")
        sys.modules[mod.__name__] = mod
        code = subprocess.check_output(["git", "show", f"{ref}:src/query.py"], cwd=ROOT).decode("utf8")
        exec(compile(code, mod.__file__, "exec"), mod.__dict__)
    kg = mod.OncoKG()
    kg.conn.execute("PRAGMA query_only=ON")
    value = {"plain": " ", "split": ";", "slash": "/"}[kind].join(["x"] * size)
    times = []
    for _ in range(3):
        start = time.perf_counter()
        entities = kg.link_entities(value)
        times.append(time.perf_counter() - start)
    detail = {}
    if ref == "HEAD":
        for name in ["_resolver_blocked", "_link"]:
            start = time.perf_counter()
            result = getattr(kg, name)(value)
            detail[name] = {"seconds": time.perf_counter() - start, "result_count": len(result)}
    kg.conn.close()
    print(json.dumps({"ref": ref, "kind": kind, "size": size, "characters": len(value),
                      "times": times, "median": statistics.median(times),
                      "entities": entities, "stages": detail}))
    raise SystemExit(0)


def post(path, payload, timeout=20):
    start = time.perf_counter()
    req = urllib.request.Request(BASE + path, data=json.dumps(payload).encode(),
                                 headers={"Content-Type": "application/json"})
    try:
        response = urllib.request.urlopen(req, timeout=timeout)
    except urllib.error.HTTPError as error:
        response = error
    raw = response.read()
    return {"path": path, "payload": payload, "status": response.status,
            "seconds": time.perf_counter() - start, "bytes": len(raw), "body": json.loads(raw)}


env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1", "PYTHONUTF8": "1",
       "PYTHONIOENCODING": "utf-8", "TEMP": str(OUT / "tmp"),
       "TMP": str(OUT / "tmp"), "TMPDIR": str(OUT / "tmp")}
rows = []
for kind, size in [("plain", 250), ("split", 250), ("split", 1000), ("split", 2000)]:
    for ref in ["b7a00f9", "HEAD"]:
        try:
            result = subprocess.run([sys.executable, "-B", __file__, "worker", ref, kind, str(size)],
                                    cwd=ROOT, env=env, capture_output=True, timeout=35)
            assert result.returncode == 0, result.stderr.decode("utf8", "replace")
            row = json.loads(result.stdout)
        except subprocess.TimeoutExpired:
            row = {"ref": ref, "kind": kind, "size": size, "timeout_seconds": 35}
        rows.append(row)
        dump("fresh_cost_comparison.json", rows)
        print(json.dumps(row), flush=True)

db = ROOT / "data/processed/oncokg.sqlite"
before = hashlib.sha256(db.read_bytes()).hexdigest()
with socket.socket() as sock:
    assert sock.connect_ex(("127.0.0.1", PORT)) != 0, "audit port occupied"
with (OUT / (PREFIX + "fresh_cost_server.txt")).open("w", encoding="utf8") as log:
    proc = subprocess.Popen([sys.executable, "-B", "-u", "src/app.py", str(PORT)], cwd=ROOT,
                            env=env, stdout=log, stderr=subprocess.STDOUT,
                            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0))
    try:
        for _ in range(100):
            assert proc.poll() is None
            try:
                urllib.request.urlopen(BASE, timeout=1).read()
                break
            except OSError:
                time.sleep(.1)
        else:
            raise RuntimeError("server unavailable")
        baseline = post("/api/explore", {"text": "EGFR"})
        value = ";".join(["x"] * 250)
        sequential = [post(path, {"text": value}) for path in ["/api/explore", "/api/ask"]]
        answer = ";".join(["x"] * 2000)
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
            started = time.perf_counter()
            leader = pool.submit(post, "/api/check", {"text": "EGFR", "answer": answer})
            time.sleep(.1)
            dispatched = time.perf_counter() - started
            follower = pool.submit(post, "/api/explore", {"text": "EGFR"})
            get_start = time.perf_counter()
            response = urllib.request.urlopen(BASE, timeout=3)
            response.read()
            live_get = {"status": response.status, "seconds": time.perf_counter() - get_start}
            check, queued = leader.result(), follower.result()
        after_request = post("/api/explore", {"text": "EGFR"})
        dump("fresh_cost_http.json", {"baseline": baseline, "sequential": sequential,
             "check": check, "queued_egfr": queued, "follower_dispatched_seconds": dispatched,
             "live_get": live_get, "normal_after": after_request})
        print(json.dumps({"check_seconds": check["seconds"], "queued_egfr_seconds": queued["seconds"],
                          "normal_after_seconds": after_request["seconds"]}), flush=True)
    finally:
        proc.terminate()
        proc.wait(timeout=10)
        with socket.socket() as sock:
            closed = sock.connect_ex(("127.0.0.1", PORT)) != 0
        after = hashlib.sha256(db.read_bytes()).hexdigest()
        dump("fresh_cost_lifecycle.json", {"pid": proc.pid, "port": PORT,
             "port_closed": closed, "database_unchanged": before == after,
             "before": before, "after": after, "exit": proc.returncode})
        assert closed and before == after
