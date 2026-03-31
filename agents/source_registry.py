"""
Source adapter registry for multi-tool research retrieval.

Design goals:
- Isolate each source in its own adapter function.
- Keep a stable unified output schema.
- Support partial success: one source failure never fails the whole task.
- Expose per-source metrics for API/UI observability.
"""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor, as_completed
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Tuple
import urllib.parse

import requests

from agents.keyed_adapters import (
    fetch_deepseek,
    fetch_exa,
    fetch_firecrawl,
    fetch_jina_search,
    fetch_scopus,
    fetch_tavily,
)
from agents.research_sources import (
    dedupe_papers,
    fetch_crossref,
    fetch_openalex,
    fetch_pubmed,
    fetch_semantic_scholar,
    rank_and_filter_relevant,
)
from utils.config import Config
from utils.logger import setup_logger

logger = setup_logger(__name__)

AdapterFn = Callable[[str, int], Any]
TOOL_CATALOG = [
    "DeepSeek LLM API", "OpenAlex API", "Semantic Scholar API", "CORE API", "Crossref API",
    "PubMed API", "DOAJ API", "Science.gov API", "ScienceOpen API", "EBSCO Free Databases API",
    "Dimensions API", "Scilit API", "arXiv API", "bioRxiv / medRxiv API", "Zenodo API",
    "Unpaywall API", "Springer Nature OA API", "PeerJ OA API", "Frontiers OA API", "BASE API",
    "Crawl4AI", "Firecrawl", "Tavily", "Exa", "paperscraper", "Jina AI Reader", "WARC-GPT",
    "Scrapy", "StormCrawler", "SmolCrawl", "LLM Scraper", "PubMed E-Utilities",
    "PLOS Search API", "BioMed Central API", "Scopus APIs", "OpenCitations", "CORE Recommender",
]


@dataclass(frozen=True)
class SourceAdapter:
    source_id: str
    enabled: Callable[[], bool]
    limit: Callable[[], int]
    fn: AdapterFn
    catalog_group: str


def _enabled_keyless() -> bool:
    return True


def _enabled_if_key(key_name: str) -> Callable[[], bool]:
    def _inner() -> bool:
        return bool(getattr(Config, key_name, None))

    return _inner


def _enabled_jina() -> bool:
    return bool(Config.JINA_API_KEY) or bool(Config.JINA_SEARCH_ALLOW_KEYLESS)


def _search_arxiv(query: str, limit: int) -> List[Dict[str, Any]]:
    if limit <= 0 or not query.strip():
        return []
    try:
        import feedparser
    except ImportError as e:
        logger.warning("[arXiv] feedparser missing: %s", e)
        return []
    base_url = "http://export.arxiv.org/api/query?"
    search_query = f"search_query=all:{urllib.parse.quote(query)}"
    max_results = f"max_results={min(limit, 25)}"
    sort_by = "sortBy=submittedDate&sortOrder=descending"
    query_url = f"{base_url}{search_query}&{max_results}&{sort_by}"
    feed = feedparser.parse(query_url)
    out: List[Dict[str, Any]] = []
    for entry in feed.entries:
        out.append(
            {
                "title": entry.title,
                "authors": [a.name for a in entry.authors],
                "abstract": entry.summary,
                "published": entry.published,
                "arxiv_id": entry.id.split("/abs/")[-1],
                "pdf_url": entry.id.replace("/abs/", "/pdf/") + ".pdf",
                "url": entry.id,
                "categories": [tag.term for tag in entry.tags] if hasattr(entry, "tags") else [],
                "source": "arXiv",
                "doi": "",
            }
        )
        if len(out) >= limit:
            break
    return out


def _core_search(query: str, limit: int) -> List[Dict[str, Any]]:
    """CORE API (supports anonymous and key-auth usage tiers)."""
    if limit <= 0 or not query.strip():
        return []
    url = "https://api.core.ac.uk/v3/search/works"
    headers = {"Accept": "application/json"}
    if Config.CORE_API_KEY:
        headers["Authorization"] = f"Bearer {Config.CORE_API_KEY}"
    params = {"q": query, "limit": min(limit, 20)}
    r = requests.get(url, params=params, headers=headers, timeout=Config.RESEARCH_SOURCE_TIMEOUT)
    r.raise_for_status()
    data = r.json()
    out: List[Dict[str, Any]] = []
    for item in data.get("results") or []:
        title = (item.get("title") or "").strip()
        if not title:
            continue
        authors = [a.get("name") for a in (item.get("authors") or []) if isinstance(a, dict) and a.get("name")]
        out.append(
            {
                "title": title,
                "authors": authors,
                "abstract": (item.get("abstract") or "").strip(),
                "published": str(item.get("yearPublished") or ""),
                "arxiv_id": "",
                "pdf_url": item.get("downloadUrl") or "",
                "url": item.get("sourceFulltextUrls", [""])[0] if item.get("sourceFulltextUrls") else "",
                "categories": [],
                "source": "CORE",
                "doi": item.get("doi") or "",
            }
        )
        if len(out) >= limit:
            break
    return out


