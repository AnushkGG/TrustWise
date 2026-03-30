import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from difflib import SequenceMatcher
from typing import Dict, List, Optional, Tuple

from utils.config import Config
from utils.logger import setup_logger
from orchestrator.prompts import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE

logger = setup_logger(__name__)

_SENTINEL = object()


def _truncate(text: str, max_len: int) -> str:
    text = text.strip()
    if len(text) <= max_len:
        return text
    return text[: max_len - 3].rstrip() + "..."


def build_mock_plan(user_query: str) -> dict:
    """
    Build a minimal valid plan when no LLM is available (no API key, Ollama down, etc.).
    Incorporates the user query into goal and task prompts so runs are distinguishable.
    """
    q = (user_query or "").strip() or "General research query"
    goal = _truncate(q, 280)
    snippet = _truncate(q, 800)
    words = [
        w.lower().strip(".,;:!?")
        for w in q.replace("/", " ").split()
        if len(w.strip(".,;:!?")) > 2
    ]
    seen = []
    for w in words:
        if w not in seen:
            seen.append(w)
        if len(seen) >= 4:
            break
    domains = seen[:4] if seen else ["general_research"]

    return {
        "goal": goal,
        "domains": domains,
        "time_range": "latest",
        "sources": ["web", "research_papers"],
        "plan_source": "mock",
        "tasks": [
            {
                "task_id": "task_web_1",
                "source_type": "web",
                "agent": "web_agent",
                "prompt": (
                    "Find recent web sources, news, and documentation related to: " + snippet
                ),
            },
            {
                "task_id": "task_paper_1",
                "source_type": "research_papers",
                "agent": "research_agent",
                "prompt": (
                    "Search academic papers and preprints related to: " + snippet
                ),
            },
        ],
    }


def mock_plan_json(user_query: str) -> str:
    """JSON string for mock plan (UTF-8 safe)."""
    return json.dumps(build_mock_plan(user_query), ensure_ascii=False)


def call_llm(user_query: str) -> str:
    """
    Calls the configured LLM to generate a structured execution plan.

    Supported providers:
      - ``gemini``  -- Google Gemini API (cloud, requires GEMINI_API_KEY)
      - ``ollama``  -- Local Ollama server (no API key needed)
      - ``both``    -- Call Gemini + Ollama in parallel, merge results

    Falls back to a mock response when the required API key is missing
    or when authentication fails.
    """

    if Config.LLM_PROVIDER in ("gemini", "both") and not Config.GEMINI_API_KEY:
        logger.warning("GEMINI_API_KEY not set. Using mock plan derived from user query.")
        return mock_plan_json(user_query)

    if Config.LLM_PROVIDER == "both":
        return _call_both(user_query)

    user_prompt = USER_PROMPT_TEMPLATE.format(query=user_query)

    try:
        if Config.LLM_PROVIDER == "gemini":
            return _call_gemini(user_prompt)
        elif Config.LLM_PROVIDER == "ollama":
            try:
                import requests as req_lib
                return _call_ollama(user_prompt)
            except (req_lib.exceptions.ConnectionError, req_lib.exceptions.Timeout) as e:
                logger.warning(
                    "Ollama unavailable (%s). Using mock plan for pipeline continuity.",
                    e,
                )
                return mock_plan_json(user_query)
        else:
            raise ValueError(f"Unsupported LLM provider: {Config.LLM_PROVIDER}")
    except Exception as e:
        error_str = str(e)

        if "401" in error_str or "invalid" in error_str.lower() or "authentication" in error_str.lower():
            logger.error("Authentication failed: %s", e)
            logger.warning("Invalid API key detected. Falling back to mock mode.")
            return mock_plan_json(user_query)

        logger.error("LLM call failed: %s", e)
        raise


def _call_gemini(user_prompt: str, model_override: Optional[str] = None) -> str:
    """Call Google Gemini API."""
    try:
        import google.generativeai as genai
    except ImportError:
        logger.error("google-generativeai package not installed. Run: pip install google-generativeai")
        raise ImportError("google-generativeai required. Install with: pip install google-generativeai")

    genai.configure(api_key=Config.GEMINI_API_KEY)

    model_name = model_override or Config.LLM_MODEL
    logger.info("Calling Gemini %s...", model_name)

    model = genai.GenerativeModel(
        model_name=model_name,
        generation_config=genai.GenerationConfig(
            temperature=Config.LLM_TEMPERATURE,
            max_output_tokens=Config.LLM_MAX_TOKENS,
            response_mime_type="application/json",
        ),
        system_instruction=SYSTEM_PROMPT,
    )

    response = model.generate_content(user_prompt)

    content = response.text
    if not content:
        raise ValueError("Gemini returned empty response")

    logger.info("Gemini response received")
    return content


