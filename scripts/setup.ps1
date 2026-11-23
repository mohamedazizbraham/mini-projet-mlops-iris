$ErrorActionPreference = 'Stop'
Set-Location (Split-Path $PSScriptRoot -Parent)
function Run-Docker { & docker @args; if ($LASTEXITCODE -ne 0) { throw "Docker a échoué : $args" } }
New-Item -ItemType Directory -Force runtime,evidence | Out-Null
Run-Docker compose build
Run-Docker compose up -d --wait mlflow
Run-Docker compose run --rm trainer python -m src.bootstrap
Run-Docker compose run --rm trainer python -m src.train
Run-Docker compose run --rm trainer pytest -q
Run-Docker compose up -d --wait api
Write-Host 'Prêt. API : http://localhost:8500/docs ; MLflow : http://localhost:5500'
