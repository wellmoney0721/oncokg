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
    old, new = read(OLD / f"independent_{stem}.json"), read(OUT / f"replay4_{stem}.json")
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
    old, new = read(OLD / "r2" / f"{stem}.json"), read(OUT / f"replay4_r2_{stem}.json")
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

(OUT / "replay4_all_cases.json").write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
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
for stem in ['root3_probe','numeric3_probe','docs3_probe_results','docs3_focused_results']:
 old,new=read(OLD/'r3'/f'{stem}.json'),read(OUT/f'replay4_r3_{stem}.json')
 assert len(old)==len(new)
 for a,b in zip(old,new):
  for field in ('id','question','answer'):
   assert a[field]==b[field],(stem,field,a['id'])
  rows.append(dict(round='R3',source=stem,id=b['id'],questions=[b['question']],answer=b['answer'],checks=b['result']['checks']))
byid={(r['source'],r['id']):r for r in rows}
N,D,F,U='numeric3_probe','docs3_probe_results','docs3_focused_results','root3_probe'
findings += [
 ('R3 B1 plural pronouns',[(U,'pronoun_same_clause'),(U,'pronoun_two_sentences')]),
 ('R3 B2 count borrowing',[(N,'count_swap_tail'),(N,'count_coordinated'),(U,'count_shared_group')]),
 ('R3 B3 headings',[(U,'heading_sponsors_full'),(U,'heading_activators_full'),(U,'heading_with_alk')]),
 ('R3 B4 clinical/kind/identity',[(U,'clinical_trial_unsupported'),(U,'nsclc_trial_unsupported'),(U,'indication_drug'),(F,'focused_07'),(U,'zero_evidence_clinical'),(U,'fragment_drug_identity'),(U,'fragment_trial_identity')]),
 ('R3 weaker count-after-colon',[(U,'unknown_number_only')]),
 ('R3 weaker approval-in-NSCLC',[(U,'indication_approved_in')]),
 ('R3 weaker id-shaped citations',[(F,'focused_18'),(F,'focused_19'),(F,'focused_20')]),
]
dispositions=[]
for name,keys in findings:
 passed=sum(byid[k]['checks']['grounded'] for k in keys)
 dispositions.append(dict(finding=name,status='NOT FIXED' if passed else 'FIXED',still_passing=passed,inputs=[byid[k] for k in keys]))
report=['# Exact R1/R2/R3 replay at 2de10d9','','All fourteen historical probe scripts were run from adapted copies. Inputs (case ID, exact question(s), answer) are checked against prior saved outputs. Per-script adaptation diffs, original source hashes, fresh full outputs and return codes are saved next to this report. Only path adjustments and the obsolete internal R2 `_tokenise` argument signature were changed. Historical classifications follow the reports, not overwritten snapshots.','','FIXED means every exact previously reported reproduction is corrected; it is not a safety claim about related variants.','','| Prior finding | Result | Prior attack inputs still passing |','|---|---|---|']
for d in dispositions:
 report.append(f"| {d['finding']} | **{d['status']}** | {d['still_passing']}/{len(d['inputs'])} |")
report += ['','## Exact reported inputs and fresh outputs','','| Finding / case | Exact question(s) | Exact answer | Fresh output |','|---|---|---|---|']
for d in dispositions:
 for r in d['inputs']:
  fs=[(x['kind'],x['value']) for x in r['checks']['unsupported_claims']]
  a=r['answer'].replace('\n','\\n')
  report.append(f"| {d['finding']} / `{r['id']}` | `{' + '.join(r['questions'])}` | `{a}` | `grounded={r['checks']['grounded']}`; `{fs}` |")
# Diagnostic faithful corpus summaries.
faithful=read(OUT/'replay4_faithful_results.json')
r3faith=[r for r in rows if r['source']==D and r['id'].startswith('faithful')]
report += ['','## Prior faithful-corpus replay','','| Question | Original R1 corpus pass | R3 added corpus pass |','|---|---|---|']
for idx,r in enumerate(faithful['summary'],1):
 cases=[c for c in r3faith if c['questions']==[r['question']]]
 report.append(f"| {r['question']} | {r['total']-r['flagged']}/{r['total']} | {sum(c['checks']['grounded'] for c in cases)}/{len(cases)} |")
report += ['','Remaining faithful/refusal failures (diagnostic hand-authored samples, not production rates):','']
for r in [r for r in rows if r['source']=='faithful_results']+r3faith:
 if not r['checks']['grounded']:
  fs=[(x['kind'],x['value']) for x in r['checks']['unsupported_claims']]
  report.append(f"- `{r['source']}/{r['id']}`: `{r['questions'][0]}` / `{r['answer']}` -> False; `{fs}`.")
fixed_faithful=[(U,'object_pronoun_faithful'),(N,'phase_after_eval'),(N,'phase_roman'),(D,'faithful_25'),(N,'alias_hyphen_second'),(N,'alias_four')]
report+=['','R3 S1 exact specifically cited faithful repairs:','']
for key in fixed_faithful:
 r=byid[key]; fs=[(x['kind'],x['value']) for x in r['checks']['unsupported_claims']]
 report.append(f"- **{'FIXED' if r['checks']['grounded'] else 'NOT FIXED'}** `{r['questions'][0]}` / `{r['answer']}` -> `{r['checks']['grounded']}`; `{fs}`.")
