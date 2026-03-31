# TrustWise — Trust-First AI System

A trust-first, agent-based AI system for collecting and preparing technology-related information through controlled, auditable execution.

## Website (GitHub Pages)

After you enable **Pages** once (see below), the **static project site** is available at:

**https://anushkgg.github.io/TrustWise/**

That page introduces the project and links to this repo. It does **not** run the Python/Node pipeline (GitHub Pages is static-only). For the full web UI, run locally (`cd web && npm install && npm run build && npm start`) or deploy the [Dockerfile](Dockerfile) to Render, Fly.io, Railway, etc.

**Enable Pages:** Repository **Settings** → **Pages** → **Build and deployment** → **Source:** GitHub Actions (the workflow [`.github/workflows/pages.yml`](.github/workflows/pages.yml) deploys the [`docs/`](docs/) folder).

## Overview

TrustWise follows a **planning-first architecture** where an LLM is used exclusively for orchestration, not for answering questions end-to-end. The system converts natural language queries into structured JSON execution plans, routes tasks to specialized agents that collect raw data, then normalizes, validates, stores, and summarizes results in downstream stages.

Comments in the codebase sometimes refer to “Phase 1–6” as **internal pipeline milestones** (planning through DB cache); the product is a single integrated pipeline.

### Implemented capabilities

The current codebase includes:

- ✅ **LLM-based Planning**: Converts user queries to structured JSON plans
- ✅ **Task Decomposition**: Breaks plans into independent, executable chunks
- ✅ **Agent Routing**: Schedules tasks to appropriate specialized agents
- ✅ **Data Collection**: Web scraping and research paper retrieval
- ✅ **Auditability**: Saves plans and raw data for reproducibility
- ✅ **Trust Validation**: Zero-trust scoring and credibility checks
- ✅ **Database Storage**: SQLite with deduplication and caching
- ✅ **Insight Generation**: LLM-based summarization with extractive fallback
- ✅ **Web UI**: TypeScript/Express web interface with REST API

## Architecture

```
User Query
    ↓
[Orchestrator] → LLM generates JSON execution plan
    ↓
[Chunker] → Breaks plan into independent tasks
    ↓
[Scheduler] → Routes tasks by source type
    ↓
[Agents] → Execute tasks and collect raw data
    ↓
[Cleaner] → Normalizes data into uniform schema
    ↓
[Trust Validator] → Zero-trust scoring and filtering
    ↓
[Storage] → SQLite persistence with deduplication
    ↓
[Insights] → LLM/extractive summarization
```

### Components

