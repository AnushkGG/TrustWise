import json
from dotenv import load_dotenv
from orchestrator.orchestrator import generate_plan
from chunker.chunker import chunk_tasks
from scheduler.scheduler import schedule, execute_chunks
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
    Run the full TrustWise CLI pipeline for one user query.

    Flow:
    1. Accept user query
    2. Generate structured execution plan
    3. Chunk and schedule tasks
    4. Execute web and research agents
    5. Normalize and trust-validate collected data
    6. Persist trusted data and generate insights
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

        # Optional fast path: reuse trusted local DB data when sufficient.
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
        chunks = chunk_tasks(plan)
        
        # Step 3 & 4: Schedule and Execute Chunks Concurrently
        logger.info("Scheduling and executing chunks concurrently...")
        print("⚡ Executing Chunks in Parallel...")
        results = execute_chunks(chunks)
        for r in results:
            status_icon = "✓" if r.get("status") == "success" else "✗"
            print(f"   {status_icon} {r.get('task_id')}: {r.get('status')}")
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

