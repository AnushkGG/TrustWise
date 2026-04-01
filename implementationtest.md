# TrustWise Implementation Test Protocol

This checklist validates the full stack in a repeatable order.

## Phase A - CI Parity

```bash
pip install -r requirements.txt
python test_basic.py
python test_comprehensive.py
cd web && npm ci && npm run build
```

On Windows PowerShell, if `&&` is not available, run the `cd web` line separately or use `;` between commands.

## Phase B - Config Validation

```bash
python -c "from utils.config import Config; Config.validate(); print('OK')"
```

## Phase C - Provider Path

Validate one mode relevant to your environment:

- `LLM_PROVIDER=ollama`
- `LLM_PROVIDER=gemini`
- `LLM_PROVIDER=both`
- optional fallback mock mode (`ALLOW_MOCK_FALLBACK=true`)

Ollama endpoint fallback expectation:

- TrustWise first calls `OLLAMA_BASE_URL/api/chat`.
- If `/api/chat` returns `404`, it automatically retries `OLLAMA_BASE_URL/api/generate`.
- If **both** endpoints return HTTP `404` (for example, something other than Ollama is bound to that port), the planner raises unless `ALLOW_MOCK_FALLBACK=true`, in which case a synthetic mock plan is used.
- A healthy Ollama install should satisfy at least one of `/api/chat` or `/api/generate`.

## Phase D - Bridge and HTTP Smoke

```bash
echo '{"action":"status"}' | python api_bridge.py
curl http://127.0.0.1:5000/api/status
```

## Phase E - Submit Flow

Send one valid query (and optionally 2–3 diverse queries) via `POST /api/submit` with `{"query":"..."}` and verify:

- `success: true`
- `execution` block: tasks, structured/trusted counts, cache hit, `research_*` metrics, `keyed_research_providers` if present (`api_bridge.py`)
- `results[]`: per-task `status`, `agent`, and whether `data` is non-empty
- outputs written to enabled destinations

**Artifacts (for debugging):**

- Plans: `data/plans/`
- Raw agent JSON: `data/raw/`
- Optional local captures: create `logs/local-test/` (gitignored) and save JSON responses plus server stderr for repeatable audits.

## No data / errors — symptom to layer

| Symptom | Likely layer | Where to look |
|--------|--------------|---------------|
| Plan fails or invalid JSON | Planner / LLM (`orchestrator/llm_client.py`, Gemini) | stderr; `data/plans/` if partial save |
| Empty web `data` | `agents/web_agent.py` | `no_data_reasons` in task result; DuckDuckGo / network |
| Empty research `data` | `agents/research_agent.py`, `agents/source_registry.py` | `source_metrics`, Semantic Scholar 429, timeouts |
| `structured_data` empty | `cleaner/` | Raw payloads too short or filtered |
| No trusted items | `trust/` | Threshold / domain rules |
| Cache masks live behavior | `storage/` | `ENABLE_DB_CACHE`, `DB_CACHE_MIN_ITEMS` |

**Note:** The LLM produces **plan JSON only**; web agents, research, cleaner, trust, and storage are separate pipeline stages. A single “one prompt does everything” mode would be a product change (new endpoint or mode), not a planner-only tweak.

**Local submit without a working Ollama:** set `ALLOW_MOCK_FALLBACK=true` in your environment (or `.env`). If something other than Ollama is listening on `OLLAMA_BASE_URL` and returns HTTP 404 for `/api/chat` and `/api/generate`, the planner will use the synthetic mock plan when mock fallback is enabled.


## One-Command Automation

```bash
python scripts/run_implementation_tests.py
```

On Windows terminals that default to cp1252, use UTF-8 output for Python checks:

```powershell
$env:PYTHONIOENCODING='utf-8'
python test_basic.py
python test_comprehensive.py
```

Useful flags:

- `--ci`
- `--no-http`
- `--strict-http`
- `--no-npm`

## Troubleshooting Notes

- If Python test output crashes on Unicode symbols in Windows terminals, run with `PYTHONIOENCODING=utf-8` (shown above).
- If `web_agent` reports `requests and beautifulsoup4 required`, install dependencies in the same interpreter used by the server: `pip install -r requirements.txt`.
- If web task data is still empty, verify outbound network access and target-site blocking behavior.
- For multi-source research runs, verify `execution.research_unique_ratio` and `execution.enabled_research_sources` in `/api/submit` output.
- Key-gated adapters (Tavily, Exa, Firecrawl, Jina, Scopus, DeepSeek) are covered by mocked contract tests in `test_comprehensive.py` without API keys. With keys set in `.env`, run a live submit and check `execution.keyed_research_providers` for `configured` and `items_last_run`.

## Sign-off Table

| Date | Commit | Environment | CI parity | Config | Provider path | API smoke | Submit | Notes |
|------|--------|-------------|----------|--------|---------------|-----------|--------|-------|
|      |        |             |          |        |               |           |        |       |