- **orchestrator/**: LLM-based planning layer
  - `orchestrator.py`: Core planning logic with plan logging
  - `llm_client.py`: Gemini/Ollama LLM integration
  - `prompts.py`: Structured prompts with JSON schema
  - `schema.py`: Plan validation

- **chunker/**: Task decomposition
  - `chunker.py`: Breaks plans into executable units

- **scheduler/**: Task routing
  - `scheduler.py`: Routes tasks to appropriate agents

- **agents/**: Execution layer (no reasoning, just data collection)
  - `web_agent.py`: Web scraping with Crawl4AI + DuckDuckGo + Wikipedia
  - `research_agent.py`: arXiv plus keyless OpenAlex and Semantic Scholar search

- **cleaner/**: Data normalization
  - `cleaner.py`: Converts mixed agent outputs to uniform schema

- **trust/**: Zero-trust validation
  - `validator.py`: Credibility scoring, duplicate detection

- **storage/**: Persistence layer
  - `db.py`: SQLite storage with deduplication and caching

- **insights/**: Analysis
  - `generator.py`: LLM and extractive insight generation

- **utils/**: Shared utilities
  - `config.py`: Configuration management
  - `logger.py`: Logging setup
  - `retry.py`: Retry with exponential backoff
  - `rate_limiter.py`: Token-bucket rate limiter

- **config/**: Configuration files
  - `sources.json`: Trusted web sources

- **data/**: Output storage
  - `plans/`: Execution plans (for audit trail)
  - `raw/`: Raw agent outputs
  - `structured/`: Normalized records (JSON)
  - `trusted/`: Trust-validated records (JSON)
  - `trustwise.db`: SQLite database (deduplication and query cache)

## Installation

### 1. Clone Repository

```bash
git clone <repository-url>
cd TrustWise
```

### 2. Create Virtual Environment

Use **Python 3.11** if possible (matches CI). On Windows, **Python 3.14** may fail to install `lxml` from source; use 3.10-3.12 or install libxml2 build prerequisites.

```bash
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac
```

### 3. Install Dependencies

Use the same Python as in step 2. For a **clean** `pip install`, prefer **3.10–3.12** (CI uses **3.11**). On Windows, **3.14** often fails to build **`lxml`** unless XML/libxml2 build tools are installed.

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

Create a `.env` file from the example:

```bash
copy .env.example .env  # Windows
# cp .env.example .env  # Linux/Mac
```

**Recommended (local, no cloud API key):** Install [Ollama](https://ollama.com), run `ollama serve`, pull a model, then use:

```env
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
LLM_MODEL=llama3.2
```

Use a model that follows JSON instructions well for plan generation.

**Optional — Google Gemini (cloud):**

Without a key, planning does not call Gemini; a query-derived mock plan is used when no local LLM is available. Set a key only when you choose Gemini as the planner.

```env
LLM_PROVIDER=gemini
GEMINI_API_KEY=your_actual_api_key_here
LLM_MODEL=gemini-2.0-flash
```

**Combined mode — Gemini + Ollama in parallel:**

```env
LLM_PROVIDER=both
GEMINI_API_KEY=your_actual_api_key_here
GEMINI_MODEL=gemini-2.0-flash   # optional per-provider override
OLLAMA_MODEL=llama3.2            # optional per-provider override
```

When `LLM_PROVIDER=both`, TrustWise calls both Gemini and Ollama concurrently and merges their plans and insight summaries. Every task and key-point in the output carries an `origin` field (`"gemini"`, `"ollama"`, or `"both"` for near-duplicate items suggested by both providers) so users can see where each item came from. If one provider fails, the other's result is used alone with a logged warning.

**Note:** If Ollama is not running while `LLM_PROVIDER=ollama`, planning falls back to a **query-derived mock plan** (field `plan_source: mock`) so the rest of the pipeline can still be tested. For Gemini without a key, the same mock is used.

## Usage

### Option 1: Web Interface (Recommended)

The recommended UI is the **TypeScript/Express** server in `web/`, which calls the Python pipeline via `api_bridge.py`. The server runs `python api_bridge.py`; set `PYTHON_EXE` or `TRUSTWISE_PYTHON` to your venv interpreter if `python` on PATH is wrong. You need **Node.js 18+** (install dependencies once: `cd web && npm install`).

```bash
# Windows
scripts/start_web.bat

# Linux/Mac
chmod +x scripts/start_web.sh
./scripts/start_web.sh

# Or directly (after: cd web && npm install)
cd web && npm run build && npm start
```

Then open your browser to: **http://localhost:5000** (or `http://127.0.0.1:5000`).

**Features:**

- 🎨 Modern, user-friendly interface
- 📊 Visual execution progress
- 📈 Results visualization
- 📜 View execution history
- 🔍 Detailed task results

See [FRONTEND.md](FRONTEND.md) for complete documentation.

### Demo Mode

Run the demo script to see multiple queries automatically:

```bash
python scripts/demo.py
```

### Option 2: Command Line Interface

```bash
python main.py
```

### Example Session

```
TrustWise - Trust-First AI System (Phase 1)
============================================================

Enter your query: Latest AI developments in healthcare

🔄 Generating execution plan...

============================================================
📋 GENERATED PLAN
============================================================
Goal: Track latest AI developments in healthcare
Domains: artificial_intelligence, healthcare
Time Range: latest
Sources: web, research_papers
Tasks: 4
============================================================

📊 Scheduled 2 web tasks and 2 research tasks

🌐 Executing Web Tasks...
   ✓ task_web_1: success
   ✓ task_web_2: success

📚 Executing Research Tasks...
   ✓ task_paper_1: success
   ✓ task_paper_2: success

============================================================
✅ EXECUTION COMPLETE
============================================================
Tasks completed: 4/4
Raw data saved to: data\raw
Plan saved to: data\plans
```

## Configuration

| Variable               | Default            | Description |
| ---------------------- | ------------------ | ----------- |
| `LLM_PROVIDER`         | `ollama`           | LLM provider: `ollama` (local), `gemini` (cloud), or `both` (parallel merge) |
| `GEMINI_API_KEY`       | -                  | Optional: Google Gemini API key (required when `LLM_PROVIDER` is `gemini` or `both`) |
| `OLLAMA_BASE_URL`      | `http://localhost:11434` | Local Ollama server URL |
| `LLM_MODEL`            | `llama3.2`         | Shared model tag (used unless per-provider override is set) |
| `GEMINI_MODEL`         | -                  | Per-provider model override for Gemini (falls back to `LLM_MODEL`) |
| `OLLAMA_MODEL`         | -                  | Per-provider model override for Ollama (falls back to `LLM_MODEL`) |
| `LLM_TEMPERATURE`      | `0.0`              | Temperature (0 for deterministic output) |
| `LLM_MAX_TOKENS`       | `2000`             | Max tokens in response |
| `WEB_SCRAPER_TIMEOUT`  | `10`               | HTTP request timeout (seconds) |
| `ARXIV_MAX_RESULTS`    | `5`                | Max results from arXiv API |
| `RESEARCH_OPENALEX_MAX` | `5`             | Max works from OpenAlex (keyless) |
| `RESEARCH_SEMANTIC_SCHOLAR_MAX` | `5`    | Max papers from Semantic Scholar (keyless) |
| `RESEARCH_TOTAL_MAX`   | `15`               | Cap on merged, deduplicated papers per task |
| `OPENALEX_MAILTO`      | `mailto:dev@localhost` | Contact URL for OpenAlex polite `User-Agent` |
| `SAVE_PLANS`           | `true`             | Save plans to `data/plans/` |
| `SAVE_RAW_DATA`        | `true`             | Save agent outputs to `data/raw/` |
| `SAVE_STRUCTURED_DATA` | `true`             | Save normalized JSON to `data/structured/` |
| `SAVE_TRUSTED_DATA`    | `true`             | Save trust reports to `data/trusted/` |
| `SAVE_TO_DB`           | `true`             | Persist trusted items to `data/trustwise.db` |
| `ENABLE_DB_CACHE`      | `true`             | Reuse cached trusted rows for repeated queries (skips agents when enough items exist) |
| `DB_CACHE_MIN_ITEMS`   | `3`                | Minimum trusted items required to use DB cache |
| `LOG_LEVEL`            | `INFO`             | Logging level |
| `FLASK_DEBUG`          | `false`            | Used by legacy `app.py` / dev tooling |
| `PORT` / `HOST`        | `5000` / `127.0.0.1` | Optional; read by `web/src/server.ts` |

## Output Files

### Execution Plans

Saved to `data/plans/plan_YYYYMMDD_HHMMSS.json`:

```json
{
  "goal": "...",
  "domains": [...],
  "time_range": "...",
  "sources": [...],
  "tasks": [...],
  "_metadata": {
    "query": "...",
    "created_at": "...",
    "llm_provider": "gemini",
    "llm_model": "gemini-2.0-flash"
  }
}
```

### Raw Agent Data

Saved to `data/raw/task_xxx_YYYYMMDD_HHMMSS.json`:

```json
{
  "task_id": "task_web_1",
  "agent": "web_agent",
  "status": "success",
  "timestamp": "...",
  "prompt": "...",
  "data": [...]
}
```

## Project Structure

```
TrustWise/
│
├── main.py                    # CLI entry point
├── api_bridge.py              # Python API bridge for TypeScript server
├── test_basic.py              # Basic tests
├── test_comprehensive.py      # Comprehensive tests
├── requirements.txt           # Python dependencies
├── .env.example              # Environment template
│
├── scripts/                   # Automation and helper scripts
│   ├── setup.py               # Setup automation
│   ├── demo.py                # Demo script
│   ├── continuous_update.py   # Periodic update runner
│   ├── start_web.bat          # Windows web launcher
│   ├── start_web.sh           # Linux/Mac web launcher
│   ├── run_implementation_tests.py # CI parity verification
│   └── run_local_varied_inputs.py  # Input variation testing
│
├── legacy/                    # Legacy Flask implementation (kept for reference)
│   ├── app.py                 # Legacy web interface
│   └── templates/             # Legacy HTML templates
│
├── web/                       # TypeScript web server
│   ├── package.json           # Node.js dependencies
│   ├── tsconfig.json          # TypeScript configuration
│   ├── src/
│   │   └── server.ts          # Express server
│   └── public/
│       └── index.html         # Main web interface
│
├── templates/                 # Legacy HTML templates (Flask)
│   └── index.html            # Main web interface (Jinja2)
│
├── static/                    # Static web assets
│   ├── css/
│   │   └── style.css         # Styles
│   └── js/
│       └── main.js           # Frontend JavaScript
│
├── orchestrator/             # Planning layer
│   ├── __init__.py
│   ├── orchestrator.py       # Plan generation + logging
│   ├── llm_client.py         # LLM API integration
│   ├── prompts.py            # Structured prompts
│   └── schema.py             # Plan validation
│
├── chunker/                  # Task decomposition
│   ├── __init__.py
│   └── chunker.py
│
├── scheduler/                # Task routing
│   ├── __init__.py
│   ├── scheduler.py          # Routes tasks to agents
│   └── continuous.py         # Periodic update logic
│
├── agents/                   # Execution agents
│   ├── __init__.py
│   ├── web_agent.py          # Web scraping (Crawl4AI/DuckDuckGo/Wikipedia)
│   └── research_agent.py     # arXiv, OpenAlex, Semantic Scholar
│
├── cleaner/                  # Data normalization
│   ├── __init__.py
│   └── cleaner.py
│
├── trust/                    # Zero-trust validation
│   ├── __init__.py
│   └── validator.py
│
├── storage/                  # Database persistence
│   ├── __init__.py
│   └── db.py
│
├── insights/                 # Insight generation
│   ├── __init__.py
│   └── generator.py
│
├── utils/                    # Utilities
│   ├── __init__.py
│   ├── config.py             # Configuration management
│   ├── logger.py             # Logging setup
│   ├── retry.py              # Retry with exponential backoff
│   └── rate_limiter.py       # Token-bucket rate limiter
│
├── config/                   # Config files
│   └── sources.json          # Trusted sources
│
├── scripts/                   # Automation scripts
│   ├── run_implementation_tests.py # CI parity + full-stack verify
│   └── run_local_varied_inputs.py  # Local varied input testing
│
└── data/                     # Output directory
    ├── plans/                # Execution plans
    ├── raw/                  # Raw agent outputs
    ├── structured/           # Normalized outputs
    ├── trusted/              # Validated outputs
    └── trustwise.db          # SQLite database
```

## Key Design Principles

1. **Planning-First**: LLM used only for orchestration, not answering
2. **Structured Contracts**: All plans are JSON with strict validation
3. **Agent Simplicity**: Agents collect data, don't reason or validate
4. **Auditability**: All plans and outputs saved for reproducibility
5. **Zero-Trust Validation**: All collected data scored and filtered before use

## Pipeline milestones (internal)

Development was tracked in stages; the running system includes all of the following:

- Orchestration, task scheduling, and data collection
- Data normalization and cleaning
- Zero-trust validation and credibility scoring
- SQLite storage with deduplication
- LLM-based insights with extractive fallback
- DB-backed query cache for repeated runs

## Future Improvements

- WebSocket-based real-time progress updates
- User authentication and profiles
- PDF/CSV export
- Advanced task decomposition in Chunker

## Development

### Adding a New Agent

1. Create `agents/new_agent.py`
2. Implement `run(task)` function
3. Update `scheduler/scheduler.py` to route to new agent
4. Add source type to plan schema

### Testing Without API Keys

The system falls back to mock responses when API keys are missing, useful for testing the pipeline without LLM costs.

### Multi-phase implementation test plan

Use **[implementationtest.md](implementationtest.md)** when you need a repeatable sign-off of the whole stack (not only unit tests). It walks through phases in order so failures are easy to localize.

| Phase | What it covers |
|-------|----------------|
| 1 | **CI parity** — `pip install`, `test_basic.py`, `test_comprehensive.py`, `web/` `npm ci` + `npm run build` (same idea as [`.github/workflows/ci.yml`](.github/workflows/ci.yml)) |
| 2 | **Configuration** — `.env` from [`.env.example`](.env.example), `Config.validate()` |
| 3 | **LLM paths** — Ollama, Gemini, `LLM_PROVIDER=both` (merged plans/insights), or mock/no-key flows |
| 4 | **API** — `api_bridge.py` stdin/JSON smoke, Express `/api/status` and related routes |
| 5 | **UI** — Optional browser smoke on the local web server |
| 6 | **Deploy context** — GitHub Pages vs full-stack; links to workflows |

The doc also includes prerequisites, a test matrix (automated vs manual vs network), a results log table, security notes, and troubleshooting.

**Automated stack check:** `python scripts/run_implementation_tests.py` (after `pip install -r requirements.txt`; flags and manual-only phases: [implementationtest.md](implementationtest.md)).

## License

This project is licensed under the [MIT License](https://opensource.org/licenses/MIT).

Copyright (c) 2026 TrustWise contributors

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.

## Contributing

1. Fork the repository and create a branch for your change.
2. Install dependencies (`pip install -r requirements.txt`; for web work, `cd web && npm ci`).
3. Run tests before opening a PR: `python test_basic.py`, `python test_comprehensive.py`, and `cd web && npm run build` (or `python scripts/run_implementation_tests.py` — see [implementationtest.md](implementationtest.md)).
4. Open a pull request against `main` with a clear description of what changed and why.

For a full manual sign-off of the stack, follow [implementationtest.md](implementationtest.md).