def _doaj_search(query: str, limit: int) -> List[Dict[str, Any]]:
    if limit <= 0 or not query.strip():
        return []
    url = "https://doaj.org/api/search/articles/" + urllib.parse.quote(query)
    params = {"pageSize": min(limit, 20)}
    r = requests.get(url, params=params, timeout=Config.RESEARCH_SOURCE_TIMEOUT)
    r.raise_for_status()
    data = r.json()
    out: List[Dict[str, Any]] = []
    for item in data.get("results") or []:
        bib = (item.get("bibjson") or {})
        title = (bib.get("title") or "").strip()
        if not title:
            continue
        authors = [a.get("name") for a in (bib.get("author") or []) if isinstance(a, dict) and a.get("name")]
        links = bib.get("link") or []
        first_link = links[0].get("url") if links and isinstance(links[0], dict) else ""
        out.append(
            {
                "title": title,
                "authors": authors,
                "abstract": (bib.get("abstract") or "").strip(),
                "published": str((bib.get("year") or "")),
                "arxiv_id": "",
                "pdf_url": first_link or "",
                "url": first_link or "",
                "categories": bib.get("keywords") or [],
                "source": "DOAJ",
                "doi": ((bib.get("identifier") or [{}])[0].get("id") if bib.get("identifier") else "") or "",
            }
        )
        if len(out) >= limit:
            break
    return out


def _biorxiv_search(query: str, limit: int) -> List[Dict[str, Any]]:
    return _rxiv_search("biorxiv", query, limit)


def _medrxiv_search(query: str, limit: int) -> List[Dict[str, Any]]:
    return _rxiv_search("medrxiv", query, limit)


def _rxiv_search(server: str, query: str, limit: int) -> List[Dict[str, Any]]:
    if limit <= 0 or not query.strip():
        return []
    # API supports date windows; use wide window for discovery.
    url = f"https://api.biorxiv.org/details/{server}/2000-01-01/2100-01-01"
    r = requests.get(url, timeout=Config.RESEARCH_SOURCE_TIMEOUT)
    r.raise_for_status()
    items = (r.json().get("collection") or [])[:500]
    q = query.lower()
    out: List[Dict[str, Any]] = []
    for item in items:
        title = (item.get("title") or "").strip()
        abstract = (item.get("abstract") or "").strip()
        hay = f"{title} {abstract}".lower()
        if q and q.split()[0] not in hay:
            continue
        out.append(
            {
                "title": title,
                "authors": [x.strip() for x in (item.get("authors") or "").split(";") if x.strip()],
                "abstract": abstract,
                "published": item.get("date") or "",
                "arxiv_id": "",
                "pdf_url": item.get("url") or "",
                "url": item.get("url") or "",
                "categories": [],
                "source": server,
                "doi": item.get("doi") or "",
            }
        )
        if len(out) >= limit:
            break
    return out


def _base_search(query: str, limit: int) -> List[Dict[str, Any]]:
    """
    BASE API requires SRU/OAI-PMH workflows. Implemented as opt-in adapter placeholder
    returning no rows when direct query endpoint is unavailable.
    """
    _ = (query, limit)
    return []


def _split_adapter_result(
    result: Any,
) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    if (
        isinstance(result, tuple)
        and len(result) == 2
        and isinstance(result[0], list)
        and isinstance(result[1], dict)
    ):
        return result[0], result[1]
    if isinstance(result, list):
        return result, {}
    return [], {"error_type": "invalid_adapter_return"}


