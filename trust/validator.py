import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Set, Tuple
from urllib.parse import urlparse

from utils.config import Config
from utils.logger import setup_logger

logger = setup_logger(__name__)


def validate_structured_data(items: List[Dict[str, Any]], query: str = "") -> Dict[str, Any]:
    """Apply simple zero-trust checks and return trusted subset with scoring."""
    trusted_domains = _load_trusted_domains()
    query_terms = _extract_query_terms(query)

    seen_signatures: Set[str] = set()
    validated: List[Dict[str, Any]] = []

    for item in items:
        scored_item, signature = _score_item(item, trusted_domains, query_terms)

        # Duplicate check across normalized signatures.
        if signature in seen_signatures:
            scored_item["trust"]["duplicate"] = True
            scored_item["trust"]["score"] = max(0.0, scored_item["trust"]["score"] - 0.35)
            scored_item["trust"]["reasons"].append("Duplicate content detected")
        else:
            seen_signatures.add(signature)

        min_relevance = 0.28 if (scored_item.get("content_type") == "web") else 0.15
        min_score = 0.65 if (scored_item.get("content_type") == "web") else 0.6
        scored_item["trust"]["trusted"] = (
            scored_item["trust"]["score"] >= min_score
            and not scored_item["trust"]["duplicate"]
            and scored_item["trust"]["relevance"] >= min_relevance
        )
        validated.append(scored_item)

    trusted_items = [item for item in validated if item["trust"]["trusted"]]

    report = {
        "query": query,
        "validated_count": len(validated),
        "trusted_count": len(trusted_items),
        "dropped_count": len(validated) - len(trusted_items),
        "trusted_items": trusted_items,
        "all_items": validated,
    }

    if Config.SAVE_TRUSTED_DATA:
        _save_trusted_data(report)

    logger.info(
        "[Trust] Validation complete: %s trusted / %s total",
        len(trusted_items),
        len(validated),
    )
    return report


def _score_item(item: Dict[str, Any], trusted_domains: Set[str], query_terms: Set[str]) -> Tuple[Dict[str, Any], str]:
    title = (item.get("title") or "").strip()
    content = (item.get("content") or "").strip()
    source = (item.get("source") or "").strip()
    url = (item.get("url") or "").strip()

    score = 0.0
    reasons: List[str] = []

    domain = _get_domain(url or source)
    if item.get("content_type") == "research_paper" and source.lower() in {"arxiv", "arxiv.org"}:
        score += 0.55
        reasons.append("Research source recognized (arXiv)")
    elif domain in trusted_domains:
        score += 0.45
        reasons.append(f"Trusted domain: {domain}")
    else:
        score += 0.1
        reasons.append("Source not in trusted whitelist")

    content_len = len(content)
    if content_len >= 600:
        score += 0.2
        reasons.append("Sufficient content length")
    elif content_len >= 200:
        score += 0.1
        reasons.append("Moderate content length")
    else:
        reasons.append("Very short content")

    relevance = _relevance_score(title, content, query_terms)
    score += min(0.25, relevance)
    reasons.append(f"Query relevance: {relevance:.2f}")

    penalty = _suspicious_penalty(content)
    if penalty > 0:
        score -= penalty
        reasons.append(f"Suspicious/noisy content penalty: -{penalty:.2f}")

    score = max(0.0, min(1.0, score))

    enriched = dict(item)
    enriched["trust"] = {
        "score": round(score, 3),
        "relevance": round(relevance, 3),
        "trusted": False,
        "duplicate": False,
        "domain": domain,
        "reasons": reasons,
    }

    signature_base = f"{title.lower()}::{content[:220].lower()}"
    signature = re.sub(r"\s+", " ", signature_base).strip()
    return enriched, signature


def _relevance_score(title: str, content: str, query_terms: Set[str]) -> float:
    if not query_terms:
        return 0.0

    text = f"{title} {content[:1200]}".lower()
    matched = sum(1 for term in query_terms if term in text)
    return matched / max(1, len(query_terms))


def _suspicious_penalty(content: str) -> float:
    markers = [
        "accept all cookies",
        "privacy policy",
        "manage preferences",
        "consent",
        "do not store directly personal information",
        "all information these cookies collect is aggregated",
        "subscribe now",
        "advertisement",
        "consent management",
        "please complete the following challenge",
    ]
    lowered = content.lower()
    hits = sum(1 for m in markers if m in lowered)
    return min(0.35, hits * 0.08)


def _extract_query_terms(query: str) -> Set[str]:
    words = re.findall(r"[a-zA-Z0-9]+", query.lower())
    stop = {
        "tell", "me", "about", "latest", "recent", "find", "get", "show", "the", "a", "an", "on", "in", "for"
    }
    return {w for w in words if len(w) > 2 and w not in stop}


def _load_trusted_domains() -> Set[str]:
    sources_file = Config.CONFIG_DIR / "sources.json"
    if not sources_file.exists():
        return set()

    try:
        data = json.loads(sources_file.read_text(encoding="utf-8"))
        urls = data.get("trusted_web_sources", []) if isinstance(data, dict) else data
        domains = {_get_domain(url) for url in urls}
        return {d for d in domains if d}
    except Exception as e:
        logger.warning(f"[Trust] Could not load trusted sources: {e}")
        return set()


def _get_domain(url_or_source: str) -> str:
    if not url_or_source:
        return ""

    parsed = urlparse(url_or_source if "://" in url_or_source else f"https://{url_or_source}")
    return parsed.netloc.lower().replace("www.", "")


def _save_trusted_data(report: Dict[str, Any]) -> None:
    filename = f"trusted_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
    filepath = Config.TRUSTED_DATA_DIR / filename

    try:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2, ensure_ascii=False)
        logger.info(f"[Trust] Saved trusted data report to {filepath}")
    except Exception as e:
        logger.error(f"[Trust] Failed to save trusted data report: {e}")