def _call_ollama(user_prompt: str, model_override: Optional[str] = None) -> str:
    """Call local Ollama API."""
    try:
        import requests
    except ImportError:
        logger.error("requests package not installed. Run: pip install requests")
        raise ImportError("requests package required. Install with: pip install requests")

    model_name = model_override or Config.LLM_MODEL
    logger.info("Calling Ollama %s at %s...", model_name, Config.OLLAMA_BASE_URL)

    url = f"{Config.OLLAMA_BASE_URL}/api/chat"

    payload = {
        "model": model_name,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt},
        ],
        "stream": False,
        "format": "json",
        "options": {
            "temperature": Config.LLM_TEMPERATURE,
            "num_predict": Config.LLM_MAX_TOKENS,
        },
    }

    try:
        response = requests.post(url, json=payload, timeout=120)
        response.raise_for_status()

        result = response.json()
        content = result.get("message", {}).get("content", "")

        if not content:
            raise ValueError("Ollama returned empty response")

        logger.info("Ollama response received")
        return content

    except requests.exceptions.ConnectionError:
        logger.error("Failed to connect to Ollama at %s", Config.OLLAMA_BASE_URL)
        logger.error("Make sure Ollama is running: ollama serve")
        raise
    except requests.exceptions.Timeout:
        logger.error("Ollama request timed out")
        raise


# ---------------------------------------------------------------------------
# Merge helpers
# ---------------------------------------------------------------------------

def _prompt_similarity(a: str, b: str) -> float:
    """Ratio of similarity between two task prompts (0..1)."""
    return SequenceMatcher(None, a.lower(), b.lower()).ratio()


def _interleave(list_a: list, list_b: list) -> list:
    """Balanced round-robin interleave of two lists."""
    result: list = []
    it_a, it_b = iter(list_a), iter(list_b)
    exhausted_a = exhausted_b = False
    while not (exhausted_a and exhausted_b):
        if not exhausted_a:
            val = next(it_a, _SENTINEL)
            if val is _SENTINEL:
                exhausted_a = True
            else:
                result.append(val)
        if not exhausted_b:
            val = next(it_b, _SENTINEL)
            if val is _SENTINEL:
                exhausted_b = True
            else:
                result.append(val)
    return result


def _stamp_tasks(tasks: list, origin: str) -> list:
    """Add ``origin`` tag to every task dict."""
    for t in tasks:
        t.setdefault("origin", origin)
    return tasks


def _dedup_tasks(tasks: list, threshold: float = 0.80) -> list:
    """Remove near-duplicate tasks by prompt similarity.

    When two tasks are close enough, the first one is kept and its ``origin``
    is set to ``"both"`` to show it was suggested by both providers.
    """
    kept: List[dict] = []
    for task in tasks:
        duplicate = False
        for existing in kept:
            if _prompt_similarity(task.get("prompt", ""), existing.get("prompt", "")) >= threshold:
                existing["origin"] = "both"
                duplicate = True
                break
        if not duplicate:
            kept.append(task)
    return kept


def _renumber_tasks(tasks: list) -> list:
    """Re-assign sequential ``task_id`` values after merge."""
    web_idx = paper_idx = 0
    for task in tasks:
        if task.get("source_type") == "research_papers":
            paper_idx += 1
            task["task_id"] = f"task_paper_{paper_idx}"
        else:
            web_idx += 1
            task["task_id"] = f"task_web_{web_idx}"
    return tasks


