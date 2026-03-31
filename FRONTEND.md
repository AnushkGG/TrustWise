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

Response:

```json
{
  "success": true,
  "plan": {},
  "execution": {},
  "results": [],
  "structured_data": [],
  "trusted_data": [],
  "insights": {},
  "trust_report": {}
}
```

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

