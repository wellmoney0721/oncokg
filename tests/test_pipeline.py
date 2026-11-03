"""Tests for the behaviours that would quietly corrupt the graph if they broke.

These are not coverage tests. Each one pins a failure mode that was actually
observed in the data and would be invisible downstream: a placebo arm turning
into an exposure, a development code binding to its neighbour, a combination
losing a drug, a contaminated synonym pulling two molecules together.

Run with:  python -m pytest tests -q
"""
from __future__ import annotations

import json
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

import config as C          # noqa: E402
import graph as G           # noqa: E402
import normalize as N       # noqa: E402
import textrules as T       # noqa: E402


# --------------------------------------------------------------------------- #
# fixtures
# --------------------------------------------------------------------------- #
def tiny_dictionary():
    rows = [
        {"maxClinicalStage": "PHASE_3", "drug": {
            "id": "CHEMBL1", "name": "OSIMERTINIB", "drugType": "Small molecule",
            "maximumClinicalStage": "APPROVAL",
            "synonyms": [{"label": "AZD9291", "source": "ChEMBL"}],
            "tradeNames": [{"label": "Tagrisso", "source": "ChEMBL"}],
            "mechanismsOfAction": None, "parentMolecule": None}},
        {"maxClinicalStage": "PHASE_3", "drug": {
            "id": "CHEMBL2", "name": "DOCETAXEL", "drugType": "Small molecule",
            "maximumClinicalStage": "APPROVAL",
            "synonyms": [{"label": "Taxotere", "source": "ChEMBL"}],
            "tradeNames": [], "mechanismsOfAction": None, "parentMolecule": None}},
        {"maxClinicalStage": "PHASE_3", "drug": {
            "id": "CHEMBL3", "name": "CARBOPLATIN", "drugType": "Small molecule",
            "maximumClinicalStage": "APPROVAL",
            "synonyms": [], "tradeNames": [], "mechanismsOfAction": None,
            "parentMolecule": None}},
        # deliberately contaminated: ATEZOLIZUMAB listing another drug's name,
        # a class term and a placebo string as synonyms -- all three occur in
        # the real ChEMBL records this project ingests.
        {"maxClinicalStage": "PHASE_3", "drug": {
            "id": "CHEMBL4", "name": "ATEZOLIZUMAB", "drugType": "Antibody",
            "maximumClinicalStage": "APPROVAL",
            "synonyms": [{"label": "durvalumab", "source": "ChEMBL"},
                         {"label": "anti-PD-L1", "source": "ChEMBL"},
                         {"label": "durvalumab placebo", "source": "ChEMBL"}],
            "tradeNames": [], "mechanismsOfAction": None, "parentMolecule": None}},
        {"maxClinicalStage": "PHASE_3", "drug": {
            "id": "CHEMBL5", "name": "DURVALUMAB", "drugType": "Antibody",
            "maximumClinicalStage": "APPROVAL",
            "synonyms": [], "tradeNames": [], "mechanismsOfAction": None,
            "parentMolecule": None}},
    ]
    dic = N.build_drug_dictionary(rows)
    dic.pop("build_findings")
    N.curate_dictionary(dic)
    return dic, list(dic["index"].keys())


def resolve(text):
    dic, keys = tiny_dictionary()
    return N.resolve_drug_string(text, dic, keys)


def drug_ids(result):
    return {c["drug_id"] for c in result["components"]
            if c["tier"] in N.ACCEPTED_TIERS}


def tiers(result):
    return {c["tier"] for c in result["components"]}


# --------------------------------------------------------------------------- #
# placebo handling
# --------------------------------------------------------------------------- #
def test_placebo_reference_arm_creates_no_exposure():
    r = resolve("Placebo for Osimertinib")
    assert drug_ids(r) == set()
    assert N.TIER_BLOCKED_PLACEBO in tiers(r)


def test_placebo_adjacent_to_its_reference_drug_creates_no_exposure():
    assert drug_ids(resolve("placebo Osimertinib")) == set()


def test_placebo_combined_with_a_real_drug_keeps_that_drug():
    r = resolve("placebo plus docetaxel")
    assert drug_ids(r) == {"CHEMBL2"}
    assert N.TIER_BLOCKED_PLACEBO in tiers(r)