def _merge_plans(gemini_plan: dict, ollama_plan: dict) -> dict:
    """Merge two provider plans into a single balanced plan with attribution."""
    g_goal = (gemini_plan.get("goal") or "").strip()
    o_goal = (ollama_plan.get("goal") or "").strip()
    goal = g_goal if len(g_goal) >= len(o_goal) else o_goal
    goal_origin = "gemini" if len(g_goal) >= len(o_goal) else "ollama"

    # Domains: case-insensitive union
    seen_domains: dict = {}
    for d in (gemini_plan.get("domains") or []) + (ollama_plan.get("domains") or []):
        key = d.lower()
        if key not in seen_domains:
            seen_domains[key] = d
    domains = list(seen_domains.values())

    # Time range: prefer specific over "latest"
    g_tr = (gemini_plan.get("time_range") or "latest").strip()
    o_tr = (ollama_plan.get("time_range") or "latest").strip()
    time_range = g_tr if g_tr.lower() != "latest" else o_tr

    # Sources: union
    sources = list(dict.fromkeys(
        (gemini_plan.get("sources") or []) + (ollama_plan.get("sources") or [])
    ))

    # Tasks: stamp origin, interleave, dedup, renumber, cap at 8
    g_tasks = _stamp_tasks(list(gemini_plan.get("tasks") or []), "gemini")
    o_tasks = _stamp_tasks(list(ollama_plan.get("tasks") or []), "ollama")
    merged_tasks = _interleave(g_tasks, o_tasks)
    merged_tasks = _dedup_tasks(merged_tasks)
    merged_tasks = _renumber_tasks(merged_tasks)[:8]

    return {
        "goal": goal,
        "goal_origin": goal_origin,
        "domains": domains,
        "time_range": time_range,
        "sources": sources,
        "plan_source": "merged",
        "providers": ["gemini", "ollama"],
        "tasks": merged_tasks,
    }


# ---------------------------------------------------------------------------
# Dual-provider runtime path
# ---------------------------------------------------------------------------

def _call_both(user_query: str) -> str:
    """Call Gemini and Ollama in parallel, merge their plans.

    Graceful degradation: if one fails the other is used alone; if both fail
    the mock plan is returned.
    """
    user_prompt = USER_PROMPT_TEMPLATE.format(query=user_query)
    gemini_model = Config.get_gemini_model()
    ollama_model = Config.get_ollama_model()

    results: Dict[str, Optional[str]] = {"gemini": None, "ollama": None}
    errors: Dict[str, str] = {}

    def _run_gemini() -> Tuple[str, str]:
        return "gemini", _call_gemini(user_prompt, model_override=gemini_model)

    def _run_ollama() -> Tuple[str, str]:
        return "ollama", _call_ollama(user_prompt, model_override=ollama_model)

    with ThreadPoolExecutor(max_workers=2) as pool:
        futures = {pool.submit(fn): fn for fn in (_run_gemini, _run_ollama)}
        for future in as_completed(futures):
            try:
                provider, raw_json = future.result()
                results[provider] = raw_json
            except Exception as exc:
                fn = futures[future]
                provider = "gemini" if fn is _run_gemini else "ollama"
                errors[provider] = str(exc)
                logger.warning("%s failed during 'both' mode: %s", provider, exc)

    gemini_raw = results["gemini"]
    ollama_raw = results["ollama"]

    if gemini_raw and ollama_raw:
        try:
            g_plan = json.loads(gemini_raw)
            o_plan = json.loads(ollama_raw)
            merged = _merge_plans(g_plan, o_plan)
            logger.info("Merged plans from both Gemini and Ollama")
            return json.dumps(merged, ensure_ascii=False)
        except (json.JSONDecodeError, ValueError) as exc:
            logger.warning("Failed to parse/merge plans: %s — falling back to first valid", exc)
            return gemini_raw  # prefer Gemini on parse failure

    if gemini_raw:
        logger.warning("Ollama unavailable in 'both' mode; using Gemini result only.")
        try:
            plan = json.loads(gemini_raw)
            _stamp_tasks(plan.get("tasks", []), "gemini")
            plan["plan_source"] = "gemini"
            plan["providers"] = ["gemini"]
            return json.dumps(plan, ensure_ascii=False)
        except (json.JSONDecodeError, ValueError):
            return gemini_raw

    if ollama_raw:
        logger.warning("Gemini unavailable in 'both' mode; using Ollama result only.")
        try:
            plan = json.loads(ollama_raw)
            _stamp_tasks(plan.get("tasks", []), "ollama")
            plan["plan_source"] = "ollama"
            plan["providers"] = ["ollama"]
            return json.dumps(plan, ensure_ascii=False)
        except (json.JSONDecodeError, ValueError):
            return ollama_raw

    logger.error("Both providers failed in 'both' mode. Falling back to mock plan.")
    return mock_plan_json(user_query)
