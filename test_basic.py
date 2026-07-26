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
    """Test task chunking and DAG dependency generation."""
    print("\nTesting chunker...")
    from chunker.chunker import chunk_tasks
    
    plan = {
        "goal": "Explain how transformer models improve medical diagnosis",
        "tasks": [
            {"task_id": "t1", "source_type": "web", "prompt": "Search web for recent diagnostic transformer developments"},
            {"task_id": "t2", "source_type": "web", "prompt": "Search web for recent diagnostic transformer developments"}, # duplicate
            {"task_id": "t3", "source_type": "research_papers", "prompt": "Retrieve PubMed papers about transformer models"},
            {"task_id": "t4", "source_type": "research_papers", "prompt": "Compare and synthesize findings of t1 and t3"}, # dependency
        ]
    }
    
    chunks = chunk_tasks(plan)
    
    try:
        # Check deduplication (t1 and t2 should merge/dedupe)
        assert len(chunks) == 3, f"Expected 3 chunks after dedup, got {len(chunks)}"
        
        # Check normalization keys
        for c in chunks:
            assert "chunk_id" in c
            assert "parent_query" in c
            assert "dependencies" in c
            assert "agent" in c
            assert "retry_policy" in c
            assert "trust_constraints" in c
            
        # Check dependency resolution (t4 is synthesis and contains compare, should depend on t1 and t3/PubMed chunk)
        t4_chunks = [c for c in chunks if "t4" in c["chunk_id"] or "compare" in c["description"].lower()]
        assert len(t4_chunks) == 1
        t4 = t4_chunks[0]
        assert len(t4["dependencies"]) >= 2
        
        print("   ✓ Chunker deduplication and dependency resolution OK")
        return True
    except AssertionError as e:
        print(f"   ✗ Chunker validation failed: {e}")
        return False
    except Exception as e:
        print(f"   ✗ Chunker test error: {e}")
        return False

def test_scheduler():
    """Test scheduling and parallel executor."""
    print("\nTesting scheduler...")
    from scheduler.scheduler import schedule, execute_chunks
    from unittest.mock import patch
    
    # Test routing compatibility
    tasks = [
        {"task_id": "t1", "source_type": "web"},
        {"task_id": "t2", "source_type": "research_papers"},
        {"task_id": "t3", "source_type": "web"}
    ]
    
    web_tasks, paper_tasks = schedule(tasks)
    assert len(web_tasks) == 2 and len(paper_tasks) == 1
    
    # Test DAG Execution with mocked agents
    chunks = [
        {
            "chunk_id": "c1",
            "parent_query": "test",
            "title": "c1",
            "description": "test",
            "priority": 3,
            "dependencies": [],
            "agent": "web_agent",
            "source_types": ["web"],
            "trust_constraints": {"min_trust_score": 0.6},
            "expected_output": "markdown",
            "retry_policy": {"max_retries": 1, "backoff_factor": 1.0}
        },
        {
            "chunk_id": "c2",
            "parent_query": "test",
            "title": "c2",
            "description": "test",
            "priority": 3,
            "dependencies": ["c1"], # c2 depends on c1
            "agent": "research_agent",
            "source_types": ["arxiv"],
            "trust_constraints": {"min_trust_score": 0.6},
            "expected_output": "metadata_json",
            "retry_policy": {"max_retries": 1, "backoff_factor": 1.0}
        }
    ]
    
    def mock_run_web(chunk):
        return {"status": "success", "agent": "web_agent", "data": "web data"}
        
    def mock_run_research(chunk):
        return {"status": "success", "agent": "research_agent", "data": "research data"}
        
    with patch("agents.web_agent.run", side_effect=mock_run_web), \
         patch("agents.research_agent.run", side_effect=mock_run_research):
         
        results = execute_chunks(chunks)
        
    try:
        assert len(results) == 2, f"Expected 2 results, got {len(results)}"
        res_map = {r["task_id"]: r for r in results}
        assert res_map["c1"]["status"] == "success"
        assert res_map["c2"]["status"] == "success"
        print("   ✓ Scheduler routing and concurrent DAG execution OK")
        return True
    except AssertionError as e:
        print(f"   ✗ Scheduler validation failed: {e}")
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
    original_allow_mock = Config.ALLOW_MOCK_FALLBACK
    Config.GEMINI_API_KEY = None
    Config.LLM_PROVIDER = "gemini"  # force mock path without calling Ollama
    Config.ALLOW_MOCK_FALLBACK = True

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
        Config.ALLOW_MOCK_FALLBACK = original_allow_mock
    
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

