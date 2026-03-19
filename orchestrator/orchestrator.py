import json
from datetime import datetime
from orchestrator.llm_client import call_llm
from orchestrator.schema import validate_plan
from utils.config import Config
import logging

logger = logging.getLogger(__name__)

def generate_plan(user_query: str) -> dict:
    """
    Generate a structured execution plan from user query.
    
    Args:
        user_query: Natural language query from user
        
    Returns:
        Validated execution plan dictionary
        
    Raises:
        ValueError: If LLM returns invalid JSON or plan fails validation
    """
    logger.info(f"Generating plan for query: {user_query}")
    
    response = call_llm(user_query)

    try:
        plan = json.loads(response)
    except json.JSONDecodeError as e:
        logger.error(f"LLM did not return valid JSON: {e}")
        raise ValueError(f"LLM did not return valid JSON: {e}")

    # Validate plan structure
    validate_plan(plan)
    
    # Add metadata
    plan["_metadata"] = {
        "query": user_query,
        "created_at": datetime.utcnow().isoformat(),
        "llm_provider": Config.LLM_PROVIDER,
        "llm_model": Config.LLM_MODEL
    }
    
    # Save plan if configured
    if Config.SAVE_PLANS:
        _save_plan(plan)
    
    logger.info(f"Plan generated successfully with {len(plan['tasks'])} tasks")
    return plan


def _save_plan(plan: dict):
    """Save execution plan to file for auditability."""
    timestamp = datetime.utcnow().strftime('%Y%m%d_%H%M%S')
    filename = f"plan_{timestamp}.json"
    filepath = Config.PLANS_DIR / filename
    
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(plan, f, indent=2, ensure_ascii=False)
        logger.info(f"Plan saved to {filepath}")
    except Exception as e:
        logger.error(f"Failed to save plan: {e}")

