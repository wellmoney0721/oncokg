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


def _page(e, t):
    """What the page shows for t. The map draws a whole name itself. Longer input is not
    drawn (refused, or "enter one name"); the question boxes then read it with the linker,
    and that reading is returned in the map's shape so a test can check it."""
    r = e.explore(t)
    if "center" in r:
        return {**r, "also": []}
    assert r.get("refused") or r.get("not_one_name") or r.get("alias_only"), (t, r)
    hits = [x for x in e.kg.link_entities(t) if x.get("id") and x["type"] != "Refused"]
    assert hits, t
    return {"center": hits[0], "also": hits[1:], "linker": True}


def _linked(e, t):
    """The one entity the question linker reads in t, with nothing refused."""
    ents = e.kg.link_entities(t)
    assert not any(x["type"] == "Refused" for x in ents), (t, ents)
    hits = [x for x in ents if x.get("id")]
    assert len(hits) == 1, (t, ents)
    return hits[0]["id"]


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
    r = _page(e, "osimertinib")
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
    e = app.Engine()
    # "Roche" is also a folic acid trade name; the map reads drugs by preferred name only
    assert e.explore("Roche")["center"]["id"] == "ORG:roche"
    r = e.explore("ABT-510")                     # two records under one name: the reader picks
    assert "center" not in r and len(r["choose"]) == 2


# Codex review m2b
def test_a_refused_product_does_not_swallow_a_separately_named_drug():
    import app
    e = app.Engine()
    for t in ("osimertinib and generic version of bevacizumab",
              "generic version of bevacizumab and osimertinib",
              "[89Zr] trastuzumab and osimertinib",
              "osimertinib, generic version of bevacizumab",
              "osimertinib and oral azacitidine"):
        r = _page(e, t)
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
        assert _page(e, t)["center"]["id"] == "CHEMBL3353410", t


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
    r = _page(e, "EGFR biosimilar bevacizumab")
    assert r["center"]["id"] == "ENSG00000146648"


def test_words_of_a_longer_name_are_not_read_again():
    import app
    e = app.Engine()
    assert _page(e, "erlotinib hydrochloride")["also"] == []
    r = _page(e, "Paclitaxel conjugate with poly-l-glutamic acid")
    assert r["center"]["id"] == "CHEMBL2108628" and r["also"] == []


# Codex review m5
def test_glued_separators_and_split_descriptions_do_not_leak_the_originator():
    import app
    e = app.Engine()
    for t in ("bevacizumab-awwb/ osimertinib", "bevacizumab-awwb| osimertinib",
              "bevacizumab - awwb/ osimertinib"):
        r = _page(e, t)
        assert r["center"]["id"] == "CHEMBL3353410", t
        assert all(x.get("id") != "CHEMBL1201583" for x in r["also"]), t
    for t in ("liposomal and nanoparticle formulation of doxorubicin",
              "liposomal and sustained release doxorubicin"):
        assert e.explore(t).get("refused"), t
    a = e.kg.answer("Which trials evaluate liposomal and nanoparticle formulations of doxorubicin?",
                    use_llm=False)
    assert all("CHEMBL53463" not in ev.edge_id for ev in a.evidence)
    assert _page(e, "Mvasi and bevacizumab")["center"]["id"] == "CHEMBL1201583"


def test_a_name_is_not_built_from_two_list_items():
    import app
    e = app.Engine()
    assert _page(e, "biosimilar anastrozole, Arimidex")["center"]["id"] == "CHEMBL1399"
    assert _page(e, "Erlotinib, hydrochloride biosimilar bevacizumab")["center"]["id"] == "CHEMBL553"


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
        r = _page(e, t)
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
    # the question linker reads the stored alias whole; the map reads a drug only by its
    # preferred name, which for the salt spelling is the salt's own record
    for t, linked, drawn in (("CP-358,774", "CHEMBL553", None),
                             ("Rapamycin, 42-o-(2-hydroxyethyl)-", "CHEMBL1908360", None),
                             ("Erlotinib/hydrochloride", "CHEMBL553", "CHEMBL1079742")):
        assert _linked(e, t) == linked, t
        r = e.explore(t)
        assert r.get("center", {}).get("id") == drawn and (drawn or r.get("alias_only")), t


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
    assert _linked(e, "Erlotinib, hydrochloride") == "CHEMBL553"
    assert e.explore("Erlotinib, hydrochloride")["center"]["id"] == "CHEMBL1079742"
    assert "center" not in e.explore("is a") and not e.kg.link_entities("is a")
    assert _page(e, "(E/Z)-AFATINIB")["center"]["id"] == "CHEMBL1173655"
    assert _page(e, "RO 09-1978/000")["center"]["id"] == "CHEMBL1773"


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
    assert _page(e, "bevacizumab-(awwb), osimertinib")["center"]["id"] == "CHEMBL3353410"


