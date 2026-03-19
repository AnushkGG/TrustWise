from collections import Counter
import json
import re
from typing import Any, Dict, List

from utils.config import Config
import logging

logger = logging.getLogger(__name__)


def _extract_query_terms(query: str) -> List[str]:
    words = re.findall(r"[a-zA-Z0-9]+", (query or "").lower())
    aliases = {
        "ai": ["artificial", "intelligence"],
        "ml": ["machine", "learning"],
        "nlp": ["language", "model", "models"],
    }
    stopwords = {
        "the", "a", "an", "and", "or", "to", "of", "for", "in", "on", "with",
        "about", "latest", "recent", "new", "tell", "me", "what", "is", "are",
        "from", "into", "at", "by", "as", "their", "its", "be", "this", "that",
    }
    terms: List[str] = []
    for w in words:
        if w in stopwords:
            continue
        if len(w) > 2 or w in aliases:
            terms.append(w)
            terms.extend(aliases.get(w, []))
    return list(dict.fromkeys(terms))


def _split_sentences(text: str) -> List[str]:
    if not text:
        return []
    compact = re.sub(r"\s+", " ", text).strip()
    if not compact:
        return []
    parts = re.split(r"(?<=[.!?])\s+", compact)
    cleaned = []
    for sentence in parts:
        s = _normalize_sentence(sentence)
        if 45 <= len(s) <= 240:
            cleaned.append(s)
    return cleaned


def _normalize_sentence(sentence: str) -> str:
    s = (sentence or "").strip()
    s = re.sub(r"^#+\s*", "", s)
    s = re.sub(r"\[([^\]]+)\]\([^\)]+\)", r"\1", s)
    s = re.sub(r"`([^`]+)`", r"\1", s)
    s = re.sub(r"\s+", " ", s)
    return s.strip()


def _rank_sentences(sentences: List[str], query_terms: List[str], require_overlap: bool = True) -> List[str]:
    scored = []
    for sentence in sentences:
        lowered = sentence.lower()
        overlap = sum(1 for term in query_terms if term in lowered)
        if require_overlap and query_terms and overlap == 0:
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


def _build_summary_context(items: List[Dict[str, Any]], max_items: int = 4, max_chars: int = 900) -> str:
    blocks: List[str] = []
    for idx, item in enumerate(items[:max_items], start=1):
        title = (item.get("title") or "Untitled").strip()
        source = (item.get("source") or "unknown").strip()
        content = _normalize_sentence((item.get("content") or "").replace("\n", " "))
        snippet = content[:max_chars]
        blocks.append(
            f"Source {idx}: {source}\n"
            f"Title {idx}: {title}\n"
            f"Content {idx}: {snippet}"
        )
    return "\n\n".join(blocks)


def _parse_json_response(raw: str) -> Dict[str, Any]:
    text = (raw or "").strip()
    if not text:
        return {}

    text = re.sub(r"^```json\s*", "", text, flags=re.IGNORECASE)
    text = re.sub(r"^```\s*", "", text)
    text = re.sub(r"\s*```$", "", text)
    try:
        return json.loads(text)
    except Exception:
        start = text.find("{")
        end = text.rfind("}")
        if start >= 0 and end > start:
            try:
                return json.loads(text[start : end + 1])
            except Exception:
                return {}
        return {}


def _call_llm_for_summary(query: str, context: str) -> Dict[str, Any]:
    system_prompt = (
        "You are a precise research summarizer. "
        "Write concise, factual summaries from provided sources only. "
        "Do not include cookie/privacy/legal boilerplate."
    )
    user_prompt = (
        "Summarize the information for the query below.\n"
        "Return ONLY valid JSON with keys: concise_answer (string), key_points (array of 3-5 strings).\n"
        "Rules:\n"
        "- concise_answer: 2-4 sentences, plain English, max 120 words\n"
        "- key_points: 3-5 bullets, each 1 sentence\n"
        "- keep it brief and relevant to the query\n"
        "- if evidence is weak, say so clearly\n\n"
        f"Query: {query}\n\n"
        f"Sources:\n{context}"
    )

    provider = Config.LLM_PROVIDER

    if provider == "ollama":
        try:
            import requests

            payload = {
                "model": Config.LLM_MODEL,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                "stream": False,
                "format": "json",
                "options": {
                    "temperature": 0.1,
                    "num_predict": 500,
                },
            }
            response = requests.post(
                f"{Config.OLLAMA_BASE_URL}/api/chat",
                json=payload,
                timeout=90,
            )
            response.raise_for_status()
            content = response.json().get("message", {}).get("content", "")
            return _parse_json_response(content)
        except Exception as exc:
            logger.warning("[Insights] Ollama summary failed: %s", exc)
            return {}

    if provider == "openai" and Config.OPENAI_API_KEY:
        try:
            from openai import OpenAI

            client = OpenAI(api_key=Config.OPENAI_API_KEY)
            response = client.chat.completions.create(
                model=Config.LLM_MODEL,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.1,
                max_tokens=500,
                response_format={"type": "json_object"},
            )
            content = response.choices[0].message.content or ""
            return _parse_json_response(content)
        except Exception as exc:
            logger.warning("[Insights] OpenAI summary failed: %s", exc)
            return {}

    if provider == "anthropic" and Config.ANTHROPIC_API_KEY:
        try:
            from anthropic import Anthropic

            client = Anthropic(api_key=Config.ANTHROPIC_API_KEY)
            response = client.messages.create(
                model=Config.LLM_MODEL,
                max_tokens=500,
                temperature=0.1,
                messages=[
                    {"role": "user", "content": f"{system_prompt}\n\n{user_prompt}"},
                ],
            )
            parts = []
            for block in (response.content or []):
                text_part = getattr(block, "text", "")
                if text_part:
                    parts.append(text_part)
            content = "\n".join(parts)
            return _parse_json_response(content)
        except Exception as exc:
            logger.warning("[Insights] Anthropic summary failed: %s", exc)
            return {}

    return {}


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
    ranked_sentences = _rank_sentences(candidate_sentences, query_terms, require_overlap=True)
    if not ranked_sentences and candidate_sentences:
        # Fallback for sparse/noisy content where exact term overlap is unavailable.
        ranked_sentences = _rank_sentences(candidate_sentences, query_terms, require_overlap=False)

    # Default extractive result (always available as fallback).
    key_points = ranked_sentences[:5]
    concise_answer = " ".join(ranked_sentences[:3]).strip()

    # Prefer LLM-generated brief summary when model is available.
    summary_method = "extractive"
    context = _build_summary_context(ranked_items)
    if context:
        llm_json = _call_llm_for_summary(query=query, context=context)
        llm_answer = _normalize_sentence(str(llm_json.get("concise_answer") or ""))
        llm_points = llm_json.get("key_points") or []
        if isinstance(llm_points, list):
            llm_points = [_normalize_sentence(str(p)) for p in llm_points if str(p).strip()]
        else:
            llm_points = []

        if llm_answer:
            concise_answer = llm_answer
            summary_method = "llm"
        if llm_points:
            key_points = llm_points[:5]
            summary_method = "llm"

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
        "summary_method": summary_method,
        "top_sources_detailed": top_sources_detailed,
        "recommended_reading": recommended_reading,
        "key_highlights": highlights,
        "source_breakdown": dict(sources),
        "content_type_breakdown": dict(content_types),
        "confidence": round(avg_score, 3),
    }
