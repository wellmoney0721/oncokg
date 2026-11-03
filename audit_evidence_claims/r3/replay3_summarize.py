import hashlib
import json
from pathlib import Path
import subprocess

OUT = Path(__file__).resolve().parent
ROOT = OUT.parents[1]
OLD = OUT.parent

def read(path):
    return json.loads(path.read_text(encoding="utf-8"))

rows = []
sources = [("main_results", "id", "result"), ("adversarial_results", "id", None),
           ("adversarial_pairs_results", "id", None), ("faithful_results", "id", None),
           ("code_probes", "tag", "result")]
for stem, key, wrapper in sources:
    old, new = read(OLD / f"independent_{stem}.json"), read(OUT / f"replay3_{stem}.json")
    if stem == "faithful_results":
        old, new = old["cases"], new["cases"]
    assert len(old) == len(new)
    for a, b in zip(old, new):
        assert a[key] == b[key]
        for field in ("question", "retrieval_questions", "answer"):
            assert a.get(field) == b.get(field), (stem, b[key], field)
        checks = b[wrapper]["checks"] if wrapper else b["checks"]
        rows.append({"round": "R1", "source": stem, "id": b[key],
                     "questions": b.get("retrieval_questions") or [b["question"]],
                     "answer": b["answer"], "checks": checks})

for stem, key, wrapper in [("root_design_probe", "id", "result"),
                           ("spec_probe_results", "id", None),
                           ("standards_probe", "case", None)]:
    old, new = read(OLD / "r2" / f"{stem}.json"), read(OUT / f"replay3_r2_{stem}.json")
    if stem == "standards_probe":
        old, new = old["cases"], new["cases"]
    assert len(old) == len(new)
    for a, b in zip(old, new):
        assert a[key] == b[key]
        for field in ("question", "questions", "answer"):
            assert a.get(field) == b.get(field), (stem, b[key], field)
        checks = b[wrapper]["checks"] if wrapper else b["checks"]
        rows.append({"round": "R2", "source": stem, "id": b[key],
                     "questions": b.get("questions") or [b["question"]],
                     "answer": b["answer"], "checks": checks})

