"""
TrustWise API Bridge

Thin JSON-over-stdin/stdout bridge so the TypeScript web server can invoke
the Python pipeline without embedding a Python runtime.

Usage (called by the TypeScript server, not by users directly):
    echo '{"action":"status"}' | python api_bridge.py
"""

import json
import logging
import sys
import os
from datetime import datetime
from pathlib import Path

# Redirect ALL logging to stderr so stdout is clean JSON for the caller.
logging.basicConfig(stream=sys.stderr, level=logging.WARNING)
for _handler in logging.root.handlers:
    _handler.stream = sys.stderr

# Ensure the repo root is on sys.path so relative imports work.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from dotenv import load_dotenv

load_dotenv()

# Patch the logger module so any future setup_logger() calls also go to stderr.
import utils.logger as _logger_mod
_orig_setup = _logger_mod.setup_logger

def _patched_setup_logger(name: str):
    logger = _orig_setup(name)
    for h in logger.handlers:
        if hasattr(h, 'stream'):
            h.stream = sys.stderr
    return logger

_logger_mod.setup_logger = _patched_setup_logger

from orchestrator.orchestrator import generate_plan
from chunker.chunker import chunk_tasks
from scheduler.scheduler import schedule
from agents import web_agent, research_agent
from agents.citation_scraper import scrape_citations
from cleaner import normalize_results
from trust import validate_structured_data
from storage import get_cached_trusted_items, save_trusted_items
from insights import generate_insights
from utils.config import Config
from utils.logger import setup_logger
from utils.retry import execute_with_retry

logger = setup_logger(__name__)


# ── Action handlers ──────────────────────────────────────

