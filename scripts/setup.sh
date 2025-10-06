#!/bin/bash
# Setup script for Movies Big Data Pipeline

set -e

echo "========================================="
echo "Movies Pipeline - Setup"
echo "========================================="

# Check if poetry is installed
if ! command -v poetry &> /dev/null; then
    echo "ERROR: Poetry is not installed!"
    echo "Install it from: https://python-poetry.org/docs/#installation"
    exit 1
fi

echo "✓ Poetry found"

# Install dependencies
echo ""
echo "Installing dependencies..."
poetry install

echo ""
echo "✓ Dependencies installed"

# Check for Kaggle credentials
echo ""
if [ -f "$HOME/.kaggle/kaggle.json" ]; then
    echo "✓ Kaggle credentials found"
else
    echo "⚠ Kaggle credentials not found!"
    echo ""
    echo "To setup Kaggle API:"
    echo "1. Go to: https://www.kaggle.com/settings"
    echo "2. Click 'Create New API Token'"
    echo "3. Move kaggle.json to ~/.kaggle/"
    echo "4. chmod 600 ~/.kaggle/kaggle.json"
    echo ""
fi

# Create .env if it doesn't exist
if [ ! -f ".env" ]; then
    echo ""
    echo "Creating .env file from template..."
    cp .env.example .env
    echo "✓ .env file created"
    echo "⚠ Please edit .env with your credentials"
else
    echo "✓ .env file exists"
fi

# Create data directories
echo ""
echo "Creating data directories..."
mkdir -p data/raw data/processed data/refined
echo "✓ Data directories created"

# Install pre-commit hooks (optional)
if command -v pre-commit &> /dev/null; then
    echo ""
    echo "Installing pre-commit hooks..."
    poetry run pre-commit install
    echo "✓ Pre-commit hooks installed"
fi

echo ""
echo "========================================="
echo "✓ Setup complete!"
echo "========================================="
echo ""
echo "Next steps:"
echo "1. Edit .env with your Kaggle credentials"
echo "2. Run the pipeline: poetry run pipeline"
echo "3. Or run specific stage: poetry run python -m src.main --stage ingestion"
echo ""
echo "For Jupyter notebooks:"
echo "  poetry run jupyter notebook"
echo ""
echo "For tests:"
echo "  poetry run pytest"
echo ""
echo "========================================="

