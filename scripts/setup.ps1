# Setup script for Movies Big Data Pipeline (PowerShell)

Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "Movies Pipeline - Setup" -ForegroundColor Cyan
Write-Host "=========================================" -ForegroundColor Cyan

# Check if poetry is installed
try {
    $poetryVersion = poetry --version
    Write-Host "✓ Poetry found: $poetryVersion" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Poetry is not installed!" -ForegroundColor Red
    Write-Host "Install it from: https://python-poetry.org/docs/#installation"
    exit 1
}

# Install dependencies
Write-Host ""
Write-Host "Installing dependencies..." -ForegroundColor Yellow
poetry install

Write-Host ""
Write-Host "✓ Dependencies installed" -ForegroundColor Green

# Check for Kaggle credentials
Write-Host ""
$kaggleConfigPath = Join-Path $env:USERPROFILE ".kaggle\kaggle.json"
if (Test-Path $kaggleConfigPath) {
    Write-Host "✓ Kaggle credentials found" -ForegroundColor Green
} else {
    Write-Host "⚠ Kaggle credentials not found!" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "To setup Kaggle API:" -ForegroundColor Yellow
    Write-Host "1. Go to: https://www.kaggle.com/settings"
    Write-Host "2. Click 'Create New API Token'"
    Write-Host "3. Move kaggle.json to $env:USERPROFILE\.kaggle\"
    Write-Host ""
}

# Copy .env.example to .env if it doesn't exist
if (-not (Test-Path ".env")) {
    Write-Host ""
    Write-Host "Creating .env file from template..." -ForegroundColor Yellow
    Copy-Item ".env.example" ".env"
    Write-Host "✓ .env file created" -ForegroundColor Green
    Write-Host "⚠ Please edit .env with your credentials" -ForegroundColor Yellow
} else {
    Write-Host "✓ .env file exists" -ForegroundColor Green
}

# Create data directories
Write-Host ""
Write-Host "Creating data directories..." -ForegroundColor Yellow
New-Item -ItemType Directory -Force -Path "data\raw" | Out-Null
New-Item -ItemType Directory -Force -Path "data\processed" | Out-Null
New-Item -ItemType Directory -Force -Path "data\refined" | Out-Null
Write-Host "✓ Data directories created" -ForegroundColor Green

Write-Host ""
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host "✓ Setup complete!" -ForegroundColor Green
Write-Host "=========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "1. Edit .env with your Kaggle credentials"
Write-Host "2. Run the pipeline: poetry run pipeline"
Write-Host "3. Or run specific stage: poetry run python -m src.main --stage ingestion"
Write-Host ""
Write-Host "For Jupyter notebooks:" -ForegroundColor Cyan
Write-Host "  poetry run jupyter notebook"
Write-Host ""
Write-Host "For tests:" -ForegroundColor Cyan
Write-Host "  poetry run pytest"
Write-Host ""
Write-Host "=========================================" -ForegroundColor Cyan

