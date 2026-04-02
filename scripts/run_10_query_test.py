#!/usr/bin/env python3
"""
TrustWise 10-Query Integration Test & Analysis

Runs 10 diverse queries through the api_bridge.py pipeline (mock mode),
captures full JSON responses, and produces a detailed analysis report.

Usage:
    python scripts/run_10_query_test.py

Output:
    - logs/query_test_results.json   (raw JSON responses)
    - logs/query_test_analysis.txt   (human-readable analysis)
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
LOGS_DIR = ROOT / "logs"
LOGS_DIR.mkdir(exist_ok=True)

# 10 diverse queries spanning different domains, lengths, and styles
QUERIES = [
    # 1. Technology / AI
    "What are the latest breakthroughs in artificial intelligence for healthcare?",
    # 2. Science / Climate
    "How is climate change affecting global food production in 2025?",
    # 3. Finance / Cryptocurrency
    "What are the current trends in cryptocurrency regulation worldwide?",
    # 4. Cybersecurity
    "What are the biggest cybersecurity threats facing enterprises in 2025?",
    # 5. Space / Astronomy
    "What are the recent discoveries from the James Webb Space Telescope?",
    # 6. Education / EdTech
    "How is AI transforming personalized learning in K-12 education?",
    # 7. Biotech / Medicine
    "What are the latest developments in CRISPR gene editing therapy?",
    # 8. Energy / Sustainability
    "What progress has been made in nuclear fusion energy research?",
    # 9. Geopolitics / Trade
    "How are US-China trade tensions impacting the global semiconductor supply chain?",
    # 10. Short / Ambiguous query
    "quantum computing applications",
]


def run_query(query: str, index: int) -> dict:
    """Run a single query through api_bridge.py and return the result."""
    payload = json.dumps({"action": "submit", "query": query})
    env = os.environ.copy()
    env["ALLOW_MOCK_FALLBACK"] = "true"
    env["PYTHONIOENCODING"] = "utf-8"

    start = time.time()
    proc = subprocess.run(
        [sys.executable, "api_bridge.py"],
        cwd=ROOT,
        env=env,
        input=payload,
        text=True,
        capture_output=True,
        timeout=120,
    )
    elapsed = round(time.time() - start, 2)

    result = {
        "query_index": index + 1,
        "query": query,
        "elapsed_seconds": elapsed,
        "exit_code": proc.returncode,
        "stderr_snippet": (proc.stderr or "")[-500:],
    }

    if proc.returncode != 0:
        result["success"] = False
        result["error"] = f"Process exited with code {proc.returncode}"
        result["stdout_raw"] = (proc.stdout or "")[:2000]
        return result

    stdout = proc.stdout.strip()
    if not stdout:
        result["success"] = False
        result["error"] = "Empty stdout"
        return result

    try:
        data = json.loads(stdout)
        result["response"] = data
        result["success"] = data.get("success", False)
    except json.JSONDecodeError as e:
        result["success"] = False
        result["error"] = f"JSON decode error: {e}"
        result["stdout_raw"] = stdout[:2000]

    return result


def analyze_response(result: dict) -> dict:
    """Analyze a single query response for quality metrics."""
    analysis = {
        "query_index": result["query_index"],
        "query": result["query"],
        "elapsed_seconds": result["elapsed_seconds"],
        "success": result["success"],
    }

    if not result["success"]:
        analysis["failure_reason"] = result.get("error", "Unknown")
        return analysis

    resp = result.get("response", {})

    # Plan analysis
    plan = resp.get("plan", {})
    analysis["plan"] = {
        "has_goal": bool(plan.get("goal")),
        "goal_length": len(plan.get("goal", "")),
        "domains": plan.get("domains", []),
        "domain_count": len(plan.get("domains", [])),
        "total_tasks": plan.get("total_tasks", 0),
        "sources": plan.get("sources", []),
    }

    # Execution stats
    execution = resp.get("execution", {})
    analysis["execution"] = {
        "web_tasks": execution.get("web_tasks", 0),
        "paper_tasks": execution.get("paper_tasks", 0),
        "total_results": execution.get("total_results", 0),
        "successful": execution.get("successful", 0),
        "structured_items": execution.get("structured_items", 0),
        "trusted_items": execution.get("trusted_items", 0),
        "citation_sources": execution.get("citation_sources", 0),
        "cache_hit": execution.get("cache_hit", False),
        "research_raw_count": execution.get("research_raw_count", 0),
        "research_unique_count": execution.get("research_unique_count", 0),
        "enabled_research_sources": execution.get("enabled_research_sources", []),
    }

    # Trust report
    trust = resp.get("trust_report", {})
    analysis["trust_report"] = {
        "validated_count": trust.get("validated_count", 0),
        "trusted_count": trust.get("trusted_count", 0),
        "dropped_count": trust.get("dropped_count", 0),
        "trust_rate": (
            round(trust.get("trusted_count", 0) / max(1, trust.get("validated_count", 1)) * 100, 1)
        ),
    }

    # Insights analysis
    insights = resp.get("insights", {})
    analysis["insights"] = {
        "has_summary": bool(insights.get("summary")),
        "summary_length": len(insights.get("summary", "")),
        "has_concise_answer": bool(insights.get("concise_answer")),
        "concise_answer_length": len(insights.get("concise_answer", "")),
        "key_points_count": len(insights.get("key_points", [])),
        "key_highlights_count": len(insights.get("key_highlights", [])),
        "confidence": insights.get("confidence", 0),
        "summary_method": insights.get("summary_method", "unknown"),
        "source_breakdown": insights.get("source_breakdown", {}),
        "content_type_breakdown": insights.get("content_type_breakdown", {}),
        "recommended_reading_count": len(insights.get("recommended_reading", [])),
        "citation_links_count": len(insights.get("citation_links", [])),
    }

    # Data quality: check structured and trusted items
    structured = resp.get("structured_data", [])
    trusted = resp.get("trusted_data", [])
    analysis["data_quality"] = {
        "structured_item_count": len(structured),
        "trusted_item_count": len(trusted),
        "has_urls": sum(1 for item in trusted if item.get("url")),
        "has_titles": sum(1 for item in trusted if item.get("title")),
        "has_content": sum(1 for item in trusted if len(item.get("content", "")) > 100),
        "avg_trust_score": (
            round(sum(item.get("trust", {}).get("score", 0) for item in trusted) / max(1, len(trusted)), 3)
            if trusted else 0
        ),
        "content_types": list(set(item.get("content_type", "unknown") for item in trusted)),
    }

    return analysis


def format_report(all_analyses: list, all_results: list) -> str:
    """Generate a human-readable analysis report."""
    lines = []
    lines.append("=" * 80)
    lines.append("TrustWise 10-Query Integration Test & Analysis Report")
    lines.append(f"Generated: {datetime.now().isoformat()}")
    lines.append("Mode: Mock fallback (no API keys)")
    lines.append("=" * 80)

    # Overall summary
    total = len(all_analyses)
    successful = sum(1 for a in all_analyses if a["success"])
    failed = total - successful
    avg_time = round(sum(a["elapsed_seconds"] for a in all_analyses) / max(1, total), 2)

    lines.append(f"\n{'OVERALL SUMMARY':^80}")
    lines.append("-" * 80)
    lines.append(f"  Total queries:        {total}")
    lines.append(f"  Successful:           {successful}/{total}")
    lines.append(f"  Failed:               {failed}/{total}")
    lines.append(f"  Average response time: {avg_time}s")
    lines.append("")

    # Per-query detail
    for analysis in all_analyses:
        idx = analysis["query_index"]
        lines.append(f"\n{'=' * 80}")
        lines.append(f"QUERY {idx}: {analysis['query']}")
        lines.append(f"{'=' * 80}")
        lines.append(f"  Status:    {'PASS' if analysis['success'] else 'FAIL'}")
        lines.append(f"  Time:      {analysis['elapsed_seconds']}s")

        if not analysis["success"]:
            lines.append(f"  Failure:   {analysis.get('failure_reason', 'Unknown')}")
            continue

        # Plan
        plan = analysis.get("plan", {})
        lines.append(f"\n  --- Plan ---")
        lines.append(f"  Goal:          {plan.get('has_goal', False)} (length: {plan.get('goal_length', 0)} chars)")
        lines.append(f"  Domains:       {plan.get('domains', [])}")
        lines.append(f"  Total tasks:   {plan.get('total_tasks', 0)}")
        lines.append(f"  Sources:       {plan.get('sources', [])}")

        # Execution
        ex = analysis.get("execution", {})
        lines.append(f"\n  --- Execution ---")
        lines.append(f"  Web tasks:     {ex.get('web_tasks', 0)}")
        lines.append(f"  Paper tasks:   {ex.get('paper_tasks', 0)}")
        lines.append(f"  Total results: {ex.get('total_results', 0)}")
        lines.append(f"  Successful:    {ex.get('successful', 0)}")
        lines.append(f"  Structured:    {ex.get('structured_items', 0)}")
        lines.append(f"  Trusted:       {ex.get('trusted_items', 0)}")
        lines.append(f"  Citations:     {ex.get('citation_sources', 0)}")
        lines.append(f"  Cache hit:     {ex.get('cache_hit', False)}")
        lines.append(f"  Research sources: {ex.get('enabled_research_sources', [])}")

        # Trust
        tr = analysis.get("trust_report", {})
        lines.append(f"\n  --- Trust Report ---")
        lines.append(f"  Validated:     {tr.get('validated_count', 0)}")
        lines.append(f"  Trusted:       {tr.get('trusted_count', 0)}")
        lines.append(f"  Dropped:       {tr.get('dropped_count', 0)}")
        lines.append(f"  Trust rate:    {tr.get('trust_rate', 0)}%")

        # Insights
        ins = analysis.get("insights", {})
        lines.append(f"\n  --- Insights ---")
        lines.append(f"  Summary:       {'Yes' if ins.get('has_summary') else 'No'} ({ins.get('summary_length', 0)} chars)")
        lines.append(f"  Concise answer: {'Yes' if ins.get('has_concise_answer') else 'No'} ({ins.get('concise_answer_length', 0)} chars)")
        lines.append(f"  Key points:    {ins.get('key_points_count', 0)}")
        lines.append(f"  Key highlights: {ins.get('key_highlights_count', 0)}")
        lines.append(f"  Confidence:    {ins.get('confidence', 0)}")
        lines.append(f"  Method:        {ins.get('summary_method', 'unknown')}")
        lines.append(f"  Source breakdown: {ins.get('source_breakdown', {})}")
        lines.append(f"  Content types: {ins.get('content_type_breakdown', {})}")
        lines.append(f"  Recommended reading: {ins.get('recommended_reading_count', 0)}")
        lines.append(f"  Citation links: {ins.get('citation_links_count', 0)}")

        # Data quality
        dq = analysis.get("data_quality", {})
        lines.append(f"\n  --- Data Quality ---")
        lines.append(f"  Structured items: {dq.get('structured_item_count', 0)}")
        lines.append(f"  Trusted items:    {dq.get('trusted_item_count', 0)}")
        lines.append(f"  Items with URLs:  {dq.get('has_urls', 0)}")
        lines.append(f"  Items with titles: {dq.get('has_titles', 0)}")
        lines.append(f"  Items with content (>100 chars): {dq.get('has_content', 0)}")
        lines.append(f"  Avg trust score:  {dq.get('avg_trust_score', 0)}")
        lines.append(f"  Content types:    {dq.get('content_types', [])}")

    # Cross-query analysis
    successful_analyses = [a for a in all_analyses if a["success"]]
    if successful_analyses:
        lines.append(f"\n\n{'=' * 80}")
        lines.append(f"{'CROSS-QUERY ANALYSIS':^80}")
        lines.append("=" * 80)

        # Response time distribution
        times = [a["elapsed_seconds"] for a in successful_analyses]
        lines.append(f"\n  Response Times:")
        lines.append(f"    Min:     {min(times)}s")
        lines.append(f"    Max:     {max(times)}s")
        lines.append(f"    Avg:     {round(sum(times) / len(times), 2)}s")

        # Pipeline consistency
        all_have_plan = all(a.get("plan", {}).get("has_goal") for a in successful_analyses)
        all_have_summary = all(a.get("insights", {}).get("has_summary") for a in successful_analyses)
        all_have_answer = all(a.get("insights", {}).get("has_concise_answer") for a in successful_analyses)

        lines.append(f"\n  Pipeline Consistency:")
        lines.append(f"    All have plan goal:    {'YES' if all_have_plan else 'NO'}")
        lines.append(f"    All have summary:      {'YES' if all_have_summary else 'NO'}")
        lines.append(f"    All have concise answer: {'YES' if all_have_answer else 'NO'}")

        # Trust scoring
        trust_rates = [a.get("trust_report", {}).get("trust_rate", 0) for a in successful_analyses]
        confidences = [a.get("insights", {}).get("confidence", 0) for a in successful_analyses]
        lines.append(f"\n  Trust Metrics:")
        lines.append(f"    Avg trust rate:   {round(sum(trust_rates) / len(trust_rates), 1)}%")
        lines.append(f"    Avg confidence:   {round(sum(confidences) / len(confidences), 3)}")

        # Content metrics
        key_points_counts = [a.get("insights", {}).get("key_points_count", 0) for a in successful_analyses]
        highlight_counts = [a.get("insights", {}).get("key_highlights_count", 0) for a in successful_analyses]
        lines.append(f"\n  Content Metrics:")
        lines.append(f"    Avg key points:   {round(sum(key_points_counts) / len(key_points_counts), 1)}")
        lines.append(f"    Avg highlights:   {round(sum(highlight_counts) / len(highlight_counts), 1)}")

        # Issues found
        lines.append(f"\n  Issues Found:")
        issues = []
        for a in successful_analyses:
            idx = a["query_index"]
            ins = a.get("insights", {})
            dq = a.get("data_quality", {})
            tr = a.get("trust_report", {})

            if not ins.get("has_summary"):
                issues.append(f"    [Q{idx}] Missing summary")
            if not ins.get("has_concise_answer"):
                issues.append(f"    [Q{idx}] Missing concise answer")
            if ins.get("key_points_count", 0) == 0:
                issues.append(f"    [Q{idx}] No key points generated")
            if dq.get("trusted_item_count", 0) == 0:
                issues.append(f"    [Q{idx}] No trusted items (all filtered out)")
            if tr.get("trust_rate", 0) < 20:
                issues.append(f"    [Q{idx}] Very low trust rate: {tr.get('trust_rate')}%")
            if ins.get("confidence", 0) < 0.2:
                issues.append(f"    [Q{idx}] Very low confidence: {ins.get('confidence')}")

        if issues:
            lines.extend(issues)
        else:
            lines.append("    None - all queries produced quality output!")

    lines.append(f"\n{'=' * 80}")
    lines.append(f"END OF REPORT")
    lines.append(f"{'=' * 80}")

    return "\n".join(lines)


def main() -> None:
    print("=" * 60)
    print("TrustWise 10-Query Integration Test")
    print("=" * 60)
    print(f"Running {len(QUERIES)} queries through api_bridge.py...")
    print(f"Mode: mock fallback (ALLOW_MOCK_FALLBACK=true)\n")

    all_results = []
    all_analyses = []

    for i, query in enumerate(QUERIES):
        print(f"[{i + 1}/{len(QUERIES)}] Running: {query[:60]}...")
        result = run_query(query, i)
        analysis = analyze_response(result)
        all_results.append(result)
        all_analyses.append(analysis)

        status = "PASS" if result["success"] else "FAIL"
        print(f"         {status} ({result['elapsed_seconds']}s)")

    # Save raw results
    results_file = LOGS_DIR / "query_test_results.json"
    with open(results_file, "w", encoding="utf-8") as f:
        json.dump(all_results, f, indent=2, default=str)
    print(f"\nRaw results saved to: {results_file}")

    # Save analyses
    analyses_file = LOGS_DIR / "query_test_analyses.json"
    with open(analyses_file, "w", encoding="utf-8") as f:
        json.dump(all_analyses, f, indent=2, default=str)
    print(f"Analyses saved to:    {analyses_file}")

    # Generate and save report
    report = format_report(all_analyses, all_results)
    report_file = LOGS_DIR / "query_test_analysis.txt"
    with open(report_file, "w", encoding="utf-8") as f:
        f.write(report)
    print(f"Report saved to:      {report_file}")

    # Print report to stdout
    print("\n")
    print(report)

    # Exit code
    failed = sum(1 for a in all_analyses if not a["success"])
    if failed > 0:
        print(f"\n{failed}/{len(QUERIES)} queries failed!")
        sys.exit(1)
    else:
        print(f"\nAll {len(QUERIES)} queries passed!")
        sys.exit(0)


if __name__ == "__main__":
    main()
