"""Build the knowledge graph into SQLite, with provenance and change history.

Two properties matter more than the schema itself:

* **Every edge states where it came from.** Source, the exact record, the fetch
  timestamp, the resolution tier that produced it, and a confidence. An edge
  whose origin cannot be shown cannot be defended to the person relying on it.
* **Every change is kept.** Re-running against a newer snapshot does not
  overwrite history: edges that disappear are retired with a timestamp rather
  than deleted, and changed attributes are written to a change log. "When did
  this relationship appear, and on what evidence?" is answerable afterwards.

Only resolutions the pipeline accepts become edges. Ambiguous, blocked and
unresolved components are deliberately left out of the graph and stay visible in
the quality report instead -- the graph is the part that claims to be true.
"""
from __future__ import annotations

import json
import sqlite3
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import config as C
import normalize as N
import textrules as T

DB_PATH = C.PROCESSED / "oncokg.sqlite"

TIER_CONFIDENCE = {
    N.TIER_EXACT: 1.00,
    N.TIER_ALIAS: 0.98,
    N.TIER_CLEANED: 0.95,
    N.TIER_SALT: 0.95,
    N.TIER_PAREN: 0.90,
    N.TIER_CONTAINED: 0.88,
    N.TIER_FUZZY: 0.80,
}

SCHEMA = """
CREATE TABLE IF NOT EXISTS node (
  id TEXT PRIMARY KEY,
  type TEXT NOT NULL,
  label TEXT NOT NULL,
  props TEXT NOT NULL DEFAULT '{}',
  first_seen TEXT NOT NULL,
  last_seen TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS node_type ON node(type);
CREATE INDEX IF NOT EXISTS node_label ON node(label);

CREATE TABLE IF NOT EXISTS edge (
  id TEXT PRIMARY KEY,
  src TEXT NOT NULL REFERENCES node(id),
  dst TEXT NOT NULL REFERENCES node(id),
  rel TEXT NOT NULL,
  props TEXT NOT NULL DEFAULT '{}',
  confidence REAL NOT NULL,
  tier TEXT,
  source TEXT NOT NULL,
  source_record TEXT,
  source_fetched_at TEXT,
  first_seen TEXT NOT NULL,
  last_seen TEXT NOT NULL,
  retired_at TEXT
);
CREATE INDEX IF NOT EXISTS edge_src ON edge(src);
CREATE INDEX IF NOT EXISTS edge_dst ON edge(dst);
CREATE INDEX IF NOT EXISTS edge_rel ON edge(rel);
CREATE INDEX IF NOT EXISTS edge_live ON edge(retired_at);

CREATE TABLE IF NOT EXISTS edge_change (
  change_id INTEGER PRIMARY KEY AUTOINCREMENT,
  edge_id TEXT NOT NULL,
  change_type TEXT NOT NULL,          -- added | attribute_changed | retired | restored
  field TEXT,
  old_value TEXT,
  new_value TEXT,
  changed_at TEXT NOT NULL,
  build_id TEXT NOT NULL
);
CREATE INDEX IF NOT EXISTS change_edge ON edge_change(edge_id);
CREATE INDEX IF NOT EXISTS change_build ON edge_change(build_id);

CREATE TABLE IF NOT EXISTS build (
  build_id TEXT PRIMARY KEY,
  started_at TEXT NOT NULL,
  sources TEXT NOT NULL,
  node_count INTEGER,
  edge_count INTEGER,
  added INTEGER, changed INTEGER, retired INTEGER, restored INTEGER
);
"""


