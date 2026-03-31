# TrustWise implementation test plan

Operational checklist to validate the full codebase in order: **automated CI parity first**, then **configuration and LLM modes**, **API smoke**, **optional UI**, and **deployment context**. For architecture details, see [IMPLEMENTATION.md](IMPLEMENTATION.md).

### How to proceed

1. Complete **Phase 1** on every machine and after every significant pull (same commands as GitHub Actions).
2. Complete **Phase 2** once per environment (or when changing `.env`).
3. Run **one** subsection of **Phase 3** that matches production (Ollama, Gemini, `both`, or mock-only).
4. Run **Phase 4** before relying on the web UI or integrations.
5. Use **Phase 5** when validating UX; **Phase 6** is read-only context for deploys.
6. Copy the **Recording results** table row when you sign off a release.

### Automation script (replaces most manual copy-paste)

From the **repository root**, after `pip install -r requirements.txt` and with **Node.js** on your PATH (for `npm ci` / `npm run build`):

```bash
python scripts/run_implementation_tests.py
```

This runs **Phase 1** (same as CI: `test_basic.py`, `test_comprehensive.py`, `web/` `npm ci` + `npm run build`), **Phase 2** if a `.env` file exists (`Config.validate()`), **Phase 4a** (`api_bridge` `status` JSON), and **Phase 4b** (HTTP `GET /api/status` — skipped if nothing is listening, unless you pass `--strict-http`). **`--ci` and `--no-http` both skip Phase 4b** (use `--ci` in automation with no server; use `--no-http` locally when you only want Phases 1–2 and 4a).

| Flag | Meaning |
|------|---------|
| `--ci` | Skip Phase 4b (used in [`.github/workflows/ci.yml`](.github/workflows/ci.yml); runners have no Express server). |
| `--http` | Run Phase 4b (default: on). Explicit for clarity next to `--no-http`. |
| `--no-http` | Skip Phase 4b. |
| `--strict-http` | Fail if the Express server is not reachable at the check URL. |
| `--no-npm` | Skip web build (only if you already built). |
| `--no-config` | Skip `Config.validate()`. |
| `--no-bridge` | Skip `api_bridge` smoke. |

Set `TRUSTWISE_STATUS_URL` to override the HTTP check URL (default `http://127.0.0.1:5000/api/status`).

**Still manual:** Phase 3 (live Ollama / Gemini / `both`), Phase 5 (browser UX), Phase 6 (deploy expectations). Phase 3 mock behavior is already covered by unit tests inside Phase 1.

---

## Prerequisites

