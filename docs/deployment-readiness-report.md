# TrustWise deployment readiness report

Generated: 2026-03-30  
Last verified: 2026-03-31 (doc refresh): `test_basic` **9/9**, `test_comprehensive` **38/38** (47 total), `npm ci` + `npm run build` OK; CI parity is also run via `python scripts/run_implementation_tests.py --ci` ([`.github/workflows/ci.yml`](../.github/workflows/ci.yml)). Earlier API/browser run (2026-03-30): `GET /api/status`, `/api/plans`, `/api/raw-data`, `POST /api/submit` (short query), empty-query **400**; browser `/` loads.  
Scope: CI-parity automated checks, multi-statement API/runtime validation, prioritized findings.

## 1. Test execution summary

### CI parity (GitHub Actions equivalent)

| Step | Result | Notes |
|------|--------|--------|
| `pip install -r requirements.txt` | Pass | Used **Python 3.10** (`py -3.10`). Default **Python 3.14** often fails building `lxml` on Windows (no wheel / missing libxml2 headers). CI uses **3.11** (`.github/workflows/ci.yml`). |
| `python test_basic.py` | Pass | **9/9** with `PYTHONIOENCODING=utf-8`. |
| `python test_comprehensive.py` | Pass | **38/38**. |
| `npm ci` + `npm run build` in `web/` | Pass | CI uses **Node 20**; local run used **Node v25.x** (acceptable; build succeeded). |

**Warnings observed**

- `RequestsDependencyWarning`: urllib3/chardet/charset_normalizer version combo mismatch (`requests` package).
- Retry test logs print to stderr (expected; tests still pass).

### Multi-statement runtime (Express + `api_bridge.py`)

Server started with **Python 3.10** first on `PATH` so `python` matches the environment with dependencies (`web/src/server.ts` uses `execFile("python", ...)`).

| Check | Result |
|-------|--------|
| `GET /api/status` | `success: true`; `ollama_reachable: false`, `gemini_configured: false` (expected without services/keys). |
| `GET /api/plans` | `success: true`; list of saved plans with metadata. |
| `GET /api/plan/:filename` | `success: true` for valid basename; returns full plan JSON. |
| `GET /api/raw-data` | `success: true`; `files: []` when no raw task files exist. |
| `POST /api/submit` — short query | `success: true`; full pipeline response. |
| `POST /api/submit` — medium multi-sentence | `success: true`. |
| `POST /api/submit` — Unicode / emoji | `success: true`; JSON round-trip OK. |
| `POST /api/submit` — empty body | **400** `{"success":false,"error":"Query cannot be empty"}` |
| Browser `/` | Page loads; query input, example chips, Run pipeline, sections present. |

**Behavioral notes**

- With **Ollama unreachable** and **no Gemini key**, planning uses a **query-derived mock plan** with `plan_source: "mock"` (`orchestrator/llm_client.py`). Goals and prompts reflect the submitted query; the UI may still show **Default LLM: local Ollama** when Ollama is down.
- **Web agent** tasks often returned `status: "partial"` with `message: "No data collected from any source"` (environment/network dependent).
- **Research agent** often succeeded with arXiv / OpenAlex / Semantic Scholar results.
- **Mojibake** in some author names in JSON (e.g. `Gu�don`) suggests encoding handling at source or console display—verify UTF-8 end-to-end.

---

## 2. CI / environment parity

| Item | CI | Local validation |
|------|----|------------------|
| Python | 3.11 | 3.10 used (3.14 fails `lxml` build) |
| Node | 20 | 25.x (build OK) |
| Ollama / API keys | Not required | Optional; mock fallback |
| Automation script | `python scripts/run_implementation_tests.py --ci` on push/PR | Same command locally for CI parity (skips HTTP); see [implementationtest.md](../implementationtest.md) |

---

## 3. Prioritized findings

### Critical

None found for automated CI or core API contracts; empty-query validation works.

### High

1. **Mock plan ignores user query** — **addressed (2026-03-30)**  
   - **Was:** `call_llm` returned a static JSON plan.  
   - **Now:** `build_mock_plan()` in [`orchestrator/llm_client.py`](orchestrator/llm_client.py) derives `goal`, `domains`, and task `prompt`s from the user query; plans include `plan_source: "mock"`.  
   - **Remaining:** Surface `plan_source` in the web UI when desired.

2. **Windows / Python 3.14: `pip install` failure on `lxml`** — **partially addressed**  
   - **Repro:** `pip install -r requirements.txt` with default Python 3.14 on Windows.  
   - **Cause:** No prebuilt wheel; build needs libxml2 headers.  
   - **Done:** README recommends Python 3.11 (CI parity) and warns about 3.14 + `lxml`.  
   - **Optional follow-up:** `python_requires` in packaging or optional `lxml` extra.

3. **`python` on PATH vs installed deps** — **addressed (2026-03-30)**  
   - **Now:** [`web/src/server.ts`](web/src/server.ts) uses `PYTHON_EXE` or `TRUSTWISE_PYTHON` when set, else `python`. Documented in README.

### Medium

4. **`RequestsDependencyWarning`**  
   - **Fix:** Align `urllib3` / `charset-normalizer` / `chardet` with `requests` supported set (pin in `requirements.txt` or relax).  
   - **Verify:** `python -W error::RequestsDependencyWarning` or clean run without warning.

5. **Rate limit (60/min)** (`server.ts`)  
   - Scripted multi-submit tests could hit limit; document for load testing.

6. **Web scraping reliability**  
   - Partial web tasks with no data may be normal for locked-down environments; consider clearer user messaging and retries.

### Low

7. **Documentation drift** — **addressed (2026-03-31)**  
   - Test counts: **9** basic + **38** comprehensive = **47** total ([`IMPLEMENTATION.md`](../IMPLEMENTATION.md) completion table). Full-stack sign-off: [implementationtest.md](../implementationtest.md); one-command automation: `scripts/run_implementation_tests.py`.

---

## 4. Verification checklist (post-fix)

- [x] CI green on `main` (GitHub Actions). *(Verified 2026-03-31: latest [`ci.yml`](https://github.com/AnushkGG/TrustWise/actions/workflows/ci.yml) run on `main` **success** via GitHub API; e.g. run id `23760161697` for commit `1dc064ae` — re-check [Actions](https://github.com/AnushkGG/TrustWise/actions) after new pushes.)*  
- [x] Local: `py -3.11` (or 3.10) + `npm ci` + `npm run build` + both test scripts. *(Verified 2026-03-31: `python scripts/run_implementation_tests.py --ci` exit 0 — same steps as [`.github/workflows/ci.yml`](../.github/workflows/ci.yml) for Phases 1–2 skip / 4a.)*  
- [ ] With Ollama or Gemini configured: plans reflect user query. *(Requires `.env` and live providers — manual.)*  
- [ ] With mock only: UI/API indicate mock mode. *(Manual browser/API check.)*  
- [x] `/api/submit` empty query returns 400. *(Recorded in §1 multi-statement runtime table, 2026-03-30 API run.)*

---

## 5. Evidence artifacts

- CI workflow: `.github/workflows/ci.yml` (runs `python scripts/run_implementation_tests.py --ci`)  
- Automation script: `scripts/run_implementation_tests.py`  
- Bridge: `api_bridge.py`  
- Server: `web/src/server.ts`  
- LLM fallback: `orchestrator/llm_client.py`  

Raw command outputs from this run are available in the session logs (API JSON, browser snapshot).
