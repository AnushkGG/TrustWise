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

High-level flow: query to plan JSON, then agents, normalization, trust, storage, and insights. **Diagrams** (pipeline, repo layout, web bridge, LLM modes): [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

```text
Query -> Orchestrator -> Chunker -> Scheduler -> Agents
      -> Cleaner -> Trust Validator -> Storage -> Insights
```

## Quick Start (Recommended: Docker)

The fastest and most stable way to run TrustWise is via Docker:

```bash
# 1. Clone and enter
git clone https://github.com/abhishekeb211/TrustWise.git
cd TrustWise

# 2. Setup environment
copy .env.example .env
# Edit .env and set your keys (see Configuration Notes)

# 3. Launch with Docker Compose
docker-compose up --build
```
Access the UI at `http://localhost:5000`.

## Quick Start (Native)

If you prefer to run natively, ensure you have Python 3.11 and Node.js 20+ installed:

```bash
pip install -r requirements.txt
copy .env.example .env
python main.py
```

For the web UI:

```bash
cd web && npm ci && npm run build && npm start
```

## Configuration Notes

- `LLM_PROVIDER` supports `ollama`, `gemini`, or `both`.
- Gemini requires `GEMINI_API_KEY` when `LLM_PROVIDER` is `gemini` or `both` (`Config.validate()`). Model name: `GEMINI_MODEL` or fallback `LLM_MODEL` (`Config.get_gemini_model()`).
- Never commit `.env`; rotate keys in the provider console if they are exposed.
- Runtime mock fallback is disabled by default (`ALLOW_MOCK_FALLBACK=false`).
- Research adapters support multi-source fanout (arXiv, OpenAlex, Semantic Scholar, Crossref, PubMed, CORE, DOAJ, BASE, bioRxiv, medRxiv). Optional key-gated tools (Tavily, Exa, Firecrawl, Jina, Scopus, DeepSeek) are enabled only when the corresponding env vars are set; see `.env.example`.

## Documentation index

| Doc | Purpose |
|-----|---------|
| [.env.example](.env.example) | Environment template (copy to local `.env`; do not commit secrets) |
| [QUICKSTART.md](QUICKSTART.md) | CLI setup, security notes, web preflight |
| [WEB_QUICKSTART.md](WEB_QUICKSTART.md) | Express app, smoke URLs, bridge checks |
| [FRONTEND.md](FRONTEND.md) | REST contract, submit/status payloads, client workflow |
| [IMPLEMENTATION.md](IMPLEMENTATION.md) | What is implemented, known gaps, verification commands |
| [implementationtest.md](implementationtest.md) | CI phases, diagnostics table, sign-off |
| [docs/deployment-readiness-report.md](docs/deployment-readiness-report.md) | Readiness checklist and risks |
| [logs/README.md](logs/README.md) | Local audit logs under `logs/local-test/` |
| [implementation-phases/README.md](implementation-phases/README.md) | Historical 40-phase pack (see **implementationtest** for current checks) |
| [docs/README.md](docs/README.md) | Index of files under `docs/` |
| [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) | Diagrams: pipeline, planner boundary, repo layout, web bridge |
| [LICENSE](LICENSE) | MIT license text |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Dev setup, tests, PR expectations |
| [SECURITY.md](SECURITY.md) | Vulnerability reporting |
| [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md) | Community standards (Contributor Covenant 2.1) |
| [CHANGELOG.md](CHANGELOG.md) | Release notes (Keep a Changelog) |

## Community

- **Contributing:** [CONTRIBUTING.md](CONTRIBUTING.md)
- **Security:** [SECURITY.md](SECURITY.md)
- **Code of conduct:** [CODE_OF_CONDUCT.md](CODE_OF_CONDUCT.md)
- **Changelog:** [CHANGELOG.md](CHANGELOG.md)
- **License:** [LICENSE](LICENSE) (MIT)

## Documentation changelog

- Phase execution pack and unified onboarding/frontend docs.
- Latest alignment: Gemini/Ollama + mock fallback, `execution` / keyed-provider metrics, no-data troubleshooting.

## Verification

```bash
python test_basic.py
python test_comprehensive.py
python scripts/run_implementation_tests.py --ci
```

## Project Status

The repository is maintained as one integrated pipeline. Historical "phase" labels in code comments should be interpreted as internal milestones, not separate products.