def test_lone_names_qualifier_boundaries_and_cache_rollover():
    import app
    e = app.Engine()
    for name, did in (("566C", "CHEMBL1450"), ("9-ac", "CHEMBL274070"), ("5ac", "CHEMBL1489"),
                      ("5.BETA.,20-EPOXY-1,2.ALPHA.,4,7.BETA.", "CHEMBL428647")):
        assert _page(e, name)["center"]["id"] == did, name
    for t in ("biosimilar, and osimertinib", "biosimilar; and osimertinib", "biosimilar and, osimertinib"):
        assert _page(e, t)["center"]["id"] == "CHEMBL3353410", t
    e.kg._resolve_cache = {f"k{i}": [] for i in range(4096)}
    assert _page(e, "osimertinib")["center"]["id"] == "CHEMBL3353410"



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
    # the isotope shares the list item with osimertinib: both refused (fail closed, round 15)
    assert e.explore("osimertinib with [89Zr] trastuzumab").get("refused")
    assert _page(e, "osimertinib, [89Zr] trastuzumab")["center"]["id"] == "CHEMBL3353410"
    assert _page(e, "bevacizumab_awwb, osimertinib")["center"]["id"] == "CHEMBL3353410"
    assert _page(e, "Theophylline in dextrose 5% in plastic container")["center"]["id"] == "CHEMBL1355736"
    assert _page(e, "cemiplimab-rwlc")["center"]["label"] == "CEMIPLIMAB"


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
        assert _page(e, name)["center"]["id"] == did, name
    assert _page(e, "trastuzumab 89 - Zr, osimertinib")["center"]["id"] == "CHEMBL3353410"


# Codex review m11: suffixes and isotopes spelt in pieces are glued back as the key glues them
def test_split_isotopes_and_spelt_out_suffixes_refuse():
    import app
    e = app.Engine()
    for t in ("[89Z.r] trastuzumab", "89Z_r trastuzumab", "trastuzumab [89Z.r]",
              "bevacizumab a - w w b", "bevacizumab - a - w - w - b", "bevacizumab a_w_w_b"):
        assert e.explore(t).get("refused"), t
    for t in ("[89Z.r] trastuzumab, osimertinib", "bevacizumab a - w w b, osimertinib"):
        assert _page(e, t)["center"]["id"] == "CHEMBL3353410", t
    for q in ("Which trials evaluate [89Z.r] trastuzumab?", "Which trials evaluate bevacizumab a - w w b?"):
        assert not e.kg.answer(q, use_llm=False).evidence, q
    for t, did in (("osimertinib 80 mg", "CHEMBL3353410"), ("paclitaxel 2 cycles", "CHEMBL428647"),
                   ("cisplatin 75 mg/m2 day 1", "CHEMBL11359")):
        assert _page(e, t)["center"]["id"] == did, t


# Codex review m12: an isotope split by punctuation inside a stored alias, with a chelator between
def test_a_split_isotope_inside_a_stored_tracer_alias_refuses():
    import app
    e = app.Engine()
    for t in ("[89Z.r]-DFO-daratumumab", "89Z_r-dfo-daratumumab"):
        assert e.explore(t).get("refused"), t
    assert _page(e, "[89Z.r]-DFO-daratumumab, osimertinib")["center"]["id"] == "CHEMBL3353410"
    assert not e.kg.answer("Which trials evaluate [89Z.r]-DFO-daratumumab?", use_llm=False).evidence
    assert _page(e, "daratumumab")["center"]["id"] == "CHEMBL1743007"


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
        r = _page(e, t)
        assert r.get("center", {}).get("id") == did, (t, r.get("center"))


