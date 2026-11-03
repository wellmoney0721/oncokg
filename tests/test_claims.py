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
    questions = [question] if isinstance(question, str) else question
    ents, ev = [], []
    for q in questions:          # several questions: the union of their evidence
        e = KG.link_entities(q)
        ents += e
        ev += KG.retrieve(KG.classify(q, e), e)
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


# Codex round 2: each of these passed the second version
Q3C = ["What does osimertinib target?", "What does crizotinib target?"]
ROUND2 = [
    ("What does osimertinib target?", "EGFR is an osimertinib inhibitor."),
    ("What does osimertinib target?", "EGFR is what inhibited osimertinib."),
    ("What trials evaluate Tagrisso?", "Osimertinib is what evaluated NCT03909334."),
    ("What is AstraZeneca running in NSCLC?", "Osimertinib is what sponsored AstraZeneca."),
    ("What does osimertinib target?", "EGFR was inhibited osimertinib."),
    ("What does osimertinib target?", "Osimertinib acts on EGFR and on ALK."),
    ("What does osimertinib target?", "Osimertinib is an inhibitor of EGFR and of ALK."),
    ("What does osimertinib target?", "Osimertinib inhibits EGFR and also ALK."),
    (Q3C, "EGFR is a target of osimertinib and of crizotinib."),
    (Q3C, "Osimertinib acts on EGFR. Crizotinib acts on ALK and it inhibits EGFR."),
    (Q3C, "Osimertinib acts on EGFR. Crizotinib acts on ALK while this drug inhibits EGFR."),
    (Q3C, "Osimertinib acts on EGFR; crizotinib on EGFR."),
    (Q3C, "Crizotinib acts on ALK. On EGFR."),
    ("What trials evaluate Tagrisso?",
     "NCT03909334 (PHASE2, ACTIVE_NOT_RECRUITING) evaluates OSIMERTINIB. It is phase 3."),
    ("What trials evaluate Tagrisso?", "It is phase 3."),
    ("What trials evaluate Tagrisso?", "phase 3."),
    ("What is AstraZeneca running in NSCLC?",
     "AstraZeneca sponsors osimertinib in 10 trials with carboplatin."),
    ("Which drugs act on ALK?", "PLB1003 has 1 clinical trial."),
    ("Which drugs act on ALK?", "PLB1003 has 1 NSCLC trials."),
    ("Which drugs act on ALK?", "PLB1003: 1 trial."),
    ("Which drugs act on ALK?", "CONTELTINIB is phase 1."),
    ("Which companies are developing osimertinib?", "It has 14 trials."),
    ("What does fulvestrant target?", "Fulvestrant activates ESR1."),
    ("What does fulvestrant target?", "Fulvestrant is an agonist of ESR1."),
    ("What does osimertinib target?", "osimertinib is safe:"),
    ("What does osimertinib target?", "osimertinib is discontinued:\nOsimertinib acts on EGFR."),
    ("What does osimertinib target?", "these drugs are safe:\n- OSIMERTINIB acts on EGFR (inhibitor)"),
    ("What does osimertinib target?",
     "these drugs do not act on EGFR:\n- OSIMERTINIB acts on EGFR (inhibitor)"),
    ("What does osimertinib target?", "EGFR acts on these drugs:\n- OSIMERTINIB acts on EGFR (inhibitor)"),
    ("What is the capital of France?", "This trial is phase 4."),
    ("What trials evaluate Tagrisso?", "This trial is phase 3."),
    ("What does osimertinib target?", "osimertinib is liposomal."),
    ("What does osimertinib target?", "osimertinib is a biosimilar."),
    ("What does osimertinib target?", "Osimertinib is not liposomal."),
    ("What does osimertinib target?", "liposomal Tagrisso."),
    ("What does osimertinib target?", "Osimertinib [ORG:is safe] acts on EGFR."),
    ("What does osimertinib target?", "Osimertinib [ORG:inhibits ALK and] acts on EGFR."),
    ("What does osimertinib target?", "Osimertinib is for lung cancer."),
    ("What does osimertinib target?", "Osimertinib is lung cancer."),
]


@pytest.mark.parametrize("q,a", ROUND2)
def test_round2_attacks_are_caught(q, a):
    grounded, found = kinds(q, a)
    assert grounded is False, a


