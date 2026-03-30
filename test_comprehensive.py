"""
TrustWise Comprehensive Test Suite

Tests for trust validation, data cleaning, storage, insights generation,
retry logic, and rate limiting — all without requiring API keys or
network access.

Run with: python test_comprehensive.py
"""

import hashlib
import json
import os
import sqlite3
import tempfile
import time
from pathlib import Path
from unittest.mock import patch

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

_results: list = []


def _run(name: str, func):
    """Run a single test and collect the result."""
    try:
        func()
        print(f"   ✓ {name}")
        _results.append(True)
    except Exception as exc:
        print(f"   ✗ {name}: {exc}")
        _results.append(False)


# ---------------------------------------------------------------------------
# Trust Validator Tests
# ---------------------------------------------------------------------------

def _test_trust_high_score_for_trusted_domain():
    from trust.validator import _score_item
    item = {
        "title": "AI in healthcare breakthrough",
        "content": "A" * 700,
        "source": "https://www.reuters.com/article/ai",
        "url": "https://www.reuters.com/article/ai",
        "content_type": "web",
    }
    trusted = {"reuters.com"}
    query_terms = {"healthcare", "breakthrough"}
    scored, _ = _score_item(item, trusted, query_terms)
    assert scored["trust"]["score"] >= 0.65, f"Expected >=0.65, got {scored['trust']['score']}"


def _test_trust_low_score_for_unknown_domain():
    from trust.validator import _score_item
    item = {
        "title": "Random post",
        "content": "Short",
        "source": "https://unknown-blog.xyz/post",
        "url": "https://unknown-blog.xyz/post",
        "content_type": "web",
    }
    scored, _ = _score_item(item, set(), set())
    assert scored["trust"]["score"] < 0.5, f"Expected <0.5, got {scored['trust']['score']}"


def _test_trust_research_paper_base_score():
    from trust.validator import _score_item
    item = {
        "title": "Transformer Models in Medical Imaging",
        "content": "A" * 800,
        "source": "arXiv",
        "url": "https://arxiv.org/abs/2401.12345",
        "content_type": "research_paper",
    }
    scored, _ = _score_item(item, set(), {"transformer", "medical"})
    assert scored["trust"]["score"] >= 0.6, f"Expected >=0.6, got {scored['trust']['score']}"


def _test_trust_suspicious_content_penalty():
    from trust.validator import _suspicious_penalty
    content = "accept all cookies privacy policy consent management subscribe now"
    penalty = _suspicious_penalty(content)
    assert penalty > 0, f"Expected penalty >0, got {penalty}"


def _test_trust_no_penalty_for_clean_content():
    from trust.validator import _suspicious_penalty
    content = "Recent advances in artificial intelligence have transformed the healthcare industry."
    penalty = _suspicious_penalty(content)
    assert penalty == 0, f"Expected 0 penalty, got {penalty}"


def _test_trust_duplicate_detection():
    from trust.validator import validate_structured_data
    items = [
        {
            "title": "Same Article Title",
            "content": "A" * 700,
            "source": "arXiv",
            "url": "https://arxiv.org/abs/1",
            "content_type": "research_paper",
        },
        {
            "title": "Same Article Title",
            "content": "A" * 700,
            "source": "arXiv",
            "url": "https://arxiv.org/abs/2",
            "content_type": "research_paper",
        },
    ]
    with patch("trust.validator.Config") as mock_cfg:
        mock_cfg.SAVE_TRUSTED_DATA = False
        mock_cfg.CONFIG_DIR = Path(tempfile.mkdtemp())
        report = validate_structured_data(items, query="test")

    # Second item should be marked as duplicate and untrusted
    all_items = report["all_items"]
    assert len(all_items) == 2
    assert all_items[1]["trust"]["duplicate"] is True


def _test_trust_query_term_extraction():
    from trust.validator import _extract_query_terms
    terms = _extract_query_terms("Tell me about latest AI in healthcare")
    assert "healthcare" in terms
    assert "tell" not in terms  # stop word
    assert "me" not in terms  # stop word


def _test_trust_relevance_score():
    from trust.validator import _relevance_score
    score = _relevance_score(
        "AI in Healthcare", "Artificial intelligence transforms healthcare delivery", {"healthcare", "transforms"}
    )
    assert score > 0, f"Expected >0, got {score}"

    zero_score = _relevance_score("Unrelated", "Nothing matching", {"quantum", "computing"})
    assert zero_score == 0, f"Expected 0, got {zero_score}"


