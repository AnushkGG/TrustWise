# TrustWise Project History & Architectural Decisions

This document outlines the major milestones in the development of TrustWise and explains the design decisions that shaped its architecture.

---

## 📅 Chronological Milestones

### 1. Baseline Implementation (Sprint 01)
* **Goal**: Assemble basic orchestrator, scheduling, scraping, caching, and insights pipelines.
* **Architecture**: A Node.js web server (`web/`) communicating with the Python pipeline via stdin/stdout using `api_bridge.py`. The backend executed all tasks in a single-threaded loop. Caching relied on simple SQLite hashing.

### 2. Modern UI & Python API Shift (Transition phase)
* **Goal**: Clean up repository layout and build a premium frontend dashboard.
* **Key Decisions**:
  * **Express UI migration**: The original `web/` folder was deleted, and `frontend2/` was merged/renamed to `frontend/`. The new Express server (`frontend/server.js`) was configured solely to host static files and proxy requests.
  * **Flask API Adoption**: The pipeline execution was shifted into a standalone Flask REST API (`legacy/app.py`). Rather than spawning Python subprocesses via the standard input/output bridge `api_bridge.py`, Flask now directly imports Python pipeline packages and executes them. This bypassed the need for `api_bridge.py` in live client sessions, although it remains in the codebase for automated integration testing.
  * **CORS Requirement**: Because the frontend static client loads on port `5001` and queries the Flask backend on port `5000`, browsers blocked API calls under the Same-Origin Policy. Adding custom Flask `@app.after_request` CORS hooks was necessary to inject access headers (`Access-Control-Allow-Origin: *`) and resolve this.

### 3. Gemini LLM Migration
* **Goal**: Establish a stable default LLM provider for plan generation and insights synthesis.
* **Key Decision**:
  * **Gemini replacing Ollama**: The baseline code was configured to query a local Ollama instance (`llama3.2`). However, Ollama's local startup overhead and latency made it unreliable for production or cloud deployments. Switched default settings to Gemini (`gemini-1.5-flash`), retaining Ollama solely as a fallback option when API keys are absent.

### 4. DAG Chunker & Concurrent Scheduler (Sprint 02)
* **Goal**: Resolve high search latency and implement robust plan scheduling.
* **Key Decisions**:
  * **Why the Chunker was introduced**: The baseline Chunker was a pass-through placeholder. This forced the system to execute plan tasks exactly as returned by the LLM, leading to duplicate prompts and missing dependency structures. The upgraded Chunker normalizes planner tasks, maps semantic and explicit dependencies, and outputs unique, structured execution chunk objects.
  * **Why the Scheduler became DAG-based**: To achieve fast query times, independent task execution had to run concurrently. Modifying the Scheduler to group chunks into topological DAG layers enables parallel execution of non-dependent tasks using a thread pool, sequencing only tasks that have explicit prerequisites (like comparison or synthesis).

### 5. Academic Retrieval Enhancement (Sprint 03)
* **Goal**: Replace stub PubMed/Scopus values with high-quality abstracts and structured metadata, upgrading RAG and zero-trust validation reliability.
* **Key Decisions**:
  * **Why PubMed XML EFetch was selected**: PubMed ESearch returns only article IDs (PMIDs). In baseline, ESummary was queried for metadata, which omitted article abstracts. Upgrading the flow to fetch XML via `efetch.fcgi` and parsing it using the Python built-in XML ElementTree parser allowed for full abstract, DOI, keywords, journal, and MeSH terms retrieval.
  * **Why Scopus View Fallback was implemented**: Scopus Search API supports retrieving full metadata (description/abstract, keywords, citation counts) only when requesting `"view": "COMPLETE"`. Since completing standard queries is constrained by different API keys and developer permission tiers, a two-step try-except fallback was implemented: standard queries first check `"view": "COMPLETE"`, and automatically fall back to standard results if a permission error (401/403/400) is returned.
  * **Why Metadata Richness was added to scoring**: Evaluating academic works solely on whitelisting and length created false positives. Incorporating DOI indicators, journal publication records, keyword presence, and citation counts into [validator.py](file:///c:/Users/salon/OneDrive/문서/websites/Trustwise/TrustWise/trust/validator.py) heuristics makes zero-trust assertions significantly more robust.
