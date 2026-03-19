import json
import urllib.parse
import urllib.request
from datetime import datetime
from typing import Dict, Any, List
import logging

try:
    from utils.config import Config
except ImportError:
    import sys, os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from utils.config import Config

try:
    import feedparser
except ImportError:
    feedparser = None

logger = logging.getLogger(__name__)

def run(task: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute a research paper collection task.
    
    Phase 1 Implementation:
    - Searches arXiv for research papers based on prompt
    - Collects metadata and abstracts
    - No validation, summarization, or LLM processing
    - Simply fetches and stores raw data
    
    Args:
        task: Task dictionary containing task_id, prompt, source_type, agent
        
    Returns:
        Dictionary with task results including status and paper data
    """
    task_id = task.get("task_id", "unknown")
    prompt = task.get("prompt", "")
    
    logger.info(f"[ResearchAgent] Processing task: {task_id}")
    logger.info(f"[ResearchAgent] Prompt: {prompt}")
    
    result = {
        "task_id": task_id,
        "agent": "research_agent",
        "status": "success",
        "timestamp": datetime.utcnow().isoformat(),
        "prompt": prompt,
        "data": []
    }
    
    try:
        # Extract search terms from prompt
        # In Phase 1: Simple keyword extraction from prompt
        search_query = _extract_search_query(prompt)
        logger.info(f"[ResearchAgent] Search query: {search_query}")
        
        # Search arXiv
        papers = _search_arxiv(search_query)
        
        if papers:
            result["data"] = papers
            logger.info(f"[ResearchAgent] Found {len(papers)} papers")
        else:
            result["status"] = "partial"
            result["message"] = "No papers found"
            logger.warning(f"[ResearchAgent] Task {task_id} found no papers")
        
        # Save raw data if configured
        if Config.SAVE_RAW_DATA:
            _save_raw_data(task_id, result)
        
    except Exception as e:
        logger.error(f"[ResearchAgent] Task {task_id} failed: {e}")
        result["status"] = "failed"
        result["error"] = str(e)
    
    return result


def _extract_search_query(prompt: str) -> str:
    """
    Extract search keywords from task prompt.
    
    Phase 1: Simple extraction without LLM.
    Removes common words and takes key terms.
    
    Args:
        prompt: Task prompt
        
    Returns:
        Search query string
    """
    # Remove common instruction words
    stop_words = {'search', 'find', 'papers', 'on', 'about', 'for', 'the', 'a', 'an', 
                  'in', 'of', 'and', 'to', 'with', 'from', 'at', 'retrieve', 'research',
                  'published', 'recent', 'past', 'year', 'focusing', 'peer-reviewed',
                  'journals', 'articles', 'extract', 'get', 'fetch'}
    
    words = prompt.lower().split()
    keywords = [w for w in words if w not in stop_words and len(w) > 2]
    
    # Return joined keywords (arXiv expects space-separated terms)
    query = ' '.join(keywords[:5])  # Limit to 5 keywords
    logger.info(f"[ResearchAgent] Filtered keywords: {query}")
    return query


def _search_arxiv(query: str) -> List[Dict[str, Any]]:
    """
    Search arXiv API for research papers.
    
    Args:
        query: Search query string
        
    Returns:
        List of paper metadata dictionaries
    """
    if feedparser is None:
        logger.error("feedparser package not installed. Run: pip install feedparser")
        raise ImportError("feedparser required. Install with: pip install feedparser")

    # Construct arXiv API query
    base_url = 'http://export.arxiv.org/api/query?'
    search_query_param = f'search_query=all:{urllib.parse.quote(query)}'
    max_results = f'max_results={Config.ARXIV_MAX_RESULTS}'
    sort_by = 'sortBy=submittedDate&sortOrder=descending'

    query_url = f"{base_url}{search_query_param}&{max_results}&{sort_by}"

    logger.info(f"[ResearchAgent] Querying arXiv: {query_url}")

    # Fetch with timeout to avoid indefinite hang
    try:
        req = urllib.request.urlopen(query_url, timeout=15)
        raw_feed = req.read()
    except Exception as fetch_err:
        logger.error(f"[ResearchAgent] arXiv HTTP fetch failed: {fetch_err}")
        raise

    # Parse feed from fetched bytes
    feed = feedparser.parse(raw_feed)

    # Check for feed-level error (bozo = feedparser's malformed-feed flag)
    if feed.get('bozo') and not feed.entries:
        bozo_exc = feed.get('bozo_exception', 'Unknown feed error')
        logger.error(f"[ResearchAgent] arXiv feed parse error: {bozo_exc}")
        raise ValueError(f"arXiv feed error: {bozo_exc}")

    papers = []
    for entry in feed.entries:
        try:
            # Guard authors: some entries have no authors field
            authors = []
            if hasattr(entry, 'authors') and entry.authors:
                authors = [getattr(a, 'name', str(a)) for a in entry.authors]

            paper = {
                "title": getattr(entry, 'title', 'Untitled'),
                "authors": authors,
                "abstract": getattr(entry, 'summary', ''),
                "published": getattr(entry, 'published', ''),
                "arxiv_id": getattr(entry, 'id', '').split('/abs/')[-1],
                "pdf_url": getattr(entry, 'id', '').replace('/abs/', '/pdf/') + '.pdf',
                "categories": [tag.term for tag in entry.tags] if hasattr(entry, 'tags') else []
            }
            papers.append(paper)
        except Exception as entry_err:
            logger.warning(f"[ResearchAgent] Skipping malformed entry: {entry_err}")
            continue

    return papers


def _save_raw_data(task_id: str, result: Dict[str, Any]):
    """Save raw agent output to file."""
    filename = f"{task_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
    filepath = Config.RAW_DATA_DIR / filename
    
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(result, f, indent=2, ensure_ascii=False)
        logger.info(f"[ResearchAgent] Saved raw data to {filepath}")
    except Exception as e:
        logger.error(f"[ResearchAgent] Failed to save raw data: {e}")