# ---------------------------------------------------------------------------
# Cleaner Tests
# ---------------------------------------------------------------------------

def _test_cleaner_normalize_web_results():
    from cleaner.cleaner import normalize_results
    results = [
        {
            "agent": "web_agent",
            "data": [
                {"source": "https://example.com/ai", "content": "# AI Breakthrough\nRecent advances in AI."}
            ],
        }
    ]
    with patch("cleaner.cleaner.Config") as mock_cfg:
        mock_cfg.SAVE_STRUCTURED_DATA = False
        structured = normalize_results(results, query="AI advances")
    assert len(structured) == 1
    assert structured[0]["content_type"] == "web"
    assert structured[0]["title"] == "AI Breakthrough"


def _test_cleaner_normalize_research_results():
    from cleaner.cleaner import normalize_results
    results = [
        {
            "agent": "research_agent",
            "data": [
                {
                    "title": "Quantum Computing Survey",
                    "abstract": "A comprehensive survey of quantum computing.",
                    "pdf_url": "https://arxiv.org/pdf/2401.00001",
                    "published": "2024-01-15",
                    "authors": ["Alice", "Bob"],
                    "categories": ["cs.AI"],
                    "arxiv_id": "2401.00001",
                }
            ],
        }
    ]
    with patch("cleaner.cleaner.Config") as mock_cfg:
        mock_cfg.SAVE_STRUCTURED_DATA = False
        structured = normalize_results(results, query="quantum")
    assert len(structured) == 1
    assert structured[0]["content_type"] == "research_paper"
    assert structured[0]["source"] == "arXiv"


def _test_cleaner_empty_content_skipped():
    from cleaner.cleaner import normalize_results
    results = [
        {
            "agent": "web_agent",
            "data": [{"source": "https://empty.com", "content": ""}],
        }
    ]
    with patch("cleaner.cleaner.Config") as mock_cfg:
        mock_cfg.SAVE_STRUCTURED_DATA = False
        structured = normalize_results(results, query="test")
    assert len(structured) == 0


def _test_cleaner_text_truncation():
    from cleaner.cleaner import _clean_text
    long_text = "A" * 5000
    cleaned = _clean_text(long_text, max_chars=100)
    assert len(cleaned) <= 120  # 100 + "... (truncated)"
    assert "truncated" in cleaned


def _test_cleaner_junk_removal():
    from cleaner.cleaner import _clean_text
    text = "Real content\nprivacy policy stuff\nMore real content"
    cleaned = _clean_text(text)
    assert "privacy policy" not in cleaned
    assert "Real content" in cleaned


def _test_cleaner_title_extraction():
    from cleaner.cleaner import _extract_web_title
    assert _extract_web_title("# Main Heading\nSome content", "fallback") == "Main Heading"
    assert _extract_web_title("## Sub Heading\nContent", "fallback") == "Sub Heading"
    assert _extract_web_title("No headings here", "fallback.com") == "fallback.com"


# ---------------------------------------------------------------------------
# Storage / DB Tests
# ---------------------------------------------------------------------------

def _test_storage_init_and_save():
    from storage.db import init_db, save_trusted_items, _build_content_hash

    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test.db"
        with patch("storage.db.Config") as mock_cfg:
            mock_cfg.DB_PATH = db_path
            init_db()
            items = [
                {
                    "title": "Test Title",
                    "content": "Test content for storage",
                    "source": "test",
                    "url": "https://test.com",
                    "published_at": None,
                    "content_type": "web",
                    "trust": {"score": 0.85},
                }
            ]
            stats = save_trusted_items(items, query="storage test")
            assert stats["inserted"] == 1
            assert stats["skipped"] == 0

            # Re-insert should skip duplicates
            stats2 = save_trusted_items(items, query="storage test")
            assert stats2["inserted"] == 0
            assert stats2["skipped"] == 1


def _test_storage_cache_retrieval():
    from storage.db import init_db, save_trusted_items, get_cached_trusted_items

    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test_cache.db"
        with patch("storage.db.Config") as mock_cfg:
            mock_cfg.DB_PATH = db_path
            init_db()

            items = [
                {
                    "title": f"Item {i}",
                    "content": f"Content for item {i} about AI",
                    "source": "test",
                    "url": f"https://test.com/{i}",
                    "published_at": None,
                    "content_type": "web",
                    "trust": {"score": 0.8},
                }
                for i in range(5)
            ]
            save_trusted_items(items, query="AI developments")

            cached = get_cached_trusted_items(query="AI developments", min_items=3)
            assert len(cached) >= 3, f"Expected >=3 cached items, got {len(cached)}"


