"""
TrustWise Unit Tests

Basic tests to verify core functionality without requiring API keys or network access.
Run with: python test_basic.py
"""

import json
from pathlib import Path

def test_imports():
    """Test that all modules import correctly."""
    print("Testing imports...")
    try:
        from orchestrator import orchestrator, llm_client, schema, prompts
        from chunker import chunker
        from scheduler import scheduler
        from agents import web_agent, research_agent
        from utils import config, logger
        print("   ✓ All imports successful")
        return True
    except ImportError as e:
        print(f"   ✗ Import failed: {e}")
        return False

def test_schema_validation():
    """Test plan validation."""
    print("\nTesting schema validation...")
    from orchestrator.schema import validate_plan
    
    # Valid plan
    valid_plan = {
        "goal": "Test goal",
        "domains": ["test"],
        "time_range": "latest",
        "sources": ["web"],
        "tasks": [{
            "task_id": "task_1",
            "source_type": "web",
            "agent": "web_agent",
            "prompt": "Test prompt"
        }]
    }
    
    try:
        validate_plan(valid_plan)
        print("   ✓ Valid plan accepted")
    except Exception as e:
        print(f"   ✗ Valid plan rejected: {e}")
        return False
    
    # Invalid plan (missing required field)
    invalid_plan = {
        "goal": "Test goal",
        "domains": ["test"]
        # Missing required fields
    }
    
    try:
        validate_plan(invalid_plan)
        print("   ✗ Invalid plan accepted (should have failed)")
        return False
    except ValueError:
        print("   ✓ Invalid plan rejected correctly")
        return True

def test_chunker():
    """Test task chunking."""
    print("\nTesting chunker...")
    from chunker.chunker import chunk_tasks
    
    plan = {
        "goal": "Test",
        "tasks": [
            {"task_id": "t1", "prompt": "test1"},
            {"task_id": "t2", "prompt": "test2"}
        ]
    }
    
    tasks = chunk_tasks(plan)
    
    if len(tasks) == 2:
        print("   ✓ Chunker works correctly")
        return True
    else:
        print(f"   ✗ Expected 2 tasks, got {len(tasks)}")
        return False

def test_scheduler():
    """Test task scheduling."""
    print("\nTesting scheduler...")
    from scheduler.scheduler import schedule
    
    tasks = [
        {"task_id": "t1", "source_type": "web"},
        {"task_id": "t2", "source_type": "research_papers"},
        {"task_id": "t3", "source_type": "web"}
    ]
    
    web_tasks, paper_tasks = schedule(tasks)
    
    if len(web_tasks) == 2 and len(paper_tasks) == 1:
        print("   ✓ Scheduler routing works correctly")
        return True
    else:
        print(f"   ✗ Expected 2 web, 1 paper. Got {len(web_tasks)} web, {len(paper_tasks)} paper")
        return False

def test_config():
    """Test configuration management."""
    print("\nTesting configuration...")
    from utils.config import Config
    
    # Check that directories exist
    if not Config.RAW_DATA_DIR.exists():
        print("   ✗ Raw data directory not created")
        return False
    
    if not Config.PLANS_DIR.exists():
        print("   ✗ Plans directory not created")
        return False
    
    print("   ✓ Configuration and directories OK")
    return True

def test_research_dedupe():
    """Dedupe merged paper lists by DOI / title."""
    print("\nTesting research dedupe...")
    from agents.research_sources import dedupe_papers

    papers = [
        {"title": "Same Paper", "doi": "10.1234/x", "published": "2024"},
        {"title": "Same Paper", "doi": "10.1234/x", "published": "2024"},
        {"title": "Other", "doi": "10.9999/y", "published": "2023"},
    ]
    u = dedupe_papers(papers)
    if len(u) == 2:
        print("   ✓ dedupe_papers works")
        return True
    print(f"   ✗ Expected 2 unique, got {len(u)}")
    return False


def test_mock_llm():
    """Test mock LLM response."""
    print("\nTesting mock LLM client...")
    from orchestrator.llm_client import call_llm
    from utils.config import Config
    
    # Temporarily ensure no API key (to force mock)
    original_key = Config.GEMINI_API_KEY
    original_provider = Config.LLM_PROVIDER
    Config.GEMINI_API_KEY = None
    Config.LLM_PROVIDER = "gemini"  # force mock path without calling Ollama

    try:
        response = call_llm("test query")
        plan = json.loads(response)

        if "goal" in plan and "tasks" in plan:
            print("   ✓ Mock LLM returns valid JSON")
            result = True
        else:
            print("   ✗ Mock LLM JSON missing required fields")
            result = False
    except Exception as e:
        print(f"   ✗ Mock LLM failed: {e}")
        result = False
    finally:
        Config.GEMINI_API_KEY = original_key
        Config.LLM_PROVIDER = original_provider
    
    return result

def main():
    """Run all tests."""
    print("=" * 60)
    print("TrustWise Basic Tests")
    print("=" * 60)
    
    tests = [
        test_imports,
        test_config,
        test_schema_validation,
        test_chunker,
        test_scheduler,
        test_research_dedupe,
        test_mock_llm
    ]
    
    results = []
    for test_func in tests:
        try:
            results.append(test_func())
        except Exception as e:
            print(f"\n✗ Test {test_func.__name__} crashed: {e}")
            results.append(False)
    
    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(results)
    total = len(results)
    
    print(f"Passed: {passed}/{total}")
    
    if passed == total:
        print("\n✅ All tests passed!")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
