"""Read-only graph probes: refused spans, alias acceptance, punctuation, docs.

Run from repository root: python -B audit_evidence_claims/r2/standards_probe.py
All writes are next to this file; no network or model calls.
"""
import sys
import json
import re
from pathlib import Path

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "src"))
from app import Engine
from claims import _tokenise

engine = Engine()
q = "What does osimertinib target?"
cases = [
    ("refused_liposomal", q, "osimertinib is liposomal."),
    ("refused_biosimilar", q, "osimertinib is a biosimilar."),
    ("refused_negation", q, "Osimertinib is not liposomal."),
    ("refused_alias", q, "liposomal Tagrisso."),
    ("refused_non", q, "Osimertinib is non-liposomal."),
    ("control_ordinary", q, "Osimertinib is safe."),
    ("control_alias", q, "Tagrisso acts on EGFR."),
    ("alias_parentheses", q, "Osimertinib (Tagrisso) acts on EGFR."),
    ("alias_spaced_code", q, "AZD 9291 acts on EGFR."),
    ("alias_unspaced_code", q, "AZD9291 acts on EGFR."),
    ("punctuation_claim", q, "Osimertinib acts on EGFR!"),
    ("refusal", "What is the capital of France?", "This graph cannot answer that question."),
]
company_q = "Which companies are developing osimertinib?"
cases.append(("verbatim_exception", company_q,
              engine.ask(company_q)["evidence"][0]["statement"]))
results = []
for name, question, answer in cases:
    result = engine.check(question, answer)
    toks, ents = _tokenise(answer, engine.kg.link_entities, {}, None)
    results.append({"case": name, "question": question, "answer": answer,
                    "linked": engine.kg.link_entities(answer),
                    "tokens": toks, "token_entities": ents, **result})

punctuation = []
for suffix in ("?", "!", ":", ";", ",", "."):
    question = "Which drugs act on ALK" + suffix
    result = engine.ask(question)
    punctuation.append({"question": question, "intent": result["intent"],
                        "entities": result["entities"], "answer": result["answer"],
                        "evidence_count": len(result["evidence"])})

alias_rows = []
for hits in engine.dic["index"].values():
    for hit in hits:
        if re.search(r"\s", hit["alias"]):
            alias_rows.append((hit["alias"], hit["drug_id"]))
aliases = sorted({a for a, _ in alias_rows})
losses = []
total_linked = 0
for alias in aliases:
    linked = engine.kg.link_entities(alias)
    before = {e["id"] for e in linked if e["type"] == "Drug"}
    expected = {d for a, d in alias_rows if a == alias}
    intended = before & expected
    if not intended:
        continue
    total_linked += 1
    _, entities = _tokenise(alias, engine.kg.link_entities, {}, None)
    after = {e.get("id") for e in entities if e["type"] == "Drug"}
    if not intended & after:
        losses.append({"alias": alias, "linked": linked, "token_entities": entities})

output = {"cases": results, "punctuation_questions": punctuation,
          "alias_tokenisation": {"unique_multiword_aliases": len(aliases),
            "intended_linked_aliases": total_linked,
            "lost_intended_links": losses}}
Path(__file__).with_suffix(".json").write_text(
    json.dumps(output, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps({"cases": [{"case": r["case"], "grounded": r["checks"]["grounded"],
    "findings": r["checks"]["unsupported_claims"]} for r in results],
    "alias_tokenisation": output["alias_tokenisation"]}, ensure_ascii=False, indent=2))