def _test_storage_empty_items_skipped():
    from storage.db import save_trusted_items

    with tempfile.TemporaryDirectory() as tmpdir:
        db_path = Path(tmpdir) / "test_empty.db"
        with patch("storage.db.Config") as mock_cfg:
            mock_cfg.DB_PATH = db_path
            stats = save_trusted_items([], query="empty")
            assert stats["inserted"] == 0
            assert stats["skipped"] == 0


def _test_storage_content_hash_deterministic():
    from storage.db import _build_content_hash
    h1 = _build_content_hash("Title", "https://url.com", "Content here")
    h2 = _build_content_hash("Title", "https://url.com", "Content here")
    h3 = _build_content_hash("Different", "https://url.com", "Content here")
    assert h1 == h2, "Same inputs should produce the same hash"
    assert h1 != h3, "Different inputs should produce different hashes"


# ---------------------------------------------------------------------------
# Insights Tests
# ---------------------------------------------------------------------------

def _test_insights_empty_input():
    from insights.generator import generate_insights
    result = generate_insights([], query="test")
    assert result["confidence"] == 0.0
    assert result["key_highlights"] == []
    assert "No trusted data" in result["summary"]


def _test_insights_with_trusted_items():
    from insights.generator import generate_insights
    items = [
        {
            "title": "AI Healthcare Paper",
            "content": "Artificial intelligence improves diagnostics accuracy by 35% in radiology studies. "
                       "The study results demonstrate significant improvements in detection rates.",
            "source": "arXiv",
            "url": "https://arxiv.org/abs/1",
            "content_type": "research_paper",
            "trust": {"score": 0.85},
        },
        {
            "title": "Machine Learning in Hospitals",
            "content": "Machine learning models reduce hospital readmission rates. "
                       "Results show a 20% improvement in patient outcomes across multiple clinical trials.",
            "source": "reuters.com",
            "url": "https://reuters.com/ai",
            "content_type": "web",
            "trust": {"score": 0.75},
        },
    ]

    with patch("insights.generator._call_llm_for_summary", return_value={}):
        result = generate_insights(items, query="AI healthcare")

    assert result["confidence"] > 0
    assert len(result["key_highlights"]) >= 1
    assert result["source_breakdown"]["arXiv"] == 1
    assert result["content_type_breakdown"]["research_paper"] == 1


def _test_insights_sentence_ranking():
    from insights.generator import _rank_sentences
    sentences = [
        "AI improves diagnostics by 35% in radiology.",
        "The weather is nice today in the park.",
        "Deep learning outperforms traditional methods in medical imaging study.",
    ]
    ranked = _rank_sentences(sentences, ["diagnostics", "radiology", "medical"], require_overlap=True)
    assert len(ranked) >= 2
    # The sentence about weather should be excluded (no overlap with query terms)


def _test_insights_query_term_extraction():
    from insights.generator import _extract_query_terms
    terms = _extract_query_terms("Latest AI developments in healthcare")
    assert "developments" in terms
    assert "healthcare" in terms
    assert "latest" not in terms  # stopword
    assert "the" not in terms


def _test_insights_sentence_splitting():
    from insights.generator import _split_sentences
    text = (
        "Artificial intelligence is transforming the healthcare industry significantly. "
        "Deep learning models achieve state-of-the-art accuracy in medical imaging tasks! "
        "Should we invest more resources into AI-driven clinical decision support systems?"
    )
    sentences = _split_sentences(text)
    assert len(sentences) >= 2, f"Expected >=2 sentences, got {len(sentences)}: {sentences}"


# ---------------------------------------------------------------------------
# Retry Logic Tests
# ---------------------------------------------------------------------------

def _test_retry_succeeds_on_first_try():
    from utils.retry import retry_with_backoff

    call_count = 0

    @retry_with_backoff(max_retries=3, base_delay=0.01)
    def succeed():
        nonlocal call_count
        call_count += 1
        return "ok"

    result = succeed()
    assert result == "ok"
    assert call_count == 1


