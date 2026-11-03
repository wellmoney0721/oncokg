import json, sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2] / "src"))
from app import Engine
engine=Engine()
corpus = [
("Which companies are developing osimertinib?", [
"AstraZeneca is a sponsor of trials evaluating osimertinib.",
"Osimertinib is being tested in trials sponsored by AstraZeneca.",
"AstraZeneca leads 14 trials investigating osimertinib.",
"For osimertinib, the graph lists AstraZeneca as a trial sponsor.",
"Sponsors of osimertinib trials:\n- AstraZeneca\n- Eli Lilly",
"AstraZeneca sponsors 14 trials evaluating osimertinib, and Eli Lilly sponsors 2 trials evaluating osimertinib."
]),
("What trials evaluate Tagrisso?", [
"NCT03909334 evaluates osimertinib.",
"Osimertinib is being tested in NCT03909334.",
"NCT03909334 is a phase 2 trial evaluating osimertinib and is active, not recruiting.",
"NCT07680790 is a phase 3 trial evaluating Tagrisso.",
"Trials evaluating osimertinib include:\n- NCT03909334\n- NCT07680790",
"NCT03535363 was a phase 1 trial of osimertinib and has completed."
]),
("What does osimertinib target?", [
"Osimertinib acts on EGFR.",
"Osimertinib is an inhibitor of EGFR.",
"EGFR is inhibited by osimertinib.",
"The target of osimertinib is EGFR.",
"Osimertinib inhibits EGFR, according to the retrieved evidence.",
"Reported mechanism:\n- Osimertinib: inhibition of EGFR."
]),
("Which drugs act on ALK?", [
"Lorlatinib and crizotinib act on ALK.",
"ALK is targeted by alectinib, brigatinib and ceritinib.",
"Agents acting on ALK:\n- LORLATINIB\n- CRIZOTINIB\n- ALECTINIB",
"Crizotinib acts on ALK and has 15 NSCLC trials in this graph.",
"CONTELTINIB acts on ALK with a maximum stage of phase 1/2.",
"The graph lists lorlatinib, crizotinib and alectinib as drugs that act on ALK."
]),
("What is AstraZeneca running in NSCLC?", [
"AstraZeneca sponsors NSCLC trials evaluating osimertinib and carboplatin.",
"Osimertinib is being tested in NSCLC trials sponsored by AstraZeneca.",
"AstraZeneca is the sponsor of 14 NSCLC trials of osimertinib and 10 NSCLC trials of carboplatin.",
"AstraZeneca supports trials studying osimertinib in NSCLC.",
"AstraZeneca sponsors trials of these NSCLC drugs:\n- OSIMERTINIB\n- CARBOPLATIN\n- GEFITINIB",
"The graph lists AstraZeneca as a sponsor of NSCLC trials evaluating durvalumab."
]),
("What is the capital of France?", [
"This graph cannot answer that question.",
"No evidence was retrieved for that question.",
"The graph covers NSCLC drugs and trials, so it cannot answer this question.",
"There is no supporting evidence in this graph.",
"The question is outside the scope of this graph.",
"I cannot determine the capital of France from the retrieved evidence."
])]
results=[]
templates=[]
for qi,(question,answers) in enumerate(corpus,1):
  template=engine.ask(question)
  prose=template['answer'].split('\nScope:')[0]
  template_out=engine.check(question,prose)
  templates.append({'question':question,'input':prose,'normal_ask_checks':template['checks'],'prose_generated_checks':template_out['checks'],'full_template_input':template['answer'],'full_template_checks':engine.check(question,template['answer'])['checks'],'evidence':template['evidence']})
  for ai,answer in enumerate(answers,1):
    out=engine.check(question,answer)
    results.append({'id':f'Q{qi}P{ai}','question':question,'answer':answer,'checks':out['checks'],'retrieved_count':out['evidence_count']})
summary=[]
for qi,(question,answers) in enumerate(corpus,1):
  rows=[r for r in results if r['question']==question]
  summary.append({'question':question,'total':len(rows),'flagged':sum(not r['checks']['grounded'] for r in rows),'refusal_question':qi==6})
out={'method':'Hand-authored six plausible faithful phrasings per demo question; not statistical LLM distribution. Refusal case kept separate from evidence paraphrases.','summary':summary,'cases':results,'templates':templates}
Path(__file__).with_name('replay3_faithful_results.json').write_text(json.dumps(out,indent=2,ensure_ascii=False),encoding='utf-8')
for row in summary: print(json.dumps(row))
for r in results:
 print(r['id'],r['checks']['grounded'],r['answer'].replace('\n','\\n'),[(x['kind'],x['value']) for x in r['checks']['unsupported_claims']])
print('TEMPLATES')
for t in templates: print(t['question'],t['prose_generated_checks']['grounded'],[(x['kind'],x['value']) for x in t['prose_generated_checks']['unsupported_claims']])
