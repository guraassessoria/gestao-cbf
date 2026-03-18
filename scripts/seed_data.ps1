<#
  Gestão CBF - Seed de dados iniciais
  Utiliza a API para carregar as estruturas de referência (sample_data)
  Requisito: backend rodando em http://127.0.0.1:8000
#>

param(
    [string]$BaseUrl = "http://127.0.0.1:8000",
    [string]$Email = "admin@empresa.com",
    [string]$Senha = "TroqueEssaSenha123!"
)

$ErrorActionPreference = "Stop"
$ROOT = Split-Path -Parent $PSScriptRoot
$SAMPLE = Join-Path $ROOT "sample_data"

function Invoke-Api {
    param(
        [string]$Method,
        [string]$Path,
        [object]$Body,
        [hashtable]$Headers = @{},
        [string]$ContentType = "application/json"
    )
    $uri = "$BaseUrl$Path"
    $params = @{
        Method = $Method
        Uri = $uri
        Headers = $Headers
        ContentType = $ContentType
    }
    if ($Body -and $ContentType -eq "application/json") {
        $params.Body = ($Body | ConvertTo-Json -Depth 10)
    } elseif ($Body) {
        $params.Body = $Body
    }
    return Invoke-RestMethod @params
}

Write-Host "`n=== Seed de Dados Iniciais ===" -ForegroundColor Cyan

# 1. Login
Write-Host "[1/5] Fazendo login..." -ForegroundColor Yellow
$loginRes = Invoke-Api -Method POST -Path "/auth/login" -Body @{ email = $Email; senha = $Senha }
$token = $loginRes.access_token
$authHeaders = @{ Authorization = "Bearer $token" }
Write-Host "  Login OK" -ForegroundColor Green

# 2. Upload Plano de Contas
Write-Host "[2/5] Uploading Plano de Contas..." -ForegroundColor Yellow
$planoFile = Join-Path $SAMPLE "plano_contas.csv"
if (Test-Path $planoFile) {
    $boundary = [System.Guid]::NewGuid().ToString()
    $fileBytes = [System.IO.File]::ReadAllBytes($planoFile)
    $fileEnc = [System.Text.Encoding]::GetEncoding("ISO-8859-1").GetString($fileBytes)

    $bodyLines = @(
        "--$boundary",
        'Content-Disposition: form-data; name="versao"',
        '',
        'seed-v1',
        "--$boundary",
        'Content-Disposition: form-data; name="arquivo"; filename="plano_contas.csv"',
        'Content-Type: text/csv',
        '',
        $fileEnc,
        "--$boundary--"
    )
    $body = $bodyLines -join "`r`n"
    try {
        Invoke-RestMethod -Method POST -Uri "$BaseUrl/estruturas/plano-contas/upload" `
            -Headers $authHeaders `
            -ContentType "multipart/form-data; boundary=$boundary" `
            -Body $body
        Write-Host "  Plano de Contas OK" -ForegroundColor Green
    } catch {
        Write-Host "  Plano de Contas: $($_.Exception.Message)" -ForegroundColor Yellow
    }
}

# 3. Upload DRE
Write-Host "[3/5] Uploading Estrutura DRE..." -ForegroundColor Yellow
$dreFile = Join-Path $SAMPLE "estrutura_dre.csv"
if (Test-Path $dreFile) {
    $boundary = [System.Guid]::NewGuid().ToString()
    $fileBytes = [System.IO.File]::ReadAllBytes($dreFile)
    $fileEnc = [System.Text.Encoding]::GetEncoding("ISO-8859-1").GetString($fileBytes)

    $bodyLines = @(
        "--$boundary",
        'Content-Disposition: form-data; name="versao"',
        '',
        'seed-v1',
        "--$boundary",
        'Content-Disposition: form-data; name="arquivo"; filename="estrutura_dre.csv"',
        'Content-Type: text/csv',
        '',
        $fileEnc,
        "--$boundary--"
    )
    $body = $bodyLines -join "`r`n"
    try {
        Invoke-RestMethod -Method POST -Uri "$BaseUrl/estruturas/dre/upload" `
            -Headers $authHeaders `
            -ContentType "multipart/form-data; boundary=$boundary" `
            -Body $body
        Write-Host "  Estrutura DRE OK" -ForegroundColor Green
    } catch {
        Write-Host "  Estrutura DRE: $($_.Exception.Message)" -ForegroundColor Yellow
    }
}

# 4. Upload Balanço
Write-Host "[4/5] Uploading Estrutura Balanço..." -ForegroundColor Yellow
$balancoFile = Join-Path $SAMPLE "estrutura_balanco.csv"
if (Test-Path $balancoFile) {
    $boundary = [System.Guid]::NewGuid().ToString()
    $fileBytes = [System.IO.File]::ReadAllBytes($balancoFile)
    $fileEnc = [System.Text.Encoding]::GetEncoding("ISO-8859-1").GetString($fileBytes)

    $bodyLines = @(
        "--$boundary",
        'Content-Disposition: form-data; name="versao"',
        '',
        'seed-v1',
        "--$boundary",
        'Content-Disposition: form-data; name="arquivo"; filename="estrutura_balanco.csv"',
        'Content-Type: text/csv',
        '',
        $fileEnc,
        "--$boundary--"
    )
    $body = $bodyLines -join "`r`n"
    try {
        Invoke-RestMethod -Method POST -Uri "$BaseUrl/estruturas/balanco/upload" `
            -Headers $authHeaders `
            -ContentType "multipart/form-data; boundary=$boundary" `
            -Body $body
        Write-Host "  Estrutura Balanco OK" -ForegroundColor Green
    } catch {
        Write-Host "  Estrutura Balanco: $($_.Exception.Message)" -ForegroundColor Yellow
    }
}

# 5. Criar competência de exemplo
Write-Host "[5/5] Criando competencia de exemplo..." -ForegroundColor Yellow
try {
    $month = (Get-Date).ToString("yyyy-MM")
    Invoke-Api -Method POST -Path "/competencias" -Body @{ referencia = $month } -Headers $authHeaders
    Write-Host "  Competencia $month criada" -ForegroundColor Green
} catch {
    Write-Host "  Competencia: $($_.Exception.Message)" -ForegroundColor Yellow
}

Write-Host "`n=== Seed concluido ===" -ForegroundColor Green
Write-Host "  Acesse http://localhost:3000 para usar o sistema`n" -ForegroundColor White
