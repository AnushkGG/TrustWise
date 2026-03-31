
"""Validation helpers for TrustWise execution plans."""

def validate_plan(plan: dict):
    """Validate the minimum required structure for a generated plan."""
    required_keys = ["goal", "domains", "time_range", "sources", "tasks"]
    for key in required_keys:
        if key not in plan:
            raise ValueError(f"Plan missing required key: {key}")
    
    if not isinstance(plan["tasks"], list):
        raise ValueError("Tasks must be a list")
    
    task_keys = ["task_id", "source_type", "agent", "prompt"]
    for task in plan["tasks"]:
        for key in task_keys:
            if key not in task:
                raise ValueError(f"Task missing required key: {key}")
