import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Config:
    """
    Configuration manager for TrustWise.
    Loads settings from environment variables with sensible defaults.
    """
    
    # Project Paths
    BASE_DIR = Path(__file__).parent.parent
    DATA_DIR = BASE_DIR / "data"
    RAW_DATA_DIR = DATA_DIR / "raw"
    PLANS_DIR = DATA_DIR / "plans"
    STRUCTURED_DATA_DIR = DATA_DIR / "structured"
    TRUSTED_DATA_DIR = DATA_DIR / "trusted"
    DB_PATH = DATA_DIR / "trustwise.db"
    CONFIG_DIR = BASE_DIR / "config"
    
    # LLM Settings — only Gemini (cloud) and Ollama (local) are supported
    LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "gemini")  # gemini or ollama
    GEMINI_API_KEY: Optional[str] = os.getenv("GEMINI_API_KEY")
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "gemini-2.0-flash")
    LLM_TEMPERATURE: float = float(os.getenv("LLM_TEMPERATURE", "0.0"))
    LLM_MAX_TOKENS: int = int(os.getenv("LLM_MAX_TOKENS", "2000"))
    
    # Agent Settings
    WEB_SCRAPER_TIMEOUT: int = int(os.getenv("WEB_SCRAPER_TIMEOUT", "10"))
    ARXIV_MAX_RESULTS: int = int(os.getenv("ARXIV_MAX_RESULTS", "5"))
    
    # System Settings
    SAVE_PLANS: bool = os.getenv("SAVE_PLANS", "true").lower() == "true"
    SAVE_RAW_DATA: bool = os.getenv("SAVE_RAW_DATA", "true").lower() == "true"
    SAVE_STRUCTURED_DATA: bool = os.getenv("SAVE_STRUCTURED_DATA", "true").lower() == "true"
    SAVE_TRUSTED_DATA: bool = os.getenv("SAVE_TRUSTED_DATA", "true").lower() == "true"
    SAVE_TO_DB: bool = os.getenv("SAVE_TO_DB", "true").lower() == "true"
    ENABLE_DB_CACHE: bool = os.getenv("ENABLE_DB_CACHE", "true").lower() == "true"
    DB_CACHE_MIN_ITEMS: int = int(os.getenv("DB_CACHE_MIN_ITEMS", "3"))
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    
    @classmethod
    def ensure_directories(cls):
        """Create necessary directories if they don't exist."""
        cls.RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
        cls.PLANS_DIR.mkdir(parents=True, exist_ok=True)
        cls.STRUCTURED_DATA_DIR.mkdir(parents=True, exist_ok=True)
        cls.TRUSTED_DATA_DIR.mkdir(parents=True, exist_ok=True)
        cls.CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    
    @classmethod
    def validate(cls):
        """Validate required configuration."""
        if cls.LLM_PROVIDER == "gemini" and not cls.GEMINI_API_KEY:
            raise ValueError("GEMINI_API_KEY is required when LLM_PROVIDER is 'gemini'")
        if cls.LLM_PROVIDER not in ["gemini", "ollama"]:
            raise ValueError(f"Invalid LLM_PROVIDER: {cls.LLM_PROVIDER}. Must be 'gemini' or 'ollama'")

# Initialize directories on import
Config.ensure_directories()
