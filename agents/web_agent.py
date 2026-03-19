"""
TrustWise Web Agent — powered by Crawl4AI

Strategy:
  1. Takes the task prompt (e.g. "Find news about quantum computing")
  2. Searches the web for relevant URLs using DuckDuckGo
  3. Crawls those specific pages with Crawl4AI (headless Chromium)
  4. Returns clean Markdown content

Falls back to Wikipedia API + basic HTTP when Crawl4AI is unavailable.

Phase 1:
  - Collects raw text/markdown from web sources
  - No trust validation; no LLM summarisation
"""

import asyncio
import json
import re
from datetime import datetime
from typing import Dict, Any, List
from utils.config import Config
from utils.logger import setup_logger

logger = setup_logger(__name__)

# ───────────────────────────────────────────
# Crawl4AI availability check
# ───────────────────────────────────────────
try:
    from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
    from crawl4ai.markdown_generation_strategy import DefaultMarkdownGenerator
    from crawl4ai.content_filter_strategy import PruningContentFilter
    CRAWL4AI_AVAILABLE = True
    logger.info("[WebAgent] Crawl4AI is available — using headless browser scraping")
except ImportError:
    CRAWL4AI_AVAILABLE = False
    logger.warning("[WebAgent] Crawl4AI not installed — falling back to basic HTTP scraping")


# ═══════════════════════════════════════════
# Public entry point
# ═══════════════════════════════════════════