# Codex review m14
def test_upper_case_one_letter_isotopes_and_trailing_markers_refuse():
    import app
    e = app.Engine()
    for t in ("3HVINBLASTINE", "3H-vinblastine", "89Zrpanitumumab-PET-CT", "A33124I"):
        assert e.explore(t).get("refused"), t
    for t, did in (("vinblastine", "CHEMBL159"), ("panitumumab", "CHEMBL1201827"),
                   ("NSC-118218H", None), ("DX-8951F", None), ("13-cis retinoic acid", "CHEMBL38")):
        r = _page(e, t)
        assert r.get("center"), t
        if did:
            assert r["center"]["id"] == did, t


# Codex review m15: a medical isotope anywhere in the item refuses an unlabelled drug
def test_a_medical_isotope_anywhere_in_the_item_refuses_an_unlabelled_drug():
    import app
    e = app.Engine()
    for t in ("89-ZrDFO trastuzumab", "3hvinblastine", "trastuzumab Ga68", "lu177 trastuzumab"):
        assert e.explore(t).get("refused"), t
    assert not e.kg.answer("Which trials evaluate 89-ZrDFO trastuzumab?", use_llm=False).evidence
    # a drug that is itself the labelled product, and text that only looks numeric
    for t, label in (("18-FDG", "FLUDEOXYGLUCOSE F 18"), ("ra-223", "RADIUM RA 223 DICHLORIDE"),
                     ("lu-177 dotatate", "LUTETIUM OXODOTREOTIDE LU-177"),
                     ("lorlatinib 13 NSCLC trials", "LORLATINIB"), ("paclitaxel 2 cycles", "PACLITAXEL")):
        assert _page(e, t)["center"]["label"] == label, t


# Codex review m16: an element-first one-letter isotope inside a word
def test_element_first_one_letter_isotopes_refuse():
    import time
    import app
    e = app.Engine()
    for t in ("I-124-labelled trastuzumab", "trastuzumab labelled with I-124", "F18 trastuzumab",
              "C14 paclitaxel"):
        r = e.explore(t)
        assert "center" not in r or r["center"]["id"] not in ("CHEMBL1201585", "CHEMBL428647"), t
    assert not e.kg.answer("Which trials evaluate I-124-labelled trastuzumab?", use_llm=False).evidence
    for t in ("BKM-120NX", "AZD9291", "IL-2"):  # a synonym: read by the question linker only
        assert _linked(e, t), t
        assert e.explore(t).get("alias_only"), t
    t0 = time.time()
    e.kg.link_entities(" ".join(["osimertinib"] * 80))
    assert time.time() - t0 < 1.0


# Codex review m17: punctuation before a one-letter isotope keeps its boundary
def test_a_punctuated_element_first_isotope_refuses():
    import app
    e = app.Engine()
    for t in ("trastuzumab labelled-I-124", "trastuzumab labelled_I_124", "paclitaxel tagged-C-14"):
        r = e.explore(t)
        assert r.get("refused") or r.get("not_found"), t
    assert not e.kg.answer("Which trials evaluate trastuzumab labelled-I-124?", use_llm=False).evidence


# Codex review m18: element names written out, and words that say "radiolabelled"
def test_written_out_isotopes_and_labelling_words_refuse():
    import app
    e = app.Engine()
    for t in ("trastuzumab radiolabelled with iodine-124", "iodine-124 trastuzumab",
              "trastuzumab labeled with zirconium 89", "tritiated vinblastine",
              "trastuzumab radiotracer"):
        assert e.explore(t).get("refused"), t
    assert not e.kg.answer("Which trials evaluate trastuzumab radiolabelled with iodine-124?",
                           use_llm=False).evidence
    for t, label in (("fluorine-18 fluorodeoxyglucose", "FLUDEOXYGLUCOSE F 18"),
                     ("lead compound osimertinib", "OSIMERTINIB")):
        assert _page(e, t)["center"]["label"] == label, t


