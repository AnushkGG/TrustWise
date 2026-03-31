# TrustWise

TrustWise is a trust-first AI pipeline for collecting, validating, storing, and summarizing technology intelligence from web and research sources.

## Core Flow

1. Generate a structured JSON plan from a natural-language query.
2. Chunk and schedule tasks to source-specific agents.
3. Collect raw data from web and research APIs.
4. Normalize records into one schema.
5. Score and filter records with trust validation.
6. Save trusted outputs to SQLite.
7. Generate concise insights.

## Architecture

```text
Query -> Orchestrator -> Chunker -> Scheduler -> Agents
      -> Cleaner -> Trust Validator -> Storage -> Insights
```

## Quick Start

```bash
pip install -r requirements.txt
copy .env.example .env  # Windows
python main.py
```

For the web UI:

```bash
cd web
npm install
npm run build
npm start
```

## Configuration Notes

- `LLM_PROVIDER` supports `ollama`, `gemini`, or `both`.
- Gemini requires `GEMINI_API_KEY` only when Gemini is selected.
- If no provider is available, planning falls back to a query-derived mock plan.

## Documentation Map

- [QUICKSTART.md](QUICKSTART.md): CLI-focused setup and first run.
- [WEB_QUICKSTART.md](WEB_QUICKSTART.md): Web server startup and smoke checks.
- [FRONTEND.md](FRONTEND.md): API and UI behavior details.
- [IMPLEMENTATION.md](IMPLEMENTATION.md): end-to-end implementation status.
- [implementationtest.md](implementationtest.md): verification checklist and test protocol.
- [docs/deployment-readiness-report.md](docs/deployment-readiness-report.md): readiness baseline and deployment checks.
- [implementation-phases/README.md](implementation-phases/README.md): 40-phase implementation execution pack.

## Documentation Changelog

- Consolidated project documentation into a consistent current-state structure.
- Added a detailed phase execution pack in `implementation-phases/` (`phase-01.md` to `phase-40.md`).
- Updated onboarding, frontend, and implementation test docs to align with the same runtime model.

## Verification

```bash
python test_basic.py
python test_comprehensive.py
python scripts/run_implementation_tests.py --ci
```

## Project Status

The repository is maintained as one integrated pipeline. Historical "phase" labels in code comments should be interpreted as internal milestones, not separate products.

