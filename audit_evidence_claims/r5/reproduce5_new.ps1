$ErrorActionPreference = 'Stop'
$env:PYTHONIOENCODING = 'utf-8'
$env:PYTHONDONTWRITEBYTECODE = '1'
$auditR5Root = Split-Path -Parent $PSScriptRoot
$auditRepoRoot = Split-Path -Parent $auditR5Root
$auditTempPath = Join-Path $PSScriptRoot 'root5_temp'
New-Item -ItemType Directory -Force -Path $auditTempPath | Out-Null
$env:TEMP = $auditTempPath
$env:TMP = $auditTempPath
Push-Location $auditRepoRoot
try {
    foreach ($probeName in @('root5_numeric.py', 'root5_confirmation.py', 'spec5_probe.py', 'spec5_extended.py', 'spec5_controls.py', 'spec5_anaphora.py', 'docs5_probe.py', 'docs5_controls.py')) {
        python -B (Join-Path $PSScriptRoot $probeName)
        if ($LASTEXITCODE -ne 0) { throw "Probe failed: $probeName" }
    }
} finally {
    Pop-Location
}