# Codex review m19
def test_split_labelling_words_and_metastable_mass_first_refuse():
    import app
    e = app.Engine()
    for t in ("radio-labelled trastuzumab", "radio labeled trastuzumab",
              "trastuzumab labelled with 99m-technetium", "trastuzumab radio-iodinated"):
        assert e.explore(t).get("refused"), t
    for t in ("radiotherapy plus cisplatin", "cisplatin and radiation"):
        assert _page(e, t)["center"]["label"] == "CISPLATIN", t


# Codex review m20
def test_therapy_nuclides_and_label_spellings_refuse():
    import app
    e = app.Engine()
    for t in ("trastuzumab labelled with terbium-161", "[161Tb] trastuzumab", "Tb-161 trastuzumab",
              "161Tb Herceptin", "227Th trastuzumab", "trastuzumab labelled with bismuth-213",
              "trastuzumab radioactively labelled", "radioconjugated trastuzumab",
              "trastuzumab labelled with iodine124", "99mtechnetium trastuzumab",
              "radio-immuno-conjugate trastuzumab"):
        assert e.explore(t).get("refused"), t
    for t in ("non-radio-labelled trastuzumab", "unlabelled trastuzumab", "trastuzumab 600 mg sc"):
        assert _page(e, t)["center"]["label"] == "TRASTUZUMAB", t
    assert _page(e, "osimertinib 51 criteria")["center"]["label"] == "OSIMERTINIB"


# Codex review m21
def test_bounded_symbol_isotopes_and_radioisotope_word_refuse():
    import app
    e = app.Engine()
    for t in ("trastuzumab labelled with Ce-134", "[134Ce] trastuzumab", "134Ce-DOTA trastuzumab",
              "trastuzumab labelled with Mn-52", "radioisotope-labelled trastuzumab",
              "trastuzumab labelled with a radioisotope", "radio-isotope-labelled trastuzumab"):
        assert e.explore(t).get("refused"), t
    for t in ("75 several trastuzumab", "51 criteria trastuzumab", "trastuzumab CR 51"):
        assert _page(e, t)["center"]["label"] == "TRASTUZUMAB", t


# Codex review m22
def test_fused_mass_symbols_and_radio_words_refuse():
    import app
    e = app.Engine()
    for t in ("trastuzumab labelled with 52Mn", "134CeDOTA trastuzumab", "134CeIII-DOTA trastuzumab",
              "trastuzumab DOTA134Ce", "astatinated trastuzumab", "radioastatinated trastuzumab",
              "radio-fluorinated trastuzumab", "isotope-labelled trastuzumab",
              "trastuzumab non-labelled radiolabelled"):
        assert e.explore(t).get("refused"), t
    for t, label in (("non-labelled trastuzumab", "TRASTUZUMAB"),
                     ("non-radioastatinated trastuzumab", "TRASTUZUMAB"),
                     ("cisplatin radiochemotherapy", "CISPLATIN"),
                     ("osimertinib after radiofrequency ablation", "OSIMERTINIB")):
        assert _page(e, t)["center"]["label"] == label, t


# Codex review m23
def test_interior_symbol_isotopes_and_conjugates_refuse():
    import app
    e = app.Engine()
    for t in ("DOTACe134 trastuzumab", "trastuzumab DOTAMn52", "trastuzumab conjugated to IRDye800CW",
              "trastuzumab conjugated to DM1", "IRDye800CW-conjugated trastuzumab",
              "trastuzumab covalently linked to DM1"):
        assert e.explore(t).get("refused"), t
    for t, label in (("non-radio-astatinated trastuzumab", "TRASTUZUMAB"),
                     ("trastuzumab not radioactively labelled", "TRASTUZUMAB"),
                     ("trastuzumab deruxtecan antibody-drug conjugate", "TRASTUZUMAB DERUXTECAN"),
                     ("Paclitaxel conjugate with poly-l-glutamic acid", "PACLITAXEL POLIGLUMEX")):
        assert _page(e, t)["center"]["label"] == label, t


