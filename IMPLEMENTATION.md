# TrustWise Implementation Summary

This document captures the current implementation baseline for TrustWise.

## Implemented Components

- `orchestrator/`: plan generation, schema validation, provider fallback.
- `chunker/`: task decomposition from plan tasks.
- `scheduler/`: source-aware routing to web/research agents.
- `agents/`: web collection and research-paper collection.
- `cleaner/`: normalization to a shared structured schema.
- `trust/`: trust scoring, filtering, and duplicate handling.
- `storage/`: SQLite persistence and query cache.
- `insights/`: LLM/extractive summary generation.
- `web/` + `api_bridge.py`: Express UI/API over Python pipeline.

Visual overview (Mermaid diagrams): [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

## Runtime Capabilities

- Provider modes: Ollama, Gemini, or both (`LLM_PROVIDER`); Gemini model resolution via `GEMINI_MODEL` / `LLM_MODEL` (`Config.get_gemini_model()`).
- Query-derived mock planning when allowed (`ALLOW_MOCK_FALLBACK=true`) and the planner cannot use the real provider (for example missing Gemini key, Ollama connection failure, or Ollama HTTP 404 on both chat and generate endpoints when mock is enabled).
- Optional key-gated research/web adapters (Tavily, Exa, Firecrawl, Jina, Scopus, DeepSeek): no key means empty contribution without failing the run; metrics appear under `execution.keyed_research_providers` on submit.
- Raw, structured, trusted, and DB persistence controls via `.env`.
- End-to-end web and CLI execution paths.

## Quality and Reliability

- Retry support for transient agent failures.
- Rate limiting for web fetch operations.
- Deterministic config validation and startup checks.
- CI-equivalent checks available locally.

## Verification Commands

```bash
python test_basic.py
python test_comprehensive.py
cd web && npm ci && npm run build
python scripts/run_implementation_tests.py --ci
```

## Known Gaps

- No user authentication.
- No realtime push updates (polling/long request model).
- No built-in PDF/CSV reporting workflow for backend jobs.
- Limited advanced chunking heuristics.

## Canonical Roadmap

Execution planning is documented in the 40-file implementation pack:

- [implementation-phases/README.md](implementation-phases/README.md)
- `implementation-phases/phase-01.md` ... `implementation-phases/phase-40.md`

