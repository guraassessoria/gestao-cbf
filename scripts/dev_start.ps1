<#
  Gestão CBF - Script de inicialização do ambiente de desenvolvimento
  Inicia backend (FastAPI) e frontend (Vite) simultaneamente
#>

$ErrorActionPreference = "Stop"
$ROOT = Split-Path -Parent $PSScriptRoot

Write-Host "`n=== Gestao CBF - Dev Environment ===" -ForegroundColor Cyan

# ─── 1. Verifica Python ───
Write-Host "`n[1/4] Verificando Python..." -ForegroundColor Yellow
$py = Get-Command python -ErrorAction SilentlyContinue
if (-not $py) {
    Write-Host "ERRO: Python nao encontrado no PATH" -ForegroundColor Red
    exit 1
}
Write-Host "  Python: $($py.Source)" -ForegroundColor Green

# ─── 2. Verifica Node ───
Write-Host "[2/4] Verificando Node.js..." -ForegroundColor Yellow
$node = Get-Command node -ErrorAction SilentlyContinue
if (-not $node) {
    Write-Host "ERRO: Node.js nao encontrado no PATH" -ForegroundColor Red
    exit 1
}
Write-Host "  Node: $($node.Source)" -ForegroundColor Green

# ─── 3. Verifica .env ───
Write-Host "[3/4] Verificando .env..." -ForegroundColor Yellow
$envFile = Join-Path $ROOT ".env"
if (-not (Test-Path $envFile)) {
    Write-Host "ALERTA: Arquivo .env nao encontrado em $ROOT" -ForegroundColor Yellow
    Write-Host "  Crie o arquivo .env com as variaveis necessarias:" -ForegroundColor Yellow
    Write-Host "    DATABASE_URL=postgresql://..." -ForegroundColor DarkGray
    Write-Host "    SECRET_KEY=..." -ForegroundColor DarkGray
    Write-Host "    DEFAULT_ADMIN_EMAIL=admin@empresa.com" -ForegroundColor DarkGray
    Write-Host "    DEFAULT_ADMIN_PASSWORD=SuaSenhaSegura123!" -ForegroundColor DarkGray
} else {
    Write-Host "  .env encontrado" -ForegroundColor Green
}

# ─── 4. Instala dependencias ───
Write-Host "[4/4] Instalando dependencias..." -ForegroundColor Yellow

# Backend
Write-Host "  Backend (pip install)..." -ForegroundColor DarkGray
Push-Location $ROOT
pip install -r requirements.txt --quiet 2>$null
Pop-Location

# Frontend
Write-Host "  Frontend (npm install)..." -ForegroundColor DarkGray
$frontendDir = Join-Path $ROOT "frontend"
if (Test-Path (Join-Path $frontendDir "package.json")) {
    Push-Location $frontendDir
    npm install --silent 2>$null
    Pop-Location
}

# ─── Iniciar serviços ───
Write-Host "`n=== Iniciando servicos ===" -ForegroundColor Cyan

# Backend
Write-Host "  Iniciando backend (http://127.0.0.1:8000)..." -ForegroundColor Green
$backendJob = Start-Job -ScriptBlock {
    param($dir)
    Set-Location $dir
    & python -m uvicorn src.main:app --reload --host 127.0.0.1 --port 8000
} -ArgumentList $ROOT

# Frontend
Write-Host "  Iniciando frontend (http://localhost:3000)..." -ForegroundColor Green
$frontendJob = Start-Job -ScriptBlock {
    param($dir)
    Set-Location $dir
    & npm run dev
} -ArgumentList $frontendDir

Write-Host "`n=== Servicos iniciados ===" -ForegroundColor Green
Write-Host "  Backend:  http://127.0.0.1:8000" -ForegroundColor White
Write-Host "  Frontend: http://localhost:3000" -ForegroundColor White
Write-Host "  API Docs: http://127.0.0.1:8000/docs" -ForegroundColor White
Write-Host "`n  Pressione Ctrl+C para parar ambos os servicos`n" -ForegroundColor DarkGray

try {
    while ($true) {
        # Mostra logs do backend
        $backendOutput = Receive-Job $backendJob -ErrorAction SilentlyContinue
        if ($backendOutput) { $backendOutput | ForEach-Object { Write-Host "[API] $_" -ForegroundColor DarkCyan } }

        # Mostra logs do frontend
        $frontendOutput = Receive-Job $frontendJob -ErrorAction SilentlyContinue
        if ($frontendOutput) { $frontendOutput | ForEach-Object { Write-Host "[WEB] $_" -ForegroundColor DarkMagenta } }

        Start-Sleep -Milliseconds 500
    }
} finally {
    Write-Host "`nParando servicos..." -ForegroundColor Yellow
    Stop-Job $backendJob -ErrorAction SilentlyContinue
    Stop-Job $frontendJob -ErrorAction SilentlyContinue
    Remove-Job $backendJob -ErrorAction SilentlyContinue
    Remove-Job $frontendJob -ErrorAction SilentlyContinue
    Write-Host "Servicos parados." -ForegroundColor Green
}
