"""Observe the legacy SDK-failure call without changing any probe inputs."""
from pathlib import Path
import contextlib
import io
import json
import runpy
import sys

OUT=Path(__file__).resolve().parent
rows=[]
for round_name in ['s1','s2']:
    script=OUT/('replay_'+round_name)/'modelui_probe.py'
    def observe(frame,event,arg):
        if event=='return' and frame.f_code.co_name=='answer' and frame.f_back:
            response=frame.f_back.f_globals.get('response')
            if isinstance(response,dict) and response.get('exception')=='simulated SDK failure' and arg is not None and arg.to_dict().get('generated_by')=='error: RuntimeError':
                rows.append({'source_round':round_name,
                    'original_source':'audit_evidence_claims/'+round_name+'/modelui_probe.py',
                    'exact_exception':"RuntimeError('simulated SDK failure')",
                    'question':frame.f_locals.get('question'),
                    'use_llm':frame.f_locals.get('use_llm'),
                    'result':arg.to_dict() if arg is not None else None})
    output=io.StringIO()
    sys.setprofile(observe)
    try:
        with contextlib.redirect_stdout(output), contextlib.redirect_stderr(output):
            runpy.run_path(str(script),run_name='__main__')
    finally:
        sys.setprofile(None)
    (OUT/('modelui_sdk_profile_'+round_name+'_stdout.txt')).write_text(output.getvalue(),encoding='utf-8')
assert len(rows)==2
assert all(r['result']['checks']['applicable'] is False for r in rows)
(OUT/'modelui_legacy_sdk_failure_results.json').write_text(json.dumps(rows,indent=2),encoding='utf-8')
print(json.dumps([{key:r[key] for key in ['source_round','exact_exception','question','use_llm']} for r in rows],indent=2))