def now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class GraphWriter:
    def __init__(self, conn: sqlite3.Connection, build_id: str, ts: str):
        self.c = conn
        self.build_id = build_id
        self.ts = ts
        self.seen_edges: set[str] = set()
        self.stats = {"added": 0, "changed": 0, "retired": 0, "restored": 0}

    # -- nodes ------------------------------------------------------------- #
    def node(self, node_id: str, type_: str, label: str, props: dict | None = None):
        props_json = json.dumps(props or {}, ensure_ascii=False, sort_keys=True)
        row = self.c.execute("SELECT props FROM node WHERE id=?", (node_id,)).fetchone()
        if row is None:
            self.c.execute(
                "INSERT INTO node(id,type,label,props,first_seen,last_seen)"
                " VALUES(?,?,?,?,?,?)",
                (node_id, type_, label, props_json, self.ts, self.ts))
        else:
            self.c.execute(
                "UPDATE node SET label=?, props=?, last_seen=? WHERE id=?",
                (label, props_json, self.ts, node_id))
        return node_id

    # -- edges ------------------------------------------------------------- #
    def edge(self, src: str, dst: str, rel: str, *, source: str,
             source_record: str | None = None, fetched_at: str | None = None,
             confidence: float = 1.0, tier: str | None = None,
             props: dict | None = None):
        edge_id = f"{src}|{rel}|{dst}|{source_record or ''}"
        # the same edge can be asserted twice inside one build (two arms of a
        # trial naming the same drug). That is not a change over time, so it
        # must not reach the change log.
        duplicate_in_build = edge_id in self.seen_edges
        self.seen_edges.add(edge_id)
        props_json = json.dumps(props or {}, ensure_ascii=False, sort_keys=True)
        row = self.c.execute(
            "SELECT props, confidence, tier, retired_at FROM edge WHERE id=?",
            (edge_id,)).fetchone()

        if row is None:
            self.c.execute(
                "INSERT INTO edge(id,src,dst,rel,props,confidence,tier,source,"
                "source_record,source_fetched_at,first_seen,last_seen)"
                " VALUES(?,?,?,?,?,?,?,?,?,?,?,?)",
                (edge_id, src, dst, rel, props_json, confidence, tier, source,
                 source_record, fetched_at, self.ts, self.ts))
            self._log(edge_id, "added", None, None,
                      json.dumps({"rel": rel, "confidence": confidence, "tier": tier}))
            self.stats["added"] += 1
            return edge_id

        old_props, old_conf, old_tier, retired = row
        if retired:
            self.c.execute("UPDATE edge SET retired_at=NULL WHERE id=?", (edge_id,))
            self._log(edge_id, "restored", None, retired, None)
            self.stats["restored"] += 1
        if duplicate_in_build:
            return edge_id
        for field, old, new in (("props", old_props, props_json),
                                ("confidence", old_conf, confidence),
                                ("tier", old_tier, tier)):
            if old != new:
                self._log(edge_id, "attribute_changed", field, str(old), str(new))
                self.stats["changed"] += 1
        self.c.execute(
            "UPDATE edge SET props=?, confidence=?, tier=?, source_fetched_at=?,"
            " last_seen=? WHERE id=?",
            (props_json, confidence, tier, fetched_at, self.ts, edge_id))
        return edge_id

    def retire_unseen(self):
        rows = self.c.execute(
            "SELECT id FROM edge WHERE retired_at IS NULL").fetchall()
        for (edge_id,) in rows:
            if edge_id in self.seen_edges:
                continue
            self.c.execute("UPDATE edge SET retired_at=? WHERE id=?",
                           (self.ts, edge_id))
            self._log(edge_id, "retired", None, None, None)
            self.stats["retired"] += 1

    def _log(self, edge_id, change_type, field, old, new):
        self.c.execute(
            "INSERT INTO edge_change(edge_id,change_type,field,old_value,new_value,"
            "changed_at,build_id) VALUES(?,?,?,?,?,?,?)",
            (edge_id, change_type, field, old, new, self.ts, self.build_id))


