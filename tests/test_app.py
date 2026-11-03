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


# Codex review m6: the linker and the intervention resolver must agree before linking
def test_glued_separators_edge_punctuation_and_parenthetical_qualifiers_refuse():
    import app
    e = app.Engine()
    for t in ("bevacizumab - awwb/osimertinib", "bevacizumab - awwb|osimertinib"):
        r = e.explore(t)
        assert r["center"]["id"] == "CHEMBL3353410", t
        assert all(x.get("id") != "CHEMBL1201583" for x in r["also"]), t
    for t in ("bevacizumab-awwb。", "bevacizumab-awwb-", "-bevacizumab-awwb",
              "doxorubicin (nanoparticle and liposomal formulation)",
              "bevacizumab (investigational and biosimilar)"):
        assert e.explore(t).get("refused"), t
    for q in ("Which trials evaluate bevacizumab - awwb/osimertinib?",
              "Which trials evaluate bevacizumab-awwb。?",
              "Which trials evaluate doxorubicin (nanoparticle and liposomal formulation)?"):
        a = e.kg.answer(q, use_llm=False)
        assert all("CHEMBL1201583" not in ev.edge_id and "CHEMBL53463" not in ev.edge_id
                   for ev in a.evidence), q


def test_a_whole_input_that_is_one_stored_name_is_read_whole():
    import app
    e = app.Engine()
    assert e.explore("CP-358,774")["center"]["id"] == "CHEMBL553"
    assert e.explore("Rapamycin, 42-o-(2-hydroxyethyl)-")["center"]["id"] == "CHEMBL1908360"
    assert e.explore("Erlotinib/hydrochloride")["center"]["id"] == "CHEMBL553"


# Codex review m7: one normalised spelling for every check
def test_wrappers_unicode_hyphens_punctuation_and_spaced_isotopes_refuse():
    import app
    e = app.Engine()
    for t in ("bevacizumab-awwb?", "bevacizumab-awwb!", '"bevacizumab-awwb"', "(bevacizumab-awwb)",
              "[bevacizumab-awwb]", "bevacizumab‑awwb", "bio‑similar bevacizumab",
              "89Zr trastuzumab", "[89Zr] trastuzumab"):
        assert e.explore(t).get("refused"), t
    for q in ("Which trials evaluate (bevacizumab-awwb)?", "Which trials evaluate 89Zr trastuzumab?",
              "Which trials evaluate bio‑similar bevacizumab?"):
        assert not e.kg.answer(q, use_llm=False).evidence, q


def test_only_an_exact_stored_name_is_read_whole():
    import app
    e = app.Engine()
    assert e.explore("Erlotinib, hydrochloride")["center"]["id"] == "CHEMBL553"
    assert e.explore("is a").get("not_found")
    assert e.explore("(E/Z)-AFATINIB")["center"]["id"] == "CHEMBL1173655"
    assert e.explore("RO 09-1978/000")["center"]["id"] == "CHEMBL1773"


def test_repeated_list_pieces_are_resolved_once():
    import time
    import query
    kg = query.OncoKG()
    t0 = time.time()
    kg.link_entities(";".join(["x"] * 2000))
    assert time.time() - t0 < 1.0


# Codex review m8
def test_spaced_isotopes_inner_wrappers_and_every_dash_refuse():
    import unicodedata
    import app
    e = app.Engine()
    for t in ("[89 Zr] trastuzumab", "[89\tZr] trastuzumab", "[89 Zr] trastuzumab",
              "bevacizumab-(awwb)", "bevacizumab-[awwb]"):
        assert e.explore(t).get("refused"), t
    for c in (chr(i) for i in range(0x110000) if unicodedata.category(chr(i)) == "Pd"):
        assert e.explore("bevacizumab" + c + "awwb").get("refused"), hex(ord(c))
    assert not e.kg.answer("Which trials evaluate [89 Zr] trastuzumab?", use_llm=False).evidence
    assert e.explore("bevacizumab-(awwb), osimertinib")["center"]["id"] == "CHEMBL3353410"


def test_lone_names_qualifier_boundaries_and_cache_rollover():
    import app
    e = app.Engine()
    for name, did in (("566C", "CHEMBL1450"), ("9-ac", "CHEMBL274070"), ("5ac", "CHEMBL1489"),
                      ("5.BETA.,20-EPOXY-1,2.ALPHA.,4,7.BETA.", "CHEMBL428647")):
        assert e.explore(name)["center"]["id"] == did, name
    for t in ("biosimilar, and osimertinib", "biosimilar; and osimertinib", "biosimilar and, osimertinib"):
        assert e.explore(t)["center"]["id"] == "CHEMBL3353410", t
    e.kg._resolve_cache = {f"k{i}": [] for i in range(4096)}
    assert e.explore("osimertinib")["center"]["id"] == "CHEMBL3353410"



