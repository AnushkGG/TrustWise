# TrustWise Quick Start (CLI)

## Prerequisites

- Python 3.10-3.12 recommended (CI uses 3.11).
- `pip` installed.
- Optional: Ollama running locally and model pulled.
- Optional: Gemini API key when using `LLM_PROVIDER=gemini`.

## API keys (security)

- Put real keys only in a **local** `.env` (gitignored). Never commit keys or paste them into the repository.
- If a Gemini (or other) key was exposed, **rotate** it in the provider console and update `.env` only on your machine.

## Setup

```bash
pip install -r requirements.txt
copy .env.example .env  # Windows
# Edit .env: for Gemini set LLM_PROVIDER=gemini, GEMINI_API_KEY, GEMINI_MODEL (see .env.example)
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

## Web stack (local)

```bash
cd web
npm ci
npm run build
npm start
```

App URL defaults to `http://127.0.0.1:5000` (see `web/src/server.ts` for `PORT` / `HOST`).

Preflight:

```bash
echo '{"action":"status"}' | python api_bridge.py
```

With the server running: open or `curl` `GET /api/status`.

## Useful Commands

```bash
python scripts/demo.py
python scripts/run_implementation_tests.py
```

## Troubleshooting

- If `lxml` fails to install on Windows, use Python 3.11.
- If Python tests fail on Unicode symbols in Windows terminals, set `PYTHONIOENCODING=utf-8`.
- By default, synthetic mock fallback is disabled (`ALLOW_MOCK_FALLBACK=false`).
- Enable optional API-key tools (Tavily/Exa/Firecrawl/Jina/Scopus/DeepSeek) via `.env` only when keys are available.
- If no data is collected from web tasks, verify network/reachability and retry.
- For empty results or errors, see the symptom-to-layer table in [implementationtest.md](implementationtest.md) (planner vs agents vs cleaner vs trust vs cache).

See [README.md](README.md) for architecture and [implementationtest.md](implementationtest.md) for full verification.

