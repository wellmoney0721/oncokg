"""Sentence-level claim check: relations, negations and ordinary-word claims."""
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
import config as C

if not (C.PROCESSED / "oncokg.sqlite").exists():
    pytest.skip("built graph missing - run src/run_all.py first", allow_module_level=True)

import query as Q

KG = Q.OncoKG()
VOCAB = set(KG.dic["index"])


def kinds(question, answer):
    ents = KG.link_entities(question)
    ev = KG.retrieve(KG.classify(question, ents), ents)
    r = KG.check_groundedness(answer, ev, ents, True, VOCAB, linker=KG.link_entities)
    return r["grounded"], {u["kind"] for u in r["unsupported_claims"]}


@pytest.mark.parametrize("q,a,kind", [
    ("Which companies are developing osimertinib?",
     "AstraZeneca has discontinued osimertinib.", "wording"),
    ("What does osimertinib target?",
     "Osimertinib targets EGFR and is safe for all patients.", "wording"),
    ("What does osimertinib target?", "Osimertinib does not act on EGFR.", "negation"),
    ("Which companies are developing osimertinib?",
     "AstraZeneca develops osimertinib.", "development_claim"),
    ("Which drugs act on ALK?", "Alectinib acts on EGFR.", "relation"),
    ("Which drugs act on ALK?", "Alectinib is better than lorlatinib on ALK.", "comparison"),
    ("Which drugs act on ALK?", "Alectinib may act on ALK.", "speculation"),
    ("What trials evaluate Tagrisso?",
     "NCT07680790 is a phase 2 trial evaluating osimertinib.", "phase"),
    ("What trials evaluate Tagrisso?", "NCT03909334 is recruiting.", "wording"),
    ("What trials evaluate Tagrisso?",
     "Osimertinib is evaluated in 12 NSCLC trials.", "count"),
])
def test_unsupported_claims_are_reported(q, a, kind):
    grounded, found = kinds(q, a)
    assert grounded is False and kind in found, found


@pytest.mark.parametrize("q,a", [
    ("Which drugs act on ALK?", "Alectinib and lorlatinib act on ALK."),
    ("What does osimertinib target?", "Osimertinib acts on EGFR."),
    ("Which companies are developing osimertinib?",
     "AstraZeneca sponsors trials of osimertinib."),
    ("What trials evaluate Tagrisso?",
     "NCT07680790 is a phase 3 trial evaluating osimertinib and is recruiting."),
])
def test_supported_claims_pass(q, a):
    grounded, found = kinds(q, a)
    assert grounded is True, found


@pytest.mark.parametrize("q", [
    "Which drugs act on ALK?", "What does osimertinib target?",
    "What trials evaluate Tagrisso?", "What is AstraZeneca running in NSCLC?",
    "Which companies are developing osimertinib?"])
def test_restating_the_evidence_passes(q):
    # the template answer is the evidence itself; read as prose it must pass
    a = KG.answer(q, use_llm=False)
    ents = KG.link_entities(q)
    ev = KG.retrieve(a.intent, ents)
    r = KG.check_groundedness(a.text.split("\nScope:")[0], ev, ents, True, VOCAB,
                              linker=KG.link_entities)
    assert r["grounded"] is True, r["unsupported_claims"]


def test_short_words_do_not_join_into_a_drug_abbreviation():
    labels = {e["label"] for e in KG.link_entities("NCT07680790 is a phase 3 trial")}
    assert "ISATUXIMAB" not in labels
