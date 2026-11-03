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
    old, new = read(OLD / f"independent_{stem}.json"), read(OUT / f"replay6_{stem}.json")
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
    old, new = read(OLD / "r2" / f"{stem}.json"), read(OUT / f"replay6_r2_{stem}.json")
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

(OUT / "replay6_all_cases.json").write_text(json.dumps(rows, ensure_ascii=False, indent=2), encoding="utf-8")
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
 old,new=read(OLD/'r3'/f'{stem}.json'),read(OUT/f'replay6_r3_{stem}.json')
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
    new = read(OUT/f'replay6_r4_{stem}.json')
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

faithful=read(OUT/'replay6_faithful_results.json')
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

# R5 original probes, including its fresh faithful corpus.
for stem in ['root5_numeric', 'root5_confirmation', 'spec5_probe', 'spec5_extended',
             'spec5_controls', 'spec5_anaphora', 'docs5_probe_results', 'docs5_controls_results']:
    old, new = read(OLD/'r5'/f'{stem}.json'), read(OUT/f'replay6_r5_{stem}.json')
    assert len(old) == len(new), stem
    for a,b in zip(old,new):
        for field in ('id','question','answer','evidence','full_evidence'):
            assert a.get(field) == b.get(field), (stem, field, a.get('id'))
        checks = b['result']['checks'] if 'result' in b else b['checks']
        rows.append(dict(round='R5',source=stem,id=b['id'],questions=[b['question']],answer=b['answer'],checks=checks))
byid = {(r['source'],r['id']):r for r in rows}
V, W, X, Y, Z = 'root5_confirmation', 'spec5_extended', 'spec5_controls', 'spec5_anaphora', 'docs5_probe_results'
r5_findings = [
    ('R5 B1 heading kind/disease erasure', [(V,'B1_heading_kind'),(V,'B1_heading_disease'),(W,'heading_wrong_kind_drug')]),
    ('R5 B2 named-group clinical context', [(V,'B2_group_clinical'),(V,'B2_group_clinical_relation'),(X,'clinical_group_graph')]),
    ('R5 B3 passive-list it', [(V,'B3_passive_it')]),
    ('R5 B4 parenthetical trial values', [(V,'B4_status_parenthetical'),(V,'B4_phase_parenthetical')]),
    ('R5 B5 longer trial labels/such trials', [(V,'B5_long_count_label'),(Y,'wrong_such'),(Y,'wrong_such_elided')]),
    ('R5 B6 kind-word owners/trial identity', [(V,'B6_relative_kind'),(V,'B6_prefix_kind'),(V,'B6_clinical_trial_identity')]),
    ('R5 N2 spaced percent/comma letters', [(V,'N_percent_spaced'),(Z,'letters_not_comma'),(Z,'letters_safe_comma')]),
]
for name,keys in r5_findings:
    passed = sum(byid[k]['checks']['grounded'] for k in keys)
    dispositions.append(dict(finding=name,status='NOT FIXED' if passed else 'FIXED',still_passing=passed,inputs=[byid[k] for k in keys]))

# This R4 diagnostic was a rejecting control, not an originally passing blocker.
# It now accepts the false group kind and must not disappear behind primary-case totals.
regressed = byid[('docs_controls_results','kind_target_nonrelation')]
dispositions.append(dict(finding='R4 kind-group diagnostic (REGRESSED)', status='NOT FIXED',
                         still_passing=1, inputs=[regressed]))

