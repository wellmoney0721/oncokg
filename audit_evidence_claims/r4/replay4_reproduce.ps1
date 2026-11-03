$ErrorActionPreference = 'Stop'
$env:PYTHONUTF8 = '1'
$env:PYTHONDONTWRITEBYTECODE = '1'
$env:PYTHONIOENCODING = 'utf-8'
python -B audit_evidence_claims/r4/replay4_all.py
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
python -B audit_evidence_claims/r4/replay4_summarize.py
exit $LASTEXITCODE
