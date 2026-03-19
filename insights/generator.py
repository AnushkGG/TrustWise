from collections import Counter
import re
from typing import Any, Dict, List


def _extract_query_terms(query: str) -> List[str]:
    words = re.findall(r"[a-zA-Z0-9]+", (query or "").lower())
    stopwords = {
        "the", "a", "an", "and", "or", "to", "of", "for", "in", "on", "with",
        "about", "latest", "recent", "new", "tell", "me", "what", "is", "are",
        "from", "into", "at", "by", "as", "their", "its", "be", "this", "that",
    }
    return [w for w in words if len(w) > 2 and w not in stopwords]


def _split_sentences(text: str) -> List[str]:
    if not text:
        return []
    compact = re.sub(r"\s+", " ", text).strip()
    if not compact:
        return []
    parts = re.split(r"(?<=[.!?])\s+", compact)
    cleaned = []
    for sentence in parts:
        s = sentence.strip()
        if 45 <= len(s) <= 240:
            cleaned.append(s)
    return cleaned


def _rank_sentences(sentences: List[str], query_terms: List[str]) -> List[str]:
    scored = []
    for sentence in sentences:
        lowered = sentence.lower()
        overlap = sum(1 for term in query_terms if term in lowered)
        if query_terms and overlap == 0:
            continue
        digits_bonus = 1 if re.search(r"\d", sentence) else 0
        novelty_bonus = 1 if any(k in lowered for k in ["improves", "reduces", "outperforms", "study", "results"]) else 0
        score = overlap * 2 + digits_bonus + novelty_bonus
        scored.append((score, sentence))
    scored.sort(key=lambda item: item[0], reverse=True)
    ranked = []
    seen = set()
    for _, sentence in scored:
        key = sentence.lower()
        if key in seen:
            continue
        seen.add(key)
        ranked.append(sentence)
    return ranked


def generate_insights(trusted_items: List[Dict[str, Any]], query: str) -> Dict[str, Any]:
    """Generate easy-to-read insights from trusted items."""
    if not trusted_items:
        return {
            "summary": "No trusted data available to generate insights.",
            "concise_answer": "No reliable information is available yet for this query.",
            "key_points": [],
            "top_sources_detailed": [],
            "recommended_reading": [],
            "key_highlights": [],
            "source_breakdown": {},
            "content_type_breakdown": {},
            "confidence": 0.0,
        }

    sources = Counter((item.get("source") or "unknown") for item in trusted_items)
    content_types = Counter((item.get("content_type") or "unknown") for item in trusted_items)

    # Prefer diverse highlights: unique titles in order.
    seen = set()
    highlights = []
    for item in trusted_items:
        title = (item.get("title") or "").strip()
        if title and title.lower() not in seen:
            seen.add(title.lower())
            highlights.append(title)
        if len(highlights) >= 5:
            break

    avg_score = 0.0
    scores = [float((item.get("trust") or {}).get("score", 0.0)) for item in trusted_items]
    if scores:
        avg_score = sum(scores) / len(scores)

    query_terms = _extract_query_terms(query)
    ranked_items = sorted(
        trusted_items,
        key=lambda item: float((item.get("trust") or {}).get("score", 0.0)),
        reverse=True,
    )

    candidate_sentences: List[str] = []
    for item in ranked_items[:8]:
        candidate_sentences.extend(_split_sentences(item.get("content") or ""))
    ranked_sentences = _rank_sentences(candidate_sentences, query_terms)

    key_points = ranked_sentences[:5]
    concise_answer = " ".join(ranked_sentences[:3]).strip()
    if not concise_answer:
        concise_answer = (
            f"TrustWise found {len(trusted_items)} trusted sources for '{query}'. "
            "Open the source cards below for details and references."
        )

    top_sources_detailed = [
        {"source": source_name, "count": count}
        for source_name, count in sources.most_common(5)
    ]

    recommended_reading = []
    for item in ranked_items:
        title = (item.get("title") or "").strip()
        url = (item.get("url") or "").strip()
        if not title:
            continue
        recommended_reading.append(
            {
                "title": title,
                "source": item.get("source") or "unknown",
                "url": url,
                "published_at": item.get("published_at") or "",
            }
        )
        if len(recommended_reading) >= 4:
            break

    summary = (
        f"For query '{query}', the system retained {len(trusted_items)} trusted items "
        f"with average trust score {avg_score:.2f}."
    )

    return {
        "summary": summary,
        "concise_answer": concise_answer,
        "key_points": key_points,
        "top_sources_detailed": top_sources_detailed,
        "recommended_reading": recommended_reading,
        "key_highlights": highlights,
        "source_breakdown": dict(sources),
        "content_type_breakdown": dict(content_types),
        "confidence": round(avg_score, 3),
    }
