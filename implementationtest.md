# TrustWise Implementation Test Protocol

This checklist validates the full stack in a repeatable order.

## Phase A - CI Parity

```bash
pip install -r requirements.txt
python test_basic.py
python test_comprehensive.py
cd web && npm ci && npm run build
```

## Phase B - Config Validation

```bash
python -c "from utils.config import Config; Config.validate(); print('OK')"
```

## Phase C - Provider Path

Validate one mode relevant to your environment:

- `LLM_PROVIDER=ollama`
- `LLM_PROVIDER=gemini`
- `LLM_PROVIDER=both`
- fallback mock mode

## Phase D - Bridge and HTTP Smoke

```bash
echo '{"action":"status"}' | python api_bridge.py
curl http://127.0.0.1:5000/api/status
```

## Phase E - Submit Flow

Send one valid query and verify:

- `success: true`
- execution metrics returned
- outputs written to enabled destinations

## One-Command Automation

```bash
python scripts/run_implementation_tests.py
```

Useful flags:

- `--ci`
- `--no-http`
- `--strict-http`
- `--no-npm`

## Sign-off Table

| Date | Commit | Environment | CI parity | Config | Provider path | API smoke | Submit | Notes |
|------|--------|-------------|----------|--------|---------------|-----------|--------|-------|
|      |        |             |          |        |               |           |        |       |

