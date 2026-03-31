# TrustWise Quick Start (CLI)

## Prerequisites

- Python 3.10-3.12 recommended (CI uses 3.11).
- `pip` installed.
- Optional: Ollama running locally and model pulled.
- Optional: Gemini API key when using `LLM_PROVIDER=gemini`.

## Setup

```bash
pip install -r requirements.txt
copy .env.example .env  # Windows
python -c "from utils.config import Config; Config.validate(); print('OK')"
```

## Run

```bash
python main.py
```

## What Happens

1. Plan generation
2. Task scheduling
3. Web/research collection
4. Structured normalization
5. Trust filtering
6. Storage and insights

## Useful Commands

```bash
python scripts/demo.py
python scripts/run_implementation_tests.py
```

## Troubleshooting

- If `lxml` fails to install on Windows, use Python 3.11.
- If Python tests fail on Unicode symbols in Windows terminals, set `PYTHONIOENCODING=utf-8`.
- If provider is unavailable, mock plan mode is used automatically.
- If no data is collected from web tasks, verify network/reachability and retry.

See [README.md](README.md) for architecture and [implementationtest.md](implementationtest.md) for full verification.

