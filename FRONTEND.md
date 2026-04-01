# TrustWise Frontend and API Reference

The web frontend is served by Express (`web/src/server.ts`) and calls Python via `api_bridge.py`.

## Main Endpoints

- `GET /`: Web UI.
- `GET /api/status`: runtime/provider status.
- `POST /api/submit`: run full pipeline for a query.
- `GET /api/plans`: list saved plans.
- `GET /api/plan/:filename`: fetch one plan.
- `GET /api/raw-data`: list raw output files.

## Submit Contract

Request:

```json
{ "query": "Latest AI developments in healthcare" }
```

Response (shape; see [`api_bridge.py`](api_bridge.py) for the full payload):

```json
{
  "success": true,
  "plan": {
    "goal": "",
    "domains": [],
    "time_range": "",
    "sources": [],
    "total_tasks": 0
  },
  "execution": {
    "web_tasks": 0,
    "paper_tasks": 0,
    "total_results": 0,
    "successful": 0,
    "structured_items": 0,
    "trusted_items": 0,
    "db_inserted": 0,
    "db_skipped": 0,
    "cache_hit": false,
    "research_raw_count": 0,
    "research_unique_count": 0,
    "research_returned_count": 0,
    "research_unique_ratio": 0,
    "enabled_research_sources": [],
    "research_source_stats": {},
    "keyed_research_providers": {}
  },
  "results": [],
  "structured_data": [],
  "trusted_data": [],
  "insights": {},
  "trust_report": {
    "validated_count": 0,
    "trusted_count": 0,
    "dropped_count": 0
  }
}
```

`keyed_research_providers` summarizes optional Tavily/Exa/Firecrawl/Jina/Scopus/DeepSeek usage when keys are configured (`configured`, `items_last_run`, etc.).

## Status payload

`GET /api/status` returns `success` and a `status` object including `llm_provider`, `llm_model`, `has_api_key`, `ollama_reachable`, `gemini_configured`, `providers_available`, persistence flags (`save_plans`, `save_raw_data`, …), and cache settings.

## Server Behavior

- Input validation rejects empty queries with HTTP 400.
- Path traversal checks protect `GET /api/plan/:filename`.
- Global Express rate limit is enabled.
- Bridge calls are executed via subprocess with timeout and JSON parsing.

## Frontend Behavior

- Displays provider status and pipeline progression.
- Shows plan summary, execution metrics, trust summary, and item cards.
- Supports plan history view and CSV/PDF export actions.

## Dev Workflow

```bash
cd web
npm ci
npm run build
npm start
```

When editing client logic, treat `web/src/client/main.ts` as source-of-truth. `static/js/main.js` is bundled output.