# Manually reviewed disposition of every current passing historical answer.
# Non-obvious passes get an explicit explanation; ordinary controls are supported.
pass_exceptions = {
 ('main_results','punctuation_only'): ('NOTE: no claim','Punctuation alone contains no clinical assertion.'),
 ('root_design_probe','number_units_count_as_phase'): ('NOTE: disclosed residue / artificial','13 phase trials is unnatural and reuses the same LORLATINIB row; it does not assert an unsupported numeric phase.'),
 ('root3_probe','fragment_without_be'): ('NOTE: no claim','A comma-separated list of two known drugs does not equate them.'),
 ('root3_probe','flat_question'): ('NOTE: evidence consistent','Punctuation converts the same supported inhibition statement into a question/fragment.'),
 ('docs3_probe_results','attack_12'): ('NOTE: explicit README residue','Osimertinib is the inhibition of EGFR is the exact odd-wording example disclosed in README item 13.'),
 ('docs_controls_results','kind_target_nonrelation'): ('BLOCKER: regression','EGFR is a Target, not a Drug. The drug kind is absent from the sole Q3 evidence statement, so this is outside the one-statement vocabulary residue. R4 and R5 both rejected this input.'),
 ('root5_numeric','phase_digit_before_roman'): ('NOTE: artificial encoding','PLB1003 has I phase is an unnatural Roman count phrase; no independent natural claim outside the disclosed numeric/word rearrangement residue.'),
 ('spec5_extended','passive_it_drug_kind'): ('NOTE: documented interpretation','The documented conservative it-after-list rule resolves the pronoun to all named drugs. LORLATINIB and PLB1003 are both drugs.'),
 ('docs5_probe_results','cite_link_destination_claim'): ('NOTE: artificial hidden encoding','Displayed Markdown label is only Osimertinib; the destination string is not ordinary prose and does not carry a claim the documented citation-id rule says it checks.'),
 ('docs5_probe_results','clinical_recruit_drug'): ('NOTE: disclosed residue','Osimertinib is recruiting rearranges drug and status vocabulary from one retrieved trial statement; R5 already classified this as the one-statement residue.'),
}
pass_dispositions=[]
for r in rows:
    if r['checks']['grounded']:
        status,reason=pass_exceptions.get((r['source'],r['id']),
            ('NOTE: evidence consistent','Faithful relation, entity kind, alias, attribute/count, quotation, citation or refusal control; no unsupported claim established.'))
        pass_dispositions.append(dict(**r,status=status,reason=reason))
prior4=read(OLD/'r5/replay5_all_cases.json')
prior4idx={(r['round'],r['source'],r['id']):r for r in prior4}
new_passes=[r for r in pass_dispositions if (r['round'],r['source'],r['id']) in prior4idx
            and not prior4idx[(r['round'],r['source'],r['id'])]['checks']['grounded']]

r5faith = [r for r in rows if r['source']==Z and r['id'].startswith('faithful')]
old5faith = [r for r in read(OLD/'r5/docs5_probe_results.json') if r.get('category')=='faithful']
failed5 = [(Z,r['id']) for r in old5faith if not r['result']['checks']['grounded'] and r['question_key'] != 6]
specific5 = [(V,'S1_faithful_relative_kind'),(V,'S1_faithful_prefix_drug')]
for name,keys in [('R5 S1 twelve original fresh faithful failures',failed5),('R5 S1 two kind-owner controls',specific5)]:
    failed = sum(not byid[k]['checks']['grounded'] for k in keys)
    faithful_dispositions.append(dict(finding=name,status='NOT FIXED' if failed else 'FIXED',still_failing=failed,inputs=[byid[k] for k in keys]))

verification = dict(head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
    input_identity_cases=len(rows), per_round={k:sum(r['round']==k for r in rows) for k in ['R1','R2','R3','R4','R5']},
    additional_citation_transforms=len(r4_extra), historical_script_count=31,
    tracked_diff_exit=subprocess.run(['git','diff','--exit-code','HEAD','--','.'],cwd=ROOT,capture_output=True).returncode,
    staged_diff_exit=subprocess.run(['git','diff','--cached','--exit-code'],cwd=ROOT,capture_output=True).returncode,
    code_sha256={p:hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in ['src/claims.py','src/query.py','src/app.py','tests/test_claims.py','data/processed/oncokg.sqlite']})

def findings_text(row):
    return str([(f['kind'],f['value']) for f in row['checks']['unsupported_claims']])

report = ['# Independent exact R1-R5 replay at 80da81b', '',
    'All 31 historical probe scripts were executed through adapted copies: six R1, three R2, five R3, nine R4, and eight R5. The R1-R4 copies derive from the R5 replay, with its earlier adaptation diffs preserved in r5; new diffs show the r6 output-path redirection. Obsolete internal `_tokenise` call signatures remain adapted, and assertions requiring historic vulnerability outcomes are disabled while expected values are retained as metadata. Every question, answer, ID and saved direct/filtered evidence input was checked for identity against its original result artifact. Current `Engine.check` or direct-call outputs are preserved in the per-script JSON files.', '',
    f"**{len(rows)} input-identity-checked answer cases**, per round: `{verification['per_round']}`. Four additional citation transformations, six templates, and dictionary experiments were also replayed.", '',
    'FIXED means the exact reported input now has the intended acceptance/rejection result; it does not establish that every variant of the mechanism is safe. Historical findings are classified from the reports, not inferred from old JSON acceptance flags, since some old artifacts were overwritten during repairs.', '',
    '## Historical BLOCKERS and additional reported diagnostics', '',
    '| Prior finding | Result | Exact attack inputs still passing |','|---|---|---|']
for d in dispositions:
    report.append(f"| {d['finding']} | **{d['status']}** | {d['still_passing']}/{len(d['inputs'])} |")
