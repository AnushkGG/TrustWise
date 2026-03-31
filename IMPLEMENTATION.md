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

## Runtime Capabilities

- Provider modes: Ollama, Gemini, or both.
- Query-derived mock planning when external provider is unavailable.
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

