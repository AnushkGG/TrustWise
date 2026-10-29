import json
import re
from datetime import datetime
from typing import Dict, Any

from agents.source_registry import collect_research_records
from utils.config import Config
from utils.logger import setup_logger

logger = setup_logger(__name__)

def run(task: Dict[str, Any]) -> Dict[str, Any]:
    """
    Execute a research paper collection task.

    The agent queries arXiv, OpenAlex, and Semantic Scholar, merges results,
    deduplicates by paper identity, and returns capped raw paper metadata.
    
    Args:
        task: Task dictionary containing task_id, prompt, source_type, agent
        
    Returns:
        Dictionary with task results including status and paper data
    """
    task_id = task.get("task_id", "unknown")
    # Chunker stores the task text under 'description'; fall back to it when 'prompt' is absent
    prompt = task.get("prompt") or task.get("description") or ""
    
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
        # Extract search terms from prompt with lightweight keyword filtering.
        search_query = _extract_search_query(prompt)
        logger.info(f"[ResearchAgent] Search query: {search_query}")
        
        papers, metrics = collect_research_records(search_query)

        if papers:
            result["data"] = papers
            result["source_metrics"] = metrics
            logger.info(
                f"[ResearchAgent] Found {len(papers)} papers "
                f"(raw={metrics.get('raw_count', 0)} unique={metrics.get('unique_count', 0)} "
                f"sources={len(metrics.get('enabled_sources', []))})"
            )
        else:
            result["status"] = "partial"
            result["message"] = "No papers found"
            result["source_metrics"] = metrics
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

    Handles two cases:
    1. Mock-plan prompts: "Search academic papers and preprints related to: <QUERY>"
       → extracts everything after the colon as the actual query.
    2. Free-form LLM-generated prompts: uses keyword filtering on the full text.
    """
    if not prompt:
        return ""

    # Case 1: Extract the subject after an explicit colon delimiter.
    # Handles patterns like "...related to: X", "...about: X", "...for: X"
    colon_match = re.search(r"(?:related to|about|for|regarding|on):\s*(.+)", prompt, re.IGNORECASE)
    if colon_match:
        subject = colon_match.group(1).strip()
        logger.info(f"[ResearchAgent] Extracted subject from prompt: {subject}")
        return subject

    # Case 2: Keyword filtering on free-form prompts.
    instruction_stop = {
        'search', 'find', 'papers', 'on', 'about', 'for', 'the', 'a', 'an',
        'in', 'of', 'and', 'to', 'with', 'from', 'at', 'retrieve', 'research',
        'published', 'recent', 'past', 'year', 'focusing', 'peer',
        'journals', 'articles', 'extract', 'get', 'fetch', 'latest',
        'implications', 'perspective', 'review', 'web', 'sources', 'news',
        'documentation', 'related', 'academic', 'preprints', 'scholarly',
    }
    words = re.findall(r"[a-z0-9]+", prompt.lower())
    keywords = [w for w in words if w not in instruction_stop and len(w) > 2]
    # Increased from 3 → 6 to preserve multi-word topic context.
    query = ' '.join(keywords[:6])
    logger.info(f"[ResearchAgent] Filtered keywords: {query}")
    return query


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

