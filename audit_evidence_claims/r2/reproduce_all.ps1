# Run from the repository root. All audit outputs and temporary files stay in r2.
$ErrorActionPreference = 'Stop'
$auditR2 = (Resolve-Path -LiteralPath 'audit_evidence_claims/r2').Path
$auditTmp = Join-Path $auditR2 'root_temp'
New-Item -ItemType Directory -Path $auditTmp -Force | Out-Null
$env:TEMP = $auditTmp
$env:TMP = $auditTmp
$env:PYTHONDONTWRITEBYTECODE = '1'
$env:PYTHONIOENCODING = 'utf-8'
$env:PYTHONUTF8 = '1'
foreach ($auditScript in @('replay_all.py', 'root_design_probe.py', 'spec_probe.py', 'standards_probe.py')) {
    python -B (Join-Path $auditR2 $auditScript)
    if ($LASTEXITCODE -ne 0) { throw "Audit script failed: $auditScript" }
}
git diff --exit-code HEAD -- .
if ($LASTEXITCODE -ne 0) { throw 'Tracked working-tree differences detected' }
git diff --cached --exit-code
if ($LASTEXITCODE -ne 0) { throw 'Staged differences detected' }
