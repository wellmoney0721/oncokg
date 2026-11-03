"""Read-only reproduction for the independent audit of 0c441e0.

Run: python -B audit_evidence_claims/r5/replay5_main.py
Only writes the adjacent JSON evidence file.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from app import Engine
from claims import check_claims, _units

engine = Engine()
Q_TARGET = "What does osimertinib target?"
Q_SPONSOR = "Which companies are developing osimertinib?"
Q_TRIAL = "What trials evaluate Tagrisso?"
Q_ALK = "Which drugs act on ALK?"
Q_PROFILE = "What is osimertinib?"

CASES = [
    ("control_safe", Q_TARGET, "Osimertinib is safe."),
    ("control_discontinued", Q_SPONSOR, "AstraZeneca has discontinued osimertinib."),
    ("control_not", Q_TARGET, "Osimertinib does not act on EGFR."),
    ("contracted_negation", Q_TARGET, "Osimertinib isn't an inhibitor of EGFR."),
    ("curly_contracted_negation", Q_TARGET, "Osimertinib isn’t an inhibitor of EGFR."),
    ("no_longer", Q_TARGET, "Osimertinib no longer acts on EGFR."),
    ("un_prefix", Q_TRIAL, "NCT07680790 is unrecruiting."),
    ("un_hyphen", Q_TRIAL, "NCT07680790 is un-recruiting."),
    ("non_hyphen", Q_TRIAL, "NCT07680790 is non-recruiting."),
    ("non_inhibitor", Q_TARGET, "Osimertinib is a non-inhibitor of EGFR."),
    ("non_closed", Q_TRIAL, "NCT07680790 is nonrecruiting."),
    ("not_laundered", Q_TRIAL, "NCT03909334 is not ACTIVE_NOT_RECRUITING."),
    ("quoted_developing", Q_SPONSOR, "AstraZeneca is developing the drug osimertinib."),
    ("quoted_developing_2", Q_SPONSOR, "AstraZeneca has evidence of developing osimertinib."),
    ("quoted_absence", Q_SPONSOR, "there is not evidence that AstraZeneca sponsors osimertinib."),
    ("quoted_absence_natural", Q_SPONSOR, "This is not evidence that AstraZeneca sponsors osimertinib."),
    ("no_evidence_control", Q_SPONSOR, "AstraZeneca has no evidence of developing osimertinib."),
    ("square_bracket_claim", Q_TARGET, "Osimertinib [is safe and discontinued] acts on EGFR."),
    ("markdown_link_label", Q_TARGET, "[osimertinib is safe](osimertinib) acts on EGFR."),
    ("markdown_bold", Q_TARGET, "**Osimertinib** acts on **EGFR**."),
    ("markdown_table", Q_TARGET, "| drug | target |\n| osimertinib | EGFR |\n| safe | all |"),
    ("korean_only", Q_TARGET, "오시머티닙은 안전하며 부작용이 없다."),
    ("korean_mixed", Q_TARGET, "osimertinib 은 안전하며 부작용이 없다."),
    ("korean_mixed_relation", Q_TARGET, "osimertinib 은 EGFR 을 억제하지 않는다."),
    ("korean_word", Q_TARGET, "osimertinib is 안전하다."),
    ("pronoun_inherits_target_only", Q_TARGET, "Osimertinib acts on EGFR. It sponsors trials."),
    ("pronoun_wrong_type", Q_TARGET, "Osimertinib acts on EGFR. It evaluates EGFR."),
    ("pronoun_newline", Q_TARGET, "Osimertinib acts on EGFR.\nit sponsors trials."),
    ("this_drug_newline", Q_TARGET, "Osimertinib acts on EGFR.\nthis drug evaluates EGFR."),
    ("plain_clinical_grammar", Q_TARGET, "Osimertinib is a treatment for all cancer."),
    ("clinical_from_profile", Q_PROFILE, "Osimertinib is approved for all lung cancer."),
    ("clinical_from_alk", Q_ALK, "PLB1003 is approved for all lung cancer and acts on ALK."),
    ("modality_can", Q_TARGET, "Osimertinib can act on EGFR."),
    ("modality_will", Q_TARGET, "Osimertinib will act on EGFR."),
    ("naked_relation", Q_TARGET, "EGFR sponsors osimertinib."),
    ("wrong_type_relation", Q_TARGET, "Osimertinib sponsors EGFR."),
    ("ownership_possessive", Q_SPONSOR, "AstraZeneca's osimertinib."),
    ("ownership_curly", Q_SPONSOR, "AstraZeneca’s osimertinib."),
    ("noun_egfr", Q_TARGET, "Osimertinib is an EGFR inhibitor."),
    ("reverse_noun", Q_TARGET, "EGFR is an osimertinib inhibitor."),
    ("agonist_as_inhibitor", "What does imiquimod target?", "Imiquimod is an inhibitor of TLR7."),
    ("agonist_as_blocks", "What does imiquimod target?", "Imiquimod blocks TLR7."),
    ("activator_as_inhibitor", "What does omaveloxolone target?", "Omaveloxolone inhibits NFE2L2."),
    ("repeat_safe_dedup", Q_TARGET, "Osimertinib is safe. EGFR is safe."),
    ("count_reversed", Q_ALK, "PLB1003 acts on ALK; NSCLC trials: 16."),
    ("count_inherited_control", Q_ALK, "PLB1003; 16 NSCLC trials."),
    ("digits_only_line", Q_TARGET, "0"),
    ("punctuation_only", Q_TARGET, "..."),
]

results = []
for case_id, question, answer in CASES:
    result = engine.check(question, answer)
    ents = engine.kg.link_entities(question)
    ev = engine.kg.retrieve(engine.kg.classify(question, ents), ents)
    raw = check_claims(answer, ev, engine.kg.link_entities)
    row = {"id": case_id, "question": question, "answer": answer,
           "result": result, "raw_claim_findings": raw,
           "units": _units(answer), "answer_entities": engine.kg.link_entities(answer)}
    results.append(row)
    print(json.dumps({"id": case_id, "grounded": result["checks"]["grounded"],
                      "findings": [(u["kind"], u["value"]) for u in result["checks"]["unsupported_claims"]]},
                     ensure_ascii=True))

out = Path(__file__).with_name("replay5_main_results.json")
out.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