def test_placebo_to_match_does_not_leak_the_matched_drug():
    assert drug_ids(resolve("Placebo to Match AZD9291, Osimertinib")) == set()


# --------------------------------------------------------------------------- #
# development codes and isotopes
# --------------------------------------------------------------------------- #
def test_development_code_is_never_fuzzy_matched():
    # one digit apart from nothing in the dictionary: must stay unresolved
    r = resolve("AZD9292")
    assert drug_ids(r) == set()
    assert any("dev_code_no_fuzzy" in (c.get("rules") or [])
               for c in r["components"])


def test_development_code_lot_suffix_still_resolves():
    assert drug_ids(resolve("AZD9291-01")) == {"CHEMBL1"}


def test_isotope_label_is_not_a_drug():
    assert T.is_isotope_label("18F")
    assert T.is_isotope_label("[68Ga]")
    assert not T.is_isotope_label("AZD9291")


def test_radiotracer_moiety_is_not_matched():
    assert drug_ids(resolve("18F-Docetaxel tracer")) == set()


# --------------------------------------------------------------------------- #
# combinations and segmentation
# --------------------------------------------------------------------------- #
def test_explicit_combination_keeps_every_component():
    assert drug_ids(resolve("Osimertinib + Docetaxel")) == {"CHEMBL1", "CHEMBL2"}


def test_unseparated_combination_keeps_every_component():
    assert drug_ids(resolve("Docetaxel Carboplatin")) == {"CHEMBL2", "CHEMBL3"}


def test_hyphenated_combination_is_split_but_codes_are_not():
    assert drug_ids(resolve("Docetaxel-Carboplatin")) == {"CHEMBL2", "CHEMBL3"}
    assert drug_ids(resolve("AZD9291")) == {"CHEMBL1"}


def test_dose_and_formulation_noise_is_removed():
    assert drug_ids(resolve("Docetaxel 75 mg/m2 IV infusion")) == {"CHEMBL2"}


def test_trade_name_resolves_to_the_molecule():
    assert drug_ids(resolve("Tagrisso")) == {"CHEMBL1"}


def test_class_term_is_refused():
    r = resolve("Platinum Based Chemotherapy")
    assert drug_ids(r) == set()
    assert N.TIER_BLOCKED_CLASS in tiers(r)


# --------------------------------------------------------------------------- #
# dictionary curation
# --------------------------------------------------------------------------- #
def test_cross_drug_synonym_is_bound_to_the_preferred_name():
    # 'durvalumab' is listed as a synonym of ATEZOLIZUMAB in the source, and is
    # also DURVALUMAB's own preferred name. The preferred name must win.
    assert drug_ids(resolve("durvalumab")) == {"CHEMBL5"}


def test_class_term_synonym_is_removed_from_the_index():
    assert drug_ids(resolve("anti-PD-L1")) == set()


def test_placebo_string_never_enters_the_dictionary():
    dic, _ = tiny_dictionary()
    assert T.canonical_key("durvalumab placebo") not in dic["index"]


def test_curation_reports_what_it_changed():
    rows_dic = N.build_drug_dictionary([
        {"maxClinicalStage": None, "drug": {
            "id": "A", "name": "ALPHA", "drugType": "x", "maximumClinicalStage": None,
            "synonyms": [{"label": "beta", "source": "s"}], "tradeNames": [],
            "mechanismsOfAction": None, "parentMolecule": None}},
        {"maxClinicalStage": None, "drug": {
            "id": "B", "name": "BETA", "drugType": "x", "maximumClinicalStage": None,
            "synonyms": [], "tradeNames": [], "mechanismsOfAction": None,
            "parentMolecule": None}},
    ])
    rows_dic.pop("build_findings")
    findings = N.curate_dictionary(rows_dic)
    kinds = {f["type"] for f in findings}
    assert "cross_drug_synonym" in kinds


# --------------------------------------------------------------------------- #
# company normalisation
# --------------------------------------------------------------------------- #
def test_legal_suffixes_do_not_split_one_company():
    a = N.normalize_company("Celgene Corporation")
    b = N.normalize_company("Celgene")
    assert a["key"] == b["key"]


