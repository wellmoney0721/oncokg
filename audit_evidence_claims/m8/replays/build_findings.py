"""Assemble complete historical finding index from round 7 and current evidence."""
from pathlib import Path
import json,re
OUT=Path(__file__).resolve().parent
prior=Path('audit_evidence_claims/m7/REPORT.md').read_text(encoding='utf8')
section=prior.split('## Earlier findings — FIXED / NOT FIXED per finding')[1].split('## Should-fix findings')[0]
rows=[];round_name=''
for line in section.splitlines():
 if line.startswith('### '):round_name=line[4:]
 if not line.startswith('| ') or '**FIXED' not in line and '**NOT FIXED' not in line:continue
 cells=line.strip().strip('|').split('|')
 finding=cells[0].strip();detail=cells[1].strip()
 detail=detail.replace('(names/','(').replace('(root_checks/','(../root_checks/').replace('(db_ui/','(../db_ui/')
 for fn in ['ui_harness_results.json','ui_assertions.json','ui_regressions.json','ui_m3_checks.json']:
  detail=detail.replace('(../db_ui/'+fn+')','(../demos_cost/'+fn+')')
 detail=detail.replace('(../db_ui/REPORT.md)','(../db_ui/db_assertions.json)').replace('(REPORT.md#reproduction-completeness)','(FINDINGS.md)')
 detail=detail.replace('(adapted_frozen_qa_relink_sweep.json)', '(adapted_frozen_qa_relink_sweep.json)')
 if finding.startswith('M5-S3'):
  detail='**FIXED for exact previous cost cases** — bounded predicate work and original plain-answer requests complete. Repeated-piece overhead also repaired; new cache-boundary failure is recorded separately below. [Original HTTP](../root_checks/perf_check_http.json), [current instrumentation](../demos_cost/perf_current.json).'
 if finding.startswith('M6-B1'):
  detail='**FIXED** — separate osimertinib retained; forbidden originator absent from QA. [Exact HTTP](../root_checks/confirm_http.json), [39-case matrix](focused_matrix.json).'
 if finding.startswith('M6-B2 U+'):
  detail='**FIXED** — all four original edge-punctuation inputs refuse, as do trial/sponsor QA. [Exact HTTP](../root_checks/confirm_http.json), [current focused stages](historical_focus.json).'
 if finding.startswith('M6-B2 supplementary'):
  detail='**FIXED** — parenthesized/bracketed suffixes and folded Unicode-hyphen cases now refuse; question-mark and quoted shortcut cases also refuse. [Historical matrix](historical_focus.json), [m7 attack HTTP](../m7_attacks/http_results.json).'
 if finding.startswith('M6-B3'):
  detail='**FIXED** — both parenthesized reversed qualifiers produce no centre or QA evidence. [Exact HTTP](../root_checks/carry_http.json), [stages](historical_focus.json).'
 if finding.startswith('M6 associated lone'):
  detail='**FIXED for all 19 non-M5-S2 historical lost aliases** — slash/joiner names restored; known M5-S2 still refuses. The current sweep separately records new isotope-token over-refusals. [Exact previous/current alias comparison](alias_regressions.json), [complete current sweep](adapted_names_m5_summary.json).'
 if finding.startswith('M6 split_2000'):
  detail='**FIXED for exact repeated-piece cost control** — current resolver skips no-drug pieces and deduplicates; the previous per-piece delay is gone. [Exact stress replay](../demos_cost/cost_stress.json), [old/current samples](../demos_cost/fresh_cost_comparison.json).'
 if finding.startswith('M5-S1 `Erlotinib'):
  detail='**FIXED** — original qualified comma/semicolon inputs preserve CHEMBL553; the simplified comma-list M7 regression is also repaired. [Exact HTTP](../root_checks/m5_http.json), [M7 controls](historical_focus.json).'
 if finding.startswith('M4 no-relink'):
  detail='**FIXED / retained** — exact frozen 1,648-input counterfactual, 64 identical / 1,560 metadata-only / 24 semantic differences / 0 errors; adapted matcher target is `_link`. [Result](adapted_frozen_qa_relink_sweep.json).'
 if finding.startswith('M6-S1 six'):
  detail='**FIXED for all six bare inputs** — intended stored IDs retained. [Current stages](historical_focus.json), [HTTP](../root_checks/alias_http.json).'
 if finding.startswith('M6-S1 prefixed'):
  detail='**NOT FIXED — current whole-input-only design consequence**. ENDOSTATIN prefixed QA still selects CHEMBL4297747 with 2 rows; Rapamycin prefixed QA CHEMBL413 with 5 rows. [Exact HTTP](../root_checks/alias_http.json), [direct QA](historical_focus.json).'
 if finding.startswith('M6 non-parenthetical'):
  detail='**NOT FIXED as original expectation; accepted current item-policy consequence** — `doxorubicin in nanoparticle and liposomal formulations` still selects doxorubicin after listing-word separation. [Exact HTTP](../root_checks/reverse_http.json).'
 detail=detail.replace('[Sweep](names_m5_summary.json)','[Sweep](adapted_names_m5_summary.json)')
 status='NOT FIXED' if detail.startswith('**NOT FIXED') else 'FIXED'
 rows.append({'round':round_name,'finding':finding,'status':status,'current_evidence':detail})