def build(resolved: dict, db_path: Path = DB_PATH, build_id: str | None = None) -> dict:
    ts = now()
    build_id = build_id or f"build-{ts}"
    conn = sqlite3.connect(db_path)
    conn.executescript(SCHEMA)
    g = GraphWriter(conn, build_id, ts)

    src_meta = resolved["_built_from"]
    drugs = resolved["dictionary"]["drugs"]
    disease = resolved["disease"]

    disease_node = g.node(disease["disease_id"], "Disease", disease["name"],
                          {"source": "Open Targets / MONDO"})

    for t_info in resolved["targets"]:
        g.node(t_info["target_id"], "Target", t_info["symbol"],
               {"name": t_info["name"], "alias_count": len(t_info["aliases"])})
        g.edge(t_info["target_id"], disease_node, "ASSOCIATED_WITH",
               source="opentargets", source_record=disease["disease_id"],
               fetched_at=src_meta["targets"],
               confidence=round(float(t_info["association_score"]), 4),
               props={"association_score": t_info["association_score"],
                      "meaning": "Open Targets target-disease association score"})

    for did, d in drugs.items():
        g.node(did, "Drug", d["name"],
               {"drug_type": d["drug_type"],
                "max_phase_overall": d["max_phase_overall"],
                "max_phase_in_disease": d["max_phase_in_nsclc"],
                "alias_count": len(d["aliases"]),
                "mechanisms": d["mechanisms"][:3]})
        for moa in d["moa_targets"]:
            if moa["target_id"]:
                g.node(moa["target_id"], "Target", moa["symbol"] or moa["target_id"])
                g.edge(did, moa["target_id"], "ACTS_ON",
                       source="opentargets/chembl", source_record=did,
                       fetched_at=src_meta["drugs"], confidence=0.95,
                       props={"action_type": moa["action_type"]})

    for t in resolved["trials"]:
        nct = t["nct_id"]
        g.node(nct, "Trial", nct,
               {"title": t["title"], "status": t["status"], "phases": t["phases"],
                "start_date": t["start_date"], "enrollment": t["enrollment"],
                "url": f"https://clinicaltrials.gov/study/{nct}"})

        for role, entry in ([("lead_sponsor", t["lead_sponsor"])] +
                            [("collaborator", c) for c in t["collaborators"]]):
            if not entry:
                continue
            cid = f"ORG:{entry['key']}"
            # A trial whose lead sponsor is a named physician is common, and
            # ClinicalTrials.gov files those under class OTHER rather than
            # INDIV, so the class alone does not separate them. Typing them as
            # Company put 36 individual investigators in the company table and
            # let the graph assert that a named doctor sponsors trials of
            # nivolumab as though they were an organisation.
            node_type = ("Investigator"
                         if (entry.get("class") == "INDIV"
                             or N.looks_like_person(entry["raw"]))
                         else "Company")
            g.node(cid, node_type, entry["display"],
                   {"raw_names": [entry["raw"]], "class": entry.get("class"),
                    "parent": entry.get("parent")})
            if entry.get("parent"):
                pid = f"ORG:{T.canonical_key(entry['parent'])}"
                if pid != cid:
                    g.node(pid, "Company", entry["parent"], {"is_parent_group": True})
                    g.edge(pid, cid, "PARENT_OF", source="curated",
                           source_record="hand-curated corporate map",
                           fetched_at=ts, confidence=0.9,
                           props={"note": "hand-curated; no licensed ownership "
                                          "dataset was used"})
            g.edge(cid, nct, "SPONSORS", source="clinicaltrials.gov",
                   source_record=nct, fetched_at=src_meta["trials"],
                   confidence=1.0,
                   props={"role": role, "sponsor_class": entry.get("class"),
                          "normalisation_rules": entry.get("rules")})

        for cond in t["conditions"]:
            if cond["disease_id"]:
                g.edge(nct, cond["disease_id"], "STUDIES",
                       source="clinicaltrials.gov", source_record=nct,
                       fetched_at=src_meta["trials"],
                       confidence=1.0 if cond["tier"] in (N.TIER_EXACT, N.TIER_CLEANED) else 0.85,
                       tier=cond["tier"],
                       props={"stated_condition": cond["raw"],
                              "normalisation_rules": cond["rules"]})

        for iv in t["interventions"]:
            for comp in iv["components"]:
                if comp["tier"] not in N.ACCEPTED_TIERS or not comp.get("drug_id"):
                    continue
                g.edge(nct, comp["drug_id"], "EVALUATES",
                       source="clinicaltrials.gov", source_record=nct,
                       fetched_at=src_meta["trials"],
                       confidence=TIER_CONFIDENCE.get(comp["tier"], 0.8),
                       tier=comp["tier"],
                       props={"stated_intervention": iv["raw"],
                              "matched_component": comp["component"],
                              "matched_alias": comp.get("matched_alias"),
                              "intervention_type": iv.get("intervention_type"),
                              "resolution_rules": comp.get("rules")})

    # Derived relation. An earlier version of this file called this edge
    # DEVELOPS, reasoning that a company that sponsors trials of a drug
    # develops it. Measuring the result showed the inference is unsound:
    # 60.6% of the edges had a non-industry lead sponsor, so the graph
    # asserted "National Cancer Institute develops paclitaxel", "Memorial
    # Sloan Kettering develops cisplatin", and — where a trial's lead sponsor
    # is an individual investigator — that a named physician develops
    # nivolumab. Sponsoring a trial is an observation; developing a drug is a
    # different claim, and nothing in these sources supports it.
    #
    # The edge is therefore named for what the evidence actually shows. The
    # sponsor class travels on the edge so a consumer can filter to industry
    # sponsors, and no confidence is manufactured from the trial count: a
    # sponsorship is either recorded or it is not.
    rows = conn.execute("""
        SELECT s.src AS org, e.dst AS drug, COUNT(DISTINCT e.src) AS n,
               GROUP_CONCAT(DISTINCT e.src) AS ncts,
               json_extract(s.props,'$.sponsor_class') AS cls
        FROM edge e
        JOIN edge s ON s.dst = e.src AND s.rel='SPONSORS' AND s.retired_at IS NULL
        WHERE e.rel='EVALUATES' AND e.retired_at IS NULL
          AND json_extract(s.props,'$.role')='lead_sponsor'
        GROUP BY s.src, e.dst
    """).fetchall()
    for org, drug, n, ncts, cls in rows:
        evidence = (ncts or "").split(",")[:10]
        g.edge(org, drug, "SPONSORS_TRIAL_OF", source="derived",
               source_record=None, fetched_at=ts, confidence=1.0,
               props={"derived": True, "evidence_trials": n,
                      "evidence_sample": evidence,
                      "sponsor_class": cls,
                      "is_industry_sponsor": cls == "INDUSTRY",
                      "rule": "lead sponsor of trials evaluating this drug",
                      "not_a_development_claim":
                          "sponsorship is not evidence of originating or "
                          "developing the molecule; academic, cooperative-group "
                          "and government sponsors run trials of other "
                          "organisations' drugs"})

    g.retire_unseen()

    node_count = conn.execute("SELECT COUNT(*) FROM node").fetchone()[0]
    edge_count = conn.execute(
        "SELECT COUNT(*) FROM edge WHERE retired_at IS NULL").fetchone()[0]
    conn.execute(
        "INSERT OR REPLACE INTO build(build_id,started_at,sources,node_count,"
        "edge_count,added,changed,retired,restored) VALUES(?,?,?,?,?,?,?,?,?)",
        (build_id, ts, json.dumps(src_meta), node_count, edge_count,
         g.stats["added"], g.stats["changed"], g.stats["retired"], g.stats["restored"]))
    conn.commit()

    stats = {"build_id": build_id, "nodes": node_count, "edges": edge_count, **g.stats}
    by_type = dict(conn.execute("SELECT type, COUNT(*) FROM node GROUP BY type").fetchall())
    by_rel = dict(conn.execute(
        "SELECT rel, COUNT(*) FROM edge WHERE retired_at IS NULL GROUP BY rel").fetchall())
    stats["nodes_by_type"] = by_type
    stats["edges_by_rel"] = by_rel
    conn.close()
    return stats


def main() -> None:
    resolved = json.loads((C.PROCESSED / "resolved.json").read_text(encoding="utf-8"))
    stats = build(resolved)
    print(f"graph -> {DB_PATH.relative_to(C.ROOT)}")
    print(f"  nodes {stats['nodes']}   edges {stats['edges']}")
    print(f"  added {stats['added']}  changed {stats['changed']}  "
          f"retired {stats['retired']}  restored {stats['restored']}")
    print("  nodes by type:", stats["nodes_by_type"])
    print("  edges by relation:", stats["edges_by_rel"])
    (C.REPORTS / "graph_stats.json").write_text(
        json.dumps(stats, indent=2, ensure_ascii=False), encoding="utf-8")


if __name__ == "__main__":
    main()
