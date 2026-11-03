"""Independent R5 documentation, citations and faithful prose probes; read-only graph."""
import json
import sys
from dataclasses import asdict
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from app import Engine
from claims import _strip_citations

Q = {1: "Which companies are developing osimertinib?",
     2: "What trials evaluate Tagrisso?", 3: "What does osimertinib target?",
     4: "Which drugs act on ALK?", 5: "What is AstraZeneca running in NSCLC?",
     6: "What is the capital of France?"}

FAITHFUL = {
1: [
    "AstraZeneca is the lead sponsor of 14 trials evaluating osimertinib.",
    "AstraZeneca leads 14 trials investigating Tagrisso.",
    "Bristol Myers Squibb and Eli Lilly sponsor trials of osimertinib.",
    "AstraZeneca sponsors 14 trials of osimertinib (Tagrisso).",
    "The graph records sponsorship of osimertinib trials by AstraZeneca.",
    "Sponsors of osimertinib trials include AstraZeneca and Bristol Myers Squibb.",
    "AstraZeneca sponsors 14 trials of osimertinib. Bristol Myers Squibb sponsors 2 trials of it.",
    "AstraZeneca sponsors trials evaluating osimertinib. This is evidence of trial sponsorship, not drug development.",
],
2: [
    "NCT03909334 is a phase 2 trial evaluating Tagrisso. It is active, not recruiting.",
    "Trials of osimertinib include NCT03909334 and NCT07680790.",
    "NCT07680790 and NCT02411448 are phase 3 trials of osimertinib.",
    "NCT03909334 and NCT02411448 evaluate osimertinib. They are active, not recruiting.",
    "Osimertinib is being tested in NCT07680790, a recruiting phase 3 trial.",
    "NCT03535363 is a completed phase 1 trial evaluating osimertinib.",
    "NCT07680790 is recruiting. NCT03909334 is active but not recruiting.",
    "Reported trials:\n- NCT03909334: phase 2, active not recruiting, evaluates osimertinib.\n- NCT07680790: phase 3, recruiting, evaluates osimertinib.",
],
3: [
    "Osimertinib inhibits EGFR.",
    "EGFR is inhibited by osimertinib.",
    "Osimertinib is an inhibitor of EGFR [CHEMBL3353410, ENSG00000146648].",
    "The graph records osimertinib acting on EGFR as an inhibitor.",
    "Tagrisso targets EGFR. It is an EGFR inhibitor.",
    "Reported mechanism: inhibition of EGFR by osimertinib.",
    "The target of osimertinib is EGFR.",
    "Osimertinib acts on EGFR; its recorded action is inhibition.",
],
4: [
    "Lorlatinib, crizotinib and alectinib inhibit ALK.",
    "ALK is targeted by lorlatinib and crizotinib.",
    "Lorlatinib and crizotinib act on ALK. They are approved.",
    "PLB1003 inhibits ALK and has a maximum stage of phase 1.",
    "The graph records 13 NSCLC trials of lorlatinib and 15 NSCLC trials of crizotinib.",
    "Conteltinib is an ALK inhibitor with a maximum stage of phase 1/2.",
    "These drugs inhibit ALK:\n- Lorlatinib\n- Crizotinib\n- Alectinib",
    "Lorlatinib inhibits ALK. It has 13 NSCLC trials in this graph.",
],
5: [
    "AstraZeneca sponsors 14 NSCLC trials evaluating osimertinib.",
    "AstraZeneca sponsors 14 trials of osimertinib and 10 trials of carboplatin.",
    "AstraZeneca is conducting trials of osimertinib and durvalumab in NSCLC.",
    "Osimertinib and carboplatin are evaluated in trials sponsored by AstraZeneca.",
    "AstraZeneca sponsors trials of Tagrisso. There are 14 such trials in this graph.",
    "AstraZeneca sponsors 7 NSCLC trials evaluating durvalumab and 8 evaluating gefitinib.",
    "Reported sponsorship:\n- AstraZeneca: 14 NSCLC trials of osimertinib.\n- AstraZeneca: 10 NSCLC trials of carboplatin.",
    "AstraZeneca runs 6 NSCLC trials of pemetrexed and 6 of cisplatin.",
],
6: [
    "This graph cannot answer that question.",
    "The retrieved evidence does not contain that information.",
    "No relevant evidence was found in this graph.",
    "I cannot determine the capital of France from this graph.",
    "The question is outside the scope of this graph.",
    "There is no supporting evidence for an answer.",
]}

