"""
TrustWise Citation Scraper

Scrapes data relevant to an input query from curated trusted citation sources.
For each citation that yields content, creates a per-source .md file.
Also creates a combined summary .md file with the most relevant data from all sources.
Returns structured data with source links for the insights pipeline.
"""

import asyncio
import hashlib
import json
import re
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

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
except ImportError:
    CRAWL4AI_AVAILABLE = False

# ───────────────────────────────────────────
# DuckDuckGo availability check
# ───────────────────────────────────────────
DDGS_AVAILABLE = False
try:
    import warnings
    warnings.filterwarnings("ignore", category=RuntimeWarning)
    # Try new package first (the old one was renamed)
    try:
        from ddgs import DDGS
        DDGS_AVAILABLE = True
    except ImportError:
        from duckduckgo_search import DDGS
        DDGS_AVAILABLE = True
except ImportError:
    DDGS_AVAILABLE = False


# ═══════════════════════════════════════════
# Load citation sources
# ═══════════════════════════════════════════

def _load_trusted_citations() -> Dict[str, Any]:
    """Load the structured trusted citations from config."""
    citations_file = Config.CONFIG_DIR / "trusted_citations.json"
    if not citations_file.exists():
        logger.warning(f"[CitationScraper] trusted_citations.json not found at {citations_file}")
        return {}
    try:
        with open(citations_file, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        logger.error(f"[CitationScraper] Failed to load trusted_citations.json: {e}")
        return {}


def _get_all_sources(citations_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Flatten all sources from all categories into a single list."""
    all_sources = []
    categories = citations_data.get("categories", {})
    for cat_key, cat_data in categories.items():
        for source in cat_data.get("sources", []):
            source_copy = dict(source)
            source_copy["category"] = cat_data.get("label", cat_key)
            all_sources.append(source_copy)
    return all_sources


# ═══════════════════════════════════════════
# Relevance matching — pick which sources to scrape
# ═══════════════════════════════════════════

def _extract_query_terms(query: str) -> List[str]:
    """Extract meaningful search terms from the query."""
    words = re.findall(r"[a-zA-Z0-9]+", (query or "").lower())
    stop_words = {
        "fetch", "retrieve", "find", "get", "search", "for", "about",
        "articles", "papers", "from", "top", "blogs", "websites",
        "published", "recent", "latest", "the", "and", "or", "in",
        "on", "at", "to", "a", "an", "reputable", "online", "sources",
        "that", "have", "been", "with", "their", "this", "these",
        "those", "such", "also", "other", "some", "many", "more",
        "information", "give", "me", "updates", "tell", "what", "is",
        "are", "how", "can", "does", "do", "news",
        "major", "latest", "recent", "new", "changes", "announcement",
        "announcements", "product", "products", "launch", "launches",
        "results", "report", "reports",
    }
    aliases = {
        "ai": ["artificial", "intelligence"],
        "ml": ["machine", "learning"],
        "nlp": ["natural", "language", "processing"],
        "llm": ["large", "language", "model"],
        "dl": ["deep", "learning"],
        "cv": ["computer", "vision"],
        "devops": ["development", "operations"],
        "k8s": ["kubernetes"],
        "infosec": ["information", "security"],
    }
    terms: List[str] = []
    for w in words:
        if w in stop_words:
            continue
        if len(w) > 2 or w in aliases:
            terms.append(w)
            terms.extend(aliases.get(w, []))
    return list(dict.fromkeys(terms))[:10]


def _source_relevance_score(source: Dict[str, Any], query_terms: List[str]) -> int:
    """Score how relevant a citation source is for the given query terms."""
    score = 0
    tags = [t.lower() for t in source.get("tags", [])]
    name = source.get("name", "").lower()
    url = source.get("url", "").lower()
    category = source.get("category", "").lower()

    searchable = " ".join(tags + [name, url, category])
    tokens = set(re.findall(r"[a-zA-Z0-9]+", searchable))

    for term in query_terms:
        if term in tokens:
            score += 2
        # Conservative partial matching for longer terms only.
        if len(term) >= 5:
            for tag in tags:
                if term in tag or tag in term:
                    score += 1
                    break

        # Lightweight acronym bridge: gcp/aws style exact acronyms in url/name.
        if len(term) <= 4 and term.isalpha():
            if re.search(rf"\b{re.escape(term)}\b", name) or re.search(rf"\b{re.escape(term)}\b", url):
                score += 1
    
    return score


def _select_relevant_sources(
    all_sources: List[Dict[str, Any]],
    query_terms: List[str],
    max_sources: int = 15,
) -> List[Dict[str, Any]]:
    """Select the most relevant citation sources for the query."""
    scored = []
    for source in all_sources:
        score = _source_relevance_score(source, query_terms)
        if score > 0:
            scored.append((score, source))
    
    # Sort by score descending
    scored.sort(key=lambda x: x[0], reverse=True)
    
    # If we have fewer than 5 matches, add some general-purpose sources
    selected = [s for _, s in scored[:max_sources]]
    
    if len(selected) < 5:
        # Add general-purpose tech sources that weren't already selected
        selected_urls = {s["url"] for s in selected}
        general_sources = [
            s for s in all_sources
            if s["url"] not in selected_urls and any(
                t in s.get("tags", []) for t in ["ai", "research", "engineering", "news"]
            )
        ]
        for s in general_sources[:max_sources - len(selected)]:
            selected.append(s)
    
    return selected


def _apply_intent_source_filter(
    sources: List[Dict[str, Any]],
    query_terms: List[str],
) -> List[Dict[str, Any]]:
    """Apply lightweight intent-specific source filtering for noisy domains."""
    term_set = set(query_terms)

    fintech_intent = bool(
        term_set.intersection(
            {"fintech", "payments", "payment", "bank", "banking", "rbi", "sec", "fraud", "regulatory", "finance", "crypto"}
        )
    )
    if not fintech_intent:
        return sources

    fintech_tags = {
        "fintech", "payments", "payment", "bank", "banking", "finance", "crypto",
        "regulatory", "stripe", "paypal", "square",
    }
    filtered: List[Dict[str, Any]] = []
    for s in sources:
        tags = {str(t).lower() for t in s.get("tags", [])}
        name = str(s.get("name", "")).lower()
        if tags.intersection(fintech_tags):
            filtered.append(s)
            continue
        if any(k in name for k in ("stripe", "paypal", "square", "fintech", "bank")):
            filtered.append(s)

    return filtered if filtered else sources


# ═══════════════════════════════════════════
# DuckDuckGo site-specific search
# ═══════════════════════════════════════════

def _search_source_duckduckgo(
    query: str,
    source_url: str,
    max_results: int = 3,
) -> List[Dict[str, str]]:
    """
    Search DuckDuckGo for query content specifically from a given source domain.
    Returns list of {"url": ..., "title": ..., "snippet": ...}
    """
    if not DDGS_AVAILABLE:
        return []
    
    domain = re.search(r"https?://([^/]+)", source_url)
    if not domain:
        return []
    domain_str = domain.group(1).replace("www.", "")
    
    site_query = f"site:{domain_str} {query}"
    
    try:
        results = []
        # Try new API (positional query) then old API (keywords kwarg)
        for attempt_fn in [
            lambda: DDGS().text(site_query, max_results=max_results),
            lambda: DDGS().text(keywords=site_query, max_results=max_results),
        ]:
            try:
                results = attempt_fn()
                if results:
                    break
            except (TypeError, Exception):
                continue
        
        hits = []
        for r in results:
            href = r.get("href", "")
            if href and href.startswith("http"):
                hits.append({
                    "url": href,
                    "title": r.get("title", ""),
                    "snippet": r.get("body", ""),
                })
        return hits[:max_results]
    
    except Exception as e:
        logger.debug(f"[CitationScraper] DDG site search failed for {domain_str}: {e}")
        return []


# ═══════════════════════════════════════════
# Crawl4AI scraping
# ═══════════════════════════════════════════

async def _crawl_urls(urls: List[str], query_terms: List[str]) -> List[Dict[str, Any]]:
    """Crawl a list of URLs with Crawl4AI and return content."""
    if not CRAWL4AI_AVAILABLE or not urls:
        return []
    
    collected = []
    
    browser_conf = BrowserConfig(
        headless=True,
        verbose=False,
    )
    
    md_generator = DefaultMarkdownGenerator(
        content_filter=PruningContentFilter(
            threshold=0.4,
            threshold_type="fixed",
        )
    )
    
    run_conf = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
        markdown_generator=md_generator,
        page_timeout=12000,
        wait_until="domcontentloaded",
    )
    
    try:
        async with AsyncWebCrawler(config=browser_conf) as crawler:
            for url in urls:
                try:
                    result = await crawler.arun(url=url, config=run_conf)
                    
                    if result.success:
                        content = ""
                        if result.markdown:
                            content = (
                                getattr(result.markdown, "fit_markdown", "")
                                or getattr(result.markdown, "raw_markdown", "")
                                or str(result.markdown)
                            )
                        if not content:
                            content = result.cleaned_html or ""
                        
                        # Trim to reasonable size
                        max_chars = 6_000
                        if len(content) > max_chars:
                            content = content[:max_chars] + "\n\n... (truncated)"
                        
                        if len(content) > 150:
                            final_url = getattr(result, "url", url) or url
                            collected.append({
                                "requested_url": url,
                                "url": final_url,
                                "content": content,
                                "success": True,
                            })
                except Exception as e:
                    logger.debug(f"[CitationScraper] Crawl error on {url[:80]}: {e}")
                    continue
    except Exception as e:
        logger.error(f"[CitationScraper] Crawler init failed: {e}")
    
    return collected


def _fetch_basic_http(url: str) -> str:
    """Basic HTTP fallback for when Crawl4AI is unavailable."""
    try:
        import requests
        from bs4 import BeautifulSoup
    except ImportError:
        return ""
    
    try:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36"
            )
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, "html.parser")
        for tag in soup(["script", "style", "nav", "footer", "header"]):
            tag.decompose()
        
        text = soup.get_text(separator="\n", strip=True)
        lines = [line.strip() for line in text.split("\n") if line.strip()]
        content = "\n".join(lines)
        
        max_chars = 6_000
        if len(content) > max_chars:
            content = content[:max_chars] + "\n... (truncated)"
        
        return content
    except Exception as e:
        logger.debug(f"[CitationScraper] Basic HTTP fetch failed for {url[:80]}: {e}")
        return ""


# ═══════════════════════════════════════════
# Run async from sync
# ═══════════════════════════════════════════

def _run_async(coro):
    """Run an async coroutine from sync code."""
    try:
        loop = asyncio.get_running_loop()
    except RuntimeError:
        loop = None
    
    if loop and loop.is_running():
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor() as pool:
            return pool.submit(asyncio.run, coro).result()
    else:
        return asyncio.run(coro)


# ═══════════════════════════════════════════
# Markdown file creation
# ═══════════════════════════════════════════

def _ensure_citations_dir(query: str) -> Path:
    """Create and return the directory for storing citation MD files."""
    safe_query = re.sub(r"[^\w\s-]", "", query)[:50].strip().replace(" ", "_").lower()
    timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    dir_name = f"citations_{safe_query}_{timestamp}"
    citations_dir = Config.DATA_DIR / "citations" / dir_name
    citations_dir.mkdir(parents=True, exist_ok=True)
    return citations_dir


def _save_source_md(
    citations_dir: Path,
    source_name: str,
    source_url: str,
    content: str,
    page_url: str,
    page_title: str = "",
) -> Path:
    """Save a per-source markdown file."""
    safe_name = re.sub(r"[^\w\s-]", "", source_name)[:40].strip().replace(" ", "_").lower()
    page_hint = ""
    if page_title:
        page_hint = re.sub(r"[^\w\s-]", "", page_title)[:30].strip().replace(" ", "_").lower()
    if not page_hint:
        page_hint = re.sub(r"[^\w\s-]", "", page_url.split("/")[-1])[:30].strip().replace(" ", "_").lower()
    page_hash = hashlib.md5(page_url.encode("utf-8")).hexdigest()[:8]
    suffix = f"{page_hint}_{page_hash}" if page_hint else page_hash
    filepath = citations_dir / f"{safe_name}_{suffix}.md"
    
    md_content = f"""# {source_name}

**Source URL:** [{source_url}]({source_url})
**Scraped Page:** [{page_url}]({page_url})
{f'**Title:** {page_title}' if page_title else ''}
**Scraped At:** {datetime.utcnow().isoformat()}Z

---

{content}
"""
    
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(md_content)
        return filepath
    except Exception as e:
        logger.error(f"[CitationScraper] Failed to save MD for {source_name}: {e}")
        return filepath


def _save_combined_md(
    citations_dir: Path,
    query: str,
    scraped_data: List[Dict[str, Any]],
) -> Path:
    """Create a combined summary markdown file from all scraped sources."""
    filepath = citations_dir / "COMBINED_SUMMARY.md"
    
    header = f"""# Combined Citation Summary

**Query:** {query}
**Sources Scraped:** {len(scraped_data)}
**Generated At:** {datetime.utcnow().isoformat()}Z

---

"""
    
    sections = []
    for idx, item in enumerate(scraped_data, 1):
        source_name = item.get("source_name", "Unknown")
        page_url = item.get("page_url", "")
        page_title = item.get("page_title", "")
        content = item.get("content", "")
        
        # Take the first 1500 chars as a summary excerpt
        excerpt = content[:1500].strip()
        if len(content) > 1500:
            excerpt += "\n\n... (see full source file for more)"
        
        section = f"""## {idx}. {source_name}

**URL:** [{page_url}]({page_url})
{f'**Title:** {page_title}' if page_title else ''}

{excerpt}

---

"""
        sections.append(section)
    
    md_content = header + "\n".join(sections)
    
    # Add links section at the end
    md_content += "\n## Source Links\n\n"
    for idx, item in enumerate(scraped_data, 1):
        page_url = item.get("page_url", "")
        source_name = item.get("source_name", "Unknown")
        md_content += f"{idx}. [{source_name}]({page_url})\n"
    
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(md_content)
        return filepath
    except Exception as e:
        logger.error(f"[CitationScraper] Failed to save combined MD: {e}")
        return filepath


# ═══════════════════════════════════════════
# Content relevance filtering
# ═══════════════════════════════════════════

def _is_content_relevant(content: str, query_terms: List[str]) -> bool:
    """Check if scraped content is relevant to the query."""
    if not content or len(content) < 200:
        return False
    
    lowered = content.lower()
    
    # Check for noisy/boilerplate content
    noisy_markers = [
        "privacy policy", "cookie", "consent", "manage preferences",
        "terms of use", "sign in", "subscribe now", "accept all",
    ]
    noise_hits = sum(1 for m in noisy_markers if m in lowered)
    if noise_hits >= 3:
        return False
    
    # At least some query terms should appear in the content
    if query_terms:
        overlap = sum(1 for term in query_terms if term in lowered)
        generic_terms = {
            "tech", "technology", "update", "updates", "weekly", "latest",
            "recent", "news", "trend", "trends", "story", "stories",
        }
        focused_terms = [term for term in query_terms if term not in generic_terms]
        focused_overlap = sum(1 for term in focused_terms if term in lowered)

        # For specific queries, require stronger overlap to reduce off-topic pages.
        min_overlap = 1 if len(query_terms) <= 3 else 2
        if focused_terms and focused_overlap == 0:
            return False
        return overlap >= min_overlap
    
    return True


def _search_general_ddg(
    query: str,
    max_results: int = 15,
) -> List[Dict[str, str]]:
    """
    General DuckDuckGo search for the query (not limited to a single site).
    Returns list of {"url": ..., "title": ..., "snippet": ...}
    """
    if not DDGS_AVAILABLE:
        return []

    try:
        results = []
        for attempt_fn in [
            lambda: DDGS().text(query, max_results=max_results),
            lambda: DDGS().text(keywords=query, max_results=max_results),
        ]:
            try:
                results = attempt_fn()
                if results:
                    break
            except (TypeError, Exception):
                continue

        hits = []
        for r in results:
            href = r.get("href", "")
            if href and href.startswith("http"):
                hits.append({
                    "url": href,
                    "title": r.get("title", ""),
                    "snippet": r.get("body", ""),
                })
        return hits[:max_results]

    except Exception as e:
        logger.debug(f"[CitationScraper] DDG general search failed: {e}")
        return []


def _enforce_source_diversity(
    urls_to_crawl: List[Tuple[str, Dict[str, Any], str]],
    max_sources: int,
    max_pages_per_source: int,
) -> List[Tuple[str, Dict[str, Any], str]]:
    """Prioritize broad source coverage before taking extra pages per source."""
    by_source: Dict[str, List[Tuple[str, Dict[str, Any], str]]] = {}
    for entry in urls_to_crawl:
        _url, source, _title = entry
        source_key = source.get("url", "") or source.get("name", "unknown")
        bucket = by_source.setdefault(source_key, [])
        if len(bucket) < max_pages_per_source:
            bucket.append(entry)

    source_keys = list(by_source.keys())[:max_sources]

    selected: List[Tuple[str, Dict[str, Any], str]] = []
    # First pass: one page per source for breadth.
    for key in source_keys:
        pages = by_source.get(key, [])
        if pages:
            selected.append(pages[0])

    # Second pass: add extra pages while preserving ordering by source and depth.
    for depth in range(1, max_pages_per_source):
        for key in source_keys:
            pages = by_source.get(key, [])
            if depth < len(pages):
                selected.append(pages[depth])

    return selected


def scrape_citations(
    query: str,
    max_sources: int = 12,
    max_pages_per_source: int = 2,
) -> Dict[str, Any]:
    """
    Scrape relevant data from trusted citation sources for the given query.

    Improved 3-phase search strategy:
      Phase A: General DDG search — find articles matching query, filter to trusted domains
      Phase B: Site-specific DDG search on top-relevant sources
      Phase C: Fallback to main URLs for remaining sources
    Then: crawl, filter, save MD files, return structured data.
    """
    logger.info(f"[CitationScraper] Starting citation scrape for: {query}")

    citations_data = _load_trusted_citations()
    if not citations_data:
        logger.warning("[CitationScraper] No citation data available")
        return {"scraped_items": [], "citations_dir": "", "sources_used": 0, "source_links": []}

    all_sources = _get_all_sources(citations_data)
    query_terms = _extract_query_terms(query)
    logger.info(f"[CitationScraper] Query terms: {query_terms}")
    logger.info(f"[CitationScraper] Total citation sources available: {len(all_sources)}")

    # Build a domain -> source mapping for quick lookups
    domain_to_source: Dict[str, Dict[str, Any]] = {}
    for source in all_sources:
        domain = re.search(r"https?://([^/]+)", source["url"])
        if domain:
            d = domain.group(1).replace("www.", "").lower()
            domain_to_source[d] = source

    # Select tag-relevant sources for site-specific search
    relevant_sources = _select_relevant_sources(all_sources, query_terms, max_sources=max_sources)
    relevant_sources = _apply_intent_source_filter(relevant_sources, query_terms)
    relevant_source_urls = {s.get("url", "") for s in relevant_sources}
    logger.info(f"[CitationScraper] Selected {len(relevant_sources)} tag-relevant sources")

    # Create output directory
    citations_dir = _ensure_citations_dir(query)

    # Track URLs to crawl: (page_url, source_dict, page_title)
    urls_to_crawl: List[Tuple[str, Dict[str, Any], str]] = []
    seen_urls: set = set()

    # ── Phase A: General DDG search → find articles on ANY trusted domain ──
    logger.info("[CitationScraper] Phase A: General DDG search for multi-source discovery")
    general_hits = _search_general_ddg(query, max_results=20)

    for hit in general_hits:
        url = hit["url"]
        domain_match = re.search(r"https?://([^/]+)", url)
        if not domain_match:
            continue
        hit_domain = domain_match.group(1).replace("www.", "").lower()

        # Check if this URL belongs to one of our trusted sources
        matched_source = domain_to_source.get(hit_domain)
        if not matched_source:
            # Try partial domain matching (e.g. blog.google -> google)
            for d, src in domain_to_source.items():
                if hit_domain.endswith(d) or d.endswith(hit_domain) or hit_domain in d:
                    matched_source = src
                    break

        if (
            matched_source
            and matched_source.get("url", "") in relevant_source_urls
            and url not in seen_urls
        ):
            urls_to_crawl.append((url, matched_source, hit.get("title", "")))
            seen_urls.add(url)

    logger.info(f"[CitationScraper] Phase A found {len(urls_to_crawl)} URLs on trusted domains")

    # ── Phase B: Site-specific DDG search on tag-relevant sources ──
    logger.info("[CitationScraper] Phase B: Site-specific DDG search on relevant sources")
    site_search_count = 0

    for source in relevant_sources:
        if len(urls_to_crawl) >= max_sources * max_pages_per_source:
            break

        ddg_results = _search_source_duckduckgo(query, source["url"], max_results=max_pages_per_source)

        for hit in ddg_results:
            url = hit["url"]
            if url not in seen_urls:
                urls_to_crawl.append((url, source, hit.get("title", "")))
                seen_urls.add(url)
                site_search_count += 1

    logger.info(f"[CitationScraper] Phase B found {site_search_count} additional URLs")

    # ── Phase C: Fallback — scrape main page of remaining relevant sources ──
    if len(urls_to_crawl) < 3:
        logger.info("[CitationScraper] Phase C: Falling back to main URLs")
        for source in relevant_sources[:5]:
            source_url = source["url"]
            if source_url not in seen_urls:
                urls_to_crawl.append((source_url, source, source["name"]))
                seen_urls.add(source_url)

    urls_to_crawl = _enforce_source_diversity(
        urls_to_crawl,
        max_sources=max_sources,
        max_pages_per_source=max_pages_per_source,
    )

    logger.info(f"[CitationScraper] Total URLs to scrape: {len(urls_to_crawl)}")

    if not urls_to_crawl:
        return {"scraped_items": [], "citations_dir": str(citations_dir), "sources_used": 0, "source_links": []}

    # ── Scrape all URLs ──
    scraped_data: List[Dict[str, Any]] = []

    if CRAWL4AI_AVAILABLE:
        all_urls = [u[0] for u in urls_to_crawl]
        crawled = _run_async(_crawl_urls(all_urls, query_terms))

        crawled_by_requested = {
            item.get("requested_url", ""): item
            for item in crawled
            if item.get("requested_url")
        }
        crawled_by_final = {
            item.get("url", ""): item
            for item in crawled
            if item.get("url")
        }

        for page_url, source, page_title in urls_to_crawl:
            crawl_result = crawled_by_requested.get(page_url) or crawled_by_final.get(page_url)
            if crawl_result and crawl_result.get("success"):
                content = crawl_result["content"]
                if _is_content_relevant(content, query_terms):
                    resolved_url = crawl_result.get("url") or page_url
                    scraped_data.append({
                        "source_name": source["name"],
                        "source_url": source["url"],
                        "page_url": resolved_url,
                        "page_title": page_title,
                        "content": content,
                        "category": source.get("category", ""),
                        "tags": source.get("tags", []),
                    })
    else:
        for page_url, source, page_title in urls_to_crawl:
            content = _fetch_basic_http(page_url)
            if content and _is_content_relevant(content, query_terms):
                scraped_data.append({
                    "source_name": source["name"],
                    "source_url": source["url"],
                    "page_url": page_url,
                    "page_title": page_title,
                    "content": content,
                    "category": source.get("category", ""),
                    "tags": source.get("tags", []),
                })

    logger.info(f"[CitationScraper] Successfully scraped {len(scraped_data)} pages with relevant content")

    # Save per-source MD files
    for item in scraped_data:
        _save_source_md(
            citations_dir=citations_dir,
            source_name=item["source_name"],
            source_url=item["source_url"],
            content=item["content"],
            page_url=item["page_url"],
            page_title=item["page_title"],
        )

    # Save combined summary MD
    if scraped_data:
        _save_combined_md(citations_dir, query, scraped_data)

    # Convert to pipeline-compatible structured items
    scraped_items = []
    source_links = []

    for item in scraped_data:
        scraped_items.append({
            "source": item["source_name"],
            "url": item["page_url"],
            "title": item["page_title"] or item["source_name"],
            "content": item["content"],
            "content_type": "web_article",
            "published_at": "",
            "category": item["category"],
            "fetch_time": datetime.utcnow().isoformat(),
        })
        source_links.append({
            "name": item["source_name"],
            "url": item["source_url"],
            "page_url": item["page_url"],
            "page_title": item["page_title"],
            "category": item["category"],
        })

    result = {
        "scraped_items": scraped_items,
        "citations_dir": str(citations_dir),
        "sources_used": len({item.get("source_name", "") for item in scraped_data if item.get("source_name")}),
        "source_links": source_links,
    }

    logger.info(
        f"[CitationScraper] Done. {len(scraped_data)} sources yielded data. "
        f"MD files saved to {citations_dir}"
    )

    return result

