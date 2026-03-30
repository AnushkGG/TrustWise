# TrustWise Web Frontend Documentation

## Overview

The TrustWise Web Frontend provides a user-friendly interface for interacting with the TrustWise system. It allows users to submit queries, view execution plans, monitor task progress, and examine results through a modern web interface.

## Features

### ✅ Implemented Features

1. **Query Submission**
   - Natural language query input
   - Example queries for quick testing
   - Real-time form validation

2. **Execution Visualization**
   - Generated plan display
   - Execution progress indicators
   - Task status tracking

3. **Results Display**
   - Plan summary with domains, time range, and sources
   - Execution statistics (web tasks, research tasks, success rate)
   - Detailed task results with data preview
   - Web scraping results with source URLs (from **Crawl4AI** + **DuckDuckGo**-discovered URLs, plus Wikipedia / HTTP fallback)
   - Research paper results with titles, authors, and PDF links (from **arXiv**, **OpenAlex**, **Semantic Scholar**)

4. **History Management**
   - List of recently generated plans (newest first)
   - View past plan details
   - No in-app search or date filters (chronological list only)

5. **System Status**
   - LLM provider and model information
   - API key status indicator
   - Mock mode detection

## Architecture

### Backend (TypeScript / Express)

**Directory:** `web/`

The TypeScript Express server provides REST API endpoints. Each API call delegates
to a Python subprocess (`api_bridge.py`) that runs the TrustWise pipeline.

**Data collection (backend):** the **web agent** uses Crawl4AI (headless browser), DuckDuckGo search, Wikipedia, and HTTP fallback. The **research agent** uses arXiv, OpenAlex, and Semantic Scholar (keyless). **LLM planning** uses Ollama and/or Google Gemini; the **Gemini API key is optional** — if missing (or the provider is unavailable), the pipeline uses query-derived mock plans.

The server applies **`express-rate-limit`**: by default **60 requests per minute per IP** (see `web/src/server.ts`). Adjust for production if needed.

- `GET /` - Serve the main HTML page
- `POST /api/submit` - Submit and execute a query
- `GET /api/plans` - List saved execution plans
- `GET /api/plan/<filename>` - Get specific plan details
- `GET /api/status` - Get system configuration status
- `GET /api/raw-data` - List raw data files

### Legacy Backend (Flask)

**File:** `app.py` (kept for reference / backwards compatibility)

### Frontend Structure

```
TrustWise/
├── web/                         # TypeScript web server
│   ├── package.json
│   ├── tsconfig.json
│   ├── src/
│   │   └── server.ts           # Express server
│   └── public/
│       └── index.html          # Main HTML page
├── api_bridge.py               # Python API bridge
└── static/
    ├── css/
    │   └── style.css           # Styles
    └── js/
        └── main.js             # JavaScript logic
```

## Installation & Setup

### 1. Install Dependencies

```bash
# Python dependencies (for the pipeline)
pip install -r requirements.txt

# TypeScript/Node.js dependencies (for the web server)
cd web && npm install
```

### 2. Configure Environment

Make sure your `.env` file exists (copy from `.env.example`). **Gemini is optional:** you only need `GEMINI_API_KEY` when `LLM_PROVIDER=gemini`. For local Ollama, use `LLM_PROVIDER=ollama` and no cloud key.

```env
# Example: local Ollama (no Gemini key)
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
LLM_MODEL=llama3.2

# Optional — Google Gemini for planning (set LLM_PROVIDER=gemini)
# GEMINI_API_KEY=your_key_here
# LLM_MODEL=gemini-2.0-flash
```

### 3. Run the Web Server

```bash
cd web
npm run build
npm start
```

The server will start on `http://localhost:5000`

### 4. Access the Interface

Open your browser and navigate to:

```
http://localhost:5000
```

## Usage Guide

### Submitting a Query

1. **Enter your query** in the text area
   - Example: "Latest AI developments in healthcare"

