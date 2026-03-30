"""
Keyless research APIs: OpenAlex and Semantic Scholar (HTTP, no API keys).
arXiv remains in research_agent; this module returns unified paper dicts.
"""

from __future__ import annotations

import re
from typing import Any, Dict, List, Optional, Set, Tuple

import requests

from utils.config import Config
from utils.logger import setup_logger

logger = setup_logger(__name__)

_SESSION = requests.Session()
_TIMEOUT = 15


def _ua() -> str:
    return f"TrustWise/1.0 ({Config.OPENALEX_MAILTO})"


def fetch_openalex(query: str, limit: int) -> List[Dict[str, Any]]:
    if limit <= 0 or not query.strip():
        return []
    url = "https://api.openalex.org/works"
    params = {"search": query, "per_page": min(limit, 25)}
    headers = {"User-Agent": _ua(), "Accept": "application/json"}
    try:
        r = _SESSION.get(url, params=params, headers=headers, timeout=_TIMEOUT)
        r.raise_for_status()
        data = r.json()
    except Exception as e:
        logger.warning("[OpenAlex] request failed: %s", e)
        return []

    out: List[Dict[str, Any]] = []
    for w in data.get("results") or []:
        title = (w.get("title") or "").strip()
        if not title:
            continue
        authors: List[str] = []
        for a in w.get("authorships") or []:
            auth = a.get("author") or {}
            name = auth.get("display_name")
            if name:
                authors.append(name)
        abstract = _openalex_abstract(w.get("abstract_inverted_index"))
        landing = None
        pl = w.get("primary_location") or {}
        if isinstance(pl, dict):
            landing = pl.get("landing_page_url")
        doi = None
        if isinstance(pl, dict) and pl.get("doi"):
            doi = pl.get("doi")
        wid = w.get("id") or ""
        if not landing and wid:
            landing = wid
        year = w.get("publication_year")
        pub = str(year) if year else ""

        out.append(
            {
                "title": title,
                "authors": authors,
                "abstract": abstract,
                "published": pub,
                "arxiv_id": "",
                "pdf_url": landing or "",
                "url": landing or "",
                "categories": [],
                "source": "OpenAlex",
                "doi": doi or "",
                "openalex_id": wid,
            }
        )
        if len(out) >= limit:
            break
    return out


def _openalex_abstract(inv_index: Any) -> str:
    """Reconstruct abstract from OpenAlex inverted index."""
    if not inv_index or not isinstance(inv_index, dict):
        return ""
    positions: List[Tuple[int, str]] = []
    for word, places in inv_index.items():
        if not isinstance(places, list):
            continue
        for pos in places:
            if isinstance(pos, int):
                positions.append((pos, word))
    if not positions:
        return ""
    positions.sort(key=lambda x: x[0])
    return " ".join(w for _, w in positions)


def fetch_semantic_scholar(query: str, limit: int) -> List[Dict[str, Any]]:
    if limit <= 0 or not query.strip():
        return []
    url = "https://api.semanticscholar.org/graph/v1/paper/search"
    params = {
        "query": query,
        "limit": min(limit, 20),
        "fields": "title,authors,year,abstract,url,openAccessPdf,externalIds",
    }
    headers = {"Accept": "application/json"}
    try:
        r = _SESSION.get(url, params=params, headers=headers, timeout=_TIMEOUT)
        r.raise_for_status()
        data = r.json()
    except Exception as e:
        logger.warning("[SemanticScholar] request failed: %s", e)
        return []

    out: List[Dict[str, Any]] = []
    for p in data.get("data") or []:
        title = (p.get("title") or "").strip()
        if not title:
            continue
        authors = []
        for a in p.get("authors") or []:
            if isinstance(a, dict) and a.get("name"):
                authors.append(a["name"])
        year = p.get("year")
        pub = str(year) if year else ""
        abstract = (p.get("abstract") or "").strip()
        pdf_url = ""
        oap = p.get("openAccessPdf") or {}
        if isinstance(oap, dict) and oap.get("url"):
            pdf_url = oap["url"]
        landing = p.get("url") or pdf_url
        ext = p.get("externalIds") or {}
        doi = ext.get("DOI") or ""

        out.append(
            {
                "title": title,
                "authors": authors,
                "abstract": abstract,
                "published": pub,
                "arxiv_id": ext.get("ArXiv") or "",
                "pdf_url": pdf_url or landing or "",
                "url": landing or "",
                "categories": [],
                "source": "Semantic Scholar",
                "doi": doi,
            }
        )
        if len(out) >= limit:
            break
    return out


def _norm_title(t: str) -> str:
    s = t.lower().strip()
    s = re.sub(r"[^a-z0-9\s]", "", s)
    s = re.sub(r"\s+", " ", s)
    return s[:200]


def dedupe_papers(papers: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    seen: Set[str] = set()
    unique: List[Dict[str, Any]] = []
    for p in papers:
        doi = (p.get("doi") or "").strip().lower()
        key = doi if doi else _norm_title(p.get("title") or "") + str(p.get("published") or "")
        if not key or key in seen:
            continue
        seen.add(key)
        unique.append(p)
    return unique
