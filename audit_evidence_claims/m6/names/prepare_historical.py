"""Adapt the existing sweep only to replay literal earlier input inventories."""
import hashlib,json
from pathlib import Path
OUT=Path('audit_evidence_claims/m6/names')
source=OUT/'names_qa_relink_sweep.py'
body=source.read_text(encoding='utf8')
start,end=body.index('aliases='),body.index('rows=[]')
replacement='''input_sources=['audit_evidence_claims/m4/qa_relink_sweep.json',
               'audit_evidence_claims/m5/names_qa_relink_sweep.json']
inventories=[json.loads(Path(p).read_text(encoding='utf8'))['inputs'] for p in input_sources]
inputs=list(dict.fromkeys(s for values in inventories for s in values))
'''
body=body[:start]+replacement+body[end:]
body=body.replace("'names_qa_relink_sweep.json'","'historical_qa_replay.json'")
body=body.replace("'summary':counts,'inputs':inputs", "'input_sources':input_sources,'source_input_counts':[len(v) for v in inventories],'summary':counts,'inputs':inputs")
(OUT/'historical_qa_replay.py').write_text(body,encoding='utf8')
(OUT/'historical_adaptation.json').write_text(json.dumps({
    'script_reused':str(source),'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
    'adaptation':'replace dynamic current-alias input generation with ordered unique union of literal M4 and M5 inputs; redirect result filename only',
    'unchanged':'current-vs-current-with-matched-token-exclusion-disabled comparison and all answer classification logic'},indent=2),encoding='utf8')
