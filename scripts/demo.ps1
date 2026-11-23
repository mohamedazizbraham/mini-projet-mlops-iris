param([switch]$Auto)
$ErrorActionPreference = 'Stop'
Set-Location (Split-Path $PSScriptRoot -Parent)
$body = @{sepal_length=5.1; sepal_width=3.5; petal_length=1.4; petal_width=0.2} | ConvertTo-Json
$proof = @()
$previousVersion = $env:MODEL_VERSION
try {
    foreach ($version in @('v1','v2','v1')) {
        if (-not $Auto) { Read-Host "Entrée : déployer $version" | Out-Null }
        $env:MODEL_VERSION = $version
        & docker compose up -d --wait --no-deps api
        if ($LASTEXITCODE -ne 0) { throw 'Échec du déploiement' }
        $result = Invoke-RestMethod http://localhost:8500/predict -Method Post -ContentType 'application/json' -Body $body
        if ($result.model_version -ne $version -or $result.species -ne 'setosa') { throw 'Prédiction ou version incorrecte' }
        $result | Format-List
        $proof += @{timestamp=(Get-Date).ToString('o'); expected=$version; response=$result}
    }
    if ($proof[0].response.mlflow_run_id -ne $proof[2].response.mlflow_run_id) { throw 'Rollback non identique' }
    $proof | ConvertTo-Json -Depth 6 | Set-Content evidence/deployment.json -Encoding utf8
    Write-Host 'SUCCÈS : v1, mise à jour v2, rollback exact v1.' -ForegroundColor Green
} finally { $env:MODEL_VERSION = $previousVersion }