def handle_submit(payload: dict) -> dict:
    """Run the full pipeline for a query."""
    query = payload.get("query", "").strip()
    if not query:
        return {"success": False, "error": "Query cannot be empty"}

    logger.info(f"Bridge: Processing query: {query}")

    # Step 1: Generate Plan
    plan = generate_plan(query)

    # Step 1.5: Check cache
    if Config.ENABLE_DB_CACHE:
        cached_items = get_cached_trusted_items(
            query=query, min_items=Config.DB_CACHE_MIN_ITEMS, limit=8
        )
        if cached_items:
            # Even on cache hit, run citation scraper for multi-source data
            citation_result = {"scraped_items": [], "source_links": [], "sources_used": 0}
            try:
                citation_result = scrape_citations(
                    query=query,
                    max_sources=Config.CITATION_MAX_SOURCES,
                    max_pages_per_source=Config.CITATION_PAGES_PER_SOURCE,
                )
                logger.info(
                    f"Bridge: Citation scraper (cache-hit path) returned "
                    f"{citation_result.get('sources_used', 0)} sources"
                )
            except Exception as e:
                logger.error(f"Bridge: Citation scraper failed on cache path: {e}")

            # Merge citation items into cached items for richer insights
            all_items = list(cached_items)
            citation_items = citation_result.get("scraped_items", [])
            if citation_items:
                all_items.extend(citation_items)

            source_links = citation_result.get("source_links", [])
            insights = generate_insights(all_items, query=query, source_links=source_links)
            return {
                "success": True,
                "plan": {
                    "goal": plan.get("goal"),
                    "domains": plan.get("domains"),
                    "time_range": plan.get("time_range"),
                    "sources": plan.get("sources"),
                    "total_tasks": len(plan.get("tasks", [])),
                },
                "execution": {
                    "web_tasks": 0,
                    "paper_tasks": 0,
                    "total_results": 0,
                    "successful": 0,
                    "structured_items": len(all_items),
                    "trusted_items": len(all_items),
                    "citation_sources": citation_result.get("sources_used", 0),
                    "db_inserted": 0,
                    "db_skipped": 0,
                    "cache_hit": True,
                },
                "results": [],
                "structured_data": all_items,
                "trusted_data": all_items,
                "insights": insights,
                "trust_report": {
                    "validated_count": len(all_items),
                    "trusted_count": len(all_items),
                    "dropped_count": 0,
                },
            }

    # Step 2-4: Chunk, Schedule, Execute
    tasks = chunk_tasks(plan)
    web_tasks, paper_tasks = schedule(tasks)

    results = []
    for task in web_tasks:
        try:
            result = execute_with_retry(
                web_agent.run,
                task,
                max_retries=2,
                base_delay=1.0,
                retryable_exceptions=(ConnectionError, TimeoutError, OSError),
            )
            results.append(result)
        except Exception as e:
            logger.error(f"Web task {task.get('task_id')} failed: {e}")
            results.append(
                {"task_id": task.get("task_id"), "status": "failed", "error": str(e)}
            )

    for task in paper_tasks:
        try:
            result = execute_with_retry(
                research_agent.run,
                task,
                max_retries=2,
                base_delay=1.0,
                retryable_exceptions=(ConnectionError, TimeoutError, OSError),
            )
            results.append(result)
        except Exception as e:
            logger.error(f"Research task {task.get('task_id')} failed: {e}")
            results.append(
                {"task_id": task.get("task_id"), "status": "failed", "error": str(e)}
            )

    # Step 4.5: Scrape trusted citation sources for multi-source data
    citation_result = {"scraped_items": [], "source_links": [], "sources_used": 0}
    try:
        citation_result = scrape_citations(
            query=query,
            max_sources=Config.CITATION_MAX_SOURCES,
            max_pages_per_source=Config.CITATION_PAGES_PER_SOURCE,
        )
        logger.info(
            f"Bridge: Citation scraper returned {citation_result.get('sources_used', 0)} sources"
        )
    except Exception as e:
        logger.error(f"Bridge: Citation scraper failed: {e}")

    # Step 5-8: Clean, Trust, Store, Insights
    structured_data = normalize_results(results, query=query)

    # Merge citation-scraped items into structured data
    citation_items = citation_result.get("scraped_items", [])
    if citation_items:
        structured_data.extend(citation_items)
        logger.info(f"Bridge: Merged {len(citation_items)} citation items into structured data")

    trust_report = validate_structured_data(structured_data, query=query)
    trusted_data = trust_report["trusted_items"]

    db_stats = {"inserted": 0, "skipped": 0}
    if Config.SAVE_TO_DB:
        db_stats = save_trusted_items(trusted_data, query=query)

    insight_input = trusted_data if trusted_data else structured_data
    source_links = citation_result.get("source_links", [])
    insights = generate_insights(insight_input, query=query, source_links=source_links)

    return {
        "success": True,
        "plan": {
            "goal": plan.get("goal"),
            "domains": plan.get("domains"),
            "time_range": plan.get("time_range"),
            "sources": plan.get("sources"),
            "total_tasks": len(plan.get("tasks", [])),
        },
        "execution": {
            "web_tasks": len(web_tasks),
            "paper_tasks": len(paper_tasks),
            "total_results": len(results),
            "successful": sum(1 for r in results if r.get("status") == "success"),
            "structured_items": len(structured_data),
            "trusted_items": len(trusted_data),
            "citation_sources": citation_result.get("sources_used", 0),
            "db_inserted": db_stats["inserted"],
            "db_skipped": db_stats["skipped"],
            "cache_hit": False,
        },
        "results": results,
        "structured_data": structured_data,
        "trusted_data": trusted_data,
        "insights": insights,
        "trust_report": {
            "validated_count": trust_report["validated_count"],
            "trusted_count": trust_report["trusted_count"],
            "dropped_count": trust_report["dropped_count"],
        },
    }


