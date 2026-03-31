"""
Keyless research APIs for production data aggregation.

This module currently integrates:
- OpenAlex
- Semantic Scholar
- Crossref
- PubMed (NCBI E-utilities)

arXiv remains in research_agent; all sources are normalized to a shared schema.
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


def fetch_crossref(query: str, limit: int) -> List[Dict[str, Any]]:
    if limit <= 0 or not query.strip():
        return []
    url = "https://api.crossref.org/works"
    params = {
        "query.bibliographic": query,
        "rows": min(limit, 20),
        "select": "DOI,title,author,issued,abstract,URL,subject",
    }
    headers = {"User-Agent": _ua(), "Accept": "application/json"}
    try:
        r = _SESSION.get(url, params=params, headers=headers, timeout=_TIMEOUT)
        r.raise_for_status()
        data = r.json()
    except Exception as e:
        logger.warning("[Crossref] request failed: %s", e)
        return []

    out: List[Dict[str, Any]] = []
    for w in (data.get("message") or {}).get("items") or []:
        title_list = w.get("title") or []
        title = (title_list[0] if title_list else "").strip()
        if not title:
            continue
        authors: List[str] = []
        for a in w.get("author") or []:
            if not isinstance(a, dict):
                continue
            given = (a.get("given") or "").strip()
            family = (a.get("family") or "").strip()
            full = " ".join(x for x in [given, family] if x).strip()
            if full:
                authors.append(full)
        year = ""
        issued = w.get("issued") or {}
        parts = issued.get("date-parts") or []
        if parts and isinstance(parts[0], list) and parts[0]:
            year = str(parts[0][0])
        abstract = _strip_jats((w.get("abstract") or "").strip())
        doi = (w.get("DOI") or "").strip()
        landing = (w.get("URL") or "").strip()
        categories = [s for s in (w.get("subject") or []) if isinstance(s, str)]
        out.append(
            {
                "title": title,
                "authors": authors,
                "abstract": abstract,
                "published": year,
                "arxiv_id": "",
                "pdf_url": landing,
                "url": landing,
                "categories": categories,
                "source": "Crossref",
                "doi": doi,
            }
        )
        if len(out) >= limit:
            break
    return out


def fetch_pubmed(query: str, limit: int) -> List[Dict[str, Any]]:
    if limit <= 0 or not query.strip():
        return []
    # 1) ESearch to retrieve PMIDs.
    search_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    search_params = {"db": "pubmed", "retmode": "json", "retmax": min(limit, 20), "term": query}
    try:
        r = _SESSION.get(search_url, params=search_params, timeout=_TIMEOUT)
        r.raise_for_status()
        ids = ((r.json().get("esearchresult") or {}).get("idlist") or [])
    except Exception as e:
        logger.warning("[PubMed] esearch failed: %s", e)
        return []
    if not ids:
        return []

    # 2) ESummary for metadata.
    summary_url = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
    summary_params = {"db": "pubmed", "retmode": "json", "id": ",".join(ids)}
    try:
        r = _SESSION.get(summary_url, params=summary_params, timeout=_TIMEOUT)
        r.raise_for_status()
        data = r.json()
    except Exception as e:
        logger.warning("[PubMed] esummary failed: %s", e)
        return []

    out: List[Dict[str, Any]] = []
    result = data.get("result") or {}
    for pmid in ids:
        item = result.get(str(pmid)) or {}
        title = (item.get("title") or "").strip()
        if not title:
            continue
        authors = []
        for a in item.get("authors") or []:
            if isinstance(a, dict) and a.get("name"):
                authors.append(a["name"])
        pubdate = (item.get("pubdate") or "").strip()
        year = pubdate[:4] if pubdate else ""
        article_ids = item.get("articleids") or []
        doi = ""
        for aid in article_ids:
            if isinstance(aid, dict) and (aid.get("idtype") or "").lower() == "doi":
                doi = aid.get("value") or ""
                break
        landing = f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"
        out.append(
            {
                "title": title,
                "authors": authors,
                "abstract": "",
                "published": year,
                "arxiv_id": "",
                "pdf_url": landing,
                "url": landing,
                "categories": [],
                "source": "PubMed",
                "doi": doi,
                "pubmed_id": str(pmid),
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
    unique_map: Dict[str, Dict[str, Any]] = {}
    for p in papers:
        doi = (p.get("doi") or "").strip().lower()
        title_key = _norm_title(p.get("title") or "")
        key = doi if doi else title_key
        if not key:
            continue
        if key not in unique_map:
            entry = dict(p)
            src = (entry.get("source") or "").strip()
            entry["source_list"] = [src] if src else []
            entry["source_count"] = len(entry["source_list"])
            unique_map[key] = entry
            continue
        existing = unique_map[key]
        # Merge details to keep richer representation for the same paper.
        if len((p.get("abstract") or "").strip()) > len((existing.get("abstract") or "").strip()):
            existing["abstract"] = p.get("abstract") or ""
        if not existing.get("doi") and p.get("doi"):
            existing["doi"] = p.get("doi")
        if not existing.get("url") and p.get("url"):
            existing["url"] = p.get("url")
        if not existing.get("pdf_url") and p.get("pdf_url"):
            existing["pdf_url"] = p.get("pdf_url")
        if not existing.get("published") and p.get("published"):
            existing["published"] = p.get("published")
        existing_authors = existing.get("authors") or []
        incoming_authors = p.get("authors") or []
        if len(incoming_authors) > len(existing_authors):
            existing["authors"] = incoming_authors
        ex_source = (existing.get("source") or "").strip()
        in_source = (p.get("source") or "").strip()
        if in_source and in_source != ex_source:
            parts = [s for s in ex_source.split("|") if s] if ex_source else []
            if in_source not in parts:
                parts.append(in_source)
            existing["source"] = "|".join(parts)
            existing["source_list"] = parts
            existing["source_count"] = len(parts)
        else:
            existing["source_list"] = list(dict.fromkeys(existing.get("source_list") or ([ex_source] if ex_source else [])))
            existing["source_count"] = len(existing.get("source_list") or [])
    return list(unique_map.values())


def rank_and_filter_relevant(papers: List[Dict[str, Any]], query: str, limit: int) -> List[Dict[str, Any]]:
    """
    Keep unique, relevant papers by token overlap score.
    This is source-agnostic and helps combine multiple APIs cleanly.
    """
    if not papers:
        return []
    q_terms = _tokenize(query)
    scored: List[Tuple[float, Dict[str, Any]]] = []
    for p in papers:
        text = " ".join(
            [
                p.get("title") or "",
                p.get("abstract") or "",
                " ".join(p.get("categories") or []),
                p.get("source") or "",
            ]
        )
        d_terms = _tokenize(text)
        score = _overlap_score(q_terms, d_terms)
        if score <= 0 and q_terms:
            continue
        p["relevance_score"] = round(score, 4)
        # Confidence combines term overlap and cross-source corroboration.
        corroboration = min(float(p.get("source_count", 1)), 3.0) / 3.0
        p["confidence"] = round((0.8 * score) + (0.2 * corroboration), 4)
        scored.append((score, p))
    scored.sort(key=lambda x: x[0], reverse=True)
    return [p for _, p in scored[: max(limit, 1)]]


def _tokenize(text: str) -> Set[str]:
    tokens = re.findall(r"[a-z0-9]+", (text or "").lower())
    stop = {
        "the", "and", "for", "with", "from", "into", "about", "latest",
        "recent", "update", "updates", "study", "paper", "research",
    }
    return {t for t in tokens if len(t) > 2 and t not in stop}


def _overlap_score(a: Set[str], b: Set[str]) -> float:
    if not a:
        return 1.0
    if not b:
        return 0.0
    inter = len(a.intersection(b))
    return inter / max(len(a), 1)


def _strip_jats(text: str) -> str:
    # Crossref abstracts are often JATS/XML-ish; keep readable text only.
    cleaned = re.sub(r"<[^>]+>", " ", text or "")
    cleaned = re.sub(r"\s+", " ", cleaned).strip()
    return cleaned
