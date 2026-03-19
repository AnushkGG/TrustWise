import time
from typing import Any, Dict, List

from agents import research_agent, web_agent
from chunker.chunker import chunk_tasks
from cleaner import normalize_results
from insights import generate_insights
from orchestrator.orchestrator import generate_plan
from scheduler.scheduler import schedule
from storage import save_trusted_items
from trust import validate_structured_data
from utils.config import Config
from utils.logger import setup_logger

logger = setup_logger(__name__)


def execute_query_pipeline(query: str) -> Dict[str, Any]:
    """Run the full pipeline for one query (Phase 1-6)."""
    plan = generate_plan(query)
    tasks = chunk_tasks(plan)
    web_tasks, paper_tasks = schedule(tasks)

    results: List[Dict[str, Any]] = []

    for task in web_tasks:
        try:
            results.append(web_agent.run(task))
        except Exception as e:
            logger.error("[Continuous] Web task failed: %s", e)

    for task in paper_tasks:
        try:
            results.append(research_agent.run(task))
        except Exception as e:
            logger.error("[Continuous] Research task failed: %s", e)

    structured = normalize_results(results, query=query)
    trust_report = validate_structured_data(structured, query=query)
    trusted = trust_report["trusted_items"]

    db_stats = {"inserted": 0, "skipped": 0}
    if Config.SAVE_TO_DB:
        db_stats = save_trusted_items(trusted, query=query)

    insights = generate_insights(trusted, query=query)

    return {
        "query": query,
        "structured_items": len(structured),
        "trusted_items": len(trusted),
        "db_inserted": db_stats["inserted"],
        "db_skipped": db_stats["skipped"],
        "insights": insights,
    }


def run_continuous_updates(queries: List[str], interval_minutes: int = 60, max_cycles: int = 0) -> None:
    """Run periodic updates for a list of queries.

    Args:
        queries: Topics/queries to refresh.
        interval_minutes: Delay between cycles.
        max_cycles: 0 means infinite, otherwise stop after N cycles.
    """
    if not queries:
        logger.warning("[Continuous] No queries provided. Exiting.")
        return

    cycle = 0
    logger.info("[Continuous] Starting periodic updates for %s queries", len(queries))

    while True:
        cycle += 1
        logger.info("[Continuous] Cycle %s started", cycle)

        for query in queries:
            try:
                report = execute_query_pipeline(query)
                logger.info(
                    "[Continuous] Query '%s': trusted=%s inserted=%s skipped=%s",
                    query,
                    report["trusted_items"],
                    report["db_inserted"],
                    report["db_skipped"],
                )
            except Exception as e:
                logger.error("[Continuous] Query '%s' failed: %s", query, e)

        if max_cycles > 0 and cycle >= max_cycles:
            logger.info("[Continuous] Reached max cycles (%s). Stopping.", max_cycles)
            return

        sleep_seconds = max(1, interval_minutes) * 60
        logger.info("[Continuous] Sleeping for %s minutes", interval_minutes)
        time.sleep(sleep_seconds)
