import hashlib,json,subprocess
from pathlib import Path
O=Path(__file__).resolve().parent;R=O.parents[2]
stage=json.loads((O/'new_results.json').read_text(encoding='utf8'));http=json.loads((O/'new_http.json').read_text(encoding='utf8'));life=json.loads((O/'new_lifecycle.json').read_text(encoding='utf8'));cases=json.loads((O/'new_cases.json').read_text(encoding='utf8'))
assert len(cases)==len(stage['cases'])==82
assert [r['text'] for r in stage['cases']]==cases
assert len(http)==4*len(cases) and all(r['status']==200 for r in http)
assert life['port_closed'] and life['database_unchanged'] and life['page_matches_worktree']
source_refs=[{'url':'https://pmc.ncbi.nlm.nih.gov/articles/PMC1575276/','title':'Preclinical characterisation of 111In-DTPA-trastuzumab','accessed_date':'2026-11-04','quote':'radio-labelled trastuzumab','supports':'Primary research article develops and evaluates isotope-labelled trastuzumab; Discussion uses this exact hyphenated wording.'},{'url':'https://pmc.ncbi.nlm.nih.gov/articles/PMC3868035/','title':'Radiopharmacy, RP-39: Labeling of trastuzumab with Tc-99m via DTPA','accessed_date':'2026-11-04','supports':'Original research abstract reports preparation of Tc-99m-labelled trastuzumab as a diagnostic radiopharmaceutical.'}]
(O/'sources.json').write_text(json.dumps(source_refs,ensure_ascii=False,indent=2),encoding='utf8')
meta={'head':stage['head'],'counterfactual_query_head':stage['previous'],'staged_pairs':len(cases),'requests':len(http),'case_literals_match':True,'all_http_200':True,'server_lifecycle':life,'no_tracked_changes':not subprocess.check_output(['git','diff','--name-only'],cwd=R,text=True).strip(),'artifacts':[{ 'file':p.name,'sha256':hashlib.sha256(p.read_bytes()).hexdigest(),'bytes':p.stat().st_size} for p in sorted(O.glob('*')) if p.is_file() and p.suffix in ['.py','.json']]}
(O/'final_checks.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({k:v for k,v in meta.items() if k!='artifacts'},ensure_ascii=False,indent=2))
