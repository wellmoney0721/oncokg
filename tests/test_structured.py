"""Structured answers: every claim checked against the graph, prose written from them."""
import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import config as C

if not (C.PROCESSED / "oncokg.sqlite").exists():
    pytest.skip("built graph missing - run src/run_all.py first", allow_module_level=True)

import query as Q

KG = Q.OncoKG()
OSI_EGFR = "CHEMBL3353410|ACTS_ON|ENSG00000146648|CHEMBL3353410"
T1 = "NCT03909334|EVALUATES|CHEMBL3353410|NCT03909334"
AZ_OSI = "ORG:astrazeneca|SPONSORS_TRIAL_OF|CHEMBL3353410|"
Q3 = "What does osimertinib target?"
Q2 = "What trials evaluate Tagrisso?"
Q5 = "What is AstraZeneca running in NSCLC?"
Q4 = "Which drugs act on ALK?"


def evidence(q):
    e = KG.link_entities(q)
    return KG.retrieve(KG.classify(q, e), e)


def verify(q, *claims, raw=None):
    return KG.verify_structured(raw if raw is not None else json.dumps({"claims": list(claims)}),
                                evidence(q))


def rel(rel, s, o, ev, **kw):
    return {"kind": "relation", "relation": rel, "subject": s, "object": o, "evidence": ev, **kw}


@pytest.mark.parametrize("q,claim", [
    (Q3, rel("ACTS_ON", "osimertinib", "EGFR", OSI_EGFR)),
    (Q3, rel("ACTS_ON", "Tagrisso", "EGFR", OSI_EGFR, action="inhibitor")),
    (Q3, rel("ACTS_ON", "CHEMBL3353410", "ENSG00000146648", OSI_EGFR)),
    (Q2, rel("EVALUATES", "NCT03909334", "osimertinib", T1)),
    (Q2, {"kind": "trial", "trial": "NCT03909334", "evidence": T1, "phase": ["phase 2"],
          "status": "active not recruiting"}),
    (Q5, rel("SPONSORS_TRIAL_OF", "AstraZeneca", "osimertinib", AZ_OSI, trial_count=14)),
])
def test_supported_claims_are_accepted(q, claim):
    r = verify(q, claim)
    assert r["verified"] and len(r["accepted"]) == 1, r["rejected"]


@pytest.mark.parametrize("q,claim,why", [
    (Q3, rel("ACTS_ON", "EGFR", "osimertinib", OSI_EGFR), "drug"),
    (Q3, rel("ACTS_ON", "osimertinib", "EGFR", OSI_EGFR, action="activator"), "action"),
    (Q3, rel("ACTS_ON", "osimertinib", "EGFR", OSI_EGFR, note="safe"), "unknown keys"),
    (Q3, rel("ACTS_ON", "osimertinib is safe", "EGFR", OSI_EGFR), "on its own"),
    (Q3, rel("EVALUATES", "osimertinib", "EGFR", OSI_EGFR), "ACTS_ON"),
    (Q3, rel("ACTS_ON", "osimertinib", "ALK",
             "CHEMBL3353410|ACTS_ON|ENSG00000171094|CHEMBL3353410"), "not among"),
    (Q3, rel("ACTS_ON", "osimertinib", "EGFR", T1), "not among"),
    (Q2, {"kind": "trial", "trial": "NCT03909334", "evidence": T1, "status": "RECRUITING"},
     "status"),
    (Q2, {"kind": "trial", "trial": "NCT03909334", "evidence": T1, "phase": ["PHASE3"]}, "phase"),
    (Q2, {"kind": "trial", "trial": "NCT07680790", "evidence": T1, "status": "RECRUITING"},
     "different trial"),
    (Q5, rel("SPONSORS_TRIAL_OF", "AstraZeneca", "osimertinib", AZ_OSI, trial_count=10), "14"),
    (Q5, rel("SPONSORS_TRIAL_OF", "AstraZeneca", "osimertinib", AZ_OSI, trial_count="14"),
     "whole number"),
    (Q5, rel("SPONSORS_TRIAL_OF", "AstraZeneca", "osimertinib", AZ_OSI, trial_count=True),
     "whole number"),
    (Q3, {"kind": "opinion", "text": "osimertinib is safe"}, "unknown kind"),
    (Q3, "osimertinib is safe", "JSON object"),
])
def test_unsupported_claims_are_rejected(q, claim, why):
    r = verify(q, claim)
    assert not r["verified"] and not r["accepted"]
    assert why in r["rejected"][0]["why"], r["rejected"][0]["why"]


def test_answer_shape_is_strict():
    assert not verify(Q3, raw="not json")["verified"]
    assert not verify(Q3, raw='{"claims": [], "summary": "safe"}')["verified"]
    assert not verify(Q3, raw='{"claims": []}')["verified"]
    assert not verify(Q3, raw='[{"kind": "relation"}]')["verified"]


def test_drug_claims_check_stage_and_count():
    ev = evidence(Q4)
    alk = next(e for e in ev if "PLB1003" in e.statement)
    ok = KG.verify_structured({"claims": [{"kind": "drug", "drug": "PLB1003",
                                            "evidence": alk.edge_id, "max_stage": "PHASE_1",
                                            "trials_in_graph": 0}]}, ev)
    assert ok["verified"], ok["rejected"]
    bad = KG.verify_structured({"claims": [{"kind": "drug", "drug": "PLB1003",
                                             "evidence": alk.edge_id, "max_stage": "APPROVAL"}]}, ev)
    assert not bad["verified"]