report+=['','## Regression run','', (OUT/'replay4_pytest.stdout.txt').read_text(encoding='utf-8').strip(),'','Bytecode and pytest cache writes disabled; TEMP/TMP confined to `r4/replay4_temp`.','']
(OUT/'replay4_all_cases.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
(OUT/'replay4_dispositions.json').write_text(json.dumps(dispositions,ensure_ascii=False,indent=2),encoding='utf-8')
(OUT/'replay4_report.md').write_text('\n'.join(report),encoding='utf-8')
verification=dict(head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),input_identity_cases=len(rows),per_round={k:sum(r['round']==k for r in rows) for k in ['R1','R2','R3']},tracked_diff_exit=subprocess.run(['git','diff','--exit-code','HEAD','--','.'],cwd=ROOT,capture_output=True).returncode,staged_diff_exit=subprocess.run(['git','diff','--cached','--exit-code'],cwd=ROOT,capture_output=True).returncode,code_sha256={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in ['src/claims.py','src/query.py','tests/test_claims.py']})
(OUT/'replay4_verification.json').write_text(json.dumps(verification,indent=2),encoding='utf-8')
print(json.dumps(verification,indent=2))
print('All prior exact blockers fixed:',all(d['status']=='FIXED' for d in dispositions))
print('R1 faithful:',faithful['summary'])
print('R3 faithful:',sum(r['checks']['grounded'] for r in r3faith),len(r3faith))
extra=['','## Prior SHOULD FIX and NOTES dispositions','','| Prior finding | Disposition | Fresh evidence |','|---|---|---|',
'| R1 faithful paraphrases/refusals | **NOT FIXED overall**, much improved | Original corpus: 29/30 evidence answers and 4/6 refusals pass; exact remaining inputs are above. |',
'| R1 Cartesian-product pairing | **FIXED** | All three faithful same-sentence pairs and all three split-sentence pairs pass; all three swapped pairs fail (`replay4_adversarial_pairs_results.json`). |',
'| R1 distinct-sentence dedup | **FIXED** | `Osimertinib is safe. EGFR is safe.` is False and retains two sentence-specific `wording: safe` findings (`repeat_safe_dedup`). |',
'| R2 S1 faithful forms/refusals | **NOT FIXED overall** | The original supports/refusal failures remain. All three specifically reported inline-pronoun, repeated-alias and spaced-code inputs now pass. |',
'| R3 S1 faithful forms/refusals | **NOT FIXED overall**; all six specifically cited repairs **FIXED** | R3 corpus improves from 24/30 to 29/30 evidence answers and 2/6 to 5/6 refusals. Exact repaired and remaining inputs are above. |',
'| R1 docs / R2 S2 / R3 S2 | **NOT FIXED overall** under the parent round-4 audit | The old universal phrasing and exact historical attack omissions were repaired. New known residues found by the parent documentation/adversarial review require separate evaluation; the replay alone does not establish documentation completeness. |',
'',
'Exact repaired R2 S1 inputs (all Q3): `Osimertinib acts on EGFR and it inhibits EGFR.`, `Osimertinib (Tagrisso) acts on EGFR.`, `AZD 9291 acts on EGFR.` All now return `grounded=True`, `unsupported_claims=[]`.',
'',
'Same-unit dedup remains a NOTE: `Osimertinib is safe and EGFR is safe.` is False with one final safe finding although raw `check_claims` has two. Dedup does not turn the nonempty finding list into a pass.',
'',
'## Templates, dictionary and additional replay controls','',
'- All **5/5 evidence template bodies** pass generated-prose checking after the same `Scope:` removal used by the normal query path. The changed headings are included in these full prose inputs; they were not manually removed. All five Scope-inclusive templates still fail as in previous rounds. Full exact inputs and outputs are in `replay4_faithful_results.json` under `templates`.',
'- The sixth query is the France question. Its normal `ask()` refusal check passes, but checking its template as generated prose still fails. This unchanged limitation is separate from the five evidence templates.',
'- Dictionary gate: **7,610 keys / 1,066 drugs / 2,634 unique multiword aliases**, zero lost intended links. `is a` is unlinked; `AZD 9291`, `osimertinib mesylate`, `trastuzumab deruxtecan`, and `pemetrexed disodium` keep intended links (`replay4_code_dictionary.json`).',
'- Dictionary-to-tokenizer replay: **2,566/2,634** aliases link an intended ID; five unchanged tokenization discrepancies remain (two parenthesized chemical names and three parent/salt overlaps). `replay4_r3_numeric3_dictionary.json` and the R2 standards replay contain exact cases. This is not a new round-4 regression.',
'- Question punctuation is unchanged: `Which drugs act on ALK!`, `Which drugs act on ALK:`, and `Which drugs act on ALK;` link no target. The normal `?` works. Answer punctuation is a separate path; `Osimertinib acts on EGFR!` passes.',
'- Evidence-consistent prior diagnostic passes are NOTES, not blockers: `Osimertinib was inhibiting EGFR.`, `EGFR has been inhibited by osimertinib.`, `Osimertinib is an EGFR blocker.`, and `Osimertinib is evaluated at NCT03909334.`. The malformed `Osimertinib is the inhibition of EGFR.` reuses the sole supported statement and fits the stated one-statement rearrangement residue; it is not independently treated as an out-of-residue blocker.',
'- Original files were read only; all 14 copies, their logs/results/diffs and temporary test files are under `audit_evidence_claims/r4/`. `brief.md` and `log.txt` were not edited. Tracked/staged diffs remain empty.',
'',
'## Reproduction','',
'From the repository root, run `powershell -NoProfile -File audit_evidence_claims/r4/replay4_reproduce.ps1`. It reruns all 14 historical scripts and the 213-test regression command, then rebuilds this report and the input-identity assertions. No historical files are overwritten.',
'']
with (OUT/'replay4_report.md').open('a',encoding='utf-8') as handle: handle.write('\n'.join(extra))
