import json
import re
from datetime import datetime
from typing import Any, Dict, List

from utils.config import Config
from utils.logger import setup_logger

logger = setup_logger(__name__)


def normalize_results(results: List[Dict[str, Any]], query: str = "") -> List[Dict[str, Any]]:
    """Convert mixed agent outputs into a uniform structured schema."""
    structured: List[Dict[str, Any]] = []

    for result in results:
        agent = result.get("agent", "")
        items = result.get("data", [])

        if agent == "web_agent":
            for item in items:
                entry = _normalize_web_item(item, query)
                if entry:
                    structured.append(entry)
        elif agent == "research_agent":
            for item in items:
                entry = _normalize_research_item(item)
                if entry:
                    structured.append(entry)

    if Config.SAVE_STRUCTURED_DATA:
        _save_structured_data(structured, query)

    logger.info(f"[Cleaner] Structured {len(structured)} entries")
    return structured


def _normalize_web_item(item: Dict[str, Any], query: str) -> Dict[str, Any]:
    source = item.get("source", "")
    raw_content = item.get("content", "")

    title = _extract_web_title(raw_content, source)
    content = _clean_text(raw_content)

    if not content:
        return {}

    return {
        "title": title,
        "content": content,
        "source": source,
        "url": source,
        "published_at": None,
        "content_type": "web",
        "query": query,
    }


def _normalize_research_item(item: Dict[str, Any]) -> Dict[str, Any]:
    title = item.get("title", "Untitled paper")
    abstract = _clean_text(item.get("abstract", ""))
    url = (item.get("pdf_url") or item.get("url") or "").strip()
    src = item.get("source") or "Research"

    return {
        "title": title,
        "content": abstract,
        "source": src,
        "url": url,
        "published_at": item.get("published"),
        "content_type": "research_paper",
        "authors": item.get("authors", []),
        "categories": item.get("categories", []),
        "arxiv_id": item.get("arxiv_id", ""),
        "doi": item.get("doi", ""),
        "journal": item.get("journal", ""),
        "citation_count": item.get("citation_count", 0),
        "keywords": item.get("keywords", []),
        "mesh_terms": item.get("mesh_terms", []),
    }


def _extract_web_title(content: str, fallback: str) -> str:
    # Prefer markdown-style headings/links from crawl outputs.
    for line in content.splitlines():
        stripped = line.strip()
        if stripped.startswith("# "):
            return stripped[2:].strip()
        if stripped.startswith("## "):
            return stripped[3:].strip()

        md_link_match = re.search(r"\[(.*?)\]\((https?://.*?)\)", stripped)
        if md_link_match:
            candidate = md_link_match.group(1).strip()
            if len(candidate) > 10:
                return candidate

    return fallback.replace("https://", "").replace("http://", "") or "Web content"


def _clean_text(text: str, max_chars: int = 3500) -> str:
    if not text:
        return ""

    lines = [line.strip() for line in text.splitlines() if line.strip()]

    junk_markers = (
        "privacy policy",
        "accept all cookies",
        "reject optional cookies",
        "manage preferences",
        "consent",
        "do not store directly personal information",
        "all information these cookies collect is aggregated",
        "skip to content",
        "subscribe",
        "advertisement",
        "sign in",
        "grid settings",
    )

    filtered = [line for line in lines if not any(marker in line.lower() for marker in junk_markers)]
    cleaned = "\n".join(filtered)

    if len(cleaned) > max_chars:
        cleaned = cleaned[:max_chars].rstrip() + "\n... (truncated)"

    return cleaned


def _save_structured_data(structured: List[Dict[str, Any]], query: str) -> None:
    payload = {
        "query": query,
        "created_at": datetime.utcnow().isoformat(),
        "items": structured,
        "total_items": len(structured),
    }

    filename = f"structured_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
    filepath = Config.STRUCTURED_DATA_DIR / filename

    try:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(payload, f, indent=2, ensure_ascii=False)
        logger.info(f"[Cleaner] Saved structured data to {filepath}")
    except Exception as e:
        logger.error(f"[Cleaner] Failed to save structured data: {e}")
