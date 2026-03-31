# TrustWise Web Interface - Quick Start

## Launch the Web Interface

### Windows

```bash
# Double-click or run in terminal:
start_web.bat
```

### Linux/Mac

```bash
chmod +x start_web.sh
./start_web.sh
```

### Or directly with npm

```bash
cd web
npm install
npm run build
npm start
```

### Legacy Flask mode (if preferred)

```bash
pip install flask
python app.py
```

## Access the Interface

Open your browser and go to:

```
http://localhost:5000
```

For API smoke (bridge JSON, `GET /api/status`) and optional browser UX checks, see [implementationtest.md](implementationtest.md) Phases 4 and 5.

## First Use

1. **Prerequisites**
   - Node.js 18+ installed
   - Python 3.10+ with `pip install -r requirements.txt` completed

2. **Check the Status Indicator** (top right)
   - 🟢 Green = Real LLM API connected
   - 🟡 Yellow = Mock mode (no API key)

2. **Enter a Query** or click an example chip:
   - "Latest AI developments in healthcare"
   - "Recent research on transformer models"
   - "Weekly tech updates on cybersecurity"

3. **Click "Generate Plan & Execute"**
   - Watch the progress indicator
   - See the execution plan
   - View results from web and research agents

4. **Explore Results**
   - Plan summary shows domains, sources, time range
   - Task results show collected data
   - Web results have source URLs and content
   - Research results have paper titles and PDF links

5. **View Past Plans**
   - Scroll down to "Recent Plans" section
   - Click any plan to view its details

## Data sources (what the agents use)

TrustWise does **not** use Google Custom Search. Collection works as follows:

| Layer | Sources |
|-------|---------|
| **Web agent** | [Crawl4AI](https://github.com/unclecode/crawl4ai) (headless browser scraping), [DuckDuckGo](https://duckduckgo.com/) search for URLs, Wikipedia, plain HTTP fallback |
| **Research agent** | [arXiv](https://arxiv.org/) API, [OpenAlex](https://openalex.org/) API, [Semantic Scholar](https://www.semanticscholar.org/) API — all **keyless** (optional `OPENALEX_MAILTO` in `.env` for OpenAlex polite use) |
| **LLM planning** | **Ollama** (default, local) or **Google Gemini** (optional cloud). Set `GEMINI_API_KEY` in `.env` only if `LLM_PROVIDER=gemini`. Without a key (or if Ollama is down), planning uses a **query-derived mock plan** so the rest of the pipeline still runs. |

## API Endpoints

If you're building automation or integrations:

- `POST /api/submit` - Submit a query
- `GET /api/plans` - List all plans
- `GET /api/plan/<filename>` - Get specific plan
- `GET /api/status` - System status

See [FRONTEND.md](FRONTEND.md) for complete API documentation.

## Troubleshooting

### Server Won't Start

- Make sure Node.js is installed: `node --version`
- Make sure dependencies are installed: `cd web && npm install`
- Make sure Python dependencies are installed: `pip install -r requirements.txt`
- Check if port 5000 is already in use
- Try building and running directly: `cd web && npm run build && npm start`

### No API Key Warning

- This is normal when **`GEMINI_API_KEY`** is not set or you use **Ollama** without it running: planning falls back to a **query-derived mock plan** (`plan_source: mock`) so you can still test the pipeline.
- **Optional — real cloud LLM:** To use **Google Gemini** for planning, set `LLM_PROVIDER=gemini` and add `GEMINI_API_KEY` to `.env`.
- **Optional — local LLM:** Run [Ollama](https://ollama.com/) and set `LLM_PROVIDER=ollama` (no Gemini key required).
- Restart the server after changing `.env`.

### Results Not Showing

- Open browser DevTools (F12)
- Check Console for errors
- Verify the query submitted successfully

## Features

✅ **User-Friendly Interface**

- Modern design
- Responsive (works on mobile)
- Clear visual feedback

✅ **Real-Time Execution**

- Progress indicators
- Task status updates
- Detailed results

✅ **History Management**

- View past plans
- Track all executions
- Audit trail

✅ **Data Visualization**

- Execution statistics
- Task results preview
- Source citations

## Next Steps

- Review [FRONTEND.md](FRONTEND.md) for detailed documentation
- Check [README.md](README.md) for system architecture
- See [QUICKSTART.md](QUICKSTART.md) for CLI usage

---

**Tip:** Keep the web interface open while using TrustWise for the best experience!