2. **Click "Generate Plan & Execute"**
   - The system will process your query
   - You'll see a loading indicator with progress steps

3. **View Results**
   - Plan summary shows the generated execution plan
   - Execution summary displays statistics
   - Task results show detailed data from each agent

### Using Example Queries

Click any of the pre-defined example query chips:

- AI in Healthcare
- Transformer Models
- Cybersecurity News
- Quantum Computing

These populate the query field with tested examples.

### Viewing Past Plans

The "Recent Plans" section shows your execution history:

- Click any plan to view its details
- See the goal, query, timestamp, and task count
- Plans are sorted by most recent first

## API Endpoints

### POST /api/submit

Submit a query for execution.

**Request:**

```json
{
  "query": "Latest AI developments in healthcare"
}
```

**Response (success):** JSON from `api_bridge.handle_submit`. Typical shape:

```json
{
  "success": true,
  "plan": {
    "goal": "...",
    "domains": ["..."],
    "time_range": "...",
    "sources": ["..."],
    "total_tasks": 4
  },
  "execution": {
    "web_tasks": 2,
    "paper_tasks": 2,
    "total_results": 4,
    "successful": 4,
    "structured_items": 10,
    "trusted_items": 6,
    "db_inserted": 4,
    "db_skipped": 2,
    "cache_hit": false
  },
  "results": [],
  "structured_data": [],
  "trusted_data": [],
  "insights": {
    "summary": "...",
    "key_highlights": [],
    "confidence": 0.0,
    "sources_breakdown": {},
    "recommended_reading": []
  },
  "trust_report": {
    "validated_count": 10,
    "trusted_count": 6,
    "dropped_count": 4
  }
}
```

- **`results`**: Raw per-task agent outputs (same schema as `data/raw/` JSON).
- **`structured_data`**: Normalized items from the cleaner.
- **`trusted_data`**: Items that passed the trust validator.
- **`insights`**: Summary and highlights from `insights/generator.py` (LLM and/or extractive fallback).
- **`trust_report`**: Counts from validation.

**Cache short-circuit:** When `ENABLE_DB_CACHE` is enabled and SQLite already has enough trusted rows for the same query (`DB_CACHE_MIN_ITEMS`), the bridge may return immediately with `"cache_hit": true`, `"web_tasks": 0`, `"paper_tasks": 0`, empty `results`, and `structured_data` / `trusted_data` / `insights` populated from the database (no live scraping run).

**Errors:** `{ "success": false, "error": "..." }` (e.g. empty query).

### GET /api/plans

List all saved plans.

**Response:**

```json
{
  "success": true,
  "plans": [
    {
      "filename": "plan_20260217_123456.json",
      "goal": "...",
      "created_at": "2026-02-17T12:34:56",
      "query": "...",
      "tasks": 4
    }
  ]
}
```

### GET /api/plan/<filename>

Get a specific plan.

**Response:**

```json
{
  "success": true,
  "plan": {
    "goal": "...",
    "domains": [...],
    "tasks": [...],
    "_metadata": {...}
  }
}
```

### GET /api/status

Get system status (from `handle_status` in `api_bridge.py`).

**Response:**

```json
{
  "success": true,
  "status": {
    "llm_provider": "gemini",
    "llm_model": "gemini-2.0-flash",
    "has_api_key": true,
    "save_plans": true,
    "save_raw_data": true,
    "save_structured_data": true,
    "save_trusted_data": true,
    "save_to_db": true,
    "enable_db_cache": true,
    "is_running": false
  }
}
```

- **`has_api_key`**: For Gemini, true when `GEMINI_API_KEY` is set; for Ollama, a quick `GET /api/tags` check against `OLLAMA_BASE_URL`.
- **Persistence flags** mirror `utils/config.py` / `.env` (whether plans, raw, structured, trusted JSON and DB writes are enabled, and whether DB-backed query cache is on).

