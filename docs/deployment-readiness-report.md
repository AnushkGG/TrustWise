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
- Surface provider status in UI before submit.
- Keep mock plan fallback documented and expected.
- Keep trust validation and DB cache enabled for stable repeated runs.

## Go/No-Go Checklist

- [ ] CI checks green on target branch.
- [ ] Local implementation protocol run completed.
- [ ] `/api/status` and `/api/submit` smoke tested.
- [ ] `.env` secrets handled outside version control.
- [ ] Operational owner approved deployment environment assumptions.

