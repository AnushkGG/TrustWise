import json
from dotenv import load_dotenv
from orchestrator.orchestrator import generate_plan
from chunker.chunker import chunk_tasks
from scheduler.scheduler import schedule
from agents import web_agent, research_agent
from cleaner import normalize_results
from trust import validate_structured_data
from storage import get_cached_trusted_items, save_trusted_items
from insights import generate_insights
from utils.config import Config
from utils.logger import setup_logger
from utils.retry import execute_with_retry

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

        # Step 1.5: Reuse local trusted data when sufficient (Phase 6)
        if Config.ENABLE_DB_CACHE:
            cached_items = get_cached_trusted_items(
                query=query,
                min_items=Config.DB_CACHE_MIN_ITEMS,
                limit=8,
            )
            if cached_items:
                print("⚡ Cache hit: using trusted local DB data")
                print(f"   ✓ Records reused: {len(cached_items)}")
                insights = generate_insights(cached_items, query=query)
                print(f"   ✓ Summary: {insights['summary']}")
                print()
                return
        
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
                    result = execute_with_retry(
                        web_agent.run, task,
                        max_retries=2, base_delay=1.0,
                        retryable_exceptions=(ConnectionError, TimeoutError, OSError),
                    )
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
                    result = execute_with_retry(
                        research_agent.run, task,
                        max_retries=2, base_delay=1.0,
                        retryable_exceptions=(ConnectionError, TimeoutError, OSError),
                    )
                    results.append(result)
                    print(f"   ✓ {task['task_id']}: {result['status']}")
                except Exception as e:
                    logger.error(f"Research task {task.get('task_id')} failed: {e}")
                    print(f"   ✗ {task['task_id']}: failed - {e}")
            print()

        # Step 5: Clean and structure outputs (Phase 2)
        print("🧹 Structuring collected data...")
        structured_data = normalize_results(results, query=query)
        print(f"   ✓ Structured records: {len(structured_data)}")
        print()

        # Step 6: Apply zero-trust validation (Phase 3)
        print("🛡️  Validating trust on structured data...")
        trust_report = validate_structured_data(structured_data, query=query)
        trusted_data = trust_report["trusted_items"]
        print(f"   ✓ Trusted records: {len(trusted_data)}/{len(structured_data)}")
        print()

        # Step 7: Persist trusted data to database (Phase 4)
        db_stats = {"inserted": 0, "skipped": 0}
        if Config.SAVE_TO_DB:
            print("🗄️  Saving trusted data to database...")
            db_stats = save_trusted_items(trusted_data, query=query)
            print(f"   ✓ Inserted: {db_stats['inserted']} | Skipped duplicates: {db_stats['skipped']}")
            print()

        # Step 8: Generate concise insights (Phase 5)
        insight_input = trusted_data if trusted_data else structured_data
        print("💡 Generating insights from collected data...")
        insights = generate_insights(insight_input, query=query)
        print(f"   ✓ Confidence: {insights['confidence']}")
        print(f"   ✓ Summary: {insights['summary']}")
        if insights["key_highlights"]:
            print("   ✓ Highlights:")
            for idx, title in enumerate(insights["key_highlights"][:3], start=1):
                print(f"      {idx}. {title}")
        print()
        
        # Summary
        print("=" * 60)
        print("✅ EXECUTION COMPLETE")
        print("=" * 60)
        
        successful = sum(1 for r in results if r.get('status') == 'success')
        print(f"Tasks completed: {successful}/{len(results)}")
        
        if Config.SAVE_RAW_DATA:
            print(f"Raw data saved to: {Config.RAW_DATA_DIR}")

        if Config.SAVE_STRUCTURED_DATA:
            print(f"Structured data saved to: {Config.STRUCTURED_DATA_DIR}")

        if Config.SAVE_TRUSTED_DATA:
            print(f"Trusted data saved to: {Config.TRUSTED_DATA_DIR}")

        if Config.SAVE_TO_DB:
            print(f"Trusted data persisted in DB: {Config.DB_PATH}")
        
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

