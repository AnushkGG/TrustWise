import uuid
import re
from typing import Dict, List, Any
from difflib import SequenceMatcher

from utils.config import Config
from utils.logger import setup_logger

logger = setup_logger(__name__)

# JSON schema representation for validation documentation
CHUNK_SCHEMA = {
    "type": "object",
    "required": [
        "chunk_id", "parent_query", "title", "description", "priority",
        "dependencies", "agent", "source_types", "trust_constraints",
        "expected_output", "retry_policy"
    ]
}

def chunk_tasks(plan: dict) -> List[Dict[str, Any]]:
    """
    Decompose plan tasks into structured, deduplicated execution Chunks
    with resolved dependency links and default trust/retry constraints.
    """
    logger.info("Starting task decomposition and chunking")
    
    parent_query = plan.get("_metadata", {}).get("query") or plan.get("goal") or "General research"
    raw_tasks = plan.get("tasks", [])
    
    chunks: List[Dict[str, Any]] = []
    seen_descriptions: List[str] = []
    
    # 1. First Pass: Deduplication and Normalization
    for idx, task in enumerate(raw_tasks):
        desc = (task.get("prompt") or task.get("description") or "").strip()
        if not desc:
            continue
            
        # Deduplication using SequenceMatcher
        is_duplicate = False
        for seen in seen_descriptions:
            if SequenceMatcher(None, desc.lower(), seen.lower()).ratio() > 0.80:
                logger.info(f"Deduplicated overlapping task prompt: '{desc[:50]}...'")
                is_duplicate = True
                break
        if is_duplicate:
            continue
            
        seen_descriptions.append(desc)
        
        # Determine agent and source types
        source_type = task.get("source_type", "").lower()
        if source_type in ("research_papers", "papers", "research"):
            agent = "research_agent"
            sources = ["arxiv", "openalex", "semantic_scholar", "crossref", "pubmed"]
            expected_out = "metadata_json"
            min_trust = 0.60
        else:
            agent = "web_agent"
            sources = ["web"]
            expected_out = "markdown"
            min_trust = 0.65
            
        # Parse task priority (default 3)
        priority = int(task.get("priority", 3))
        priority = max(1, min(5, priority))
        
        # Build chunk base
        chunk_id = task.get("task_id") or f"chunk_{source_type}_{idx + 1}"
        
        chunk = {
            "chunk_id": chunk_id,
            "parent_query": parent_query,
            "title": task.get("title") or f"Research Angle: {chunk_id}",
            "description": desc,
            "priority": priority,
            "dependencies": [],  # Filled in second pass
            "agent": agent,
            "source_types": sources,
            "trust_constraints": {
                "min_trust_score": min_trust,
                "require_whitelist": False
            },
            "expected_output": expected_out,
            "retry_policy": {
                "max_retries": int(Config.RESEARCH_PER_SOURCE_RETRIES) if hasattr(Config, "RESEARCH_PER_SOURCE_RETRIES") else 2,
                "backoff_factor": 1.5
            }
        }
        chunks.append(chunk)
        
    # 2. Second Pass: Dependency Mapping
    for chunk in chunks:
        desc_lower = chunk["description"].lower()
        
        # Check if description explicitly refers to another chunk id
        for other in chunks:
            if other["chunk_id"] == chunk["chunk_id"]:
                continue
            # Regex match for exact word match of task id
            if re.search(r'\b' + re.escape(other["chunk_id"]) + r'\b', desc_lower):
                chunk["dependencies"].append(other["chunk_id"])
                logger.info(f"Resolved explicit dependency: {chunk['chunk_id']} -> {other['chunk_id']}")
                
        # Semantic dependency heuristics: synthesis/comparison depends on retrieval
        is_synthesis = any(word in desc_lower for word in ["compare", "synthesize", "summarize", "overview", "consensus"])
        if is_synthesis:
            for other in chunks:
                if other["chunk_id"] != chunk["chunk_id"] and other["agent"] != "synthesis_agent":
                    if other["chunk_id"] not in chunk["dependencies"]:
                        chunk["dependencies"].append(other["chunk_id"])
            logger.info(f"Resolved comparative synthesis dependency: {chunk['chunk_id']} depends on collection chunks")

    logger.info(f"Chunker created {len(chunks)} execution chunks")
    return chunks
