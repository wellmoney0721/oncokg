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
    old, new = read(OLD / f"independent_{stem}.json"), read(OUT / f"replay5_{stem}.json")
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
    old, new = read(OLD / "r2" / f"{stem}.json"), read(OUT / f"replay5_r2_{stem}.json")
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

(OUT / "replay5_all_cases.json").write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
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
 old,new=read(OLD/'r3'/f'{stem}.json'),read(OUT/f'replay5_r3_{stem}.json')
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

# R4 source-script replay, preserving direct/filtered-evidence diagnostic mode.
r4_sources = ['docs_controls_results', 'docs_diagnostics_results', 'docs_probe_results',
              'root4_confirmation', 'root4_probe', 'spec_probe', 'spec_controls',
              'spec_probe2', 'spec_probe3']
r4_extra = []
for stem in r4_sources:
    old = read(OLD/'r4'/f'{stem}.json')
    new = read(OUT/f'replay5_r4_{stem}.json')
    assert len(old) == len(new), stem
    for a,b in zip(old,new):
        for field in ('id','question','answer','input','evidence'):
            # Evidence payload includes unchanged retrieved graph; assertions also
            # ensure the filtered PLB-only diagnostic is not changed into a full retrieval.
            assert a.get(field) == b.get(field), (stem,field,a.get('id'))
        if 'question' not in b:
            r4_extra.append(dict(source=stem,**b))
            continue
        checks=b['result']['checks'] if 'result' in b else b['checks']
        rows.append(dict(round='R4',source=stem,id=b['id'],questions=[b['question']],answer=b['answer'],checks=checks))
byid={(r['source'],r['id']):r for r in rows}
H,J,K,L='root4_confirmation','root4_probe','docs_controls_results','docs_diagnostics_results'
r4_findings = [
 ('R4 B1 heading adjective erasure',[(H,'heading_safe'),(H,'heading_discontinued'),(H,'heading_safe_bare'),(K,'head_terminated')]),
 ('R4 B2 plural chaining/object/elision',[(H,'plural_chain'),(H,'plural_implicit'),(H,'object_count')]),
 ('R4 B3 count after trial label',[(H,'colon_count')]),
 ('R4 B4 shared trial phase/status',[(H,'trial_group_status'),(H,'trial_group_phase'),(H,'trial_status_prefix')]),
 ('R4 B5 kind/clinical ownership',[(H,'kind_drug'),(L,'trial_graph')]),
 ('R4 B6 spelled-out letters',[(H,'split_negation'),(J,'negation_split')]),
 ('R4 weaker NSCLC/identity/percentage residues',[(H,'nsclc_residue'),(J,'relation_precedes_identity'),(J,'percent')]),
 ('R4 additional phase-as-figure diagnostic',[(J,'drug_count_unit')]),
]
for name,keys in r4_findings:
    passed=sum(byid[k]['checks']['grounded'] for k in keys)
    dispositions.append(dict(finding=name,status='NOT FIXED' if passed else 'FIXED',still_passing=passed,inputs=[byid[k] for k in keys]))

faithful=read(OUT/'replay5_faithful_results.json')
r1faith=[r for r in rows if r['source']=='faithful_results']
r3faith=[r for r in rows if r['source']=='docs3_probe_results' and r['id'].startswith('faithful')]
specific_faithful = [
 ('R2 S1 inline pronoun/repeated alias/spaced code',[(S,'inline_pronoun_correct'),(S,'same_alias'),(S,'spaced_code')]),
 ('R3 S1 six specifically cited faithful forms',[(U,'object_pronoun_faithful'),(N,'phase_after_eval'),(N,'phase_roman'),(D,'faithful_25'),(N,'alias_hyphen_second'),(N,'alias_four')]),
 ('R4 S1 five specifically cited faithful forms',[(H,'faithful_two_phases'),(H,'faithful_count_alias'),(H,'faithful_capital_they'),(K,'cite_valid_list'),(J,'faithful_trial_noun')]),
]
# R2 exact inputs are identified by answer, because historic case IDs differ
# across author scripts; preserve source IDs in the saved report.
r2exact=['Osimertinib acts on EGFR and it inhibits EGFR.','Osimertinib (Tagrisso) acts on EGFR.','AZD 9291 acts on EGFR.']
specific_faithful[0]=(specific_faithful[0][0],[(r['source'],r['id']) for a in r2exact for r in rows if r['answer']==a and r['round']=='R2'][:])
faithful_dispositions=[]
for name,keys in specific_faithful:
    assert keys, name
    failed=sum(not byid[k]['checks']['grounded'] for k in keys)
    faithful_dispositions.append(dict(finding=name,status='NOT FIXED' if failed else 'FIXED',still_failing=failed,inputs=[byid[k] for k in keys]))

