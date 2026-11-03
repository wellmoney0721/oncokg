$ErrorActionPreference = 'Stop'
$env:PYTHONDONTWRITEBYTECODE = '1'
$env:PYTHONUTF8 = '1'
$env:PYTHONIOENCODING = 'utf-8'
$auditTemp = Join-Path $PSScriptRoot 'replay3_temp'
New-Item -ItemType Directory -Path $auditTemp -Force | Out-Null
$env:TEMP = $auditTemp
$env:TMP = $auditTemp
foreach ($script in @('replay3_all.py', 'replay3_summarize.py', 'root3_probe.py', 'numeric3_probe.py', 'numeric3_dictionary.py', 'docs3_probe.py', 'docs3_focused.py', 'verify_artifacts.py')) {
    python -B (Join-Path $PSScriptRoot $script)
    if ($LASTEXITCODE -ne 0) { throw "Audit script failed: $script" }
}
