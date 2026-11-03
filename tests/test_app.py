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
    assert [u["value"].lower() for u in bad["checks"]["unsupported_claims"]] == ["zorbatinib"]
    num = ENGINE.check("What trials evaluate Tagrisso?", "It is in 4,812 trials.")
    assert not num["checks"]["grounded"]
    # a false relation built from true tokens passes: the documented limit
    rel = ENGINE.check("Which companies are developing osimertinib?",
                       "AstraZeneca has discontinued osimertinib.")
    assert rel["checks"]["grounded"] is True