## Interface Components

### Header

- **Title:** TrustWise branding
- **Status Indicator:** Shows LLM provider and mode
  - 🟢 Green: Real API connected
  - 🟡 Yellow: Mock mode
  - 🔴 Red: Error

### Query Section

- **Text Area:** Multi-line input for queries
- **Submit Button:** Triggers execution
- **Example Chips:** Quick-select common queries

### Results Section

**Plan Summary:**

- Goal
- Domains (as chips)
- Time range
- Sources (as chips)
- Total tasks

**Execution Summary:**

- Web tasks count
- Research tasks count
- Total results
- Successful tasks

**Task Results:**

- Individual task cards
- Status badges (success/failed/partial)
- Agent type indicators (🌐 web, 📚 research)
- Data preview
  - Web: Source URLs and content snippets
  - Research: Paper titles, authors, PDF links

### Saved Plans Section

- List of recent plans (20 most recent)
- Click to view details
- Shows goal, timestamp, and task count

## Styling

### Color Scheme

- **Primary:** Blue (#2563eb)
- **Success:** Green (#10b981)
- **Warning:** Orange (#f59e0b)
- **Error:** Red (#ef4444)
- **Background:** Light gray (#f8fafc)

### Responsive Design

The interface is fully responsive:

- Desktop: Multi-column layouts
- Tablet: Adjusted grid sizes
- Mobile: Single column, stacked elements

### Animations

- Loading spinner
- Pulsing status indicator
- Hover effects on buttons and cards
- Smooth transitions

## Development

### Adding New Features

#### 1. Add API Endpoint (Backend)

Edit `web/src/server.ts`:

```typescript
app.get("/api/my-endpoint", async (_req: Request, res: Response) => {
  const result = await callPythonBridge("my_action");
  res.json(result);
});
```

Or add the Python handler in `api_bridge.py`:

```python
def handle_my_action(payload: dict) -> dict:
    # Your logic here
    return {"success": True, "data": []}
```

#### 2. Add Frontend Function (JavaScript)

Edit `static/js/main.js`:

```javascript
async function myFunction() {
  const response = await fetch("/api/my-endpoint");
  const data = await response.json();
  // Update UI
}
```

#### 3. Update HTML (if needed)

Edit `web/public/index.html`:

```html
<div id="myNewSection">
  <!-- Your HTML here -->
</div>
```

#### 4. Add Styles (if needed)

Edit `static/css/style.css`:

```css
.my-new-class {
  /* Your styles */
}
```

### Best Practices

1. **Always validate input** on both client and server
2. **Handle errors gracefully** with user-friendly messages
3. **Use loading indicators** for async operations
4. **Escape HTML** to prevent XSS attacks
5. **Keep API responses consistent** with `{success, data/error}` format

## Security Considerations

### Implemented Security

1. **Input Validation**
   - Query length limits
   - Required field validation

2. **Path Traversal Prevention**
   - Filename validation in `/api/plan/<filename>`
   - No directory traversal allowed

3. **XSS Prevention**
   - HTML escaping in JavaScript
   - Using `textContent` instead of `innerHTML` for user input

4. **CORS**
   - Configured via `cors` npm package
   - Restrict origins for production use

5. **HTTP rate limiting (Express)**
   - Global `express-rate-limit` middleware on the Node server (default 60 requests/minute per IP)

### Recommended for Production

1. **HTTPS**
   - Use SSL certificates
   - Redirect HTTP to HTTPS

2. **Authentication**
   - Add user login system
   - Session management
   - API key authentication

3. **Rate limiting (server)** — The Express app already uses **`express-rate-limit`** (global middleware). For public deployment, tune limits, add auth, and consider a reverse proxy (nginx, Cloudflare).

4. **Input Sanitization**
   - Validate query length
   - Filter malicious content

5. **CSRF protection**
   - Use CSRF tokens for form submissions
   - Consider `csurf` or `csrf-csrf` npm packages

## Performance Optimization

### Current implementation

- **Request model:** Each `/api/submit` runs the Python bridge synchronously in a subprocess until the pipeline finishes (long-running requests are expected for full runs).
- **Query cache:** When `ENABLE_DB_CACHE` is true, `api_bridge.py` may return cached trusted rows from SQLite without re-running agents (see `storage` module and `/api/submit` response `cache_hit`).
- **Express:** Static files for `/static`; rate limiting as above.

### Recommendations for scale

1. **Async processing**
   - Offload work to a job queue (e.g. Celery/RQ) and poll or use WebSockets for progress

2. **Caching and storage**
   - Optional Redis or similar for sessions or hot keys; SQLite remains the default local store

3. **Database**
   - For multi-user production, consider migrating plan/history storage to a shared database with proper indexing

4. **CDN**
   - Serve static assets via a CDN for global latency

## Troubleshooting

### Common Issues

#### 1. Server Won't Start

**Error:** `Address already in use`

**Solution:**

```bash
# Kill process on port 5000
# Windows:
netstat -ano | findstr :5000
taskkill /PID <PID> /F

# Linux/Mac:
lsof -ti:5000 | xargs kill
```

#### 2. API Calls Failing

**Error:** `Failed to fetch`

**Solution:**

- Check if the TypeScript server is running
- Verify URL is `http://localhost:5000`
- Check browser console for errors
- Verify the Python bridge is working: `echo '{"action":"status"}' | python api_bridge.py`

#### 3. Results Not Displaying

**Error:** No visible error, but results section is empty

**Solution:**

- Open browser DevTools (F12)
- Check Console for JavaScript errors
- Verify API response format matches expected structure

#### 4. Styles Not Loading

**Error:** Page looks unstyled

**Solution:**

- Clear browser cache (Ctrl+Shift+R)
- Check `static/css/style.css` exists
- Verify the Express server is serving static files correctly

## Future Enhancements

### Planned Features

1. **Real-time Progress**
   - WebSocket integration
   - Live task status updates
   - Streaming results

2. **Advanced Filtering**
   - Filter plans by date range
   - Search plans by keywords
   - Sort by various fields

3. **Data Visualization**
   - Charts for execution stats
   - Timeline visualization
   - Domain distribution graphs

4. **Export Features**
   - Download results as PDF
   - Export to CSV/JSON
   - Share plan links

5. **User Management**
   - Login/logout
   - User profiles
   - Saved queries

6. **Enhanced Results Display**
   - Modal dialogs for detailed views
   - Pagination for large result sets
   - Syntax highlighting for code snippets

7. **Settings Page**
   - Configure LLM provider via UI
   - Adjust agent parameters
   - Manage trusted sources

## Testing

### Manual Testing Checklist

- [ ] Submit query with valid input
- [ ] Submit query with empty input (should show error)
- [ ] View generated plan
- [ ] Check execution statistics
- [ ] View web task results
- [ ] View research task results
- [ ] Click example query chips
- [ ] View saved plans list
- [ ] Click on a saved plan
- [ ] Test on different browsers
- [ ] Test responsive design on mobile

### Browser Compatibility

Tested on:

- ✅ Chrome 120+
- ✅ Firefox 121+
- ✅ Edge 120+
- ✅ Safari 17+ (MacOS)

## Contributing

To contribute to the frontend:

1. **Fork the repository**
2. **Create a feature branch**
   ```bash
   git checkout -b feature/my-new-feature
   ```
3. **Make your changes**
4. **Test thoroughly**
5. **Submit a pull request**

## License

Same as main TrustWise project.

## Support

For issues or questions:

- Open an issue on GitHub
- Check the main README.md
- Review the QUICKSTART.md guide

---

**Note:** This frontend uses a TypeScript/Express web server that delegates to the Python pipeline via `api_bridge.py`.
