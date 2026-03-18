<#
  Gestão CBF - Script de deploy do frontend para Vercel
  Faz build do frontend e prepara para deploy
#>

$ErrorActionPreference = "Stop"
$ROOT = Split-Path -Parent $PSScriptRoot
$FRONTEND = Join-Path $ROOT "frontend"

Write-Host "`n=== Build Frontend ===" -ForegroundColor Cyan

# Instalar dependências
Write-Host "[1/3] Instalando dependencias..." -ForegroundColor Yellow
Push-Location $FRONTEND
npm ci --silent 2>$null

# Build
Write-Host "[2/3] Executando build..." -ForegroundColor Yellow
npm run build
if ($LASTEXITCODE -ne 0) {
    Write-Host "ERRO: Build falhou!" -ForegroundColor Red
    Pop-Location
    exit 1
}

Write-Host "[3/3] Build concluido!" -ForegroundColor Green
$distSize = (Get-ChildItem -Path "dist" -Recurse | Measure-Object -Property Length -Sum).Sum / 1KB
Write-Host "  Output: frontend/dist/" -ForegroundColor White
Write-Host "  Tamanho: $([math]::Round($distSize, 1)) KB" -ForegroundColor White

Pop-Location
Write-Host "`nPronto para deploy!`n" -ForegroundColor Green