extra=[
 ('M7-B1','Whole-name refusal bypass: `bevacizumab-awwb?`, `bevacizumab-awwb!`, quoted form','FIXED','All return refusal/no centre; trial and sponsor QA zero. [Current stages](historical_focus.json), [original m7 HTTP replay](../m7_attacks/http_results.json).'),
 ('M7-B2','Wrappers and Unicode hyphens: `(bevacizumab-awwb)`, `[bevacizumab-awwb]`, U+2011 suffix and bio-similar','FIXED','All named inputs refuse after shared normalization and edge stripping; no originator QA. [Stages](historical_focus.json), [HTTP](../m7_attacks/http_results.json).'),
 ('M7-B3','Whitespace isotope: `89Zr trastuzumab`','FIXED','No centre; both QA forms have zero evidence. [Stages](historical_focus.json), [HTTP](../m7_attacks/http_results.json).'),
 ('M7-S1','Canonical equality too broad: `Erlotinib, hydrochloride`, `osimertinib,mesylate`, `is a`','FIXED','Respectively CHEMBL553, CHEMBL3353410 and not_found; actual exact aliases retain intended IDs. [Current controls](historical_focus.json), [HTTP](../m7_attacks/http_results.json).'),
 ('M7-S2','Lone exact stored names: `(E/Z)-AFATINIB`, `RO 09-1978/000`, `Anusol plus hc` and 19-alias set','FIXED','All 19 old non-M5-S2 losses restored; three named controls select CHEMBL1173655 / CHEMBL1773 / CHEMBL389621. [Exact previous/current comparison](alias_regressions.json), [HTTP](alias_http.json).'),
 ('M7-S3','Repeated identical-piece full resolver cost / queued ordinary map','FIXED','Exact old repeated-x controls and corresponding requests complete with materially reduced work. New distinct-drug workload and cache failure are separate. [Cost replay](../demos_cost/cost_stress.json), [comparison](../demos_cost/fresh_cost_comparison.json), [HTTP](../demos_cost/fresh_cost_http.json).')
]
for ident,finding,status,detail in extra:rows.append({'round':'M7','finding':ident+' '+finding,'status':status,'current_evidence':'**'+status+'** — '+detail})
OUT.joinpath('historical_findings_matrix.json').write_text(json.dumps(rows,ensure_ascii=False,indent=2),encoding='utf8')
lines=['# Round 8 historical reproduction report','','HEAD `ec4eede`. The exact named m1–m7 originator leaks and m7 list/name regressions are FIXED. Historical usability and explicit current-design qualifications remain individually recorded below. Newly found valid-alone over-refusals and a cache rollover exception are separate from those historical dispositions.','','## Execution, provenance and limits','',
'The source reports exist for m1 and m3–m7; `m2/REPORT.md` is absent. M2b findings are preserved in m3–m7 disposition tables and exercised by the inherited m2 scripts. This table retains every row of m7’s historical matrix and appends all six m7 findings.',
'',
'- [Reuse manifest](reuse_manifest.json): 30 original Python scripts relocated with output-path and fixed-port changes only. Own HTTP port was 8913; server lifecycles ended.',
'- [13-script run](replay_execution.json): 12 exit 0; the exact 7,511-key sweep aborts on the new application cache defect, preserved in [traceback](names_m5_attack_stdout.txt). A [documented per-case exception-record/retry adaptation](alias_sweep_adaptation.json) completes the exact 113 cases and all 7,511 keys, with one recorded exception and zero wrong-ID results. [Full adapted result](adapted_names_m5_attack.json).',
'- [Six original supplements](supplement_execution.json) exit 0: includes 106-case / 8-QA fresh probe and 11 reversed-qualifier probes. [All five original m1 scripts](m1_exact/execution.json) also exit 0, including unchanged-CLI HTTP and isolated retired-node HTTP fixture.',
'- [Old m7 focused script](m7_focus.py.stdout.txt) initially fails because `_whole_name` now needs `found`. [Mechanical signature adaptation](m7_focus_adaptation.json) preserves all 23 inputs and passes every expected centre; [result](adapted_m7_focus.json). The separate [26-case m6/m7 matrix](historical_focus.json) adds all newly repaired m7 findings and four prefixed-QA controls.',
'- Historical no-relink scripts patch `link_entities` and are now inert counterfactuals; they are rerun but not used as evidence of no-relink. The inherited meaningful adaptation patches `_link` and reuses the exact frozen 1,648-input m5 corpus: **64 identical / 1,560 metadata-only / 24 semantic / 0 errors**. [Result](adapted_frozen_qa_relink_sweep.json).',
'- Coverage: 62 original name inputs + 14 probes; 30 boundary inputs + 21 joiner aliases; 45 attacks + 37 QA + 2,584 multi-token aliases; 113 attacks + 7,511 unique alias keys; 49 confirmation inputs; 13 cross-item controls. The original 39-case finding matrix has only the accepted M5-S2 mismatch. [Matrix](focused_matrix.json).',
'- Parent DB replays: 6,469 centres, 22 relation/direction/type/role combinations, zero oracle errors; [19/19 assertions](../db_ui/db_assertions.json). UI sibling: [24/24 assertions](../demos_cost/ui_assertions.json), [36/36 exact demo responses](../demos_cost/ui_demo_compare.json). Generated markup/Node VM evidence is not browser paint or exploit execution certification. All timings outside the cost worker’s isolated run may include concurrent audit workload.',
'','## Every earlier finding: current disposition','']
last=None
for row in rows:
 if row['round']!=last:
  lines+=['### '+row['round'],'','| Finding / reproduction | Current result |','|---|---|'];last=row['round']
 lines.append('| '+row['finding']+' | '+row['current_evidence']+' |')
