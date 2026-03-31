# TrustWise Deployment Readiness Report

Generated: 2026-03-31

## Readiness Scope

- CI parity and local validation commands.
- API runtime smoke behavior.
- Operational constraints and mitigations.

## Baseline Evidence

- Python tests pass locally with supported Python runtime.
- Web build passes (`npm ci`, `npm run build`).
- Bridge status and API status endpoints respond successfully.
- Empty-query validation returns proper client error.

## Key Risks

1. Environment mismatch between configured Python and server runtime.
2. Provider unavailability (Ollama/Gemini) causing unexpected user assumptions.
3. Web source variance causing partial collection in restricted networks.

## Mitigations

- Use `PYTHON_EXE`/`TRUSTWISE_PYTHON` for deterministic bridge interpreter.
- Surface provider status in UI before submit (`GET /api/status`: `llm_provider`, `gemini_configured`, `ollama_reachable`).
- Keep mock plan fallback documented (`ALLOW_MOCK_FALLBACK`); clarify that Gemini requires `GEMINI_API_KEY` when `LLM_PROVIDER` is `gemini` or `both`.
- Inspect `execution` and `keyed_research_providers` on successful submits to confirm optional keyed adapters when keys exist.
- Keep trust validation and DB cache enabled for stable repeated runs.

## Go/No-Go Checklist

- [ ] CI checks green on target branch.
- [ ] Local implementation protocol run completed.
- [ ] `/api/status` and `/api/submit` smoke tested.
- [ ] `.env` secrets handled outside version control.
- [ ] Operational owner approved deployment environment assumptions.

