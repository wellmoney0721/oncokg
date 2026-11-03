"""The try-it page calls the pipeline's own functions; these pin what it shows."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import config as C

if not (C.PROCESSED / "oncokg.sqlite").exists():
    pytest.skip("built graph missing - run src/run_all.py first", allow_module_level=True)

import app

ENGINE = app.Engine()


def tiers(text):
    return [c["tier"] for c in ENGINE.resolve(text)["components"]]


def test_resolve_matches_pipeline_rules():
    assert tiers("placebo plus docetaxel") == ["BLOCKED_PLACEBO", "EXACT"]
    assert tiers("Mvasi") == ["BLOCKED_DISTINCT_PRODUCT"]
    assert tiers("EGFR") == ["BLOCKED_TARGET_TERM"]


def test_salt_record_reports_parent_molecule():
    drug = ENGINE.resolve("Tarceva")["components"][0]["drug"]
    assert drug["parent"]["name"] == "ERLOTINIB"


def test_check_flags_invented_name_and_number_not_relation():
    bad = ENGINE.check("Which drugs act on ALK?", "Alectinib and zorbatinib act on ALK.")
    assert {u["value"].lower() for u in bad["checks"]["unsupported_claims"]} == {"zorbatinib"}
    num = ENGINE.check("What trials evaluate Tagrisso?", "It is in 4,812 trials.")
    assert not num["checks"]["grounded"]
    # a false statement built from true tokens is caught by the claim check
    rel = ENGINE.check("Which companies are developing osimertinib?",
                       "AstraZeneca has discontinued osimertinib.")
    assert rel["checks"]["grounded"] is False


def test_explore_draws_a_drug_and_refuses_a_biosimilar():
    import app
    e = app.Engine()
    r = e.explore("osimertinib")
    assert r["center"]["id"] == "CHEMBL3353410"
    rels = {(g["rel"], g["dir"]) for g in r["groups"]}
    assert ("ACTS_ON", "out") in rels and ("SPONSORS_TRIAL_OF", "in") in rels
    assert all(len(g["items"]) <= 30 for g in r["groups"])
    assert e.explore("Mvasi").get("refused")
    assert e.explore("no such thing zz").get("not_found")


# Codex review m1
def test_explore_refuses_products_and_tracers_spelt_across_tokens():
    import app
    e = app.Engine()
    for t in ("bevacizumab - awwb", "89Zr - trastuzumab", "[89Zr] trastuzumab", "bevacizumab-awwb"):
        r = e.explore(t)
        assert r.get("refused"), t


def test_explore_keeps_sponsor_role_and_investigator_type():
    import app
    e = app.Engine()
    r = e.explore("NCT00200395")
    roles = {(g["type"], g["role"]): [i["id"] for i in g["items"]]
             for g in r["groups"] if g["rel"] == "SPONSORS"}
    assert "ORG:genentech" in roles[("Company", "collaborator")]
    assert "ORG:genentech" not in roles.get(("Company", "lead_sponsor"), [])
    r = e.explore("NCT00754364")
    assert any(g["rel"] == "SPONSORS" and g["type"] == "Investigator" for g in r["groups"])


def test_explore_does_not_draw_a_retired_centre_by_name():
    import app
    import sqlite3
    e = app.Engine()
    mem = sqlite3.connect(":memory:", check_same_thread=False)
    e.kg.conn.backup(mem)
    mem.row_factory = sqlite3.Row
    mem.execute("UPDATE node SET retired_at='T' WHERE id='CHEMBL3353410'")
    e.kg.conn = mem
    assert e.explore("osimertinib").get("not_found")


def test_explore_shows_other_readings_of_an_ambiguous_name():
    import app
    r = app.Engine().explore("Roche")
    assert any(x.get("id") == "ORG:roche" for x in r["also"])
