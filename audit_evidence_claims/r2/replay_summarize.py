import json
from pathlib import Path

OUT = Path(__file__).resolve().parent
OLD = OUT.parent
sources = [
    ("main_results", "id", "result"),
    ("adversarial_results", "id", None),
    ("adversarial_pairs_results", "id", None),
    ("faithful_results", "id", None),
    ("code_probes", "tag", "result"),
]
comparisons = []
for stem, key, wrapper in sources:
    old = json.loads((OLD / f"independent_{stem}.json").read_text(encoding="utf-8"))
    new = json.loads((OUT / f"replay_{stem}.json").read_text(encoding="utf-8"))
    if stem == "faithful_results":
        old, new = old["cases"], new["cases"]
    assert len(old) == len(new)
    for a, b in zip(old, new):
        assert a[key] == b[key]
        for field in ("question", "retrieval_questions", "answer"):
            assert a.get(field) == b.get(field), (stem, a[key], field)
        ac = a[wrapper]["checks"] if wrapper else a["checks"]
        bc = b[wrapper]["checks"] if wrapper else b["checks"]
        comparisons.append({"source":stem, "id":b[key], "question":b.get("question"),
                            "retrieval_questions":b.get("retrieval_questions"), "answer":b["answer"],
                            "saved_snapshot_grounded":ac["grounded"], "r2_grounded":bc["grounded"],
                            "r2_unsupported_claims":bc["unsupported_claims"]})
(OUT / "replay_comparison.json").write_text(json.dumps(comparisons, indent=2, ensure_ascii=False), encoding="utf-8")
for stem, _, _ in sources:
    rows = [r for r in comparisons if r["source"] == stem]
    print(stem, len(rows), "passed now:", sum(r["r2_grounded"] for r in rows))
print("TOTAL", len(comparisons))
print("PASSED BOTH NONFAITHFUL")
for r in comparisons:
    if r["source"] != "faithful_results" and r["saved_snapshot_grounded"] and r["r2_grounded"]:
        print(r["source"], r["id"], r["answer"])
print("TEMPLATES")
for r in json.loads((OUT / "replay_faithful_results.json").read_text(encoding="utf-8"))["templates"]:
    print(r["question"], "prose", r["prose_generated_checks"]["grounded"], "full", r["full_template_checks"]["grounded"])

byid = {(r["source"], r["id"]):r for r in comparisons}
M, A, P, C = "main_results", "adversarial_results", "adversarial_pairs_results", "code_probes"
finding_rows = [
    (1, [(A,"reversed_target"),(M,"reverse_noun"),(A,"reversed_trial"),(A,"reversed_sponsor"),(M,"wrong_type_relation")]),
    (2, [(A,"pronoun_target_same_line"),(A,"pronoun_target_newline"),(A,"pronoun_this_drug"),(A,"trial_pronoun_reset")]),
    (3, [(A,"swapped_trial_phases"),(A,"pooled_trial_status2"),(A,"wrong_sponsor_count"),(A,"wrong_drug_count_target"),(M,"clinical_from_alk")]),
    (4, [(M,"quoted_developing"),(M,"quoted_developing_2"),(M,"quoted_absence_natural")]),
    (5, [(M,"non_inhibitor"),(M,"non_hyphen")]),
    (6, [(M,"square_bracket_claim"),(M,"markdown_link_label"),(M,"korean_only"),(M,"korean_mixed_relation")]),
    (7, [(M,"plain_clinical_grammar"),(M,"activator_as_inhibitor")]),
    (8, [(P,"phase_13_regex"),(C,"phase_suffix"),(A,"count_long_unit"),(P,"count_after_colon_list")]),
]
report = ["# Round 1 reproduction replay at a12762b", "",
"All six original `independent_*.py` probe scripts were rerun through adapted copies. Only import-root depth, output filenames, and the run-command comment changed. The adaptation diffs and source SHA-256 values are retained in `replay_*_adaptation.diff` and `replay_manifest.json`. All six exit codes are zero. `replay_comparison.json` covers all 142 exact question/answer cases; question and answer identity against the stored input snapshots was asserted. The dictionary probe and six template cases are additional to the 142.", "",
"Stored `independent_*_results.json` outcomes are not treated as pristine round-1 results: for example, the stored paired-clause result already says true at line 138, despite the R1 report recording false. Historical status below follows `r1_report.md`; current status follows this fresh replay.", "",
"## BLOCKERS", "",
"R1 finding 1 is **NOT FIXED**. `Engine().check(\"What does osimertinib target?\", \"EGFR is an osimertinib inhibitor.\")` still yields `grounded=True`, `unsupported_claims=[]`. Retrieved evidence says `OSIMERTINIB acts on EGFR (inhibitor)`. The nearest left entity becomes osimertinib (`src/claims.py:382`); because the right endpoint is missing, the noun fallback fills it from any unused entity of target type (`src/claims.py:407-411`). This reconstructs the valid inverse relation rather than checking the written claim.", "",
"FIXED below means the exact R1 reported reproductions are now rejected; it makes no claim about every new variant of that mechanism.", "",
"| R1 finding | Status | Fresh result |", "|---|---|---|"]
for number, ids in finding_rows:
    passed = sum(byid[k]["r2_grounded"] for k in ids)
    report.append(f"| {number} | {'NOT FIXED' if passed else 'FIXED'} | {passed}/{len(ids)} exact reported attacks still pass |")
