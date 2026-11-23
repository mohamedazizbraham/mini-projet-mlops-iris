$ErrorActionPreference = 'Stop'
Set-Location (Split-Path $PSScriptRoot -Parent)
if (-not (Test-Path models/v1.joblib) -or -not (Test-Path models/v2.joblib)) {
    throw 'Exécuter scripts/setup.ps1 avant la démo pour préparer les modèles.'
}
$env:MODEL_VERSION = 'v1'
docker compose up -d --wait mlflow api
if ($LASTEXITCODE -ne 0) { throw 'Impossible de démarrer les services. Vérifier Docker Desktop.' }
Start-Process http://localhost:5500
& "$PSScriptRoot/demo.ps1"
