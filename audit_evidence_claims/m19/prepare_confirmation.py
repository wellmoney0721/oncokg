from pathlib import Path
import ast,hashlib,json,re
OUT=Path(__file__).resolve().parent
src=OUT/'root_checks/independent_m18_http.py'
dst=OUT/'root_checks/independent_m19_http.py'
assert not dst.exists()
cases=['trastuzumab','radio-labelled trastuzumab','radio-labeled trastuzumab','radiolabelled trastuzumab','radiolabeled trastuzumab','trastuzumab radioactively labelled','trastuzumab radiolabelled with iodine-124','99m-technetium trastuzumab','technetium-99m trastuzumab','trastuzumab 99m-technetium','trastuzumab technetium-99m','osimertinib, radio-labelled trastuzumab','radio-labelled trastuzumab, osimertinib','fluorine-18 fluorodeoxyglucose','lead compound osimertinib','BKM120','AZD9291','osimertinib 80 mg','paclitaxel 2 cycles','13-cis retinoic acid','b.i.o.similar bevacizumab','lip.osomal doxorubicin']
t=src.read_text(encoding='utf8')
t=re.sub(r'^CASES = .*$', 'CASES = '+repr(cases),t,flags=re.M)
t=t.replace('PORT = 8849','PORT = 19319').replace('independent_m18','independent_m19')
dst.write_text(t,encoding='utf8')
(OUT/'root_checks/independent_m19_manifest.json').write_text(json.dumps(dict(source=str(src.relative_to(OUT)),source_sha256=hashlib.sha256(src.read_bytes()).hexdigest(),copy=str(dst.relative_to(OUT)),copy_sha256=hashlib.sha256(dst.read_bytes()).hexdigest(),changes=['new exact case list','owned port 19319','m19 output names'],cases=cases),indent=2),encoding='utf8')