ATTACKS = [
("cite_known_target",3,"Osimertinib acts on EGFR [ENSG00000146648]."),
("cite_known_pair_space",3,"Osimertinib acts on EGFR [CHEMBL3353410 ENSG00000146648]."),
("cite_known_pair_semicolon",3,"Osimertinib acts on EGFR [CHEMBL3353410; ENSG00000146648]."),
("cite_known_pair_newline",3,"Osimertinib acts on EGFR [CHEMBL3353410\nENSG00000146648]."),
("cite_known_dup",3,"Osimertinib acts on EGFR [CHEMBL3353410,CHEMBL3353410]."),
("cite_unknown_target",3,"Osimertinib acts on EGFR [ENSG00000171094]."),
("cite_unknown_drug",3,"Osimertinib acts on EGFR [CHEMBL601719]."),
("cite_mixed_target",3,"Osimertinib acts on EGFR [CHEMBL3353410, ENSG00000171094]."),
("cite_fake_org",3,"Osimertinib [ORG:is-safe] acts on EGFR."),
("cite_mixed_org",3,"Osimertinib [CHEMBL3353410, ORG:is-safe] acts on EGFR."),
("cite_known_safe",3,"Osimertinib is safe [CHEMBL3353410, ENSG00000146648]."),
("cite_known_not",3,"Osimertinib does not inhibit EGFR [CHEMBL3353410]."),
("cite_known_bracket_claim",3,"Osimertinib [CHEMBL3353410 is safe] acts on EGFR."),
("cite_md_claim",3,"[Osimertinib is safe](CHEMBL3353410) acts on EGFR."),
("cite_html_link_claim",3,"Osimertinib <a href='CHEMBL3353410'>is safe</a> acts on EGFR."),
("cite_link_destination_claim",3,"[Osimertinib](is-safe-and-discontinued) acts on EGFR."),
("letters_not",3,"Osimertinib does N O T inhibit EGFR."),
("letters_not_hyphen",3,"Osimertinib does N-O-T inhibit EGFR."),
("letters_not_comma",3,"Osimertinib does N, O, T inhibit EGFR."),
("letters_not_slash",3,"Osimertinib does N/O/T inhibit EGFR."),
("letters_not_dots",3,"Osimertinib does N.O.T inhibit EGFR."),
("letters_safe",3,"Osimertinib is S A F E."),
("letters_safe_comma",3,"Osimertinib is S, A, F, E."),
("letters_safe_dot",3,"Osimertinib is S.A.F.E."),
("clinical_drug_is_trial",2,"Osimertinib is a clinical trial evaluated in NCT07680790."),
("clinical_drug_is_trial_plain",2,"Osimertinib is a clinical trial."),
("clinical_target_trial",4,"ALK is in clinical trials with lorlatinib."),
("clinical_target_drug",3,"The drug EGFR is inhibited by osimertinib."),
("clinical_source_words",3,"Osimertinib is a treatment for all cancer."),
("clinical_recruit_drug",2,"Osimertinib is recruiting."),
("clinical_phase_drug",2,"Osimertinib is phase 3."),
("ordinary_safe",3,"Osimertinib is safe."),
("ordinary_discontinued",3,"Osimertinib is discontinued."),
]

engine = Engine()
rows = []
for category, cases in [("faithful", [(f"faithful_q{q}_{i+1}",q,a) for q, answers in FAITHFUL.items() for i,a in enumerate(answers)]), ("probe", ATTACKS)]:
    for ident,q,a in cases:
        result=engine.check(Q[q],a)
        ents=engine.kg.link_entities(Q[q]); evidence=engine.kg.retrieve(engine.kg.classify(Q[q],ents),ents)
        row={"id":ident,"category":category,"question_key":q,"question":Q[q],"answer":a,"result":result,"full_evidence":[asdict(e) for e in evidence]}
        rows.append(row)
        print(ident,result['checks']['grounded'],[(u['kind'],u['value']) for u in result['checks']['unsupported_claims']])
(ROOT/'audit_evidence_claims/r6/replay6_r5_docs5_probe_results.json').write_text(json.dumps(rows,indent=2,ensure_ascii=False),encoding='utf-8')
summary={str(q):{'passed':sum(r['result']['checks']['grounded'] for r in rows if r['category']=='faithful' and r['question_key']==q),'total':len(answers)} for q,answers in FAITHFUL.items()}
print(json.dumps(summary))
(ROOT/'audit_evidence_claims/r6/replay6_r5_docs5_faithful_summary.json').write_text(json.dumps(summary,indent=2),encoding='utf-8')
