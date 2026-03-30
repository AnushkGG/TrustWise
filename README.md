# TrustWise - Trust-First AI System (Phase 1)

A trust-first, agent-based AI system for collecting and preparing technology-related information through controlled, auditable execution.

## Overview

TrustWise follows a **planning-first architecture** where an LLM is used exclusively for orchestration, not for answering questions. The system converts natural language queries into structured JSON execution plans, then routes tasks to specialized agents that collect raw data without validation or summarization.

### Phase 1 Scope

Phase 1 establishes the core orchestration and execution pipeline:

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
  - `research_agent.py`: arXiv paper retrieval

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

## Installation

### 1. Clone Repository

```bash
git clone <repository-url>
cd TrustWise_Anushk
```

### 2. Create Virtual Environment

```bash
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Configure Environment

Create a `.env` file from the example:

```bash
copy .env.example .env  # Windows
# cp .env.example .env  # Linux/Mac
```

Edit `.env` and add your API key:

```env
LLM_PROVIDER=gemini
GEMINI_API_KEY=your_actual_api_key_here
LLM_MODEL=gemini-2.0-flash
```

Or use a local Ollama model (no API key needed):

```env
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
LLM_MODEL=llama3
```

**Note**: The system works with mock responses if no API key is provided (for testing).

## Usage

### Option 1: Web Interface (Recommended)

The easiest way to use TrustWise is through the web interface:

```bash
# Windows
start_web.bat

# Linux/Mac
chmod +x start_web.sh
./start_web.sh

# Or directly
cd web && npm run build && npm start
```

Then open your browser to: **http://localhost:5000**

**Features:**

- 🎨 Modern, user-friendly interface
- 📊 Visual execution progress
- 📈 Results visualization
- 📜 View execution history
- 🔍 Detailed task results

See [FRONTEND.md](FRONTEND.md) for complete documentation.

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

| Variable              | Default            | Description                         |
| --------------------- | ------------------ | ----------------------------------- |
| `LLM_PROVIDER`        | `gemini`           | LLM provider: `gemini` or `ollama`  |
| `GEMINI_API_KEY`      | -                  | Google Gemini API key               |
| `OLLAMA_BASE_URL`     | `localhost:11434`  | Local Ollama server URL             |
| `LLM_MODEL`           | `gemini-2.0-flash` | Model to use                        |
| `LLM_TEMPERATURE`     | `0.0`              | Temperature (0 for deterministic)   |
| `LLM_MAX_TOKENS`      | `2000`             | Max tokens in response              |
| `WEB_SCRAPER_TIMEOUT` | `10`               | HTTP request timeout (seconds)      |
| `ARXIV_MAX_RESULTS`   | `5`                | Max papers per search               |
| `SAVE_PLANS`          | `true`             | Save plans to `data/plans/`         |
| `SAVE_RAW_DATA`       | `true`             | Save agent outputs to `data/raw/`   |
| `LOG_LEVEL`           | `INFO`             | Logging level                       |
| `FLASK_SECRET_KEY`    | auto-generated     | Secret key for sessions             |
| `FLASK_DEBUG`         | `false`            | Enable debug mode                   |

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
├── app.py                     # Legacy web interface (Flask, kept for reference)
├── api_bridge.py              # Python API bridge for TypeScript server
├── demo.py                    # Demo script
├── continuous_update.py       # Periodic update runner
├── setup.py                   # Setup automation
├── test_basic.py              # Basic tests
├── test_comprehensive.py      # Comprehensive tests
├── start_web.bat              # Windows web launcher
├── start_web.sh               # Linux/Mac web launcher
├── requirements.txt           # Python dependencies
├── .env.example              # Environment template
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
│   └── research_agent.py     # arXiv papers
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

## Completed Phases

- **Phase 1**: Core orchestration, task scheduling, data collection
- **Phase 2**: Data normalization and cleaning
- **Phase 3**: Zero-trust validation and credibility scoring
- **Phase 4**: SQLite database integration with deduplication
- **Phase 5**: LLM-based summarization with citation tracking
- **Phase 6**: DB caching for repeated queries

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

## License

[Add your license here]

## Contributing

[Add contribution guidelines here]
