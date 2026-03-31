# Contributing to TrustWise

Thank you for helping improve TrustWise. This document describes how to set up a development environment, run checks, and open pull requests.

## Prerequisites

- **Python** 3.10–3.12 (CI uses 3.11). See [implementationtest.md](implementationtest.md) for parity commands.
- **Node.js** 18+ for the `web/` TypeScript server and client bundle.
- **Git** for forks and branches.

## Getting started

1. Fork the repository and clone your fork.
2. Create a virtual environment and install Python dependencies:

   ```bash
   pip install -r requirements.txt
   ```

3. Copy environment template and configure locally (never commit real secrets):

   ```bash
   copy .env.example .env   # Windows
   ```

4. For the web UI:

   ```bash
   cd web
   npm ci
   npm run build
   ```

See [QUICKSTART.md](QUICKSTART.md) and [WEB_QUICKSTART.md](WEB_QUICKSTART.md) for more detail.

## Before you open a PR

Run the same checks as CI:

```bash
python test_basic.py
python test_comprehensive.py
cd web && npm ci && npm run build
```

On Windows terminals that default to a legacy code page, use:

```powershell
$env:PYTHONIOENCODING='utf-8'
python test_basic.py
python test_comprehensive.py
```

Optional automation:

```bash
python scripts/run_implementation_tests.py --ci
```

Full protocol: [implementationtest.md](implementationtest.md).

## Pull requests

- Use a clear branch name and PR title.
- Describe **what** changed and **why** (not only the diff).
- Do not include API keys, tokens, or personal data in commits, PR descriptions, or issues. Use `.env` locally; only `.env.example` belongs in the repo with placeholders.
- If you change user-visible behavior or configuration, update the relevant markdown (e.g. [README.md](README.md), [QUICKSTART.md](QUICKSTART.md), [FRONTEND.md](FRONTEND.md)) in the same PR when practical.

## Security

See [SECURITY.md](SECURITY.md). Report vulnerabilities privately; do not file public issues with exploit details before a fix is coordinated.

## Code of conduct

This project follows the [Contributor Covenant](CODE_OF_CONDUCT.md). By participating, you agree to uphold it.
