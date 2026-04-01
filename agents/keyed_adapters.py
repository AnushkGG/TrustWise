"""
Fetch + normalize implementations for key-gated research adapters.

All functions return (rows, meta) where meta includes observability fields.
No-key: returns ([], empty_meta_no_key(...)) without raising.
"""

from __future__ import annotations

import json
import re
from typing import Any, Dict, List, Tuple

import requests

from agents.keyed_http import KeyedAdapterError, empty_meta_no_key, safe_request_json, safe_request_text
from utils.config import Config
from utils.logger import setup_logger

logger = setup_logger(__name__)

_SESSION = requests.Session()


def _paper(
    *,
    title: str,
    source: str,
    url: str = "",
    abstract: str = "",
    authors: List[str] | None = None,
    published: str = "",
    doi: str = "",
    pdf_url: str = "",
    extra: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    row: Dict[str, Any] = {
        "title": (title or "").strip() or "Untitled",
        "authors": authors or [],
        "abstract": (abstract or "")[:12000],
        "published": published or "",
        "arxiv_id": "",
        "pdf_url": pdf_url or url or "",
        "url": url or pdf_url or "",
        "categories": [],
        "source": source,
        "doi": doi or "",
    }
    if extra:
        row.update(extra)
    return row


def fetch_tavily(query: str, limit: int) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    if not Config.TAVILY_API_KEY or limit <= 0 or not query.strip():
        return [], {**empty_meta_no_key("tavily"), "normalized_count": 0}
    meta: Dict[str, Any] = {
        "attempted": True,
        "ok": False,
        "error_type": None,
        "http_status": None,
        "normalized_count": 0,
        "provider": "tavily",
    }
    try:
        data, http_meta = safe_request_json(
            "POST",
            "https://api.tavily.com/search",
            session=_SESSION,
            json={
                "api_key": Config.TAVILY_API_KEY,
                "query": query,
                "search_depth": "advanced",
                "max_results": min(limit, 20),
            },
        )
        meta.update({k: http_meta.get(k) for k in ("http_status", "retries_used", "ok") if k in http_meta})
        rows: List[Dict[str, Any]] = []
        for r in data.get("results") or []:
            url = (r.get("url") or "").strip()
            title = (r.get("title") or url or "Result").strip()
            content = (r.get("content") or r.get("snippet") or "").strip()
            if not url and not title:
                continue
            rows.append(
                _paper(
                    title=title,
                    source="Tavily",
                    url=url,
                    abstract=content,
                    extra={"tavily_score": r.get("score")},
                )
            )
            if len(rows) >= limit:
                break
        meta["ok"] = True
        meta["normalized_count"] = len(rows)
        return rows, meta
    except KeyedAdapterError as e:
        meta["ok"] = False
        meta["error_type"] = e.error_type
        meta["http_status"] = e.http_status
        logger.warning("[Tavily] %s", e)
        return [], meta
    except Exception as e:  # noqa: BLE001
        meta["error_type"] = "unexpected"
        logger.warning("[Tavily] %s", e)
        return [], meta


def fetch_exa(query: str, limit: int) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    if not Config.EXA_API_KEY or limit <= 0 or not query.strip():
        return [], {**empty_meta_no_key("exa"), "normalized_count": 0}
    meta: Dict[str, Any] = {
        "attempted": True,
        "ok": False,
        "error_type": None,
        "http_status": None,
        "normalized_count": 0,
        "provider": "exa",
    }
    try:
        data, http_meta = safe_request_json(
            "POST",
            "https://api.exa.ai/search",
            session=_SESSION,
            headers={"x-api-key": Config.EXA_API_KEY, "Content-Type": "application/json"},
            json={"query": query, "numResults": min(limit, 20), "useAutoprompt": True},
        )
        meta.update({k: http_meta.get(k) for k in ("http_status", "retries_used", "ok") if k in http_meta})
        rows: List[Dict[str, Any]] = []
        for r in data.get("results") or []:
            url = (r.get("url") or "").strip()
            title = (r.get("title") or url or "Result").strip()
            abstract = (r.get("snippet") or r.get("text") or "").strip()
            rows.append(
                _paper(
                    title=title,
                    source="Exa",
                    url=url,
                    abstract=abstract[:8000],
                    extra={"exa_id": r.get("id")},
                )
            )
            if len(rows) >= limit:
                break
        meta["ok"] = True
        meta["normalized_count"] = len(rows)
        return rows, meta
    except KeyedAdapterError as e:
        meta["error_type"] = e.error_type
        meta["http_status"] = e.http_status
        logger.warning("[Exa] %s", e)
        return [], meta
    except Exception as e:  # noqa: BLE001
        meta["error_type"] = "unexpected"
        logger.warning("[Exa] %s", e)
        return [], meta


def fetch_firecrawl(query: str, limit: int) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    if not Config.FIRECRAWL_API_KEY or limit <= 0 or not query.strip():
        return [], {**empty_meta_no_key("firecrawl"), "normalized_count": 0}
    meta: Dict[str, Any] = {
        "attempted": True,
        "ok": False,
        "error_type": None,
        "http_status": None,
        "normalized_count": 0,
        "provider": "firecrawl",
    }
    try:
        data, http_meta = safe_request_json(
            "POST",
            "https://api.firecrawl.dev/v1/search",
            session=_SESSION,
            headers={
                "Authorization": f"Bearer {Config.FIRECRAWL_API_KEY}",
                "Content-Type": "application/json",
            },
            json={"query": query, "limit": min(limit, 20)},
        )
        meta.update({k: http_meta.get(k) for k in ("http_status", "retries_used", "ok") if k in http_meta})
        rows: List[Dict[str, Any]] = []
        raw = data.get("data") or data.get("results") or []
        for r in raw:
            if not isinstance(r, dict):
                continue
            url = (r.get("url") or "").strip()
            md = (r.get("markdown") or r.get("content") or r.get("description") or "").strip()
            title = (r.get("title") or url or "Result").strip()
            rows.append(_paper(title=title, source="Firecrawl", url=url, abstract=md[:8000]))
            if len(rows) >= limit:
                break
        meta["ok"] = True
        meta["normalized_count"] = len(rows)
        return rows, meta
    except KeyedAdapterError as e:
        meta["error_type"] = e.error_type
        meta["http_status"] = e.http_status
        logger.warning("[Firecrawl] %s", e)
        return [], meta
    except Exception as e:  # noqa: BLE001
        meta["error_type"] = "unexpected"
        logger.warning("[Firecrawl] %s", e)
        return [], meta


def fetch_jina_search(query: str, limit: int) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """
    Jina Search (s.jina.ai) returns markdown; we extract URLs and build paper-like rows.
    Optional Bearer token for higher rate limits.
    """
    if not query.strip() or limit <= 0:
        return [], {"attempted": False, "ok": True, "normalized_count": 0, "provider": "jina_reader"}
    # s.jina.ai works without key; key improves rate limits
    meta: Dict[str, Any] = {
        "attempted": True,
        "ok": False,
        "error_type": None,
        "http_status": None,
        "normalized_count": 0,
        "provider": "jina_reader",
    }
    try:
        from urllib.parse import quote

        path_q = quote(query, safe="")
        url = f"https://s.jina.ai/{path_q}"
        headers = {"Accept": "text/plain"}
        if Config.JINA_API_KEY:
            headers["Authorization"] = f"Bearer {Config.JINA_API_KEY}"
        text, http_meta = safe_request_text("GET", url, session=_SESSION, headers=headers)
        meta.update({k: http_meta.get(k) for k in ("http_status", "retries_used", "ok") if k in http_meta})
        urls = re.findall(r"https?://[^\s\)\]]+", text)
        seen = set()
        rows: List[Dict[str, Any]] = []
        snippet = text[:3500] if text else ""
        for u in urls:
            if u in seen or "jina.ai" in u.lower():
                continue
            seen.add(u)
            rows.append(
                _paper(
                    title=u[:120],
                    source="Jina",
                    url=u,
                    abstract=snippet if len(rows) == 0 else "",
                )
            )
            if len(rows) >= limit:
                break
        meta["ok"] = True
        meta["normalized_count"] = len(rows)
        return rows, meta
    except KeyedAdapterError as e:
        meta["error_type"] = e.error_type
        meta["http_status"] = e.http_status
        logger.warning("[Jina] %s", e)
        return [], meta
    except Exception as e:  # noqa: BLE001
        meta["error_type"] = "unexpected"
        logger.warning("[Jina] %s", e)
        return [], meta


def fetch_scopus(query: str, limit: int) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    if not Config.SCOPUS_API_KEY or limit <= 0 or not query.strip():
        return [], {**empty_meta_no_key("scopus"), "normalized_count": 0}
    meta: Dict[str, Any] = {
        "attempted": True,
        "ok": False,
        "error_type": None,
        "http_status": None,
        "normalized_count": 0,
        "provider": "scopus",
    }
    try:
        data, http_meta = safe_request_json(
            "GET",
            "https://api.elsevier.com/content/search/scopus",
            session=_SESSION,
            params={
                "query": f"TITLE-ABS-KEY({query})",
                "count": min(limit, 25),
                "apiKey": Config.SCOPUS_API_KEY,
                "httpAccept": "application/json",
            },
        )
        meta.update({k: http_meta.get(k) for k in ("http_status", "retries_used", "ok") if k in http_meta})
        entries = (data.get("search-results") or {}).get("entry") or []
        if isinstance(entries, dict):
            entries = [entries]
        rows: List[Dict[str, Any]] = []
        for ent in entries:
            if not isinstance(ent, dict):
                continue
            title = (ent.get("dc:title") or "").strip()
            if isinstance(title, list):
                title = title[0] if title else ""
            creators = ent.get("dc:creator") or ""
            if isinstance(creators, list):
                authors = [str(c) for c in creators]
            else:
                authors = [creators] if creators else []
            date = (ent.get("prism:coverDate") or ent.get("prism:coverDisplayDate") or "")[:16]
            doi = (ent.get("prism:doi") or ent.get("article-number") or "") or ""
            landing = ""
            for link in ent.get("link") or []:
                if isinstance(link, dict) and link.get("@href"):
                    landing = link["@href"]
                    break
            rows.append(
                _paper(
                    title=title or "Scopus result",
                    source="Scopus",
                    url=landing,
                    abstract="",
                    authors=authors,
                    published=date,
                    doi=str(doi) if doi else "",
                )
            )
            if len(rows) >= limit:
                break
        meta["ok"] = True
        meta["normalized_count"] = len(rows)
        return rows, meta
    except KeyedAdapterError as e:
        meta["error_type"] = e.error_type
        meta["http_status"] = e.http_status
        logger.warning("[Scopus] %s", e)
        return [], meta
    except Exception as e:  # noqa: BLE001
        meta["error_type"] = "unexpected"
        logger.warning("[Scopus] %s", e)
        return [], meta


def fetch_deepseek(query: str, limit: int) -> Tuple[List[Dict[str, Any]], Dict[str, Any]]:
    """
    Uses DeepSeek chat to emit a JSON array of suggested papers (titles + abstracts).
    """
    if not Config.DEEPSEEK_API_KEY or limit <= 0 or not query.strip():
        return [], {**empty_meta_no_key("deepseek"), "normalized_count": 0}
    meta: Dict[str, Any] = {
        "attempted": True,
        "ok": False,
        "error_type": None,
        "http_status": None,
        "normalized_count": 0,
        "provider": "deepseek",
    }
    system = (
        "You are a research assistant. Respond with ONLY valid JSON: an array of objects, "
        'each with keys: title (string), abstract (string), optional url (string), '
        f"optional authors (array of strings), optional published (string). "
        f"At most {min(limit, 10)} items. No markdown, no prose outside JSON."
    )
    user = f"Suggest relevant scholarly works for this query: {query}"
    try:
        data, http_meta = safe_request_json(
            "POST",
            "https://api.deepseek.com/v1/chat/completions",
            session=_SESSION,
            headers={
                "Authorization": f"Bearer {Config.DEEPSEEK_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": "deepseek-chat",
                "messages": [
                    {"role": "system", "content": system},
                    {"role": "user", "content": user},
                ],
                "temperature": 0.2,
                "max_tokens": 2000,
            },
        )
        meta.update({k: http_meta.get(k) for k in ("http_status", "retries_used", "ok") if k in http_meta})
        content = (
            (data.get("choices") or [{}])[0]
            .get("message", {})
            .get("content", "")
        )
        content = (content or "").strip()
        # strip markdown code fence if present
        if content.startswith("```"):
            content = re.sub(r"^```[a-z]*\n", "", content)
            content = re.sub(r"\n```$", "", content).strip()
        try:
            parsed = json.loads(content)
        except json.JSONDecodeError:
            parsed = []
        if isinstance(parsed, dict):
            arr = [parsed]
        elif isinstance(parsed, list):
            arr = parsed
        else:
            arr = []
        rows: List[Dict[str, Any]] = []
        for item in arr:
            if not isinstance(item, dict):
                continue
            rows.append(
                _paper(
                    title=str(item.get("title") or ""),
                    source="DeepSeek",
                    url=str(item.get("url") or ""),
                    abstract=str(item.get("abstract") or ""),
                    authors=list(item.get("authors") or []) if isinstance(item.get("authors"), list) else [],
                    published=str(item.get("published") or ""),
                    extra={"deepseek_synthetic": True},
                )
            )
            if len(rows) >= limit:
                break
        meta["ok"] = True
        meta["normalized_count"] = len(rows)
        return rows, meta
    except (json.JSONDecodeError, KeyError) as e:
        meta["error_type"] = "json_error"
        logger.warning("[DeepSeek] parse error: %s", e)
        return [], meta
    except KeyedAdapterError as e:
        meta["error_type"] = e.error_type
        meta["http_status"] = e.http_status
        logger.warning("[DeepSeek] %s", e)
        return [], meta
    except Exception as e:  # noqa: BLE001
        meta["error_type"] = "unexpected"
        logger.warning("[DeepSeek] %s", e)
        return [], meta
