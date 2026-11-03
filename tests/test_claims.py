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
    ("What trials evaluate Tagrisso?", "NCT03909334 is recruiting.", "status"),
    ("What trials evaluate Tagrisso?",
     "Osimertinib is evaluated in 12 NSCLC trials.", "number"),
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


# Codex round 1: each of these passed the first version of the claim check
ROUND1 = [
    ("What does osimertinib target?", "EGFR acts on osimertinib."),
    ("What trials evaluate Tagrisso?", "osimertinib evaluates NCT03909334."),
    ("What is AstraZeneca running in NSCLC?", "osimertinib sponsors AstraZeneca."),
    ("What does osimertinib target?", "Osimertinib sponsors EGFR."),
    ("What is AstraZeneca running in NSCLC?", "osimertinib evaluates AstraZeneca."),
    ("What does osimertinib target?", "osimertinib acts on EGFR. It inhibits ALK."),
    ("What does osimertinib target?", "osimertinib acts on EGFR.\nThis drug inhibits ALK."),
    ("What trials evaluate Tagrisso?",
     "NCT03909334 evaluates osimertinib. It evaluates osimertinib and is phase 3."),
    ("What trials evaluate Tagrisso?", "NCT03909334 is phase 3 and NCT07680790 is phase 2."),
    ("What trials evaluate Tagrisso?", "NCT03909334 and NCT07680790 are recruiting."),
    ("What is AstraZeneca running in NSCLC?",
     "AstraZeneca sponsors 10 NSCLC trials evaluating osimertinib."),
    ("Which drugs act on ALK?", "PLB1003 acts on ALK with 13 NSCLC trials."),
    ("Which drugs act on ALK?", "PLB1003 is approved for all lung cancer and acts on ALK."),
    ("Which companies are developing osimertinib?",
     "AstraZeneca is developing the drug osimertinib."),
    ("Which companies are developing osimertinib?",
     "AstraZeneca has evidence of developing osimertinib."),
    ("Which companies are developing osimertinib?",
     "This is not evidence that AstraZeneca sponsors osimertinib."),
    ("What does osimertinib target?", "Osimertinib is a non-inhibitor of EGFR."),
    ("What trials evaluate Tagrisso?", "NCT07680790 is non-recruiting."),
    ("What does osimertinib target?", "Osimertinib [is safe and discontinued] acts on EGFR."),
    ("What does osimertinib target?", "[osimertinib is safe](osimertinib) acts on EGFR."),
    ("What does osimertinib target?", "오시머티닙은 안전하며 부작용이 없다."),
    ("What does osimertinib target?", "osimertinib 은 EGFR 을 억제하지 않는다."),
    ("What does osimertinib target?", "Osimertinib is a treatment for all cancer."),
    ("What does omaveloxolone target?", "Omaveloxolone inhibits NFE2L2."),
    ("Which drugs act on ALK?", "PLB1003 is phase 13."),
    ("What trials evaluate Tagrisso?", "NCT07680790 is phase 3b."),
    ("Which drugs act on ALK?", "PLB1003 has 13 non small cell lung cancer trials."),
    ("Which drugs act on ALK?", "- PLB1003: NSCLC trials: 13\n- lorlatinib: NSCLC trials: 0"),
    ("What does osimertinib target?", "Osimertinib can act on EGFR."),
    ("What is AstraZeneca running in NSCLC?",
     "AstraZeneca sponsors 10 NSCLC trials evaluating osimertinib and "
     "14 NSCLC trials evaluating carboplatin."),
    ("What does osimertinib target?", "osimertinib is the target of EGFR."),
    ("What does osimertinib target?", "The target of osimertinib is ALK."),
    ("Which drugs act on ALK?", "Lorlatinib activates ALK."),
]


@pytest.mark.parametrize("q,a", ROUND1)
def test_round1_attacks_are_caught(q, a):
    grounded, found = kinds(q, a)
    assert grounded is False, a


FAITHFUL = [
    ("Which companies are developing osimertinib?",
     "For osimertinib, the graph lists AstraZeneca as a trial sponsor."),
    ("Which companies are developing osimertinib?",
     "AstraZeneca sponsors 14 trials evaluating osimertinib, and Eli Lilly sponsors "
     "2 trials evaluating osimertinib."),
    ("What trials evaluate Tagrisso?",
     "NCT03909334 is a phase 2 trial evaluating osimertinib and is active, not recruiting."),
    ("What trials evaluate Tagrisso?", "NCT07680790 is a phase 3 trial evaluating Tagrisso."),
    ("What trials evaluate Tagrisso?", "Osimertinib is being tested in NCT03909334."),
    ("What does osimertinib target?", "The target of osimertinib is EGFR."),
    ("What does osimertinib target?", "EGFR is inhibited by osimertinib."),
    ("What does osimertinib target?", "Reported mechanism:\n- Osimertinib: inhibition of EGFR."),
    ("Which drugs act on ALK?", "ALK is targeted by alectinib, brigatinib and ceritinib."),
    ("Which drugs act on ALK?", "Agents acting on ALK:\n- LORLATINIB\n- CRIZOTINIB"),
    ("Which drugs act on ALK?", "CONTELTINIB acts on ALK with a maximum stage of phase 1/2."),
    ("Which drugs act on ALK?", "Crizotinib acts on ALK and has 15 NSCLC trials in this graph."),
    ("Which drugs act on ALK?", "Lorlatinib inhibits ALK."),
    ("What is AstraZeneca running in NSCLC?",
     "Osimertinib is being tested in NSCLC trials sponsored by AstraZeneca."),
    ("What is AstraZeneca running in NSCLC?",
     "AstraZeneca is the sponsor of 14 NSCLC trials of osimertinib and 10 NSCLC trials "
     "of carboplatin."),
    ("What is AstraZeneca running in NSCLC?",
     "AstraZeneca sponsors trials of these NSCLC drugs:\n- OSIMERTINIB\n- CARBOPLATIN"),
]


@pytest.mark.parametrize("q,a", FAITHFUL)
def test_faithful_paraphrases_pass(q, a):
    grounded, found = kinds(q, a)
    assert grounded is True, found