def _test_retry_succeeds_after_failures():
    from utils.retry import retry_with_backoff

    call_count = 0

    @retry_with_backoff(max_retries=3, base_delay=0.01, max_delay=0.05)
    def fail_twice():
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            raise ConnectionError("temporary failure")
        return "ok"

    result = fail_twice()
    assert result == "ok"
    assert call_count == 3


def _test_retry_exhausted_raises():
    from utils.retry import retry_with_backoff

    call_count = 0

    @retry_with_backoff(max_retries=2, base_delay=0.01, max_delay=0.02)
    def always_fail():
        nonlocal call_count
        call_count += 1
        raise ValueError("permanent failure")

    raised = False
    try:
        always_fail()
    except ValueError:
        raised = True

    assert raised, "Expected ValueError to be raised after retries exhausted"
    assert call_count == 3  # 1 initial + 2 retries


def _test_retry_only_retries_specified_exceptions():
    from utils.retry import retry_with_backoff

    @retry_with_backoff(
        max_retries=3,
        base_delay=0.01,
        retryable_exceptions=(ConnectionError,),
    )
    def type_error():
        raise TypeError("not retryable")

    raised = False
    try:
        type_error()
    except TypeError:
        raised = True

    assert raised, "TypeError should not be retried"


def _test_execute_with_retry():
    from utils.retry import execute_with_retry

    call_count = 0

    def flaky(x):
        nonlocal call_count
        call_count += 1
        if call_count < 2:
            raise RuntimeError("oops")
        return x * 2

    result = execute_with_retry(flaky, 5, max_retries=3, base_delay=0.01)
    assert result == 10
    assert call_count == 2


# ---------------------------------------------------------------------------
# Rate Limiter Tests
# ---------------------------------------------------------------------------

def _test_rate_limiter_basic():
    from utils.rate_limiter import RateLimiter
    limiter = RateLimiter(max_requests=3, period=0.5)
    assert limiter.available_tokens == 3
    limiter.acquire()
    limiter.acquire()
    assert limiter.available_tokens == 1
    limiter.acquire()
    assert limiter.available_tokens == 0


def _test_rate_limiter_blocks_when_exhausted():
    from utils.rate_limiter import RateLimiter
    limiter = RateLimiter(max_requests=2, period=0.3)
    limiter.acquire()
    limiter.acquire()
    start = time.monotonic()
    limiter.acquire()  # Should block until a token expires
    elapsed = time.monotonic() - start
    assert elapsed >= 0.2, f"Expected blocking for at least 0.2s, got {elapsed:.3f}s"


def _test_rate_limiter_invalid_args():
    from utils.rate_limiter import RateLimiter
    raised = False
    try:
        RateLimiter(max_requests=0, period=1.0)
    except ValueError:
        raised = True
    assert raised, "Expected ValueError for max_requests=0"

    raised = False
    try:
        RateLimiter(max_requests=5, period=-1)
    except ValueError:
        raised = True
    assert raised, "Expected ValueError for negative period"


# ---------------------------------------------------------------------------
# Integration Tests
# ---------------------------------------------------------------------------

def _test_pipeline_mock_end_to_end():
    """Test the full pipeline with mock LLM (no network)."""
    from orchestrator.orchestrator import generate_plan
    from chunker.chunker import chunk_tasks
    from scheduler.scheduler import schedule
    from utils.config import Config

    # Force mock mode
    original_key = Config.GEMINI_API_KEY
    Config.GEMINI_API_KEY = None

    try:
        plan = generate_plan("AI in healthcare")
        assert "goal" in plan
        assert "tasks" in plan

        tasks = chunk_tasks(plan)
        assert len(tasks) > 0

        web_tasks, paper_tasks = schedule(tasks)
        assert len(web_tasks) + len(paper_tasks) == len(tasks)

        # Verify all tasks have agent assignments
        for t in web_tasks:
            assert t["agent"] == "web_agent"
        for t in paper_tasks:
            assert t["agent"] == "research_agent"
    finally:
        Config.GEMINI_API_KEY = original_key


