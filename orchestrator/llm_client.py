import json

# Mock response for testing the architecture
MOCK_RESPONSE = json.dumps({
  "goal": "Analyze the impact of AI on healthcare",
  "domains": ["healthcare", "artificial_intelligence"],
  "time_range": "2023-2024",
  "sources": ["web", "research_papers"],
  "tasks": [
    {
      "task_id": "task_web_1",
      "source_type": "web",
      "agent": "scraper_agent",
      "prompt": "Find recent news about AI diagnostics tools released in 2024"
    },
    {
      "task_id": "task_paper_1",
      "source_type": "research_papers",
      "agent": "paper_agent",
      "prompt": "Search for papers on transformer models in medical imaging"
    }
  ]
})

def call_llm(user_query: str) -> str:
    """
    Simulates an LLM call. 
    In production, replace this with an OpenAI/Anthropic API call.
    """
    # For now, we return a valid JSON response to prove the pipeline works.
    # In a real scenario, you'd send `user_query` and the SYSTEM_PROMPT to the LLM.
    return MOCK_RESPONSE
