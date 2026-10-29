from typing import List, Dict, Any, Tuple, Set
import concurrent.futures
from utils.logger import setup_logger
from utils.retry import execute_with_retry
from agents import web_agent, research_agent

logger = setup_logger(__name__)

def schedule(tasks: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], List[Dict[str, Any]]]:
    """
    Route tasks to appropriate agents based on agent/source_type.
    Kept for backward compatibility with existing tests.
    """
    web_tasks = []
    paper_tasks = []
    
    for task in tasks:
        # Check either 'agent' or 'source_type' to support both Chunks and old tasks
        agent = task.get("agent")
        source_type = task.get("source_type", "").lower()
        
        if agent == "web_agent" or source_type == "web":
            task["agent"] = "web_agent"
            web_tasks.append(task)
        elif agent == "research_agent" or source_type in ["research_papers", "papers", "research"]:
            task["agent"] = "research_agent"
            paper_tasks.append(task)
        else:
            task["agent"] = "web_agent"
            web_tasks.append(task)
            
    return web_tasks, paper_tasks


def execute_chunks(chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Execute chunks concurrently according to their dependency graph.
    Returns a flat list of result dictionaries from all chunks.
    """
    logger.info(f"Scheduling {len(chunks)} chunks for parallel DAG execution")
    
    chunk_map = {c["chunk_id"]: c for c in chunks}
    completed_chunks: Set[str] = set()
    failed_chunks: Set[str] = set()
    results: List[Dict[str, Any]] = []
    
    # Process chunks in stages until all are completed or blocked
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        while len(completed_chunks) + len(failed_chunks) < len(chunks):
            # Identify chunks ready to execute in the current stage
            ready_chunks = []
            for cid, chunk in chunk_map.items():
                if cid in completed_chunks or cid in failed_chunks:
                    continue
                
                # Check if all dependencies are satisfied
                deps = chunk.get("dependencies", [])
                if all(dep in completed_chunks for dep in deps):
                    ready_chunks.append(chunk)
            
            if not ready_chunks:
                # Cycle detected or blocked dependencies
                remaining = [cid for cid in chunk_map if cid not in completed_chunks and cid not in failed_chunks]
                logger.error(f"Execution stalled. Circular dependency or blocked path detected for chunks: {remaining}")
                for cid in remaining:
                    failed_chunks.add(cid)
                    results.append({
                        "task_id": cid,
                        "status": "failed",
                        "error": "Dependency blocked or circular reference detected"
                    })
                break
                
            logger.info(f"Executing topological layer: {[c['chunk_id'] for c in ready_chunks]}")
            
            # Map futures to chunk IDs
            futures = {}
            for chunk in ready_chunks:
                cid = chunk["chunk_id"]
                agent_name = chunk["agent"]
                
                # Target execution agent runner
                if agent_name == "research_agent":
                    run_func = research_agent.run
                else:
                    run_func = web_agent.run
                    
                policy = chunk.get("retry_policy", {"max_retries": 2, "backoff_factor": 1.5})
                max_retries = policy.get("max_retries", 2)
                
                # Schedule in Executor
                future = executor.submit(
                    execute_with_retry,
                    run_func, chunk,
                    max_retries=max_retries,
                    base_delay=1.0,
                    retryable_exceptions=(ConnectionError, TimeoutError, OSError)
                )
                futures[future] = cid
                
            # Wait for all futures in this layer to complete
            for future in concurrent.futures.as_completed(futures):
                cid = futures[future]
                try:
                    result = future.result()
                    # Ensure status key is present
                    if not isinstance(result, dict):
                        result = {"status": "success", "data": result}
                    result["task_id"] = cid
                    results.append(result)
                    completed_chunks.add(cid)
                    logger.info(f"Chunk {cid} completed successfully")
                except Exception as e:
                    logger.error(f"Chunk {cid} failed: {e}")
                    failed_chunks.add(cid)
                    results.append({
                        "task_id": cid,
                        "status": "failed",
                        "error": str(e)
                    })
                    
    logger.info(f"DAG execution completed. Success: {len(completed_chunks)}, Failed: {len(failed_chunks)}")
    return results
