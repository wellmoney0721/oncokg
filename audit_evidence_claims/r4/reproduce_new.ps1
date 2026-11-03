$ErrorActionPreference = 'Stop'
$env:PYTHONDONTWRITEBYTECODE = '1'
$env:PYTHONUTF8 = '1'
$env:PYTHONIOENCODING = 'utf-8'
$scratchRoot = $PSScriptRoot
$env:TEMP = Join-Path $scratchRoot 'new_probe_temp'
$env:TMP = $env:TEMP
New-Item -ItemType Directory -Force -Path $env:TEMP | Out-Null
foreach ($scriptName in @('root4_probe.py','root4_confirmation.py','spec_probe.py','spec_probe2.py','spec_probe3.py','spec_controls.py','docs_probe.py','docs_controls.py','docs_diagnostics.py')) {
    python -B (Join-Path $scratchRoot $scriptName)
    if ($LASTEXITCODE -ne 0) { throw "$scriptName failed with exit code $LASTEXITCODE" }
}