lines+=['','## New failures discovered by the historical scripts','','### Valid stored aliases newly refused or lost','','`566C` (ATOVAQUONE / CHEMBL1450), `9-ac` (9-AMINOCAMPTOTHECIN / CHEMBL274070), and `5ac` (AZACITIDINE / CHEMBL1489) now return no centre with Refused metadata. They are uniquely stored aliases, select their correct nodes with the exact previous query module, and their canonical IDs still draw live nodes. These are valid names alone in their input, not an intentionally dropped drug sharing a qualified item. [Exact previous-module comparison and controls](alias_regressions.json).',
'','`src/query.py:112-113` now treats any token accepted by `is_isotope_label` as a qualifying tracer; `_link` removes edge punctuation (`240-242`) before that predicate. `_whole_name` refuses to rescue any item that produced a refusal (`208-212`). The new broad token check therefore also covers code-like aliases; the source dictionary supplies a concrete stored-name premise rather than an external pharmacology inference. Separately, `5.BETA.,20-EPOXY-1,2.ALPHA.,4,7.BETA.` (CHEMBL428647) returns **not_found with no Refused hit**. It is a different exact-name failure: `_whole_name` removes its terminal period with `text.strip(" ?!.")` at `src/query.py:210`, then compares the resulting name against the unstripped stored alias at `215-216`. The exact previous query module accepts it and its canonical ID still works. This is not an isotope-token refusal. [Separate stored-name control](alias_regressions.json).',
'','The same 7,511-key sweep has 23 formerly linked aliases with no current Drug: accepted M5-S2, the four controls above, and 18 isotope-bearing names. The latter need product policy interpretation and are not all called defects here. Every one of the 19 non-M5-S2 losses reported at m7 is restored. No current wrong-ID result appears in this particular unique-key sweep. [Complete list](adapted_names_m5_summary.json).',
'','### Resolver cache clears the value before reading it','','The original alias sweep aborts at alias index 4,071 on `Gallium gozetotide ga-68`. Source `src/query.py:180-182` clears `_resolve_cache` when it grows past 4,096, then immediately accesses `_resolve_cache[piece]`. The exception is `KeyError`, and the recorded cache size after failure is 0. This is an application failure from a natural sequence, not a harness-signature issue. A catch-and-retry-only audit adaptation preserves the exception, then completes every original input after the application emptied its cache. [Original traceback](names_m5_attack_stdout.txt), [recorded failure](adapted_names_m5_summary.json), [separate actual HTTP confirmation](../demos_cost/cache_boundary_http.json).',
'','## Reproduction commands','','```text','python -B audit_evidence_claims/m8/replays/run_all.py','python -B audit_evidence_claims/m8/replays/adapted_names_m5_attack.py','python -B audit_evidence_claims/m8/replays/adapted_m7_focus.py','python -B audit_evidence_claims/m8/replays/historical_focus.py','python -B audit_evidence_claims/m8/replays/alias_regressions.py','```','','All new files are below m8; no application or tracked file was edited. The earlier scripts’ old-revision comparisons isolate the named methods or query module, while keeping current surrounding data/code. They are not claimed to recreate the entire old application.']
OUT.joinpath('FINDINGS.md').write_text('\n'.join(lines)+'\n',encoding='utf8')
print('historical finding rows',len(rows))