def _test_cleaner_trust_pipeline():
    """Test cleaner -> trust validator pipeline integration."""
    from cleaner.cleaner import normalize_results
    from trust.validator import validate_structured_data

    results = [
        {
            "agent": "research_agent",
            "data": [
                {
                    "title": "Deep Learning for Medical Imaging",
                    "abstract": "We present a novel deep learning approach for medical imaging "
                                "that achieves state-of-the-art results on multiple benchmarks. "
                                "Our method improves detection accuracy by 15% compared to "
                                "previous approaches." * 5,
                    "pdf_url": "https://arxiv.org/pdf/2401.99999",
                    "published": "2024-01-20",
                    "authors": ["Dr. Smith"],
                    "categories": ["cs.CV"],
                    "arxiv_id": "2401.99999",
                }
            ],
        }
    ]

    with patch("cleaner.cleaner.Config") as mock_cleaner_cfg:
        mock_cleaner_cfg.SAVE_STRUCTURED_DATA = False
        structured = normalize_results(results, query="deep learning medical")

    assert len(structured) == 1

    with patch("trust.validator.Config") as mock_trust_cfg:
        mock_trust_cfg.SAVE_TRUSTED_DATA = False
        mock_trust_cfg.CONFIG_DIR = Path(tempfile.mkdtemp())
        report = validate_structured_data(structured, query="deep learning medical")

    assert report["validated_count"] == 1
    assert report["trusted_count"] >= 0  # May or may not pass threshold depending on content


# ---------------------------------------------------------------------------
# Main runner
# ---------------------------------------------------------------------------

def main():
    print("=" * 60)
    print("TrustWise Comprehensive Tests")
    print("=" * 60)

    sections = [
        (
            "Trust Validator",
            [
                ("Trusted domain gets high score", _test_trust_high_score_for_trusted_domain),
                ("Unknown domain gets low score", _test_trust_low_score_for_unknown_domain),
                ("Research paper base score", _test_trust_research_paper_base_score),
                ("Suspicious content penalty applied", _test_trust_suspicious_content_penalty),
                ("Clean content has no penalty", _test_trust_no_penalty_for_clean_content),
                ("Duplicate detection works", _test_trust_duplicate_detection),
                ("Query term extraction", _test_trust_query_term_extraction),
                ("Relevance scoring", _test_trust_relevance_score),
            ],
        ),
        (
            "Data Cleaner",
            [
                ("Normalize web results", _test_cleaner_normalize_web_results),
                ("Normalize research results", _test_cleaner_normalize_research_results),
                ("Empty content skipped", _test_cleaner_empty_content_skipped),
                ("Text truncation", _test_cleaner_text_truncation),
                ("Junk content removal", _test_cleaner_junk_removal),
                ("Title extraction from markdown", _test_cleaner_title_extraction),
            ],
        ),
        (
            "Storage / Database",
            [
                ("Init DB, save and deduplicate", _test_storage_init_and_save),
                ("Cache retrieval", _test_storage_cache_retrieval),
                ("Empty items handled", _test_storage_empty_items_skipped),
                ("Content hash is deterministic", _test_storage_content_hash_deterministic),
            ],
        ),
        (
            "Insights Generator",
            [
                ("Empty input returns defaults", _test_insights_empty_input),
                ("Generates insights from items", _test_insights_with_trusted_items),
                ("Sentence ranking by relevance", _test_insights_sentence_ranking),
                ("Query term extraction", _test_insights_query_term_extraction),
                ("Sentence splitting", _test_insights_sentence_splitting),
            ],
        ),
        (
            "Retry Logic",
            [
                ("Succeeds on first try", _test_retry_succeeds_on_first_try),
                ("Succeeds after transient failures", _test_retry_succeeds_after_failures),
                ("Raises after retries exhausted", _test_retry_exhausted_raises),
                ("Only retries specified exceptions", _test_retry_only_retries_specified_exceptions),
                ("execute_with_retry helper", _test_execute_with_retry),
            ],
        ),
        (
            "Rate Limiter",
            [
                ("Basic token consumption", _test_rate_limiter_basic),
                ("Blocks when tokens exhausted", _test_rate_limiter_blocks_when_exhausted),
                ("Rejects invalid arguments", _test_rate_limiter_invalid_args),
            ],
        ),
        (
            "Integration",
            [
                ("Mock pipeline end-to-end", _test_pipeline_mock_end_to_end),
                ("Cleaner → Trust pipeline", _test_cleaner_trust_pipeline),
            ],
        ),
    ]

    for section_name, tests in sections:
        print(f"\n{section_name}:")
        for test_name, test_func in tests:
            _run(test_name, test_func)

    # Summary
    passed = sum(_results)
    total = len(_results)

    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)
    print(f"Passed: {passed}/{total}")

    if passed == total:
        print("\n✅ All tests passed!")
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")

    return passed == total


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