# Codex review m24
def test_plain_molecule_with_payload_letters_and_coupling_wording_refuse():
    import app
    e = app.Engine()
    for t in ("irinotecan conjugated to polyethylene glycol", "tasidotin conjugated to PEG",
              "trastuzumab coupled to IRDye800CW", "trastuzumab linked via a linker to IRDye800CW",
              "trastuzumab chemically attached to IRDye800CW"):
        assert e.explore(t).get("refused"), t
    for t, label in (("irinotecan", "IRINOTECAN"), ("etirinotecan pegol", "ETIRINOTECAN PEGOL"),
                     ("trastuzumab not covalently linked to DM1", "TRASTUZUMAB"),
                     ("non-radio-immuno-conjugated trastuzumab", "TRASTUZUMAB"),
                     ("osimertinib linked to resistance", "OSIMERTINIB")):
        assert _page(e, t)["center"]["label"] == label, t


# Codex review m25
def test_negation_stops_at_its_word_and_named_reagents_after_an_article_refuse():
    import app
    e = app.Engine()
    for t in ("trastuzumab not radiolabelled but conjugated to DM1",
              "non-radioactive trastuzumab conjugated to DM1", "trastuzumab linked to a DM1 payload",
              "irinotecan linked to polyethylene glycol"):
        assert e.explore(t).get("refused"), t
    for t, label in (("trastuzumab not covalently linked to DM1", "TRASTUZUMAB"),
                     ("trastuzumab not chemically attached to IRDye800CW", "TRASTUZUMAB"),
                     ("osimertinib linked to drug resistance", "OSIMERTINIB"),
                     ("osimertinib linked with poor prognosis", "OSIMERTINIB")):
        assert _page(e, t)["center"]["label"] == label, t


# Codex review m26
def test_not_only_affirms_and_linked_reads_the_whole_item():
    import app
    e = app.Engine()
    for t in ("trastuzumab is not only conjugated to DM1 but also purified",
              "trastuzumab linked to a derivative of the toxin DM1",
              "polyethylene glycol linked to irinotecan"):
        assert e.explore(t).get("refused"), t
    for t in ("osimertinib linked to longer PFS", "osimertinib linked to response in 2026",
              "osimertinib linked to resistance in EGFR"):
        assert _page(e, t)["center"]["label"] == "OSIMERTINIB", t
    assert _page(e, "trastuzumab not covalently linked to DM1")["center"]["label"] == "TRASTUZUMAB"


# Codex review m27 (partial: the run stopped at model capacity before its report)
def test_hyphenated_payload_codes_named_dyes_and_focus_words():
    import app
    e = app.Engine()
    for t in ("trastuzumab linked to SN-38", "SN-38 linked to trastuzumab", "trastuzumab linked to DM-1",
              "trastuzumab linked to Alexa Fluor 488",
              "trastuzumab not merely conjugated to DM1 but also purified"):
        assert e.explore(t).get("refused"), t
    assert _page(e, "trastuzumab not directly conjugated to DM1")["center"]["label"] == "TRASTUZUMAB"


# Codex review m28
def test_focus_words_in_label_guard_dye_codes_and_extra_modification_of_an_adc():
    import app
    e = app.Engine()
    for t in ("trastuzumab not only radiolabelled but also purified",
              "trastuzumab not simply tagged with biotin but also purified",
              "trastuzumab linked to Cy3", "trastuzumab linked to TAMRA",
              "trastuzumab emtansine linked to Alexa Fluor 488",
              "trastuzumab emtansine conjugated to polyethylene glycol"):
        assert e.explore(t).get("refused"), t
    for t, label in (("trastuzumab not radiolabelled", "TRASTUZUMAB"),
                     ("trastuzumab deruxtecan antibody-drug conjugate", "TRASTUZUMAB DERUXTECAN")):
        assert _page(e, t)["center"]["label"] == label, t