def test_curated_parent_is_applied():
    assert N.normalize_company("Genentech, Inc.")["parent"] == "Roche"


# --------------------------------------------------------------------------- #
# graph provenance and change history
# --------------------------------------------------------------------------- #
def _mini_resolved(trial_drug="CHEMBL1", include_trial=True):
    dic, _ = tiny_dictionary()
    trials = []
    if include_trial:
        trials.append({
            "nct_id": "NCT00000001", "title": "demo", "status": "COMPLETED",
            "why_stopped": None, "start_date": "2020-01-01", "phases": ["PHASE3"],
            "enrollment": 100,
            "lead_sponsor": {"raw": "Acme Pharma Inc.", "key": "acme",
                             "display": "Acme", "parent": None, "rules": [],
                             "class": "INDUSTRY"},
            "collaborators": [],
            "conditions": [{"raw": "NSCLC", "disease_id": "MONDO_0005233",
                            "tier": N.TIER_EXACT, "rules": [], "score": 100.0}],
            "interventions": [{
                "raw": "Osimertinib", "intervention_type": "DRUG",
                "other_names": [],
                "components": [{"component": "Osimertinib", "tier": N.TIER_EXACT,
                                "drug_id": trial_drug, "score": None,
                                "rules": [], "matched_alias": "OSIMERTINIB",
                                "candidates": None}]}],
        })
    return {
        "_built_from": {"disease": "t", "drugs": "t", "targets": "t", "trials": "t"},
        "disease": {"disease_id": "MONDO_0005233", "name": "NSCLC", "index": {}},
        "dictionary": dic, "dictionary_findings": [], "duplicate_findings": [],
        "ambiguous_keys": {}, "targets": [], "trials": trials, "companies": {},
    }


def test_every_evaluates_edge_carries_its_source_record():
    import sqlite3
    with tempfile.TemporaryDirectory() as tmp:
        db = Path(tmp) / "g.sqlite"
        G.build(_mini_resolved(), db_path=db, build_id="b1")
        conn = sqlite3.connect(db)
        rows = conn.execute(
            "SELECT source, source_record, source_fetched_at, confidence"
            " FROM edge WHERE rel='EVALUATES'").fetchall()
        conn.close()
    assert rows and all(r[0] and r[1] and r[2] and r[3] for r in rows)


def test_a_disappearing_edge_is_retired_not_deleted():
    import sqlite3
    with tempfile.TemporaryDirectory() as tmp:
        db = Path(tmp) / "g.sqlite"
        G.build(_mini_resolved(), db_path=db, build_id="b1")
        stats = G.build(_mini_resolved(include_trial=False), db_path=db, build_id="b2")
        conn = sqlite3.connect(db)
        retired = conn.execute(
            "SELECT COUNT(*) FROM edge WHERE rel='EVALUATES'"
            " AND retired_at IS NOT NULL").fetchone()[0]
        logged = conn.execute(
            "SELECT COUNT(*) FROM edge_change WHERE change_type='retired'").fetchone()[0]
        conn.close()
    assert stats["retired"] > 0 and retired == 1 and logged > 0


def test_rebuilding_unchanged_sources_records_no_change():
    with tempfile.TemporaryDirectory() as tmp:
        db = Path(tmp) / "g.sqlite"
        G.build(_mini_resolved(), db_path=db, build_id="b1")
        stats = G.build(_mini_resolved(), db_path=db, build_id="b2")
    assert (stats["added"], stats["changed"], stats["retired"]) == (0, 0, 0)


def test_a_changed_resolution_is_written_to_the_change_log():
    import sqlite3
    with tempfile.TemporaryDirectory() as tmp:
        db = Path(tmp) / "g.sqlite"
        G.build(_mini_resolved(trial_drug="CHEMBL1"), db_path=db, build_id="b1")
        G.build(_mini_resolved(trial_drug="CHEMBL2"), db_path=db, build_id="b2")
        conn = sqlite3.connect(db)
        changes = conn.execute(
            "SELECT change_type, COUNT(*) FROM edge_change WHERE build_id='b2'"
            " GROUP BY change_type").fetchall()
        conn.close()
    kinds = dict(changes)
    assert kinds.get("added", 0) >= 1 and kinds.get("retired", 0) >= 1
