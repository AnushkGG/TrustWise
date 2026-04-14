# TrustWise Setup Directory

This directory contains all the files necessary to initialize and configure the TrustWise environment.

## Contents

- **`setup.sh`**: Automated setup script for Linux/macOS.
- **`setup.ps1`**: Automated setup script for Windows (PowerShell).
- **`Dockerfile`**: Docker configuration for building the TrustWise image.
- **`docker-compose.yml`**: Docker Compose configuration for running the full stack.
- **`requirements.txt`**: Python dependencies.
- **`.env.example`**: Template for environment variables (lives at the repository root).

## How to Setup

### Automated Setup (Recommended)

#### Windows (PowerShell)
1. Open PowerShell.
2. Run:
   ```powershell
   .\setup\setup.ps1
   ```

#### Linux/macOS (Bash)
1. Open a terminal.
2. Run:
   ```bash
   bash setup/setup.sh
   ```

### Manual Setup

1. **Python Dependencies**:
   ```bash
   pip install -r setup/requirements.txt
   ```

2. **Environment Variables**:
   Copy the repository root `.env.example` to `.env` and fill in your API keys.

3. **Docker**:
   To build and run using Docker:
   ```bash
   docker-compose -f setup/docker-compose.yml up --build
   ```

## Key Configuration Parts

- **Build Context**: The Docker and Docker Compose files are configured to use the project root as the build context.
- **Requirements**: The `Dockerfile` specifically copies `setup/requirements.txt` during the build process.
