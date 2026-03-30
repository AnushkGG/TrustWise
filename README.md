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

**Not in Phase 1**: Trust validation, credibility scoring, LLM-based summarization, database storage

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
Raw Data Storage (local files)
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
  - `web_agent.py`: Web scraping with BeautifulSoup
  - `research_agent.py`: arXiv paper retrieval

- **utils/**: Shared utilities
  - `config.py`: Configuration management
  - `logger.py`: Logging setup

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
python app.py
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
TrustWise_Anushk/
│
├── main.py                    # CLI entry point
├── app.py                     # Web interface (Flask)
├── demo.py                    # Demo script
├── setup.py                   # Setup automation
├── test_basic.py              # Basic tests
├── start_web.bat              # Windows web launcher
├── start_web.sh               # Linux/Mac web launcher
├── requirements.txt           # Python dependencies
├── .env.example              # Environment template
├── .gitignore                # Git ignore rules
│
├── templates/                 # HTML templates
│   └── index.html            # Main web interface
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
│   └── scheduler.py
│
├── agents/                   # Execution agents
│   ├── __init__.py
│   ├── web_agent.py          # Web scraping
│   └── research_agent.py     # arXiv papers
│
├── utils/                    # Utilities
│   ├── __init__.py
│   ├── config.py             # Configuration management
│   └── logger.py             # Logging setup
│
├── config/                   # Config files
│   └── sources.json          # Trusted sources
│
└── data/                     # Output directory
    ├── plans/                # Execution plans
    │   └── .gitkeep
    └── raw/                  # Raw agent outputs
        └── .gitkeep
```

## Key Design Principles

1. **Planning-First**: LLM used only for orchestration, not answering
2. **Structured Contracts**: All plans are JSON with strict validation
3. **Agent Simplicity**: Agents collect data, don't reason or validate
4. **Auditability**: All plans and outputs saved for reproducibility
5. **No Trust Validation**: Phase 1 focuses on execution flow, not verification

## Future Phases

- **Phase 2**: Trust validation, credibility scoring, source verification
- **Phase 3**: LLM-based summarization with citation tracking
- **Phase 4**: Database integration, user feedback loops

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
