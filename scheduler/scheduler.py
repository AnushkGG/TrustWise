from typing import List, Dict, Any, Tuple
from utils.logger import setup_logger

logger = setup_logger(__name__)

def schedule(tasks: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Route tasks to appropriate agents based on source_type.
    
    Phase 1: Simple routing by source type
    - web -> web_agent
    - research_papers -> research_agent
    
    Args:
        tasks: List of task dictionaries from execution plan
        
    Returns:
        Tuple of (web_tasks, paper_tasks)
    """
    web_tasks = []
    paper_tasks = []
    
    for task in tasks:
        source_type = task.get("source_type", "").lower()
        
        # Normalize agent name to match our implementation
        if source_type == "web":
            task["agent"] = "web_agent"  # Ensure consistent naming
            web_tasks.append(task)
            logger.debug(f"Scheduled {task.get('task_id')} to web_agent")
        elif source_type in ["research_papers", "papers", "research"]:
            task["agent"] = "research_agent"  # Ensure consistent naming
            paper_tasks.append(task)
            logger.debug(f"Scheduled {task.get('task_id')} to research_agent")
        else:
            logger.warning(f"Unknown source_type '{source_type}' for task {task.get('task_id')}")
            # Default to web agent for unknown types
            task["agent"] = "web_agent"
            web_tasks.append(task)
    
    logger.info(f"Scheduled {len(web_tasks)} web tasks, {len(paper_tasks)} research tasks")
    return web_tasks, paper_tasks

