# TrustWise Quick Start (Web)

## Prerequisites

- Complete Python setup first (`pip install -r requirements.txt`).
- Node.js 18+.

## Start Web App (Recommended: Docker)

```bash
copy .env.example .env
# Edit .env and set OLLAMA_BASE_URL to http://host.docker.internal:11434

docker-compose -f setup/docker-compose.yml up --build
```
Open `http://localhost:5000`.

## Start Web App (Native)

```bash
cd web
npm ci
npm run build
npm start
```

Open `http://127.0.0.1:5000` (override with `PORT` / `HOST` in `.env`; see `web/src/server.ts`).

## Optional Launch Scripts

- Windows: `scripts/start_web.bat`
- Linux/macOS: `scripts/start_web.sh`

## API Smoke Checks

```bash
curl http://127.0.0.1:5000/api/status
curl http://127.0.0.1:5000/api/plans
```

Bridge smoke:

```bash
echo '{"action":"status"}' | python api_bridge.py
```

## Notes

- The Express server delegates execution to `api_bridge.py`.
- Set `PYTHON_EXE` or `TRUSTWISE_PYTHON` when PATH points to the wrong Python interpreter.
- Planning uses the configured LLM (`LLM_PROVIDER`: Ollama, Gemini, or both). For Gemini or `both`, set `GEMINI_API_KEY` in `.env` (never commit it). With `ALLOW_MOCK_FALLBACK=true`, the planner can use a synthetic mock plan when the real provider is unavailable (for example Ollama connection errors, HTTP 404 on both `/api/chat` and `/api/generate`, or missing Gemini key in those code paths).
- After a submit, inspect `execution` and `results` in the JSON response; for empty data or errors, use the symptom table in [implementationtest.md](implementationtest.md).

For endpoint details see [FRONTEND.md](FRONTEND.md). CLI-oriented setup is in [QUICKSTART.md](QUICKSTART.md).

