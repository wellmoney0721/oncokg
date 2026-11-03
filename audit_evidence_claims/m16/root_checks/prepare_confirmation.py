"""Adapt the prior independent HTTP reproducer to new paired isotope inputs."""
from pathlib import Path
import ast, hashlib, json
OUT=Path(__file__).resolve().parent
source=OUT/'independent_m15_http.py'
code=source.read_text(encoding='utf8')
cases=['trastuzumab','I-124 trastuzumab','I124 trastuzumab','trastuzumab I-124',
       'trastuzumab I124','124I trastuzumab','trastuzumab 124I',
       'i-124 trastuzumab','I-124 trastuzumab, osimertinib','osimertinib, I-124 trastuzumab',
       'H3 vinblastine','3h vinblastine','C11 erlotinib','11C erlotinib',
       'Cu64 trastuzumab','64Cu trastuzumab','89-ZrDFO trastuzumab','3hvinblastine','A33124i']
old=next(line for line in code.splitlines() if line.startswith('CASES ='))
code=code.replace(old,'CASES = '+repr(cases)).replace('PORT = 8946','PORT = 8947')
code=code.replace('independent_m15','independent_m16')
code=code.replace('env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1", "PYTHONIOENCODING": "utf-8"}',
    'env = {**os.environ, "PYTHONDONTWRITEBYTECODE": "1", "PYTHONUTF8": "1", "PYTHONIOENCODING": "utf-8", "TMP":str(OUT/"tmp"), "TEMP":str(OUT/"tmp"), "TMPDIR":str(OUT/"tmp")}')
ast.parse(code)
(OUT/'independent_m16_http.py').write_text(code,encoding='utf8')
(OUT/'independent_m16_manifest.json').write_text(json.dumps(dict(source=str(source),
    source_sha256=hashlib.sha256(source.read_bytes()).hexdigest(),changes=['new cases','port 8947','m16 output prefix','temp env']),indent=2),encoding='utf8')
