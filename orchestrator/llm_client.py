import json
from utils.config import Config
import logging
from orchestrator.prompts import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE

logger = logging.getLogger(__name__)

# Mock response for testing without API keys
MOCK_RESPONSE = json.dumps({
  "goal": "Analyze the impact of AI on healthcare",
  "domains": ["healthcare", "artificial_intelligence"],
  "time_range": "2023-2024",
  "sources": ["web", "research_papers"],
  "tasks": [
    {
      "task_id": "task_web_1",
      "source_type": "web",
      "agent": "web_agent",
      "prompt": "Find recent news about AI diagnostics tools released in 2024"
    },
    {
      "task_id": "task_paper_1",
      "source_type": "research_papers",
      "agent": "research_agent",
      "prompt": "Search for papers on transformer models in medical imaging"
    }
  ]
})

def call_llm(user_query: str) -> str:
    """
    Calls the configured LLM to generate a structured execution plan.
    
    Args:
        user_query: Natural language query from the user
        
    Returns:
        JSON string containing the execution plan
        
    Raises:
        ValueError: If API key is missing or LLM call fails
    """
    
    # Use mock response if no API key is configured
    if Config.LLM_PROVIDER == "openai" and not Config.OPENAI_API_KEY:
        logger.warning("OPENAI_API_KEY not set. Using mock response.")
        return MOCK_RESPONSE
    
    if Config.LLM_PROVIDER == "anthropic" and not Config.ANTHROPIC_API_KEY:
        logger.warning("ANTHROPIC_API_KEY not set. Using mock response.")
        return MOCK_RESPONSE
    
    user_prompt = USER_PROMPT_TEMPLATE.format(query=user_query)
    
    try:
        if Config.LLM_PROVIDER == "openai":
            return _call_openai(user_prompt)
        elif Config.LLM_PROVIDER == "anthropic":
            return _call_anthropic(user_prompt)
        elif Config.LLM_PROVIDER == "ollama":
            return _call_ollama(user_prompt)
        else:
            raise ValueError(f"Unsupported LLM provider: {Config.LLM_PROVIDER}")
    except Exception as e:
        error_str = str(e)
        
        # Check for common API key errors
        if "401" in error_str or "invalid_api_key" in error_str or "authentication" in error_str.lower():
            logger.error(f"Authentication failed: {e}")
            logger.warning("Invalid API key detected. Falling back to mock mode.")
            logger.info("Note: OpenAI keys start with 'sk-', not 'AIzaSy' (that's a Google key)")
            return MOCK_RESPONSE
        
        # For other errors, re-raise
        logger.error(f"LLM call failed: {e}")
        raise


def _call_openai(user_prompt: str) -> str:
    """Call OpenAI API."""
    try:
        from openai import OpenAI
    except ImportError:
        logger.error("openai package not installed. Run: pip install openai")
        raise ImportError("openai package required. Install with: pip install openai")
    
    client = OpenAI(api_key=Config.OPENAI_API_KEY)
    
    logger.info(f"Calling OpenAI {Config.LLM_MODEL}...")
    
    response = client.chat.completions.create(
        model=Config.LLM_MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ],
        temperature=Config.LLM_TEMPERATURE,
        max_tokens=Config.LLM_MAX_TOKENS,
        response_format={"type": "json_object"}  # Ensure JSON output
    )
    
    content = response.choices[0].message.content
    if content is None:
        raise ValueError("OpenAI returned empty response")
    
    logger.info("OpenAI response received")
    return content


def _call_anthropic(user_prompt: str) -> str:
    """Call Anthropic Claude API."""
    try:
        from anthropic import Anthropic  # type: ignore
    except ImportError:
        logger.error("anthropic package not installed. Run: pip install anthropic")
        raise ImportError("anthropic package required. Install with: pip install anthropic")
    
    client = Anthropic(api_key=Config.ANTHROPIC_API_KEY)
    
    logger.info(f"Calling Anthropic {Config.LLM_MODEL}...")
    
    # Anthropic requires JSON schema in the prompt itself
    full_prompt = f"{SYSTEM_PROMPT}\n\n{user_prompt}"
    
    response = client.messages.create(
        model=Config.LLM_MODEL,
        max_tokens=Config.LLM_MAX_TOKENS,
        temperature=Config.LLM_TEMPERATURE,
        messages=[
            {"role": "user", "content": full_prompt}
        ]
    )
    
    content = response.content[0].text  # type: ignore
    logger.info("Anthropic response received")
    return content


def _call_ollama(user_prompt: str) -> str:
    """Call local Ollama API."""
    try:
        import requests
    except ImportError:
        logger.error("requests package not installed. Run: pip install requests")
        raise ImportError("requests package required. Install with: pip install requests")
    
    logger.info(f"Calling Ollama {Config.LLM_MODEL} at {Config.OLLAMA_BASE_URL}...")
    
    url = f"{Config.OLLAMA_BASE_URL}/api/chat"
    
    payload = {
        "model": Config.LLM_MODEL,
        "messages": [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_prompt}
        ],
        "stream": False,
        "format": "json",
        "options": {
            "temperature": Config.LLM_TEMPERATURE,
            "num_predict": Config.LLM_MAX_TOKENS
        }
    }
    
    try:
        response = requests.post(url, json=payload, timeout=120)
        response.raise_for_status()
        
        result = response.json()
        content = result.get("message", {}).get("content", "")
        
        if not content:
            raise ValueError("Ollama returned empty response")
        
        logger.info("Ollama response received")
        return content
        
    except requests.exceptions.ConnectionError:
        logger.error(f"Failed to connect to Ollama at {Config.OLLAMA_BASE_URL}")
        logger.error("Make sure Ollama is running: ollama serve")
        raise
    except requests.exceptions.Timeout:
        logger.error("Ollama request timed out")
        raise