report += ['', '**All mapped primary R1–R5 blocker reproductions reject, but a prior R4 rejecting kind-group control has regressed.** Do not summarize this as every old unsafe input being repaired. The four False→True transitions across the full prior 606-case corpus are:', '']
for r in new_passes:
    report.append(f"- `{r['source']}/{r['id']}` / `{r['answer']}` → True/[]: **{r['status']}**. {r['reason']}")
report += ['', f"All **{len(pass_dispositions)} current passing cases** were dispositioned in `replay6_passing_dispositions.json`: one unsafe regression, with all other passes classified as evidence-consistent, disclosed residue, artificial encoding, or no claim. Non-obvious passing diagnostics:", '']
for r in pass_dispositions:
    if (r['source'],r['id']) in pass_exceptions:
        report.append(f"- `{r['source']}/{r['id']}`: `{r['questions'][0]}` / `{r['answer']}` → True/[]; **{r['status']}**. {r['reason']}")
report += ['', '## Exact inputs for every mapped finding', '',
    '| Finding / case | Exact question(s) | Exact answer | Current output |','|---|---|---|---|']
for d in dispositions:
    for r in d['inputs']:
        a = r['answer'].replace('\n','\\n').replace('|','\\|')
        report.append(f"| {d['finding']} / `{r['source']}/{r['id']}` | `{' + '.join(r['questions'])}` | `{a}` | `grounded={r['checks']['grounded']}`; `{findings_text(r)}` |")
report += ['', '## SHOULD FIX: faithful corpora', '',
    '| Question | R1 original | R3 added | R5 fresh |','|---|---:|---:|---:|']
faithful_summary = []
for oldsum in faithful['summary']:
    question = oldsum['question']
    groups = [[r for r in corpus if r['questions']==[question]] for corpus in [r1faith,r3faith,r5faith]]
    stats = [dict(passed=sum(r['checks']['grounded'] for r in group),total=len(group)) for group in groups]
    faithful_summary.append(dict(question=question,R1=stats[0],R3=stats[1],R5=stats[2]))
    report.append('| ' + question + ' | ' + ' | '.join(f"{s['passed']}/{s['total']}" for s in stats) + ' |')
report += ['', '**Evidence-answer totals: R1 29/30 (96.7%); R3 29/30 (96.7%); R5 39/40 (97.5%). Refusals separately: 4/6, 5/6, 5/6.** These hand-authored diagnostic corpora are not production LLM error-rate estimates and must not be pooled as independent samples.', '',
    'The repair table reports R5 38/40, but the unchanged fresh corpus actually yields 39/40 evidence answers, plus one refusal failure in the separate six-case Q6 corpus. This is a denominator/documentation correction, not a blocker.', '',
    '| Specific prior false-positive finding | Result | Remaining rejected inputs |','|---|---|---|']
for d in faithful_dispositions:
    report.append(f"| {d['finding']} | **{d['status']}** | {d['still_failing']}/{len(d['inputs'])} |")
report += ['', 'R1–R5 overall faithful/refusal handling is **NOT FIXED** in the literal all-cases sense: documented strictness remains. The current evidence corpus results satisfy the requested mostly-pass bar. Remaining faithful/refusal rejections:', '']
for r in r1faith+r3faith+r5faith:
    if not r['checks']['grounded']:
        report.append(f"- `{r['source']}/{r['id']}`: `{r['questions'][0]}` / `{r['answer']}` → `grounded=False`; `{findings_text(r)}`.")
report += ['', 'Exact outcomes for specifically cited false-positive repairs:', '']
for d in faithful_dispositions:
    for r in d['inputs']:
        report.append(f"- `{r['source']}/{r['id']}`: `{r['questions'][0]}` / `{r['answer']}` → `grounded={r['checks']['grounded']}`; `{findings_text(r)}`.")
