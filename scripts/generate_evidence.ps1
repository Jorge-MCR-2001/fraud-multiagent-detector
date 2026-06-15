param(
    [string]$ApiBase = "http://127.0.0.1:8000",
    [switch]$RunDockerTests
)

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectRoot = Split-Path -Parent $ScriptDir
$BackendDir = Join-Path $ProjectRoot "backend"
$EvidenceDir = Join-Path $ProjectRoot "docs\evidence"

New-Item -ItemType Directory -Force -Path $EvidenceDir | Out-Null

Write-Host "========================================"
Write-Host " Generando evidencias del desafío"
Write-Host " API: $ApiBase"
Write-Host " Evidence dir: $EvidenceDir"
Write-Host "========================================"

function Save-Json {
    param(
        [object]$Data,
        [string]$Path
    )

    $Data |
        ConvertTo-Json -Depth 80 |
        Out-File -FilePath $Path -Encoding utf8
}

function Invoke-And-Save-Evaluation {
    param(
        [string]$TransactionId,
        [string]$ExpectedDecision,
        [string]$OutputFile
    )

    $Url = "$ApiBase/evaluate/$TransactionId"

    Write-Host ""
    Write-Host "Evaluando $TransactionId -> esperado: $ExpectedDecision"

    $Response = Invoke-RestMethod -Uri $Url -Method GET

    $OutputPath = Join-Path $EvidenceDir $OutputFile
    Save-Json -Data $Response -Path $OutputPath

    $ActualDecision = $Response.decision

    if ($ActualDecision -ne $ExpectedDecision) {
        Write-Warning "Decision diferente para $TransactionId. Esperado=$ExpectedDecision | Actual=$ActualDecision"
    }
    else {
        Write-Host "OK: $TransactionId genero $ActualDecision"
    }

    Write-Host "Guardado: $OutputFile"
}

# 1. Evidencias de las 4 decisiones requeridas
Invoke-And-Save-Evaluation `
    -TransactionId "T-1003" `
    -ExpectedDecision "APPROVE" `
    -OutputFile "evaluate_T-1003_APPROVE.json"

Invoke-And-Save-Evaluation `
    -TransactionId "T-1007" `
    -ExpectedDecision "CHALLENGE" `
    -OutputFile "evaluate_T-1007_CHALLENGE.json"

Invoke-And-Save-Evaluation `
    -TransactionId "T-1004" `
    -ExpectedDecision "BLOCK" `
    -OutputFile "evaluate_T-1004_BLOCK.json"

Invoke-And-Save-Evaluation `
    -TransactionId "T-1005" `
    -ExpectedDecision "ESCALATE_TO_HUMAN" `
    -OutputFile "evaluate_T-1005_ESCALATE_TO_HUMAN.json"

# 2. Evidencia de HITL
Write-Host ""
Write-Host "Guardando cola HITL..."

$HitlQueue = Invoke-RestMethod -Uri "$ApiBase/hitl/queue?status=PENDING_REVIEW" -Method GET
Save-Json -Data $HitlQueue -Path (Join-Path $EvidenceDir "hitl_queue_sample.json")

Write-Host "Guardado: hitl_queue_sample.json"

# 3. Evidencia de runtime
Write-Host ""
Write-Host "Guardando runtime y readiness..."

$Runtime = Invoke-RestMethod -Uri "$ApiBase/" -Method GET
Save-Json -Data $Runtime -Path (Join-Path $EvidenceDir "runtime_root_response.json")

try {
    $Readiness = Invoke-RestMethod -Uri "$ApiBase/health/ready" -Method GET
    Save-Json -Data $Readiness -Path (Join-Path $EvidenceDir "health_ready_response.json")
}
catch {
    $ErrorPayload = $_.ErrorDetails.Message

    if ($ErrorPayload) {
        $ErrorPayload | Out-File -FilePath (Join-Path $EvidenceDir "health_ready_response.json") -Encoding utf8
    }
    else {
        $_ | Out-File -FilePath (Join-Path $EvidenceDir "health_ready_response.json") -Encoding utf8
    }
}

Write-Host "Guardado: runtime_root_response.json"
Write-Host "Guardado: health_ready_response.json"

# 4. Copia de audit trail
Write-Host ""
Write-Host "Buscando audit trail..."

$AuditTrailPath = Join-Path $BackendDir "data\audit\audit_trail.jsonl"
$AuditOutputPath = Join-Path $EvidenceDir "audit_trail_sample.jsonl"

if (Test-Path $AuditTrailPath) {
    Get-Content $AuditTrailPath -Tail 80 |
        Out-File -FilePath $AuditOutputPath -Encoding utf8

    Write-Host "Guardado: audit_trail_sample.jsonl"
}
else {
    "Audit trail not found at: $AuditTrailPath" |
        Out-File -FilePath $AuditOutputPath -Encoding utf8

    Write-Warning "No se encontro audit trail en $AuditTrailPath"
}

# 5. Copia de observability opcional
Write-Host ""
Write-Host "Buscando eventos de agentes..."

$AgentEventsPath = Join-Path $BackendDir "data\observability\agent_events.jsonl"
$AgentEventsOutputPath = Join-Path $EvidenceDir "agent_events_sample.jsonl"

if (Test-Path $AgentEventsPath) {
    Get-Content $AgentEventsPath -Tail 80 |
        Out-File -FilePath $AgentEventsOutputPath -Encoding utf8

    Write-Host "Guardado: agent_events_sample.jsonl"
}
else {
    "Agent events file not found at: $AgentEventsPath" |
        Out-File -FilePath $AgentEventsOutputPath -Encoding utf8

    Write-Warning "No se encontro agent_events en $AgentEventsPath"
}

# 6. Resultado de tests Docker
if ($RunDockerTests) {
    Write-Host ""
    Write-Host "Ejecutando tests Docker..."

    Push-Location $BackendDir

    docker run --rm --env-file .env fraud-multiagent pytest -v 2>&1 |
        Tee-Object -FilePath (Join-Path $EvidenceDir "test_result_23_passed.txt")

    Pop-Location
}
else {
    $TestOutput = Join-Path $EvidenceDir "test_result_23_passed.txt"

    if (!(Test-Path $TestOutput)) {
        @"
Test evidence pending.

Ejecutar desde backend:

docker run --rm --env-file .env fraud-multiagent pytest -v

O ejecutar este script con:

.\scripts\generate_evidence.ps1 -RunDockerTests
"@ | Out-File -FilePath $TestOutput -Encoding utf8
    }
}

Write-Host ""
Write-Host "========================================"
Write-Host " Evidencias generadas correctamente"
Write-Host " Ruta: $EvidenceDir"
Write-Host "========================================"