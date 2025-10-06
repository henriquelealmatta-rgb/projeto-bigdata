# Script para executar o projeto sem Poetry

Write-Host "=" -NoNewline -ForegroundColor Cyan
Write-Host "=" * 79 -ForegroundColor Cyan
Write-Host "Movies Big Data Pipeline - Setup" -ForegroundColor Cyan
Write-Host "=" * 80 -ForegroundColor Cyan
Write-Host ""

# Verificar se venv existe
if (-not (Test-Path "venv")) {
    Write-Host "Criando ambiente virtual..." -ForegroundColor Yellow
    python -m venv venv
}

# Ativar venv
Write-Host "Ativando ambiente virtual..." -ForegroundColor Yellow
.\venv\Scripts\Activate.ps1

# Instalar dependências
Write-Host ""
Write-Host "Instalando dependências..." -ForegroundColor Yellow
pip install -r requirements.txt

Write-Host ""
Write-Host "=" * 80 -ForegroundColor Green
Write-Host "✓ Setup concluído!" -ForegroundColor Green
Write-Host "=" * 80 -ForegroundColor Green
Write-Host ""
Write-Host "Para executar o pipeline:" -ForegroundColor Cyan
Write-Host "  python -m src.main" -ForegroundColor White
Write-Host ""
Write-Host "Para iniciar a interface web:" -ForegroundColor Cyan
Write-Host "  streamlit run app.py" -ForegroundColor White
Write-Host ""

