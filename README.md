# TrustWise - LLM Orchestrator

This is a modular LLM-based orchestrator framework designed to plan, chunk, and execute research tasks across different sources (Web, Research Papers).

## Project Structure

```
trustwise/
│
├── main.py              # Entry point
│
├── orchestrator/        # Planning Layer
│   ├── orchestrator.py  # Core logic
│   ├── llm_client.py    # LLM abstraction (currently mocked)
│   ├── schema.py        # JSON Plan validation
│   └── prompts.py       # Prompt templates
│
├── chunker/             # Task Decomposition
│   └── chunker.py
│
├── scheduler/           # Source-based Routing
│   └── scheduler.py
│
├── agents/              # 🤖 AGENTS (Execution Layer)
│   ├── web_agent.py     # Web Search Agent
│   └── research_agent.py# Research Paper Agent
│
├── pipelines/           # [DEPRECATED -> Moved to agents/]
│
├── utils/
│   └── logger.py
│
└── config/
    └── sources.json
```

## How to Run

1.  Make sure you have Python installed.
2.  Run the main script:

```bash
python main.py
```

3.  Enter a query when prompted. The orchestrator will generate a plan (mocked for now) and execute the pipeline stubs.

## Next Steps

1.  Replace `orchestrator/llm_client.py` with a real API client (e.g., OpenAI).
2.  Implement real logic in `pipelines/`.
3.  Add database storage for plans.
