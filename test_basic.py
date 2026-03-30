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

        if "goal" in plan and "tasks" in plan and plan.get("plan_source") == "mock":
            assert "test query" in plan.get("goal", "").lower()
            print("   ✓ Mock LLM returns valid JSON [query-aware mock]")
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


def test_merge_plans():
    """Test _merge_plans produces balanced, attributed output."""
    print("\nTesting plan merge logic...")
    from orchestrator.llm_client import _merge_plans

    gemini_plan = {
        "goal": "Understand AI in healthcare",
        "domains": ["AI", "Healthcare"],
        "time_range": "2024",
        "sources": ["web"],
        "tasks": [
            {"task_id": "g1", "source_type": "web", "agent": "web_agent",
             "prompt": "Find recent AI healthcare news articles"},
            {"task_id": "g2", "source_type": "research_papers", "agent": "research_agent",
             "prompt": "Search papers on AI diagnostics"},
        ],
    }
    ollama_plan = {
        "goal": "AI healthcare overview",
        "domains": ["ai", "Medicine"],
        "time_range": "latest",
        "sources": ["web", "research_papers"],
        "tasks": [
            {"task_id": "o1", "source_type": "web", "agent": "web_agent",
             "prompt": "Find recent AI healthcare news articles and reports"},
            {"task_id": "o2", "source_type": "research_papers", "agent": "research_agent",
             "prompt": "Look up machine learning medical papers"},
        ],
    }

    merged = _merge_plans(gemini_plan, ollama_plan)

    try:
        assert merged["plan_source"] == "merged"
        assert set(merged["providers"]) == {"gemini", "ollama"}

        # Domains union (case-insensitive dedup)
        domain_lower = [d.lower() for d in merged["domains"]]
        assert "ai" in domain_lower
        assert "healthcare" in domain_lower
        assert "medicine" in domain_lower

        # Time range: prefer specific over "latest"
        assert merged["time_range"] == "2024"

        # Sources union
        assert "web" in merged["sources"]
        assert "research_papers" in merged["sources"]

        # Every task has origin
        for t in merged["tasks"]:
            assert t.get("origin") in ("gemini", "ollama", "both"), f"Missing origin on {t}"

        # Near-duplicate prompt dedup should mark at least one task as "both"
        both_count = sum(1 for t in merged["tasks"] if t["origin"] == "both")
        assert both_count >= 1, "Expected at least one deduplicated task with origin='both'"

        assert len(merged["tasks"]) <= 8

        print("   ✓ Plan merge: attribution, dedup, balanced interleave OK")
        return True
    except AssertionError as e:
        print(f"   ✗ Plan merge assertion failed: {e}")
        return False
    except Exception as e:
        print(f"   ✗ Plan merge failed: {e}")
        return False


def test_merge_summaries():
    """Test _merge_summaries produces attributed key-points."""
    print("\nTesting summary merge logic...")
    from insights.generator import _merge_summaries

    gemini_res = {
        "concise_answer": "AI significantly improves healthcare outcomes across multiple domains.",
        "key_points": [
            "AI improves diagnostic accuracy by 35%.",
            "Deep learning models outperform traditional methods.",
            "Cost reduction is a key benefit.",
        ],
    }
    ollama_res = {
        "concise_answer": "Healthcare AI is growing fast.",
        "key_points": [
            "AI improves diagnostic accuracy by 35 percent.",
            "Regulatory challenges remain significant.",
        ],
    }

    merged = _merge_summaries(gemini_res, ollama_res)

    try:
        # Longer answer wins
        assert "significantly" in merged["concise_answer"]
        assert merged["concise_answer_origin"] == "gemini"

        # Key points are dicts with text + origin
        for kp in merged["key_points"]:
            assert isinstance(kp, dict), f"Expected dict, got {type(kp)}"
            assert "text" in kp and "origin" in kp
            assert kp["origin"] in ("gemini", "ollama", "both")

        # Near-duplicate "35%" points should be merged to "both"
        both_points = [kp for kp in merged["key_points"] if kp["origin"] == "both"]
        assert len(both_points) >= 1, "Expected at least one 'both' origin point from dedup"

        assert len(merged["key_points"]) <= 5

        print("   ✓ Summary merge: attribution, dedup, cap OK")
        return True
    except AssertionError as e:
        print(f"   ✗ Summary merge failed: {e}")
        return False
    except Exception as e:
        print(f"   ✗ Summary merge error: {e}")
        return False

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
        test_mock_llm,
        test_merge_plans,
        test_merge_summaries,
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