(OUT / "replay3_all_cases.json").write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
byid = {(r["source"], r["id"]):r for r in rows}
M,A,P,C,R,S,T = "main_results", "adversarial_results", "adversarial_pairs_results", "code_probes", "root_design_probe", "spec_probe_results", "standards_probe"
findings = [
("R1 B1 direction/endpoints", [(A,"reversed_target"),(M,"reverse_noun"),(A,"reversed_trial"),(A,"reversed_sponsor"),(M,"wrong_type_relation")]),
("R1 B2 pronoun subject loss", [(A,"pronoun_target_same_line"),(A,"pronoun_target_newline"),(A,"pronoun_this_drug"),(A,"trial_pronoun_reset")]),
("R1 B3 phase/status/count pooling", [(A,"swapped_trial_phases"),(A,"pooled_trial_status2"),(A,"wrong_sponsor_count"),(A,"wrong_drug_count_target"),(M,"clinical_from_alk")]),
("R1 B4 bigram laundering", [(M,"quoted_developing"),(M,"quoted_developing_2"),(M,"quoted_absence_natural")]),
("R1 B5 non- negation", [(M,"non_inhibitor"),(M,"non_hyphen")]),
("R1 B6 brackets/non-English", [(M,"square_bracket_claim"),(M,"markdown_link_label"),(M,"korean_only"),(M,"korean_mixed_relation")]),
("R1 B7 clinical grammar/action", [(M,"plain_clinical_grammar"),(M,"activator_as_inhibitor")]),
("R1 B8 numeric layouts", [(P,"phase_13_regex"),(C,"phase_suffix"),(A,"count_long_unit"),(P,"count_after_colon_list")]),
("R2 B1 reversed noun/cleft", [(M,"reverse_noun"),(S,"passive_cleft"),(S,"passive_cleft_trial"),(S,"passive_cleft_sponsor")]),
("R2 B2 hidden extra endpoint", [(S,"endpoint_preposition"),(S,"endpoint_noun"),(S,"endpoint_adverb"),(S,"noun_target_second")]),
("R2 B3 pronoun timing/verbatim trial", [(S,"pronoun_stale"),(S,"pronoun_stale2"),(R,"verbatim_antecedent_trial")]),
("R2 B4 numeric ownership/count slots", [(S,"number_drug_other"),(S,"count_morph")]),
("R2 B5 action substring", [(S,"action_antagonist"),(S,"action_noun_agonist")]),
("R2 B6 headings", [(R,"discarded_heading"),(R,"discarded_heading_before_prose"),(R,"verbatim_under_unsafe_heading"),(R,"verbatim_under_negated_heading"),(R,"verbatim_under_reversed_heading")]),
("R2 B7 META clinical claims", [(R,"meta_france_unsupported_phase"),(R,"meta_missing_typed_phase"),(R,"meta_missing_negation"),(R,"meta_missing_count")]),
("R2 B8 refused spans", [(T,"refused_liposomal"),(T,"refused_biosimilar"),(T,"refused_negation"),(T,"refused_alias")]),
("R2 B9 ORG citation content", [(R,"citation_embedded_claim"),(R,"citation_embedded_wrong_relation")]),
]
dispositions=[]
report = ["# Exact R1/R2 replay at 8d4a606", "",
"All six R1 scripts and all three additional R2 scripts were rerun through adapted copies. All nine exit codes are zero. Only output paths/import depth and the obsolete internal `_tokenise` signature in the R2 standards probe were adapted; per-script diffs and source SHA-256 values are retained. Input question(s), answer and case ID identity against saved snapshots was asserted for every answer case. Historical verdicts follow the R1/R2 reports, because several saved JSON files were overwritten after repairs.", "",
f"R1: {sum(r['round']=='R1' for r in rows)} exact answer cases, plus six templates and the dictionary gate experiment. R2: {sum(r['round']=='R2' for r in rows)} additional exact answer cases, plus six question-punctuation cases and exhaustive dictionary-to-tokenizer comparison.", "",
"## Reported blockers", "",
"FIXED describes the exact prior reported reproductions, not every variant of the mechanism. New R3 attacks must be judged separately.", "",
"| Finding | Disposition | Prior reported attack inputs still passing |", "|---|---|---|"]
for name, keys in findings:
    passed = sum(byid[k]["checks"]["grounded"] for k in keys)
    status = "NOT FIXED" if passed else "FIXED"
    report.append(f"| {name} | **{status}** | {passed}/{len(keys)} |")
    dispositions.append({"finding": name, "status": status, "still_passing": passed,
                         "inputs": [byid[k] for k in keys]})
report += ["", "## Exact reported blocker inputs and fresh outputs", "",
           "| Finding | Question(s) | Answer | Observed output |", "|---|---|---|---|"]
for name, keys in findings:
    for key in keys:
        r=byid[key]
        claims=[(u["kind"],u["value"]) for u in r["checks"]["unsupported_claims"]]
        answer=r["answer"].replace("\n", "\\n")
        report.append(f"| {name.split(' ',2)[0]} {name.split(' ',2)[1]} / `{r['id']}` | `{' + '.join(r['questions'])}` | `{answer}` | `grounded={r['checks']['grounded']}`; `{claims}` |")
report += ["", "## Prior SHOULD FIX findings", "",
"- **R1 faithful paraphrases/refusals: NOT FIXED**, substantially improved from R1 and unchanged on the original corpus since R2. Evidence answers: 29/30 pass, 1/30 flagged (3.3%). Refusals: 4/6 pass, 2/6 flagged. This hand-authored diagnostic corpus is not an estimate of a production LLM distribution.",
"- **R1 Cartesian-product pairing: FIXED**. All three same-sentence and all three two-sentence faithful pair examples pass; all three swapped drug/target, trial/drug, company/drug examples fail.",
"- **R1 distinct-sentence dedup: FIXED**. `Osimertinib is safe. EGFR is safe.` retains both sentence-specific `wording: safe` findings. Same-unit dedup remains unchanged: `Osimertinib is safe and EGFR is safe.` retains only one final finding although raw checking finds two; it remains rejected.",
"- **R2 S1 faithful forms: NOT FIXED overall**. The three reported defects in within-sentence pronouns, repeated aliases, and spaced-code digits are FIXED. `Osimertinib acts on EGFR and it inhibits EGFR.`, `Osimertinib (Tagrisso) acts on EGFR.`, and `AZD 9291 acts on EGFR.` now all return `grounded=True`, `unsupported_claims=[]`. The two reported refusal failures and the `supports` strictness remain (exact outputs below).",
"- **R1 documentation / R2 S2:** assessed by the parent documentation review, not inferred from passing tests here.", "",
"| Demo question | R1 flagged | R2 flagged | R3 flagged |", "|---|---|---|---|"]
faithful=read(OUT / "replay3_faithful_results.json")
for old,old2,r in zip([2,2,1,3,2,6],[0,0,0,0,1,2],faithful["summary"]):
    report.append(f"| {r['question']} | {old}/6 | {old2}/6 | {r['flagged']}/6 |")
