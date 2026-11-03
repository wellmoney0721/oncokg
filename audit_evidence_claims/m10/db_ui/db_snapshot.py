"""Read-only snapshot facts supporting the round-four data audit."""
from collections import Counter
import hashlib
import json
from pathlib import Path
import sqlite3

ROOT = Path(__file__).resolve().parents[3]
OUT = Path(__file__).resolve().parent
db = ROOT / "data/processed/oncokg.sqlite"
c = sqlite3.connect(f"file:{db.as_posix()}?mode=ro", uri=True)
c.row_factory = sqlite3.Row
out = {"db_sha256": hashlib.sha256(db.read_bytes()).hexdigest()}
out["node_types"] = dict(c.execute("SELECT type,count(*) FROM node WHERE retired_at IS NULL GROUP BY type"))
out["bad_props"] = []
urls = []
for table in ("node", "edge"):
    for row in c.execute(f"SELECT id,props FROM {table}"):
        try:
            obj = json.loads(row["props"])
            if not isinstance(obj, dict):
                out["bad_props"].append({"table": table, "id": row["id"], "kind": type(obj).__name__})
            elif table == "node" and obj.get("url"):
                urls.append({"id": row["id"], "url": obj["url"]})
        except (ValueError, TypeError):
            out["bad_props"].append({"table": table, "id": row["id"], "kind": "invalid JSON"})
out["url_count"] = len(urls)
out["non_registry_https_urls"] = [r for r in urls if not r["url"].startswith("https://clinicaltrials.gov/study/")]
out["association_score_types"] = [list(r) for r in c.execute("SELECT json_type(props,'$.association_score'),count(*) FROM edge WHERE rel='ASSOCIATED_WITH' AND retired_at IS NULL GROUP BY 1")]
out["sponsor_count_types"] = [list(r) for r in c.execute("SELECT json_type(props,'$.evidence_trials'),count(*) FROM edge WHERE rel='SPONSORS_TRIAL_OF' AND retired_at IS NULL GROUP BY 1")]
out["retired_evaluates_edges"] = c.execute("SELECT count(*) FROM edge WHERE rel='EVALUATES' AND retired_at IS NOT NULL").fetchone()[0]
out["investigator_sponsors_edges"] = c.execute("SELECT count(*) FROM edge e JOIN node n ON n.id=e.src WHERE e.rel='SPONSORS' AND e.retired_at IS NULL AND n.type='Investigator'").fetchone()[0]
c.close()
(OUT / "db_snapshot_facts.json").write_text(json.dumps(out, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps(out, ensure_ascii=False))
