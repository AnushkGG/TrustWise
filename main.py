import json
from dotenv import load_dotenv
from orchestrator.orchestrator import generate_plan
from chunker.chunker import chunk_tasks
from scheduler.scheduler import schedule
from agents import web_agent, research_agent
from utils.config import Config
from utils.logger import setup_logger

# Load environment variables from .env file
load_dotenv()

logger = setup_logger(__name__)

def main():
    """
    TrustWise Phase 1 - Main Entry Point
    
    Flow:
    1. Accept user query
    2. Generate structured execution plan (LLM-based orchestration)
    3. Chunk tasks
    4. Schedule tasks to appropriate agents
    5. Execute tasks via agents
    6. Collect raw data (no validation or summarization in Phase 1)
    """
    
    print("=" * 60)
    print("TrustWise - Trust-First AI System (Phase 1)")
    print("=" * 60)
    print()
    
    # Validate configuration
    try:
        Config.validate()
    except ValueError as e:
        logger.warning(f"Configuration validation: {e}")
        print(f"⚠️  {e}")
        print("   Using mock LLM responses for demonstration.")
        print()
    
    # Get user query
    query = input("Enter your query: ").strip()
    
    if not query:
        print("Error: Query cannot be empty")
        return

    print()
    logger.info(f"Processing query: {query}")

    try:
        # Step 1: Generate Plan
        print("🔄 Generating execution plan...")
        plan = generate_plan(query)
        
        print("\n" + "=" * 60)
        print("📋 GENERATED PLAN")
        print("=" * 60)
        print(f"Goal: {plan.get('goal', 'N/A')}")
        print(f"Domains: {', '.join(plan.get('domains', []))}")
        print(f"Time Range: {plan.get('time_range', 'N/A')}")
        print(f"Sources: {', '.join(plan.get('sources', []))}")
        print(f"Tasks: {len(plan.get('tasks', []))}")
        print("=" * 60)
        print()
        
        # Step 2: Chunk Tasks
        logger.info("Chunking tasks...")
        tasks = chunk_tasks(plan)
        
        # Step 3: Schedule Tasks
        logger.info("Scheduling tasks to agents...")
        web_tasks, paper_tasks = schedule(tasks)

        print(f"📊 Scheduled {len(web_tasks)} web tasks and {len(paper_tasks)} research tasks")
        print()

        # Step 4: Execute Tasks
        results = []
        
        if web_tasks:
            print("🌐 Executing Web Tasks...")
            for task in web_tasks:
                try:
                    result = web_agent.run(task)
                    results.append(result)
                    print(f"   ✓ {task['task_id']}: {result['status']}")
                except Exception as e:
                    logger.error(f"Web task {task.get('task_id')} failed: {e}")
                    print(f"   ✗ {task['task_id']}: failed - {e}")
            print()

        if paper_tasks:
            print("📚 Executing Research Tasks...")
            for task in paper_tasks:
                try:
                    result = research_agent.run(task)
                    results.append(result)
                    print(f"   ✓ {task['task_id']}: {result['status']}")
                except Exception as e:
                    logger.error(f"Research task {task.get('task_id')} failed: {e}")
                    print(f"   ✗ {task['task_id']}: failed - {e}")
            print()
        
        # Summary
        print("=" * 60)
        print("✅ EXECUTION COMPLETE")
        print("=" * 60)
        
        successful = sum(1 for r in results if r.get('status') == 'success')
        print(f"Tasks completed: {successful}/{len(results)}")
        
        if Config.SAVE_RAW_DATA:
            print(f"Raw data saved to: {Config.RAW_DATA_DIR}")
        
        if Config.SAVE_PLANS:
            print(f"Plan saved to: {Config.PLANS_DIR}")
        
        print()
        logger.info("Execution completed successfully")

    except Exception as e:
        logger.error(f"Execution failed: {e}", exc_info=True)
        print(f"\n❌ Error: {e}")
        print()

if __name__ == "__main__":
    main()

