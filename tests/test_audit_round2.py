"""Regression tests for the defects found by the second independent audit.

Each test reproduces one finding from codex_report.txt / CODEX_R2_VERDICT.md
against the real snapshot, so a repair that is quietly undone fails here.

Run with:  python -m pytest tests -q
"""
from __future__ import annotations

import csv
import sqlite3
import subprocess
import sys
import tempfile
from functools import lru_cache
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "src"))

import config as C          # noqa: E402
import graph as G           # noqa: E402
import normalize as N       # noqa: E402
import query as Q           # noqa: E402
import textrules as T       # noqa: E402


@lru_cache(maxsize=1)
def real_dictionary():
    rows, _, _ = N._load("drugs")
    dic = N.build_drug_dictionary(rows)
    dic.pop("build_findings")
    N.curate_dictionary(dic)
    return dic, list(dic["index"].keys())


def resolve(text: str) -> list[tuple]:
    dic, keys = real_dictionary()
    out = N.resolve_drug_string(text, dic, keys)
    return [(c["tier"], dic["drugs"].get(c.get("drug_id"), {}).get("name"))
            for c in out["components"]]


# -- corporate map ---------------------------------------------------------- #
def test_merck_and_co_is_not_a_merck_kgaa_subsidiary():
    assert N.normalize_company("Merck & Co., Inc.")["parent"] != "Merck KGaA"
    assert N.normalize_company("Merck Sharp & Dohme LLC")["parent"] == "Merck & Co"
    assert N.normalize_company("EMD Serono")["parent"] == "Merck KGaA"


def test_a_rename_is_one_node_not_a_parent_relation():
    old = N.normalize_company("BeiGene")
    new = N.normalize_company("BeOne Medicines")
    assert old["key"] == new["key"] == "beonemedicines"
    assert old["parent"] is None and new["parent"] is None


def test_schering_ag_is_not_merck():
    assert N.normalize_company("Schering AG")["parent"] != "Merck & Co"


# -- groundedness ----------------------------------------------------------- #
def _check(text: str) -> dict:
    ev = [Q.Evidence(statement="Osimertinib was evaluated in 47.5% of 1,234 trials",
                     edge_id="e", relation="EVALUATES", source="test",
                     source_record="NCT00000001", fetched_at=None, confidence=1.0)]
    return Q.OncoKG.check_groundedness(text, ev, [{"label": "OSIMERTINIB"}], True)


def test_groundedness_rejects_invented_lowercase_drug():
    assert _check("xyzabumab cures cancer.")["grounded"] is False


def test_groundedness_matches_decimals_whole():
    assert _check("Osimertinib was evaluated in 47.5% of trials.")["grounded"] is True
    assert _check("Osimertinib was evaluated in 47% of trials.")["grounded"] is False


def test_groundedness_refuses_figures_written_in_words():
    assert _check("Osimertinib was evaluated in forty-seven percent.")["grounded"] is False


def test_groundedness_is_not_applicable_to_template_answers():
    ev = []
    r = Q.OncoKG.check_groundedness("anything", ev, [], generated=False)
    assert r["applicable"] is False and r["grounded"] is None


# -- label corrections ------------------------------------------------------ #
def test_correction_check_fails_when_a_correction_is_pending():
    import apply_label_corrections as L
    with tempfile.TemporaryDirectory() as tmp:
        tmp = Path(tmp)
        for name in L.FILES.values():
            rows = list(csv.DictReader((C.REPORTS / name).open(encoding="utf-8")))
            for r in rows:
                if name == "gold_postfix.csv" and r["id"] == "8":
                    r["verdict"] = "correct"          # undo one correction
            with (tmp / name).open("w", encoding="utf-8", newline="") as fh:
                w = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
                w.writeheader()
                w.writerows(rows)
        code = ("import sys; sys.path.insert(0, r'%s'); import config as C, "
                "pathlib; C.REPORTS = pathlib.Path(r'%s'); "
                "import apply_label_corrections as L; sys.argv=['x','--check']; L.main()"
                % (ROOT / "src", tmp))
        proc = subprocess.run([sys.executable, "-c", code], capture_output=True, text=True)
        assert proc.returncode != 0
        assert "already in the labels" not in proc.stdout