def test_academic_retrieval():
    """Test PubMed XML parsing and Scopus complete/standard fallback logic."""
    print("\nTesting academic retrieval enhancement...")
    from agents.research_sources import _parse_pubmed_efetch_xml
    from agents.keyed_adapters import fetch_scopus
    from utils.config import Config
    from unittest.mock import patch
    from agents.keyed_http import KeyedAdapterError

    # 1. PubMed XML Parsing Tests
    xml_with_abstract = """
    <PubmedArticleSet>
      <PubmedArticle>
        <MedlineCitation>
          <PMID>11111</PMID>
          <Article>
            <Journal>
              <Title>Journal of TrustWise Medicine</Title>
              <JournalIssue>
                <PubDate>
                  <Year>2024</Year>
                </PubDate>
              </JournalIssue>
            </Journal>
            <ArticleTitle>AI in Diagnostics</ArticleTitle>
            <Abstract>
              <AbstractText Label="OBJECTIVE">To test diagnostics.</AbstractText>
              <AbstractText Label="CONCLUSION">Conclusion of test.</AbstractText>
            </Abstract>
            <AuthorList>
              <Author>
                <LastName>Doe</LastName>
                <ForeName>John</ForeName>
              </Author>
            </AuthorList>
            <KeywordList>
              <Keyword>Deep Learning</Keyword>
            </KeywordList>
          </Article>
          <MeshHeadingList>
            <MeshHeading>
              <DescriptorName>Diagnostics</DescriptorName>
            </MeshHeading>
          </MeshHeadingList>
        </MedlineCitation>
        <PubmedData>
          <ArticleIdList>
            <ArticleId IdType="doi">10.1111/tw.123</ArticleId>
          </ArticleIdList>
        </PubmedData>
      </PubmedArticle>
    </PubmedArticleSet>
    """
    
    papers = _parse_pubmed_efetch_xml(xml_with_abstract)
    try:
        assert len(papers) == 1
        p = papers[0]
        assert p["pubmed_id"] == "11111"
        assert p["title"] == "AI in Diagnostics"
        assert "OBJECTIVE: To test diagnostics." in p["abstract"]
        assert "CONCLUSION: Conclusion of test." in p["abstract"]
        assert p["authors"] == ["John Doe"]
        assert p["journal"] == "Journal of TrustWise Medicine"
        assert p["published"] == "2024"
        assert p["doi"] == "10.1111/tw.123"
        assert "Deep Learning" in p["keywords"]
        assert "Diagnostics" in p["mesh_terms"]
    except AssertionError as e:
        print(f"   ✗ PubMed XML parsing with abstract failed: {e}")
        return False

    # XML without abstract
    xml_no_abstract = """
    <PubmedArticleSet>
      <PubmedArticle>
        <MedlineCitation>
          <PMID>22222</PMID>
          <Article>
            <ArticleTitle>No Abstract Article</ArticleTitle>
          </Article>
        </MedlineCitation>
      </PubmedArticle>
    </PubmedArticleSet>
    """
    papers_no = _parse_pubmed_efetch_xml(xml_no_abstract)
    try:
        assert len(papers_no) == 1
        assert papers_no[0]["pubmed_id"] == "22222"
        assert papers_no[0]["abstract"] == ""
    except AssertionError as e:
        print(f"   ✗ PubMed XML parsing without abstract failed: {e}")
        return False

    # Invalid XML
    assert _parse_pubmed_efetch_xml("<invalid>") == []

    # 2. Scopus Fallback and complete view test
    original_key = Config.SCOPUS_API_KEY
    Config.SCOPUS_API_KEY = "test_key"
    
    complete_err = KeyedAdapterError("HTTP Error", http_status=403, error_type="http_error")
    
    def mock_request(method, url, session, params):
        if params.get("view") == "COMPLETE":
            raise complete_err
        return {
            "search-results": {
                "entry": [
                    {
                        "dc:title": "Scopus Fallback Hit",
                        "dc:creator": ["Alice Smith"],
                        "prism:coverDate": "2024-05-12",
                        "prism:doi": "10.5555/scp.123",
                        "dc:description": "Scopus abstract fallback",
                        "authkeywords": "Machine Learning|Healthcare",
                        "citedby-count": "15"
                    }
                ]
            }
        }, {"http_status": 200, "retries_used": 1, "ok": True}

    with patch("agents.keyed_adapters.safe_request_json", side_effect=mock_request):
        rows, meta = fetch_scopus("test query", limit=1)
        
    try:
        assert meta["ok"] is True
        assert len(rows) == 1
        r = rows[0]
        assert r["title"] == "Scopus Fallback Hit"
        assert r["authors"] == ["Alice Smith"]
        assert r["published"] == "2024-05-12"
        assert r["doi"] == "10.5555/scp.123"
        assert r["abstract"] == "Scopus abstract fallback"
        assert r["journal"] == ""
        assert r["citation_count"] == 15
        assert "Machine Learning" in r["keywords"]
        print("   ✓ PubMed & Scopus metadata parsing and fallback execution OK")
        return True
    except AssertionError as e:
        print(f"   ✗ Scopus complete to standard fallback failed: {e}")
        return False
    finally:
        Config.SCOPUS_API_KEY = original_key

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
        test_academic_retrieval,
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
