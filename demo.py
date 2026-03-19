"""
TrustWise Demo Script

Demonstrates the system with example queries without requiring user input.
Useful for testing and understanding the flow.
"""

import json
from dotenv import load_dotenv
from orchestrator.orchestrator import generate_plan
from chunker.chunker import chunk_tasks
from scheduler.scheduler import schedule
from agents import web_agent, research_agent
from utils.config import Config
from utils.logger import setup_logger

# Load environment variables
load_dotenv()

logger = setup_logger(__name__)

# Example queries for demonstration
DEMO_QUERIES = [
    "What are the latest AI developments in healthcare?",
    "Find recent research on transformer models in computer vision",
    "Weekly tech updates on cybersecurity breaches",
    "What are the latest developments in quantum computing?",
]

def run_demo(query: str):
    """Run a single demo query through the system."""
    
    print("\n" + "=" * 70)
    print(f"DEMO QUERY: {query}")
    print("=" * 70)
    
    try:
        # Generate Plan
        print("\n🔄 Generating execution plan...")
        plan = generate_plan(query)
        
        print(f"\n📋 Plan Generated:")
        print(f"   Goal: {plan.get('goal', 'N/A')}")
        print(f"   Domains: {', '.join(plan.get('domains', []))}")
        print(f"   Time Range: {plan.get('time_range', 'N/A')}")
        print(f"   Sources: {', '.join(plan.get('sources', []))}")
        print(f"   Tasks: {len(plan.get('tasks', []))}")
        
        # Chunk and Schedule
        tasks = chunk_tasks(plan)
        web_tasks, paper_tasks = schedule(tasks)
        
        print(f"\n📊 Scheduled: {len(web_tasks)} web, {len(paper_tasks)} research")
        
        # Execute (limited for demo)
        results = []
        
        if web_tasks:
            print(f"\n🌐 Executing {len(web_tasks)} Web Task(s)...")
            for i, task in enumerate(web_tasks[:2], 1):  # Limit to 2 for demo
                print(f"   [{i}] {task['task_id']}: {task['prompt'][:60]}...")
                try:
                    result = web_agent.run(task)
                    results.append(result)
                    print(f"       → Status: {result['status']}")
                except Exception as e:
                    print(f"       → Error: {e}")
        
        if paper_tasks:
            print(f"\n📚 Executing {len(paper_tasks)} Research Task(s)...")
            for i, task in enumerate(paper_tasks[:2], 1):  # Limit to 2 for demo
                print(f"   [{i}] {task['task_id']}: {task['prompt'][:60]}...")
                try:
                    result = research_agent.run(task)
                    results.append(result)
                    print(f"       → Status: {result['status']}")
                    if result.get('data'):
                        print(f"       → Papers found: {len(result['data'])}")
                except Exception as e:
                    print(f"       → Error: {e}")
        
        # Summary
        successful = sum(1 for r in results if r.get('status') == 'success')
        print(f"\n✅ Completed: {successful}/{len(results)} tasks successful")
        
        return True
        
    except Exception as e:
        logger.error(f"Demo failed: {e}", exc_info=True)
        print(f"\n❌ Error: {e}")
        return False

def main():
    """Run all demo queries."""
    
    print("=" * 70)
    print("TrustWise - Phase 1 Demo")
    print("=" * 70)
    print("\nThis demo runs example queries through the system.")
    
    # Check config
    try:
        Config.validate()
        print("✓ Using real LLM API")
    except ValueError:
        print("⚠️  Using mock LLM responses (no API key configured)")
    
    print(f"\nRunning {len(DEMO_QUERIES)} demo queries...\n")
    
    # Run demos
    succeeded = 0
    for i, query in enumerate(DEMO_QUERIES, 1):
        print(f"\n{'─' * 70}")
        print(f"Demo {i}/{len(DEMO_QUERIES)}")
        print(f"{'─' * 70}")
        
        if run_demo(query):
            succeeded += 1
        
        if i < len(DEMO_QUERIES):
            input("\nPress Enter to continue to next demo...")
    
    # Final summary
    print("\n" + "=" * 70)
    print("DEMO COMPLETE")
    print("=" * 70)
    print(f"Successfully completed: {succeeded}/{len(DEMO_QUERIES)} queries")
    
    if Config.SAVE_PLANS:
        print(f"\n📁 Plans saved to: {Config.PLANS_DIR}")
    if Config.SAVE_RAW_DATA:
        print(f"📁 Raw data saved to: {Config.RAW_DATA_DIR}")
    
    print()

if __name__ == "__main__":
    main()
