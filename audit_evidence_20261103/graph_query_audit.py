"""Read-only source audit; mutations are restricted to temporary databases."""
import copy
import io
import json
import os
from pathlib import Path
import runpy
import sqlite3
import sys
import tempfile
from contextlib import redirect_stdout, redirect_stderr

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
import config as C
import graph as G
import normalize as N
import query as Q

out = {"api_key_present": bool(os.environ.get("ANTHROPIC_API_KEY"))}
kg = Q.OncoKG()
questions = [
    "Which companies are developing osimertinib?",
    "Is pembrolizumab safe in patients with autoimmune disease?",
    "What is the capital of France?",
    "What is AstraZeneca running in NSCLC?",
    "What trials evaluate Tagrisso?",
]
out["queries"] = [kg.answer(q, use_llm=False).to_dict() for q in questions]
sqls = [
    "SELECT rel,count(*),sum(source_record IS NULL),sum(source_fetched_at IS NULL),sum(tier IS NULL) FROM edge WHERE retired_at IS NULL GROUP BY rel",
    "SELECT n.label,count(*) FROM edge e JOIN node n ON n.id=e.dst WHERE e.rel='SPONSORS_TRIAL_OF' AND n.label='OSIMERTINIB' GROUP BY n.label",
    "SELECT id,type,label,props FROM node WHERE lower(label) LIKE '%xiuning%'",
    "SELECT e.id,n.label,m.label,e.props FROM edge e JOIN node n ON n.id=e.src JOIN node m ON m.id=e.dst WHERE e.rel='PARENT_OF' AND (lower(n.label) LIKE '%merck%' OR lower(m.label) LIKE '%merck%' OR lower(m.label) LIKE '%beigene%' OR lower(n.label) LIKE '%beone%')",
]
out["sql"] = [{"query": sql, "rows": [list(r) for r in kg.conn.execute(sql)]} for sql in sqls]
entities = kg.link_entities("pembrolizumab")
ev = kg.retrieve("drug_profile", entities)
claims = [
    "pembrolizumab is safe in patients with autoimmune disease.",
    "xyzabumab cures cancer.",
    "pembrolizumab cures cancer in forty-seven percent of patients.",
    "pembrolizumab has a 47% response rate.",
    "pembrolizumab causes cancer.",
]
out["groundedness"] = [{"claim": s, "result": Q.OncoKG.check_groundedness(s, ev, entities)} for s in claims]
evnum = [Q.Evidence(statement="Response was 47.5 percent in 1,234 patients", edge_id="x", relation="TEST", source="test", source_record="NCT12345678", fetched_at=None, confidence=1)]
out["numeric_checks"] = [{"claim": s, "result": Q.OncoKG.check_groundedness(s, evnum, [])} for s in ["response was 47.5 percent in 1,234 patients.", "response was 47 percent."]]
raw = json.loads((ROOT / "data/processed/resolved.json").read_text(encoding="utf-8"))
trial = next(t for t in raw["trials"] if t["lead_sponsor"] and any(c["tier"] in N.ACCEPTED_TIERS and c.get("drug_id") for iv in t["interventions"] for c in iv["components"]))
mini = {"_built_from": raw["_built_from"], "dictionary": {"drugs": raw["dictionary"]["drugs"]}, "disease": raw["disease"], "targets": [], "trials": [trial]}
out["retirement"] = []
with tempfile.TemporaryDirectory(prefix="oncokg_graph_audit_") as td:
    db = Path(td) / "test.sqlite"
    for i in range(3):
        if i:
            mini["trials"] = []
        stats = G.build(mini, db, build_id=f"audit{i}")
        conn = sqlite3.connect(db)
        out["retirement"].append({"build": i, "stats": stats, "live_edges": conn.execute("SELECT rel,count(*) FROM edge WHERE retired_at IS NULL GROUP BY rel").fetchall(), "trial_nodes": conn.execute("SELECT id,type FROM node WHERE type='Trial'").fetchall()})
        conn.close()
conn = sqlite3.connect(":memory:")
conn.executescript(G.SCHEMA)
writer = G.GraphWriter(conn, "audit", "time")
writer.node("ORG:test", "Company", "John Smith")
writer.node("ORG:test", "Investigator", "John Smith")
out["node_type_update"] = conn.execute("SELECT id,type,label FROM node").fetchall()
out["company_probes"] = [{"raw": s, "person": N.looks_like_person(s), "normalized": N.normalize_company(s)} for s in ["Dr. Xiuning Le", "Xiuning Le", "John Smith, MD", "Alliance For Clinical Trials In Oncology", "Spanish Lung Cancer Group", "Hellenic Oncology Research Group", "Merck", "Merck & Co., Inc.", "MSD", "Schering AG", "BeiGene"]]
dashboard = json.loads((ROOT / "web/data.json").read_text(encoding="utf-8"))
out["dashboard_top_companies"] = dashboard["top_companies"]
out["investigator_primary_source"] = "https://faculty.mdanderson.org/profiles/xiuning_le.html"
# Exercise the real CLI entry point, redirecting only its report write to temp.
with tempfile.TemporaryDirectory(prefix="oncokg_query_cli_audit_") as td:
    previous_root, previous_reports, previous_argv = C.ROOT, C.REPORTS, sys.argv
    C.ROOT = Path(td)
    C.REPORTS = Path(td)
    sys.argv = ["src/query.py", *questions[:3]]
    stdout, stderr = io.StringIO(), io.StringIO()
    try:
        with redirect_stdout(stdout), redirect_stderr(stderr):
            runpy.run_path(str(ROOT / "src/query.py"), run_name="__main__")
        out["cli"] = {"exit_code": 0, "stdout": stdout.getvalue(), "stderr": stderr.getvalue()}
    finally:
        C.ROOT, C.REPORTS, sys.argv = previous_root, previous_reports, previous_argv
destination = Path(__file__).with_suffix(".json")
destination.write_text(json.dumps(out, indent=2, ensure_ascii=False), encoding="utf-8")
print(destination)
