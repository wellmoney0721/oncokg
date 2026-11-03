"""Assemble a compact payload for the dashboard.

Everything here is read back out of the artefacts the pipeline produced; nothing
is recomputed by hand. If a number on the dashboard is wrong, it is wrong in the
pipeline too, which is the point.
"""
from __future__ import annotations

import json
import sqlite3
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import config as C
import normalize as N
import query as Q

OUT = C.WEB / "data.json"


def main() -> None:
    resolved = json.loads((C.PROCESSED / "resolved.json").read_text(encoding="utf-8"))
    quality = json.loads((C.REPORTS / "quality_report.json").read_text(encoding="utf-8"))
    graph_stats = json.loads((C.REPORTS / "graph_stats.json").read_text(encoding="utf-8"))
    evals = {
        "dev": json.loads((C.REPORTS / "evaluation_dev.json").read_text(encoding="utf-8")),
        "test": json.loads((C.REPORTS / "evaluation_frozen_test.json").read_text(encoding="utf-8")),
        "postfix": json.loads((C.REPORTS / "evaluation_postfix.json").read_text(encoding="utf-8")),
    }

    drugs = resolved["dictionary"]["drugs"]
    conn = sqlite3.connect(C.PROCESSED / "oncokg.sqlite")
    conn.row_factory = sqlite3.Row

    tiers = Counter()
    for t in resolved["trials"]:
        for iv in t["interventions"]:
            for c in iv["components"]:
                tiers[c["tier"]] += 1

    top_drugs = [
        {"name": r["label"], "trials": r["n"]}
        for r in conn.execute("""
            SELECT n.label AS label, COUNT(*) AS n FROM edge e
            JOIN node n ON n.id = e.dst
            WHERE e.rel='EVALUATES' AND e.retired_at IS NULL
            GROUP BY e.dst ORDER BY n DESC LIMIT 15""")
    ]
    top_companies = [
        {"name": r["label"], "drugs": r["n"], "sponsor_class": r["cls"]}
        for r in conn.execute("""
            SELECT n.label AS label, COUNT(DISTINCT e.dst) AS n,
                   json_extract(n.props,'$.class') AS cls
            FROM edge e JOIN node n ON n.id = e.src
            WHERE e.rel='SPONSORS_TRIAL_OF' AND e.retired_at IS NULL
            GROUP BY e.src ORDER BY n DESC LIMIT 15""")
    ]

    # an ego network small enough to draw, centred on the disease's best-known target
    ego_nodes, ego_edges = {}, []
    centre = conn.execute(
        "SELECT id,label FROM node WHERE type='Target' AND label='EGFR'").fetchone()
    if centre:
        ego_nodes[centre["id"]] = {"id": centre["id"], "label": centre["label"],
                                   "type": "Target"}
        for r in conn.execute("""
            SELECT e.src AS did, n.label AS label, n.props AS props,
                   (SELECT COUNT(*) FROM edge x WHERE x.rel='EVALUATES'
                     AND x.dst=e.src AND x.retired_at IS NULL) AS trials
            FROM edge e JOIN node n ON n.id = e.src
            WHERE e.rel='ACTS_ON' AND e.dst=? AND e.retired_at IS NULL
            ORDER BY trials DESC LIMIT 12""", (centre["id"],)):
            ego_nodes[r["did"]] = {"id": r["did"], "label": r["label"], "type": "Drug",
                                   "trials": r["trials"]}
            ego_edges.append({"src": r["did"], "dst": centre["id"], "rel": "ACTS_ON"})
            for c in conn.execute("""
                SELECT e.src AS cid, n.label AS label,
                       json_extract(e.props,'$.evidence_trials') AS n
                FROM edge e JOIN node n ON n.id = e.src
                WHERE e.rel='SPONSORS_TRIAL_OF' AND e.dst=? AND e.retired_at IS NULL
                ORDER BY n DESC LIMIT 2""", (r["did"],)):
                ego_nodes.setdefault(c["cid"], {"id": c["cid"], "label": c["label"],
                                                "type": "Company"})
                ego_edges.append({"src": c["cid"], "dst": r["did"], "rel": "SPONSORS_TRIAL_OF",
                                  "weight": c["n"]})

    by_type: dict[str, list] = defaultdict(list)
    for f in quality["findings"]:
        by_type[f["type"]].append(f)
    qc_examples = {k: v[:4] for k, v in by_type.items()}

    # the headline dictionary defect, spelled out
    contamination = [f for f in quality["findings"]
                     if f["type"] == "cross_drug_synonym"][:6]

    kg = Q.OncoKG()
    demo_questions = [
        "Which companies are developing osimertinib?",
        "What trials evaluate Tagrisso?",
        "Which drugs act on ALK?",
        "What does osimertinib target?",
        "What is AstraZeneca running in NSCLC?",
        "What is the capital of France?",
    ]
    demos = [kg.answer(q).to_dict() for q in demo_questions]
    for d in demos:
        d["evidence"] = d["evidence"][:8]

    payload = {
        "meta": {
            "disease": resolved["disease"]["name"],
            "built_from": resolved["_built_from"],
            "sources": ["Open Targets Platform", "ChEMBL (via Open Targets)",
                        "ClinicalTrials.gov API v2"],
        },
        "headline": {
            "trials": len(resolved["trials"]),
            "molecules": len(drugs),
            "aliases": sum(len(d["aliases"]) for d in drugs.values()),
            "targets": len(resolved["targets"]),
            "companies": graph_stats["nodes_by_type"].get("Company", 0),
            "nodes": graph_stats["nodes"],
            "edges": graph_stats["edges"],
            "qc_findings": quality["totals"]["findings"],
            "accepted_precision": evals["postfix"]["accepted_precision"],
            "frozen_test_precision": evals["test"]["accepted_precision"],
            "coverage": evals["postfix"]["coverage"],
        },
        "tiers": [{"tier": k, "count": v} for k, v in tiers.most_common()],
        # sorted, not list(set): set iteration order varies per process, which
        # made every rebuild dirty the working tree and contradicted the
        # reproducibility the rest of the pipeline is built around
        "accepting_tiers": sorted(N.ACCEPTED_TIERS),
        "evaluation": {
            k: {"per_tier": v["per_tier"],
                "accepted_precision": v["accepted_precision"],
                "coverage": v["coverage"],
                "sample_size": v["gold_sample_size"],
                "limitations": v["limitations"]}
            for k, v in evals.items()
        },
        "quality": {
            "totals": quality["totals"],
            "examples": qc_examples,
            "contamination": contamination,
        },
        "graph": {"stats": graph_stats,
                  "ego": {"nodes": list(ego_nodes.values()), "edges": ego_edges}},
        "top_drugs": top_drugs,
        "top_companies": top_companies,
        "demos": demos,
    }
    OUT.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    size = OUT.stat().st_size / 1024
    print(f"-> {OUT.relative_to(C.ROOT)}  ({size:.0f} KB)")


if __name__ == "__main__":
    main()