| Requirement | Notes |
|-------------|--------|
| Python | **3.11** matches [`.github/workflows/ci.yml`](.github/workflows/ci.yml). **3.10–3.12** are reasonable locally. On Windows, **3.14** may fail building `lxml`; prefer 3.10–3.12 (see [README.md](README.md)). |
| Node.js | **18+**; CI uses **20** for the web build. |
| Virtual environment | Recommended: `python -m venv venv` then activate before `pip install`. |
| Optional: Ollama | For `LLM_PROVIDER=ollama` or `both`: [Ollama](https://ollama.com) running, model pulled (e.g. `ollama pull llama3.2`). |
| Optional: Gemini | For `LLM_PROVIDER=gemini` or `both`: `GEMINI_API_KEY` in **local** `.env` only; never commit secrets. |

**Windows encoding:** If console output garbles Unicode in tests, set `PYTHONIOENCODING=utf-8` (CI sets this for Python test steps).

---

## Test matrix

| Area | Automated | Needs network | Needs API key / Ollama |
|------|-----------|---------------|-------------------------|
| Phase 1 (CI parity) | Yes — [scripts/run_implementation_tests.py](scripts/run_implementation_tests.py) | No (pip/npm registries only) | No |
| Phase 2 (`.env` / validate) | Yes — same script if `.env` exists | No | Only if you set Gemini |
| Phase 3 (LLM paths) | Partial (mock + merge in unit tests; live paths manual) | Yes for real agents | Yes for Gemini; Ollama for local/both |
| Phase 4a (bridge `status`) | Yes — same script | No | No |
| Phase 4b (HTTP `/api/status`) | Yes — same script (tries locally; soft-skip if down unless `--strict-http`; **not run** in CI — use `--ci`) | Local server when check runs | No |
| Phase 4 `submit` / agents | No (use bridge or UI manually) | Yes | Same as Phase 3 for real LLM |
| Phase 5 (browser UI) | No | Yes | Same as Phase 3 |
| Phase 6 (deploy) | N/A | N/A | N/A |

---

## Phase 1 — CI-equivalent (no secrets, no Ollama)

**Goal:** Match [`.github/workflows/ci.yml`](.github/workflows/ci.yml) locally.

From the **repository root** (with venv activated):

```bash
pip install -r requirements.txt
```

**Windows CMD:**

```bat
set PYTHONIOENCODING=utf-8
python test_basic.py
python test_comprehensive.py
```

**Windows PowerShell:**

```powershell
$env:PYTHONIOENCODING = "utf-8"
python test_basic.py
python test_comprehensive.py
```

On Linux/macOS:

```bash
export PYTHONIOENCODING=utf-8
python test_basic.py
python test_comprehensive.py
```

**Web build (CI uses Node 20, `npm ci`):**

```bash
cd web
npm ci
npm run build
cd ..
```

**Pass criteria**

- `test_basic.py` exits **0** (currently 9 tests).
- `test_comprehensive.py` exits **0** (currently 38 tests).
- `npm ci` and `npm run build` in `web/` exit **0**.

---

## Phase 2 — Environment and configuration

**Goal:** `.env` is consistent with how you intend to run (CLI, bridge, or web).

1. Copy [`.env.example`](.env.example) to `.env` and edit.
2. Confirm `LLM_PROVIDER` is one of: `ollama`, `gemini`, `both`.
3. Optional: run validation from repo root:

```bash
python -c "from utils.config import Config; Config.validate(); print('OK')"
```

**Pass criteria**

- Command prints `OK` without `ValueError`.
- If `LLM_PROVIDER` is `gemini` or `both`, `GEMINI_API_KEY` is set in `.env` (not in git).

**Notes**

- `both` mode requires a Gemini key **and** a reachable Ollama server for full dual-provider behavior; see Phase 3.

---

## Phase 3 — LLM provider paths

Exercise **at least one** path relevant to your setup. Automated tests already cover **mock** and **merge helpers** without live APIs.

### A. Mock / no cloud key (quick)

- Set `LLM_PROVIDER=gemini` and **omit** `GEMINI_API_KEY`, **or** use paths that trigger mock plans as documented in [README.md](README.md).
- Run Phase 4 **status** check; planning may use query-derived mock (`plan_source: mock`).

**Pass criteria:** No unhandled exceptions when generating a plan via pipeline or bridge.

### B. Ollama only

```env
LLM_PROVIDER=ollama
OLLAMA_BASE_URL=http://localhost:11434
LLM_MODEL=llama3.2
```

- Start Ollama; ensure the model is pulled.

**Pass criteria:** Plan generation succeeds; logs show Ollama usage (not mock) when Ollama is up.

### C. Gemini only

```env
LLM_PROVIDER=gemini
GEMINI_API_KEY=<your key>
LLM_MODEL=gemini-2.0-flash
```

**Pass criteria:** Plan generation succeeds against Gemini (no auth errors in logs).

### D. Both (parallel merge)

```env
LLM_PROVIDER=both
GEMINI_API_KEY=<your key>
# Optional per-provider overrides:
# GEMINI_MODEL=gemini-2.0-flash
# OLLAMA_MODEL=llama3.2
```

- Ollama must be running for the Ollama leg; merged plans may include `plan_source: merged`, `providers`, and per-task `origin` (`gemini`, `ollama`, `both`). Insights in merged mode may include `concise_answer_origin` and key points as `{text, origin}`.

**Pass criteria:** Both providers reachable, or documented fallback (single provider or mock) with warnings in logs, not a crash.

---

## Phase 4 — API bridge and HTTP smoke (local)

### 4a. Python bridge (stdin/stdout JSON)

From **repo root** (use the same Python as your venv; on Windows you can set `PYTHON_EXE` / `TRUSTWISE_PYTHON` when using the Node server):

**PowerShell:**

```powershell
'{"action":"status"}' | python api_bridge.py
```

**Bash:**

```bash
echo '{"action":"status"}' | python api_bridge.py
```

**Pass criteria**

- Single JSON object on **stdout** with `"success": true`.
- `status` includes `llm_provider`, `llm_model`, `has_api_key`, `ollama_reachable`, `gemini_configured`, and `providers_available` (list of configured/reachable backends).

Optional (may run full pipeline and hit the network):

```bash
echo '{"action":"submit","query":"short test query about AI"}' | python api_bridge.py
```

**PowerShell (optional submit):**

```powershell
'{"action":"submit","query":"short test query about AI"}' | python api_bridge.py
```

Expect a JSON result; stderr may contain logs.

### 4b. Express server (`web/`)

After Phase 1 build:

```bash
cd web
npm start
```

Default URL: **http://127.0.0.1:5000** (see `PORT` / `HOST` in [web/src/server.ts](web/src/server.ts)).

| Method | Path | Purpose |
|--------|------|---------|
| GET | `/api/status` | Same info as bridge `status` |
| POST | `/api/submit` | Body: `{"query":"..."}` |
| GET | `/api/plans` | List saved plans |
| GET | `/api/raw-data` | List raw task files |

**Pass criteria**

- `GET /api/status` returns JSON with `"success": true`.
- If Python is not on PATH correctly, set `PYTHON_EXE` or `TRUSTWISE_PYTHON` to your venv’s `python` before `npm start`.

---

## Phase 5 — End-to-end UI smoke (optional)

1. Open **http://127.0.0.1:5000** (or your `HOST`/`PORT`).
2. Submit a short query.
3. Confirm the UI shows progress and a result (plan summary, insights, sources as applicable).

**Pass criteria:** Subjective: page loads, submit completes without a generic 500 error.

---

## Phase 6 — Deployment and GitHub (informational)

- **Static site:** GitHub Pages from `docs/` (see [README.md](README.md) — does **not** run the Python/Node pipeline).
- **Full stack:** Container or VM with Python + Node + optional Ollama/Gemini per README.
- **CI:** [`.github/workflows/ci.yml`](.github/workflows/ci.yml) runs on push/PR to `main`/`master`.

No local “pass/fail” for this phase; use it to set expectations for hosted vs local testing.

---

## Recording results

Use this table when signing off a release or environment.

| Date | Git commit | OS | Phase 1 | Phase 2 | Phase 3 mode | Phase 4 | Phase 5 | Notes |
|------|------------|-----|---------|---------|--------------|---------|---------|-------|
| | | | ☐ | ☐ | | ☐ | ☐ | |
| 2026-03-30 | *(fill `git rev-parse --short HEAD`)* | Windows | OK | *(optional)* | mock (unit tests) | bridge `status` OK | *(optional)* | Example row: Phase 1 = tests 9/9 + comprehensive 38/38 + `npm ci` / `npm run build`; Phase 4a = JSON success from `api_bridge` |

Replace or remove the example row when recording your own sign-off.

---

## Security

- Do **not** commit `.env` or paste API keys into chat, tickets, or screenshots.
- Rotate any key that was exposed.

---

## Troubleshooting

| Symptom | Things to check |
|---------|-------------------|
| `lxml` build failure on Windows | Use Python 3.10–3.12 or install XML build prerequisites; align with CI 3.11. |
| Ollama connection errors | `OLLAMA_BASE_URL`, firewall, `ollama serve`, model pulled. |
| Gemini 401 / auth | `GEMINI_API_KEY`, quota, model id in `LLM_MODEL` / `GEMINI_MODEL`. |
| Bridge returns error from Node | `PYTHON_EXE` / `TRUSTWISE_PYTHON` pointing to venv `python`; run bridge from repo root. |
| Tests fail after pull | Re-run `pip install -r requirements.txt` and `cd web && npm ci && npm run build`. |

---

## Related files

- [scripts/run_implementation_tests.py](scripts/run_implementation_tests.py) — automation entrypoint
- [`.github/workflows/ci.yml`](.github/workflows/ci.yml) — CI runs `python scripts/run_implementation_tests.py --ci`
- [test_basic.py](test_basic.py), [test_comprehensive.py](test_comprehensive.py)
- [api_bridge.py](api_bridge.py)
- [utils/config.py](utils/config.py)
- [web/src/server.ts](web/src/server.ts) — default `HOST` / `PORT` for Phase 4b
- [orchestrator/llm_client.py](orchestrator/llm_client.py)
- [insights/generator.py](insights/generator.py)