# Codex review m29 (partial: stopped at model capacity; attacks/assertions.json is the record)
def test_suffixed_dye_codes_and_any_further_partner_of_a_named_adc_refuse():
    import app
    e = app.Engine()
    for t in ("trastuzumab linked to ATTO 647N", "Cy3B linked to trastuzumab",
              "trastuzumab linked to CF488A", "trastuzumab linked to Pacific Blue",
              "trastuzumab emtansine conjugated to streptavidin",
              "trastuzumab deruxtecan conjugated to Cy3B"):
        assert e.explore(t).get("refused"), t
    assert (_page(e, "trastuzumab emtansine is an antibody drug conjugate")["center"]["label"]
            == "TRASTUZUMAB EMTANSINE")


# Codex review m30
def test_linked_fails_closed_and_modification_verbs_refuse():
    import app
    e = app.Engine()
    for t in ("trastuzumab linked to eFluor 450", "VioBlue linked to trastuzumab",
              "trastuzumab emtansine linked to eFluor 450", "biotinylated trastuzumab",
              "FITC-derivatized trastuzumab", "trastuzumab functionalized with Pacific Blue"):
        assert e.explore(t).get("refused"), t
    for t, label in (("trastuzumab not biotinylated", "TRASTUZUMAB"),
                     ("osimertinib linked to improved 3-year survival", "OSIMERTINIB"),
                     ("resistance linked to osimertinib", "OSIMERTINIB")):
        assert _page(e, t)["center"]["label"] == label, t
    q = e.kg.link_entities("Which trials evaluate trastuzumab emtansine antibody-drug conjugate?")
    assert [x["label"] for x in q if x["type"] == "Drug"] == ["TRASTUZUMAB EMTANSINE"]


# Codex review m31
def test_setting_phrase_before_partner_and_gene_relations_and_question_scaffold():
    import app
    e = app.Engine()
    for t in ("trastuzumab linked at lysine residues to eFluor 450",
              "trastuzumab emtansine conjugated in solution to eFluor 450",
              "trastuzumab deruxtecan functionalized in solution with eFluor 450"):
        assert e.explore(t).get("refused"), t
    for t in ("osimertinib linked to EGFR mutations", "osimertinib linked to TP53 mutations"):
        assert _page(e, t)["center"]["label"] == "OSIMERTINIB", t
    for q, label in (("Which trials evaluate resistance linked to osimertinib?", "OSIMERTINIB"),
                     ("Which trials evaluate antibody-drug conjugate trastuzumab emtansine?",
                      "TRASTUZUMAB EMTANSINE")):
        ents = e.kg.link_entities(q)
        assert [x["label"] for x in ents if x["type"] == "Drug"] == [label], q
        assert not any(x["type"] == "Refused" for x in ents), q


# Codex review m32 (prepared before the round): the map takes one whole name
def test_the_map_draws_only_a_whole_stored_name():
    import app
    e = app.Engine()
    for t in ("osimertinib", " Osimertinib? ", "OSIMERTINIB", "ＯＳＩＭＥＲＴＩＮＩＢ",
              "osimertinib​", "Osimertinib®", "nct00200395", "chembl553", "Merck & Co", "EGFR", "egfr"):
        assert e.explore(t).get("center"), t
    # a second name, a qualifier, a dose, a partner, a dye, a sentence: not drawn
    for t in ("osimertinib EGFR", "osimertinib 80 mg", "trastuzumab linked at lysine residues to eFluor 450",
              "trastuzumab conjugated to a new dye", "osimertinib linked to EGFR mutations",
              "Which trials evaluate osimertinib?", "the osimertinib", "osimertinib osimertinib",
              "osimertinib and bevacizumab", "trastu+zumab", "trastu$zumab", "trastuzumabß",
              "AstraZeneca +", "Pfi+zer", "Roche $"):
        r = e.explore(t)
        assert "center" not in r and (r.get("not_one_name") or r.get("not_found") or r.get("refused")), t
    # a symbol or non-Latin letter the dictionary key drops still counts as more than the name
    for t in ("trastuzumab ☢", "☢ trastuzumab", "interferon α", "Roche ☢",
              "trastu☢zumab", "trastuzumab-α", "interferon-γ", "trastuzumab٣",
              "trastuzumab😀"):
        assert "center" not in e.explore(t), t
    # a node's own label is a name too; a label shared with a drug alias asks to choose
    assert e.explore("Li Zhang Md")["center"]["type"] == "Investigator"
    assert e.explore("Armando Santoro Md")["center"]["type"] == "Investigator"
    # any refused part refuses the whole input, even beside a plain name
    for t in ("Mvasi", "osimertinib, Mvasi", "Mvasi and bevacizumab", "osimertinib, [89Zr] trastuzumab"):
        assert e.explore(t).get("refused"), t