def test_prose_is_written_from_the_graph_not_the_claim():
    r = verify(Q3, rel("ACTS_ON", "tagrisso", "egfr", OSI_EGFR, action="Inhibitor"))
    assert r["text"] == f"- OSIMERTINIB acts on EGFR (inhibitor) [{OSI_EGFR}]"


def test_model_reply_is_checked_and_only_accepted_claims_reach_the_answer(monkeypatch):
    reply = json.dumps({"claims": [
        rel("ACTS_ON", "osimertinib", "EGFR", OSI_EGFR, action="INHIBITOR"),
        rel("ACTS_ON", "osimertinib", "EGFR", OSI_EGFR, action="ACTIVATOR"),
    ]})
    monkeypatch.setattr(Q.OncoKG, "_llm_claims", staticmethod(lambda q, ev: (reply, "fake")))
    a = KG.answer(Q3, use_llm=True)
    assert a.checks["grounded"] is False and a.checks["accepted"] == 1
    assert "ACTIVATOR" not in a.text.upper().replace("(INHIBITOR)", "")
    assert a.text.startswith("- OSIMERTINIB acts on EGFR (inhibitor)")
    assert "1 claim(s) were removed" in a.text


# Codex review s1
@pytest.mark.parametrize("name", ["osimertinib가 아닌", "osimertinib是安全的", "非osimertinib",
                                  "osimertinib💉", "OSIMERTINIB​", "osimertinib癌"])
def test_names_outside_the_graphs_spelling_are_rejected(name):
    r = verify(Q3, rel("ACTS_ON", name, "EGFR", OSI_EGFR))
    assert not r["verified"]


def test_label_copied_from_the_evidence_is_accepted():
    ev = evidence(Q4)
    alec = next(e for e in ev if e.statement.startswith("ALECTINIB HYDROCHLORIDE"))
    r = KG.verify_structured({"claims": [rel("ACTS_ON", "ALECTINIB HYDROCHLORIDE", "ALK",
                                             alec.edge_id, action="INHIBITOR")]}, ev)
    assert r["verified"], r["rejected"]


@pytest.mark.parametrize("raw", [
    '{"claims":[{"kind":[]}]}',
    '{"claims":[{"kind":"relation","relation":{},"subject":"osimertinib","object":"EGFR",'
    '"evidence":"' + OSI_EGFR + '"}]}',
    '{"claims":[{"kind":"relation","relation":"ACTS_ON","subject":"osimertinib",'
    '"object":"EGFR","evidence":"' + OSI_EGFR + '","action":NaN}]}',
    '{"claims":' + '[' * 5000 + 'null' + ']' * 5000 + '}',
])
def test_malformed_input_is_rejected_not_raised(raw):
    r = verify(Q3, raw=raw)
    assert not r["verified"] and r["rejected"]
    json.dumps(r, allow_nan=False)


def test_empty_reply_means_no_answer_not_a_removed_claim(monkeypatch):
    monkeypatch.setattr(Q.OncoKG, "_llm_claims", staticmethod(lambda q, ev: ('{"claims": []}', "f")))
    a = KG.answer(Q3, use_llm=True)
    assert "removed" not in a.text and "nothing in the evidence" in a.text


# Codex review s2
def test_overflowing_and_non_finite_numbers_keep_the_result_serialisable():
    raw = ('{"claims":[{"kind":"relation","relation":"SPONSORS_TRIAL_OF","subject":"AstraZeneca",'
           '"object":"osimertinib","evidence":"' + AZ_OSI + '","trial_count":1e309}]}')
    r = verify(Q5, raw=raw)
    assert not r["verified"]
    json.dumps(r, allow_nan=False)
    direct = KG.verify_structured({"claims": [rel("SPONSORS_TRIAL_OF", "AstraZeneca", "osimertinib",
                                                   AZ_OSI, trial_count=float("nan"))]}, evidence(Q5))
    assert not direct["verified"]
    json.dumps(direct, allow_nan=False)


def test_a_label_shared_by_two_nodes_is_ambiguous(monkeypatch):
    import structured as St
    v = St.Verifier(KG)

    class Conn:
        def __init__(self, real):
            self.real = real

        def execute(self, sql, args=()):
            if "lower(label)=lower(?)" in sql:
                return type("R", (), {"fetchall": lambda s: [
                    {"id": "CHEMBL1", "type": "Drug"}, {"id": "CHEMBL2", "type": "Drug"}]})()
            return self.real.execute(sql, args)

    monkeypatch.setattr(v, "kg", type("K", (), {"conn": Conn(KG.conn),
                                                 "link_entities": KG.link_entities})())
    ids, why = v.resolve("SHARED NAME", "Drug")
    assert not ids and "use the id" in why


def test_a_missing_or_failing_model_is_reported_not_presented_as_an_empty_answer(monkeypatch):
    monkeypatch.setattr(Q.OncoKG, "_llm_claims",
                        staticmethod(lambda q, ev: ("", "error: RuntimeError")))
    a = KG.answer(Q3, use_llm=True)
    assert "could not be used" in a.text and a.checks["applicable"] is False
