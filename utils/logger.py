import logging
import os
import sys

_VALID_LEVELS = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}

def setup_logger(name: str):
    """Create or return a configured stream logger for the given module name."""
    logger = logging.getLogger(name)
    if not logger.handlers:
        level_name = os.getenv("LOG_LEVEL", "INFO").upper()
        if level_name not in _VALID_LEVELS:
            level_name = "INFO"
        logger.setLevel(getattr(logging, level_name))
        handler = logging.StreamHandler(sys.stdout)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler.setFormatter(formatter)
        logger.addHandler(handler)
    return logger