def test_a_key_shared_by_several_drugs_is_not_decided_by_spelling():
    import app
    e = app.Engine()
    # medi4736 is filed under durvalumab (ChEMBL) and, by a registry synonym, atezolizumab;
    # 5-fluorouracil also under capecitabine; ak112 under envafolimab and ivonescimab. The
    # question linker reads none of them; the map reads no synonym at all
    right: dict = {}
    for t in ("medi4736", "MEDI-4736", "MEDI4736", "5-fluorouracil", "5 - fluorouracil", "ak112",
              "AK-112", "peginterferon alfa-2b", "peg-interferon alfa-2b", "crlx101", "PD-1 mAb",
              "dha-paclitaxel", "Dha paclitaxel"):
        r = e.explore(t)
        assert r.get("center", {}).get("id") == right.get(t), (t, r)
        ents = e.kg.link_entities(t)
        assert not [x for x in ents if x["type"] == "Drug"], (t, ents)
    # a drug's own preferred name still chooses it
    assert e.explore("NICOTINE")["center"]["id"] == "CHEMBL3"
    assert e.explore("(+/-)NICOTINE")["center"]["id"] == "CHEMBL440464"
    assert e.explore("fluorouracil")["center"]["label"] == "FLUOROURACIL"


def test_the_map_reads_stored_names_under_one_rule():
    import app
    e = app.Engine()
    # several live nodes under one name: the reader chooses, whatever the spelling
    for t, ids in (("ABT-510", {"CHEMBL386115", "CHEMBL262489"}), ("ABT 510", {"CHEMBL386115", "CHEMBL262489"}),
                   ("FLUDEOXYGLUCOSE F 18", {"CHEMBL2030434", "CHEMBL497613"}),
                   ("FLUDEOXYGLUCOSE-F18", {"CHEMBL2030434", "CHEMBL497613"})):
        r = e.explore(t)
        assert "center" not in r and {c["id"] for c in r["choose"]} == ids, (t, r)
    # a trademark sign is dropped before compatibility folding, never turned into "TM"
    for t in ("osimertinib\u2122", "Osimertinib\u00ae", "AstraZeneca\u2122"):
        assert e.explore(t).get("center"), t
    # MAGE-A3 is the target's name; the vaccine's synonym is not read
    for t in ("MAGE-A3", "MAGEA3"):
        assert e.explore(t)["center"]["id"] == "ENSG00000221867", t
    # a drug's trade names and synonyms are not read: they file combination products,
    # formulations, biosimilars and wrong substances under a molecule
    for t in ("bupivacaine hydrochloride", "irinotecan liposome", "13-cis retinoic acid", "CT-P13",
              "Zessly", "ABP 980", "MK-3475", "MEDI4736", "Tagrisso", "Keytruda", "Remicade", "Kadcyla",
              "Megace", "Tarceva", "Tarceva\u2122", "Actikerall", "Betnesol-n", "Maxitrol", "Cipro hc"):
        r = e.explore(t)
        assert "center" not in r and (r.get("alias_only") or r.get("refused")), (t, r)
    for t, did in (("infliximab", "CHEMBL1201581"), ("trastuzumab emtansine", "CHEMBL1743082"),
                   ("megestrol acetate", "CHEMBL1201139"), ("pembrolizumab", "CHEMBL3137343")):
        assert e.explore(t)["center"]["id"] == did, t
    # trade names of other products filed under a molecule are refused, however spelt,
    # here and in questions
    for t in ("Inflectra", "Remsima", "Herwenda", "Equidacent", "Zarzio", "Pelgraz", "Myocet",
              "Fyarro", "Megace es", "Jelmyto", "Locteron", "Tobradex", "Oraqix", "LEP-ETU",
              "Myocet\u2122", "My/o/cet", "My ocet", "Inf/lectra", "Megace/ES", "Fy/arro", "Equi/dacent"):
        assert e.explore(t).get("refused"), t
    for t in ("Inflectra", "Myocet", "Tobradex", "Megace es"):
        assert any(x["type"] == "Refused" for x in e.kg.link_entities(f"Which trials evaluate {t}?")), t
    # the preferred-name rule in a question needs the name as a word of its own
    assert not e.kg.link_entities("What trials evaluate (+/-)NICOTINE?")
    assert [x["id"] for x in e.kg.link_entities("What trials evaluate NICOTINE?")] == ["CHEMBL3"]
    # a company key matches only input with nothing the key would drop
    assert e.explore("Merck Co")["center"]["id"] == e.explore("Merck & Co")["center"]["id"]
    for t in ("Merck + Co", "Pfizer$", "AstraZeneca +"):
        assert "center" not in e.explore(t), t