FAITHFUL2 = [
    ("What does osimertinib target?", "Osimertinib acts on EGFR and it inhibits EGFR."),
    ("What does osimertinib target?", "Osimertinib (Tagrisso) acts on EGFR."),
    ("What does osimertinib target?", "AZD 9291 acts on EGFR."),
    ("What does osimertinib target?", "Osimertinib is an EGFR inhibitor."),
    ("What does fulvestrant target?", "Fulvestrant is an antagonist of ESR1."),
    (Q3C, "Osimertinib acts on EGFR. Crizotinib acts on ALK and it inhibits ALK."),
    (Q3C, "osimertinib acts on EGFR and crizotinib acts on ALK."),
    ("What is the capital of France?", "This graph cannot answer that question."),
]


@pytest.mark.parametrize("q,a", FAITHFUL2)
def test_round2_faithful_forms_pass(q, a):
    grounded, found = kinds(q, a)
    assert grounded is True, found


# Codex round 3: each of these passed the third version
ROUND3 = [
    ("Which drugs act on ALK?", "LORLATINIB and PLB1003 act on ALK and they are approved."),
    ("Which drugs act on ALK?", "PLB1003 and LORLATINIB act on ALK and they are approved."),
    ("What is AstraZeneca running in NSCLC?",
     "AstraZeneca sponsors osimertinib in 10 trials evaluating carboplatin."),
    ("What is AstraZeneca running in NSCLC?",
     "AstraZeneca sponsors 10 trials evaluating carboplatin and osimertinib."),
    ("What is AstraZeneca running in NSCLC?",
     "AstraZeneca sponsors osimertinib and carboplatin in 10 trials."),
    ("What does osimertinib target?",
     "these drugs are sponsors of trials:\n- OSIMERTINIB acts on EGFR (inhibitor)"),
    ("What does osimertinib target?",
     "these drugs are activators:\n- OSIMERTINIB acts on EGFR (inhibitor)"),
    ("What does osimertinib target?",
     "these drugs inhibit EGFR with ALK:\n- OSIMERTINIB acts on EGFR (inhibitor)"),
    ("What does osimertinib target?", "these drugs with ALK:\n- OSIMERTINIB acts on EGFR (inhibitor)"),
    ("What does osimertinib target?", "Osimertinib is in clinical trials."),
    ("What does osimertinib target?", "Osimertinib is in NSCLC trials."),
    ("What does osimertinib target?", "Osimertinib is an NSCLC drug."),
    ("What does osimertinib target?", "EGFR is a drug."),
    ("What is the capital of France?", "There are clinical trials."),
    ("Which drugs act on ALK?", "PLB1003 is LORLATINIB."),
    ("What trials evaluate Tagrisso?", "NCT03909334 is NCT07680790."),
    ("Which drugs act on ALK?", "PLB1003 has NSCLC trials: 1."),
    ("Which drugs act on ALK?", "PLB1003 has NSCLC trials."),
    ("Which drugs act on ALK?", "LORLATINIB is approved in NSCLC."),
    ("Which drugs act on ALK?", "Lorlatinib is approved in lung cancer."),
    ("What does osimertinib target?", "Osimertinib [ORG:is-safe] acts on EGFR."),
    ("What does osimertinib target?", "Osimertinib [ORG:does-not-inhibit] acts on EGFR."),
]


@pytest.mark.parametrize("q,a", ROUND3)
def test_round3_attacks_are_caught(q, a):
    grounded, found = kinds(q, a)
    assert grounded is False, a


FAITHFUL3 = [
    ("What does osimertinib target?", "Osimertinib targets EGFR and inhibits it."),
    ("What trials evaluate Tagrisso?", "NCT03909334 evaluates osimertinib in phase 2."),
    ("What trials evaluate Tagrisso?", "NCT03909334 is a phase II trial evaluating osimertinib."),
    ("What trials evaluate Tagrisso?", "NCT03535363 is a completed phase 1 trial of osimertinib."),
    ("What trials evaluate Tagrisso?",
     "Phase 3 trials evaluating osimertinib include NCT07680790 and NCT02411448."),
    ("What trials evaluate Tagrisso?",
     "The trials include NCT03909334 (phase 2, active not recruiting) and "
     "NCT07680790 (phase 3, recruiting)."),
    ("What is AstraZeneca running in NSCLC?",
     "AstraZeneca sponsors 14 NSCLC trials evaluating osimertinib and 10 NSCLC trials "
     "evaluating carboplatin."),
    ("What is AstraZeneca running in NSCLC?",
     "AstraZeneca is the sponsor of 14 NSCLC trials of osimertinib and 10 NSCLC trials of "
     "carboplatin and 8 NSCLC trials of gefitinib."),
    ("What does osimertinib target?", "AZD9291 (AZD-9291) acts on EGFR."),
    ("What does osimertinib target?", "Osimertinib (Tagrisso, AZD 9291, AZD9291) acts on EGFR."),
    ("What does osimertinib target?", "The mechanism recorded for osimertinib is inhibition of EGFR."),
    ("Which drugs act on ALK?",
     "PLB1003 inhibits ALK; its maximum stage is phase 1, with 0 NSCLC trials in this graph."),
    ("Which drugs act on ALK?", "ALK inhibitors include:\n- lorlatinib\n- crizotinib\n- alectinib"),
    ("Which companies are developing osimertinib?",
     "The graph records trial sponsorship. AstraZeneca is a lead sponsor for osimertinib trials."),
    ("What is the capital of France?",
     "The graph does not contain the information needed to answer this question."),
    ("What is the capital of France?", "No relevant evidence was retrieved."),
]


