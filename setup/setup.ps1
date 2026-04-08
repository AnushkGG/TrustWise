# TrustWise Automated Setup Script (PowerShell)
# This script prepares the environment for TrustWise on Windows.

# Error handling
$ErrorActionPreference = "Stop"

Write-Host "=================================================" -ForegroundColor Blue
Write-Host "          TrustWise Environment Setup          " -ForegroundColor Blue
Write-Host "=================================================" -ForegroundColor Blue

# Navigate to the root directory (always one level up from setup/)
$ScriptPath = Split-Path -Parent $MyInvocation.MyCommand.Definition
Set-Location "$ScriptPath\.."

# 1. Directory Structure
Write-Host "`n1. Creating runtime directories..." -ForegroundColor Yellow
$dirs = @("data/raw", "data/plans", "config", "logs")
foreach ($dir in $dirs) {
    if (-not (Test-Path $dir)) {
        New-Item -ItemType Directory -Path $dir | Out-Null
        Write-Host "   ✓ Created $dir" -ForegroundColor Green
    } else {
        Write-Host "   ✓ $dir already exists" -ForegroundColor Green
    }
}

# 2. Environment Configuration
Write-Host "`n2. Setting up environment variables..." -ForegroundColor Yellow
if (-not (Test-Path ".env")) {
    if (Test-Path "setup/.env.example") {
        Copy-Item "setup/.env.example" ".env"
        Write-Host "   ✓ Created .env from setup/.env.example" -ForegroundColor Green
        Write-Host "   ⚠️  Please edit .env to add your API keys." -ForegroundColor Yellow
    } else {
        Write-Host "   ❌ Error: setup/.env.example not found." -ForegroundColor Red
    }
} else {
    Write-Host "   ✓ .env already exists." -ForegroundColor Green
}

# 3. Python Setup
Write-Host "`n3. Configuring Python virtual environment..." -ForegroundColor Yellow
if (-not (Get-Command python -ErrorAction SilentlyContinue)) {
    Write-Host "   ❌ Error: python is not installed or not in PATH." -ForegroundColor Red
    exit 1
}

# Create virtual environment
python -m venv venv
Write-Host "   ✓ Virtual environment created." -ForegroundColor Green

# Activate virtual environment
.\venv\Scripts\Activate.ps1
Write-Host "   ✓ Virtual environment activated." -ForegroundColor Green

Write-Host "`nInstalling Python dependencies..." -ForegroundColor Yellow
python -m pip install --upgrade pip
pip install -r setup/requirements.txt
Write-Host "   ✓ Python dependencies installed." -ForegroundColor Green

# 4. Node.js Setup (Web UI)
Write-Host "`n4. Installing Web UI dependencies..." -ForegroundColor Yellow
if (Get-Command npm -ErrorAction SilentlyContinue) {
    if (Test-Path "web") {
        Push-Location "web"
        npm install
        Pop-Location
        Write-Host "   ✓ Node.js dependencies installed." -ForegroundColor Green
    } else {
        Write-Host "   ℹ️  Warning: 'web' directory not found. Skipping UI setup." -ForegroundColor Yellow
    }
} else {
    Write-Host "   ℹ️  Warning: npm is not installed. Skipping UI setup." -ForegroundColor Yellow
}

Write-Host "`n=================================================" -ForegroundColor Blue
Write-Host "✅ Setup Complete!" -ForegroundColor Green
Write-Host "=================================================" -ForegroundColor Blue
Write-Host "`nNext steps:"
Write-Host "1. Edit .env and set your GEMINI_API_KEY."
Write-Host "2. Activate venv: .\venv\Scripts\Activate.ps1"
Write-Host "3. Run 'python main.py' to start the system."
Write-Host "4. Navigate to 'web/' and run 'npm run dev' for the UI."