# Codex review m34
def test_every_stored_spelling_is_checked_and_rotation_signs_count():
    import app
    e = app.Engine()
    # a refused spelling the lookup index dropped still refuses its whole family
    for t in ("Cabozantinib (s)-malate", "cabozantinibsmalate", "CABOZANTINIB S-MALATE",
              "Cabozantinib (s)-malate?", "Cabozantinib/(s)-malate", "Cabozantinib\u200b(s)-malate"):
        assert e.explore(t).get("refused"), t
    # an optical-rotation sign is part of the name
    for t in ("(+)-NICOTINE", "(+)NICOTINE", "(-)-nicotine"):
        assert "center" not in e.explore(t), t
    for t in ("(+/-)NICOTINE", "(\u00b1)-nicotine"):
        assert e.explore(t)["center"]["id"] == "CHEMBL440464", t
    # brackets around a shared-key name in a question are fine; a descriptor is not
    for q in ("What trials evaluate (NICOTINE)?", "What does (NICOTINE) target?", "What trials evaluate [NICOTINE]?"):
        assert [x["id"] for x in e.kg.link_entities(q)] == ["CHEMBL3"], q
    for q in ("What trials evaluate (+/-)NICOTINE?", "What trials evaluate NICOTINE(+)?"):
        assert not e.kg.link_entities(q), q


# Codex review m35
def test_rotation_signs_survive_invisible_characters_dash_styles_and_order():
    import app
    e = app.Engine()
    assert e.explore("ARTEMISININ")["center"]["id"] == "CHEMBL269671"
    for t in ("(-)-ARTEMISININ", "(-\u200b)-ARTEMISININ", "(-\ufeff)-ARTEMISININ", "(-\u2060)-ARTEMISININ",
              "(-\u0301)-ARTEMISININ", "(\u2212\u200b)-ARTEMISININ", "(\u2013)-ARTEMISININ", "(\u2010)-ARTEMISININ",
              "(\uff0d)-ARTEMISININ", "(\u207b)-ARTEMISININ", "[-]-ARTEMISININ", "(\u034f-)-ARTEMISININ",
              "(-\ufe0f)-ARTEMISININ", "(+)-ARTEMISININ"):
        assert "center" not in e.explore(t), t
    for t in ("(-+)-NICOTINE", "(+-)NICOTINE", "( + / - )NICOTINE", "(+/\u2013)NICOTINE"):
        assert e.explore(t)["center"]["id"] == "CHEMBL440464", t
    # a sign group beside a bracketed name in a question blocks the shared-key reading
    for q in ("What trials evaluate (+/-)(NICOTINE)?", "What does (+/-)[NICOTINE] target?",
              "What trials evaluate (NICOTINE)(+/-)?", "What trials evaluate [NICOTINE](+/-)?",
              "What trials evaluate (NICOTINE)(+)?", "What trials evaluate NICOTINE (+/-)?"):
        assert not e.kg.link_entities(q), q
    assert [x["id"] for x in e.kg.link_entities("What trials evaluate ( NICOTINE ) and osimertinib?")] == \
        ["CHEMBL3", "CHEMBL3353410"]