@pytest.mark.parametrize("q,a", FAITHFUL3)
def test_round3_faithful_forms_pass(q, a):
    grounded, found = kinds(q, a)
    assert grounded is True, found


# Codex round 4: each of these passed the fourth version
ROUND4 = [
    ("What does osimertinib target?", "The following safe drugs:\n- OSIMERTINIB acts on EGFR (inhibitor)."),
    ("What does osimertinib target?",
     "The following discontinued drugs:\n- OSIMERTINIB acts on EGFR (inhibitor)."),
    ("What does osimertinib target?", "The following safe drugs:\n- Osimertinib"),
    ("What trials evaluate Tagrisso?",
     "The following terminated trials:\n- NCT07680790 (PHASE3, RECRUITING) evaluates OSIMERTINIB."),
    ("Which drugs act on ALK?",
     "PLB1003 and LORLATINIB act on ALK and they act on ALK and they are approved."),
    ("Which drugs act on ALK?", "LORLATINIB and PLB1003 act on ALK and are approved."),
    ("What is AstraZeneca running in NSCLC?",
     "AstraZeneca sponsors osimertinib and carboplatin. It sponsors them in 10 trials."),
    ("What is AstraZeneca running in NSCLC?",
     "AstraZeneca sponsors osimertinib and carboplatin. It sponsors them. They have 10 trials."),
    ("What is AstraZeneca running in NSCLC?",
     "AstraZeneca sponsors osimertinib and carboplatin in trials: 10."),
    ("What trials evaluate Tagrisso?",
     "NCT03909334 and NCT07680790 are recruiting trials of osimertinib."),
    ("What trials evaluate Tagrisso?",
     "NCT03909334 and NCT07680790 are phase 3 trials of osimertinib."),
    ("What trials evaluate Tagrisso?",
     "Recruiting trials evaluating osimertinib include NCT07680790 and NCT03909334."),
    ("What does osimertinib target?", "EGFR is a drug inhibited by osimertinib."),
    ("Which drugs act on ALK?", "PLB1003 inhibits ALK in clinical trials in this graph."),
    ("Which drugs act on ALK?", "PLB1003 acts on ALK in NSCLC trials."),
    ("What does osimertinib target?", "Osimertinib does N O T inhibit EGFR."),
    ("Which drugs act on ALK?", "ALK is targeted by PLB1003 and LORLATINIB. they are approved."),
    ("Which drugs act on ALK?", "LORLATINIB and PLB1003 act on ALK. it is approved."),
    ("What does osimertinib target?", "Osimertinib inhibits EGFR and is EGFR."),
    ("Which drugs act on ALK?", "LORLATINIB has 13% NSCLC trials."),
    ("Which drugs act on ALK?", "PLB1003 has 1 phase."),
]


@pytest.mark.parametrize("q,a", ROUND4)
def test_round4_attacks_are_caught(q, a):
    grounded, found = kinds(q, a)
    assert grounded is False, a


FAITHFUL4 = [
    ("Which drugs act on ALK?", "LORLATINIB and CRIZOTINIB act on ALK. They are approved."),
    ("Which drugs act on ALK?", "LORLATINIB and CRIZOTINIB act on ALK. they are approved."),
    ("What trials evaluate Tagrisso?", "NCT07680790 and NCT02411448 are phase 3."),
    ("What is AstraZeneca running in NSCLC?",
     "AstraZeneca sponsors 14 trials of osimertinib (Tagrisso)."),
    ("What does osimertinib target?",
     "Osimertinib acts on EGFR [CHEMBL3353410, ENSG00000146648]."),
    ("What trials evaluate Tagrisso?",
     "Trials of osimertinib include NCT03909334 and NCT07680790."),
]


@pytest.mark.parametrize("q,a", FAITHFUL4)
def test_round4_faithful_forms_pass(q, a):
    grounded, found = kinds(q, a)
    assert grounded is True, found