# Codex review m9: refusal on the same letters-and-digits form the name is looked up by
def test_underscores_accents_spaced_suffixes_and_punctuated_isotopes_refuse():
    import app
    e = app.Engine()
    for t in ("bevacizumab_awwb", "bevacizumab__awwb", "bevácizumab-awwb",
              "bevácizumab-awwb", "[89.Zr] trastuzumab", "89:Zr trastuzumab",
              "bevacizumab awwb", "bevacizumab (awwb)", "trastuzumab 89Zr"):
        assert e.explore(t).get("refused"), t
    for q in ("Which trials evaluate bevacizumab_awwb?", "Which trials evaluate [89.Zr] trastuzumab?",
              "Which trials evaluate bevacizumab awwb?"):
        assert not e.kg.answer(q, use_llm=False).evidence, q
    r = e.explore("osimertinib with [89Zr] trastuzumab")
    assert r["center"]["id"] == "CHEMBL3353410"
    assert all(x.get("id") != "CHEMBL1201585" for x in r["also"])
    assert e.explore("bevacizumab_awwb, osimertinib")["center"]["id"] == "CHEMBL3353410"
    assert e.explore("Theophylline in dextrose 5% in plastic container")["center"]["id"] == "CHEMBL1355736"
    assert e.explore("cemiplimab-rwlc")["center"]["label"] == "CEMIPLIMAB"


# Codex review m10
def test_isotopes_inside_beside_or_instead_of_a_name_and_respelt_qualifiers_refuse():
    import app
    e = app.Engine()
    for t in ("A33 124i", "A33 124 i", "A33 [124i]", "A33 124-I", "A33-124i",
              "18F fluorothymidine", "18F nonexistingdrug", "[18F] fluorothymidine",
              "trastuzumab 89 - Zr", "trastuzumab [89 - Zr]", "trastuzumab 89_Zr",
              "generic-version of bevacizumab", "albumin - bound paclitaxel",
              "generic_version of bevacizumab", "follow-on-biologic bevacizumab"):
        assert e.explore(t).get("refused"), t
    for q in ("Which trials evaluate 18F fluorothymidine?", "Which trials evaluate trastuzumab 89 - Zr?",
              "Which trials evaluate generic-version of bevacizumab?"):
        assert not e.kg.answer(q, use_llm=False).evidence, q
    for name, did in (("18f", "CHEMBL2030434"), ("9-ac", "CHEMBL274070"), ("ADAKITUG", "CHEMBL5314551")):
        assert e.explore(name)["center"]["id"] == did, name
    assert e.explore("trastuzumab 89 - Zr, osimertinib")["center"]["id"] == "CHEMBL3353410"


# Codex review m11: suffixes and isotopes spelt in pieces are glued back as the key glues them
def test_split_isotopes_and_spelt_out_suffixes_refuse():
    import app
    e = app.Engine()
    for t in ("[89Z.r] trastuzumab", "89Z_r trastuzumab", "trastuzumab [89Z.r]",
              "bevacizumab a - w w b", "bevacizumab - a - w - w - b", "bevacizumab a_w_w_b"):
        assert e.explore(t).get("refused"), t
    for t in ("[89Z.r] trastuzumab, osimertinib", "bevacizumab a - w w b, osimertinib"):
        assert e.explore(t)["center"]["id"] == "CHEMBL3353410", t
    for q in ("Which trials evaluate [89Z.r] trastuzumab?", "Which trials evaluate bevacizumab a - w w b?"):
        assert not e.kg.answer(q, use_llm=False).evidence, q
    for t, did in (("osimertinib 80 mg", "CHEMBL3353410"), ("paclitaxel 2 cycles", "CHEMBL428647"),
                   ("cisplatin 75 mg/m2 day 1", "CHEMBL11359")):
        assert e.explore(t)["center"]["id"] == did, t


# Codex review m12: an isotope split by punctuation inside a stored alias, with a chelator between
def test_a_split_isotope_inside_a_stored_tracer_alias_refuses():
    import app
    e = app.Engine()
    for t in ("[89Z.r]-DFO-daratumumab", "89Z_r-dfo-daratumumab"):
        assert e.explore(t).get("refused"), t
    assert e.explore("[89Z.r]-DFO-daratumumab, osimertinib")["center"]["id"] == "CHEMBL3353410"
    assert not e.kg.answer("Which trials evaluate [89Z.r]-DFO-daratumumab?", use_llm=False).evidence
    assert e.explore("daratumumab")["center"]["id"] == "CHEMBL1743007"


# Codex review m13: an isotope fused to a chelator, inside the name or beside it
def test_an_isotope_fused_to_a_chelator_refuses():
    import app
    e = app.Engine()
    for t in ("89ZrDFO-daratumumab", "89zrdfo-daratumumab", "89ZrDFOdaratumumab",
              "daratumumab DFO89Zr", "89ZrDFO daratumumab"):
        assert e.explore(t).get("refused"), t
    assert not e.kg.answer("Which trials evaluate 89ZrDFO-daratumumab?", use_llm=False).evidence
    for t, did in (("13-cis retinoic acid", "CHEMBL38"), ("BKM-120NX", "CHEMBL2017974"),
                   ("paclitaxel 2 cycles", "CHEMBL428647")):
        r = e.explore(t)
        assert r.get("center", {}).get("id") == did, (t, r.get("center"))


# Codex review m14
def test_upper_case_one_letter_isotopes_and_trailing_markers_refuse():
    import app
    e = app.Engine()
    for t in ("3HVINBLASTINE", "3H-vinblastine", "89Zrpanitumumab-PET-CT", "A33124I"):
        assert e.explore(t).get("refused"), t
    for t, did in (("vinblastine", "CHEMBL159"), ("panitumumab", "CHEMBL1201827"),
                   ("NSC-118218H", None), ("DX-8951F", None), ("13-cis retinoic acid", "CHEMBL38")):
        r = e.explore(t)
        assert r.get("center"), t
        if did:
            assert r["center"]["id"] == did, t