def handle_status(_payload: dict) -> dict:
    """Return system status."""
    ollama_reachable = False
    gemini_configured = bool(Config.GEMINI_API_KEY)

    try:
        import requests
        resp = requests.get(f"{Config.OLLAMA_BASE_URL}/api/tags", timeout=2)
        ollama_reachable = resp.status_code == 200
    except Exception:
        ollama_reachable = False

    if Config.LLM_PROVIDER == "both":
        has_api_key = gemini_configured or ollama_reachable
    elif Config.LLM_PROVIDER == "gemini":
        has_api_key = gemini_configured
    elif Config.LLM_PROVIDER == "ollama":
        has_api_key = ollama_reachable
    else:
        has_api_key = False

    providers_available = []
    if gemini_configured:
        providers_available.append("gemini")
    if ollama_reachable:
        providers_available.append("ollama")

    return {
        "success": True,
        "status": {
            "llm_provider": Config.LLM_PROVIDER,
            "llm_model": Config.LLM_MODEL,
            "has_api_key": has_api_key,
            "ollama_reachable": ollama_reachable,
            "gemini_configured": gemini_configured,
            "providers_available": providers_available,
            "save_plans": Config.SAVE_PLANS,
            "save_raw_data": Config.SAVE_RAW_DATA,
            "save_structured_data": Config.SAVE_STRUCTURED_DATA,
            "save_trusted_data": Config.SAVE_TRUSTED_DATA,
            "save_to_db": Config.SAVE_TO_DB,
            "enable_db_cache": Config.ENABLE_DB_CACHE,
            "is_running": False,
        },
    }


def handle_list_plans(_payload: dict) -> dict:
    """List saved plans."""
    plans_dir = Config.PLANS_DIR
    plan_files = sorted(plans_dir.glob("plan_*.json"), reverse=True)

    plans = []
    for plan_file in list(plan_files)[:20]:
        try:
            with open(plan_file, "r", encoding="utf-8") as f:
                plan_data = json.load(f)
                plans.append(
                    {
                        "filename": plan_file.name,
                        "goal": plan_data.get("goal", "N/A"),
                        "created_at": plan_data.get("_metadata", {}).get(
                            "created_at", "Unknown"
                        ),
                        "query": plan_data.get("_metadata", {}).get("query", "N/A"),
                        "tasks": len(plan_data.get("tasks", [])),
                    }
                )
        except Exception as e:
            logger.warning(f"Failed to read plan {plan_file}: {e}")
            continue

    return {"success": True, "plans": plans}


def handle_get_plan(payload: dict) -> dict:
    """Get a specific plan by filename."""
    filename = payload.get("filename", "")
    if ".." in filename or "/" in filename or "\\" in filename:
        return {"success": False, "error": "Invalid filename"}

    plan_file = (Config.PLANS_DIR / filename).resolve()
    plans_dir = Config.PLANS_DIR.resolve()

    try:
        plan_file.relative_to(plans_dir)
    except ValueError:
        return {"success": False, "error": "Invalid filename"}

    if not plan_file.exists():
        return {"success": False, "error": "Plan not found"}

    with open(plan_file, "r", encoding="utf-8") as f:
        plan_data = json.load(f)

    return {"success": True, "plan": plan_data}


def handle_list_raw_data(_payload: dict) -> dict:
    """List raw data files."""
    raw_dir = Config.RAW_DATA_DIR
    raw_files = sorted(raw_dir.glob("task_*.json"), reverse=True)

    files = []
    for raw_file in list(raw_files)[:50]:
        try:
            stat = raw_file.stat()
            files.append(
                {
                    "filename": raw_file.name,
                    "size": stat.st_size,
                    "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                }
            )
        except Exception as e:
            logger.warning(f"Failed to stat file {raw_file}: {e}")
            continue

    return {"success": True, "files": files}


# ── Main dispatcher ──────────────────────────────────────

ACTIONS = {
    "submit": handle_submit,
    "status": handle_status,
    "list_plans": handle_list_plans,
    "get_plan": handle_get_plan,
    "list_raw_data": handle_list_raw_data,
}


def main() -> None:
    raw = sys.stdin.read()
    try:
        request = json.loads(raw)
    except json.JSONDecodeError:
        json.dump({"success": False, "error": "Invalid JSON input"}, sys.stdout)
        return

    action = request.pop("action", "")
    handler = ACTIONS.get(action)

    if handler is None:
        json.dump({"success": False, "error": f"Unknown action: {action}"}, sys.stdout)
        return

    try:
        result = handler(request)
    except Exception as e:
        logger.error(f"Bridge action '{action}' failed: {e}", exc_info=True)
        result = {"success": False, "error": "An internal error occurred."}

    json.dump(result, sys.stdout)


if __name__ == "__main__":
    main()