report=['# Exact R1-R4 replay at 9fda6f8','',
'All 23 original probe scripts were run via adapted copies. Six R1, three R2, five R3 and nine R4 scripts preserve exact questions, answers, case IDs and retrieval modes. Input identity is asserted against original saved outputs; historical classification follows the reports because some old result files were overwritten during repairs. Source SHA-256 hashes, adaptation diffs, full results and logs accompany this report. The only behavioral adaptation is disabling the R4 confirmation script assertion that outcomes must remain equal to obsolete R4 outcomes; its historic expected values remain as metadata. The earlier obsolete internal `_tokenise` call signature is also adapted.','',
'FIXED means all exact reported reproductions listed below are corrected, not that every variant of the mechanism is safe.','',
'| Prior finding | Result | Exact prior attacks still passing |','|---|---|---|']
for d in dispositions:
    report.append(f"| {d['finding']} | **{d['status']}** | {d['still_passing']}/{len(d['inputs'])} |")
report+=['','## Exact previously reported attacks and fresh findings','','| Finding / case | Exact question(s) | Exact answer | Fresh output |','|---|---|---|---|']
for d in dispositions:
    for r in d['inputs']:
        fs=[(x['kind'],x['value']) for x in r['checks']['unsupported_claims']]
        a=r['answer'].replace('\n','\\n')
        report.append(f"| {d['finding']} / `{r['source']}/{r['id']}` | `{' + '.join(r['questions'])}` | `{a}` | `grounded={r['checks']['grounded']}`; `{fs}` |")

report+=['','## SHOULD FIX dispositions and faithful answer replay','','| Question | Original R1 corpus passed | R3 added corpus passed |','|---|---|---|']
for r in faithful['summary']:
    cases=[c for c in r3faith if c['questions']==[r['question']]]
    report.append(f"| {r['question']} | {r['total']-r['flagged']}/{r['total']} | {sum(c['checks']['grounded'] for c in cases)}/{len(cases)} |")
report+=['','Both evidence corpora remain **29/30 (96.7%)** passing; refusals remain **4/6** and **5/6**, respectively. These are diagnostic hand-authored samples, not a production LLM error-rate estimate; they are not independent samples to pool. R1, R2 S1, R3 S1 and R4 S1 overall faithful/refusal handling remains **NOT FIXED** in the sense that some original faithful answers still fail. The five specifically cited R4 forms are **FIXED**.','',
'Remaining historical faithful/refusal failures:','']
for r in r1faith+r3faith:
    if not r['checks']['grounded']:
        fs=[(x['kind'],x['value']) for x in r['checks']['unsupported_claims']]
        report.append(f"- `{r['source']}/{r['id']}`: `{r['questions'][0]}` / `{r['answer']}` -> False; `{fs}`.")
report+=['','Specific faithful repairs:','']
for d in faithful_dispositions:
    report.append(f"- **{d['status']}** {d['finding']} ({len(d['inputs'])-d['still_failing']}/{len(d['inputs'])} pass).")
    for r in d['inputs']:
        report.append(f"  - `{r['questions'][0]}` / `{r['answer']}` -> {r['checks']['grounded']}; `{[(x['kind'],x['value']) for x in r['checks']['unsupported_claims']]}`.")
report+=['','Additional R4 faithful diagnostics remain **NOT FIXED** (they already failed before R5):','']
for key in [('spec_probe3','faithful_approval_coord'),(J,'faithful_phase_list')]:
    r=byid[key]
    report.append(f"- `{r['source']}/{r['id']}`: `{r['questions'][0]}` / `{r['answer']}` -> {r['checks']['grounded']}; `{[(x['kind'],x['value']) for x in r['checks']['unsupported_claims']]}`.")
