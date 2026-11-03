"""Summarize independently rerun DB/UI evidence and standards inspection."""
from pathlib import Path
import hashlib,json,socket,subprocess
out=Path(__file__).resolve().parent
root=out.parents[2]
current=json.loads((out/'ui_demos_responses.json').read_text(encoding='utf8'))
comparisons=[]
for round_no in range(7,15):
    family={8:'demos_cost',9:'db_ui_cost'}.get(round_no,'db_ui')
    p=root/f'audit_evidence_claims/m{round_no}/{family}/ui_demos_responses.json'
    prior=json.loads(p.read_text(encoding='utf8'))
    comparisons.append({'round':round_no,'total':len(current),'equal':sum(a==b for a,b in zip(current,prior)),'same_length':len(current)==len(prior),'errors':[r for r in current if r.get('error')]})
(out/'demo_previous_comparison.json').write_text(json.dumps(comparisons,ensure_ascii=False,indent=2),encoding='utf8')
head=subprocess.check_output(['git','rev-parse','HEAD'],cwd=root,text=True).strip()
standards={'head':head,'fixed_point':'bfcb83d','app_ui_diff':'git diff bfcb83d...HEAD -- src/app.py web/try.html','latest_diff':'git show HEAD -- src/query.py tests/test_app.py','repository_standards_files':(out/'review_diff_standards.txt').read_text(encoding='utf8').splitlines(),'governing_user_instructions':['Evidence-based independent review','No tracked file changes','All scratch output under m15','Historical findings FIXED / NOT FIXED'],'documented_violations':[],'bootstrap_issue_tracker':'Not performed: user audit-only scope excludes tracked setup writes','KOA_comparison':'Conditional on code changes; no application code changed','source_findings':['README.md:565 and README.ko.md:386 retain stale 317-test comments. App descriptions at 566 and 387 remain accurate.','Engine.ask explicitly sets use_llm=False at src/app.py:181.','Engine.explore read paths and markup escaping reviewed; no new DB/UI blocker found.']}
(out/'standards_review.json').write_text(json.dumps(standards,ensure_ascii=False,indent=2),encoding='utf8')
inventory=[]
for round_name in ['m1','m2','m2b']+[f'm{x}' for x in range(3,15)]:
    p=root/'audit_evidence_claims'/round_name/'REPORT.md'
    inventory.append({'round':round_name,'report_exists':p.exists(),'headings': [{'line':i,'text':s} for i,s in enumerate(p.read_text(encoding='utf8').splitlines(),1) if s.startswith('#')] if p.exists() else []})
(out/'historical_report_headings.json').write_text(json.dumps(inventory,ensure_ascii=False,indent=2),encoding='utf8')
sock=socket.socket(); port_open=sock.connect_ex(('127.0.0.1',8951))==0; sock.close()
summary={'head':head,'port':8951,'port_closed':not port_open,'db_sha256':hashlib.sha256((root/'data/processed/oncokg.sqlite').read_bytes()).hexdigest(),'demo_comparison':comparisons}
(out/'worker_status.json').write_text(json.dumps(summary,indent=2),encoding='utf8')
print(json.dumps(summary))
