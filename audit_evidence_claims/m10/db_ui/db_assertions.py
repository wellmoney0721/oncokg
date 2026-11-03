"""Assert the reused database reproductions' current results; writes beside this script."""
import json
from pathlib import Path

OUT = Path(__file__).resolve().parent
checks = []

def read(name):
    return json.loads((OUT / name).read_text(encoding="utf-8"))

def check(name, ok):
    checks.append({"name": name, "pass": bool(ok)})

v = read("db_validate.json")
check("all_live_centres", v["checks"] == 6469)
check("all_node_oracle_no_errors", not v["errors"])
check("role_aware_combinations", len(v["relation_combinations"]) == 22)
check("no_live_edges_with_retired_endpoint", not v["facts"]["live_edges_with_retired_endpoint"])

r = read("db_retired_center.json")["requests"]
check("retired_centre_name_and_id", all(x["status"] == 200 and x["response"].get("not_found") for x in r[:2]))
check("retired_neighbour_excluded", all(it["id"] != "CHEMBL3353410" for g in r[2]["response"]["groups"] for it in g["items"]))

f = read("db_fixtures.json")
check("retired_trial_center_count_zero", f["retired_trial"][0]["response"]["center"]["trials"] == 0)
check("retired_trial_neighbour_count_zero", f["retired_trial"][1]["response"]["groups"][0]["items"][0]["trials"] == 0)
check("malformed_props_12_calls", len([r for x in f["malformed"] for r in x["requests"]]) == 12 and all(r["status"] == 200 for x in f["malformed"] for r in x["requests"]))
check("restored_calls", all(x["after_restore"]["status"] == 200 for x in f["malformed"]))
check("1001_drug_chunking", f["chunking"]["returned"] == f["chunking"]["total"] == 1001 and f["chunking"]["trials_histogram"] == {"1": 1001} and f["chunking"]["weight_histogram"] == {"1": 1001})

s = read("db_missing_sponsor_count.json")["HEAD"]
check("missing_sponsor_unknown_not_zero", all(r["status"] == 200 and r["matched_edge_items"] and all(m["item"]["evidence_trials"] is None and m["item"]["weight"] == 0 for m in r["matched_edge_items"]) for case in s[1:] for r in case["requests"]))
check("original_sponsor_count_retained", all(m["item"]["evidence_trials"] == 1 for r in s[0]["requests"] for m in r["matched_edge_items"]))

score = read("db_score_fixture.json")["cases"]
check("bool_scores_unknown", all(r["status"] == 200 and r["body"]["groups"][0]["items"][0]["score"] is None for case in score[:2] for r in case["HEAD"]))
check("score_precision", all(r["body"]["groups"][0]["items"][0]["score"] == 0.8883707400322897 for r in score[2]["HEAD"]))
role = read("db_role_fallback.json")["cases"]
check("all_role_props_http_200", len(role) == 8 and all(r["status"] == 200 for case in role for r in case["repair_HEAD"]))
nums = read("db_numeric_fixture.json")["cases"]
check("infinity_failure_closed", all(r["status"] == 400 and "error" in r["body"] for case in nums if "Infinity" in case["stored_json_numeric_literal"] for r in case["requests"]))
check("finite_numeric_controls_http_200", all(r["status"] == 200 for case in nums if "Infinity" not in case["stored_json_numeric_literal"] for r in case["requests"]))
snapshot = read("db_snapshot_facts.json")
check("current_props_and_urls", not snapshot["bad_props"] and not snapshot["non_registry_https_urls"])
result = {"checks": checks, "passed": sum(x["pass"] for x in checks), "total": len(checks)}
(OUT / "db_assertions.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
print(json.dumps(result, indent=2))
assert all(x["pass"] for x in checks)