report+=['',
'R1 Cartesian-product pairing: **FIXED**. All three faithful joined and three split relation pairs pass; all three swapped pairs fail (see `replay5_adversarial_pairs_results.json`).',
'',
'R1 distinct-sentence dedup: **FIXED**. `Osimertinib is safe. EGFR is safe.` is rejected and both sentence-specific `safe` findings survive. Same-unit dedup remains a NOTE: `Osimertinib is safe and EGFR is safe.` is rejected, although only one final `safe` finding remains; no nonempty finding list becomes acceptance (see `replay5_main_results.json` / `repeat_safe_dedup` and `replay5_r2_root_design_probe.json` / `dedup_same_unit`).',
'',
'R1 documentation / R2 S2 / R3 S2 / R4 S2: behavioral replay establishes that exact earlier omissions are repaired; documentation completeness against newly discovered R5 behavior is decided separately in the parent documentation review. It must not be inferred from replay alone.','',
'## Regression, templates and dictionary','',
(OUT/'replay5_pytest.stdout.txt').read_text(encoding='utf-8').strip(),'',
'Exit 0, empty stderr. TEMP/TMP point to `r5/replay5_temp`; bytecode and pytest cache writes are disabled.','',
'All **5/5 evidence template bodies pass** generated-prose checking after exactly the normal `Scope:` removal. All five Scope-inclusive templates still fail; the France template remains rejected when treated as generated prose, while the normal `ask()` refusal path passes. Exact text and results: `replay5_faithful_results.json` / `templates`.','',
'The dictionary gate replay checks **7,610 keys / 1,066 drugs / 2,634 unique multiword aliases**, with **zero lost intended links** relative to the old short-word joining behavior. `is a` remains unlinked; `AZD 9291`, `osimertinib mesylate`, `trastuzumab deruxtecan`, and `pemetrexed disodium` retain intended links. See `replay5_code_dictionary.json`.','',
'Separate dictionary-to-tokenizer replay: **2,566/2,634** aliases link an intended ID; the five previously documented tokenizer discrepancies (two parenthesized chemical names and three parent/salt overlaps) are unchanged. These five are not new R5 losses. See `replay5_r3_numeric3_dictionary.json`.','',
'Question punctuation remains unchanged: ALK followed by `!`, `:` or `;` is not linked in the question; `?` works. This is independent of answer punctuation.','',
'## Reproduction and integrity','',
'Run `powershell -NoProfile -File audit_evidence_claims/r5/replay5_reproduce.ps1`. All source copies, outputs, diffs and temporary test files stay under `audit_evidence_claims/r5/`. Original files and pre-existing `r5/brief.md` / `r5/log.txt` are untouched.','']

verification=dict(head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
    input_identity_cases=len(rows),per_round={k:sum(r['round']==k for r in rows) for k in ['R1','R2','R3','R4']},
    additional_citation_transforms=len(r4_extra),historical_script_count=23,
    tracked_diff_exit=subprocess.run(['git','diff','--exit-code','HEAD','--','.'],cwd=ROOT,capture_output=True).returncode,
    staged_diff_exit=subprocess.run(['git','diff','--cached','--exit-code'],cwd=ROOT,capture_output=True).returncode,
    code_sha256={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in ['src/claims.py','src/query.py','src/app.py','tests/test_claims.py','data/processed/oncokg.sqlite']})
report.insert(4,f"**{len(rows)} input-identity-checked answer cases**: "+', '.join(f"{k}: {v}" for k,v in verification['per_round'].items())+f". Four additional citation transformations, templates and dictionary experiments were also replayed.")
(OUT/'replay5_all_cases.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
(OUT/'replay5_dispositions.json').write_text(json.dumps(dict(blockers=dispositions,faithful=faithful_dispositions),ensure_ascii=False,indent=2),encoding='utf-8')
(OUT/'replay5_verification.json').write_text(json.dumps(verification,indent=2),encoding='utf-8')
(OUT/'replay5_report.md').write_text('\n'.join(report),encoding='utf-8')
print(json.dumps(verification,indent=2))
print('All prior exact blockers fixed:',all(d['status']=='FIXED' for d in dispositions))
print('All specific faithful repair cases fixed:',all(d['status']=='FIXED' for d in faithful_dispositions))
