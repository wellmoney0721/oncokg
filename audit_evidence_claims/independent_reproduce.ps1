# Run from the repository root. All generated files stay in audit_evidence_claims.
$ErrorActionPreference = 'Stop'
$auditRoot = Join-Path (Get-Location).Path 'audit_evidence_claims'
$auditTemp = Join-Path $auditRoot 'independent_replay_temp'
New-Item -ItemType Directory -Path $auditTemp -Force | Out-Null
$env:TEMP = $auditTemp
$env:TMP = $auditTemp
$env:PYTHONDONTWRITEBYTECODE = '1'
$env:PYTHONIOENCODING = 'utf-8'

python -B audit_evidence_claims/independent_main.py
if ($LASTEXITCODE -ne 0) { throw 'Main probes failed to run' }
python -B audit_evidence_claims/independent_adversarial_probe.py
if ($LASTEXITCODE -ne 0) { throw 'Adversarial probes failed to run' }
python -B audit_evidence_claims/independent_adversarial_pairs.py
if ($LASTEXITCODE -ne 0) { throw 'Paired relation probes failed to run' }
python -B audit_evidence_claims/independent_faithful_probe.py
if ($LASTEXITCODE -ne 0) { throw 'Faithful paraphrases failed to run' }
python -B audit_evidence_claims/independent_code_dictionary.py
if ($LASTEXITCODE -ne 0) { throw 'Dictionary comparison failed to run' }
python -B audit_evidence_claims/independent_code_probes.py
if ($LASTEXITCODE -ne 0) { throw 'Code probes failed to run' }
python -m pytest tests -q -p no:cacheprovider
if ($LASTEXITCODE -ne 0) { throw 'Regression tests failed' }

git diff --exit-code 0c441e0 -- .
if ($LASTEXITCODE -ne 0) { throw 'Tracked working-tree differences detected' }