def build_registry() -> List[SourceAdapter]:
    return [
        SourceAdapter("arxiv", lambda: Config.ENABLE_SOURCE_ARXIV, lambda: Config.RESEARCH_ARXIV_MAX, _search_arxiv, "preprint"),
        SourceAdapter("openalex", lambda: Config.ENABLE_SOURCE_OPENALEX, lambda: Config.RESEARCH_OPENALEX_MAX, fetch_openalex, "metadata"),
        SourceAdapter("semantic_scholar", lambda: Config.ENABLE_SOURCE_SEMANTIC_SCHOLAR, lambda: Config.RESEARCH_SEMANTIC_SCHOLAR_MAX, fetch_semantic_scholar, "metadata"),
        SourceAdapter("crossref", lambda: Config.ENABLE_SOURCE_CROSSREF, lambda: Config.RESEARCH_CROSSREF_MAX, fetch_crossref, "metadata"),
        SourceAdapter("pubmed", lambda: Config.ENABLE_SOURCE_PUBMED, lambda: Config.RESEARCH_PUBMED_MAX, fetch_pubmed, "biomedical"),
        SourceAdapter("core", lambda: Config.ENABLE_SOURCE_CORE, lambda: Config.RESEARCH_CORE_MAX, _core_search, "oa"),
        SourceAdapter("doaj", lambda: Config.ENABLE_SOURCE_DOAJ, lambda: Config.RESEARCH_DOAJ_MAX, _doaj_search, "oa"),
        SourceAdapter("base", lambda: Config.ENABLE_SOURCE_BASE, lambda: Config.RESEARCH_BASE_MAX, _base_search, "oa"),
        SourceAdapter("biorxiv", lambda: Config.ENABLE_SOURCE_BIORXIV, lambda: Config.RESEARCH_BIORXIV_MAX, _biorxiv_search, "biomedical"),
        SourceAdapter("medrxiv", lambda: Config.ENABLE_SOURCE_MEDRXIV, lambda: Config.RESEARCH_MEDRXIV_MAX, _medrxiv_search, "biomedical"),
        # Key-gated adapters (full fetch + normalize in keyed_adapters.py).
        SourceAdapter("tavily", _enabled_if_key("TAVILY_API_KEY"), lambda: 5, fetch_tavily, "llm_search"),
        SourceAdapter("exa", _enabled_if_key("EXA_API_KEY"), lambda: 5, fetch_exa, "llm_search"),
        SourceAdapter("firecrawl", _enabled_if_key("FIRECRAWL_API_KEY"), lambda: 5, fetch_firecrawl, "llm_search"),
        SourceAdapter("jina_reader", _enabled_jina, lambda: 5, fetch_jina_search, "llm_search"),
        SourceAdapter("deepseek", _enabled_if_key("DEEPSEEK_API_KEY"), lambda: 5, fetch_deepseek, "llm"),
        SourceAdapter("scopus", _enabled_if_key("SCOPUS_API_KEY"), lambda: 5, fetch_scopus, "citation"),
    ]


def collect_research_records(query: str) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """
    Execute enabled adapters in parallel and return deduped+ranked records and metrics.
    """
    registry = build_registry()
    source_stats: Dict[str, Dict[str, Any]] = {}
    collected: List[Dict[str, Any]] = []
    enabled = [a for a in registry if a.enabled()]

    def _run(adapter: SourceAdapter) -> Tuple[str, List[Dict[str, Any]], str, Dict[str, Any]]:
        retries = max(Config.RESEARCH_PER_SOURCE_RETRIES, 0) + 1
        last_err = ""
        detail: Dict[str, Any] = {}
        for _ in range(retries):
            try:
                raw = adapter.fn(query, adapter.limit())
                rows, detail = _split_adapter_result(raw)
                return adapter.source_id, rows, "", detail
            except Exception as e:  # noqa: BLE001
                last_err = str(e)
        return adapter.source_id, [], last_err, {"error_type": "exception", "detail": last_err}

    workers = max(1, min(Config.RESEARCH_MAX_WORKERS, len(enabled) or 1))
    with ThreadPoolExecutor(max_workers=workers) as pool:
        futures = {pool.submit(_run, adapter): adapter for adapter in enabled}
        for future in as_completed(futures):
            source_id, rows, err, extra = future.result()
            stat: Dict[str, Any] = {
                "count": len(rows),
                "ok": err == "",
                "error": err,
                "normalized_count": len(rows),
            }
            if isinstance(extra, dict):
                stat.update(
                    {
                        "attempted": extra.get("attempted", True),
                        "http_status": extra.get("http_status"),
                        "error_type": extra.get("error_type"),
                        "retries_used": extra.get("retries_used"),
                        "provider": extra.get("provider"),
                    }
                )
                if "normalized_count" in extra:
                    stat["normalized_count"] = extra["normalized_count"]
            source_stats[source_id] = stat
            collected.extend(rows)

    unique = dedupe_papers(collected)
    ranked = rank_and_filter_relevant(unique, query, Config.RESEARCH_TOTAL_MAX)

    metrics = {
        "catalog_total": len(TOOL_CATALOG),
        "enabled_sources": [a.source_id for a in enabled],
        "source_stats": source_stats,
        "raw_count": len(collected),
        "unique_count": len(unique),
        "returned_count": len(ranked),
        "unique_ratio": round((len(unique) / max(len(collected), 1)), 4),
    }
    return ranked, metrics

