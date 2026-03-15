param(
  [string]$PythonExe = "python"
)

$ErrorActionPreference = "Stop"

& $PythonExe -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install --upgrade pip
pip install -r requirements.txt

if (-not (Test-Path ".env")) {
  Copy-Item ".env.example" ".env"
  Write-Host "Arquivo .env criado a partir de .env.example. Ajuste as variáveis antes de usar."
}

Write-Host "Ambiente preparado."
Write-Host "Para rodar localmente:"
Write-Host "uvicorn src.index:app --reload"
