# Changelog

All notable changes to this project are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html)
where versioning applies.

## [Unreleased]

## [0.3.0] - 2026-07-26

### Added
- **Academic Retrieval Enhancements (Sprint 03)**:
  - Replaced the PubMed placeholder summary API with PubMed EFetch XML querying, enabling full abstract, DOI, keywords, MeSH terms, journal, and author extraction.
  - Upgraded the Scopus adapter to retrieve COMPLETE details (abstract, citation count, keywords, journal) with automatic authentication fallbacks.
  - Added SQLite migration checks for `journal`, `citation_count`, and `keywords` columns.
  - Expanded Trust scoring heuristics to evaluate academic metadata metrics.
  - Enriched RAG generator summary context with rich authors/journal/citations metadata details.
  - Added new unit test validations for XML parsing and credential fallback errors.

## [0.2.0] - 2026-07-26

### Added
- **DAG Chunker & Scheduler Upgrades (Sprint 02)**:
  - Designed task decomposition, overlap-ratio deduplication, and dependency checking.
  - Implemented parallel chunk executor using ThreadPoolExecutor for concurrent web/paper queries.
  - Integrated Flask, CLI, API bridge, and continuous updates.

### Changed
- LLM defaults changed to Gemini (`gemini-1.5-flash`).
- Enabled CORS support on Flask backend API.

## [0.1.0] - 2026-03-31

### Added
- Baseline TrustWise pipeline: orchestrator, agents, cleaner, trust, storage, insights, `api_bridge.py`, and TypeScript web server under `web/`.
- Operational and verification documentation (`QUICKSTART`, `implementationtest`, deployment readiness notes, implementation phase pack).

---

Earlier granular history is available in the Git commit log and in [implementation-phases/](implementation-phases/README.md) where applicable.
