#!/bin/bash

# TrustWise Automated Setup Script (Bash)
# This script prepares the environment for TrustWise.

# Exit on error
set -e

# Color codes
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${BLUE}=================================================${NC}"
echo -e "${BLUE}          TrustWise Environment Setup          ${NC}"
echo -e "${BLUE}=================================================${NC}"

# Navigate to the root directory (one level up from setup/)
cd "$(dirname "$0")/.."

# 1. Directory Structure
echo -e "\n${YELLOW}1. Creating runtime directories...${NC}"
mkdir -p data/raw data/plans config logs
echo -e "${GREEN}✓ Directories created.${NC}"

# 2. Environment Configuration
echo -e "\n${YELLOW}2. Setting up environment variables...${NC}"
if [ ! -f .env ]; then
    if [ -f .env.example ]; then
        cp .env.example .env
        echo -e "${GREEN}✓ Created .env from .env.example${NC}"
        echo -e "${YELLOW}⚠️  Please edit .env to add your API keys.${NC}"
    else
        echo -e "${RED}✗ Error: .env.example not found at repo root.${NC}"
    fi
else
    echo -e "${GREEN}✓ .env already exists.${NC}"
fi

# 3. Python Setup
echo -e "\n${YELLOW}3. Configuring Python virtual environment...${NC}"
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}✗ Error: python3 is not installed.${NC}"
    exit 1
fi

python3 -m venv venv
source venv/bin/activate
echo -e "${GREEN}✓ Virtual environment activated.${NC}"

echo -e "\n${YELLOW}Installing Python dependencies...${NC}"
pip install --upgrade pip
pip install -r setup/requirements.txt
echo -e "${GREEN}✓ Python dependencies installed.${NC}"

# 4. Node.js Setup (Web UI)
echo -e "\n${YELLOW}4. Installing Web UI dependencies...${NC}"
if command -v npm &> /dev/null; then
    if [ -d "frontend" ]; then
        cd frontend
        npm install
        cd ..
        echo -e "${GREEN}✓ Node.js dependencies installed.${NC}"
    else
        echo -e "${YELLOW}ℹ️  Warning: 'frontend' directory not found. Skipping UI setup.${NC}"
    fi
else
    echo -e "${YELLOW}ℹ️  Warning: npm is not installed. Skipping UI setup.${NC}"
fi

echo -e "\n${BLUE}=================================================${NC}"
echo -e "${GREEN}✅ Setup Complete!${NC}"
echo -e "${BLUE}=================================================${NC}"
echo -e "\nNext steps:"
echo -e "1. Edit .env and set your GEMINI_API_KEY."
echo -e "2. Run 'source venv/bin/activate' to enter the environment."
echo -e "3. Run 'python main.py' to start the system."
echo -e "4. Navigate to 'frontend/' and run 'npm run dev' for the UI."