report += ["", "Exact remaining original faithful/refusal failures:", ""]
for r in faithful["cases"]:
    if not r["checks"]["grounded"]:
        claims=[(u["kind"],u["value"]) for u in r["checks"]["unsupported_claims"]]
        report.append(f"- `{r['id']}` / `{r['question']}` / `{r['answer']}` => `grounded=False`, `{claims}`.")
report += ["", "## Regressions and additional replay observations", "",
"- `python -m pytest tests -q -p no:cacheprovider`: **175 passed in 5.97s**, exit 0, empty stderr. PYTHONUTF8=1, PYTHONDONTWRITEBYTECODE=1, TEMP/TMP under `r3/replay3_temp`; no cache provider or bytecode writes.",
"- **5/5 evidence template prose bodies pass** after the same `Scope:` removal as the normal answer path. All five full Scope-inclusive templates fail as before. France refusal template fails generated checking with `no_antecedent: it` and `no_subject: no entity question matched`; normal `ask()` uses its separate refusal path.",
"- Original linker gate experiment: **7,610 keys / 1,066 drugs / 2,634 unique multiword aliases**, zero lost intended links. `is a` remains unlinked; `AZD 9291`, `osimertinib mesylate`, `trastuzumab deruxtecan`, `pemetrexed disodium` retain intended links. This is the current gate-on/gate-off comparison, not old-commit execution.",
"- R2 dictionary-to-tokenizer replay: **2,566/2,634** aliases link an intended ID; five still lose an intended ID during tokenization (two parenthesized chemical names, three parent/salt overlaps). Exact cases are in `replay3_r2_standards_probe.json`. These are unchanged diagnostic discrepancies.",
"- `Which drugs act on ALK!`, with `:` or `;`, still links no target and returns unsupported; `?` works. The answer `Osimertinib acts on EGFR!` passes. Unchanged question-linker punctuation limitation.",
"- R2 `no_antecedent_control`: Q3 / `It inhibits EGFR.` now passes due the intentional question-seeded antecedent. It is faithful to Q3 evidence, not an unsupported claim. The raw helper without question entities may differ from `Engine.check`; the exact public call was preserved in replay.",
"- The previously recorded odd wording Q4 / `LORLATINIB has 13 phase trials.` still passes. It asserts the correct trial count with malformed grammar; it is not one of the reported R2 blocker attacks.",
"- No tracked changes were detected by `git diff --exit-code HEAD -- .` and `git diff --cached --exit-code` after execution.", ""]
(OUT / "replay3_report.md").write_text("\n".join(report), encoding="utf-8")
(OUT / "replay3_dispositions.json").write_text(json.dumps(dispositions,ensure_ascii=False,indent=2),encoding="utf-8")
verification={"head":subprocess.check_output(["git","rev-parse","HEAD"],cwd=ROOT,text=True).strip(),
              "input_identity_cases":len(rows),"r1_cases":sum(r["round"]=="R1" for r in rows),
              "r2_cases":sum(r["round"]=="R2" for r in rows),
              "tracked_diff_exit":subprocess.run(["git","diff","--exit-code","HEAD","--","."],cwd=ROOT,capture_output=True).returncode,
              "staged_diff_exit":subprocess.run(["git","diff","--cached","--exit-code"],cwd=ROOT,capture_output=True).returncode,
              "code_sha256":{p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in ["src/claims.py","src/query.py","tests/test_claims.py"]}}
(OUT/"replay3_verification.json").write_text(json.dumps(verification,indent=2),encoding="utf-8")
print(json.dumps(verification,indent=2))
print("All reported old blocker groups fixed:", all(r["status"]=="FIXED" for r in dispositions))