# -- graph ------------------------------------------------------------------ #
def _resolved_two_trials(include_second: bool) -> dict:
    sponsor = {"raw": "Acme Pharma", "key": "acme", "display": "Acme Pharma",
               "parent": None, "rules": [], "class": "INDUSTRY"}
    trial = lambda nct: {
        "nct_id": nct, "title": nct, "status": "COMPLETED", "phases": ["PHASE2"],
        "start_date": None, "enrollment": 10, "lead_sponsor": sponsor,
        "collaborators": [], "conditions": [],
        "interventions": [{"raw": "docetaxel", "intervention_type": "DRUG",
                           "components": [{"component": "docetaxel",
                                           "tier": N.TIER_EXACT,
                                           "drug_id": "CHEMBL2", "rules": []}]}]}
    trials = [trial("NCT00000001")] + ([trial("NCT00000002")] if include_second else [])
    return {"_built_from": {"targets": "t", "drugs": "t", "trials": "t"},
            "dictionary": {"drugs": {"CHEMBL2": {
                "name": "DOCETAXEL", "drug_type": "Small molecule",
                "max_phase_overall": 4, "max_phase_in_nsclc": 4, "aliases": [],
                "mechanisms": [], "moa_targets": []}}},
            "disease": {"disease_id": "EFO_1", "name": "NSCLC"},
            "targets": [], "trials": trials}


def test_removed_trial_does_not_keep_its_derived_sponsorship():
    with tempfile.TemporaryDirectory() as tmp:
        db = Path(tmp) / "g.sqlite"
        G.build(_resolved_two_trials(True), db_path=db, build_id="b1")
        G.build(_resolved_two_trials(False), db_path=db, build_id="b2")
        conn = sqlite3.connect(db)
        props = conn.execute(
            "SELECT props FROM edge WHERE rel='SPONSORS_TRIAL_OF' "
            "AND retired_at IS NULL").fetchone()[0]
        assert '"evidence_trials": 1' in props
        live = {r[0] for r in conn.execute(
            "SELECT id FROM node WHERE type='Trial' AND retired_at IS NULL")}
        conn.close()
        assert live == {"NCT00000001"}


def test_query_reads_the_current_relation_name():
    src = (ROOT / "src" / "query.py").read_text(encoding="utf-8")
    assert "DEVELOPS'" not in src
    src = (ROOT / "src" / "make_dashboard_data.py").read_text(encoding="utf-8")
    assert "DEVELOPS'" not in src


# -- domain ----------------------------------------------------------------- #
def test_registry_synonym_of_another_ingredient_is_removed():
    assert resolve("tobramycin") == [(N.TIER_UNRESOLVED, None)]


def test_class_word_does_not_resolve_to_a_steroid():
    assert resolve("corticosteroid") == [(N.TIER_BLOCKED_CLASS, None)]


def test_biosimilar_brands_do_not_become_the_originator():
    for brand in ("Mvasi", "Alymsys", "Zirabev", "bevacizumab-awwb"):
        assert resolve(brand) == [(N.TIER_BLOCKED_DISTINCT_PRODUCT, None)], brand


def test_originator_with_fda_suffix_resolves():
    assert [name for _t, name in resolve("cemiplimab-rwlc")] == ["CEMIPLIMAB"]


def test_reformulation_stays_blocked_inside_a_combination():
    assert (N.TIER_BLOCKED_DISTINCT_PRODUCT, None) in resolve(
        "liposomal doxorubicin and cisplatin")
    assert (N.TIER_BLOCKED_DISTINCT_PRODUCT, None) in resolve(
        "Carboplatin and Paclitaxel (Abraxane)")


def test_ester_is_not_stripped_as_a_salt():
    assert ("PREDNISOLONE" not in
            {name for _t, name in resolve("prednisolone phosphate")})


def test_negated_drug_is_not_an_exposure():
    assert resolve("No pembrolizumab") == [(N.TIER_BLOCKED_NEGATED, None)]
    # a prefix is not a negation
    assert (N.TIER_CONTAINED, "PACLITAXEL") in resolve(
        "Non-platinum chemotherapy: paclitaxel or nab-paclitaxel")


def test_bracketed_code_belongs_to_its_own_component():
    tiers = resolve("AZD8205 and AZD5305 (saruparib)")
    assert tiers[0][1] is None             # AZD8205 is not saruparib


def test_class_guard_exempts_named_antibodies_only():
    assert T.is_class_like("mab inhibitor")
    assert not T.is_class_like("pembrolizumab antibody")


def test_three_letter_abbreviation_kept_when_unambiguous():
    assert resolve("PTX")[0][1] == "PACLITAXEL"
    assert resolve("AC") == [(N.TIER_UNRESOLVED, None)]   # a regimen
