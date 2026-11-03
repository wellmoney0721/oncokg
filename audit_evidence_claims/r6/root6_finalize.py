"""Assemble the exact per-finding table and validate review artifacts only."""
import hashlib
import json
import re
import subprocess
from pathlib import Path
OUT=Path(__file__).resolve().parent
ROOT=OUT.parents[1]
p=OUT/'r6_report.md'
report=p.read_text(encoding='utf-8')
start=report.index('| Prior finding family | Current disposition |') if '| Prior finding family | Current disposition |' in report else report.index('| Prior finding | R6 disposition | Evidence |')
end=report.index('\nThe sole unsafe False-to-True change',start)
report=report[:start]+(OUT/'replay6_findings_table.md').read_text(encoding='utf-8').strip()+'\n'+report[end:]
p.write_text(report,encoding='utf-8')
rows=json.loads((OUT/'root6_confirmation.json').read_text(encoding='utf-8'))
by_id={r['id']:r for r in rows}
attacks=['B1_relative_status','B1_relative_phase','B2_record_status','B3_count_after_entities',
 'B3_count_after_entities_reverse','B4_reference_interruption','B4_reference_interruption_short',
 'B5_record_group','B6_kind_relative','B6_kind_group','B6_trial_kind_group','B6_trial_record_kind','B7_heading_sentence',
 'B8_as_inhibitor_multirecord']
assert all(by_id[x]['result']['checks']['grounded'] is True and
 not by_id[x]['result']['checks']['unsupported_claims'] for x in attacks)
links=re.findall(r'\]\(([^)]+)\)',report)
missing=[x for x in links if not (OUT/x).exists()]
assert not missing,missing
assert report.rstrip().endswith('VERDICT: CHANGES REQUIRED')
assert report.count('VERDICT:')==1
tracked=subprocess.check_output(['git','diff','--name-only'],cwd=ROOT,text=True).strip()
staged=subprocess.check_output(['git','diff','--cached','--name-only'],cwd=ROOT,text=True).strip()
assert not tracked and not staged
files=['r6_report.md','root6_confirmation.py','root6_confirmation.json','root6_numeric.py','root6_numeric.json',
 'replay6_manifest.json','replay6_all_cases.json','docs6_probe_results.json','docs6_faithful_evidence_review.json',
 'spec6_controls.json']
result={'head':subprocess.check_output(['git','rev-parse','HEAD'],cwd=ROOT,text=True).strip(),
 'tracked_diff':tracked,'staged_diff':staged,'missing_artifact_links':missing,'verified_blocker_inputs':len(attacks),
 'report_lines':len(report.splitlines()),'sha256':{f:hashlib.sha256((OUT/f).read_bytes()).hexdigest() for f in files}}
(OUT/'root6_final_verification.json').write_text(json.dumps(result,indent=2),encoding='utf-8')
print(json.dumps({k:v for k,v in result.items() if k!='sha256'},indent=2))
