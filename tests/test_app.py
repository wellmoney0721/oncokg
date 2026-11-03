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


# Codex review m2b
def test_a_refused_product_does_not_swallow_a_separately_named_drug():
    import app
    e = app.Engine()
    for t in ("osimertinib and generic version of bevacizumab",
              "generic version of bevacizumab and osimertinib",
              "[89Zr] trastuzumab and osimertinib",
              "osimertinib, generic version of bevacizumab",
              "osimertinib and oral azacitidine"):
        r = e.explore(t)
        assert r["center"]["id"] == "CHEMBL3353410", t
        assert all(x.get("id") != "CHEMBL1201583" for x in r["also"]), t
    a = e.kg.answer("Which trials evaluate osimertinib and generic version of bevacizumab?",
                    use_llm=False)
    assert a.evidence and all("CHEMBL1201583" not in ev.edge_id for ev in a.evidence)


def test_an_unrecorded_sponsor_count_stays_unknown():
    import app
    import sqlite3
    e = app.Engine()
    mem = sqlite3.connect(":memory:", check_same_thread=False)
    e.kg.conn.backup(mem)
    mem.row_factory = sqlite3.Row
    eid = "ORG:alaunos|SPONSORS_TRIAL_OF|CHEMBL1201438|"
    for bad in ("null", "[]", "{broken", '{"evidence_trials": true}'):
        mem.execute("UPDATE edge SET props=? WHERE id=?", (bad, eid))
        e.kg.conn = mem
        r = e.explore("CHEMBL1201438")
        items = [i for g in r["groups"] for i in g["items"] if i["edge_id"] == eid]
        assert items and items[0]["evidence_trials"] is None, bad


# Codex review m3: a refusal is bound to the drug it qualifies
def test_a_qualified_product_is_refused_with_its_drug_wherever_it_sits():
    import app
    e = app.Engine()
    for t in ("paclitaxel with albumin bound nanoparticles",
              "What is the generic version of bevacizumab?",
              "generic version with bevacizumab"):
        assert e.explore(t).get("refused"), t
    a = e.kg.answer("What trials evaluate paclitaxel with albumin bound nanoparticles?",
                    use_llm=False)
    assert not a.evidence
    for t in ("osimertinib, liposomal doxorubicin", "osimertinib, biosimilar bevacizumab",
              "osimertinib; generic version of bevacizumab"):
        assert e.explore(t)["center"]["id"] == "CHEMBL3353410", t


# Codex review m4: inside one list item the qualified drug is not guessed; all its drugs
# are refused, however far the qualifier sits and however long the drug's name
def test_a_list_item_with_a_qualifier_refuses_every_drug_in_it():
    import app
    e = app.Engine()
    for t in ("osimertinib with generic version of bevacizumab",
              "osimertinib with [89Zr] trastuzumab",
              "generic version of Paclitaxel conjugate with poly-l-glutamic acid",
              "generic version of the monoclonal antibody bevacizumab",
              "biosimilar version of bevacizumab",
              "liposomal formulation of doxorubicin",
              "paclitaxel with albumin-bound nanoparticles",
              "liposomal formulation of doxorubicin and biosimilar version of bevacizumab"):
        assert e.explore(t).get("refused"), t
    for q in ("Which trials evaluate osimertinib with generic version of bevacizumab?",
              "Which trials evaluate generic version of the monoclonal antibody bevacizumab?",
              "Which trials evaluate biosimilar version of bevacizumab?"):
        a = e.kg.answer(q, use_llm=False)
        assert all("CHEMBL1201583" not in ev.edge_id for ev in a.evidence), q
    r = e.explore("EGFR biosimilar bevacizumab")
    assert r["center"]["id"] == "ENSG00000146648"


def test_words_of_a_longer_name_are_not_read_again():
    import app
    e = app.Engine()
    assert e.explore("erlotinib hydrochloride")["also"] == []
    r = e.explore("Paclitaxel conjugate with poly-l-glutamic acid")
    assert r["center"]["id"] == "CHEMBL2108628" and r["also"] == []


# Codex review m5
def test_glued_separators_and_split_descriptions_do_not_leak_the_originator():
    import app
    e = app.Engine()
    for t in ("bevacizumab-awwb/ osimertinib", "bevacizumab-awwb| osimertinib",
              "bevacizumab - awwb/ osimertinib"):
        r = e.explore(t)
        assert r["center"]["id"] == "CHEMBL3353410", t
        assert all(x.get("id") != "CHEMBL1201583" for x in r["also"]), t
    for t in ("liposomal and nanoparticle formulation of doxorubicin",
              "liposomal and sustained release doxorubicin"):
        assert e.explore(t).get("refused"), t
    a = e.kg.answer("Which trials evaluate liposomal and nanoparticle formulations of doxorubicin?",
                    use_llm=False)
    assert all("CHEMBL53463" not in ev.edge_id for ev in a.evidence)
    assert e.explore("Mvasi and bevacizumab")["center"]["id"] == "CHEMBL1201583"


def test_a_name_is_not_built_from_two_list_items():
    import app
    e = app.Engine()
    assert e.explore("biosimilar anastrozole, Arimidex")["center"]["id"] == "CHEMBL1399"
    assert e.explore("Erlotinib, hydrochloride biosimilar bevacizumab")["center"]["id"] == "CHEMBL553"


def test_the_refusal_scan_grows_linearly():
    import time
    import query
    kg = query.OncoKG()
    t0 = time.time()
    kg.link_entities(" ".join(["x"] * 500))
    assert time.time() - t0 < 1.0