report.extend(["", "Exact R1 reported inputs, including the newline pronoun variant:", "",
               "| R1 | Question | Exact answer | Observed output |", "|---|---|---|---|"])
for number, ids in finding_rows:
    for k in ids:
        r = byid[k]
        question = r["question"] or " + ".join(r["retrieval_questions"])
        answer = r["answer"].replace("\n", "\\n")
        findings = [(u["kind"], u["value"]) for u in r["r2_unsupported_claims"]]
        report.append(f"| {number} | `{question}` | `{answer}` | `grounded={r['r2_grounded']}`; `{findings}` |")
report.extend(["", "## SHOULD FIX", "",
"R1 faithful-paraphrase finding: **NOT FIXED (substantially improved)**. The unchanged 36-answer corpus now flags 1/30 evidence answers (3.3%) versus the R1 report's 10/30 (33.3%). Refusals improve from 6/6 flagged to 2/6 flagged. This is a diagnostic corpus, not a production LLM rate.", "",
"| Demo question | R1 flagged | R2 flagged |", "|---|---|---|"])
faithful = json.loads((OUT / "replay_faithful_results.json").read_text(encoding="utf-8"))
for old, r in zip([2,2,1,3,2,6], faithful["summary"]):
    report.append(f"| {r['question']} | {old}/6 | {r['flagged']}/6 |")
report.extend(["", "The remaining exact rejected corpus answers are:", ""])
for r in faithful["cases"]:
    if not r["checks"]["grounded"]:
        findings = [(u["kind"], u["value"]) for u in r["checks"]["unsupported_claims"]]
        report.append(f"- `{r['id']}` / `{r['question']}` / `{r['answer']}` => `grounded=False`, `{findings}`.")
report.extend(["", "R1 paired-clause Cartesian-product finding: **FIXED for all three exact relation-pair reproductions**. Correct drug/target, trial/drug, and company/drug clauses now pass both the same-sentence and two-sentence forms; all three swapped-pair attacks fail. See `replay_adversarial_pairs_results.json`.", "",
"R1 dedup finding: **FIXED for distinct sentence contexts**. `Osimertinib is safe. EGFR is safe.` preserves two separate `wording: safe` findings. The second dedup reproduction, `osimertinib is safe. osimertinib is safe for all.`, preserves both safe contexts plus all. `src/query.py:560-562` keys by `(value, sentence)`. Both remain `grounded=False`.", "",
"The documentation finding is assigned to the independent documentation reviewer; no status is inferred from test success here.", "",
"## NOTES", "",
"- Exact regression command: `python -m pytest tests -q -p no:cacheprovider`. Initial run: **128 passed, 1 warning in 6.26s**. The warning was a cp949 subprocess-output reader decoding UTF-8 in `test_correction_check_fails_when_a_correction_is_pending`. A second run with `PYTHONUTF8=1` gave **128 passed in 6.24s**, no warnings. Both logs are retained. TEMP/TMP were restricted to `audit_evidence_claims/r2/replay_temp`; bytecode and pytest cache writes were disabled.",
"- Templates: all **5/5 evidence template bodies** pass when checked as generated prose after the normal `Scope:` removal. Full Scope-inclusive templates remain rejected. The France refusal template still fails generated checking with `no_antecedent: it` and `no_subject: no entity question matched`.",
"- Replayed original dictionary experiment: **7,610 index keys, 1,066 drugs, 2,634 unique stored multiword aliases; zero lost intended links**. There are two removed extraneous numeric `1 ×` links. `is a` no longer maps to ISATUXIMAB; AZD 9291, AZD9291, osimertinib mesylate, trastuzumab deruxtecan, pemetrexed disodium, and nab paclitaxel retain the prior intended links.",
"- The original dictionary experiment removes the abbreviation gate from the current linker; it does not load 0c441e0's method and therefore does not isolate the new punctuation change. The separate R2 linker audit must cover that difference.",
"- All old negative controls (safe, discontinued, not, contractions, no longer, un-/non- forms, explicit wrong pairs) remain rejected. A punctuation-only answer `...` still passes, but makes no biomedical claim; this was an R1 note-level probe rather than a reported blocker.",
"- No tracked files were edited. Only `audit_evidence_claims/r2/replay_*` files were written by this replay work.", ""])
(OUT / "replay_report.md").write_text("\n".join(report), encoding="utf-8")
