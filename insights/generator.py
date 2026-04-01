from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed
from difflib import SequenceMatcher
import json
import re
from typing import Any, Dict, List, Tuple

from utils.config import Config
from utils.logger import setup_logger

logger = setup_logger(__name__)


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


def _summary_prompt(query: str, context: str) -> Tuple[str, str]:
    """Return (system_prompt, user_prompt) pair for summary generation."""
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
    return system_prompt, user_prompt


def _ollama_summary(system_prompt: str, user_prompt: str) -> Dict[str, Any]:
    """Call Ollama for an insight summary."""
    import requests

    model_name = Config.get_ollama_model()
    payload = {
        "model": model_name,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        "stream": False,
        "format": "json",
        "options": {"temperature": 0.1, "num_predict": 500},
    }
    response = requests.post(
        f"{Config.OLLAMA_BASE_URL}/api/chat",
        json=payload,
        timeout=90,
    )
    response.raise_for_status()
    content = response.json().get("message", {}).get("content", "")
    return _parse_json_response(content)


def _gemini_summary(system_prompt: str, user_prompt: str) -> Dict[str, Any]:
    """Call Gemini for an insight summary."""
    import google.generativeai as genai

    genai.configure(api_key=Config.GEMINI_API_KEY)
    model_name = Config.get_gemini_model()
    model = genai.GenerativeModel(
        model_name=model_name,
        generation_config=genai.GenerationConfig(
            temperature=0.1,
            max_output_tokens=500,
            response_mime_type="application/json",
        ),
        system_instruction=system_prompt,
    )
    response = model.generate_content(user_prompt)
    content = response.text or ""
    return _parse_json_response(content)


# ---------------------------------------------------------------------------
# Merge helpers for insight summaries
# ---------------------------------------------------------------------------

def _point_similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def _merge_summaries(
    gemini_result: Dict[str, Any],
    ollama_result: Dict[str, Any],
) -> Dict[str, Any]:
    """Merge two LLM summaries with source attribution on every field."""
    g_answer = str(gemini_result.get("concise_answer") or "").strip()
    o_answer = str(ollama_result.get("concise_answer") or "").strip()

    if len(g_answer) >= len(o_answer) and g_answer:
        concise_answer = g_answer
        concise_answer_origin = "gemini"
    elif o_answer:
        concise_answer = o_answer
        concise_answer_origin = "ollama"
    else:
        concise_answer = ""
        concise_answer_origin = ""

    g_points = gemini_result.get("key_points") or []
    o_points = ollama_result.get("key_points") or []
    if not isinstance(g_points, list):
        g_points = []
    if not isinstance(o_points, list):
        o_points = []
    g_points = [str(p).strip() for p in g_points if str(p).strip()]
    o_points = [str(p).strip() for p in o_points if str(p).strip()]

    tagged_g = [{"text": p, "origin": "gemini"} for p in g_points]
    tagged_o = [{"text": p, "origin": "ollama"} for p in o_points]

    # Balanced interleave
    interleaved: List[Dict[str, str]] = []
    it_g, it_o = iter(tagged_g), iter(tagged_o)
    done_g = done_o = False
    sentinel = object()
    while not (done_g and done_o):
        if not done_g:
            val = next(it_g, sentinel)
            if val is sentinel:
                done_g = True
            else:
                interleaved.append(val)  # type: ignore[arg-type]
        if not done_o:
            val = next(it_o, sentinel)
            if val is sentinel:
                done_o = True
            else:
                interleaved.append(val)  # type: ignore[arg-type]

    # Deduplicate near-identical points
    kept: List[Dict[str, str]] = []
    for item in interleaved:
        dup = False
        for existing in kept:
            if _point_similarity(item["text"], existing["text"]) >= 0.75:
                existing["origin"] = "both"
                dup = True
                break
        if not dup:
            kept.append(item)

    return {
        "concise_answer": concise_answer,
        "concise_answer_origin": concise_answer_origin,
        "key_points": kept[:5],
    }


def _call_both_for_summary(query: str, context: str) -> Dict[str, Any]:
    """Call Gemini and Ollama in parallel for summary, merge results."""
    sys_p, usr_p = _summary_prompt(query, context)

    results: Dict[str, Dict[str, Any]] = {}
    errors: Dict[str, str] = {}

    def _run_gemini() -> Tuple[str, Dict[str, Any]]:
        return "gemini", _gemini_summary(sys_p, usr_p)

    def _run_ollama() -> Tuple[str, Dict[str, Any]]:
        return "ollama", _ollama_summary(sys_p, usr_p)

    with ThreadPoolExecutor(max_workers=2) as pool:
        futures = {pool.submit(fn): fn for fn in (_run_gemini, _run_ollama)}
        for future in as_completed(futures):
            try:
                provider, data = future.result()
                results[provider] = data
            except Exception as exc:
                fn = futures[future]
                provider = "gemini" if fn is _run_gemini else "ollama"
                errors[provider] = str(exc)
                logger.warning("[Insights] %s summary failed in 'both' mode: %s", provider, exc)

    gemini_res = results.get("gemini") or {}
    ollama_res = results.get("ollama") or {}

    if gemini_res and ollama_res:
        return _merge_summaries(gemini_res, ollama_res)

    if gemini_res:
        return gemini_res
    if ollama_res:
        return ollama_res
    return {}


def _call_llm_for_summary(query: str, context: str) -> Dict[str, Any]:
    """Route to the correct summary provider(s)."""
    provider = Config.LLM_PROVIDER

    if provider == "both":
        return _call_both_for_summary(query, context)

    sys_p, usr_p = _summary_prompt(query, context)

    if provider == "ollama":
        try:
            return _ollama_summary(sys_p, usr_p)
        except Exception as exc:
            logger.warning("[Insights] Ollama summary failed: %s", exc)
            return {}

    if provider == "gemini" and Config.GEMINI_API_KEY:
        try:
            return _gemini_summary(sys_p, usr_p)
        except Exception as exc:
            logger.warning("[Insights] Gemini summary failed: %s", exc)
            return {}

    return {}


def generate_insights(trusted_items: List[Dict[str, Any]], query: str, source_links: List[Dict[str, Any]] = None) -> Dict[str, Any]:
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

    summary_method = "extractive"
    concise_answer_origin = ""
    context = _build_summary_context(ranked_items)
    if context:
        llm_json = _call_llm_for_summary(query=query, context=context)
        llm_answer = _normalize_sentence(str(llm_json.get("concise_answer") or ""))
        concise_answer_origin = llm_json.get("concise_answer_origin", "")
        llm_points = llm_json.get("key_points") or []

        if isinstance(llm_points, list):
            # In "both" mode points are dicts {"text": ..., "origin": ...};
            # in single-provider mode they are plain strings.
            normalized: list = []
            for p in llm_points:
                if isinstance(p, dict):
                    txt = _normalize_sentence(str(p.get("text") or ""))
                    if txt:
                        normalized.append({"text": txt, "origin": p.get("origin", "")})
                else:
                    txt = _normalize_sentence(str(p))
                    if txt:
                        normalized.append(txt)
            llm_points = normalized
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

    result = {
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
        "citation_links": source_links or [],
    }
    if concise_answer_origin:
        result["concise_answer_origin"] = concise_answer_origin
    return result
