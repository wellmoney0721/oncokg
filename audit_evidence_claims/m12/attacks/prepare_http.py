from pathlib import Path
import json
p=Path('audit_evidence_claims/m12/attacks')
s=Path('audit_evidence_claims/m11/root_checks/new_leaks_http.py').read_text(encoding='utf8')
s=s.replace('PORT = 8899','PORT = 8962')
a=s.index('CASES = ');b=s.index('\n\n\ndef post',a)
cases=['[89Z.r]-DFO-daratumumab','89Z_r-dfo-daratumumab','89Z.r-dfo-daratumumab','89Z.r dfo daratumumab','89Zr-dfo-daratumumab','[89Zr]-DFO-daratumumab','[89Z.r]-DFO-daratumumab, osimertinib','daratumumab','trastuzumab labelled with [89Zr]','trastuzumab labelled with [89Zr], osimertinib','[89Z.r]-labelled trastuzumab','[89Z.r]-labelled trastuzumab, osimertinib','[89Zr]-labelled trastuzumab','[89Z.r] trastuzumab','trastuzumab','bevacizumab a - w w b','bevacizumab','osimertinib','osimertinib 80 mg']
s=s[:a]+'CASES = '+repr(cases)+s[b:]
s=s.replace('env = {**os.environ,','env = {**os.environ, "TMP": str(OUT), "TEMP": str(OUT), "TMPDIR": str(OUT),')
(p/'http_probe.py').write_text(s,encoding='utf8')
(p/'reuse_manifest.json').write_text(json.dumps({'http_probe':{'source':'audit_evidence_claims/m11/root_checks/new_leaks_http.py','adaptations':['output location derives from script','port 8899 to 8962','new candidate/control case list','temp paths inside output directory']},'focused':'Original m12 stage probe patterned after m11/attacks/key_equivalence.py; HEAD^ reference intentionally preserved.'},indent=2),encoding='utf8')