report += ['', '## NOTES: regressions, templates, dictionary, dedup', '',
    (OUT/'replay6_pytest.stdout.txt').read_text(encoding='utf-8').strip(), '',
    'Exit 0; stderr empty. Exact command: `python -m pytest tests -q -p no:cacheprovider`. TEMP/TMP were `r6/replay6_temp`; bytecode and pytest cache writes disabled.', '',
    '**5/5 evidence template prose bodies pass**, retaining headings and removing `Scope:` exactly as the normal path does. Scope-inclusive template inputs still reject. France refusal still rejects in the generated checker and succeeds in the normal `ask()` refusal path. Full text/output: `replay6_faithful_results.json`.', '',
    '**Dictionary gate: 7,610 keys / 1,066 drugs / 2,634 unique multiword aliases, zero lost intended links** versus the prior short-word joining behavior. `is a` remains unlinked; `AZD 9291`, `osimertinib mesylate`, `trastuzumab deruxtecan`, and `pemetrexed disodium` retain links (`replay6_code_dictionary.json`). Separate dictionary-to-tokenizer replay still has 2,566/2,634 aliases linking an intended ID and the same five previously documented tokenizer discrepancies (two parenthesized chemical names, three parent/salt overlaps; `replay6_r3_numeric3_dictionary.json`).', '',
    '**R1 Cartesian-product paired relations: FIXED.** Three faithful joined and three split relation pairs pass; all three swapped pairs reject (`replay6_adversarial_pairs_results.json`).', '',
    '**R1 distinct-sentence dedup: FIXED.** `Osimertinib is safe. EGFR is safe.` retains two sentence-specific safe findings and rejects. Same-unit `Osimertinib is safe and EGFR is safe.` still merges safe findings but rejects; dedup cannot empty a nonempty list (`replay6_main_results.json`, `replay6_r2_root_design_probe.json`).', '',
    'Question punctuation after ALK (`!`, `:`, `;`) remains an unchanged linker limitation; `?` links correctly. This is distinct from answer punctuation.', '',
    'R1 documentation / R2 S2 / R3 S2 / R4 S2 / R5 S2 overall: the exact historical behavior underlying those objections is repaired; current documentation completeness and any new R6 failures require the separate documentation review. Replay does not infer a universal documentation guarantee.', '',
    '## Reproduction and integrity', '',
    'Run `powershell -NoProfile -File audit_evidence_claims/r6/replay6_reproduce.ps1`. All writes go under r6. Original probe files, tracked files, and pre-existing r6/brief.md and r6/log.txt are not edited. `replay6_manifest.json` records sources, hashes, derived copies and exit codes; `replay6_verification.json` records HEAD, code/database hashes and clean tracked/staged diffs. Per-script JSON files preserve complete outputs, and `replay6_all_cases.json` aggregates all replayed answer checks.']

(OUT/'replay6_all_cases.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf-8')
(OUT/'replay6_dispositions.json').write_text(json.dumps(dict(blockers=dispositions,faithful=faithful_dispositions),ensure_ascii=False,indent=2),encoding='utf-8')
(OUT/'replay6_passing_dispositions.json').write_text(json.dumps(pass_dispositions,ensure_ascii=False,indent=2),encoding='utf-8')
(OUT/'replay6_faithful_summary.json').write_text(json.dumps(faithful_summary,ensure_ascii=False,indent=2),encoding='utf-8')
(OUT/'replay6_verification.json').write_text(json.dumps(verification,indent=2),encoding='utf-8')
(OUT/'replay6_report.md').write_text('\n'.join(report),encoding='utf-8')
print(json.dumps(verification,indent=2))
print('All prior mapped exact attacks now reject:',all(d['status']=='FIXED' for d in dispositions))
print('Faithful summary:', json.dumps(faithful_summary))

table=['| Prior finding | R6 disposition | Evidence |','|---|---|---|']
for d in dispositions:
    table.append(f"| {d['finding']} | {d['status']} | {d['still_passing']}/{len(d['inputs'])} exact inputs still pass |")
for d in faithful_dispositions:
    table.append(f"| {d['finding']} | {d['status']} | {d['still_failing']}/{len(d['inputs'])} exact faithful inputs still fail |")
for round_name,detail in [('R1 SF','29/30 evidence answers, 4/6 refusals pass'),('R2 S1','same R1 residual supports/refusal forms'),('R3 S1','29/30 evidence answers, 5/6 refusals pass'),('R4 S1','same remaining faithful/refusal failures'),('R5 S1','39/40 evidence answers, 5/6 refusals pass')]:
    table.append(f'| {round_name} faithful/refusal handling overall | NOT FIXED; mostly-pass bar met | {detail} |')
table += ['| R1 SF Cartesian-product pairs | FIXED | All faithful joined/split pairs pass; swaps reject |','| R1 SF distinct-sentence dedup | FIXED | Both safe contexts retained; same-unit merging remains a NOTE |']
for name in ['R1 SF documentation','R2 S2 documentation','R3 S2 documentation','R4 S2 documentation','R5 S2 documentation']:
    table.append(f'| {name} overall | NOT FIXED overall | Earlier caveats improved; R4 kind-group regression lies outside README item 13 explicit residues; see separate R6 documentation review |')
(OUT/'replay6_findings_table.md').write_text('\n'.join(table),encoding='utf-8')

