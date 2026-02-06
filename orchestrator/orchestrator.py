import json
from orchestrator.llm_client import call_llm
from orchestrator.schema import validate_plan

def generate_plan(user_query: str) -> dict:
    response = call_llm(user_query)

    try:
        plan = json.loads(response)
    except json.JSONDecodeError:
        raise ValueError("LLM did not return valid JSON")

    validate_plan(plan)
    return plan