def run(task: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute a web scraping task.

    Flow:
      1. Extract search terms from the task prompt
      2. Search the web (DuckDuckGo) for relevant URLs
      3. Crawl those pages with Crawl4AI
      4. Also fetch Wikipedia for knowledge queries
      5. Return collected data

    Args:
        task: Dict with task_id, prompt, source_type, agent

    Returns:
        Dict with task results including status and raw data
    """
    task_id = task.get("task_id", "unknown")
    prompt = task.get("prompt", "")

    logger.info(f"[WebAgent] Processing task: {task_id}")
    logger.info(f"[WebAgent] Prompt: {prompt}")

    result = {
        "task_id": task_id,
        "agent": "web_agent",
        "status": "success",
        "timestamp": datetime.utcnow().isoformat(),
        "prompt": prompt,
        "data": [],
    }

    try:
        search_terms = _extract_search_terms(prompt)
        logger.info(f"[WebAgent] Search terms: {search_terms}")

        is_news_query = any(
            w in prompt.lower()
            for w in ["news", "latest", "recent", "update", "announcement", "release"]
        )

        # ── Step 1: Search the web for relevant URLs ──
        if CRAWL4AI_AVAILABLE and search_terms:
            logger.info("[WebAgent] Searching the web for relevant pages...")
            search_urls = _search_duckduckgo(search_terms, max_results=5)

            if search_urls:
                logger.info(f"[WebAgent] Found {len(search_urls)} relevant URLs to crawl")
                crawl_results = _run_async(_crawl_with_crawl4ai(search_urls, prompt))
                result["data"].extend(crawl_results)
            else:
                logger.warning("[WebAgent] No search results — crawling trusted sources")
                sources = _load_trusted_sources()
                if sources:
                    crawl_results = _run_async(_crawl_with_crawl4ai(sources[:3], prompt))
                    result["data"].extend(crawl_results)

        # ── Step 2: Wikipedia for knowledge queries ──
        if (not is_news_query and search_terms) or not result["data"]:
            logger.info("[WebAgent] Trying Wikipedia for knowledge content...")
            wiki_content = _fetch_from_wikipedia(search_terms)
            if wiki_content and len(wiki_content) > 500:
                result["data"].append({
                    "source": "Wikipedia",
                    "content": wiki_content,
                    "content_type": "text",
                    "fetch_time": datetime.utcnow().isoformat(),
                })

        # ── Step 3: Basic HTTP fallback if nothing collected ──
        if not result["data"] and not CRAWL4AI_AVAILABLE:
            logger.info("[WebAgent] Crawl4AI unavailable — using basic HTTP")
            sources = _load_trusted_sources()
            for url in sources[:2]:
                try:
                    content = _fetch_basic_http(url)
                    if content and len(content) > 200:
                        result["data"].append({
                            "source": url,
                            "content": content,
                            "content_type": "text",
                            "fetch_time": datetime.utcnow().isoformat(),
                        })
                except Exception as e:
                    logger.warning(f"[WebAgent] Failed to fetch {url}: {e}")

        if not result["data"]:
            result["status"] = "partial"
            result["message"] = "No data collected from any source"
            logger.warning(f"[WebAgent] Task {task_id} collected no data")

        if Config.SAVE_RAW_DATA:
            _save_raw_data(task_id, result)

    except Exception as e:
        logger.error(f"[WebAgent] Task {task_id} failed: {e}")
        result["status"] = "failed"
        result["error"] = str(e)

    return result


# ═══════════════════════════════════════════
# Web Search — find URLs relevant to the query
# ═══════════════════════════════════════════

def _search_duckduckgo(query: str, max_results: int = 5) -> List[str]:
    """
    Search DuckDuckGo for relevant URLs matching the query.

    Uses the duckduckgo_search library for reliable results.

    Returns:
        List of URLs relevant to the query
    """
    try:
        import warnings
        warnings.filterwarnings("ignore", category=RuntimeWarning)
        from duckduckgo_search import DDGS
    except ImportError:
        logger.warning("[WebAgent] duckduckgo_search not installed — cannot search web")
        return []

    try:
        logger.info(f"[WebAgent] DuckDuckGo search: {query}")
        results = DDGS().text(query, max_results=max_results)

        urls = []
        skip_domains = [
            "youtube.com", "facebook.com", "twitter.com", "x.com",
            "instagram.com", "reddit.com", "linkedin.com", "pinterest.com",
        ]

        for r in results:
            href = r.get("href", "")
            if href and not any(d in href for d in skip_domains):
                urls.append(href)
                logger.info(f"[WebAgent]   → {r.get('title', '?')[:70]}")
                logger.info(f"[WebAgent]     {href[:100]}")

        logger.info(f"[WebAgent] DuckDuckGo returned {len(urls)} URLs")
        return urls

    except Exception as e:
        logger.warning(f"[WebAgent] DuckDuckGo search failed: {e}")
        return []


# ═══════════════════════════════════════════
# Crawl4AI — crawl specific URLs
# ═══════════════════════════════════════════

async def _crawl_with_crawl4ai(
    urls: List[str],
    prompt: str,
) -> List[Dict[str, Any]]:
    """
    Use Crawl4AI to crawl specific URLs with a headless browser.

    Returns a list of dicts suitable for result["data"].
    """
    collected: List[Dict[str, Any]] = []

    browser_conf = BrowserConfig(
        headless=True,
        verbose=False,
    )

    # Markdown generator with content-pruning filter
    md_generator = DefaultMarkdownGenerator(
        content_filter=PruningContentFilter(
            threshold=0.4,
            threshold_type="fixed",
        )
    )

    run_conf = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,      # always fetch fresh
        markdown_generator=md_generator,
        page_timeout=15000,                # 15 s per page
        wait_until="domcontentloaded",
    )

    try:
        async with AsyncWebCrawler(config=browser_conf) as crawler:
            for url in urls:
                try:
                    logger.info(f"[WebAgent][Crawl4AI] Crawling: {url[:100]}")
                    result = await crawler.arun(url=url, config=run_conf)

                    if result.success:
                        # Prefer the filtered "fit" markdown; fall back to raw
                        content = ""
                        if result.markdown:
                            content = (
                                getattr(result.markdown, "fit_markdown", "")
                                or getattr(result.markdown, "raw_markdown", "")
                                or str(result.markdown)
                            )

                        if not content:
                            content = result.cleaned_html or ""

                        # Trim to a reasonable size
                        max_chars = 8_000
                        if len(content) > max_chars:
                            content = content[:max_chars] + "\n\n... (truncated)"

                        if len(content) > 100:
                            # Use the final URL (after redirects)
                            final_url = getattr(result, "url", url) or url
                            collected.append({
                                "source": final_url,
                                "content": content,
                                "content_type": "markdown",
                                "fetch_time": datetime.utcnow().isoformat(),
                                "crawl4ai_status": "success",
                            })
                            logger.info(
                                f"[WebAgent][Crawl4AI] ✓ {len(content)} chars from {url[:80]}"
                            )
                        else:
                            logger.warning(
                                f"[WebAgent][Crawl4AI] Content too short "
                                f"({len(content)} chars) from {url[:80]}"
                            )
                    else:
                        logger.warning(
                            f"[WebAgent][Crawl4AI] Crawl failed for {url[:80]}: "
                            f"{result.error_message}"
                        )

                except Exception as e:
                    logger.warning(f"[WebAgent][Crawl4AI] Error on {url[:80]}: {e}")
                    continue

    except Exception as e:
        logger.error(f"[WebAgent][Crawl4AI] Crawler init failed: {e}")

    return collected


# ═══════════════════════════════════════════
# Helpers
# ═══════════════════════════════════════════

def _run_async(coro):
    """Run an async coroutine from sync code (Flask context)."""
    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            import concurrent.futures
            with concurrent.futures.ThreadPoolExecutor() as pool:
                return pool.submit(asyncio.run, coro).result()
        else:
            return loop.run_until_complete(coro)
    except RuntimeError:
        return asyncio.run(coro)


def _load_trusted_sources() -> list:
    """Load trusted web sources from config/sources.json."""
    sources_file = Config.CONFIG_DIR / "sources.json"
    if not sources_file.exists():
        logger.warning(f"Sources file not found: {sources_file}")
        return []

    try:
        with open(sources_file, "r") as f:
            data = json.load(f)
            if isinstance(data, list):
                return data
            elif isinstance(data, dict) and "trusted_web_sources" in data:
                return data["trusted_web_sources"]
            else:
                logger.warning("Invalid sources.json format")
                return []
    except Exception as e:
        logger.error(f"Failed to load sources: {e}")
        return []


def _extract_search_terms(prompt: str) -> str:
    """Extract key search terms from the task prompt."""
    stop_words = {
        "fetch", "retrieve", "find", "get", "search", "for", "about",
        "articles", "papers", "from", "top", "blogs", "websites",
        "published", "recent", "latest", "the", "and", "or", "in",
        "on", "at", "to", "a", "an", "reputable", "online", "sources",
        "that", "have", "been", "with", "their", "this", "these",
        "those", "such", "also", "other", "some", "many", "more",
    }
    words = prompt.lower().split()
    terms = [w for w in words if w not in stop_words and len(w) > 2]
    return " ".join(terms[:6])


def _fetch_from_wikipedia(search_terms: str) -> str:
    """Fetch content from Wikipedia API."""
    try:
        import requests
    except ImportError:
        return ""

    try:
        url = "https://en.wikipedia.org/w/api.php"

        search_params = {
            "action": "opensearch",
            "search": search_terms,
            "limit": 1,
            "format": "json",
        }
        response = requests.get(url, params=search_params, timeout=10)
        response.raise_for_status()
        search_results = response.json()

        if not search_results[1]:
            logger.info(f"[WebAgent] No Wikipedia article found for: {search_terms}")
            return ""

        article_title = search_results[1][0]
        logger.info(f"[WebAgent] Found Wikipedia article: {article_title}")

        content_params = {
            "action": "query",
            "prop": "extracts",
            "titles": article_title,
            "explaintext": True,
            "exintro": False,
            "format": "json",
        }
        response = requests.get(url, params=content_params, timeout=10)
        response.raise_for_status()
        data = response.json()

        pages = data.get("query", {}).get("pages", {})
        for page_id, page_data in pages.items():
            if page_id != "-1":
                extract = page_data.get("extract", "")
                if extract:
                    max_chars = 5000
                    if len(extract) > max_chars:
                        extract = extract[:max_chars] + "\n... (truncated)"
                    wiki_url = (
                        f"https://en.wikipedia.org/wiki/"
                        f"{article_title.replace(' ', '_')}"
                    )
                    content = (
                        f"Wikipedia Article: {article_title}\n"
                        f"URL: {wiki_url}\n\n{extract}"
                    )
                    return content

        return ""

    except Exception as e:
        logger.warning(f"[WebAgent] Wikipedia fetch failed: {e}")
        return ""


def _fetch_basic_http(url: str) -> str:
    """Basic HTTP fallback (used when Crawl4AI is not available)."""
    try:
        import requests
        from bs4 import BeautifulSoup
    except ImportError:
        raise ImportError(
            "requests and beautifulsoup4 required. "
            "Install with: pip install requests beautifulsoup4"
        )

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36"
        )
    }
    response = requests.get(url, headers=headers, timeout=Config.WEB_SCRAPER_TIMEOUT)
    response.raise_for_status()

    soup = BeautifulSoup(response.content, "html.parser")
    for tag in soup(["script", "style", "nav", "footer", "header"]):
        tag.decompose()

    text = soup.get_text(separator="\n", strip=True)
    lines = [line.strip() for line in text.split("\n") if line.strip()]
    content = "\n".join(lines)

    max_chars = 8_000
    if len(content) > max_chars:
        content = content[:max_chars] + "\n... (truncated)"

    return content


def _save_raw_data(task_id: str, result: Dict[str, Any]):
    """Save raw agent output to file."""
    filename = f"{task_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
    filepath = Config.RAW_DATA_DIR / filename

    try:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        logger.info(f"[WebAgent] Saved raw data to {filepath}")
    except Exception as e:
        logger.error(f"[WebAgent] Failed to save raw data: {e}")
