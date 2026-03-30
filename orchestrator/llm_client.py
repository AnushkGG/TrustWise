import json
from utils.config import Config
from utils.logger import setup_logger
from orchestrator.prompts import SYSTEM_PROMPT, USER_PROMPT_TEMPLATE

logger = setup_logger(__name__)

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

    Supported providers:
      - ``gemini``  – Google Gemini API (cloud, requires GEMINI_API_KEY)
      - ``ollama``  – Local Ollama server (no API key needed)

    Falls back to a mock response when the required API key is missing
    or when authentication fails.

    Args:
        user_query: Natural language query from the user

    Returns:
        JSON string containing the execution plan

    Raises:
        ValueError: If LLM call fails for a non-auth reason
    """

    # Use mock response if no API key is configured
    if Config.LLM_PROVIDER == "gemini" and not Config.GEMINI_API_KEY:
        logger.warning("GEMINI_API_KEY not set. Using mock response.")
        return MOCK_RESPONSE

    user_prompt = USER_PROMPT_TEMPLATE.format(query=user_query)

    try:
        if Config.LLM_PROVIDER == "gemini":
            return _call_gemini(user_prompt)
        elif Config.LLM_PROVIDER == "ollama":
            return _call_ollama(user_prompt)
        else:
            raise ValueError(f"Unsupported LLM provider: {Config.LLM_PROVIDER}")
    except Exception as e:
        error_str = str(e)

        # Check for common API key errors
        if "401" in error_str or "invalid" in error_str.lower() or "authentication" in error_str.lower():
            logger.error(f"Authentication failed: {e}")
            logger.warning("Invalid API key detected. Falling back to mock mode.")
            return MOCK_RESPONSE

        # For other errors, re-raise
        logger.error(f"LLM call failed: {e}")
        raise


def _call_gemini(user_prompt: str) -> str:
    """Call Google Gemini API."""
    try:
        import google.generativeai as genai
    except ImportError:
        logger.error("google-generativeai package not installed. Run: pip install google-generativeai")
        raise ImportError("google-generativeai required. Install with: pip install google-generativeai")

    genai.configure(api_key=Config.GEMINI_API_KEY)

    logger.info(f"Calling Gemini {Config.LLM_MODEL}...")

    model = genai.GenerativeModel(
        model_name=Config.LLM_MODEL,
        generation_config=genai.GenerationConfig(
            temperature=Config.LLM_TEMPERATURE,
            max_output_tokens=Config.LLM_MAX_TOKENS,
            response_mime_type="application/json",
        ),
        system_instruction=SYSTEM_PROMPT,
    )

    response = model.generate_content(user_prompt)

    content = response.text
    if not content:
        raise ValueError("Gemini returned empty response")

    logger.info("Gemini response received")
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

