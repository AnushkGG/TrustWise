# TrustWise Implementation Status

This document tracks the status of all modules in TrustWise, specifying completed features, gaps, and roadmap tasks.

---

## 📊 Summary Status
* **Current Implementation Percentage**: **85%**
* **Active Sprint**: Sprint 03 (Academic Retrieval Enhancements - Scopus & PubMed Abstracts)

---

## 🧩 Module Status Table

| Module | Category | Status | Notes |
| :--- | :--- | :--- | :--- |
| **Query Planner** | Core Pipeline | **Completed** | Generates structured JSON plans. Default LLM changed from Ollama to Gemini. |
| **Chunker** | Core Pipeline | **Completed** | Upgraded from placeholder to production-ready DAG builder. Resolves dependencies and deduplicates. |
| **Scheduler** | Core Pipeline | **Completed** | DAG-based scheduling with parallel execution using `ThreadPoolExecutor`. |
| **Source Collectors** | Agents / Scrapers | **Completed** | Full metadata extraction (abstracts, citation counts, keywords, journals, authors) added to PubMed and Scopus. |
| **Trust Scoring** | Validation | **Completed** | Upgraded heuristics to evaluate DOI, keywords, journal, and citation count fields. |
| **Content Cleaner** | Normalization | **Completed** | Normalizes result schemas and strips cookie boilerplate lines. Supports new metadata fields. |
| **Database Storage** | Persistence | **Completed** | SQLite storage with deterministic hash deduping and backward-compatible metadata column migrations. |
| **RAG / Insights** | Synthesis | **Completed** | Consensus verification and metadata-enriched context templates for LLM summaries. |
| **Web Dashboard UI** | Frontend | **Completed** | Modern premium dark-mode dashboard (port 5001) querying Flask API (port 5000). |
| **Chat Assistant Widget**| Frontend | **Mocked / Not Started** | Front-end widget is a client-side mockup; not connected to Flask backend. |
| **PDF Reporting** | Utilities | **Partially Completed** | Relies on client-side `window.print()` instead of backend PDF rendering. |

---

## 🎯 Task Roadmap & Backlog

### P0 – Critical (System and Setup)
*None. All setup errors, missing configs, CORS blockages, and Windows terminal crashes are fully resolved.*

### P1 – Core Gaps
- [x] **Academic Retrieval Enhancement (PubMed & Scopus)**: Replace stub abstract values with full, real academic XML/JSON metadata extraction (abstracts, keywords, journals, authors).
- [ ] **Chat Assistant Integration**: Connect the client-side chat panel widget to the Flask pipeline API to allow interactive query runs.
- [ ] **Express API Bridge Cleanup**: Remove or retire the unused `api_bridge.py` since Express acts only as a static file server and Flask directly imports Python files.

### P2 – Important Enhancements
- [ ] **Replace Synthetic DeepSeek adapter**: Query real indices rather than prompting DeepSeek chat to synthesize imaginary paper titles and abstracts.
- [ ] **SQLAlchemy Connection Pooling**: Add proper connection locks or SQLAlchemy to SQLite interactions to avoid database locks under concurrent load.
- [ ] **Semantic Scoring / Embeddings**: Move Trust scoring from simple lowercase overlap checking to semantic text similarity.

### P3 – Nice-to-Have
- [ ] **Backend PDF Generation**: Use ReportLab/WeasyPrint to generate structured PDF reports for research queries.
- [ ] **Advanced HTML cleaning**: Replace manual boilerplate string stripping with `trafilatura` or `readability`.

---

## 🏗️ Current Architecture Overview
The system relies on a decoupled, pipeline execution model:

```
[Web UI Dashboard] (Port 5001, Express Static File Server)
       │
   (HTTP)
       ▼
[Flask Backend API] (Port 5000, legacy/app.py)
       │
       ├─► [Query Planner] (LLM plan generation / Gemini fallback)
       ├─► [Chunker] (DAG building, deduplication)
       ├─► [Scheduler] (ThreadPoolExecutor, parallel executing)
       │         │
       │         ├─► [Web Agent] (DuckDuckGo + BeautifulSoup/Crawl4AI)
       │         └─► [Research Agent] (PubMed EFetch, arXiv, Semantic Scholar, Scopus COMPLETE)
       │
       ├─► [Content Cleaner] (Normalization)
       ├─► [Trust Engine] (Heuristic Scoring with Metadata Richness)
       ├─► [SQLite DB] (storage/db.py query caching + metadata columns)
       └─► [Insights Engine] (Metadata-enriched RAG summaries)
```
